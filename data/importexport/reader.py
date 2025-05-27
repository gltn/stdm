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
import os
import re

from PyQt4.QtCore import *
from PyQt4.QtGui import *

try:
    from osgeo import gdal
    from osgeo import ogr
except:
    import gdal
    import ogr

from sqlalchemy.exc import DataError, IntegrityError

from stdm.data.pg_utils import (
    delete_table_data,
    geometryType,
    execute_query,
    create_ms_record,
    get_lookup_data
)

from stdm.utils.util import (
        getIndex, 
        mapfile_section,
        get_working_mapfile,
        get_import_logfile
    )

from stdm.settings import (
    current_profile
)

from stdm.data.database import (
    STDMDb
)

from stdm.data.importexport.value_translators import (
    IgnoreType,
    ValueTranslatorManager
)
from stdm.data.configuration import entity_model
from stdm.data.configuration.exception import ConfigurationException
from stdm.ui.sourcedocument import SourceDocumentManager

from stdm.ui.support_doc_manager import (
        SupportDocManager,
        ImportLogger
        )

class ImportFeatureException(Exception):
    """
    Rasied when an error during feature import.
    """


class OGRReader(object):
    def __init__(self, source_file):
        self._ds = ogr.Open(source_file)
        self._targetGeomColSRID = -1
        self._geomType = ''
        self._dbSession = STDMDb.instance().session
        self._mapped_cls = None
        self._mapped_doc_cls = None
        self._current_profile = current_profile()
        self._source_doc_manager = None

    def getLayer(self):
        # Return the first layer in the data source
        if self.isValid():
            numLayers = self._ds.GetLayerCount()
            if numLayers > 0:
                return self._ds.GetLayer(0)

            else:
                return None

    def getSpatialRefCode(self):
        # Get the EPSG code (More work required)
        if self.getLayer() != None:
            spRef = self.getLayer().GetSpatialRef()
            refCode = spRef.GetAttrValue("PRIMEM|AUTHORITY", 1)

        else:
            # Fallback to WGS84
            refCode = 4326

        return refCode

    def isValid(self):
        # Whether the open process succeeded or failed
        if self._ds is None:
            return False
        else:
            return True

    def reset(self):
        # Destroy
        self._ds = None
        self._geomType = ""
        self._targetGeomColSRID = -1

    def getFields(self):
        # Return the data source's fields in a list
        fields = []
        lyr = self.getLayer()
        lyr.ResetReading()
        feat_defn = lyr.GetLayerDefn()

        for l in range(feat_defn.GetFieldCount()):
            field_defn = feat_defn.GetFieldDefn(l)
            fields.append(unicode(field_defn.GetNameRef(),'utf-8'))

        return fields

    def _data_source_entity(self, table_name):
        entity = self._current_profile.entity_by_name(table_name)

        return entity

    def entity_virtual_columns(self, table_name):
        """
        :param table_name: Name of the target table.
        :type table_name: str
        :return: Returns a list of derived columns for the specified target table.
        :rtype: list
        """
        entity = self._data_source_entity(table_name)

        if entity is None:
            return []

        return entity.virtual_columns()

    def _get_mapped_class(self, table_name):
        # Get entity from the corresponding table name
        entity = self._data_source_entity(table_name)

        if entity is None:
            return None

        ent_model, doc_model = entity_model(entity,
                                            with_supporting_document=True)

        return ent_model, doc_model

    def auto_fix_percent(self, target_table, col_a_name, value):
        """
        Fixes percent columns if empty and with a wrong format.
        :param target_table: The destination table name
        :type target_table: String
        :param col_a_name: The destination column name
        :type col_a_name: String
        :param value: Value to be saved to the DB
        :type value: Any
        :return: Converted value
        :rtype: Any
        """
        entity = self._data_source_entity(target_table)

        if entity.columns[col_a_name].TYPE_INFO == 'PERCENT':
            if isinstance(value, str):
                if not bool(value.strip()) or value.strip().lower() == 'null':
                    value = None
            if '%' in value:
                value = value.replace('%', '')
            try:
                if value is not None:
                    value = float(value)

            except ValueError:
                value = None

        return value

    def auto_fix_float_integer(self, target_table, col_a_name, value):
        """
        Fixes float and integer columns if empty and with a wrong format.
        :param target_table: The destination table name
        :type target_table: String
        :param col_a_name: The destination column name
        :type col_a_name: String
        :param value: Value to be saved to the DB
        :type value: Any
        :return: Converted value
        :rtype: Any
        """
        entity = self._data_source_entity(target_table)
        integer_types = ['INT', 'LOOKUP', 'ADMIN_SPATIAL_UNIT',
                         'FOREIGN_KEY', 'DOUBLE']
        float_type = ['DOUBLE']
        int_type = ['INT', 'LOOKUP', 'ADMIN_SPATIAL_UNIT',
                    'FOREIGN_KEY']

        if col_a_name in entity.columns.keys():
            if entity.columns[col_a_name].TYPE_INFO in integer_types:
                if isinstance(value, str):
                    if not bool(value.strip()) or value.strip().lower() == 'null':
                        value = None
                if entity.columns[col_a_name].TYPE_INFO in float_type:
                    try:
                        if value is not None:
                            value = float(value)

                    except ValueError:
                        value = None

                elif entity.columns[col_a_name].TYPE_INFO in int_type:
                    try:
                        if value is not None:
                            value = int(value)
                            if isinstance(value, int):
                                if value == 0:
                                    if entity.columns[col_a_name].TYPE_INFO in \
                                        ['LOOKUP', 'ADMIN_SPATIAL_UNIT',
                                        'FOREIGN_KEY']:
                                        value = None
                    except:
                        #TODO show warning to the user that
                        #  some values cannot be converted to integer.
                        value = None
                    
        return value

    def auto_fix_date(self, target_table, col_a_name, value):
        """
        Fixes date and datetime columns if empty and with a wrong format.
        :param target_table: The destination table name
        :type target_table: String
        :param col_a_name: The destination column name
        :type col_a_name: String
        :param value: Value to be saved to the DB
        :type value: Any
        :return: Converted value
        :rtype: Any
        """
        entity = self._data_source_entity(target_table)

        date_types = ['DATE', 'DATETIME']

        if entity.columns[col_a_name].TYPE_INFO in date_types:
            if not bool(value) or value.lower() == 'null':
                value = None

        return value

    def auto_fix_yes_no(self, target_table, col_a_name, value):
        """
        Fixes Yes_NO columns if empty and with a wrong format.
        :param target_table: The destination table name
        :type target_table: String
        :param col_a_name: The destination column name
        :type col_a_name: String
        :param value: Value to be saved to the DB
        :type value: Any
        :return: Converted value
        :rtype: Any
        """
        entity = self._data_source_entity(target_table)
        yes_no_types = ['BOOL']
       
        if entity.columns[col_a_name].TYPE_INFO in yes_no_types:
            if not bool(value.strip()) or value.strip().lower() == 'null':
                value = None
            elif value.strip().lower() == 'yes':
                value = True
            elif value.strip().lower() == 'no':
                value = False
            elif value.strip().lower() == 'true':
                value = True
            elif value.strip().lower() == 'false':
                value = False
        return value

    def update_geom_column(self, target_table, geom_loc, ref_code):
        """
        Updates the geometry data for an existing property record
        :param target_table: Table with containing geometry column
        :type target_table: str
        :param geom_loc: String containing geometry data
        :type geom_loc: str
        :param ref_code: Reference code to use to search record to update
                         in the target_table
        :type ref_code: str
        """
        upd_sql = "Update {} set geom_location = {} where reference_code = '{}'".format(target_table, geom_loc, ref_code)
        execute_query(upd_sql)

    def _insertRow(self, target_table, columnValueMapping):
        """
        Insert a new row using the mapped class instance then mapping column
        names to the corresponding column values.
        """
        model_instance = self._mapped_cls()

        for col, value in columnValueMapping.iteritems():

            if hasattr(model_instance, col):
                '''
                #Check if column type is enumeration and transform accordingly
                col_a_is_enum, enum_symbol = self._enumeration_column_type(col, value)

                if col_a_is_enum:
                    value = enum_symbol
                '''
                # documents is not a column so exclude it.
                if col != 'documents':

                    value = self.auto_fix_float_integer(target_table, col,
                                                        value)
                    value = self.auto_fix_percent(target_table, col, value)
                    value = self.auto_fix_date(target_table, col, value)
                    value = self.auto_fix_yes_no(target_table, col, value)

                if not isinstance(value, IgnoreType):
                    setattr(model_instance, col, value)

        last_id = -1
        try:
            self._dbSession.add(model_instance)
            self._dbSession.flush()
            last_id = model_instance.id
            self._dbSession.commit()
        except (DataError, IntegrityError) as e:
            self._dbSession.rollback()
            raise ImportFeatureException(str(e))
        return last_id

    def auto_fix_geom_type(self, geom, source_geom_type, destination_geom_type):
        """
        Converts single geometry type to multi type if the destination is multi type.
        :param geom: The OGR geometry
        :type geom: OGRGeometry
        :param source_geom_type: Source geometry type
        :type source_geom_type: String
        :param destination_geom_type: Destination geometry type
        :type destination_geom_type: String
        :return: WkB geometry and the output layer geometry type.
        :rtype: Tuple
        """
        # Convert polygon to multipolygon if the destination table is multi-polygon.
        if source_geom_type.lower() == 'polygon' and \
                        destination_geom_type.lower() == 'multipolygon':
            geom_wkb, geom_type = self.to_ogr_multi_type(geom,
                                                            ogr.wkbMultiPolygon)

        elif source_geom_type.lower() == 'linestring' and \
                        destination_geom_type.lower() == 'multilinestring':
            geom_wkb, geom_type = self.to_ogr_multi_type(geom,
                                                            ogr.wkbMultiLineString)

        elif source_geom_type.lower() == 'point' and \
                        destination_geom_type.lower() == 'multipoint':
            geom_wkb, geom_type = self.to_ogr_multi_type(geom, ogr.wkbMultiPoint)
        else:
            geom_wkb = geom.ExportToWkt()
            geom_type = geom.GetGeometryName()

        return geom_wkb, geom_type

    def to_ogr_multi_type(self, geom, ogr_type):
        """
        Convert ogr geometry to multi-type when supplied the ogr.type.
        :param geom: The ogr geometry
        :type geom: OGRGeometry
        :param ogr_type: The ogr geometry type
        :type ogr_type: String
        :return: WkB geometry and the output layer geometry type.
        :rtype: Tuple
        """
        multi_geom = ogr.Geometry(ogr_type)
        multi_geom.AddGeometry(geom)
        geom_wkb = multi_geom.ExportToWkt()
        geom_type = multi_geom.GetGeometryName()
        return geom_wkb, geom_type

    def featToDb(self, targettable, columnmatch, append, parentdialog, 
            unique_data={}, lost_documents={}, geomColumn=None, geomCode=-1,
            update_geom_column_only=False, translator_manager=None, docs_only=False):
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
        target_table = targettable[3:]
        working_mapfile = get_working_mapfile(target_table)

        multi_select_src_column = ''
        multi_select_dest_table = ''
        multiple_selection = []
        multi_select_lookup_table = ''
        if len(lost_documents) > 0:
            multi_select = mapfile_section(working_mapfile, target_table+'-multiple_select')
            multi_select_src_column = multi_select['src_column']
            multi_select_dest_table = multi_select['dest_table']
            multi_select_lookup_table = multi_select['lookup_table']

        sdoc_manager = SupportDocManager(target_table, working_mapfile)
            
        # Check current profile
        if self._current_profile is None:
            msg = QApplication.translate(
                'OGRReader',
                'The current profile could not be determined.\nPlease set it '
                'in the Options dialog or Configuration Wizard.'
            )
            raise ConfigurationException(msg)

        if translator_manager is None:
            translator_manager = ValueTranslatorManager()

        # Delete existing rows in the target table if user has chosen to overwrite
        if not append:
            delete_table_data(targettable)

        # Container for mapping column names to their corresponding values

        lyr = self.getLayer()
        lyr.ResetReading()
        feat_defn = lyr.GetLayerDefn()
        numFeat = lyr.GetFeatureCount()

        # Configure progress dialog
        init_val = 0
        progress = QProgressDialog("", "&Cancel", init_val, numFeat,
                parentdialog)
        progress.setWindowModality(Qt.WindowModal)
        lblMsgTemp = "Importing {0} of {1} to STDM..."

        # Set entity for use in translators
        destination_entity = self._data_source_entity(targettable)

        acols = {}
        for k,v in columnmatch.iteritems():
            acols[k.encode('ascii', 'ignore')]= v

        # rows in the file
        import_logfile = get_import_logfile()
        import_logger = ImportLogger(import_logfile, target_table);
        row_ids = []

        start_data_row = 2
        row_count = 1
        for r_count, feat in enumerate(lyr):
            if row_count < start_data_row:
                row_count += 1
                continue
            column_value_mapping = {}
            column_count = 0
            progress.setValue(init_val)
            progressMsg = lblMsgTemp.format((init_val + 1), numFeat)
            progress.setLabelText(progressMsg)

            if progress.wasCanceled():
                break

            # Reset source document manager for new records
            if destination_entity.supports_documents:
                if not self._source_doc_manager is None:
                    self._source_doc_manager.reset()

            # columns in the file
            for f in range(feat_defn.GetFieldCount()):
                field_defn = feat_defn.GetFieldDefn(f)
                field_name = field_defn.GetNameRef()

                # Append value only if it has been defined by the user
                #if field_name in columnmatch:
                    #dest_column = columnmatch[field_name]
                a_field_name = unicode(field_name, 'utf-8').encode('ascii', 'ignore')
                if a_field_name in acols:
                    dest_column = acols[a_field_name]

                    #field_value = feat.GetField(f)
                    field_value = unicode(feat.GetField(f), 'utf-8')

                    if sdoc_manager.download_docs:
                        if sdoc_manager.support_doc_column(a_field_name) and field_value != '':
                            sdoc_manager.append_doc(r_count, a_field_name, field_value)

                    # Check if the value already exists for unique columns
                    if dest_column in unique_data:
                        if field_value in unique_data[dest_column]:
                            #print "Record with same unique value already exists - ",field_value
                            continue
                        else:
                            unique_data[dest_column].append(field_value)

                    # Check if this is multiple select column
                    if a_field_name == multi_select_src_column:
                       multiple_selection = self.find_multi_select_id(field_value, lost_documents)

                    # Create mapped class only once
                    if self._mapped_cls is None:
                        mapped_cls, mapped_doc_cls = self._get_mapped_class(
                            targettable)

                        if mapped_cls is None:
                            msg = QApplication.translate(
                                "OGRReader",
                                "Something happened that caused the "
                                "database table not to be mapped to the "
                                "corresponding model class. Please contact"
                                " your system administrator."
                            )

                            raise RuntimeError(msg)

                        self._mapped_cls = mapped_cls
                        self._mapped_doc_cls = mapped_doc_cls

                        # Create source document manager if the entity supports them
                        if destination_entity.supports_documents:
                            self._source_doc_manager = SourceDocumentManager(
                                destination_entity.supporting_doc,
                                self._mapped_doc_cls
                            )

                        if geomColumn is not None:
                            # Use geometry column SRID in the target table
                            self._geomType, self._targetGeomColSRID = \
                                geometryType(targettable, geomColumn)

                    '''
                    Check if there is a value translator defined for the
                    specified destination column.
                    '''
                    value_translator = translator_manager.translator(
                        dest_column)

                    if value_translator is not None:
                        # Set destination table entity
                        value_translator.entity = destination_entity

                        source_col_a_names = value_translator.source_column_names()

                        field_value_mappings = self._map_column_values(feat,
                                                                       feat_defn,
                                                                       source_col_a_names)
                        # Set source document manager if required
                        if value_translator.requires_source_document_manager:
                            value_translator.source_document_manager = self._source_doc_manager

                        field_value = value_translator.referencing_column_value(
                            field_value_mappings
                        )


                    if not isinstance(field_value, IgnoreType):
                        column_value_mapping[dest_column] = field_value

                    # Set supporting documents
                    if destination_entity.supports_documents:
                        column_value_mapping['documents'] = \
                            self._source_doc_manager.model_objects()

                    column_count += 1

            # Only insert geometry if it has been defined by the user
            if geomColumn is not None:
                geom = feat.GetGeometryRef()

                if geom is not None:
                    # Check if the geometry types match
                    layerGeomType = geom.GetGeometryName()
                    # Convert polygon to multipolygon if the destination table is multi-polygon.
                    geom_wkb, geom_type = self.auto_fix_geom_type(
                        geom, layerGeomType, self._geomType)
                    column_value_mapping[geomColumn] = "SRID={0!s};{1}".format(
                        self._targetGeomColSRID, geom_wkb)

                    upd_geom_col = "ST_GeomFromText('{0}',{1})".format(geom_wkb, self._targetGeomColSRID)

                    if geom_type.lower() != self._geomType.lower():
                        raise TypeError(
                            "The geometries of the source and destination columns do not match.\n" \
                            "Source Geometry Type: {0}, Destination Geometry Type: {1}".format(
                                geom_type,
                                self._geomType))

            try:
                # Insert the record
                if update_geom_column_only:
                    self.update_geom_column(targettable, upd_geom_col, column_value_mapping['reference_code'])
                else:
                    last_id = self._insertRow(targettable, column_value_mapping)

                    # process multiple selection
                    if len(multiple_selection) > 0:
                        self.create_multiple_select_records(targettable, last_id,
                                multi_select_dest_table, multiple_selection,
                                multi_select_lookup_table)

                    row_ids.append(last_id) #
                    if sdoc_manager.download_docs:
                        sdoc_manager.update_parent_id(r_count, last_id)
            except:
                progress.close()
                raise

            init_val += 1

        progress.setValue(numFeat)

        if len(row_ids) > 0:
            import_logger.min_row_id = min(row_ids)
            import_logger.max_row_id = max(row_ids)
        else:
            import_logger.min_row_id = 0
            import_logger.max_row_id = 0
        import_logger.write()

        return sdoc_manager

    def find_multi_select_id(self, field_value, lost_documents):
        """
        """
        selection_ids = []
        values = re.split('(\d+)', field_value)
        if values[0].strip() == '':
            values.pop(0)
        sel_options = [i+j for i,j in zip(values[::2], values[1::2])]
        for option in sel_options:
            for id, value in lost_documents.items():
                if option.strip() == value:
                    selection_ids.append(id)
        return selection_ids


    def create_multiple_select_records(self, target_table, target_table_id,
            multi_select_dest_table, multiple_selection, multi_select_lookup_table):
        """
        :param target_table: Parent table for the record that has done the selection
        :type target_table: str

        :param target_table_id: ID of the record that has done the selection - last id
        :type target_table_id: int

        :param multi_select_dest_table: Table to store selections - hl_lost_documents
        :type multi_select_dest_table: str

        :param multiple_selection: List with ids for the selected options
        :type multiple_selection : list

        :param multi_select_lookup_table: Multiple selection lookup table
        :type multi_select_lookup_table: str

        """
        for multi_select_id in multiple_selection:
            create_ms_record(target_table, target_table_id,
                    multi_select_id, multi_select_dest_table,
                    multi_select_lookup_table)

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
            # Get column type of the enumeration
            enum_col_a_type = self._mapped_cls.__mapper__.columns[
                column_name].type
        except KeyError:
            return False, None

        if not hasattr(enum_col_a_type, "enum"):
            return False, None

        else:
            enum_obj = enum_col_a_type.enum

            try:
                if not isinstance(value, str) or not isinstance(value,
                                                                unicode):
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
        col_a_values = {}

        if len(source_cols) == 0:
            return col_a_values

        for f in range(feature_defn.GetFieldCount()):
            field_defn = feature_defn.GetFieldDefn(f)
            field_name = field_defn.GetNameRef()

            #match_idx = getIndex(source_cols, field_name)

            cast = ''

            match_idx = -1
            if source_cols[0] is None:
                continue

            #if source_cols[0].lower in lookup_fields and field_name.lower() in lookup_fields:
                #match_idx = 1

            #if source_cols[0].lower in related_ent_fields and field_name.lower() in related_ent_fields:
                #match_idx = 1
                #cast = 'int'

            if source_cols[0].lower()=='col_a_4' and field_name.lower()=='col_a_4':
                match_idx = 1

            if source_cols[0].lower()=='col_a_5' and field_name.lower()=='col_a_5':
                match_idx = 1

            if source_cols[0].lower()=='col_a_7' and field_name.lower()=='col_a_7':
                match_idx = 1

            if source_cols[0].lower()=='col_a_13' and field_name.lower()=='col_a_13':
                match_idx = 1

            if source_cols[0].lower()=='col_a_21' and field_name.lower()=='col_a_21':
                match_idx = 1

            if source_cols[0].lower()=='col_a_24' and field_name.lower()=='col_a_24':
                match_idx = 1

            if source_cols[0].lower()=='col_a_27' and field_name.lower()=='col_a_27':
                match_idx = 1

            if source_cols[0].lower()=='col_a_28' and field_name.lower()=='col_a_28':
                match_idx = 1

            #To fix Respondent.enumeration(FK) -> Enumeration.id(PK) Relation   
            if source_cols[0].lower()=='col_a_29' and field_name.lower()=='col_a_29':
                match_idx = 1
                cast = 'int'

            if source_cols[0].lower()=='col_b_1' and field_name.lower()=='col_b_1':
                match_idx = 1

            if source_cols[0].lower()=='col_b_5' and field_name.lower()=='col_b_5':
                match_idx = 1

            if source_cols[0].lower()=='col_b_6' and field_name.lower()=='col_b_6':
                match_idx = 1

            if source_cols[0].lower()=='col_b_10' and field_name.lower()=='col_b_10':
                match_idx = 1
                cast = 'int'

            if source_cols[0].lower()=='col_c_5' and field_name.lower()=='col_c_5':
                match_idx = 1

            if source_cols[0].lower()=='col_c_8' and field_name.lower()=='col_c_8':
                match_idx = 1

            if source_cols[0].lower()=='col_c_10' and field_name.lower()=='col_c_10':
                match_idx = 1

            if source_cols[0].lower()=='col_c_11' and field_name.lower()=='col_c_11':
                match_idx = 1

            if source_cols[0].lower()=='col_c_16' and field_name.lower()=='col_c_16':
                match_idx = 1
                cast = 'int'

            if source_cols[0].lower()=='col_d_1' and field_name.lower()=='col_d_1':
                match_idx = 1

            if source_cols[0].lower()=='col_d_7' and field_name.lower()=='col_d_7':
                match_idx = 1
                cast = 'int'

            if source_cols[0].lower()=='col_e_1' and field_name.lower()=='col_e_1':
                match_idx = 1

            if source_cols[0].lower()=='col_e_3' and field_name.lower()=='col_e_3':
                match_idx = 1

            if source_cols[0].lower()=='col_e_4' and field_name.lower()=='col_e_4':
                match_idx = 1

            if source_cols[0].lower()=='col_e_6' and field_name.lower()=='col_e_6':
                match_idx = 1

            if source_cols[0].lower()=='col_e_11' and field_name.lower()=='col_e_11':
                match_idx = 1

            if source_cols[0].lower()=='col_e_12' and field_name.lower()=='col_e_12':
                match_idx = 1

            if source_cols[0].lower()=='col_e_13' and field_name.lower()=='col_e_13':
                match_idx = 1

            if source_cols[0].lower()=='col_e_15' and field_name.lower()=='col_e_15':
                match_idx = 1

            if source_cols[0].lower()=='col_e_16' and field_name.lower()=='col_e_16':
                match_idx = 1

            if source_cols[0].lower()=='col_e_18' and field_name.lower()=='col_e_18':
                match_idx = 1

            if source_cols[0].lower()=='col_e_19' and field_name.lower()=='col_e_19':
                match_idx = 1

            if source_cols[0].lower()=='col_e_20' and field_name.lower()=='col_e_20':
                match_idx = 1

            if source_cols[0].lower()=='col_e_23' and field_name.lower()=='col_e_23':
                match_idx = 1

            if source_cols[0].lower()=='col_e_72' and field_name.lower()=='col_e_72':
                match_idx = 1

            if source_cols[0].lower()=='col_e_76' and field_name.lower()=='col_e_76':
                match_idx = 1
                cast = 'int'

            if source_cols[0].lower()=='col_f_1' and field_name.lower()=='col_f_1':
                match_idx = 1

            if source_cols[0].lower()=='col_f_3' and field_name.lower()=='col_f_3':
                match_idx = 1

            if source_cols[0].lower()=='col_f_4' and field_name.lower()=='col_f_4':
                match_idx = 1

            if source_cols[0].lower()=='col_f_6' and field_name.lower()=='col_f_6':
                match_idx = 1

            if source_cols[0].lower()=='col_f_7' and field_name.lower()=='col_f_7':
                match_idx = 1

            if source_cols[0].lower()=='col_f_11' and field_name.lower()=='col_f_11':
                match_idx = 1
                cast = 'int'

            if match_idx != -1:
                field_value = feature.GetField(f)

                col_a_values[field_name] = unicode(feature.GetField(f), 'utf-8')  #.encode('ascii', 'ignore').strip()

                if cast == 'int' and field_value is not None:
                    col_a_values[field_name] = int(field_value)

        return col_a_values


