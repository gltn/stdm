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
    QgsFeatureRequest
)
from PyQt4.QtGui import (
    QApplication,
    QLabel,
    QHBoxLayout
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

    def format_form(self):
        title = format_name(
            self.entity().short_name
        )

        title = QApplication.translate(
            'WidgetWrapper',
            '{} Editor'.format(title)
        )

        # Set title for QGIS form
        if self.parent.parent() is not None:
            self.parent.parent().setWindowTitle(title)

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

        self.format_form()

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

    def set_entity(self, source):
        curr_profile = current_profile()
        self.entity = curr_profile.entity_by_name(
            source
        )

    def qgis_version(self):
        qgis_version = '.'.join(
            re.findall(
                "[-+]?\d+[\.]?\d*",
                QGis.QGIS_VERSION[:4]
            )
        )
        return Decimal(qgis_version)

    def _set_widget_type(self, layer, column, widget_type_id):

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
        # if column.mandatory:
        #     layer.editFormConfig().setNotNull(idx, True)
        except Exception as ex:
            layer.setEditorWidgetV2(
                idx, widget_type_id
            )



    def set_widget_mapping(self):
        self.widget_mapping.clear()
        for c in self.entity.columns.values():

            if c.TYPE_INFO == 'SERIAL':
                self.widget_mapping[c] = ['Hidden', None]
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
        self.layer = layer
        for col, widget_id_name in \
                self.widget_mapping.iteritems():

            self._set_widget_type(
                layer, col, widget_id_name[0]
            )

    def load_stdm_form(self, feature_id):
        """
        Loads STDM Form
        :param feature_id:
        :type feature_id:
        :return:
        :rtype:
        """
        srid = None
        geom_column = None
        self.current_feature = feature_id

        # If the digitizing save button is clicked,
        # the featureAdded signal is called but the
        # feature ids value is over 0. Return to prevent
        # the dialog from poping up for every feature.
        if feature_id > 0:
            return

        # If the added feature is removed earlier, add it
        # back to feature_models and don't show the form.
        # This happens when redo button(add feature back) is
        # clicked after an undo button(remove feature)
        if feature_id in self.removed_feature_models.keys():
            print vars(self.removed_feature_models[feature_id])
            self.feature_models[feature_id] = \
                self.removed_feature_models[feature_id]
            return
        # if the feature is already don't show the form
        # as the model of the feature is
        # already populated by the form
        if feature_id in self.feature_models.keys():
            return

        geom_wkt = self.get_wkt(feature_id)
        # init form
        self.editor = EntityEditorDialog(
            self.entity, None, iface.mainWindow(), True, True
        )

        self.editor.addedModel.connect(self.on_form_saved)
        self.model = self.editor.model()

        for column in self.entity.columns.values():
            if column.TYPE_INFO == 'GEOMETRY':
                srid = column.srid
                geom_column = column.name

        if not geom_wkt is None:
            # add geometry into the model
            setattr(
                self.model,
                geom_column,
                'SRID={};{}'.format(srid, geom_wkt)
            )

        # open editor
        result = self.editor.exec_()
        if result < 1:
            self.layer.deleteFeature(feature_id)

    def get_wkt(self, feature_id):
        geom_wkt = None
        fids = [feature_id]
        request = QgsFeatureRequest()
        request.setFilterFids(fids)
        features = self.layer.getFeatures(request)
        # get the wkt of the geometry
        for feature in features:
            geom_wkt = feature.geometry().exportToWkt()

        return geom_wkt

    def on_form_saved(self, model):
        self.feature_models[self.current_feature] = model
        self.editor.accept()

    def on_feature_deleted(self, feature_id):
        if feature_id in self.feature_models.keys():
            self.removed_feature_models[feature_id] = \
                self.feature_models[feature_id]
            del self.feature_models[feature_id]

    def on_digitizing_saved(self):
        ent_model = entity_model(self.entity)
        entity_obj = ent_model()
        entity_obj.saveMany(
            self.feature_models.values()
        )
        # undo each feature created so that qgis
        # don't try to save the same feature.
        for i in range(len(self.feature_models)):
            self.layer.undoStack().undo()
