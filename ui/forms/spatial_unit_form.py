# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Spatial Unit Form
Description          : Classes that customize QGIS form and use STDM forms
                      in QGIS 2.14.
Date                 : 15/July/2016
copyright            : (C) 2016 by UN-Habitat and implementing partners.
                       See the accompanying file CONTRIBUTORS.txt in the root
email                : stdm@unhabitat.org
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of th e GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import os
import json
import re
import logging
from decimal import Decimal
from collections import OrderedDict

from PyQt4.QtCore import QCoreApplication, QObject, pyqtSignal
from qgis.core import (
    NULL,
    QgsFeatureRequest,
    QgsMessageLog,
    QgsVectorLayerCache,
    QgsGeometry,
    QgsFeatureRequest,
    QgsMapLayerRegistry,
    QgsFeature,
    QgsPoint,
    QgsVectorLayer,
    QgsField, edit)
from PyQt4.QtGui import (
    QApplication,
    QLabel,
    QHBoxLayout,
    QColor,
    QMessageBox,
    QAction)

from qgis.gui import (
    QgsEditorWidgetWrapper,
    QgsEditorConfigWidget,
    QgsEditorWidgetFactory,
    QgsEditorWidgetRegistry
)

from qgis.utils import (
    iface,
    QGis
)
from sqlalchemy import func

from sqlalchemy.sql import (
    select
)
from stdm.data.database import (
    STDMDb
)
from stdm.data.configuration import entity_model

from stdm.ui.forms.widgets import ColumnWidgetRegistry
from stdm.geometry.geometry_utils import feature_id_to_feature, get_wkt
from stdm.settings import (
    current_profile
)
from stdm.geometry.geometry_utils import (
    zoom_to_selected, active_spatial_column, get_wkt
)

from stdm.ui.forms.editor_dialog import EntityEditorDialog

from stdm.utils.util import (
    setComboCurrentIndexWithItemData,
    format_name
)
from stdm.ui.forms.spatial_forms_container import  SpatialFormsContainer

from stdm.ui.customcontrols.relation_line_edit import ExpressionLineEdit

from stdm.ui.helpers import valueHandler

LOGGER = logging.getLogger('stdm')
EXCLUDED_COLUMNS_TO_FETCH = ['parcel_number', 'shape_area', 'shape_length']

class WidgetWrapper(QgsEditorWidgetWrapper):
    def __init__(self, layer, fieldIdx, editor, parent):
        super(WidgetWrapper, self).__init__(
            layer, fieldIdx, editor, parent
        )
        self.layer = layer
        self.field_idx = fieldIdx
        self.parent = parent
        self.column = self.field().name()

        self.value = None
        self.setValue = None
        self.column_widget = None
        self.handler_obj = None

    def entity(self):
        """
        Returns the current entity.
        :return: Entity Object
        :rtype: Object
        """
        curr_profile = current_profile()

        entity = curr_profile.entity_by_name(
            self.get_layer_source()
        )
        return entity

    def get_layer_source(self):
        """
        Get the layer table name if the source
        is from the database.
        :param layer: The layer for which the
        source is checked
        :type QGIS Vector Layer
        :return: The table name of the layer
        :rtype: String or None
        """
        if self.layer is not None:
            source = self.layer.source()
            vals = dict(
                re.findall('(\S+)="?(.*?)"? ', source)
            )
            try:
                #table = vals['table'].split('.')
                #table_name = table[1].strip('"')
                table_name = self.layer.shortName()
                return table_name
            except KeyError:
                return None

    def value(self):
        """ Return the current value of the widget"""
        if not self.handler_obj is None:
            self.value()

    def setValue(self, value):
        """ Set a value on the widget """
        if not self.handler_obj is None:
            if value != NULL:
                self.set_value(value)

    def createWidget(self, parent):
        """ Create a new empty widget """
        column_obj = self.entity().columns[self.column]
        self.column_widget = ColumnWidgetRegistry.create(
            column_obj,
            parent
        )

        return self.column_widget

    def valid(self):
        """
        Make certain widget types valid and hide the rest.
        But set to return True as all are valid
        :return: The validity of certain widget type.
        :rtype: Boolean
        """
        return True

    def initWidget(self, widget):
        """
        Initialize the widget
        """
        if not widget is None:
            self.value_handler = valueHandler(widget)

            if not self.value_handler is None:
                self.handler_obj = self.value_handler()

                if widget is not None:
                    self.handler_obj.setControl(widget)

                self.value = getattr(
                    self.handler_obj, 'value'
                )

                self.set_value = getattr(
                    self.handler_obj, 'setValue'
                )


class QGISFieldWidgetConfig(QgsEditorConfigWidget):
    def __init__(self, layer, idx, parent):
        QgsEditorConfigWidget.__init__(
            self, layer, idx, parent
        )

        self.setLayout(QHBoxLayout())
        self.label = QLabel()
        self.layout().addWidget(self.label)

    def setConfig(self, config):
        info_text = 'You can modify the data type by changing ' \
                    'the columns in STDM configuration wizard.'
        self.label.setText(
            QApplication.translate(
                'QGISFieldWidgetConfig', info_text
            )
        )

    def config(self):
        pass


class QGISFieldWidgetFactory(QgsEditorWidgetFactory):
    def __init__(self, name):
        QgsEditorWidgetFactory.__init__(self, name)

    def create(self, layer, fieldIdx, editor, parent):
        try:
            widget_wrapper = WidgetWrapper(
                layer, fieldIdx, editor, parent
            )

            if not widget_wrapper is None:
                return widget_wrapper

        except Exception:
            pass

    def configWidget(self, layer, idx, parent):
        return QGISFieldWidgetConfig(layer, idx, parent)


class QgsFeatureId(object):
    pass


class STDMFieldWidget(QObject):
    # Instantiate the singleton QgsEditorWidgetRegistry
    widgetRegistry = QgsEditorWidgetRegistry.instance()
    # onFeatureUpdated = pyqtSignal(long, str)
    def __init__(self, plugin):
        QObject.__init__(self, iface.mainWindow())
        self.entity = None
        self.plugin = plugin
        self.widget_mapping = {}
        self.layer = None
        self.spatial_column = None
        self.feature_models = OrderedDict()
        self.removed_feature_models = OrderedDict()
        self.current_feature = None
        self.editor = None
        # self.onFeatureUpdated.connect(self.load_stdm_form)

    def init_form(self, table, spatial_column, curr_layer):
        """
        Initialize required methods and slots
        to be used in form initialization.
        :param table: The table name of the layer
        :type table: String
        :param spatial_column: The spatial column name
        of the layer
        :type spatial_column: String
        :param curr_layer: The current layer of form.
        :type curr_layer: QgsVectorLayer
        :return: None
        :rtype: NoneTYpe
        """

        try:
            # init form
            self.set_entity(table)
            self.set_widget_mapping()
            self.register_factory()
            self.set_widget_type(curr_layer)

            curr_layer.editFormConfig().setSuppress(1)
            try:

                curr_layer.featureAdded.connect(
                    lambda feature_id: self.load_stdm_form(
                        feature_id, spatial_column
                    )
                )
            except Exception:
                pass

            curr_layer.featureDeleted.connect(
                self.on_feature_deleted
            )

            curr_layer.beforeCommitChanges.connect(
                self.on_digitizing_saved
            )
            self.spatial_column = active_spatial_column(self.entity, self.layer)

        except Exception as ex:
            LOGGER.debug(ex)

    def set_entity(self, source):
        """
        Sets the layer entity of the layer
        based on a table name.
        :param source: Table name that acts as a layer source.
        :type source: String
        :return: None
        :rtype: NoneType
        """
        curr_profile = current_profile()
        self.entity = curr_profile.entity_by_name(
            source
        )

    def _set_widget_type(self, layer, column, widget_type_id):
        """
        Sets the widget type for each field into
        QGIS form configuration.
        :param layer: The layer to which the widget type is set.
        :type layer: QgsVectorLayer
        :param column: STDM column object
        :type column: Object
        :param widget_type_id: The widget type id which could be
         the default QGIS or the custom STDM widget id which is
         based on column.TYPE_INFO.
        :type widget_type_id: String
        :return: None
        :rtype:NoneType
        """
        idx = layer.fieldNameIndex(column.name)
        # Set Alias/ Display names for the column names
        layer.addAttributeAlias(
            idx,
            column.header()
        )

        try:
            layer.editFormConfig().setWidgetType(
                idx, widget_type_id
            )

        except Exception:
            layer.setEditorWidgetV2(
                idx, widget_type_id
            )

    def set_widget_mapping(self):
        """
        Maps each column to QGIS or STDM editor widgets.
        :return: None
        :rtype:NoneType
        """
        self.widget_mapping.clear()
        for c in self.entity.columns.values():

            if c.TYPE_INFO == 'SERIAL':
                self.widget_mapping[c] = ['Hidden', None]
            elif c.TYPE_INFO == 'GEOMETRY':
                self.widget_mapping[c] = ['TextEdit', None]
            else:
                stdm = QApplication.translate(
                    'STDMFieldWidget', u'STDM'
                )
                self.widget_mapping[c] = [
                    u'stdm_{}'.format(
                        c.TYPE_INFO.lower()
                    ),
                    u'{} {}'.format(
                        stdm, c.display_name()
                    )
                ]

    def register_factory(self):
        """
        Registers each widget type
        to a QGIS widget factory registry.
        :return: None
        :rtype: NoneType
        """
        # The destructor has no effects. It is QGIS bug.
        # So restarting QGIS is required to destroy
        # registered stdm widgets.
        for widget_id_name in self.widget_mapping.values():
            # add and register stdm widget type only
            if not widget_id_name[1] is None:
                widget_name = widget_id_name[1]

                if widget_id_name[0] not in \
                        self.widgetRegistry.factories().keys():
                    widget_factory = QGISFieldWidgetFactory(
                        widget_name
                    )

                    self.widgetRegistry.registerWidget(
                        widget_id_name[0], widget_factory
                    )

    def set_widget_type(self, layer):
        """
        Sets widget type for each fields in a layer.
        :param layer: The layer to which the widget type is set.
        :type layer: QgsVectorLayer
        :return: None
        :rtype: NoneType
        """
        self.layer = layer
        for col, widget_id_name in \
                self.widget_mapping.iteritems():
            self._set_widget_type(
                layer, col, widget_id_name[0]
            )

    def feature_to_model(self, feature_id):
        """
        Converts feature to db model.
        :param feature_id: The feature id
        :type feature_id: Integer
        :return: The model and number of columns with data.
        :rtype: Tuple
        """
        ent_model = entity_model(self.entity)
        ent_model = ent_model()

        geom_wkt = get_wkt(self.entity, self.layer, self.spatial_column, feature_id)
        srid = None
        # get srid with EPSG text
        full_srid = self.layer.crs().authid().split(':')
        if len(full_srid) > 0:
            # Only extract the number
            srid = full_srid[1]

        iterator = self.layer.getFeatures(
            QgsFeatureRequest().setFilterFid(feature_id)
        )
        feature = next(iterator)

        field_names = [field.name() for field in self.layer.pendingFields()]
        attribute = feature.attributes()
        if isinstance(attribute[0], QgsField):
            return None, 0
        mapped_data = OrderedDict(zip(field_names, feature.attributes()))
        col_with_data = []
        entity_cols = [c.name for c in self.entity.columns.values()]
        for col, value in mapped_data.iteritems():
            # print feature_id, col, value
            if col == 'id' and feature_id <= 0:
                continue
            if col == 'id' and feature_id > 0:
                value = int(value)
            if col in EXCLUDED_COLUMNS_TO_FETCH:
                continue
            if col not in entity_cols:
                continue
            if value is None:
                continue
            if value == NULL:
                continue

            setattr(ent_model, col, value)
            col_with_data.append(col)
        if geom_wkt is not None:
            # add geometry into the model
            setattr(
                ent_model,
                self.spatial_column,
                'SRID={};{}'.format(srid, geom_wkt)
            )
        else:
            return ent_model, 0
        return ent_model, len(col_with_data)

    def load_stdm_form(self, feature_id, spatial_column=None, entity=None,
                       layer=None, allow_saved_ft=False):
        """
        Loads STDM Form and collects the model added
        into the form so that it is saved later.
        :param feature_id: the ID of a feature that
        is last added
        :type feature_id: Integer
        :param spatial_column: The spatial column name
        of the layer
        :type spatial_column: String
        :return: None
        :rtype:NoneType
        """

        if entity is not None:
            self.entity = entity
        if layer is not None:
            self.layer = layer
        if spatial_column is not None:
            self.spatial_column = spatial_column

        srid = None

        self.current_feature = feature_id

        # If the digitizing save button is clicked,
        # the featureAdded signal is called but the
        # feature ids value is over 0. Return to prevent
        # the dialog from popping up for every feature.
        if feature_id > 0:
            if not allow_saved_ft:
                return

        # if the feature is already in the OrderedDict don't
        # show the form as the model of the feature is
        # already populated by the form
        if feature_id in self.feature_models.keys():
            return

        # If the feature is removed by the undo button, don't
        # load the form for it but add it
        # back to feature_models and don't show the form.
        # This happens when redo button(add feature back) is
        # clicked after an undo button(remove feature)
        if feature_id in self.removed_feature_models.keys():
            self.feature_models[feature_id] = \
                self.removed_feature_models[feature_id]
            return

        feature_model, col_with_data = self.feature_to_model(feature_id)

        self.feature_models[feature_id] = feature_model

    def on_form_saved(self, model):
        """
        A slot raised when the save button is clicked
        in spatial unit form. It adds the feature model
        in feature_models ordered dictionary to be saved
        later.
        :param model: The model holding feature geometry
        and attributes obtained from the form
        :type model: SQLAlchemy Model
        :return: None
        :rtype: NoneType
        """
        if model is not None and self.editor.is_valid:
            self.feature_models[self.current_feature] = model
            self.editor.accept()

    def on_feature_deleted(self, feature_id):
        """
        A slot raised when a feature is deleted
        in QGIS map canvas via the undo button.
        It deletes the associated model of the feature.
        :param feature_id: The id that is removed.
        :type feature_id: Integer
        :return: None
        :rtype: NoneType
        """
        if feature_id in self.feature_models.keys():
            self.removed_feature_models[feature_id] = \
                self.feature_models[feature_id]
            del self.feature_models[feature_id]

    def clear_split_parcel_key(self):
        for k, model in self.feature_models.iteritems():
            if model.id is None:
                model.parcel_key = ''

    def on_digitizing_saved(self):
        """
        A slot raised when the save button is clicked
        on Digitizing Toolbar of QGIS. It saves feature
        models created by the digitizer and STDM form to
        the Database.
        :return: None
        :rtype: NoneType
        """
        if len(self.feature_models) == 0:
            return

        # Very serious work-around: to be removed after shipping the first version 
        ###################
        self.clear_split_parcel_key()
        #####################

        spatial_forms = SpatialFormsContainer(
            self.entity, self.layer, self.feature_models, self.plugin
        )


        result = spatial_forms.exec_()

        if result == 1:

            # undo each feature created so that qgis
            # don't try to save the same feature again.
            # It will also clear all the models from
            # self.feature_models as on_feature_deleted
            # is raised when a feature is removed.
            iface.mainWindow().blockSignals(True)
            for f_id in self.feature_models.keys():
                # self.layer.deleteFeature(f_id)
                self.on_feature_deleted(f_id)

            iface.mainWindow().blockSignals(False)

            for i in range(len(self.feature_models)):
                self.layer.undoStack().undo()
