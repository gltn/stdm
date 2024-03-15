"""
/***************************************************************************
Name                 : Styling and labeling configuration for spatial data
                       fields.
Date                 : 26/May/2014
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
from collections import OrderedDict

from qgis.PyQt.QtXml import QDomDocument
from qgis.core import (
    QgsApplication,
    QgsSymbolLayerUtils
)

from stdm.ui.composer.composer_symbol_editor import (
    ComposerSymbolEditor
)

from stdm.composer.custom_items.map import StdmMapLayoutItem

class SpatialFieldsConfiguration:
    """
    Styling and labeling configuration for spatial data fields.
    """
    def __init__(self):
        # Mapping of map item id and list of spatial field configurations
        self._sp_fields_mapping_collec = OrderedDict()
        self._map_item = None

    def set_map_item(self, map_item):
        self._map_item = map_item

    def map_item(self):
        return self._map_item

    def addSpatialFieldMapping(self, spatial_field_mapping):
        """
        Add spatial field mapping to the collection
        """
        item_id = spatial_field_mapping.itemId()

        if not item_id:
            return

        if item_id in self._sp_fields_mapping_collec:
            self._sp_fields_mapping_collec[item_id].append(spatial_field_mapping)

        else:
            itemCollection = []
            itemCollection.append(spatial_field_mapping)
            self._sp_fields_mapping_collec[item_id] = itemCollection

    def spatialFieldsMapping(self):
        """
        Returns an instance of spatial fields mapping.
        """
        return self._sp_fields_mapping_collec

    def itemSpatialFieldsMapping(self, itemId):
        """
        Returns the list of items in the map item with the given id.
        """
        if itemId in self._sp_fields_mapping_collec:
            return self._sp_fields_mapping_collec[itemId]

        else:
            return []

    @staticmethod
    def domElement(composerWrapper, dom_document: QDomDocument):
        """
        Helper method that creates a spatial columns DOM element from a composer wrapper instance.
        """
        spatialColumnsElement = dom_document.createElement("SpatialFields")

        # Get the configured composer style editors for spatial columns
        for uuid, symbolEditor in composerWrapper.widgetMappings().items():
            composerItem = composerWrapper.composition().itemByUuid(uuid)

            if composerItem is not None:
                if isinstance(symbolEditor, ComposerSymbolEditor):
                    spFieldMappings = symbolEditor.spatial_field_mappings()
                    for spfm in spFieldMappings:
                        if spfm is not None:
                            spfm.setItemId(uuid)
                            spfmElement = spfm.toDomElement(dom_document)
                            spatialColumnsElement.appendChild(spfmElement)

        return spatialColumnsElement

    @staticmethod
    def createXXX(dom_document):
        """
        Create an instance of the 'SpatialFieldsConfiguration' object from a DOM document.
        Returns None if the dom_document is invalid.
        """
        from stdm.ui.composer.composer_spcolumn_styler import SpatialFieldMapping

        dataSourceElem = dom_document.documentElement().firstChildElement("DataSource")

        if dataSourceElem is None:
            return None

        spatialFieldsConfigElement = dataSourceElem.firstChildElement("SpatialFields")
        spFieldsConfig = SpatialFieldsConfiguration()

        # Get spatial field mappings
        spatialFieldMappingList = spatialFieldsConfigElement.elementsByTagName("SpatialField")
        numItems = spatialFieldMappingList.length()

        for i in range(numItems):
            spatialFieldMappingElement = spatialFieldMappingList.item(i).toElement()
            labelField = spatialFieldMappingElement.attribute("labelField")
            spatialField = spatialFieldMappingElement.attribute("name")
            itemId = spatialFieldMappingElement.attribute("itemid")
            srid = int(spatialFieldMappingElement.attribute("srid"))
            geomType = spatialFieldMappingElement.attribute("geomType")
            zoom = float(spatialFieldMappingElement.attribute("zoom"))
            zoom_type = spatialFieldMappingElement.attribute('zoomType', 'RELATIVE')

            # Create spatial field mapping
            spFieldMapping = SpatialFieldMapping(spatialField, labelField)
            spFieldMapping.setItemId(itemId)
            spFieldMapping.setSRID(srid)
            spFieldMapping.setGeometryType(geomType)
            spFieldMapping.setZoomLevel(zoom)
            spFieldMapping.zoom_type = zoom_type

            symbolElement = spatialFieldMappingElement.firstChildElement("Symbol")
            if symbolElement is not None:
                layerType = symbolElement.attribute("layerType")
                layerProps = QgsSymbolLayerUtils.parseProperties(symbolElement)
                symbolLayer = QgsApplication.symbolLayerRegistry().createSymbolLayer(layerType, layerProps)
                spFieldMapping.setSymbolLayer(symbolLayer)

            spFieldsConfig.addSpatialFieldMapping(spFieldMapping)

        return spFieldsConfig

    @staticmethod
    def dom_element(layout_items: list['QgsLayoutItem']):
        """
        Helper method that creates a spatial columns DOM element from a composer wrapper instance.
        """
        for layout_item in layout_items:
            spatial_columns_element = dom_document.createElement("SpatialFields")

        # Get the configured composer style editors for spatial columns
        for uuid, symbolEditor in composerWrapper.widgetMappings().items():
            composerItem = composerWrapper.composition().itemByUuid(uuid)

            if composerItem is not None:
                if isinstance(symbolEditor, ComposerSymbolEditor):
                    spFieldMappings = symbolEditor.spatial_field_mappings()

                    for spfm in spFieldMappings:
                        spfm.setItemId(uuid)
                        spfmElement = spfm.toDomElement(dom_document)
                        spatialColumnsElement.appendChild(spfmElement)

        return spatialColumnsElement

    @staticmethod
    def create(layout_items: list['QgsLayoutItem']):

        from stdm.ui.composer.composer_spcolumn_styler import SpatialFieldMapping

        spatial_field_configs = []

        for layout_item in layout_items:

            sp_field_config = SpatialFieldsConfiguration()

            if isinstance(layout_item, StdmMapLayoutItem):

                sp_field_config.set_map_item(layout_item)

                label_field = layout_item.label_field
                print('CREATE > ', label_field)

                spatial_field = layout_item.name
                item_id = layout_item.uuid()
                srid = layout_item.srid
                geom_type = layout_item.geom_type
                zoom = layout_item.zoom
                zoom_type = layout_item.zoom_type or 'RELATIVE'

                sp_fmap = SpatialFieldMapping(spatial_field, label_field)
                sp_fmap.setItemId(item_id)
                sp_fmap.setSRID(srid)
                sp_fmap.setGeometryType(geom_type)
                sp_fmap.setZoomLevel(zoom)
                sp_fmap.setLabelField(label_field)
                sp_fmap.zoom_type = zoom_type

                #TODO: Add a Symbol Element

                sp_field_config.addSpatialFieldMapping(sp_fmap)

                spatial_field_configs.append(sp_field_config)

        return spatial_field_configs





