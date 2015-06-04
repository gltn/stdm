"""
/***************************************************************************
Name                 : OGRReader
Description          : Wrapper class for reading OGR data files. It only 
                       supports single layers for now.
Date                 : 5/March/2012
copyright            : (C) 2012 by John Gitau
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
import logging
import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

try:
    from osgeo import gdal
    from osgeo import ogr
except:
    import gdal
    import ogr

import sqlalchemy
from sqlalchemy.schema import (
                               Table,
                               MetaData
                               )
from sqlalchemy.orm import (
                            mapper,
                            class_mapper
                            )

from stdm.data import (
                       delete_table_data,
                       STDMDb,
                       geometryType
                       )

class _ReflectedModel(object):
    """
    Placeholder model for the reflected database table.
    """
    pass

class OGRReader(object):
    def __init__(self, sourceFile = None):
        # self._ds = ogr.Open(sourceFile)
        try:
            self._ds = ogr.Open(sourceFile)
        except RuntimeError:
            pass
        self._targetGeomColSRID = -1 
        self._geomType = ""
        self._dbSession = STDMDb.instance().session   
        self._mappedClass = None 
                
    def getLayer(self):
        #Return the first layer in the data source
        if self.isValid():
            numLayers = self._ds.GetLayerCount()
            if numLayers > 0:                
                return self._ds.GetLayer(0)
            else:
                return None
            
    def getSpatialRefCode(self):
        #Get the EPSG code (More work required)
        if self.getLayer() != None:
            spRef = self.getLayer().GetSpatialRef()
            refCode = spRef.GetAttrValue("PRIMEM|AUTHORITY", 1)
            
        else:
            #Fallback to WGS84
            refCode = 4326
            
        return refCode
        
    def isValid(self):
        #Whether the open process succeeded or failed
        if self._ds is None:
            return False
        else:
            return True
        
    def reset(self):
        #Destroy
        self._ds=None
        self._geomType = ""
        self._targetGeomColSRID = -1
        
    def getFields(self):
        #Return the data source's fields in a list
        fields = []
        lyr = self.getLayer()
        lyr.ResetReading()
        feat_defn = lyr.GetLayerDefn()
        
        for l in range(feat_defn.GetFieldCount()):
            field_defn = feat_defn.GetFieldDefn(l)
            fields.append(str(field_defn.GetNameRef()))
            
        return fields
    
    def _mapTable(self,dataSourceName):
        """
        Reflect the data source.
        """
        meta = MetaData(bind = STDMDb.instance().engine)
        dsTable = Table(dataSourceName,meta,autoload = True)
        
        return dsTable
    
    def _insertRow(self,columnValueMapping):
        """
        Insert a new row using the mapped class instance then mapping column names to the corresponding column values.
        """
        modelInstance = self._mappedClass()
        
        for col,value in columnValueMapping.iteritems():
            if hasattr(modelInstance,col):

                setattr(modelInstance,col,value)
        #raise NameError(str(dir(modelInstance)))
        try:
            self._dbSession.add(modelInstance)
            self._dbSession.commit()
        except Exception as ex:
            raise 
        finally:
            self._dbSession.rollback()
    
    def featToDb(self,targettable,columnmatch,append,parentdialog,geomColumn=None,geomCode=-1):
        '''
        Performs the data import from the source layer to the STDM database.
        :param targettable: Destination table name
        :param columnmatch: Dictionary containing source columns as keys and target columns as the values
        :param append: True to append, false to overwrite by deleting previous records
        :param parentdialog: A reference to the calling dialog
        ''' 
        #Delete existing rows if user has chosen to overwrite
        if not append:
            delete_table_data(targettable)
            
        """
        #Debug logging
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(levelname)s %(message)s',
                            filename='stdm.log',
                            filemode='w')        
        """
              
        #Container for mapping column names to their corresponding values
        columnValueMapping = {}
        
        lyr = self.getLayer()
        lyr.ResetReading()
        feat_defn = lyr.GetLayerDefn()
        numFeat = lyr.GetFeatureCount() 
          
        #Configure progress dialog
        initVal = 0 
        progress = QProgressDialog("","&Cancel",initVal,numFeat,parentdialog)
        progress.setWindowModality(Qt.WindowModal)    
        lblMsgTemp = "Importing {0} of {1} to STDM..."  
           
        for feat in lyr: 
            progress.setValue(initVal) 
            progressMsg = lblMsgTemp.format(str(initVal+1),str(numFeat))
            progress.setLabelText(progressMsg)
            
            if progress.wasCanceled():
                break
            
            for f in range(feat_defn.GetFieldCount()):
                field_defn = feat_defn.GetFieldDefn(f) 
                field_name = field_defn.GetNameRef()  
                
                #Append value only if it has been defined by the user                         
                if field_name in columnmatch:
                    fieldValue = feat.GetField(f)  
                    columnValueMapping[columnmatch[field_name]] = fieldValue
                    
                    #Create mapped table only once
                    if self._mappedClass == None:
                        
                        #Execute only once, when all fields have been iterated
                        if len(columnValueMapping.keys()) == len(columnmatch):                             
                            #Add geometry column to the mapping 
                            if geomColumn is not None:                                                                                                                    
                                columnValueMapping[geomColumn] = None 
                                
                                #Use geometry column SRID in the target table
                                self._geomType,self._targetGeomColSRID = geometryType(targettable,geomColumn)
                            
                            try:
                                primaryMapper = class_mapper(_ReflectedModel) 
                                
                            except (sqlalchemy.orm.exc.UnmappedClassError,sqlalchemy.exc.ArgumentError):     
                                #Reflect table and map it to '_ReflectedModel' class only once                                                                        
                                mapper(_ReflectedModel,self._mapTable(targettable))
                                
                            self._mappedClass = _ReflectedModel
                                                       
            #Only insert geometry if it has been defined by the user
            if geomColumn is not None:
                geom = feat.GetGeometryRef()
                
                if geom is not None:
                    #Get geometry in WKT/WKB format
                    geomWkb = geom.ExportToWkt()
                    columnValueMapping[geomColumn] = "SRID={0!s};{1}".format(self._targetGeomColSRID,geomWkb)
                    
                    #Check if the geometry types match
                    layerGeomType = geom.GetGeometryName()
                    
                    if layerGeomType.lower() != self._geomType.lower():
                        raise TypeError("The geometries of the source and destination columns do not match.\n" \
                                        "Source Geometry Type: {0}, Destination Geometry Type: {1}".format(layerGeomType,
                                                                                                           self._geomType))
                        return
    
            #logging.debug()
            
            try:               
                #Insert the record
                self._insertRow(columnValueMapping)
            except:
                progress.close()
                raise
            
            initVal+=1
            
        progress.setValue(numFeat)
        
            

        
        
