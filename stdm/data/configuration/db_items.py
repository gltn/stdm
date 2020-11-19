"""
/***************************************************************************
Name                 : DbItem
Description          : Base classes for database table and column items.
Date                 : 26/December/2015
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


class DbItem:
    """
    Represents the main objects
    that are managed in the database. Constraints
    are handled separately since they are implicitly referenced by this item.
    """
    ALTER, CREATE, DROP, NONE = range(0, 4)
    sql_updater = None

    def __init__(self, name, action=1):
        self.name = name
        self.action = action


class TableItem(DbItem):
    pass


class ColumnItem(DbItem):
    pass
