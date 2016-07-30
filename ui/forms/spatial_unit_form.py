# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : spatial_unit_form
Description          : GUI classes for managing and viewing supporting
                       documents.
Date                 : 15/July/2016
copyright            : (C) 2016 by UN-Habitat and implementing partners.
                       See the accompanying file CONTRIBUTORS.txt in the root
email                : stdm@unhabitat.org
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
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
    QgsVectorLayer
)
from PyQt4.QtGui import (
    QApplication,
    QLabel,
    QHBoxLayout,
    QColor,
    QMessageBox
)

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

from stdm.settings import (
    current_profile
)

from stdm.ui.forms.editor_dialog import EntityEditorDialog

from stdm.utils.util import (
    setComboCurrentIndexWithItemData,
    format_name
)

from stdm.ui.helpers import valueHandler

LOGGER = logging.getLogger('stdm')

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
                table = vals['table'].split('.')
                table_name = table[1].strip('"')
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

        except Exception as ex:
            pass

    def configWidget(self, layer, idx, parent):
        return QGISFieldWidgetConfig(layer, idx, parent)


class STDMFieldWidget():
    # Instantiate the singleton QgsEditorWidgetRegistry
    widgetRegistry = QgsEditorWidgetRegistry.instance()

    def __init__(self):
        self.entity = None
        self.widget_mapping = {}
        self.layer = None
        self.feature_models = OrderedDict()
        self.removed_feature_models=OrderedDict()
        self.current_feature = None
        self.editor = None

    def init_form(self, table, spatial_column, curr_layer):
        """
        Initialize required methods and slots
        to be used in form initialization.
        :param table: The table name of the layer
        :type table: String
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

            curr_layer.featureAdded.connect(
                lambda feature_id:
                self.load_stdm_form(feature_id, spatial_column)
            )

            curr_layer.featureDeleted.connect(
                self.on_feature_deleted
            )

            curr_layer.beforeCommitChanges.connect(
                self.on_digitizing_saved
            )

        except Exception as ex:
            LOGGER.debug(unicode(ex))

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
            layer.featureFormSuppress(1)



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
                    'STDMFieldWidget', 'STDM'
                )
                self.widget_mapping[c] = [
                    'stdm_{}'.format(
                        c.TYPE_INFO.lower()
                    ),
                    '{} {}'.format(
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
                widget_name = QApplication.translate(
                    'STDMFieldWidget', widget_id_name[1]
                )
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

    def load_stdm_form(self, feature_id, spatial_column):
        """
        Loads STDM Form and collects the model added
        into the form so that it is saved later.
        :param feature_id: the ID of a feature that
        is last added
        :type feature_id: Integer
        :return: None
        :rtype:NoneType
        """
        srid = None
        self.current_feature = feature_id

        # If the digitizing save button is clicked,
        # the featureAdded signal is called but the
        # feature ids value is over 0. Return to prevent
        # the dialog from poping up for every feature.
        if feature_id > 0:
            return

        # if the feature is already in the OrderedDict don't
        # show the form as the model of the feature is
        # already populated by the form
        if feature_id in self.feature_models.keys():
            return

        # If the added feature is removed earlier, add it
        # back to feature_models and don't show the form.
        # This happens when redo button(add feature back) is
        # clicked after an undo button(remove feature)
        if feature_id in self.removed_feature_models.keys():
            self.feature_models[feature_id] = \
                self.removed_feature_models[feature_id]
            return

        # If the feature is not valid, geom_wkt will be None
        # So don't launch form for invalid feature and
        # delete feature
        geom_wkt = self.get_wkt(feature_id)

        if geom_wkt is None:
            title = QApplication.translate(
                'STDMFieldWidget',
                'Spatial Entity Form Error'
            )
            msg = QApplication.translate(
                'STDMFieldWidget',
                'The feature you have added is invalid. \n'
                'To fix this issue, check if the feature '
                'is digitized correctly.  \n'
                'Removing and re-adding the layer could '
                'also fix the error.'
            )
            # Message: Spatial column information
            # could not be found
            QMessageBox.critical(
                iface.mainWindow(),
                title,
                msg
            )
            return
        # init form
        self.editor = EntityEditorDialog(
            self.entity,
            None,
            iface.mainWindow(),
            True,
            True
        )

        self.editor.addedModel.connect(self.on_form_saved)
        self.model = self.editor.model()

        # get srid with EPSG text
        full_srid = self.layer.crs().authid().split(':')

        if len(full_srid) > 0:
            # Only extract the number
            srid = full_srid[1]
        if not geom_wkt is None:
            # add geometry into the model
            setattr(
                self.model,
                spatial_column,
                'SRID={};{}'.format(srid, geom_wkt)
            )

        # open editor
        result = self.editor.exec_()
        if result < 1:
            self.layer.deleteFeature(feature_id)

    def get_wkt(self, feature_id):
        """
        Gets feature geometry in Well-Known Text
        format and returns it.
        :param feature_id: Feature id
        :type feature_id: Integer
        :return: Well-Known Text format of a geometry
        :rtype: WKT
        """
        geom_wkt = None
        fid = feature_id
        request = QgsFeatureRequest()
        request.setFilterFid(fid)
        features = self.layer.getFeatures(request)

        # get the wkt of the geometry
        for feature in features:
            geometry = feature.geometry()
            if geometry.isGeosValid():
                geom_wkt = feature.geometry().exportToWkt()

        return geom_wkt

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
        if not model is None:
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

    def on_digitizing_saved(self):
        """
        A slot raised when the save button is clicked
        on Digitizing Toolbar of QGIS. It saves feature
        models created by the digitizer and STDM form to
        the Database.
        :return: None
        :rtype: NoneType
        """
        ent_model = entity_model(self.entity)
        entity_obj = ent_model()
        entity_obj.saveMany(
            self.feature_models.values()
        )
        # undo each feature created so that qgis
        # don't try to save the same feature again.
        # It will also clear all the models from
        # self.feature_models as on_feature_deleted
        # is raised when a feature is removed.
        for i in range(len(self.feature_models)):
            self.layer.undoStack().undo()
