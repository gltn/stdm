"""
/***************************************************************************
Name                 : ListPairTableView
Description          : 2-column table view that enables pairing of list data
                       through combo boxes.
Date                 : 24/October/2014
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
from PyQt4.QtGui import (
    QAbstractItemView,
    QComboBox,
    QHeaderView,
    QMessageBox,
    QStyledItemDelegate,
    QStandardItem,
    QStandardItemModel,
    QTableView
)
from PyQt4.QtCore import (
    Qt,
    QModelIndex
)


class PairComboBoxDelegate(QStyledItemDelegate):
    """
    Provides a combobox for editing table view data.
    """

    def __init__(self, parent=None, items_pair=[[], []]):
        QStyledItemDelegate.__init__(self, parent)
        self._items_pair = items_pair

    def _insert_empty_item(self, items_lst):
        if len(items_lst) > 0:
            first_item = items_lst[0]
            if first_item != "":
                items_lst.insert(0, "")

        return items_lst

    def set_items_pair(self, items_pair, empty_item=True):
        if len(items_pair) < 2:
            raise RuntimeError(
                "Item columns' list contains less than two sub-lists.")

        if not isinstance(items_pair[0], list) or \
                not isinstance(items_pair[1], list):
            raise TypeError("Column data should be of type 'list'.")

        # Ensure empty item is only inserted once
        if empty_item:
            items_pair[0] = self._insert_empty_item(items_pair[0])
            items_pair[1] = self._insert_empty_item(items_pair[1])

        self._items_pair = items_pair

    def items_pair(self):
        return self._items_pair

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)

        if index.column() == 0:
            items = self._items_pair[0]

        elif index.column() == 1:
            items = self._items_pair[1]

        editor.addItems(items)

        return editor

    def setEditorData(self, combo_box, index):
        item_text = index.model().data(index)

        if item_text:
            item_idx = combo_box.findText(item_text)

            if item_idx != -1:
                combo_box.setCurrentIndex(item_idx)

        else:
            if combo_box.count() > 0:
                combo_box.setCurrentIndex(0)

    def setModelData(self, combo_box, model, index):
        item_text = combo_box.currentText()

        if combo_box.count() > 0:
            model.setData(index, item_text)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class ListPairTableView(QTableView):
    """
    2-column table view that enables pairing of list data through combo boxes.
    """

    def __init__(self, parent=None):
        QTableView.__init__(self, parent)

        self.setEditTriggers(QAbstractItemView.DoubleClicked |
                             QAbstractItemView.SelectedClicked)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)

        self._pair_model = QStandardItemModel(1, 2, self)
        self._pair_model.dataChanged.connect(self._on_pair_data_changed)

        self.setModel(self._pair_model)
        self.horizontalHeader().setResizeMode(QHeaderView.Stretch)

        self._combo_delegate = PairComboBoxDelegate(self)
        self.setItemDelegate(self._combo_delegate)

    def set_header_labels(self, labels):
        """
        Set the table's header labels using labels.
        :param labels: Header labels.
        :type labels: list
        """
        if len(labels) < 2:
            return

        lbls = []
        for i in range(2):
            lbls.append(labels[i])

        self._pair_model.setHorizontalHeaderLabels(lbls)

    def clear_view(self):
        """
        Clears all row pairings in the view.
        """
        rows = self._pair_model.rowCount()
        self._pair_model.removeRows(0, rows)

        # Insert blank row
        self.append_row()

    def append_row(self):
        """
        Add a blank row after the last item in the view.
        """
        items = [QStandardItem(), QStandardItem()]

        self._pair_model.appendRow(items)

    def set_combo_selection(self, selection, empty_item=True):
        """
        Set combo selection for both columns. Any existing rows will be removed
        from the view.
        :param selection: A list containing two sub-lists for each column that
        correspond to the selection list for the combobox in each column.
        :type selection: list
        :param empty_item: True to insert an empty first item in each of the
        column comboboxes.
        :type empty_item: bool
        """
        self._combo_delegate.set_items_pair(selection, empty_item)

        self.clear_view()

    def _on_pair_data_changed(self, old_index, new_index):
        """
        This slot asserts whether selections in both columns in a row have
        been specified. If true, then automatically adds a new empty row
        for additional entries; If false, then the empty is removed from
        the view.
        :param old_index: Model index
        :type old_index: QModelIndex
        :param new_index: Model index
        :type new_index: QModelIndex
        """
        row_state = self.row_data_state(new_index.row())

        row_data = self.row_data(new_index.row())
        if row_state == 0:
            self._pair_model.removeRows(new_index.row(), 1)

            if self._pair_model.rowCount() == 0:
                self.append_row()

        elif row_state == 2:
            if not self.is_last_row_empty():
                self.append_row()

    def is_last_row_empty(self):
        """
        :return: True if the last row in the view does not contain any data,
        False if one or both columns contains data.
        :rtype: bool
        """
        last_row_idx = self._pair_model.rowCount() - 1

        last_row_state = self.row_data_state(last_row_idx)
        if last_row_state == 0:
            return True

        else:
            return False

    def row_data_state(self, row_index):
        """
        :param row_index: Row position
        :type row_index: int
        :return: 0 if data for each of the columns is empty. 1 if one column
        contains data and the other is empty. 2 if both columns contain data.
        :rtype: int
        """
        col_0_val, col_1_val = self.row_data(row_index)

        if col_0_val is None and col_1_val is None:
            return 0

        elif self._is_empty(col_0_val) and not self._is_empty(col_1_val):
            return 1

        elif not self._is_empty(col_0_val) and self._is_empty(col_1_val):
            return 1

        elif self._is_empty(col_0_val) and self._is_empty(col_1_val):
            return 0

        elif not self._is_empty(col_0_val) and not self._is_empty(col_1_val):
            return 2

    def _is_empty(self, val):
        if val is None:
            return True

        else:
            if (isinstance(val, str) or isinstance(val, unicode)) and not val:
                return True

        return False

    def row_data(self, row_index):
        """
        :param row_index: Row position
        :type row_index: int
        :return: Data in both first and second columns for the specified row.
        :rtype: tuple
        """
        if row_index >= 0:
            idx_col_0 = self._pair_model.index(row_index, 0)
            idx_col_1 = self._pair_model.index(row_index, 1)

            val_0 = self._pair_model.data(idx_col_0)
            val_1 = self._pair_model.data(idx_col_1)

            return val_0, val_1

        else:
            return None, None

    def column_pairings(self):
        """
        :return: Collection of column matchings specified as specified by the user.
        :rtype: dict
        """
        col_pairings = {}

        for row_idx in range(self._pair_model.rowCount()):
            if self.row_data_state(row_idx) != 0:
                col_val_0, col_val_1 = self.row_data(row_idx)
                col_pairings[col_val_0] = col_val_1

        return col_pairings
