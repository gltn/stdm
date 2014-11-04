"""
/***************************************************************************
Name                 : Lookup
Description          : class for handling lookup and lookup table models for the forms
Date                 : 24/September/2014
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

from stdm.utils import readComboSelections
from stdm.ui.stdmdialog import  DeclareMapping

class LookupModeller(object):
    def __init__(self,):
        self._lookup = []
        self._lookupFormatter = {}
        self._mapper =  DeclareMapping.instance()

    def setLookupAttribute(self, attributeName):
        self._lookup.append(attributeName)

    def lookupChoices(self, attributeName, lkupModel):
        """
        """
        self._lookupFormatter[attributeName] = lkupModel

    def lookupModel(self, tName):
        """
        ensure the lookup table is mapped to an SQLALchemy mapper entity
        """
        lkModel = self._mapper.tableMapping(tName.lower())
        self._lookupFormatter[tName.lower()] = lkModel
        return lkModel




