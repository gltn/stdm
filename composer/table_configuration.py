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
from PyQt4.QtXml import (
    QDomDocument,
    QDomElement
)

from .configuration_collection_base import (
    ConfigurationCollectionBase,
    LinkedTableItemConfiguration,
    ItemConfigValueHandler
)
from qgis.core import (
    QgsMapLayerRegistry,
    QgsVectorLayer
)

from .photo_configuration import PhotoConfiguration

class TableConfiguration(PhotoConfiguration):

    def vector_layer(self):
        """
        :return: Instance of vector layer in the layer registry matching
        the linked table name.
        :rtype: QgsVectorLayer
        """
        layers = QgsMapLayerRegistry.instance().mapLayersByName(self.linked_table())

        #Return first matching layer
        if len(layers) > 0:
            return layers[0]

        return None

    @staticmethod
    def create(dom_element):
        """
        Create a TableConfiguration object from a QDomElement instance.
        :param dom_element: QDomDocument that represents composer configuration.
        :type dom_element: QDomElement
        :return: TableConfiguration instance whose properties have been
        extracted from the composer document instance.
        :rtype: TableConfiguration
        """
        linked_table_props = TableConfiguration.linked_table_properties(dom_element)

        item_id = dom_element.attribute("itemid")
        link_table = linked_table_props.linked_table
        source_col = linked_table_props.source_field
        ref_col = linked_table_props.linked_field

        return TableConfiguration(linked_table=link_table,
                                  source_field=source_col,
                                  linked_field=ref_col,
                                  item_id=item_id)

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
    from stdm.ui.composer import ComposerTableDataSourceEditor

    collection_root = "Tables"
    editor_type = ComposerTableDataSourceEditor
    config_root = TableConfiguration.tag_name
    item_config = TableConfiguration

class TableItemValueHandler(ItemConfigValueHandler):
    """
    Class that applies the appropriate filter to the table composer item
    to fetch the corresponding rows from the linked table in the database.
    """
    def set_data_source_record(self, record):
        table_item = self.composer_item()
        if table_item is None:
            return

        '''
        Capture saved column settings since we are about to reset the vector
        layer
        '''
        display_attrs_cols = []
        cols = table_item.columns()

        for col in cols:
            display_attrs_cols.append(col.clone())

        vl = self._config_item.vector_layer()
        if not vl is None:
            table_item.setVectorLayer(vl)

            #Restore column settings
            table_item.setColumns(display_attrs_cols)

        else:
            return

        if not self._config_item.source_field():
            return

        #We are definitely going to filter the rows
        if not table_item.filterFeatures():
            table_item.setFilterFeatures(True)

        source_col_value = getattr(record, self._config_item.source_field(), '')
        if not source_col_value:
            return

        if isinstance(source_col_value, str) or isinstance(source_col_value, unicode):
            source_col_value = u"'{0}'".format(source_col_value)

        linked_field = self._config_item.linked_field()
        if not linked_field:
            return

        exp = u"{0} = {1}".format(linked_field, source_col_value)
        table_item.setFeatureFilter(exp)

