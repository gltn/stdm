"""
/***************************************************************************
Name                 : STRSpatialUnitListView
Description          : A widget for listing and selecting STR spatial unit
                       entities.
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
from PyQt4.QtGui import (
    QStandardItem
)
from PyQt4.QtCore import (
    pyqtSignal,
    Qt
)

from stdm import AbstractSTREnityListView


class STRSpatialUnitListView(AbstractSTREnityListView):
    """
    A widget for listing and selecting STR spatial unit entities.
    .. versionadded:: 1.7
    """
    spatial_unit_selected = pyqtSignal(QStandardItem)
    spatial_unit_deselected = pyqtSignal(QStandardItem)

    def __init__(self, parent=None, **kwargs):
        super(STRSpatialUnitListView, self).__init__(parent, **kwargs)

    def _on_item_changed(self, item):
        # Emit signals when an item has been (de)selected.
        if item.checkState() == Qt.Checked:
            self.spatial_unit_selected.emit(item)
        elif item.checkState() == Qt.Unchecked:
            self.spatial_unit_deselected.emit(item)

    def _load_profile_entities(self):
        # Override base class implementation
        # Reset view
        self.clear()

        # Populate entity items in the view
        for e in self._profile.user_entities():
            # Load spatial unit entities only
            if e.has_geometry_column():
                self._add_entity(e)

    def _select_str_entities(self):
        # Override default implementation.
        if not self._social_tenure is None:
            self.select_spatial_units(self.social_tenure.spatial_units)

    def select_spatial_units(self, sp_units):
        """
        Checks spatial unit entities in the view and emit the
        spatial_unit_selected signal for each item selected.
        :param sp_units: Collection of STR party entities.
        :type sp_units: list
        """
        # Call base classs implementation
        self.select_entities(sp_units)

    def spatial_units(self):
        """
        :return: Returns a list of selected spatial unit names.
        :rtype: list
        """
        # Call base class implementation
        return self.selected_entities()

    def select_spatial_unit(self, name):
        """
        Selects a spatial unit entity with the given short name.
        :param name: Entity short name
        :type name: str
        """
        # Call base class implementation
        self.select_entity(name)

    def deselect_spatial_unit(self, name):
        """
        Deselects a spatial unit entity with the given short name.
        :param name: Entity short name
        :type name: str
        """
        # Call base class implementation
        self.deselect_entity(name)