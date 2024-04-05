"""
/***************************************************************************
Name                 : TableConfiguration
Description          : Container for table configuration options in the
                       database.
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

from typing import Optional

from qgis.PyQt.QtXml import (
    QDomElement
)
from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsLayoutFrame,
    QgsLayoutItemAttributeTable,
    QgsLayoutTableColumn,
    QgsReadWriteContext
)

from stdm.composer.configuration_collection_base import (
    ConfigurationCollectionBase,
    ItemConfigValueHandler
)
from stdm.composer.photo_configuration import PhotoConfiguration
from stdm.composer.custom_items.table import StdmTableLayoutItem

from stdm.data.pg_utils import vector_layer as vec_layer


class TableConfiguration(PhotoConfiguration):

    def vector_layer(self) -> Optional[QgsVectorLayer]:
        """
        :return: Instance of vector layer in the layer registry matching
        the linked table name.
        :rtype: QgsVectorLayer
        """
        layers = QgsProject.instance().mapLayersByName(self.linked_table())

        #Return first matching layer
        if layers:
            return layers[0]
        return None

    @staticmethod
    def create(stdm_table_item: StdmTableLayoutItem):
        """
        #TODO: Refactor comments

        Create a TableConfiguration object from a QDomElement instance.
        :param dom_element: QDomDocument that represents composer configuration.
        :type dom_element: QDomElement
        :return: TableConfiguration instance whose properties have been
        extracted from the composer document instance.
        :rtype: TableConfiguration
        """

        print("* D *")

        return TableConfiguration(linked_table=stdm_table_item.table,
                                  source_field=stdm_table_item.datasource_field,
                                  linked_field=stdm_table_item.referencing_field,
                                  item_id=stdm_table_item.uuid(),
                                  table_layout_item=stdm_table_item)

    def create_handler(self, composition, query_handler=None):
        """
        :return: Returns the item value handler for the composer table item.
        :rtype: TableItemValueHandler
        """
        return TableItemValueHandler(composition, self, query_handler)


class TableConfigurationCollection(ConfigurationCollectionBase):
    """
    Class for managing multiple instances of TableConfiguration objects.
    """
    from stdm.ui.composer.table_data_source import ComposerTableDataSourceEditor

    collection_root = "Tables"
    editor_type = ComposerTableDataSourceEditor
    config_root = TableConfiguration.tag_name
    item_config = TableConfiguration

    layout_item_type = StdmTableLayoutItem
    is_multi_frame = True

class TableItemValueHandler(ItemConfigValueHandler):
    """
    Class that applies the appropriate filter to the table composer item
    to fetch the corresponding rows from the linked table in the database.
    """

    def set_data_source_record(self, record):
        # # table_item = self.composer_item()
        table_item = self._config_item.table_layout_item()

        if table_item is None:
            return

        try:
            cols = table_item.columns()
        except AttributeError:
            cols = table_item.multiFrame().columns()

        # if isinstance(table_item, QgsLayoutFrame):
        #     table_item = table_item.multiFrame()

        # '''
        # Capture saved column settings since we are about to reset the vector
        # layer
        # '''
        display_attrs_cols = []

        cols = table_item.columns()

        for col in cols:
            display_attrs_cols.append(col.clone())

        vl = self._config_item.vector_layer()
        if vl is None:
            return

        #TODO: Create logs for document generation process
        if not vl.isValid():
            return

        table_item.setVectorLayer(vl)
        
        table_item.recalculateTableSize()

        # Restore column settings
        table_item.setColumns(display_attrs_cols)
       
        if not self._config_item.source_field():
            return

        # We are definitely going to filter the rows
        if not table_item.filterFeatures():
            table_item.setFilterFeatures(True)

        source_col_value = getattr(record, self._config_item.source_field(), '')
        if not source_col_value:
            return

        if isinstance(source_col_value, str) or isinstance(source_col_value, str):
            source_col_value = f"'{source_col_value}'"

        linked_field = self._config_item.linked_field()
        if not linked_field:
            return

        exp = f"{linked_field} = {source_col_value}"

        table_item.setFeatureFilter(exp)

