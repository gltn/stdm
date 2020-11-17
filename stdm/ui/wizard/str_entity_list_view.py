"""
/***************************************************************************
Name                 : AbstractSTREnityListView
Description          : A widget for listing and selecting STR entities.
Date                 : 8/July/2017
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
from qgis.PyQt.QtCore import (
    Qt
)
from qgis.PyQt.QtGui import (
    QStandardItem,
    QStandardItemModel
)
from qgis.PyQt.QtWidgets import (
    QAbstractItemView,
    QListView
)

from stdm.ui.gui_utils import GuiUtils


class AbstractSTREnityListView(QListView):
    """
    A widget for listing and selecting one or more STR entities.
    .. versionadded:: 1.7
    """

    def __init__(self, parent=None, **kwargs):
        super(AbstractSTREnityListView, self).__init__(parent)

        self._model = QStandardItemModel(self)
        self._model.setColumnCount(1)
        self.setModel(self._model)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._model.itemChanged.connect(self._on_item_changed)

        self._profile = kwargs.get('profile', None)
        self._social_tenure = kwargs.get('social_tenure', None)

        # Load appropriate entities to the view
        if not self._profile is None:
            self._load_profile_entities()

        # Load entities in the STR definition
        if not self._social_tenure is None:
            self._select_str_entities()

    def _on_item_changed(self, item):
        # Emit signals when an item has been (de)selected. To be
        # implemented by subclasses.
        pass

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
        self._select_str_entities()

    def _select_str_entities(self):
        """
        Select the entities defined in the STR. E.g. parties for party
        entity and spatial units for spatial unit entity. Default
        implementation does nothing, to be implemented by subclasses.
        """
        pass

    def _load_profile_entities(self):
        # Reset view
        self.clear()

        # Populate entity items in the view
        for e in self._profile.user_entities():
            self._add_entity(e)

    def _add_entity(self, entity):
        # Add entity item to view
        item = QStandardItem(
            GuiUtils.get_icon('table.png'),
            entity.short_name
        )
        item.setCheckable(True)
        item.setCheckState(Qt.Unchecked)

        self._model.appendRow(item)

    def select_entities(self, entities):
        """
        Checks STR entities in the view and emit the entity_selected
        signal for each item selected.
        :param entities: Collection of STR entities.
        :type entities: list
        """
        # Clear selection
        self.clear_selection()

        for e in entities:
            name = e.short_name
            self.select_entity(name)

    def selected_entities(self):
        """
        :return: Returns a list of selected entity short names.
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

    def select_entity(self, name):
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

    def deselect_entity(self, name):
        """
        Deselects an entity with the given short name.
        :param name: Entity short name
        :type name: str
        """
        items = self._model.findItems(name)
        if len(items) > 0:
            item = items[0]
            if item.checkState() == Qt.Checked:
                item.setCheckState(Qt.Unchecked)
