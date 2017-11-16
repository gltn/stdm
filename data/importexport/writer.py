#begin:            26th March 2012
#copyright:        (c) 2012 by John Gitau
#email:            gkahiu@gmail.com
#about:            Wrapper class for writing PostgreSQL/PostGIS tables to user-defined OGR formats
import decimal

import sys, logging
import datetime
from PyQt4.QtCore import *
from PyQt4.QtGui import *

try:
    from osgeo import gdal
    from osgeo import ogr
except:
    import gdal
    import ogr

from stdm.data.pg_utils import (
    columnType,
    geometryType,
    pg_views
)
from stdm.utils.util import (
    date_from_string,
    datetime_from_string
)
from stdm.settings import (
    current_profile,
    save_configuration
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

        colType = columnType(table, field)
        #Get OGR type
        ogrType = ogrTypes[colType]

        field_defn = ogr.FieldDefn(field.encode('utf-8'), ogrType)

        return field_defn
        
    def db2Feat(self,parent,table,results,columns,geom=""):
        #Execute the export process
        #Create driver
        drv = ogr.GetDriverByName(self.getDriverName())        
        if drv is None:
            raise Exception(u"{0} driver not available.".format(self.getDriverName()))
        
        #Create data source
        self._ds = drv.CreateDataSource(self._targetFile)
        if self._ds is None:
            raise Exception("Creation of output file failed.")
        dest_crs = None
        #Create layer
        if geom != "":
            pgGeomType,srid = geometryType(table,geom)
            geomType = wkbTypes[pgGeomType]
            dest_crs = ogr.osr.SpatialReference()
            dest_crs.ImportFromEPSG(srid)

        else:
            geomType=ogr.wkbNone
        layer_name = self.getLayerName()

        lyr = self._ds.CreateLayer(layer_name, dest_crs, geomType)
        
        if lyr is None:
            raise Exception("Layer creation failed")

        #Create fields
        for c in columns:

            field_defn = self.createField(table, c)

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

        entity = current_profile().entity_by_name(table)
        #Iterate the result set
        for r in results:
            #Progress dialog 
            progress.setValue(initVal) 
            progressMsg = lblMsgTemp.format(str(initVal+1), str(numFeat))
            progress.setLabelText(progressMsg)
            
            if progress.wasCanceled():
                break  
            
            #Create OGR Feature
            feat = ogr.Feature(lyr.GetLayerDefn())

            for i in range(len(columns)):
                colName = columns[i]

                #Check if its the geometry column in the iteration
                if colName == geom:
                    if r[i] is not None:
                        featGeom = ogr.CreateGeometryFromWkt(r[i])
                    else:
                        featGeom = ogr.CreateGeometryFromWkt("")
                        
                    feat.SetGeometry(featGeom)
                    
                else:

                    if isinstance(r[i], decimal.Decimal):

                        value = int(r[i])
                        feat.setField(i, value)

                    elif self.is_date(r[i]):
                        date = datetime.datetime.strptime(r[i], "%Y-%m-%d").date()
                        feat.setField(i, date)
                    else:
                        feat.SetField(i, r[i])

            if lyr.CreateFeature(feat) != 0:
                progress.close()
                raise Exception(
                    "Failed to create feature in %s"%(self._targetFile)
                )
            
            if featGeom is not None:                
                featGeom.Destroy()
                
            feat.Destroy()
            initVal+=1
            
        progress.setValue(numFeat)

    @staticmethod
    def is_date(string):
        try:
            date = datetime.datetime.strptime(string, "%Y-%m-%d").date()

            return True
        except Exception:
            return False

    def is_decimal(self, number):
        try:
            n = round(number)

            return True
        except Exception:
            return False

        