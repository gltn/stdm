"""
/***************************************************************************
Name                 : ComposerPhotoDatSourceEditor
Description          : Widget for specifying data properties for tables in
                       the document designer.
Date                 : 5/January/2015
copyright            : (C) 2014 by UN-Habitat and implementing partners.
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
import typing

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QApplication,
    QWidget
)
from qgis.core import (
    QgsLayoutItem,
    QgsLayoutFrame,
    QgsProject
)

from stdm.composer.layout_utils import LayoutUtils
from stdm.data.pg_utils import (
    vector_layer
)
from stdm.ui.composer.referenced_table_editor import LinkedTableProps
from stdm.ui.gui_utils import GuiUtils
from stdm.ui.notification import (
    NotificationBar
)

WIDGET, BASE = uic.loadUiType(
    GuiUtils.get_ui_file_path('composer/ui_composer_table_source.ui'))


class ComposerTableDataSourceEditor(WIDGET, BASE):
    def __init__(self, frame_item:typing.Union[QgsLayoutItem, QgsLayoutFrame], parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)

        print('* C *')

        if isinstance(frame_item, QgsLayoutFrame):
            self._composer_table_item = frame_item.multiFrame()
        else: 
            self._composer_table_item = frame_item  # QgsLayoutItem

        self._layout = self._composer_table_item.layout()

        self._notif_bar = NotificationBar(self.vl_notification)

        self.ref_table.load_link_tables()

        # Load fields if the data source has been specified
        ds_name = LayoutUtils.get_stdm_data_source_for_layout(self._layout)
        self.ref_table.load_data_source_fields(ds_name)

        referenced_table_name = LayoutUtils.get_stdm_referenced_table_for_layout(self._layout)
        self.ref_table.load_referencing_fields(referenced_table_name)

        table_name = self._composer_table_item.table
        datasource_field = self._composer_table_item.datasource_field
        referencing_field = self._composer_table_item.referencing_field

        self.ref_table.set_layout(self._layout)

        current_cols = []
        table_cols = self._composer_table_item.columns()
        for col in table_cols:
            current_cols.append(col.clone())

        if table_name:
            self.set_table_vector_layer(table_name)

        # self.ref_table.cbo_ref_table.currentIndexChanged[str].connect(
        #         self.set_table_vector_layer)

        self._composer_table_item.setColumns(current_cols)

        layer_name = self.current_table_layer_name()

        # Referenced table
        idx = self.ref_table.cbo_ref_table.findText(layer_name)
        if idx != -1:
            self.ref_table.cbo_ref_table.setCurrentIndex(idx)

        # FIXME: There is confusion between "referenced" and "References" table name
        idx = self.ref_table.cbo_ref_table.findText(table_name)   
        if idx != -1:
            self.ref_table.cbo_ref_table.setCurrentIndex(idx)
        
        self.ref_table.cbo_ref_table.currentIndexChanged[str].connect(
                self.set_references_field
                )

        # Datasource field
        idx = self.ref_table.cbo_source_field.findText(datasource_field)
        if idx != -1:
            self.ref_table.cbo_source_field.setCurrentIndex(idx)

        self.ref_table.cbo_source_field.currentIndexChanged[str].connect(
                self.set_datasource_field
                )

        # Referencing field
        idx = self.ref_table.cbo_referencing_col.findText(referencing_field)
        if idx != -1:
            self.ref_table.cbo_referencing_col.setCurrentIndex(idx)

        self.ref_table.cbo_referencing_col.currentIndexChanged[str].connect(
                self.set_referencing_field
                )

        self._composer_table_item.recalculateFrameSizes()


    def composer_item(self):
        return self._composer_table_item

    def current_table_layer_name(self):
        return self._composer_table_item.vectorLayer().name() if self._composer_table_item.vectorLayer() else ''

    def set_table_vector_layer(self, table_name):
        """
        Creates a vector layer and appends it to the composer table item.
        :param table_name: Name of the linked table containing tabular
        information.
        :type table_name: str
        """
        self._notif_bar.clear()

        if not table_name:
            return

        v_layer = vector_layer(table_name)
        if v_layer is None:
            msg = QApplication.translate("ComposerTableDataSourceEditor",
                                         "A vector layer could not be created from the table.")
            self._notif_bar.insertErrorNotification(msg)

            return

        if not v_layer.isValid():
            msg = QApplication.translate("ComposerTableDataSourceEditor",
                                         "Invalid vector layer, the table will not be added.")
            self._notif_bar.insertErrorNotification(msg)

            return

        # No need to add the layer in the legend
        QgsProject.instance().addMapLayer(v_layer, False)

        if len(self.composer_item().columns()) > 0:
            self._composer_table_item.setVectorLayer(v_layer) 
        

    def set_references_field(self, field: str):
        self._composer_table_item.set_table(field)
        self._composer_table_item.update()
        self.set_table_vector_layer(field)

    def set_datasource_field(self, field: str):
        self._composer_table_item.set_datasource_field(field)
        self._composer_table_item.update()

    def set_referencing_field(self, field: str):
        self._composer_table_item.set_referencing_field(field)
        self._composer_table_item.update()

    def configuration(self):
        from stdm.composer.table_configuration import TableConfiguration

        linked_table_props = self.ref_table.properties()

        table_config = TableConfiguration()
        table_config.set_linked_table(linked_table_props.linked_table)
        table_config.set_source_field(linked_table_props.source_field)
        table_config.set_linked_column(linked_table_props.linked_field)

        return table_config

    def set_configuration(self, configuration):
        # Load referenced table editor with item configuration settings.
        table_props = LinkedTableProps(linked_table=configuration.linked_table(),
                                       source_field=configuration.source_field(),
                                       linked_field=configuration.linked_field())

        self.ref_table.set_properties(table_props)
