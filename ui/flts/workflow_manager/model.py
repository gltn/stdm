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
import datetime
from decimal import Decimal
from PyQt4.QtCore import *
from sqlalchemy import exc


class WorkflowManagerModel(QAbstractTableModel):
    """
    Handles data for Scheme Establishment and First, Second
    and Third Examination FLTS modules
    """
    def __init__(self, data_service):
        super(WorkflowManagerModel, self).__init__()
        self.data_service = data_service
        self.query_object = None
        self.results = []
        self._headers = []

    def flags(self, index):
        """
        Implementation of QAbstractTableModel
        flags method
        """
        column = index.column()
        if not index.isValid():
            return Qt.ItemIsEnabled
        elif self._headers[column].flag == Qt.ItemIsUserCheckable:
            return Qt.ItemFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
        return Qt.ItemFlags(QAbstractTableModel.flags(self, index))

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
        if role == Qt.DisplayRole and flag != Qt.ItemIsUserCheckable:
            return value
        elif role == Qt.CheckStateRole and flag == Qt.ItemIsUserCheckable:
            if isinstance(value, float):
                return Qt.Checked if int(value) == 1 else Qt.Unchecked
        elif role == Qt.TextAlignmentRole:
            if flag == Qt.ItemIsUserCheckable:
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
        elif orientation == Qt.Vertical:
            return
        return int(section + 1)

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

    def setData(self, index, value, role=Qt.EditRole):
        """
        Implementation of QAbstractTableModel
        setData method
        """
        if not index.isValid() and \
                not (0 <= index.row() < len(self.results)):
            return False
        result = self.results[index.row()]
        column = index.column()
        flag = self._headers[column].flag
        if isinstance(result.get(column, None), float):
            if flag == Qt.ItemIsUserCheckable:
                result[column] = 1.0 if value == Qt.Checked else 0.0
            else:
                result[column] = float(value)
        else:
            result[column] = value
        self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"), index, index)
        return True

    def load(self):
        """
        Loads query results to be used in the table view
        """
        try:
            self.query_object = self.data_service.run_query()
            fk_entity_name = self.data_service.related_entity_name()
            print(0)
            for row in self.query_object:
                store = {}
                row_dict = row.__dict__
                for n, prop in enumerate(self.data_service.field_option):
                    field = prop.values()[0]
                    header = prop.keys()[0]
                    if isinstance(field, dict):
                        fk_name = field.keys()[0]
                        if fk_name in fk_entity_name and fk_name in row_dict:
                            value = getattr(row_dict[fk_name], field[fk_name])
                            store[n] = self._cast_data(value)
                            self._append(header, self._headers)
                            continue
                    elif field in row_dict:
                        value = row_dict[field]
                        store[n] = self._cast_data(value)
                        self._append(header, self._headers)
                        continue
                    else:
                        store[n] = self._cast_data(field)
                        self._append(header, self._headers)

                store["data"] = row if 'data' not in row_dict else row_dict["data"]
                self.results.append(store)
            print(0)
        except (AttributeError, exc.SQLAlchemyError, Exception) as e:
            raise e

    @staticmethod
    def _cast_data(value):
        """
        Cast data from one type to another
        :param value: Item data
        :type value: Multiple types
        :return value: Cast data
        :rtype value: Multiple types
        """
        if isinstance(value, (Decimal, int)):
            return float(value)
        elif isinstance(value, datetime.date):
            return QDate(value)
        return unicode(value) if value is not None else value

    @staticmethod
    def _append(item, container):
        """
        Append unique items to a list
        :param item: Data attribute
        :type item: Multiple types
        :param container: Items container
        :type container: List
        """
        if item not in container:
            container.append(item)
    @property
    def entity_name(self):
        """
        Entity name
        :return _name: Entity name
        :rtype _name: String
        """
        return self.data_service.entity_name

    def get_record_id(self, row=0):
        """
        Gets record/entity id (primary key)
        :param row: Row index/number
        :rtype row: Integer
        :return: Record id
        :rtype: integer
        """
        return self.results[row]["data"].id

