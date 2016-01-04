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
from sqlalchemy import Table

from ..database import (
    metadata,
    STDMDb
)

from .db_items import DbItem

LOGGER = logging.getLogger('stdm')


def entity_updater(entity):
    """
    Creates/updates/deletes an entity in the database using SQLAlchemy.
    :param entity: Entity instance.
    :type entity: Entity
    """
    LOGGER.debug('Attempting to update %s entity', entity.name)

    engine = STDMDb.instance().engine
    table = Table(entity.name, metadata)

    if entity.action == DbItem.CREATE:
        LOGGER.debug('Creating %s entity...', entity.name)
        create_entity(entity, table, engine)

    elif entity.action == DbItem.ALTER:
        LOGGER.debug('Altering %s entity...', entity.name)

    elif entity.action == DbItem.DROP:
        LOGGER.debug('Deleting %s entity...', entity.name)
        drop_entity(entity)


def create_entity(entity, table, engine):
    """
    Creates a database table corresponding to the entity.
    """
    #Create table
    table.create(engine)
    update_entity_columns(entity, table)


def drop_entity(entity, table, engine):
    """
    Delete the entity from the database.
    """
    #Check existing entity relation where this entity is the parent.
    table.drop(engine)


def update_entity_columns(entity, table):
    """
    Create, alter or drop the entity columns in the database.
    :param entity: Entity
    :type entity: Entity
    :param table: Table object
    :type table: Table
    """
    for c in entity.columns.values():
        LOGGER.debug('Updating %s column.', c.name)

        c.update(table)