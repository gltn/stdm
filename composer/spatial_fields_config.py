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

from stdm.ui import (
                     ComposerSymbolEditor
                     )

__all__ = ["SpatialFieldsConfiguration"]

class SpatialFieldsConfiguration(object):
    """
    Styling and labeling configuration for spatial data fields.
    """
    def __init__(self):
        #Mapping of map item id and list of spatial field configurations
        self._spFieldsMapping = OrderedDict()
        
    def addSpatialFieldMapping(self,spatialFieldMapping):
        """
        Add spatial field mapping to the collection
        """
        itemId = spatialFieldMapping.itemId()
        
        if itemId == "":
            return
        
        if itemId in self._spFieldsMapping:
            self._spFieldsMapping[itemId].append(spatialFieldMapping)
            
        else:
            itemCollection = []
            itemCollection.append(spatialFieldMapping)
            self._spFieldsMapping[itemId] = itemCollection
            
    def spatialFieldsMapping(self):
        """
        Returns an instance of spatial fields mapping.
        """
        return self._spFieldsMapping
    
    def itemSpatialFieldsMapping(self,itemId):
        """
        Returns the list of items in the map item with the given id.
        """
        if itemId in self._spFieldsMapping:
            return self._spFieldsMapping[itemId]
        
        else:
            return []
        
    @staticmethod   
    def domElement(composerWrapper,domDocument):
        """
        Helper method that creates a spatial columns DOM element from a composer wrapper instance.
        """
        spatialColumnsElement = domDocument.createElement("SpatialFields")
        
        #Get the configured composer style editors for spatial columns
        for uuid,symbolEditor in composerWrapper.widgetMappings().iteritems():
            composerItem = composerWrapper.composition().getComposerItemByUuid(uuid)
            
            if composerItem != None:
                if isinstance(symbolEditor,ComposerSymbolEditor):
                    spFieldMappings = symbolEditor.spatialFieldMappings()
                    
                    for spfm in spFieldMappings:
                        spfm.setItemId(uuid)
                        spfmElement = spfm.toDomElement(domDocument)
                        spatialColumnsElement.appendChild(spfmElement)
                    
        return spatialColumnsElement
    
    @staticmethod    
    def create(domDocument):
        """
        Create an instance of the 'SpatialFieldsConfiguration' object from a DOM document.
        Returns None if the domDocument is invalid.
        """
        from stdm.ui import SpatialFieldMapping
        
        dataSourceElem = domDocument.documentElement().firstChildElement("DataSource") 
        
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
            srid = spatialFieldMappingElement.attribute("srid") 
            geomType = spatialFieldMappingElement.attribute("geomType") 
            zoom = spatialFieldMappingElement.attribute("zoom") 
            
            #Create spatial field mapping
            spFieldMapping = SpatialFieldMapping(spatialField,labelField) 
            spFieldMapping.setItemId(itemId)
            spFieldMapping.setSRID(srid)
            spFieldMapping.setGeometryType(geomType)
            spFieldMapping.setZoomLevel(zoom)
            
            symbolElement = spatialFieldMappingElement.firstChildElement("Symbol")
            if symbolElement != None:
                layerType = symbolElement.attribute("layerType")
                layerProps = QgsSymbolLayerV2Utils.parseProperties(symbolElement)
                symbolLayer =  QgsSymbolLayerV2Registry.instance().createSymbolLayer(layerType,layerProps)
                spFieldMapping.setSymbolLayer(symbolLayer)
            
            spFieldsConfig.addSpatialFieldMapping(spFieldMapping)
            
        return spFieldsConfig