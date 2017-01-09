"""
/***************************************************************************
Name                 : STRPartyListView
Description          : A widget for listing and selecting STR party entities.
Date                 : 5/January/2017
copyright            : John Kahiu
email                : gkahiu at gmail dot com
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
    QAbstractItemView,
    QIcon,
    QListView,
    QStandardItem,
    QStandardItemModel
)
from PyQt4.QtCore import (
    pyqtSignal,
    Qt
)


class STRPartyListView(QListView):
    """
    A widget for listing and selecting STR party entities.
    .. versionadded:: 1.5
    """
    party_selected = pyqtSignal(QStandardItem)
    party_deselected = pyqtSignal(QStandardItem)

    def __init__(self, parent=None, profile=None, social_tenure=None):
        super(STRPartyListView, self).__init__(parent)

        self._model = QStandardItemModel(self)
        self._model.setColumnCount(1)
        self.setModel(self._model)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._model.itemChanged.connect(self._on_item_changed)

        self._profile = profile
        if not self._profile is None:
            self._load_profile_entities()

        self._social_tenure = social_tenure
        if not self._social_tenure is None:
            self.select_parties(self._social_tenure.parties)

    def _on_item_changed(self, item):
        # Emit signals when an item has been (de)selected.
        if item.checkState() == Qt.Checked:
            self.party_selected.emit(item)
        elif item.checkState() == Qt.Unchecked:
            self.party_deselected.emit(item)

    @property
    def profile(self):
        """
        :return: Returns the current profile object in the configuration.
        :rtype: Profile
        """
        return self._profile

    @profile.setter
    def profile(self, profile):
        """
        Sets the current profile object in the configuration.
        :param profile: Profile object.
        :type profile: Profile
        """
        self._profile = profile
        self._load_profile_entities()

    @property
    def social_tenure(self):
        """
        :return: Returns the profile's social tenure entity.
        :rtype: SocialTenure
        """
        return self._social_tenure

    @social_tenure.setter
    def social_tenure(self, social_tenure):
        """
        Set the social_tenure entity.
        :param social_tenure: A profile's social tenure entity.
        :type social_tenure: SocialTenure
        """
        self._social_tenure = social_tenure
        self.select_parties(self._social_tenure.parties)

    def _load_profile_entities(self):
        # Reset view
        self.clear()

        # Populate entity items in the view
        for e in self._profile.user_entities():
            self._add_entity(e)

    def _add_entity(self, party):
        # Add entity item to view
        item = QStandardItem(
            QIcon(':/plugins/stdm/images/icons/table.png'),
            party.short_name
        )
        item.setCheckable(True)
        item.setCheckState(Qt.Unchecked)

        self._model.appendRow(item)

    def select_parties(self, parties):
        """
        Checks party entities in the view and emit the party_selected
        signal for each item selected.
        :param parties: Collection of STR party entities.
        :type parties: list
        """
        # Clear selection
        self.clear_selection()

        for p in parties:
            name = p.short_name
            self.select_party(name)

    def parties(self):
        """
        :return: Returns a list of selected party names.
        :rtype: list
        """
        selected_items = []

        for i in range(self._model.rowCount()):
            item = self._model.item(i)
            if item.checkState() == Qt.Checked:
                selected_items.append(item.text())

        return selected_items

    def clear(self):
        """
        Remove all party items in the view.
        """
        self._model.clear()
        self._model.setColumnCount(1)

    def clear_selection(self):
        """
        Uncheck all items in the view.
        """
        for i in range(self._model.rowCount()):
            item = self._model.item(i)
            if item.checkState() == Qt.Checked:
                item.setCheckState(Qt.Unchecked)

    def select_party(self, name):
        """
        Selects a party entity with the given short name.
        :param name: Entity short name
        :type name: str
        """
        items = self._model.findItems(name)
        if len(items) > 0:
            item = items[0]
            if item.checkState() == Qt.Unchecked:
                item.setCheckState(Qt.Checked)

    def deselect_party(self, name):
        """
        Deselects a party entity with the given short name.
        :param name: Entity short name
        :type name: str
        """
        items = self._model.findItems(name)
        if len(items) > 0:
            item = items[0]
            if item.checkState() == Qt.Checked:
                item.setCheckState(Qt.Unchecked)