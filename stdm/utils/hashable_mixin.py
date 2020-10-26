"""
/***************************************************************************
Name                 : HashableMixin
Description          : Mixin class that enables custom objects to be hashable
                       using a concatenation of current date and a randomly
                       generated code.
Date                 : 30/April/2014
copyright            : (C) 2014 by John Gitau
email                : gkahiu@gmail.com
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
from qgis.PyQt.QtCore import QDate

from stdm.utils.util import randomCodeGenerator

__all__ = ["HashableMixin"]


class HashableMixin(object):
    """
    Mixin class that enables objects to be hashable using a concatenation of
    current date and a randomly generated code.
    """

    def __init__(self):
        currDate = QDate.currentDate().toString()
        self._code = currDate + randomCodeGenerator()

    def __hash__(self):
        return hash(self._code)

    def __cmp__(self, other):
        return cmp(self._code, other._code)
