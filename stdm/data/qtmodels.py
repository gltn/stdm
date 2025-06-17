"""
/***************************************************************************
Name                 : PyQT Models
Description          : Contains entity models for using in PyQt widgets
                       for those controls implementing the Model/View
                       framework
Date                 : 4/June/2013
copyright            : (C) 2013 by John Gitau
email                : gkahiu@gmail.com
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

from decimal import Decimal

from qgis.PyQt.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    Qt,
    QVariant,
    QAbstractListModel,
    QDate,
    QSortFilterProxyModel,
    QAbstractItemModel
)
from qgis.PyQt.QtGui import (
    QColor,
    QFont
)

from stdm.data.modelformatters import (
    LookupFormatter,
    DoBFormatter,
)

# Standard colors for widgets supporting alternating rows
ALT_COLOR_EVEN = QColor(255, 165, 79)
ALT_COLOR_ODD = QColor(135, 206, 255)


class EnumeratorTableModel(QAbstractTableModel):
    """
    Model for displaying enumerators in a tableview
    """

    def __init__(self, enumdata, headerdata, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.enumdata = enumdata
        self.headerdata = headerdata

    def rowCount(self, parent=QModelIndex()):
        return len(self.enumdata)

    def columnCount(self, parent):
        return 4

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        elif role == Qt.DisplayRole or role == Qt.EditRole:
            return QVariant(self.enumdata[index.row()][index.column()])
        elif role == Qt.BackgroundRole:
            if index.row() % 2 == 0:
                # Orange
                return QVariant(ALT_COLOR_EVEN)
            else:
                # Blue
                return QVariant(ALT_COLOR_ODD)
        else:
            return QVariant()

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.headerdata[col])
        return QVariant()

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and role == Qt.EditRole:
            self.enumdata[index.row()][index.column()] = value
            self.dataChanged.emit(index, index)
            return True

        return False

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def insertRows(self, position, rows, parent=QModelIndex()):
        if position < 0 or position > len(self.enumdata):
            return False

        self.beginInsertRows(parent, position, position + rows - 1)

        for i in range(rows):
            self.enumdata.insert(position, ["", "", "", ""])

        self.endInsertRows()

        return True


class DepartmentTableModel(QAbstractTableModel):
    """
    Model for displaying departments in a tableview
    """

    def __init__(self, departmentdata, headerdata, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.dptdata = departmentdata
        self.headerdata = headerdata

    def rowCount(self, parent=QModelIndex()):
        return len(self.dptdata)

    def columnCount(self, parent=QModelIndex()):
        return 3

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        elif role == Qt.DisplayRole or role == Qt.EditRole:
            return QVariant(self.dptdata[index.row()][index.column()])
        elif role == Qt.BackgroundRole:
            if index.row() % 2 == 0:
                # Orange
                return QVariant(ALT_COLOR_EVEN)
            else:
                # Blue
                return QVariant(ALT_COLOR_ODD)
        else:
            return QVariant()

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.headerdata[col])
        return QVariant()

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and role == Qt.EditRole:
            self.dptdata[index.row()][index.column()] = value
            self.dataChanged.emit(index, index)
            return True

        return False

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def insertRows(self, position, rows, parent=QModelIndex()):
        if position < 0 or position > len(self.dptdata):
            return False

        self.beginInsertRows(parent, position, position + rows - 1)

        for i in range(rows):
            self.dptdata.insert(position, ["", "", "", ""])

        self.endInsertRows()

        return True

    def removeRows(self, position, count, parent=QModelIndex()):
        if position < 0 or position > len(self.dptdata):
            return False

        self.beginRemoveRows(parent, position, position + count - 1)

        for i in range(count):
            del self.dptdata[position]

        self.endRemoveRows()

        return True


class QuestionnaireTableModel(QAbstractTableModel):
    """
    Model for use in the questionnaire table view
    """

    def __init__(self, questionnairedata, headerdata, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.questdata = questionnairedata
        self.headerdata = headerdata
        self._wkformatter = WorksiteFormatter()
        self._enumformatter = InvestigatorFormatter()
        self._respformatter = RespondentFormatter()

    def rowCount(self, parent=QModelIndex()):
        return len(self.questdata)

    def columnCount(self, parent=QModelIndex()):
        return 8

    def data(self, index, role):

        indexData = self.questdata[index.row()][index.column()]

        if not index.isValid():
            return QVariant()

        elif role == Qt.DisplayRole:

            col = index.column()
            # Specify formatters for columns with
            if col == 4:
                # Worksite formatter
                return self._wkformatter.setDisplay(indexData)
            elif col == 5:
                # Enumerator formatter
                return self._enumformatter.setDisplay(indexData)
            elif col == 6:
                return self._respformatter.setDisplay(indexData)
            else:
                return QVariant(indexData)

        # For columns representing foreign keys then we need to pass the integer value to the editor
        elif role == Qt.EditRole:
            return QVariant(indexData)

        elif role == Qt.BackgroundRole:
            if index.row() % 2 == 0:
                # Orange
                return QVariant(ALT_COLOR_EVEN)
            else:
                # Blue
                return QVariant(ALT_COLOR_ODD)

        else:
            return QVariant()

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.headerdata[col])
        return QVariant()

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and role == Qt.EditRole:
            self.questdata[index.row()][index.column()] = value
            self.dataChanged.emit(index, index)
            return True

        return False

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def insertRows(self, position, rows, parent=QModelIndex()):
        if position < 0 or position > len(self.questdata):
            return False

        self.beginInsertRows(parent, position, position + rows - 1)

        # Initialize column values for the new row
        initRowVals = ["" for c in range(self.columnCount())]

        for i in range(rows):
            self.questdata.insert(position, initRowVals)

        self.endInsertRows()

        return True

    def removeRows(self, position, count, parent=QModelIndex()):
        if position < 0 or position > len(self.questdata):
            return False

        self.beginRemoveRows(parent, position, position + count - 1)

        for i in range(count):
            del self.questdata[position]

        self.endRemoveRows()

        return True


class UsersRolesModel(QAbstractListModel):
    """
    Model for showing existing system users/roles/contents in a QListView
    """

    def __init__(self, users):
        QAbstractListModel.__init__(self)

        # Cache the users
        self._users = users

    def rowCount(self, parent=QModelIndex()):
        return len(self._users)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self._users[index.row()]

        elif role == Qt.FontRole:
            lstFont = QFont("Segoe UI", 10)
            return lstFont
        else:
            return None

    def insertRows(self, position, rows, parent=QModelIndex()):
        if position < 0 or position > len(self._users):
            return False

        self.beginInsertRows(parent, position, position + rows - 1)

        for i in range(rows):
            self._users.insert(position, "")

        self.endInsertRows()

        return True

    def removeRows(self, row, count, parent=QModelIndex()):
        if row < 0 or row > len(self._users):
            return

        self.beginRemoveRows(parent, row, row + count - 1)
        while count != 0:
            del self._users[row]
            count -= 1
        self.endRemoveRows()

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and role == Qt.EditRole:
            self._users[index.row()] = value
            self.dataChanged.emit(index, index)
            return True

        return False


class PersonTableModel(QAbstractTableModel):
    """
    Model for use in the Person table view
    """

    def __init__(self, persondata, headerdata, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.persondata = persondata
        self.headerdata = headerdata
        self._genderFormatter = LookupFormatter(CheckGender)
        self._mStatFormatter = LookupFormatter(CheckMaritalStatus)
        self._ageFormatter = DoBFormatter()

    def rowCount(self, parent=QModelIndex()):
        return len(self.persondata)

    def columnCount(self, parent=QModelIndex()):
        return 11

    def data(self, index, role):

        indexData = self.persondata[index.row()][index.column()]

        if not index.isValid():
            return QVariant()

        elif role == Qt.DisplayRole:
            col = index.column()

            # Specify formatters for columns whose values are foreign keys
            if col == 5:
                # Gender formatter
                return self._genderFormatter.setDisplay(indexData)

            elif col == 6:
                # Current age calculation
                return self._ageFormatter.setDisplay(indexData)

            elif col == 7:
                return self._mStatFormatter.setDisplay(indexData)

            else:
                return QVariant(indexData)

        # For columns representing foreign keys then we need to pass the integer value to the editor
        elif role == Qt.EditRole:
            # Create QDate from Python date then pass it to QVariant constructor where applicable
            if index.column() == 6:

                if isinstance(indexData, QVariant):
                    return QVariant(indexData)
                else:
                    return QVariant(QDate(indexData))

            else:
                return QVariant(indexData)

        elif role == Qt.BackgroundRole:
            if index.row() % 2 == 0:
                # Orange
                return QVariant(ALT_COLOR_EVEN)
            else:
                # Blue
                return QVariant(ALT_COLOR_ODD)

        else:
            return QVariant()

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.headerdata[col])
        return QVariant()

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and role == Qt.EditRole:
            self.persondata[index.row()][index.column()] = value
            self.dataChanged.emit(index, index)
            return True

        return False

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled

        return Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def insertRows(self, position, rows, parent=QModelIndex()):
        if position < 0 or position > len(self.persondata):
            return False

        self.beginInsertRows(parent, position, position + rows - 1)

        # Initialize column values for the new row
        initRowVals = ["" for c in range(self.columnCount())]

        for i in range(rows):
            self.persondata.insert(position, initRowVals)

        self.endInsertRows()

        return True

    def removeRows(self, position, count, parent=QModelIndex()):
        if position < 0 or position > len(self.persondata):
            return False

        self.beginRemoveRows(parent, position, position + count - 1)

        for i in range(count):
            del self.persondata[position]

        self.endRemoveRows()

        return True


class BaseSTDMTableModel(QAbstractTableModel):
    """
    Generic table model for use in STDM table views.
    """
    ROLE_ATTRIBUTE_NAME = Qt.UserRole + 10
    ROLE_RAW_VALUE = ROLE_ATTRIBUTE_NAME + 1
    ROLE_ROW_ID = ROLE_ATTRIBUTE_NAME + 2

    def __init__(self, initdata, headerdata, parent=None, attribute_names=None, raw_values=None, row_ids=None):
        QAbstractTableModel.__init__(self, parent)

        self._initData = initdata
        self._headerdata = headerdata
        self._attribute_names = attribute_names
        self._raw_values = raw_values
        self._row_ids = row_ids

    def rowCount(self, parent=QModelIndex()):
        return len(self._initData)

    def columnCount(self, parent=QModelIndex()):
        return len(self._headerdata)

    def data(self, index, role):
        if index.row() < 0 or index.row() >= len(self._initData):
            return None

        if index.column() < 0 or index.column() >= self.columnCount():
            return None

        if not index.isValid():
            return None

        if role == BaseSTDMTableModel.ROLE_ATTRIBUTE_NAME:
            return self._attribute_names[index.column()]
        if role == BaseSTDMTableModel.ROLE_ROW_ID:
            return self._row_ids[index.row()]
        elif role == BaseSTDMTableModel.ROLE_RAW_VALUE:
            if self._raw_values is None:
                return self._initData[index.row()][index.column()]
            else:
                return self._raw_values[index.row()][index.column()]
        elif role == Qt.DisplayRole:
            val = self._initData[index.row()][index.column()]

            # Decimal not supported by QVariant so we adapt it to a supported type
            if isinstance(val, Decimal):
                return str(val)

            else:
                return val
        else:
            return None

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._headerdata[section]

        elif orientation == Qt.Vertical and role == Qt.DisplayRole:
            return section + 1

        return None

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and role == Qt.EditRole:
            self._initData[index.row()][index.column()] = value
            self.dataChanged.emit(index, index)
            return True
        elif index.isValid() and role == BaseSTDMTableModel.ROLE_RAW_VALUE:
            if self._raw_values is not None:
                self._raw_values[index.row()][index.column()] = value
            self.dataChanged.emit(index, index)
            return True
        elif index.isValid() and role == BaseSTDMTableModel.ROLE_ROW_ID:
            if self._row_ids is not None:
                self._row_ids[index.row()] = value
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        # elif index.column() > 1:
        #             return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        return Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def insertRows(self, position, rows, parent=QModelIndex()):
        if position < 0 or position > len(self._initData):
            return False

        self.beginInsertRows(parent, position, position + rows - 1)

        # Initialize column values for the new row
        initRowVals = ["" for c in range(self.columnCount())]
        init_raw_values = [None] * self.columnCount()

        for i in range(rows):
            self._initData.insert(position, initRowVals[:])

        if self._raw_values is not None:
            for i in range(rows):
                self._raw_values.insert(position, init_raw_values[:])
        if self._row_ids is not None:
            for i in range(rows):
                self._row_ids.insert(position, None)

        self.endInsertRows()

        return True

    def removeRows(self, position, count, parent=QModelIndex()):

        if position < 0 or position > len(self._initData):
            return False

        self.beginRemoveRows(parent, position, position + count - 1)

        for i in range(count):
            try:
                del self._initData[position]
            except IndexError:
                pass

            if self._raw_values is not None:
                del self._raw_values[position]
            if self._row_ids is not None:
                del self._row_ids[position]

        self.endRemoveRows()

        return True


class VerticalHeaderSortFilterProxyModel(QSortFilterProxyModel):
    """
    A sort/filter proxy model that ensures row numbers in vertical headers
    are ordered correctly.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.filter_params = {}

    def headerData(self, section, orientation, role):
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return section + 1

        return super(VerticalHeaderSortFilterProxyModel, self).headerData(section, orientation, role)

    def set_filter_params(self, parameters: dict):
        """
        Sets a dictionary of filtering parameters to use to filter the model
        """
        self.filter_params = parameters
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        if not super().filterAcceptsRow(source_row, source_parent):
            return False

        for col in range(self.sourceModel().columnCount()):
            attribute_name = self.sourceModel().data(self.sourceModel().index(source_row, col, QModelIndex()),
                                                     BaseSTDMTableModel.ROLE_ATTRIBUTE_NAME)
            if attribute_name in self.filter_params:
                row_attribute_value = self.sourceModel().data(self.sourceModel().index(source_row, col, QModelIndex()),
                                                              BaseSTDMTableModel.ROLE_RAW_VALUE)

                search_cond = self.filter_params[attribute_name][0]
                try:
                    if isinstance(row_attribute_value, str):
                        # For string values we do a case insensitive "contains" search

                        value = str(self.filter_params[attribute_name][1]).upper()

                        if search_cond == "=":
                            is_match = value in row_attribute_value.upper()

                        if search_cond == ">":
                            is_match = value > row_attribute_value.upper()

                        if search_cond == "<":
                            is_match = value < row_attribute_value.upper()

                        #is_match = str(self.filter_params[attribute_name]).upper() in row_attribute_value.upper()
                    else:
                        value = self.filter_params[attribute_name][1]
                        if search_cond == "=":
                            is_match = row_attribute_value == value

                        if search_cond == ">":
                            is_match = row_attribute_value > value

                        if search_cond == "<":
                            is_match = row_attribute_value < value

                except TypeError as te:
                    is_match = False

                if not is_match:
                    return False

        return True


class STRTreeViewModel(QAbstractItemModel):
    """
    Model for rendering social tenure relationship nodes in a tree view.
    """

    def __init__(self, root, parent=None, view=None):
        QAbstractItemModel.__init__(self, parent)
        self._rootNode = root
        self._view = view

    def rowCount(self, parent=QModelIndex()):
        if not parent.isValid():
            parentNode = self._rootNode

        else:
            parentNode = parent.internalPointer()

        return parentNode.childCount()

    def columnCount(self, parent=QModelIndex()):
        return self._rootNode.columnCount()

    def _getNode(self, index):
        """
        Convenience method for extracting STRNodes from the model index.
        """
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node

        return self._rootNode

    def data(self, index, role):
        """
        Data to be displayed in the tree view.
        """
        if not index.isValid():
            return None

        node = self._getNode(index)

        if role == Qt.DisplayRole or role == Qt.EditRole:
            if index.column() >= node.columnCount():
                return None

            return node.data(index.column())

        elif role == Qt.DecorationRole:
            if index.column() == 0:
                if not node.icon() is None and node.depth() > 1:
                    return node.icon()

        elif role == Qt.FontRole:
            if index.column() == 0:
                if node.styleIfChild():
                    if self._view is not None:
                        currFont = self._view.font()
                        currFont.setBold(True)
                        return currFont

        elif role == Qt.ToolTipRole:
            if index.column() >= node.columnCount():
                return None

            return node.data(index.column())

        else:
            return None

    def headerData(self, section, orientation, role):
        """
        Set the column headers to be displayed by the tree view.
        """
        if self._rootNode.columnCount() == 0:
            return

        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._rootNode.data(section)

        elif orientation == Qt.Vertical and role == Qt.DisplayRole:
            return section + 1

        return None

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable

    def parent(self, index):
        """
        Returns a QModelIndex reference of the parent node.
        """
        if not index.isValid():
            return QModelIndex()

        node = self._getNode(index)

        parentNode = node.parent()

        if parentNode == self._rootNode or parentNode is None:
            return QModelIndex()

        return self.createIndex(parentNode.row(), 0, parentNode)

    def index(self, row, column, parent=QModelIndex()):
        if parent.isValid() and parent.column() != 0:
            return QModelIndex()

        parentNode = self._getNode(parent)

        childItem = parentNode.child(row)

        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def removeAllChildren(self, position, count, parent=QModelIndex()):
        """
        Removes all children under the node with the specified parent index.
        """
        parentNode = self._getNode(parent)
        success = True

        self.beginRemoveRows(parent, position, position + count - 1)

        success = parentNode.clear()

        self.endRemoveRows()

        return success

    def removeRows(self, position, count, parent=QModelIndex()):
        """
        Removes count rows starting with the given position under parent from the model.
        """
        parentNode = self._getNode(parent)
        success = True

        self.beginRemoveRows(parent, position, position + count - 1)

        for row in range(count):
            success = parentNode.removeChild(position)

        self.endRemoveRows()

        return success

    def insertRows(self, position, count, parent=QModelIndex()):
        """
        Insert children starting at the given position for the given parent item.
        """
        parentNode = self._getNode(parent)
        success = True

        self.beginInsertRows(parent, position, position + count - 1)
        '''
        We do not insert any children in this case since the internal methods of the
        BaseSTRNode have already inserted the children nodes that contain the
        information.
        '''
        self.endInsertRows()

        return success

    def removeColumns(self, position, columnCount, parent=QModelIndex()):
        success = True

        self.beginRemoveColumns(parent, position, position + columnCount - 1)
        success = self._rootNode.removeColumns(position, columnCount)
        self.endRemoveColumns()

        if self._rootNode.columnCount() == 0:
            self.removeRows(0, self.rowCount())

        return success

    def clear(self):
        """
        Removes all items (rows and columns) in the model.
        """
        rootChildrenNum = self._rootNode.childCount()
        self.beginResetModel()

        # Delete each child individually then clear the root node or else there will be indexing issues
        for i in range(rootChildrenNum):
            childNode = self._rootNode.child(i)
            childNode._parent = None
            del childNode

        self._rootNode.clear()
        # TODO: Clear columns
        self.endResetModel()

    def setData(self, index, value, role):
        """
        Sets the role data for the item at index to value.
        """
        if role == Qt.EditRole or role == Qt.DisplayRole:
            nodeItem = self._getNode(index)
            result = nodeItem.setData(index.column(), value)

            if result:
                self.dataChanged.emit(index, index)

            return result

        return False
