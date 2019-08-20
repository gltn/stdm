"""
/***************************************************************************
Name                 : Scheme Model
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
from PyQt4.QtGui import *
from sqlalchemy import exc


class SchemeModel(QAbstractTableModel):
    """
    Handles data for Scheme Establishment and First, Second
    and Third Examination FLTS modules
    """
    def __init__(self, data_service):
        super(SchemeModel, self).__init__()
        self.data_service = data_service
        self.query_object = None
        self.results = []
        self._headers = []

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or \
           not (0 <= index.row() < len(self.results)):
            return None
        result = self.results[index.row()]
        column = index.column()
        if role == Qt.DisplayRole:
            if column in result:
                return result[column]
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return int(Qt.AlignLeft|Qt.AlignVCenter)
            return int(Qt.AlignRight|Qt.AlignVCenter)
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            if self._headers:
                return self._headers[section]
        return int(section + 1)

    def rowCount(self, index=QModelIndex()):
        return len(self.results)

    def columnCount(self, index=QModelIndex()):
        # return 12
        return len(self._headers)

    def load(self):
        """
        Loads query results to be used in the table view
        """
        exception = None
        try:
            self.query_object = self.data_service.run_query()
            self.query_object = self.query_object.all()
            fk_entity_name = self.data_service.related_entity_name()
            for row in self.query_object:
                store = {}
                row_dict = row.__dict__
                for n, prop in enumerate(self.data_service.config):
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
                store["data"] = row
                self.results.append(store)
        except (AttributeError, exc.SQLAlchemyError, Exception) as e:
            exception = e
        finally:
            if exception:
                raise exception

    @staticmethod
    def _cast_data(value):
        """
        Cast data from one type to another
        :param value: Item data
        :type value: Multiple types
        :return value: Cast data
        :rtype value: Multiple types
        """
        if isinstance(value, Decimal):
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

