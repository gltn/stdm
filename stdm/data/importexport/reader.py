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
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QApplication,
    QProgressDialog
)

try:
    from osgeo import gdal
    from osgeo import ogr
except ImportError:
    import gdal
    import ogr

from stdm.data.pg_utils import (
    delete_table_data,
    geometryType
)
from stdm.utils.util import getIndex
from stdm.settings import (
    current_profile
)

from sqlalchemy.exc import DataError, IntegrityError

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


class ImportFeatureException(Exception):
    """
    Raised when an error occurs during feature import
    """


class OGRReader:
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
        if self.getLayer() is not None:
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

        for field in range(feat_defn.GetFieldCount()):
            field_defn = feat_defn.GetFieldDefn(field)
            fields.append(str(field_defn.GetNameRef()))

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

    def auto_fix_percent(self, target_table, col_name, value):
        """
        Fixes percent columns if empty and with a wrong format.
        :param target_table: The destination table name
        :type target_table: String
        :param col_name: The destination column name
        :type col_name: String
        :param value: Value to be saved to the DB
        :type value: Any
        :return: Converted value
        :rtype: Any
        """
        entity = self._data_source_entity(target_table)

        if entity.columns[col_name].TYPE_INFO == 'PERCENT':
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

    def auto_fix_float_integer(self, target_table, col_name, value):
        """
        Fixes float and integer columns if empty and with a wrong format.
        :param target_table: The destination table name
        :type target_table: String
        :param col_name: The destination column name
        :type col_name: String
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

        if col_name in entity.columns.keys():
            if entity.columns[col_name].TYPE_INFO in integer_types:
                if isinstance(value, str):
                    if not bool(value.strip()) or value.strip().lower() == 'null':
                        value = None
                if entity.columns[col_name].TYPE_INFO in float_type:
                    try:
                        if value is not None:
                            value = float(value)

                    except ValueError:
                        value = None

                elif entity.columns[col_name].TYPE_INFO in int_type:

                    try:
                        if value is not None:
                            value = int(value)
                            if isinstance(value, int):
                                if value == 0:
                                    if entity.columns[col_name].TYPE_INFO in \
                                            ['LOOKUP', 'ADMIN_SPATIAL_UNIT',
                                             'FOREIGN_KEY']:
                                        value = None
                    except ValueError:
                        # TODO show warning to the user that
                        #  some values cannot be converted to integer.
                        value = None

        return value

    def auto_fix_date(self, target_table, col_name, value):
        """
        Fixes date and datetime columns if empty and with a wrong format.
        :param target_table: The destination table name
        :type target_table: String
        :param col_name: The destination column name
        :type col_name: String
        :param value: Value to be saved to the DB
        :type value: Any
        :return: Converted value
        :rtype: Any
        """
        entity = self._data_source_entity(target_table)

        date_types = ['DATE', 'DATETIME']

        if entity.columns[col_name].TYPE_INFO in date_types:
            if not bool(value) or value.lower() == 'null':
                value = None

        return value

    def auto_fix_yes_no(self, target_table, col_name, value):
        """
        Fixes Yes_NO columns if empty and with a wrong format.
        :param target_table: The destination table name
        :type target_table: String
        :param col_name: The destination column name
        :type col_name: String
        :param value: Value to be saved to the DB
        :type value: Any
        :return: Converted value
        :rtype: Any
        """
        entity = self._data_source_entity(target_table)
        yes_no_types = ['BOOL']

        if entity.columns[col_name].TYPE_INFO in yes_no_types:
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

    def _insertRow(self, target_table, columnValueMapping):
        """
        Insert a new row using the mapped class instance then mapping column
        names to the corresponding column values.
        """
        model_instance = self._mapped_cls()
        for col, value in columnValueMapping.items():
            if hasattr(model_instance, col):
                # 'documents' is not a column so exclude it.
                if col != 'documents' and 'collection' not in col:
                    value = self.auto_fix_float_integer(target_table, col,
                                                        value)
                    value = self.auto_fix_percent(target_table, col, value)
                    value = self.auto_fix_date(target_table, col, value)
                    value = self.auto_fix_yes_no(target_table, col, value)

                if not isinstance(value, IgnoreType):
                    setattr(model_instance, col, value)

        self._dbSession.add(model_instance)

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
                 geomColumn=None, geomCode=-1, translator_manager=None):
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

        for feat in lyr:
            column_value_mapping = {}
            column_count = 0
            progress.setValue(init_val)
            progressMsg = lblMsgTemp.format((init_val + 1), numFeat)
            progress.setLabelText(progressMsg)

            if progress.wasCanceled():
                break

            # Reset source document manager for new records
            if destination_entity.supports_documents:
                if self._source_doc_manager is not None:
                    self._source_doc_manager.reset()

            for f in range(feat_defn.GetFieldCount()):
                field_defn = feat_defn.GetFieldDefn(f)
                field_name = field_defn.GetNameRef()

                # Append value only if it has been defined by the user
                if field_name in columnmatch:
                    dest_column = columnmatch[field_name]

                    field_value = feat.GetField(f)

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

                        source_col_names = value_translator.source_column_names()
                        field_value_mappings = self._map_column_values(
                            feat,
                            feat_defn,
                            source_col_names
                        )
                        # Set source document manager if required
                        if value_translator.requires_source_document_manager:
                            value_translator.source_document_manager = self._source_doc_manager

                        field_value = value_translator.referencing_column_value(
                            field_value_mappings
                        )

                    if not isinstance(field_value, IgnoreType):
                        # Check column type and rename if multiple select for
                        # SQLAlchemy compatibility
                        col_obj = destination_entity.column(dest_column)
                        if col_obj.TYPE_INFO == 'MULTIPLE_SELECT':
                            lk_name = col_obj.value_list.name
                            dest_column = '{0}_collection'.format(lk_name)

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

                    if geom_type.lower() != self._geomType.lower():
                        raise TypeError(
                            "The geometries of the source and destination columns do not match.\n"
                            "Source Geometry Type: {0}, Destination Geometry Type: {1}".format(
                                geom_type,
                                self._geomType))

            # Insert the record
            self._insertRow(targettable, column_value_mapping)

            init_val += 1

        try:
            self._dbSession.commit()
        except (DataError, IntegrityError) as e:
            self._dbSession.rollback()
            progress.close()
            progress.deleteLater()
            del progress
            raise ImportFeatureException(str(e))

        progress.setValue(numFeat)

        progress.deleteLater()
        del progress

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
            enum_col_type = self._mapped_cls.__mapper__.columns[
                column_name].type
        except KeyError:
            return False, None

        if not hasattr(enum_col_type, "enum"):
            return False, None

        else:
            enum_obj = enum_col_type.enum

            try:
                if not isinstance(value, str) or not isinstance(value,
                                                                str):
                    value = str(value)

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
