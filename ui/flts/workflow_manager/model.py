"""
/***************************************************************************
Name                 : Workflow Manager Model
Description          : Model for handling scheme table data in
                       Scheme Establishment and First, Second and
                       Third Examination FLTS modules.
Date                 : 11/August/2019
copyright            : (C) 2019
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

from PyQt4.QtCore import *
from sqlalchemy import exc


class WorkflowManagerModel(QAbstractTableModel):
    """
    Handles data for Scheme Establishment and First, Second
    and Third Examination FLTS modules
    """
    def __init__(self, data_source, data_service):
        super(WorkflowManagerModel, self).__init__()
        self._data_source = data_source
        self._data_service = data_service
        self._icons = self._data_service.icons \
            if hasattr(self._data_service, "icons") else None
        self._vertical_header = self._data_service.vertical_header
        self.results = []
        self._headers = []

    def data(self, index, role=Qt.DisplayRole):
        """
        Implementation of QAbstractTableModel
        data method
        """
        if not index.isValid() or \
           not (0 <= index.row() < len(self.results)):
            return
        result = self.results[index.row()]
        column = index.column()
        value = result.get(column, None)
        flag = self._headers[column].flag
        if role == Qt.DisplayRole and flag not in(
                Qt.ItemIsUserCheckable, Qt.DecorationRole
        ):
            return value
        elif role == Qt.DecorationRole and flag == Qt.DecorationRole:
            if self._icons:
                if isinstance(value, float):
                    value = float(value)
                return self._icons[value]
        elif role == Qt.CheckStateRole and flag == Qt.ItemIsUserCheckable:
            if isinstance(value, float):
                return Qt.Checked if int(value) == 1 else Qt.Unchecked
        elif role == Qt.TextAlignmentRole:
            if flag == Qt.ItemIsUserCheckable or flag == Qt.DecorationRole:
                return int(Qt.AlignCenter | Qt.AlignVCenter)
            return int(Qt.AlignLeft | Qt.AlignVCenter)
        return

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """
        Implementation of QAbstractTableModel
        headerData method
        """
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return int(Qt.AlignLeft | Qt.AlignVCenter)
            return int(Qt.AlignRight | Qt.AlignVCenter)
        elif role != Qt.DisplayRole:
            return
        if orientation == Qt.Horizontal:
            if self._headers:
                return self._headers[section].name
        if self._vertical_header:
            return section + 1

    def rowCount(self, index=QModelIndex()):
        """
        Implementation of QAbstractTableModel
        rowCount method
        """
        return len(self.results)

    def columnCount(self, index=QModelIndex()):
        """
        Implementation of QAbstractTableModel
        columnCount method
        """
        return len(self._headers)

    def flags(self, index):
        """
        Implementation of QAbstractTableModel
        flags method
        """
        column = index.column()
        flag = QAbstractTableModel.flags(self, index)
        if self._headers[column].flag == Qt.ItemIsUserCheckable:
            flag |= Qt.ItemIsUserCheckable
        return flag

    def setData(self, index, value, role=Qt.EditRole):
        """
        Implementation of QAbstractTableModel
        setData method
        """
        if index.isValid() and (0 <= index.row() < len(self.results)):
            result = self.results[index.row()]
            column = index.column()
            if role == Qt.CheckStateRole:
                result[column] = 1.0 if value == Qt.Checked else 0.0
            self.dataChanged.emit(index, index)
            return True
        return False

    def get_record_id(self, row=0):
        """
        Gets record/entity id (primary key)
        :param row: Row index/number
        :rtype row: Integer
        :return: Record id
        :rtype: integer
        """
        return self.results[row]["data"].id

    def model_item(self, row, column):
        """
        Return model item
        :param row: Row index
        :rtype row: Integer
        :param column: Column index
        :rtype column: Integer
        :return item: Table field value
        :rtype item: Multiple types
        """
        item = self.results[row].get(column)
        return item

    def create_index(self, row, column):
        """
        Safely creates and returns the index
        :param row: Table view row index
        :param column: Table view column
        :return index: Table view item identifier or False
        :rtype index: QModelIndex or Boolean
        """
        index = self.index(row, column)
        if not index.isValid() and \
                not (0 <= index.row() < len(self.results)) and \
                not (0 <= index.column() < len(self._headers)):
            return False
        return index

    @property
    def entity_name(self):
        """
        Entity name
        :return _name: Entity name
        :rtype _name: String
        """
        return self._data_service.entity_name

    def load(self):
        """
        Load results from data source to be used in the table view
        """
        try:
            self.results = self._data_source.load()
            self._headers = self._data_source.get_headers()
        except (AttributeError, exc.SQLAlchemyError, Exception) as e:
            raise e

    def load_collection(self):
        """
        Load collection query results to be used in the table view
        """
        try:
            self.results = self._data_source.load_collection()
            self._headers = self._data_source.get_headers()
        except (AttributeError, exc.SQLAlchemyError, Exception) as e:
            raise e

    def refresh(self):
        """
        Refresh model
        """
        self.layoutAboutToBeChanged.emit()
        self.results = []
        self._headers = []
        self.load()
        self.layoutChanged.emit()
