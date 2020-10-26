"""
/***************************************************************************
Name                 : MultipleSelectTreeView
Description          : Custom QListView implementation that displays checkable
                       items.
Date                 : 21/June/2016
copyright            : (C) 2016 by UN-Habitat and implementing partners.
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
    QStandardItemModel,
)
from qgis.PyQt.QtWidgets import (
    QAbstractItemView,
    QListView
)

from stdm.data.configuration import entity_model
from stdm.data.configuration.columns import MultipleSelectColumn


class MultipleSelectTreeView(QListView):
    """
    Custom QListView implementation that displays checkable items from a
    multiple select column type.
    """

    def __init__(self, column, parent=None):
        """
        Class constructor.
        :param column: Multiple select column object.
        :type column: MultipleSelectColumn
        :param parent: Parent widget for the control.
        :type parent: QWidget
        """
        QListView.__init__(self, parent)

        # Disable editing of lookup values
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.column = column

        self._item_model = QStandardItemModel(self)

        self._value_list = self.column.value_list

        # Stores lookup objects based on primary keys
        self._lookup_cache = {}

        self._initialize()

        self._association = self.column.association

        self._first_parent_col = self._association.first_reference_column.name
        self._second_parent_col = self._association.second_reference_column.name

        # Association model
        self._assoc_cls = entity_model(self._association)

    def reset_model(self):
        """
        Resets the item model.
        """
        self._item_model.clear()
        self._item_model.setColumnCount(2)

    def clear(self):
        """
        Clears all items in the model.
        """
        self._item_model.clear()

    @property
    def association(self):
        """
        :return: Returns the association object corresponding to the column.
        :rtype: AssociationEntity
        """
        return self._association

    @property
    def value_list(self):
        """
        :return: Returns the ValueList object corresponding to the configured
        column object.
        :rtype: ValueList
        """
        return self._value_list

    @property
    def item_model(self):
        """
        :return: Returns the model corresponding to the checkable items.
        :rtype: QStandardItemModel
        """
        return self._item_model

    def _add_item(self, id, value):
        """
        Adds a row corresponding to id and corresponding value from a lookup
        table.
        :param id: Primary key of a lookup record.
        :type id: int
        :param value: Lookup value
        :type value: str
        """
        value_item = QStandardItem(value)
        value_item.setCheckable(True)
        id_item = QStandardItem(str(id))

        self._item_model.appendRow([value_item, id_item])

    def _initialize(self):
        # Populate list with lookup items
        self.reset_model()

        # Add all lookup values in the value list table
        vl_cls = entity_model(self._value_list)
        if not vl_cls is None:
            vl_obj = vl_cls()
            res = vl_obj.queryObject().all()
            for r in res:
                self._lookup_cache[r.id] = r
                self._add_item(r.id, r.value)

        self.setModel(self._item_model)

    def clear_selection(self):
        """
        Unchecks all items in the view.
        """
        for i in range(self._item_model.rowCount()):
            value_item = self._item_model.item(i, 0)

            if value_item.checkState() == Qt.Checked:
                value_item.setCheckState(Qt.Unchecked)

                if value_item.rowCount() > 0:
                    value_item.removeRow(0)

    def selection(self):
        """
        :return: Returns a list of selected items.
        :rtype: list
        """
        selection = []

        for i in range(self._item_model.rowCount()):
            value_item = self._item_model.item(i, 0)

            if value_item.checkState() == Qt.Checked:
                id_item = self._item_model.item(i, 1)
                id = int(id_item.text())

                # Get item from the lookup cache and append to selection
                if id in self._lookup_cache:
                    lookup_rec = self._lookup_cache[id]
                    selection.append(lookup_rec)

        return selection

    def set_selection(self, models):
        """
        Checks items corresponding to the specified models.
        :param models: List containing model values in the view for selection.
        :type models: list
        """
        for m in models:
            search_value = m.value
            v_items = self._item_model.findItems(search_value)

            # Loop through result and check items
            for vi in v_items:
                if vi.checkState() == Qt.Unchecked:
                    vi.setCheckState(Qt.Checked)
