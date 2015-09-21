"""
/***************************************************************************
Name                 : HashableMixin
Description          : Mixin class that enables custom objects to be hashable
                       using a concatenation of current date and a randomly
                       generated code.
Date                 : 30/April/2014
copyright            : (C) 2014 by UN-Habitat and implementing partners.
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
from PyQt4.QtCore import QDate

from util import random_code_generator

__all__ = ["HashableMixin"]


class HashableMixin(object):
    """
    Mixin class that enables objects to be hashable using a concatenation of
    current date and a randomly generated code.
    """
    def __init__(self):
        curr_date = QDate.currentDate().toString()
        self._code = curr_date + random_code_generator()

    def __hash__(self):
        return hash(self._code)

    def __cmp__(self, other):
        return cmp(self._code, other._code)
