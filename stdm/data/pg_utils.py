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
from typing import List

from geoalchemy2 import WKBElement
from qgis.PyQt.QtCore import (
    QFile,
    QIODevice,
    QRegExp,
    QTextStream)
from qgis.core import (
    QgsGeometry,
    QgsVectorLayer,
    QgsCoordinateReferenceSystem,
    QgsProject
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql.expression import text

from stdm.data import globals
from stdm.data.database import (
    STDMDb,
    Base
)
from stdm.exceptions import DummyException
from stdm.utils.util import (
    getIndex,
    PLUGIN_DIR
)

_postGISTables = ["spatial_ref_sys", "supporting_document"]
_postGISViews = ["geometry_columns", "raster_columns", "geography_columns",
                 "raster_overviews", "foreign_key_references"]

_pg_numeric_col_types = ["smallint", "integer", "bigint", "double precision",
                         "numeric", "decimal", "real", "smallserial", "serial",
                         "bigserial"]
_text_col_types = ["character varying", "text"]

# Flags for specifying data source type
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
            tableIndex = getIndex(views, spTable)
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
    t = text("SELECT table_name FROM information_schema.tables WHERE table_schema = :tschema and table_type = :tbtype "
             "ORDER BY table_name ASC")
    result = _execute(t, tschema=schema, tbtype="BASE TABLE")

    pgTables = []

    for r in result:
        tableName = r["table_name"]

        # Remove default PostGIS tables
        tableIndex = getIndex(_postGISTables, tableName)
        if tableIndex != -1:
            continue
        if exclude_lookups:
            # Validate if table is a lookup table and if it is, then omit
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
    t = text("SELECT table_name FROM information_schema.tables WHERE table_schema = :tschema and table_type = :tbtype "
             "ORDER BY table_name ASC")
    result = _execute(t, tschema=schema, tbtype="VIEW")

    pgViews = []

    for r in result:

        viewName = r["table_name"]

        # Remove default PostGIS tables
        viewIndex = getIndex(_postGISViews, viewName)
        if viewIndex == -1:
            pgViews.append(viewName)

    return pgViews


def view_details(self, view):
    """
    Gets the view definition/query
    used to create it.
    :param view: The name of the view.
    :type view: String
    :return: The definition/query.
    :rtype: String
    """
    if view in pg_views():
        t = text('SELECT definition '
                 'FROM pg_views '
                 'WHERE viewname=:view_name;'
                 )

        result = _execute(t, view_name=view)

        definition = []
        for row in result:
            definition.append(row[0])
        return definition[0]


def get_referenced_table(self, view):
    """
    Returns the referenced table name
    from an old view definition.
    :param view: The view name
    :type view: String
    :return: Referenced table name
    :rtype: String
    """
    definition = self.view_details(view)
    if definition is None:
        return None
    lo_def = definition.lower().strip().lstrip('select')
    query_lines = lo_def.splitlines()
    ref_table = None
    for q in query_lines:
        if ' id ' in q:
            q = q.split('.')
            ref_table = q[0].strip()
            break
        if '.id' in q and 'as' not in q.lower():
            q = q.split('.')
            q = q[0].split(' ')
            ref_table = q[-1].strip()

            break

    return ref_table


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


def pg_column_exists(table_name:str, column_name: str):
    sql_str = (f"Select count(*) cnt from information_schema.columns "
               f" Where table_name = '{table_name}' and column_name = '{column_name}' "
               )
    try:
        results = _execute(sql_str)
        cnt = 0
        for result in results:
            cnt = result['cnt']

        return True if cnt > 0 else False
    except SQLAlchemyError as db_error:
        return False

def column_has_no_unique_values(table_name: str, column_name: str)->bool:
    sql_stmt = f'Select count(*) cnt from {table_name} group by {column_name} having count(*) > 1'
    try:
        results = run_query(sql_stmt)
        cnt = 0
        for result in results:
            cnt = result['cnt']
        return True if cnt > 0 else False
    except SQLAlchemyError as db_error:
        return False

def pg_table_record_count(table_name):
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
    # Process the report builder filter
    if "'" in columns and '"' not in columns:
        cols = []
        spited_cols = columns.split(',')
        for col in spited_cols:
            col = '{}'.format(col)
            cols.append(col)
        columns = ','.join(cols)

    sql = "SELECT {0} FROM {1}".format(columns, tableName)

    if whereStr != "":
        sql += " WHERE {0} ".format(whereStr)

    if sortStmnt != "":
        sql += sortStmnt

    t = text(sql)

    return _execute(t)


def export_data(table_name):
    sql = "SELECT * FROM {0} ".format(str(table_name))

    t = text(sql)

    return _execute(t)

def run_query(query: str):
    t = text(query)
    return _execute(t)

def fetch_with_filter(sql_str):
    sql = str(sql_str)

    t = text(sql)

    return _execute(t)


def fetch_from_table(table_name, limit):
    """
    Fetches data from a table with a limit.
    :param table_name: The table name.
    :type table_name: String
    :param limit: The limit.
    :type limit: Integer
    :return:
    :rtype:
    """
    sql = "SELECT * FROM {0} ORDER BY id DESC LIMIT {1} ".format(
        str(table_name), str(limit)
    )

    t = text(sql)

    return _execute(t)


def export_data_from_columns(columns, table_name):
    sql = "SELECT {0} FROM {1}".format(str(columns), str(table_name))

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
        "SELECT setval(u'{0}_id_seq', (SELECT MAX(id) FROM {0}));".format(
            table_name
        )
    )

    _execute(sql_sequence_fix)


def import_data(table_name, columns_names, data, **kwargs):
    sql = "INSERT INTO {0} ({1}) VALUES {2}".format(table_name,
                                                    columns_names, str(data))

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


def table_column_names(tableName, spatialColumns=False, creation_order=False) -> List[str]:
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
    result = _execute(t, tbname=tableName)

    columnNames = []

    for r in result:
        colName = r[columnName]
        columnNames.append(colName)

    return columnNames


def mandatory_columns(tables: list)->list:
    """
    Returns mandatory columns in the given table.
    """
    table_names = ",".join([f"'{t}'" for t in tables])
    sql = f"SELECT column_name FROM information_schema.columns WHERE table_name in ({table_names}) AND is_nullable = 'NO'"
    sql_text = text(sql)
    result = _execute(sql_text)

    mandatory_cols = []

    for r in result:
        col_name = r["column_name"]
        if col_name != "id":
            mandatory_cols.append(col_name)

    return mandatory_cols

def unique_columns(tables: list)-> list:
    """
    Returns unique columns in the given table.
    """
    table_names = ",".join([f"'{t}'" for t in tables])
    sql = f"SELECT constraint_name FROM information_schema.table_constraints WHERE table_name in ({table_names}) and constraint_type = 'UNIQUE' "
    sql_text =  text(sql)

    result = _execute(sql_text)

    unique_cols = []

    for r in result:
        col_name = r["constraint_name"]
        unique_cols.append(col_name)

    return unique_cols


def non_spatial_table_columns(table):
    """
    Returns non spatial table columns.
    """
    all_columns = table_column_names(table)

    excluded_columns = ['id']

    spatial_columns = table_column_names(table, True) + excluded_columns

    return [x for x in all_columns if x not in spatial_columns]


def delete_table_data(tableName, cascade=True):
    """
    Delete all the rows in the target table.
    """
    tables = pg_tables()
    tableIndex = getIndex(tables, tableName)

    if tableIndex != -1:
        sql = "TRUNCATE {0}".format(tableName)

        if cascade:
            sql += " CASCADE"

        t = text(sql)
        _execute(t)


def geometryType(tableName, spatialColumnName, schemaName="public"):
    """
    Returns a tuple of geometry type and EPSG code of the given column name in
    the table within the given schema.
    """
    sql = "select type,srid from geometry_columns where f_table_name = :tbname " \
          "and f_geometry_column = :spcolumn and f_table_schema = :tbschema"
    t = text(sql)

    result = _execute(t, tbname=tableName, spcolumn=spatialColumnName, tbschema=schemaName)

    geomType, epsg_code = "", -1

    for r in result:
        geomType = r["type"]
        epsg_code = r["srid"]

        break

    return geomType, epsg_code


def unique_column_values(tableName, columnName, quoteDataTypes=["character varying"]):
    """
    Select unique row values in the specified column.
    Specify the data types of row values which need to be quoted. Default is varchar.
    """
    # tableName = str(tableName)
    # columnName = str(columnName)
    dataType = columnType(tableName, columnName)
    quoteRequired = getIndex(quoteDataTypes, dataType)
    if "'" in columnName and '"' not in columnName:
        sql = 'SELECT DISTINCT "{0}" FROM {1}'.format(str(columnName),
                                                      tableName)
    else:

        sql = "SELECT DISTINCT {0} FROM {1}".format(str(columnName), tableName)
    t = text(sql)
    result = _execute(t)

    uniqueVals = []

    for r in result:

        if r[str(columnName)] is None:
            if quoteRequired == -1:
                uniqueVals.append("NULL")
            else:
                uniqueVals.append("''")

        else:
            if quoteRequired == -1:
                uniqueVals.append(str(r[columnName]))
            else:
                uniqueVals.append("'{0}'".format(r[columnName]))

    return uniqueVals


def columnType(tableName, columnName):
    """
    Returns the PostgreSQL data type of the specified column.
    """
    view = tableName in pg_views()
    if not view:
        sql = "SELECT data_type FROM information_schema.columns where table_name='{}' AND column_name='{}'". \
            format(tableName, columnName)
    else:
        # if ' ' in columnName:
        #     columnName = u'"{}"'.format(columnName)
        if '"' in columnName:
            sql = 'SELECT pg_typeof({}) from {} limit 1;'.format(
                columnName, tableName
            )
        else:
            sql = 'SELECT pg_typeof("{}") from {} limit 1;'.format(
                columnName, tableName
            )

    t = text(sql)

    result = _execute(t)

    dataType = ""
    for r in result:
        if view:
            if len(r) > 0:
                dataType = r[0]
        else:
            dataType = r["data_type"]

        break
    return dataType

def check_mandatory_exists(table_name, column_name):
    """
    Checks if the column is mandatory.
    """
    sql = "SELECT is_nullable FROM information_schema.columns WHERE table_name = :tbname AND column_name = :colname"
    t = text(sql)
    result = _execute(t, tbname=table_name, colname=column_name)

    for r in result:
        is_nullable = r["is_nullable"]

        break

    return is_nullable == "NO"


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
    # Combines numeric and text column types mostly used for display columns
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


def _execute(sql, **kwargs):
    """
    Execute the passed in sql statement
    """
    try:
        conn = STDMDb.instance().engine.connect()
        trans = conn.begin()
    except AttributeError as attr_error:
        return {}

    try:
        result = conn.execute(sql, **kwargs)
        trans.commit()
        conn.close()
        return result
    except SQLAlchemyError as db_error:
        trans.rollback()
        raise db_error


def reset_content_roles():
    rolesSet = "truncate table content_base cascade;"
    _execute(text(rolesSet))
    resetSql = text(rolesSet)
    _execute(resetSql)


def delete_table_keys(table):
    # clean_delete_table(table)
    capabilities = ["Create", "Select", "Update", "Delete"]
    for action in capabilities:
        init_key = action + " " + str(table).title()
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


def vector_layer(table_name, sql='', key='id', geom_column='', layer_name='', proj_wkt=None):
    """
    Returns a QgsVectorLayer based on the specified table name.
    """
    if not table_name:
        return None

    conn = globals.APP_DBCONN
    if conn is None:
        return None

    if not geom_column:
        geom_column = None

    ds_uri = conn.toQgsDataSourceUri()
    ds_uri.setDataSource("public", table_name, geom_column, sql, key)

    if not layer_name:
        layer_name = table_name

    layer_options = QgsVectorLayer.LayerOptions(QgsProject.instance().transformContext())
    if proj_wkt is not None:
        layer_options.skipCrsValidation = True

    v_layer = QgsVectorLayer(ds_uri.uri(), layer_name, "postgres", layer_options)

    if proj_wkt is not None:
        try:
            target_crs = QgsCoordinateReferenceSystem(
                proj_wkt, QgsCoordinateReferenceSystem.InternalCrsId
            )
            v_layer.setCrs(target_crs)
        except DummyException:
            pass
    return v_layer


def foreign_key_parent_tables(table_name, search_parent=True, filter_exp=None):
    """
    Function that searches for foreign key references in the specified table.
    :param table_name: Name of the database table.
    :type table_name: str
    :param search_parent: Select True if table_name is the child and
    parent tables are to be retrieved, else child tables will be
    returned.
    :type search_parent: bool
    :param filter_exp: A regex expression to filter related table names.
    :type filter_exp: QRegExp
    :return: A list of tuples containing the local column name, foreign table
    name, corresponding foreign column name and constraint name.
    :rtype: list
    """
    # Check if the view for listing foreign key references exists
    fk_ref_view = pg_table_exists("foreign_key_references")

    # Create if it does not exist
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

    # Fetch foreign key references
    sql = "SELECT column_name,{0},foreign_column_name, constraint_name FROM " \
          "foreign_key_references where {1} =:tb_name".format(ref_table,
                                                              search_table)

    t = text(sql)
    result = _execute(t, tb_name=table_name)

    fk_refs = []

    for r in result:
        rel_table = r[ref_table]

        fk_ref = r["column_name"], rel_table, \
                 r["foreign_column_name"], r["constraint_name"]

        if filter_exp is not None:
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

    # Load the SQL file depending on whether its table or table/column
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
                result = _execute(
                    t,
                    table_name=table_name
                )

            else:
                result = _execute(
                    t,
                    table_name=table_name,
                    column_name=column_name
                )

            # Get view names
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

    # Error if the current user is not the owner.
    except SQLAlchemyError:
        return False


def drop_cascade_column(table_name: str, column_name: str) ->bool:
    """
    Safely deletes the column contained in the given table using the CASCADE option.
    :param table_name: Name of the database table.
    :type table_name: str
    :param column: Name of the column to delete.
    :type column: str
    :return: Returns True if the operation succeeded. otherwise False.
    :rtype: bool
    """
    del_com = 'ALTER TABLE {0} DROP COLUMN IF EXISTS {1} CASCADE;'.format(
        table_name,
        column_name
    )
    t = text(del_com)

    try:
        _execute(t)

        return True

    # Error if the current user is not the owner.
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

    # Error such as view dependencies or the current user is not the owner.
    except SQLAlchemyError:

        return False


def copy_from_column_to_another(table, source, destination):
    """
    Copy data from one column to another column
    within the same table.
    :param table: The table name holding the two columns
    :type table: String
    :param source: The source column name
    :type source: String
    :param destination: The destination column name
    :type destination: String
    :return:
    :rtype:
    """
    sql = 'UPDATE {0} SET {1} = {2};'.format(table, destination, source)
    t = text(sql)
    result = _execute(t)


def remove_constraint(child, child_col):
    """
    Removes constraint from the current database.
    :param child: The child table name
    :type child: String
    :param child_col: The child column name
    :type child_col: String
    """
    # Validate that the referenced columns exist in the respective tables.
    # Parent table
    constraint = '{}_{}_fkey'.format(child, child_col)
    sql = 'ALTER TABLE {} DROP CONSTRAINT IF EXISTS {};'.format(
        child, constraint
    )
    t = text(sql)
    _execute(t)


def add_constraint(child_table, child_column, parent_table):
    """
    Adds constraint to a table.
    :param child_table: The table name in which the constraint is added.
    :type child_table: String
    :param child_column: The foreign key column/child column name
    :type child_column: String
    :param parent_table: The source/parent table name
    :type parent_table: String
    :return:
    :rtype:
    """
    remove_constraint(child_table, child_column)
    sql = 'ALTER TABLE {0} ' \
          'ADD CONSTRAINT {0}_{1}_fkey FOREIGN KEY ({1}) ' \
          'REFERENCES {2} (id) MATCH SIMPLE ' \
          'ON UPDATE NO ACTION ON DELETE NO ACTION;'.format(
        child_table, child_column, parent_table
    )
    t = text(sql)
    _execute(t)


def drop_column(table, column):
    """
    Deletes column from a table.
    :param table: The table name in which the column resides.
    :type table: String
    :param column: The column name to be deleted.
    :type column: String
    """
    sql = 'ALTER TABLE {} DROP COLUMN {} CASCADE;'.format(
        table, column
    )
    t = text(sql)
    _execute(t)


def postgis_exists():
    """
    Checks if the PostGIS extension exists in the STDM database.
    """
    sql = "SELECT * FROM pg_available_extensions WHERE name='postgis';"
    t = text(sql)
    results = _execute(t)
    for result in results:
        if result['name'] == 'postgis':
            return True
    return False


def create_postgis():
    """
    Creates the postgis extension in the STDM database.
    """
    sql = 'CREATE EXTENSION postgis;'
    t = text(sql)
    _execute(t)


def profile_sequences(prefix):
    """
    Returns all sequences of a given profile based on the profile prefix.
    :param prefix: The profile prefix.
    :type prefix: String
    :return: The list of prefix names in a profile.
    :rtype: List
    """
    sql = 'SELECT sequence_name FROM information_schema.sequences;'
    result = _execute(sql)
    profile_sequences = []
    column_name = 'sequence_name'
    for r in result:
        profile_sequence = r[column_name]
        splited_sequence = profile_sequence.split('_')
        if len(splited_sequence) > 1:
            if splited_sequence[0] == prefix:
                profile_sequences.append(profile_sequence)

    return profile_sequences


def set_child_dependencies_null_on_delete(table):
    """
    Sets the foreign key constraints of child tables to null on delete. This
    is a workaround for foreign keys whose delete action has been set to
    NO_ACTION.
    :param table: Name of the parent table.
    :type table: str
    :return: True if the operation succeeded, otherwise False.
    :rtype: bool
    """
    # Get foreign key dependencies
    deps = foreign_key_parent_tables(table, False)

    if deps is None or len(deps) == 0:
        return False

    for d in deps:
        local_col, fk_table, fk_col, fk_name = d[0], d[1], d[2], d[3]

        # Drop the constraint
        sql = 'ALTER TABLE {0} DROP CONSTRAINT IF EXISTS {1};'.format(
            fk_table, fk_name
        )
        _execute(sql)

        # Recreate constraint
        sql = 'ALTER TABLE {0} ADD CONSTRAINT {1} FOREIGN KEY ({2}) ' \
              'REFERENCES {3}({4}) ON DELETE SET NULL;'.format(
            fk_table,
            fk_name,
            fk_col,
            table,
            local_col
        )
        _execute(sql)

    return True
