"""
/***************************************************************************
Name                 : entity_relation_updater
Description          : Functions for updating entity relations..
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

from sqlalchemy import Table
from sqlalchemy.exc import ProgrammingError

from migrate.changeset.constraint import ForeignKeyConstraint

from stdm.data.database import (
    metadata
)

from stdm.data.pg_utils import (
    pg_table_exists,
    table_column_names
)


LOGGER = logging.getLogger('stdm')


def _table_col_attr(table, col_names):
    col_attrs = []

    for c in col_names:
        col_attr = getattr(table.c, c, None)
        if not col_attr is None:
            col_attrs.append(col_attr)

    return col_attrs


def fk_constraint(child, child_cols, parent, parent_cols):
    """
    Creates a ForeignKeyConstraint object based on the parent and child
    table information.
    :param child: Name of the child table.
    :type child: str
    :param child_cols: Column names in constraint.
    :type child_cols: list
    :param parent: Name of the parent table.
    :type parent: str
    :param parent_cols: Referred column names in the other table.
    :type parent_cols: list
    :return: A ForeignKeyConstraint object or None if some of the information
    is invalid.
    :rtype: ForeignKeyConstraint
    """
    parent_exists = _check_table_exists(parent)

    if not parent_exists:
        return

    all_parent_cols_exist = True
    for c in parent_cols:
        parent_col_exists = _check_column_exists(c, parent)
        if not parent_col_exists:
            all_parent_cols_exist = False

    if not all_parent_cols_exist:
        return None

    child_exists = _check_table_exists(child)

    if not child_exists:
        return None

    all_child_cols_exist = True
    for cc in child_cols:
        child_col_exists = _check_column_exists(cc, child)
        if not child_col_exists:
            all_child_cols_exist = False

    if not all_child_cols_exist:
        return None

    child_table = _table(child)
    parent_table = _table(parent)

    child_col_attrs = _table_col_attr(child_table, child_cols)
    parent_col_attrs = _table_col_attr(parent_table, parent_cols)

    #Return None if one of the column attributes is None
    if len(child_col_attrs) == 0 or len(parent_col_attrs) == 0:
        return None

    return ForeignKeyConstraint(child_col_attrs, parent_col_attrs)


def fk_constraint_from_er(entity_relation):
    """
    Creates a ForeignKeyConstraint object from an EntityRelation object.
    :param entity_relation: EntityRelation object.
    :type entity_relation: EntityRelation
    :return: A ForeignKeyConstraint object.
    :rtype: ForeignKeyConstraint
    """
    #Validate that the referenced columns exist in the respective tables.
    #Parent table
    parent = entity_relation.parent.name
    parent_col = entity_relation.parent_column

    #Child table
    child = entity_relation.child.name
    child_col = entity_relation.child_column

    return fk_constraint(child, [child_col], parent, [parent_col])


def create_foreign_key_constraint(entity_relation):
    """
    Creates an FK constraint in the database.
    :param entity_relation: EntityRelation object
    :type entity_relation: EntityRelation
    :return: True if the foreign key was successfully created, else False.
    :rtype: bool
    """
    fk_cons = fk_constraint_from_er(entity_relation)

    if fk_cons is None:
        LOGGER.debug('Foreign key constraint object could not be created.')

        return False

    #Catch exception of foreign key already exists
    try:
        fk_cons.create()

        return True

    except ProgrammingError as pe:
        LOGGER.debug('Creation of foreign key constraint failed - %s',
                     unicode(pe))

        return False


def drop_foreign_key_constraint(entity_relation):
    """
    Drops an FK constraint in the database.
    :param entity_relation: EntityRelation object
    :type entity_relation: EntityRelation
    :return: True if the foreign key was successfully dropped, else False.
    :rtype: bool
    """
    fk_cons = fk_constraint_from_er(entity_relation)

    if fk_cons is None:
        LOGGER.debug('Foreign key constraint object could not be created.')

        return False

    '''
    Catch and log exception if the constraint does not exist mostly due to
    related cascades(s) having removed the constraint.
    '''
    try:
        fk_cons.drop()

        return True

    except ProgrammingError as pe:
        LOGGER.debug('Drop of foreign key constraint failed - %s',
                     unicode(pe))

        return False


def _check_table_exists(table):
    table_exists = pg_table_exists(table, False)

    if not table_exists:
        LOGGER.debug('%s table does not exist. Foreign key will not be '
                     'created.', table)

        return False

    return True


def _check_column_exists(column, table):
    table_columns = table_column_names(table)

    if not column in table_columns:
        LOGGER.debug('%s column does not exist in % table. Foreign key will '
                     'not be created', column, table)

        return False

    return True


def _table(table_name):
    return Table(table_name, metadata, autoload=True)
