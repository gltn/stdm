"""
/***************************************************************************
Name                 : Document Generator class
Description          : Generates documents from user-defined templates.
Date                 : 21/May/2014
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
from PyQt4.QtGui import (
                         QApplication,
                         QImage,
                         QPainter,
                         QPrinter
                         )
from PyQt4.QtCore import (
                          QObject,
                          QIODevice,
                          QFile,
                          QFileInfo,
                          QSize,
                          QSizeF,
                          QRectF,
                          QDir
                          )
from PyQt4.QtXml import QDomDocument

from qgis.core import (
                       QgsComposition,
                       QgsComposerLabel,
                       QgsVectorLayer,
                       QgsFeature,
                       QgsGeometry,
                       QgsMapLayerRegistry
                       )

from sqlalchemy.exc import ProgrammingError
from sqlalchemy.sql.expression import text
from sqlalchemy.schema import (
                               Table,
                               MetaData
                               )
from sqlalchemy import (
                        Column,
                        func
                        )
from geoalchemy2 import Geometry

from stdm.settings import RegistryConfig
from stdm.data import STDMDb

from .composer_data_source import ComposerDataSource
from .spatial_fields_config import SpatialFieldsConfiguration
    
class DocumentGenerator(QObject):
    """
    Generates documents from user-defined templates.
    """
    
    #Output types
    Image = 0
    PDF = 1
    
    def __init__(self,iface,parent = None):
        QObject.__init__(self,parent)
        self._iface = iface
        self._mapRenderer = self._iface.mapCanvas().mapRenderer()
        
        self._dbSession = STDMDb.instance().session
        
        self._attrValueFormatters = {}
        
        #For cleanup after document compositions have been created
        self._memoryLayers = []
        
    def setAttrValueFormatters(self,formattermapping):
        '''
        Dictionary of attribute mappings and corresponding functions for 
        formatting the attribute value when naming an output file using 
        attribute values.
        '''
        self._attrValueFormatters = formattermapping
        
    def addAttrValueFormatter(self,attributeName,formatterFunc):
        '''
        Add a new attribute value formatter configuration to the collection
        '''
        self._attrValueFormatters[attributeName] = formatterFunc
        
    def AttrValueFormatters(self):
        """
        Returns a dictionary of attribute value formatters used by the document generators.
        """
        return self._attrValueFormatters
        
    def run(self,*args,**kwargs):
        """
        :param templatePath: The file path to the user-defined template.
        :param entityFieldName: The name of the column for the specified entity which
        must exist in the data source view or table.
        :param entityFieldValue: The value for filtering the records in the data source
        view or table.
        :param outputMode: Whether the output composition should be an image or PDF.
        :param filePath: The output file where the composition will be written to. Applies
        to single mode output generation.
        :param dataFields: List containing the field names whose values will be used to name the files.
        This is used in multiple mode configuration.
        :param fileExtension: The output file format. Used in multiple mode configuration.
        :param dbmodel: In order to name the files using the custom column mapping, a callable
        sqlalchemy data model must be specified.
        """
        #Unpack arguments
        templatePath = args[0]
        entityFieldName = args[1]
        entityFieldValue = args[2]
        outputMode = args[3]
        filePath = kwargs.get("filePath",None)
        dataFields = kwargs.get("dataFields",[])
        fileExtension = kwargs.get("fileExtension","")
        dataModel = kwargs.get("dbmodel",None)
        
        templateFile = QFile(templatePath)
        
        if not templateFile.open(QIODevice.ReadOnly):
            return (False,QApplication.translate("DocumentGenerator","Cannot read template file."))   
         
        templateDoc = QDomDocument()
        
        if templateDoc.setContent(templateFile):
            composerDS = ComposerDataSource.create(templateDoc)
            spatialFieldsConfig = SpatialFieldsConfiguration.create(templateDoc)
            composerDS.setSpatialFieldsConfig(spatialFieldsConfig)
            
            #Execute query
            dsTable,records = self._execQuery(composerDS.name(), entityFieldName, entityFieldValue)
            
            if records == None:
                return (False,QApplication.translate("DocumentGenerator","No matching records in the database"))
            
            """
            Iterate through records where a single file output will be generated for each matching record.
            """
            for rec in records:
                composition = QgsComposition(self._mapRenderer)
                composition.loadFromTemplate(templateDoc)
                
                #Set value of composer items based on the corresponding db values
                for composerId in composerDS.dataFieldMappings().reverse:
                    #Use composer item id since the uuid is stripped off
                    composerItem = composition.getComposerItemById(composerId)
                    
                    if composerItem != None:
                        fieldName = composerDS.dataFieldName(composerId)
                        fieldValue = getattr(rec,fieldName)
                        self._composerItemValueHandler(composerItem, fieldValue)
                            
                #Create memory layers for spatial features and add them to the map
                for mapId,spfmList in spatialFieldsConfig.spatialFieldsMapping().iteritems():
                    mapItem = composition.getComposerItemById(mapId)
                    
                    if mapItem!= None:
                        #Clear any previous memory layer
                        self.clearTemporaryLayers()
                        
                        for spfm in spfmList:
                            #Use the value of the label field to name the layer
                            layerName = getattr(rec,spfm.labelField())
                            
                            #Extract the geometry using geoalchemy spatial capabilities
                            geomFunc = getattr(rec,spfm.spatialField()).ST_AsText()
                            geomWKT = self._dbSession.scalar(geomFunc)
                            
                            #Create reference layer with feature
                            refLayer = self._buildVectorLayer(layerName)
                            
                            #Add feature
                            bbox = self._addFeatureToLayer(refLayer, geomWKT)
                            bbox.scale(spfm.zoomLevel())
                            
                            #Add layer to map
                            QgsMapLayerRegistry.instance().addMapLayer(refLayer)
                            self._iface.mapCanvas().setExtent(bbox)
                            self._iface.mapCanvas().refresh()
                            
                            #mapItem.storeCurrentLayerSet()
                            #mapItem.updateCachedImage()
                            
                            #Add layer to memory layer list
                            self._memoryLayers.append(refLayer)
                            
                        mapItem.setNewExtent(self._mapRenderer.extent())
                            
                #Build output path and generate composition
                if filePath != None and len(dataFields) == 0:
                    self._writeOutput(composition,outputMode,filePath) 
                    
                elif filePath == None and len(dataFields) > 0:
                    docFileName = self._buildFileName(dataModel,entityFieldName,entityFieldValue,dataFields,fileExtension)
                    if docFileName == "":
                        return (False,QApplication.translate("DocumentGenerator",
                                                             "File name could not be generated from the data fields."))
                        
                    outputDir = self._composerOutputPath()
                    if outputDir == None:
                        return (False,QApplication.translate("DocumentGenerator",
                                                             "System could not read the location of the output directory in the registry."))
                    
                    qDir = QDir()
                    if not qDir.exists(outputDir):
                        return (False,QApplication.translate("DocumentGenerator",
                                                             "Output directory does not exist"))
                    
                    absDocPath = unicode(outputDir) + "/" + docFileName
                    self._writeOutput(composition,outputMode,absDocPath)
            
            #Clear temporary layers
            self.clearTemporaryLayers()        
            
            return (True,"Success")
        
        return (False,"Composition could not be generated")
    
    def clearTemporaryLayers(self):
        """
        Clears all memory layers that were used to create the composition.
        """
        memoryLayerIds = [ml.id() for ml in self._memoryLayers]
        QgsMapLayerRegistry.instance().removeMapLayers(memoryLayerIds)
    
    def _buildVectorLayer(self,layerName):
        """
        Builds a memory vector layer based on the spatial field mapping properties.
        """
        refLayer = QgsVectorLayer("Polygon?crs=epsg:4326&field=name:string(20)&index=yes", layerName, "memory")
        
        return refLayer
    
    def _addFeatureToLayer(self,vlayer,geomWkb):
        """
        Create feature and add it to the vector layer.
        Return the extents of the geometry.
        """
        if not isinstance(vlayer, QgsVectorLayer):
            return
        
        dp = vlayer.dataProvider()
        
        feat = QgsFeature()
        g = QgsGeometry.fromWkt(geomWkb)
        feat.setGeometry(g)
        
        dp.addFeatures([feat])
        
        vlayer.updateExtents()
        
        return g.boundingBox()
    
    def _writeOutput(self,composition,outputMode,filePath):    
        """
        Write composition to file based on the output type (PDF or IMAGE).
        """  
        if outputMode == DocumentGenerator.Image:
            self._exportCompositionAsImage(composition,filePath)
        
        elif outputMode == DocumentGenerator.PDF:
            self._exportCompositionAsPDF(composition,filePath)
        
    def _exportCompositionAsImage(self,composition,filePath):  
        """
        Export the composition as a raster image.
        """                               
        #Image size
        dpi = composition.printResolution()
        dpmm = dpi / 25.4
        width = int(dpmm * composition.paperWidth())
        height = int(dpmm * composition.paperHeight())
        
        #Create output image and initialize it
        image = QImage(QSize(width,height),QImage.Format_ARGB32)
        image.setDotsPerMeterX(dpmm * 1000)
        image.setDotsPerMeterY(dpmm * 1000)
        image.fill(0)
        
        #Render the composition
        imagePainter = QPainter(image)
        sourceArea = QRectF(0,0,composition.paperWidth(),composition.paperHeight())
        targetArea = QRectF(0,0,width,height)
        composition.render(imagePainter,targetArea,sourceArea)
        imagePainter.end()
        
        image.save(filePath)
    
    def _exportCompositionAsPDF(self,composition,filePath):  
        """
        Render the composition as a PDF file.
        """
        printer = QPrinter()
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(filePath)
        printer.setPaperSize(QSizeF(composition.paperWidth(),composition.paperHeight()),QPrinter.Millimeter)
        printer.setFullPage(True)
        printer.setColorMode(QPrinter.Color)
        printer.setResolution(composition.printResolution())
        
        #Use painter to send output to printer
        pdfPainter = QPainter(printer)
        paperRectMM = printer.pageRect(QPrinter.Millimeter)
        paperRectPixel = printer.pageRect(QPrinter.DevicePixel)
        composition.render(pdfPainter,paperRectPixel,paperRectMM)
        pdfPainter.end()
    
    def _buildFileName(self,dataModel,fieldName,fieldValue,dataFields,fileExtension):
        """
        Build a file name based on the values of the specified data fields.
        """
        modelObj = dataModel()
        queryField = getattr(dataModel,fieldName)
        modelInstance = modelObj.queryObject().filter(queryField == fieldValue).first()
        
        if modelInstance != None:
            modelValues = []
            
            for dt in dataFields:
                fValue = getattr(modelInstance,dt)
                if fValue != None:
                    modelValues.append(unicode(fValue))
                    
            return "_".join(modelValues) + "." +fileExtension
            
        return ""

    def _execQuery(self,dataSourceName,queryField,queryValue):
        """
        Reflects the data source then execute the query using the specified
        query parameters.
        Returns a tuple containing the reflected table and results of the query.
        """
        meta = MetaData(bind = STDMDb.instance().engine)
        dsTable = Table(dataSourceName,meta,autoload = True)
        
        sql = "{0} = :qvalue".format(queryField)
        results = self._dbSession.query(dsTable).filter(sql).params(qvalue = queryValue).all()
        
        return (dsTable,results)
    
    def _composerOutputPath(self):
        """
        Returns the directory name of the composer output directory.
        """
        regConfig = RegistryConfig()
        keyName = "ComposerOutputs"
        
        valueCollection = regConfig.read([keyName])
        
        if len(valueCollection) == 0:
            return None
        
        else:
            return valueCollection[keyName]
    
    def _composerItemValueHandler(self,composerItem,value):
        """
        Factory for setting values based on the composer item type and value.
        """
        if isinstance(composerItem,QgsComposerLabel):
            if value == None:
                composerItem.setText("")
                return
            
            if isinstance(value,int) or isinstance(value,float) or isinstance(value,long):
                composerItem.setText(str(value))
                return
            
            #TODO: Rendering for photos
            composerItem.setText(value)
            return
            
    