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
from stdm.ui.stdmdialog import DeclareMapping

class LookupModeller(object):
    def __init__(self,):
        self._lookup = []
        self._lookup_formatter = {}
        self._mapper = DeclareMapping.instance()

    def set_lookup_attribute(self, attribute_name):
        """Add the attribute to the list of attribute in this model"""
        self._lookup.append(attribute_name)

    def lookup_choices(self, attribute_name, lkup_model):
        """
        Temporarily hold the mapping of table to model. Need further implementation
        """
        self._lookup_formatter[attribute_name] = lkup_model

    def lookup_model(self, tName):
        """
        Ensure the lookup table is mapped to an SQLALchemy model
        """
        lk_model = self._mapper.tableMapping(tName.lower())
        self._lookup_formatter[tName.lower()] = lk_model
        return lk_model




