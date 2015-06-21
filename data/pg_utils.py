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
from PyQt4.QtCore import QRegExp

from qgis.core import *

from sqlalchemy.sql.expression import text

import stdm.data
from stdm.data import STDMDb, Base
from stdm.utils import getIndex

_postGISTables = ["spatial_ref_sys"]
_postGISViews = ["geometry_columns","raster_columns","geography_columns","raster_overviews"]

_pg_numeric_col_types = ["smallint","integer","bigint","double precision",
                      "numeric","decimal","real","smallserial","serial",
                      "bigserial"]
_text_col_types = ["character varying", "text"]

#Flags for specifying data source type
VIEWS = 2500
TABLES = 2501

def spatial_tables(excludeViews=False):
    '''
    Returns a list of spatial table names in the STDM database.
    '''
    t = text("select DISTINCT f_table_name from geometry_columns")
    result = _execute(t)
        
    spTables = []
    views = pg_views()
        
    for r in result:
        spTable = r["f_table_name"]
        if excludeViews:
            tableIndex = getIndex(views,spTable)
            if tableIndex == -1:
                spTables.append(spTable)
        else:
            spTables.append(spTable)
            
    return spTables

def pg_tables(schema="public",excludeLookups = False):
    """
    Returns all the tables in the given schema minus the default PostGIS tables.
    Views are also excluded. See separate function for retrieving views.
    """
    t = text("SELECT table_name FROM information_schema.tables WHERE table_schema = :tschema and table_type = :tbtype " \
             "ORDER BY table_name ASC")
    result = _execute(t,tschema = schema,tbtype = "BASE TABLE")
        
    pgTables = []
        
    for r in result:
        tableName = r["table_name"]
        
        #Remove default PostGIS tables
        tableIndex = getIndex(_postGISTables, tableName)
        if tableIndex == -1:
            if excludeLookups:
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
    result = _execute(t,tschema = schema,tbtype = "VIEW")
        
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

def process_report_filter(tableName,columns,whereStr="",sortStmnt=""):
    #Process the report builder filter    
    sql = "SELECT {0} FROM {1}".format(columns,tableName)
    
    if whereStr != "":
        sql += " WHERE {0} ".format(whereStr)
        
    if sortStmnt !="":
        sql += sortStmnt
        
    t = text(sql)
    
    return _execute(t)

def table_column_names(tableName,spatialColumns = False):
    """
    Returns the column names of the given table name. 
    If 'spatialColumns' then the function will lookup for spatial columns in the given 
    table or view.
    """
    if spatialColumns:
        sql = "select f_geometry_column from geometry_columns where f_table_name = :tbname ORDER BY f_geometry_column ASC"
        columnName = "f_geometry_column"
    else:
        sql = "select column_name from information_schema.columns where table_name = :tbname ORDER BY column_name ASC"
        columnName = "column_name"
        
    t = text(sql)
    result = _execute(t,tbname = tableName)
        
    columnNames = []
       
    for r in result:
        colName = r[columnName]
        columnNames.append(colName)
           
    return columnNames

def non_spatial_table_columns(spatial_table):
    """
    Returns non spatial table columns
    Uses list comprehension
    """
    all_columns = table_column_names(spatial_table)

    excluded_columns = [u'id']

    spatial_columns = table_column_names(spatial_table, True) + excluded_columns

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

def geometryType(tableName,spatialColumnName,schemaName = "public"):
    """
    Returns a tuple of geometry type and EPSG code of the given column name in the table within the given schema.
    """
    sql = "select type,srid from geometry_columns where f_table_name = :tbname and f_geometry_column = :spcolumn and f_table_schema = :tbschema"
    t = text(sql)
    
    result = _execute(t,tbname = tableName,spcolumn=spatialColumnName,tbschema=schemaName)
        
    geomType,epsg_code = "", -1
       
    for r in result:
        geomType = r["type"]
        epsg_code = r["srid"]
        
        break
        
    return (geomType,epsg_code)

def unique_column_values(tableName,columnName,quoteDataTypes=["character varying"]):
    """
    Select unique row values in the specified column.
    Specify the data types of row values which need to be quoted. Default is varchar.
    """
    dataType = columnType(tableName,columnName)
    quoteRequired = getIndex(quoteDataTypes, dataType)
    
    sql = "SELECT DISTINCT {0} FROM {1}".format(columnName,tableName)
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

def columnType(tableName,columnName):
    """
    Returns the PostgreSQL data type of the specified column.
    """
    sql = "SELECT data_type FROM information_schema.columns where table_name=:tbName AND column_name=:colName"
    t = text(sql)
    
    result = _execute(t,tbName = tableName,colName = columnName)

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

def numeric_varchar_columns(table):
    #Combines numeric and text column types
    num_char_types = _pg_numeric_col_types + _text_col_types

    return columns_by_type(table, num_char_types)

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
    result = conn.execute(sql,**kwargs)
    conn.close()
    return result

def reset_content_roles():
    rolesSet = "truncate table content_base cascade;"
    _execute(text(rolesSet))
    resetSql = text(rolesSet)
    _execute(resetSql)
    # rolesSet1 = "truncate table content_roles cascade;"
    # resetSql1 = text(rolesSet1)
    # _execute(resetSql1)

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

def vector_layer(table_name, sql="", key="id",geom_column=""):
    """
    Returns a QgsVectorLayer based on the specified table name.
    """
    if not table_name:
        return None

    conn = stdm.data.app_dbconn
    if conn is None:
        return None

    if not geom_column:
        geom_column=None

    ds_uri = conn.toQgsDataSourceUri()
    ds_uri.setDataSource("public", table_name, geom_column, sql, key)

    v_layer = QgsVectorLayer(ds_uri.uri(), table_name, "postgres")

    return v_layer
