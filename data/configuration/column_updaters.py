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
from sqlalchemy import (
    Date,
    DateTime,
    Integer,
    Numeric,
    String,
    Table,
    Text
)

from sqlalchemy.schema import Column

from migrate.changeset import *

from geoalchemy2 import Geometry

from .db_items import DbItem

def _base_col_attrs(col):
    """
    Extracts the base attributes of a column.
    :param col: Base column
    :type col: BaseColumn
    :returns: Dictionary of name-values for an SQLAlchemy column.
    :rtype: dict
    """
    col_attrs = {}
    col_attrs['index'] = col.index
    col_attrs['nullable'] = not col.mandatory
    col_attrs['unique'] = col.unique

    return col_attrs


def base_column_updater(base_column, table):
    """
    Generic function to be implemented by a BaseColumn object for updating
    the table column in the database using SQLAlchemy.
    This is a default implementation which does nothing.
    :param base_column: BaseColumn or its subclass object.
    :type base_column: BaseColumn
    :param table: SQLAlchemy table object
    :type table: Table
    """
    pass

def _update_col(column, table, data_type):
    """
    Update the column based on the database operation.
    :param column: Base column.
    :type column: BaseColumn
    :returns: SQLAlchemy column object.
    :rtype: Column
    """
    alchemy_column = Column(column.name, data_type, **_base_col_attrs(column))

    if column.action == DbItem.CREATE:
        alchemy_column.create(table)

    elif column.action == DbItem.ALTER:
        alchemy_column.alter(**_base_col_attrs(column))

    elif column.action == DbItem.DROP:
        pass

    return alchemy_column


def serial_updater(column, table):
    """
    Updater for a serial column.
    :param serial_column: Serial column.
    :type serial_column: SerialColumn
    """
    col = Column(column.name, Integer, primary_key=True)

    if col.action == DbItem.CREATE:
        col.create(table)

    return col


def varchar_updater(column, table):
    """
    Updater for a character varying column.
    :param varchar_column: Character varying column.
    :type varchar_column: VarCharColumn
    """
    return _update_col(column, table, String(column.maximum))


def text_updater(column, table):
    """
    Updater for a text column.
    :param column: Text column.
    :type column: TextColumn
    """
    return _update_col(column, table, Text)


def integer_updater(column, table):
    """
    Updater for an integer column.
    :param column: Integer column
    :type column: IntegerColumn
    """
    col = Column(column.name, Integer,
                 **_base_col_attrs(column))
    col.create(table)

    return col


def double_updater(column, table):
    """
    SQLAlchemy does not have a corresponding float type so NUMERIC type will be used.
    :param column: Double column
    :type column: DoubleColumn
    """
    return _update_col(column, table, Numeric)


def date_updater(column, table):
    """
    Updater for a date column.
    :param column: Date column
    :type column: DateColumn
    """
    return _update_col(column, table, Date)


def datetime_updater(column, table):
    """
    Updater for a date-time column.
    :param column: Date time column
    :type column: DateTimeColumn
    """
    return _update_col(column, table, DateTime)


def geometry_updater(column, table):
    """
    Updater for a geometry column.
    :param column: Geometry column
    :type column: GeometryColumn
    """
    geom_type = column.geometry_type()

    return _update_col(column, table, Geometry(geometry_type=geom_type,
                                               srid=column.srid))
