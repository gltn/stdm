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
from sqlalchemy import Table

def entity_updater(entity):
    """
    Creates/updates/deletes an entity in the database using SQLAlchemy.
    :param entity: Entity instance.
    :type entity: Entity
    """
    pass