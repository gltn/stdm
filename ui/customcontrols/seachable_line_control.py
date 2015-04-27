"""
/***************************************************************************
Name                 : lineEditButton
Description          : subclasses Qline edit to support a button for browsing
                        foreign key relations.
Date                 : 8/January/2015
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
from .line_edit_button import SearchableLineEdit


class BrowsableForeingKey(SearchableLineEdit):
    """
    Class to implement browsable line control for foreign key references
    """
    def __init__(self, model = None, parent = None):
        SearchableLineEdit.__init__(self, parent)

        self._dbmodel = model
