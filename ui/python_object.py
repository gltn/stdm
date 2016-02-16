"""
/***************************************************************************
Name                 : PythonObject
Description          : provides abstract methods for creating a python class from a table name
Date                 : 5/March/2015
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
from stdm.data.database import Model

def create_dynamic_class(clsname, **attr):
        """create a python object from database table name"""
        return type(clsname, (Model,), dict(**attr))


def class_from_table(clsname):
        return create_dynamic_class(clsname)


