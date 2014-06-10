#begin:            26th March 2012
#copyright:        (c) 2012 by John Gitau
#email:            gkahiu@gmail.com
#about:            Wrapper class for writing PostgreSQL/PostGIS tables to user-defined OGR formats

import sys, logging

from PyQt4.QtCore import *
from PyQt4.QtGui import *

try:
    from osgeo import gdal
    from osgeo import ogr
except:
    import gdal
    import ogr

from stdm.data import (
                       columnType,
                       geometryType
                       )
from enums import *

class OGRWriter():
   
    def __init__(self,targetFile): 
        self._ds=None 
        self._targetFile = targetFile
        
    def reset(self):
        #Destroy
        self._ds = None
        
    def getDriverName(self):
        #Return the name of the driver derived from the file extension
        fi = QFileInfo(self._targetFile)
        fileExt = str(fi.suffix())
        
        return drivers[fileExt]  
    
    def getLayerName(self):
        #Simply derived from the file name
        fi = QFileInfo(self._targetFile)
        
        return str(fi.baseName()) 
    
    def createField(self,table,field):
        #Creates an OGR field
        colType = columnType(table,field)
        
        #Get OGR type
        ogrType = ogrTypes[colType]
        field_defn = ogr.FieldDefn(field,ogrType)
        
        return field_defn
        
    def db2Feat(self,parent,table,results,columns,geom=""):
        #Execute the export process
        #Create driver
        drv = ogr.GetDriverByName(self.getDriverName())        
        if drv is None:
            raise Exception("{0} driver not available.".format(self.getDriverName()))
        
        #Create data source
        self._ds = drv.CreateDataSource(self._targetFile)
        if self._ds is None:
            raise Exception("Creation of output file failed.")
        
        #Create layer
        if geom != "":
            pgGeomType,srid = geometryType(table,geom)
            geomType = wkbTypes[pgGeomType]
            
        else:
            geomType=ogr.wkbNone
            
        lyr = self._ds.CreateLayer(self.getLayerName(),None,geomType)
        
        if lyr is None:
            raise Exception("Layer creation failed")
        
        #Create fields
        for c in columns:
            #SQLAlchemy string values are in unicode so decoding is required in order to use in OGR
            encodedFieldName = c.encode('utf-8')
            field_defn = self.createField(table,encodedFieldName)
            if lyr.CreateField(field_defn) != 0:
                raise Exception("Creating %s field failed"%(c))
            
        #Add Geometry column to list for referencing in the result set
        if geom != "":
            columns.append(geom) 
            
        featGeom=None  
             
        #Configure progress dialog
        initVal=0 
        numFeat = results.rowcount
        progress = QProgressDialog("","&Cancel",initVal,numFeat,parent)        
        progress.setWindowModality(Qt.WindowModal)    
        lblMsgTemp = "Writing {0} of {1} to file..." 
         
        #Iterate the result set        
        for r in results:
            #Progress dialog 
            progress.setValue(initVal) 
            progressMsg = lblMsgTemp.format(str(initVal+1),str(numFeat))
            progress.setLabelText(progressMsg)
            
            if progress.wasCanceled():
                break  
            
            #Create OGR Feature
            feat = ogr.Feature(lyr.GetLayerDefn())    
                    
            for i in range(len(columns)):
                colName = columns[i]   
                             
                #Check if its the geometry column in the iteration
                if colName==geom: 
                    if r[i] is not None:                                                                               
                        featGeom=ogr.CreateGeometryFromWkt(r[i])
                    else:
                        featGeom=ogr.CreateGeometryFromWkt("")
                        
                    feat.SetGeometry(featGeom)
                    
                else:
                    fieldValue = r[i]  
                    if isinstance(fieldValue,unicode):
                        fieldValue = fieldValue.encode('utf-8')
                        
                    feat.SetField(i,fieldValue)
                          
            if lyr.CreateFeature(feat) != 0:
                progress.close()
                raise Exception("Failed to create feature in %s"%(self._targetFile))
            
            if featGeom is not None:                
                featGeom.Destroy()
                
            feat.Destroy()
            initVal+=1
            
        progress.setValue(numFeat)
                
  
        
            

        
        