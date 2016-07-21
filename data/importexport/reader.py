"""
/***************************************************************************
Name                 : OGRReader
Description          : Wrapper class for reading OGR data files. It only 
                       supports single layers for now.
Date                 : 5/March/2012
copyright            : (C) 2012 by UN-Habitat and implementing partners.
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

from stdm.data.database import (
    STDMDb,
    table_mapper
)
from stdm.ui.stdmdialog import DeclareMapping
from stdm.data.pg_utils import (
    delete_table_data,
    geometryType
)
from stdm.utils.util import getIndex

from .value_translators import (
    IgnoreType,
    ValueTranslatorManager
)

class OGRReader(object):
    def __init__(self, source_file):
        self._ds = ogr.Open(source_file)
        self._targetGeomColSRID = -1 
        self._geomType = ""
        self._dbSession = STDMDb.instance().session   
        self._mapped_class = None
                
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
        dsTable = Table(dataSourceName,meta,autoload=True)
        
        return dsTable

    def _get_mapped_class(self, table_name):
        return DeclareMapping.instance().tableMapping(table_name)
    
    def _insertRow(self, columnValueMapping):
        """
        Insert a new row using the mapped class instance then mapping column
        names to the corresponding column values.
        """
        model_instance = self._mapped_class()
        
        for col,value in columnValueMapping.iteritems():
            if hasattr(model_instance, col):
                '''
                #Check if column type is enumeration and transform accordingly
                col_is_enum, enum_symbol = self._enumeration_column_type(col, value)

                if col_is_enum:
                    value = enum_symbol
                '''
                if not isinstance(value, IgnoreType):
                    setattr(model_instance, col, value)

        try:
            self._dbSession.add(model_instance)
            self._dbSession.commit()

        except:
            self._dbSession.rollback()
            raise
    
    def featToDb(self, targettable , columnmatch, append, parentdialog,
                 geomColumn=None, geomCode=-1, translator_manager=ValueTranslatorManager()):
        """
        Performs the data import from the source layer to the STDM database.
        :param targettable: Destination table name
        :param columnmatch: Dictionary containing source columns as keys and target columns as the values.
        :param append: True to append, false to overwrite by deleting previous records
        :param parentdialog: A reference to the calling dialog.
        :param translator_manager: Instance of 'stdm.data.importexport.ValueTranslatorManager'
        containing value translators defined for the destination table columns.
        :type translator_manager: ValueTranslatorManager
        """
        #Delete existing rows in the target table if user has chosen to overwrite
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
        column_value_mapping = {}
        
        lyr = self.getLayer()
        lyr.ResetReading()
        feat_defn = lyr.GetLayerDefn()
        numFeat = lyr.GetFeatureCount() 
          
        #Configure progress dialog
        init_val = 0
        progress = QProgressDialog("", "&Cancel", init_val, numFeat,
                                   parentdialog)
        progress.setWindowModality(Qt.WindowModal)    
        lblMsgTemp = "Importing {0} of {1} to STDM..."  
           
        for feat in lyr:
            column_count = 0
            progress.setValue(init_val)
            progressMsg = lblMsgTemp.format((init_val + 1), numFeat)
            progress.setLabelText(progressMsg)
            
            if progress.wasCanceled():
                break
            
            for f in range(feat_defn.GetFieldCount()):
                field_defn = feat_defn.GetFieldDefn(f) 
                field_name = field_defn.GetNameRef()  
                
                #Append value only if it has been defined by the user                         
                if field_name in columnmatch:
                    dest_column = columnmatch[field_name]

                    field_value = feat.GetField(f)

                    '''
                    Check if there is a value translator defined for the specified destination column.
                    '''
                    value_translator = translator_manager.translator(dest_column)

                    if not value_translator is None:
                        source_col_names = value_translator.source_column_names()

                        field_value_mappings = self._map_column_values(feat, feat_defn,
                                                                       source_col_names)
                        field_value = value_translator.referencing_column_value(field_value_mappings)

                    if not isinstance(field_value, IgnoreType):
                            column_value_mapping[dest_column] = field_value

                    column_count += 1

                    #Create mapped table only once
                    if self._mapped_class is None:
                        #Execute only once, when all fields have been iterated
                        if column_count == len(columnmatch):
                            #Add geometry column to the mapping 
                            if geomColumn is not None:                                                                                                                    
                                column_value_mapping[geomColumn] = None
                                
                                #Use geometry column SRID in the target table
                                self._geomType,self._targetGeomColSRID = geometryType(targettable,
                                                                                      geomColumn)

                            mapped_class = self._get_mapped_class(targettable)

                            if mapped_class is None:
                                msg = QApplication.translate("OGRReader",
                                                             "Something happened that caused the database table " \
                                      "not to be mapped to the corresponding model class. Please try again.")

                                raise RuntimeError(msg)
                                
                            self._mapped_class = mapped_class
                                                       
            #Only insert geometry if it has been defined by the user
            if geomColumn is not None:
                geom = feat.GetGeometryRef()
                
                if geom is not None:
                    #Get geometry in WKT/WKB format
                    geomWkb = geom.ExportToWkt()
                    column_value_mapping[geomColumn] = "SRID={0!s};{1}".format(self._targetGeomColSRID,geomWkb)
                    
                    #Check if the geometry types match
                    layerGeomType = geom.GetGeometryName()
                    
                    if layerGeomType.lower() != self._geomType.lower():
                        raise TypeError("The geometries of the source and destination columns do not match.\n" \
                                        "Source Geometry Type: {0}, Destination Geometry Type: {1}".format(layerGeomType,
                                                                                                           self._geomType))
                        return
            
            try:               
                #Insert the record
                self._insertRow(column_value_mapping)

            except:
                progress.close()
                raise
            
            init_val+=1
            
        progress.setValue(numFeat)

    def _enumeration_column_type(self, column_name, value):
        """
        Checks if the given column is of DeclEnumType.
        :param column_name: Name of the enumeration column.
        :type column_name: str
        :return: True if column is of DeclType and return Enum symbol;
        Else, False and None.
        :rtype: tuple
        """
        try:
            #Get column type of the enumeration
            enum_col_type = self._mapped_class.__mapper__.columns[column_name].type
        except KeyError:
            return False, None

        if not hasattr(enum_col_type, "enum"):
            return False, None

        else:
            enum_obj = enum_col_type.enum

            try:
                if not isinstance(value, str) or not isinstance(value, unicode):
                    value = unicode(value)

                enum_symbol = enum_obj.from_string(value.strip())

            except ValueError:
                enum_symbol = IgnoreType()

            return True, enum_symbol

    def _map_column_values(self, feature, feature_defn, source_cols):
        """
        Retrieves values for specific columns from the specified feature.
        :param feature: Input feature.
        :type feature: ogr.Feature
        :param feature_defn: Feature definition for the layer.
        :type feature_defn: ogr.FeatureDefn
        :param source_cols: List of columns whose respective values will be
        retrieved.
        :type source_cols: list
        :return: Collection containing pairs of column names and corresponding
        values.
        :rtype: dict
        """
        col_values = {}

        if len(source_cols) == 0:
            return col_values

        for f in range(feature_defn.GetFieldCount()):
            field_defn = feature_defn.GetFieldDefn(f)
            field_name = field_defn.GetNameRef()

            match_idx = getIndex(source_cols, field_name)
            if match_idx != -1:
                field_value = feature.GetField(f)

                col_values[field_name] = field_value

        return col_values
        
            

        
        
