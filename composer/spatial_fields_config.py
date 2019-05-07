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

from qgis.core import (
    QgsSymbolLayerV2Registry,
    QgsSymbolLayerV2Utils
)

from stdm.ui.composer import (
    ComposerSymbolEditor
)

__all__ = ["SpatialFieldsConfiguration"]

class SpatialFieldsConfiguration(object):
    """
    Styling and labeling configuration for spatial data fields.
    """
    def __init__(self):
        #Mapping of map item id and list of spatial field configurations
        self._sp_fields_mapping_collec = OrderedDict()
        
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
    def domElement(composerWrapper, dom_document):
        """
        Helper method that creates a spatial columns DOM element from a composer wrapper instance.
        """
        spatialColumnsElement = dom_document.createElement("SpatialFields")
        
        #Get the configured composer style editors for spatial columns
        for uuid,symbolEditor in composerWrapper.widgetMappings().iteritems():
            composerItem = composerWrapper.composition().getComposerItemByUuid(uuid)
            
            if not composerItem is None:
                if isinstance(symbolEditor, ComposerSymbolEditor):
                    spFieldMappings = symbolEditor.spatial_field_mappings()
                    
                    for spfm in spFieldMappings:
                        spfm.setItemId(uuid)
                        spfmElement = spfm.toDomElement(dom_document)
                        spatialColumnsElement.appendChild(spfmElement)
                    
        return spatialColumnsElement
    
    @staticmethod    
    def create(dom_document):
        """
        Create an instance of the 'SpatialFieldsConfiguration' object from a DOM document.
        Returns None if the dom_document is invalid.
        """
        from stdm.ui.composer import SpatialFieldMapping
        
        dataSourceElem = dom_document.documentElement().firstChildElement("DataSource")
        
        if dataSourceElem == None:
            return None
        
        spatialFieldsConfigElement = dataSourceElem.firstChildElement("SpatialFields") 
        spFieldsConfig = SpatialFieldsConfiguration()
        
        #Get spatial field mappings
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
            
            #Create spatial field mapping
            spFieldMapping = SpatialFieldMapping(spatialField,labelField) 
            spFieldMapping.setItemId(itemId)
            spFieldMapping.setSRID(srid)
            spFieldMapping.setGeometryType(geomType)
            spFieldMapping.setZoomLevel(zoom)
            spFieldMapping.zoom_type = zoom_type

            symbolElement = spatialFieldMappingElement.firstChildElement("Symbol")
            if not symbolElement is None:
                layerType = symbolElement.attribute("layerType")
                layerProps = QgsSymbolLayerV2Utils.parseProperties(symbolElement)
                symbolLayer =  QgsSymbolLayerV2Registry.instance().createSymbolLayer(layerType,layerProps)
                spFieldMapping.setSymbolLayer(symbolLayer)
            
            spFieldsConfig.addSpatialFieldMapping(spFieldMapping)
            
        return spFieldsConfig