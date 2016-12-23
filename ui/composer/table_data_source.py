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
from PyQt4.QtGui import (
    QApplication,
    QWidget
)
from PyQt4.QtCore import QRegExp

from qgis.core import QgsMapLayerRegistry, QgsComposerFrame

from stdm.data.pg_utils import (
    VIEWS,
    vector_layer
)

from ..notification import (
    NotificationBar,
    ERROR
)
from .referenced_table_editor import LinkedTableProps
from .ui_composer_table_source import Ui_TableDataSourceEditor

class ComposerTableDataSourceEditor(QWidget, Ui_TableDataSourceEditor):
    def __init__(self, composer_wrapper, frame_item, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)

        self._composer_wrapper = composer_wrapper
        if isinstance(frame_item, QgsComposerFrame):
            self._composer_table_item = frame_item.multiFrame()

        else:
            self._composer_table_item = frame_item

        self._notif_bar = NotificationBar(self.vl_notification)

        #Load fields if the data source has been specified
        ds_name = self._composer_wrapper.selectedDataSource()
        self.ref_table.load_data_source_fields(ds_name)

        #Load source tables
        self.ref_table.load_link_tables()

        #Connect signals
        self._composer_wrapper.dataSourceSelected.connect(self.ref_table.on_data_source_changed)
        self.ref_table.cbo_ref_table.currentIndexChanged[str].connect(self.set_table_vector_layer)

    def composer_item(self):
        return self._composer_table_item

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

        #No need to add the layer in the legend
        QgsMapLayerRegistry.instance().addMapLayer(v_layer, False)
        self._composer_table_item.setVectorLayer(v_layer)
        self._composer_table_item.update()

    def configuration(self):
        from stdm.composer import TableConfiguration

        linked_table_props = self.ref_table.properties()

        table_config = TableConfiguration()
        table_config.set_linked_table(linked_table_props.linked_table)
        table_config.set_source_field(linked_table_props.source_field)
        table_config.set_linked_column(linked_table_props.linked_field)

        return table_config

    def set_configuration(self, configuration):
        #Load referenced table editor with item configuration settings.
        table_props = LinkedTableProps(linked_table=configuration.linked_table(),
                                source_field=configuration.source_field(),
                                linked_field=configuration.linked_field())

        self.ref_table.set_properties(table_props)