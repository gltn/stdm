"""
/***************************************************************************
Name                 : STRPartyListView
Description          : A widget for listing and selecting STR party entities.
Date                 : 5/January/2017
copyright            : (C) 2017 by UN-Habitat and implementing partners.
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
from PyQt4.QtGui import (
    QStandardItem
)
from PyQt4.QtCore import (
    pyqtSignal,
    Qt
)

from stdm.ui.wizard.str_entity_list_view import AbstractSTREnityListView


class STRPartyListView(AbstractSTREnityListView):
    """
    A widget for listing and selecting STR party entities.
    .. versionadded:: 1.5
    """
    party_selected = pyqtSignal(QStandardItem)
    party_deselected = pyqtSignal(QStandardItem)

    def __init__(self, parent=None, **kwargs):
        super(STRPartyListView, self).__init__(parent, **kwargs)

    def _on_item_changed(self, item):
        # Emit signals when an item has been (de)selected.
        if item.checkState() == Qt.Checked:
            self.party_selected.emit(item)
        elif item.checkState() == Qt.Unchecked:
            self.party_deselected.emit(item)

    def _select_str_entities(self):
        # Override default implementation.
        if not self._social_tenure is None:
            self.select_parties(self.social_tenure.parties)

    def select_parties(self, parties):
        """
        Checks party entities in the view and emit the party_selected
        signal for each item selected.
        :param parties: Collection of STR party entities.
        :type parties: list
        """
        # Call base classs implementation
        self.select_entities(parties)

    def parties(self):
        """
        :return: Returns a list of selected party names.
        :rtype: list
        """
        # Call base class implementation
        return self.selected_entities()

    def select_party(self, name):
        """
        Selects a party entity with the given short name.
        :param name: Entity short name
        :type name: str
        """
        # Call base class implementation
        self.select_entity(name)

    def deselect_party(self, name):
        """
        Deselects a party entity with the given short name.
        :param name: Entity short name
        :type name: str
        """
        # Call base class implementation
        self.deselect_entity(name)