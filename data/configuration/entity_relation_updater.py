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
from stdm.data.pg_utils import pg_table_exists

from stdm.data.pg_utils import (
    pg_table_exists,
    table_column_names
)


LOGGER = logging.getLogger('stdm')


def foreign_key_constraint(entity_relation):
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
    parent_exists = _check_table_exists(parent)

    if not parent_exists:
        return None

    parent_col_exists = _check_column_exists(entity_relation.parent_column,
                                             parent)
    if not parent_col_exists:
        return None

    #Child table
    child = entity_relation.child.name
    child_exists = _check_table_exists(child)

    if not child_exists:
        return None

    child_col_exists = _check_column_exists(entity_relation.child_column,
                                            child)
    if not child_col_exists:
        return None

    #Create FK constraint
    child_table = _table(child)
    parent_table = _table(parent)

    child_col_attr = getattr(child_table.c, entity_relation.child_column, None)
    parent_col_attr = getattr(parent_table.c, entity_relation.parent_column, None)

    return ForeignKeyConstraint([child_col_attr], [parent_col_attr])


def create_foreign_key_constraint(entity_relation):
    """
    Creates an FK constraint in the database.
    :param entity_relation: EntityRelation object
    :type entity_relation: EntityRelation
    :return: True if the foreign key was successfully created, else False.
    :rtype: bool
    """
    fk_cons = foreign_key_constraint(entity_relation)

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
    fk_cons = foreign_key_constraint(entity_relation)

    if fk_cons is None:
        LOGGER.debug('Foreign key constraint object could not be created.')

        return False

    fk_cons.drop()

    return True


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
    return Table(table_name, metadata)
