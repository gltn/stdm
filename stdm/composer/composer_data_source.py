"""
/***************************************************************************
Name                 : Configuration for custom STDM data source.
Date                 : 20/May/2014
copyright            : (C) 2014 by John Gitau
email                : gkahiu@gmail.com
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

from qgis.PyQt.QtCore import (
    QFile,
    QIODevice
)
from qgis.PyQt.QtXml import (
    QDomDocument
)
from qgis.core import (
    QgsLayout,
    QgsObjectCustomProperties
)

from stdm.composer.layout_utils import LayoutUtils
from stdm.utils.reverse_dict import ReverseDict


class ComposerDataSource:
    """
    Container for data source settings.
    """

    def __init__(self, datasource_name:str="", category: str = "", referenced_table_name: str = ''):
        self._datasource_name = datasource_name
        self._dataSourceCategory = category
        self.referenced_table_name = referenced_table_name
        self._dataFieldmappings = ReverseDict()
        self._spatialFieldsConfig = None

    def setName(self, dataSourceName):
        """
        Sets the data source name.
        """
        self._datasource_name = dataSourceName

    def name(self):
        """
        Returns the data source name.
        """
        return self._datasource_name

    def category(self) -> str:
        """
        Returns the category of the data source.
        """
        return self._dataSourceCategory

    def setCategory(self, category: str):
        """
        Set the category of the data source.
        """
        self._dataSourceCategory = category

    def setSpatialFieldsConfig(self, spFieldsConfig):
        """
        Set the spatial fields configuration object
        """
        self._spatialFieldsConfig = spFieldsConfig

    def addDataFieldMapping(self, dataField, composerItemId):
        """
        Add the name of the data field.
        """
        self._dataFieldmappings[dataField] = composerItemId

    def dataFieldMappings(self):
        """
        Returns the collection of data field mappings.
        """
        return self._dataFieldmappings

    def clear(self):
        """
        Clears the data source name and removes all data field mappings.
        """
        self._datasource_name = ""
        self._dataFieldmappings = ReverseDict()

    def dataFieldName(self, composerItemId):
        """
        Returns the data field name corresponding to the composer item id.
        """
        if composerItemId in self._dataFieldmappings.reverse:
            return self._dataFieldmappings.reverse[composerItemId]
        else:
            return None

    def composerItemId(self, dataField):
        """
        Returns the composer item unique identifier corresponding to the given
        field.
        """
        if dataField in self._dataFieldmappings:
            return self._dataFieldmappings[dataField]
        else:
            return None

    def sqlSelectStatement(self):
        """
        Returns a sql select statement based on the data source and fields specified,as
        well as the spatial fields.
        """
        dataFields = list(self._dataFieldmappings.keys())

        # Get spatial fields and embed into the dataFields list
        if self._spatialFieldsConfig is not None:
            spatialFieldsCollection = list(self._spatialFieldsConfig.spatialFieldsMapping().values())

            for spfEntry in spatialFieldsCollection:
                spFields = [spm.spatialField() for spm in spfEntry]

                labelFields = [spm.labelField() for spm in spfEntry]

                dataFields.extend(spFields)
                dataFields.extend(labelFields)

        if len(dataFields) == 0:
            return ""

        # Ensure you only have unique fields
        dataFieldsSet = set(dataFields)

        dtFieldsStr = ",".join(dataFieldsSet)

        return "SELECT {0} FROM {1}".format(dtFieldsStr, self._datasource_name)

    @staticmethod
    def from_layout(layout: QgsLayout) -> 'ComposerDataSource':
        """
        Creates a ComposerDataSource using properties from the specified layout
        """
        data_source_name = LayoutUtils.get_stdm_data_source_for_layout(layout)
        data_source_category = LayoutUtils.get_stdm_data_category_for_layout(layout)
        referenced_table_name = LayoutUtils.get_stdm_referenced_table_for_layout(layout)

        return ComposerDataSource(
            data_source_name,
            data_source_category,
            referenced_table_name
        )

    @staticmethod
    def create(document: QDomDocument) -> 'ComposerDataSource':
        """
        Create an instance of the ComposerDataSource object from a DOM document.
        Returns None if the domDocument is invalid.
        """
        custom_properties = QgsObjectCustomProperties()
        custom_properties.readXml(document.documentElement())

        data_source_name = custom_properties.value(LayoutUtils.DATA_SOURCE_PROPERTY)
        data_category = custom_properties.value(LayoutUtils.DATA_CATEGORY_PROPERTY)
        referenced_table_name = custom_properties.value(LayoutUtils.REFERENCED_TABLE_PROPERTY)

        if not data_source_name:
            return None

        data_source = ComposerDataSource(
            data_source_name,
            data_category,
            referenced_table_name
        )

        data_field_list = document.elementsByTagName('LayoutItem')

        for n in range(data_field_list.count()):
            layout_node = data_field_list.item(n)
            element = layout_node.toElement()
            field_name = element.attribute('linked_field', None)
            item_id = element.attribute('id', None)

            if field_name is not None:
                data_source.addDataFieldMapping(field_name, item_id)

        return data_source

    @staticmethod
    def from_template_file(template_file: str) -> 'Optional[ComposerDataSource]':
        """
        Creates a ComposerDataSource object from the specified template file. If
        the file cannot be opened due to file permissions or if it does not exist
        then the function will return None.
        :param template_file: Absolute template file path.
        :type template_file: str
        :return: Composer data source object.
        :rtype: ComposerDataSource
        """
        t_file = QFile(template_file)

        # Check if the file exists
        if not t_file.exists():
            return None

        # Check if the file can be opened
        if not t_file.open(QIODevice.ReadOnly):
            return None

        template_doc = QDomDocument()

        # Populate dom document
        if template_doc.setContent(t_file):
            return ComposerDataSource.create(template_doc)

        return None
