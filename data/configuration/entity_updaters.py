"""
/***************************************************************************
Name                 : entity_updater
Description          : Functions for updating entities in the database based
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

from sqlalchemy import (
    Column,
    Integer,
    Table
)

from stdm.data.configuration import entity_model
from stdm.data.configuration.db_items import DbItem
from stdm.data.pg_utils import (
    drop_cascade_table,
    drop_view,
    table_column_names
)

LOGGER = logging.getLogger('stdm')


def entity_updater(entity, engine, metadata):
    """
    Creates/updates/deletes an entity in the database using SQLAlchemy.
    :param entity: Entity instance.
    :type entity: Entity
    :param engine: SQLAlchemy engine object.
    :type engine: Engine
    :param metadata: Database container with the schema definition.
    :type metadata: MetaData
    """
    if entity.is_proxy:
        LOGGER.debug('%s is a proxy entity. Table creation will be skipped.',
                     entity.name)

        return

    LOGGER.debug('Attempting to update %s entity', entity.name)

    #All tables will have an ID column
    table = Table(entity.name, metadata,
                  Column('id', Integer, primary_key=True),
                  extend_existing=True
                  )

    if entity.action == DbItem.CREATE:
        LOGGER.debug('Creating %s entity...', entity.name)
        create_entity(entity, table, engine)

        #Clear remnants
        _remove_dropped_columns(entity, table)

    elif entity.action == DbItem.ALTER:
        LOGGER.debug('Altering %s entity...', entity.name)
        update_entity_columns(entity, table, entity.updated_columns.values())

    elif entity.action == DbItem.DROP:
        LOGGER.debug('Deleting %s entity...', entity.name)
        #drop_entity(entity, table, engine)
        drop_cascade_table(entity.name)


def create_entity(entity, table, engine):
    """
    Creates a database table corresponding to the entity.
    """
    #Create table
    table.create(engine, checkfirst=True)
    update_entity_columns(entity, table, entity.columns.values())


def drop_entity(entity, table, engine):
    """
    Delete the entity from the database.
    """
    #Drop dependencies first
    status = drop_dependencies(entity)

    #Only drop table if dropping dependencies succeeded
    if status:
        table.drop(engine, checkfirst=True)


def drop_dependencies(entity):
    """
    Deletes dependent views before deleting the table.
    :return: True if the DROP succeeded, otherwise False.
    :rtype: bool
    """
    dep = entity.dependencies()
    dep_views = dep['views']

    for v in dep_views:
        status = drop_view(v)

        if not status:
            return False

    return True


def _table_column_names(table):
    #Returns both spatial and non-spatial column names in the given table.
    sp_cols = table_column_names(table, True)
    textual_cols = table_column_names(table)

    return sp_cols + textual_cols

def _remove_dropped_columns(entity, table):
    # Drop removed columns
    updated_cols = entity.updated_columns.values()
    col_names = _table_column_names(entity.name)

    for c in updated_cols:
        if c.action == DbItem.DROP:
            LOGGER.debug('Dropping %s column.', c.name)

            c.update(table, col_names)

            LOGGER.debug('Finished dropping %s column.', c.name)


def update_entity_columns(entity, table, columns):
    """
    Create, alter or drop the entity columns in the database.
    :param entity: Entity
    :type entity: Entity
    :param table: Table object
    :type table: Table
    :param columns: List of column objects to be updated.
    :type columns: list
    """
    col_names = _table_column_names(entity.name)

    for c in columns:
        if c.name != 'id':
            LOGGER.debug('Updating %s column.', c.name)

            c.update(table, col_names)

            LOGGER.debug('Finished updating %s column.', c.name)


def value_list_updater(value_list, engine, metadata):
    """
    Creates the value list table and adds the lookup values in the table.
    :param value_list: ValueList object containing lookup values.
    :type value_list: ValueList
    :param engine: SQLAlchemy engine object.
    :type engine: Engine
    :param metadata: Database container with the schema definition.
    :type metadata: MetaData
    """
    entity_updater(value_list, engine, metadata)

    #Return if action is to delete the lookup table
    if value_list.action == DbItem.DROP:
        return

    #Update lookup values
    model = entity_model(value_list, True)

    if model is None:
        LOGGER.debug('Model for %s ValueList object could not be created.',
                     value_list.name)

        return

    model_obj = model()

    #Get all the lookup values in the table
    db_values = model_obj.queryObject().all()

    #Update database values
    for cd in value_list.values.values():
        #Search if the current code value exists in the collection
        matching_items = [db_obj for db_obj in db_values if db_obj.value == cd.value]

        model_obj = model()

        #If it does not exist then create
        if len(matching_items) == 0:
            model_obj.code = cd.code
            model_obj.value = cd.value

            model_obj.save()

        else:
            item = matching_items[0]
            needs_update = False

            #Check if the values have changed and update accordingly
            if cd.updated_value:
                item.value = cd.updated_value
                cd.updated_value = ''

                needs_update = True

            if item.code != cd.code:
                item.code = cd.code

                needs_update = True

            if needs_update:
                item.update()

    #Remove redundant values in the database
    for db_val in db_values:
        lookup_val = db_val.value

        #Check if it exists in the lookup collection
        code_value = value_list.code_value(lookup_val)

        model_obj = model()

        #Delete if it does not exist in the configuration collection
        if code_value is None:
            lookup_obj = model_obj.queryObject().filter(model.value == lookup_val).one()
            if not lookup_obj is None:
                lookup_obj.delete()


