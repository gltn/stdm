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
import re
import logging
from decimal import Decimal
from qgis.core import (
    NULL,
    QgsFeatureRequest,
    QgsMessageLog,
    QgsVectorLayerCache
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

from stdm.ui.forms.widgets import ColumnWidgetRegistry

from stdm.settings import (
    current_profile
)

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
        :type QGIS vectorlayer
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
            'STDMFieldWidget',
            '{} Editor'.format(title)
        )

        # Set title and format labels for QGIS form
        if self.parent.parent() is not None:
            self.parent.parent().setWindowTitle(title)
            label = self.parent.parent().findChildren(QLabel)[-1:]
            if len(label) == 1:
                text = label[0].text()
                formatted_text = format_name(text)
                label[0].setText(formatted_text)

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
        for col, widget_id_name in \
                self.widget_mapping.iteritems():

            self._set_widget_type(
                layer, col, widget_id_name[0]
            )
