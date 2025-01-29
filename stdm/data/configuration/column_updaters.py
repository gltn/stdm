"""
/***************************************************************************
Name                 : column_updater
Description          : Functions for updating columns in the database based
                        on type.
Date                 : 27/December/2015
copyright            : (C) 2015 by UN-Habitat and implementing partners.
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

from geoalchemy2 import Geometry
from migrate.changeset import *
from migrate.changeset.constraint import CheckConstraint
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Integer,
    Numeric,
    String,
    Table,
    Text,
    Index
)
from sqlalchemy.engine import reflection

from stdm.exceptions import DummyException
from stdm.data.configuration.db_items import DbItem
from stdm.data.database import (
    metadata
)

from stdm.data.pg_utils import (
    drop_cascade_column,
    run_query
)

from . import _bind_metadata

LOGGER = logging.getLogger('stdm')


def _base_col_attrs(col):
    """
    Extracts the base attributes of a column.
    :param col: Base column
    :type col: BaseColumn
    :returns: Dictionary of name-values for an SQLAlchemy column.
    :rtype: dict
    """
    col_attrs = {'nullable': not col.mandatory}
    # col_attrs['index'] = col.index
    # col_attrs['unique'] = col.unique

    return col_attrs


def _quote_value(value):
    # Encloses value in single quotes
    return '\'{0}\''.format(value)


def check_constraint(column, sa_column, table):
    """
    Creates minimum and/or maximum check constraints.
    .. versionadded:: 1.5
    :param column: BoundsColumn object.
    :type column: BoundsColumn
    :param sa_column: SQLAlchemy column object
    :type sa_column: Column
    :param table: SQLAlchemy table object
    :type table: Table
    :return: Returns a check constraint object.
    :rtype: CheckConstraint
    """
    if not hasattr(table.c, column.name):
        return None

    col_attr = getattr(table.c, column.name)

    min_value = str(column.minimum)
    max_value = str(column.maximum)

    # Check if the values need to be enclosed in single quotes
    if column.value_requires_quote():
        min_value = _quote_value(min_value)
        max_value = _quote_value(max_value)

    # Create SQL statements
    min_sql = '{0} >= {1}'.format(column.name, min_value)
    max_sql = '{0} <= {1}'.format(column.name, max_value)

    if column.minimum > column.SQL_MIN and column.maximum == column.SQL_MAX:
        return CheckConstraint(min_sql, columns=[col_attr])

    if column.minimum == column.SQL_MIN and column.maximum < column.SQL_MAX:
        return CheckConstraint(max_sql, columns=[col_attr])

    if column.minimum > column.SQL_MIN and column.maximum < column.SQL_MAX:
        min_max_sql = '{0} AND {1}'.format(min_sql, max_sql)

        return CheckConstraint(min_max_sql, columns=[col_attr])

    return None


def _constraint_exists(constraint_name, table_name):
    """
    Check if a constraint exists in the database.
    :param constraint_name: Name of the constraint.
    :type constraint_name: str
    :param table_name: Name of the table.
    :type table_name: str
    :returns: True if the constraint exists, False otherwise.
    :rtype: bool
    """
    _bind_metadata(metadata)
    inspector = reflection.Inspector.from_engine(metadata.bind)
    constraints = inspector.get_check_constraints(table_name)

    return constraint_name in constraints


def _update_col(column, table, data_type, columns):
    """
    Update the column based on the database operation.
    :param column: Base column.
    :type column: BaseColumn
    :param columns: Existing column names in the database for the given table.
    :type columns: list
    :returns: SQLAlchemy column object.
    :rtype: Column
    """
    from stdm.data.configuration.columns import BoundsColumn

    alchemy_column = Column(column.name, data_type, **_base_col_attrs(column))

    idx_name = None
    if column.index:
        idx_name = 'idx_{0}_{1}'.format(column.entity.name, column.name)

    unique_name = None
    if column.unique:
        unique_name = 'unq_{0}_{1}'.format(column.entity.name, column.name)

    if column.action == DbItem.CREATE:
        # Ensure the column does not exist otherwise an exception will be thrown
        if column.name not in columns:

            alchemy_column.create(
                table=table,
                unique_name=unique_name
            )

            # Create check constraints accordingly
            if isinstance(column, BoundsColumn) and \
                    column.can_create_check_constraints():
                # Create check constraint if need be
                chk_const = check_constraint(
                    column, alchemy_column, table
                )
                if chk_const is not None:
                    chk_const.create()

    elif column.action == DbItem.ALTER:
        # Ensure the column exists before altering
        if column.name in columns:
            col_attrs = _base_col_attrs(column)

            col_attrs['table'] = table

            alchemy_column.alter(**col_attrs)

    elif column.action == DbItem.DROP:
        # Ensure the column exists before dropping
        if column.name in columns:
            _clear_ref_in_entity_relations(column)
            # Use drop cascade command
            drop_cascade_column(column.entity.name, column.name)

    # Ensure column is added to the table
    if alchemy_column.table is None:
        alchemy_column._set_parent(table)
    # add different type of index for columns with index
    if column.index:
        _bind_metadata(metadata)
        inspector = reflection.Inspector.from_engine(metadata.bind)
        indexes_list = inspector.get_indexes(column.entity.name)
        indexes = [i['name'] for i in indexes_list if not i['unique']]
        # get_indexes do not get gist indexes so try/ except needs to be used.
        try:
            if idx_name not in indexes:

                if column.TYPE_INFO == 'GEOMETRY':
                    idx = Index(idx_name, alchemy_column, postgresql_using='gist')
                    idx.create()

                else:
                    idx = Index(idx_name, alchemy_column, postgresql_using='btree')
                    idx.create()
        except DummyException:
            pass


    return alchemy_column


def _clear_ref_in_entity_relations(column):
    # Check if the column is referenced by entity relation objects and delete.
    child_relations = column.child_entity_relations()
    parent_relations = column.parent_entity_relations()

    referenced_relations = child_relations + parent_relations

    # Flag profile to remove entity relations that reference the given column
    for er in referenced_relations:
        column.profile.remove_relation(er.name)


def base_column_updater(base_column, table, columns):
    """
    Generic function to be implemented by a BaseColumn object for updating
    the table column in the database using SQLAlchemy.
    This is a default implementation which does nothing.
    :param base_column: BaseColumn or its subclass object.
    :type base_column: BaseColumn
    :param table: SQLAlchemy table object
    :type table: Table
    :param columns: Existing column names in the database for the given table.
    :type columns: list
    """
    pass


def serial_updater(column, table, columns):
    """
    Updater for a serial column.
    :param serial_column: Serial column.
    :type serial_column: SerialColumn
    :param columns: Existing column names in the database for the given table.
    :type columns: list
    """
    col = Column(column.name, Integer, primary_key=True)

    if col.name in columns:
        return col

    if column.action == DbItem.CREATE:
        col.create(table=table)

    return col


def varchar_updater(column: 'Column', table: str, columns: list):
    """
    Updater for a character varying column.
    :param varchar_column: Character varying column.
    :type varchar_column: VarCharColumn
    :param columns: Existing column names in the database for the given table.
    :type columns: list
    """

    if column.action == DbItem.ALTER:
        alter = f"ALTER TABLE {table} ALTER COLUMN {column.name} TYPE varchar({column.maximum});"
        run_query(alter)
        return

    return _update_col(column, table, String(column.maximum), columns)


def text_updater(column, table, columns):
    """
    Updater for a text column.
    :param column: Text column.
    :type column: TextColumn
    :param columns: Existing column names in the database for the given table.
    :type columns: list
    """
    return _update_col(column, table, Text, columns)


def integer_updater(column, table, columns):
    """
    Updater for an integer column.
    :param column: Integer column
    :type column: IntegerColumn
    :param columns: Existing column names in the database for the given table.
    :type columns: list
    """
    return _update_col(column, table, Integer, columns)


def double_updater(column, table, columns):
    """
    SQLAlchemy does not have a corresponding float type so NUMERIC type will be used.
    :param column: Double column
    :type column: DoubleColumn
    :param columns: Existing column names in the database for the given table.
    :type columns: list
    """
    return _update_col(
        column,
        table,
        Numeric(column.precision, column.scale),
        columns
    )


def date_updater(column, table, columns):
    """
    Updater for a date column.
    :param column: Date column
    :type column: DateColumn
    :param columns: Existing column names in the database for the given table.
    :type columns: list
    """
    return _update_col(column, table, Date, columns)


def datetime_updater(column, table, columns):
    """
    Updater for a date-time column.
    :param column: Date time column
    :type column: DateTimeColumn
    :param columns: Existing column names in the database for the given table.
    :type columns: list
    """
    return _update_col(column, table, DateTime, columns)


def geometry_updater(column, table, columns):
    """
    Updater for a geometry column.
    :param column: Geometry column
    :type column: GeometryColumn
    :param columns: Existing column names in the database for the given table.
    :type columns: list
    """
    geom_type = column.geometry_type()

    return _update_col(column, table, Geometry(geometry_type=geom_type,
                                               srid=column.srid),
                       columns)


def yes_no_updater(column, table, columns):
    """
    Updater for Yes/No column.
    :param column: Yes/No column.
    :type column: BooleanColumn
    :param table: SQLAlchemy table
    :type table: Table
    :param columns: Existing column names in the database for the given table.
    :type columns: list
    """
    return _update_col(column, table, Boolean, columns)
