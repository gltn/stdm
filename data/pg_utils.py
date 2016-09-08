"""
/***************************************************************************
Name                 : PostgreSQL/PostGIS util functions
Description          : Contains generic util functions for accessing the 
                       PostgreSQL/PostGIS STDM database.
Date                 : 1/April/2014
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
from PyQt4.QtCore import (
    QFile,
    QIODevice,
    QRegExp,
    QTextStream
)

from qgis.core import *

from sqlalchemy.sql.expression import text
from sqlalchemy.exc import SQLAlchemyError
from geoalchemy2 import WKBElement
import stdm.data

from stdm.data.database import (
    STDMDb,
    Base
)
from stdm.utils.util import (
    getIndex,
    PLUGIN_DIR
)

from sqlalchemy.exc import IntegrityError

_postGISTables = ["spatial_ref_sys", "supporting_document"]
_postGISViews = ["geometry_columns","raster_columns","geography_columns",
                 "raster_overviews","foreign_key_references"]

_pg_numeric_col_types = ["smallint","integer","bigint","double precision",
                      "numeric","decimal","real","smallserial","serial",
                      "bigserial"]
_text_col_types = ["character varying", "text"]

#Flags for specifying data source type
VIEWS = 2500
TABLES = 2501

def spatial_tables(exclude_views=False):
    """
    Returns a list of spatial table names in the STDM database.
    """
    t = text("select DISTINCT f_table_name from geometry_columns")
    result = _execute(t)

    spTables = []
    views = pg_views()

    for r in result:
        spTable = r["f_table_name"]
        if exclude_views:
            tableIndex = getIndex(views,spTable)
            if tableIndex == -1:
                spTables.append(spTable)
        else:
            spTables.append(spTable)

    return spTables

def pg_tables(schema="public", exclude_lookups=False):
    """
    Returns a list of all the tables in the given schema minus the default PostGIS tables.
    Views are also excluded. See separate function for retrieving views.
    :rtype: list
    """
    t = text("SELECT table_name FROM information_schema.tables WHERE table_schema = :tschema and table_type = :tbtype " \
             "ORDER BY table_name ASC")
    result = _execute(t, tschema=schema, tbtype="BASE TABLE")
        
    pgTables = []
        
    for r in result:
        tableName = r["table_name"]
        
        #Remove default PostGIS tables
        tableIndex = getIndex(_postGISTables, tableName)
        if tableIndex == -1:
            if exclude_lookups:
                #Validate if table is a lookup table and if it is, then omit
                rx = QRegExp("check_*")
                rx.setPatternSyntax(QRegExp.Wildcard)
                
                if not rx.exactMatch(tableName):
                    pgTables.append(tableName)
                    
            else:
                pgTables.append(tableName)
            
    return pgTables

def pg_views(schema="public"):
    """
    Returns the views in the given schema minus the default PostGIS views.
    """
    t = text("SELECT table_name FROM information_schema.tables WHERE table_schema = :tschema and table_type = :tbtype " \
             "ORDER BY table_name ASC")
    result = _execute(t, tschema = schema, tbtype = "VIEW")
        
    pgViews = []
        
    for r in result:

        viewName = r["table_name"]
        
        #Remove default PostGIS tables
        viewIndex = getIndex(_postGISViews, viewName)
        if viewIndex == -1:
            pgViews.append(viewName)
            
    return pgViews

def pg_table_exists(table_name, include_views=True, schema="public"):
    """
    Checks whether the given table name exists in the current database
    connection.
    :param table_name: Name of the table or view. If include_views is False
    the result will always be False since views have been excluded from the
    search.
    :type table_name: str
    :param include_views: True if view names will be also be included in the
    search.
    :type include_views: bool
    :param schema: Schema to search against. Default is "public" schema.
    :type schema: str
    :return: True if the table or view (if include_views is True) exists in
    currently connected database.
    :rtype: bool
    """
    tables = pg_tables(schema=schema)
    if include_views:
        tables.extend(pg_views(schema=schema))

    if getIndex(tables, table_name) == -1:
        return False

    else:
        return True

def pg_table_count(table_name):
    """
    Returns a count of records in a table
    :param table_name: Table to get count of.
    :type table_name: str
    :rtype: int
    """
    sql_str = "Select COUNT(*) cnt from {0}".format(table_name)
    sql = text(sql_str)

    results = _execute(sql)
    for result in results:
        cnt = result['cnt']

    return cnt

def process_report_filter(tableName, columns, whereStr="", sortStmnt=""):
    #Process the report builder filter    
    sql = "SELECT {0} FROM {1}".format(columns,tableName)
    
    if whereStr != "":
        sql += " WHERE {0} ".format(whereStr)
        
    if sortStmnt !="":
        sql += sortStmnt
        
    t = text(sql)
    
    return _execute(t)

def export_data(table_name):
    sql = "SELECT * FROM {0}".format(table_name, )

    t = text(sql)

    return _execute(t)

def export_data_from_columns(columns, table_name):
    sql = "SELECT {0} FROM {1}".format(columns, table_name)

    t = text(sql)

    return _execute(t)

def fix_sequence(table_name):
    """
    Fixes a sequence error that commonly happen
    after a batch insert such as in
    import_data(), csv import, etc.
    :param table_name: The name of the table to be fixed
    :type table_name: String
    """
    sql_sequence_fix = text(
        "SELECT setval('{0}_id_seq', (SELECT MAX(id) FROM {0}));".format(
            table_name
        )
    )

    _execute(sql_sequence_fix)


def import_data(table_name, columns_names, data, **kwargs):

    sql = "INSERT INTO {0} ({1}) VALUES {2}".format(table_name,
                                                    columns_names, data)

    t = text(sql)
    conn = STDMDb.instance().engine.connect()
    trans = conn.begin()

    try:
        result = conn.execute(t, **kwargs)
        trans.commit()

        conn.close()
        return result

    except IntegrityError:
        trans.rollback()
        return False
    except SQLAlchemyError:
        trans.rollback()
        return False

def table_column_names(tableName, spatialColumns=False, creation_order=False):
    """
    Returns the column names of the given table name. 
    If 'spatialColumns' then the function will lookup for spatial columns in the given 
    table or view.
    """
    if spatialColumns:
        sql = "select f_geometry_column from geometry_columns where f_table_name = :tbname ORDER BY f_geometry_column ASC"
        columnName = "f_geometry_column"
    else:
        if not creation_order:
            sql = "select column_name from information_schema.columns where table_name = :tbname ORDER BY column_name ASC"
            columnName = "column_name"
        else:
            sql = "select column_name from information_schema.columns where table_name = :tbname"
            columnName = "column_name"

    t = text(sql)
    result = _execute(t,tbname = tableName)
        
    columnNames = []
       
    for r in result:
        colName = r[columnName]
        columnNames.append(colName)
           
    return columnNames

def non_spatial_table_columns(table):
    """
    Returns non spatial table columns.
    """
    all_columns = table_column_names(table)

    excluded_columns = [u'id']

    spatial_columns = table_column_names(table, True) + excluded_columns

    return [x for x in all_columns if x not in spatial_columns]

def delete_table_data(tableName,cascade = True):
    """
    Delete all the rows in the target table.
    """
    tables = pg_tables()
    tableIndex = getIndex(tables, tableName)
    
    if tableIndex != -1:
        sql = "DELETE FROM {0}".format(tableName)
        
        if cascade:
            sql += " CASCADE"
        
        t = text(sql)
        _execute(t) 

def geometryType(tableName, spatialColumnName, schemaName="public"):
    """
    Returns a tuple of geometry type and EPSG code of the given column name in the table within the given schema.
    """
    sql = "select type,srid from geometry_columns where f_table_name = :tbname " \
          "and f_geometry_column = :spcolumn and f_table_schema = :tbschema"
    t = text(sql)
    
    result = _execute(t,tbname = tableName,spcolumn=spatialColumnName,tbschema=schemaName)
        
    geomType,epsg_code = "", -1
       
    for r in result:
        geomType = r["type"]
        epsg_code = r["srid"]
        
        break
        
    return (geomType,epsg_code)

def unique_column_values(tableName, columnName, quoteDataTypes=["character varying"]):
    """
    Select unique row values in the specified column.
    Specify the data types of row values which need to be quoted. Default is varchar.
    """
    dataType = columnType(tableName,columnName)
    quoteRequired = getIndex(quoteDataTypes, dataType)
    
    sql = "SELECT DISTINCT {0} FROM {1}".format(columnName, tableName)
    t = text(sql)
    result = _execute(t)
    
    uniqueVals = []
    
    for r in result:
        if r[columnName] == None:
            if quoteRequired == -1:
                uniqueVals.append("NULL")
            else:
                uniqueVals.append("''")
                
        else:
            if quoteRequired == -1:
                uniqueVals.append(str(r[columnName]))
            else:
                uniqueVals.append("'{0}'".format(str(r[columnName])))
                
    return uniqueVals

def columnType(tableName, columnName):
    """
    Returns the PostgreSQL data type of the specified column.
    """
    sql = "SELECT data_type FROM information_schema.columns where table_name=:tbName AND column_name=:colName"
    t = text(sql)
    
    result = _execute(t, tbName=tableName, colName=columnName)

    dataType = ""
    for r in result:
        dataType = r["data_type"]
        
        break
    return dataType

def columns_by_type(table, data_types):
    """
    :param table: Name of the database table.
    :type table: str
    :param data_types: List containing matching datatypes that should be
    retrieved from the table.
    :type data_types: list
    :return: Returns those columns of given types from the specified
    database table.
    :rtype: list
    """
    cols = []

    table_cols = table_column_names(table)
    for tc in table_cols:
        col_type = columnType(table, tc)
        type_idx = getIndex(data_types, col_type)

        if type_idx != -1:
            cols.append(tc)

    return cols

def numeric_columns(table):
    """
    :param table: Name of the database table.
    :type table: str
    :return: Returns a list of columns that are of number type such as
    integer, decimal, double etc.
    :rtype: list
    """
    return columns_by_type(table, _pg_numeric_col_types)

def numeric_varchar_columns(table, exclude_fk_columns=True):
    #Combines numeric and text column types mostly used for display columns
    num_char_types = _pg_numeric_col_types + _text_col_types

    num_char_cols = columns_by_type(table, num_char_types)

    if exclude_fk_columns:
        fk_refs = foreign_key_parent_tables(table)

        for fk in fk_refs:
            local_col = fk[0]
            col_idx = getIndex(num_char_cols, local_col)
            if col_idx != -1:
                num_char_cols.remove(local_col)

        return num_char_cols

    else:
        return num_char_cols

def qgsgeometry_from_wkbelement(wkb_element):
    """
    Convert a geoalchemy object in str or WKBElement format to the a
    QgsGeometry object.
    :return: QGIS Geometry object.
    """
    if isinstance(wkb_element, WKBElement):
        db_session = STDMDb.instance().session
        geom_wkt = db_session.scalar(wkb_element.ST_AsText())

    elif isinstance(wkb_element, str):
        split_geom = wkb_element.split(";")

        if len(split_geom) < 2:
            return None

        geom_wkt = split_geom[1]

    return QgsGeometry.fromWkt(geom_wkt)
    
def _execute(sql,**kwargs):
    """
    Execute the passed in sql statement
    """
    conn = STDMDb.instance().engine.connect()
    trans = conn.begin()
    result = conn.execute(sql,**kwargs)
    try:
        trans.commit()
        conn.close()
        return result
    except SQLAlchemyError:
        trans.rollback()


def reset_content_roles():
    rolesSet = "truncate table content_base cascade;"
    _execute(text(rolesSet))
    resetSql = text(rolesSet)
    _execute(resetSql)

def delete_table_keys(table):
    #clean_delete_table(table)
    capabilities = ["Create", "Select", "Update", "Delete"]
    for action in capabilities:
        init_key = action +" "+ str(table).title()
        sql = "DELETE FROM content_roles WHERE content_base_id IN" \
              " (SELECT id FROM content_base WHERE name = '{0}');".format(init_key)
        sql2 = "DELETE FROM content_base WHERE content_base.id IN" \
               " (SELECT id FROM content_base WHERE name = '{0}');".format(init_key)
        r = text(sql)
        r2 = text(sql2)
        _execute(r)
        _execute(r2)
        Base.metadata._remove_table(table, 'public')

def safely_delete_tables(tables):
    for table in tables:
        sql = "DROP TABLE  if exists {0} CASCADE".format(table)
        _execute(text(sql))
        Base.metadata._remove_table(table, 'public')
        flush_session_activity()

def flush_session_activity():
    STDMDb.instance().session._autoflush()

def vector_layer(table_name, sql='', key='id', geom_column='', layer_name=''):
    """
    Returns a QgsVectorLayer based on the specified table name.
    """
    if not table_name:
        return None

    conn = stdm.data.app_dbconn
    if conn is None:
        return None

    if not geom_column:
        geom_column = None

    ds_uri = conn.toQgsDataSourceUri()
    ds_uri.setDataSource("public", table_name, geom_column, sql, key)

    if not layer_name:
        layer_name = table_name

    v_layer = QgsVectorLayer(ds_uri.uri(), layer_name, "postgres")

    return v_layer

def foreign_key_parent_tables(table_name, search_parent=True, filter_exp=None):
    """
    Functions that searches for foreign key references in the specified table.
    :param table_name: Name of the database table.
    :type table_name: str
    :param search_parent: Select True if table_name is the child and
    parent tables are to be retrieved, else child tables will be
    returned.
    :type search_parent: bool
    :param filter_exp: A regex expression to filter related table names.
    :type filter_exp: QRegExp
    :return: A list of tuples containing the local column name, foreign table
    name and corresponding foreign column name.
    :rtype: list
    """
    #Check if the view for listing foreign key references exists
    fk_ref_view = pg_table_exists("foreign_key_references")

    #Create if it does not exist
    if not fk_ref_view:
        script_path = PLUGIN_DIR + "/scripts/foreign_key_references.sql"

        script_file = QFile(script_path)
        if script_file.exists():
            if not script_file.open(QIODevice.ReadOnly):
                return None

            reader = QTextStream(script_file)
            sql = reader.readAll()
            if sql:
                t = text(sql)
                _execute(t)

        else:
            return None

    if search_parent:
        ref_table = "foreign_table_name"
        search_table = "table_name"
    else:
        ref_table = "table_name"
        search_table = "foreign_table_name"

    #Fetch foreign key references
    sql = u"SELECT column_name,{0},foreign_column_name FROM " \
          u"foreign_key_references where {1} =:tb_name".format(ref_table,
                                                               search_table)
    t = text(sql)
    result = _execute(t, tb_name=table_name)

    fk_refs = []

    for r in result:
        rel_table = r[ref_table]

        fk_ref = r["column_name"], rel_table,\
                 r["foreign_column_name"]

        if not filter_exp is None:
            if filter_exp.indexIn(rel_table) >= 0:
                fk_refs.append(fk_ref)

                continue

        fk_refs.append(fk_ref)

    return fk_refs


def table_view_dependencies(table_name, column_name=None):
    """
    Find database views that are dependent on the given table and
    optionally the column.
    :param table_name: Table name
    :type table_name: str
    :param column_name: Name of the column whose dependent views are to be
    extracted.
    :type column_name: str
    :return: A list of views which are dependent on the given table name and
    column respectively.
    :rtype: list(str)
    """
    views = []

    #Load the SQL file depending on whether its table or table/column
    if column_name is None:
        script_path = PLUGIN_DIR + '/scripts/table_related_views.sql'
    else:
        script_path = PLUGIN_DIR + '/scripts/table_column_related_views.sql'

    script_file = QFile(script_path)

    if not script_file.exists():
        raise IOError('SQL file for retrieving view dependencies could '
                      'not be found.')

    else:
        if not script_file.open(QIODevice.ReadOnly):
            raise IOError('Failed to read the SQL file for retrieving view '
                          'dependencies.')

        reader = QTextStream(script_file)
        sql = reader.readAll()
        if sql:
            t = text(sql)
            if column_name is None:
                result = _execute(t,table_name=table_name)

            else:
                result = _execute(t,table_name=table_name, column_name=column_name)

            #Get view names
            for r in result:
                view_name = r['view_name']
                views.append(view_name)

    return views


def drop_cascade_table(table_name):
    """
    Safely deletes the table with the specified name using the CASCADE option.
    :param table_name: Name of the database table.
    :type table_name: str
    :return: Returns True if the operation succeeded. otherwise False.
    :rtype: bool
    """
    del_com = 'DROP TABLE IF EXISTS {0} CASCADE;'.format(table_name)
    t = text(del_com)

    try:
        _execute(t)

        return True

    #Error if the current user is not the owner.
    except SQLAlchemyError:

        return False


def drop_view(view_name):
    """
    Deletes the database view with the given name. The CASCADE command option
    will be used hence dependent objects will also be dropped.
    :param view_name: Name of the database view.
    :type view_name: str
    """
    del_com = 'DROP VIEW IF EXISTS {0} CASCADE;'.format(view_name)
    t = text(del_com)

    try:
        _execute(t)
        return True

    #Error such as view dependencies or the current user is not the owner.
    except SQLAlchemyError:

        return False


