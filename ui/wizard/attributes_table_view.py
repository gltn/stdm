"""
/***************************************************************************
Name                 : AttributesTableView
Description          : Table for viewing an entity's attributes.
Date                 : 13/July/2017
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

from collections import OrderedDict

from PyQt4.QtGui import (
    QAbstractItemView,
    QHeaderView,
    QStandardItem,
    QStandardItemModel,
    QTableView
)
from PyQt4.QtCore import (
    QModelIndex,
    Qt
)


class AttributesTableView(QTableView):
    """
    Table view for displaying a collection of column objects. Management of 
    the entity's columns will be done by the calling class.
    """
    def __init__(self, parent=None, attributes=None):
        super(AttributesTableView, self).__init__(parent)

        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)

        hv = self.horizontalHeader()
        hv.setResizeMode(QHeaderView.Interactive)
        hv.setStretchLastSection(True)

        self._configure_model()

        # Adjust column width
        hv.resizeSection(0, 110)
        hv.resizeSection(1, 110)

    def _configure_model(self):
        model = QStandardItemModel(0, 3, self)

        # Set headers
        headers = [
            self.tr('Name'),
            self.tr('Data Type'),
            self.tr('Description')
        ]
        model.setHorizontalHeaderLabels(headers)

        self.setModel(model)

    def add_item(self, attribute):
        """
        Adds a BaseColumn object to the view.
        :param attribute: BaseColumn to be added to the view.
        :type attribute: BaseColumn
        """
        col_name_it = QStandardItem(attribute.name)
        col_type_it = QStandardItem(attribute.display_name())
        col_desc_it = QStandardItem(attribute.description)

        self.model().appendRow([col_name_it, col_type_it, col_desc_it])

    def update_item(self, original_name, attribute):
        """
        Update an existing column entry in the view.
        :param original_name: Original name of the attribute.
        :type original_name: str
        :param attribute: BaseColumn to be edited in the view.
        :type attribute: BaseColumn
        :return: Returns True if the column was successfully updated 
        otherwise False if there is no column with the specified name.
        :rtype: bool
        """
        row_idx = self.row_from_column_name(original_name)
        if row_idx == -1:
            return False

        # Get model idxs
        name_idx = self.model().index(row_idx, 0)
        type_idx = self.model().index(row_idx, 1)
        desc_idx = self.model().index(row_idx, 2)

        # Update row data
        self.model().setData(name_idx, attribute.name, Qt.DisplayRole)
        self.model().setData(
            type_idx,
            attribute.display_name(),
            Qt.DisplayRole
        )
        self.model().setData(
            desc_idx,
            attribute.description,
            Qt.DisplayRole
        )

    def remove_item(self, name):
        """
        Removes an existing column entry from the view.
        :param name: BaseColumn object to be removed.
        :type name: str
        :return: Returns True if the column was successfully removed 
        otherwise False if there is no column with the specified name.
        :rtype: bool
        """
        # Remove row from the view
        row_idx = self.row_from_column_name(name)
        if row_idx == -1:
            return False

        status = self.model().removeRows(row_idx, 1)
        if not status:
            return False

        return True

    def selected_column(self):
        """
        :return: Returns the name of the selected column object in the view 
        otherwise an empty string if there is no row selected.
        :rtype: str
        """
        sel_rw = self.selectionModel().selectedRows()
        if len(sel_rw) == 0:
            return None

        name = self.model().data(sel_rw[0])

        return name

    def row_from_column_name(self, name):
        """
        Get the row index of the given column name.
        :param name: Name of the column.
        :type name: str
        :return: Returns the row index of the matching column name, if not 
        found then returns -1.
        :rtype: int
        """
        row_idx = -1

        items = self.model().findItems(
            name,
            Qt.MatchExactly,
            0
        )

        if len(items) > 0:
            row_idx = items[0].row()

        return row_idx

    def attributes(self):
        """
       :return: Returns a collection of attributes specified in the view.
       :rtype: OrderedDict(name, BaseColumn)
       """
        return self._attrs