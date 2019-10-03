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
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from sqlalchemy import exc
from sqlalchemy.orm.base import object_mapper
from sqlalchemy.orm.collections import InstrumentedList
from sqlalchemy.orm.exc import UnmappedInstanceError


class DataRoutine:
    """
    Common data manipulation methods
    """

    def _get_value(self, query_obj, column, attr=None):
        """
        Returns entity column value
        :param query_obj: Entity query object
        :type query_obj: Entity
        :param column: Column or related entity name
        :type column: String/Dictionary
        :param attr: Related entity column
        :type attr: String
        :return value: Field value
        :rtype value: Multiple types
        """
        if attr:
            fk_entity_object = getattr(query_obj, attr, None)
            value = getattr(fk_entity_object, column.get(attr), None)
        else:
            value = getattr(query_obj, column, None)
        return value

    def cast_data(self, value):
        """
        Cast data from one type to another
        :param value: Item data
        :type value: Multiple types
        :return value: Cast data
        :rtype value: Multiple types
        """
        value = float(value) if self._is_number(value) else value
        if isinstance(value, (Decimal, int, float)):
            return float(value)
        elif type(value) is datetime.date:
            return QDate(value)
        elif type(value) is datetime.datetime:
            return QDateTime(value).toLocalTime()
        return unicode(value) if value is not None else value

    @staticmethod
    def _is_number(value):
        """
        Checks if value is a number
        :param value: Input value
        :type value: Multiple types
        :return: True if number otherwise return false
        :rtype: Boolean
        """
        try:
            float(value)
            return True
        except (ValueError, TypeError, Exception):
            return False

    @staticmethod
    def _get_collection_item(query_obj, collection_name):
        """
        Returns a collection of related entity values
        :param query_obj: Entity query object
        :type query_obj: Entity Object
        :param collection_name: Name of relationship
        :return item: Collection item of values
        :rtype item:
        """
        for name in collection_name:
            collection = getattr(query_obj, name, None)
            if isinstance(collection, InstrumentedList):
                for item in collection:
                    yield item

    @staticmethod
    def _is_mapped(value):
        """
        Check if value is an ORM mapped object
        :param value: Input value
        :type value: Multiple type
        :return: True if mapped otherwise false
        :rtype: Boolean
        """
        try:
            object_mapper(value)
            return True
        except UnmappedInstanceError:
            return False

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


class Load(DataRoutine):
    """
    Loads query results to be used in the table view
    """
    def __init__(self, data_service, collection_filter=None):
        """
        :param data_service: Data service
        :type data_service: DataService
        :type collection_filter: View data collection identifier
        :type collection_filter: Multiple types
        """
        self._data_service = data_service
        self._fk_entity_name = data_service.related_entities()
        self._collection_name = data_service.collections
        self._results = []
        self._headers = []
        self._collection_filter = collection_filter

    def load(self):
        """
        Load data based on query results
        """
        self._query_data()
        return self._results, self._headers

    def load_collection(self):
        """
        Loads data based on collection items in the query results
        """
        self._query_collection()
        return self._results, self._headers

    def _query_collection(self):
        """
        Gets data based on collection items in the query results
        """
        try:
            query_objs = self._data_service.run_query()
            load_collections = self._data_service.load_collections
            for row in query_objs:
                for item in self._get_collection_item(row, load_collections):
                    store = self._get_query_data(item)
                    if store:
                        store["data"] = item
                        self._results.append(store)
        except (AttributeError, exc.SQLAlchemyError, Exception) as e:
            raise e

    def _query_data(self):
        """
        Gets data based on query results
        """
        try:
            query_objs = self._data_service.run_query()
            for row in query_objs:
                store = self._get_query_data(row)
                if store:
                    store["data"] = row
                    self._results.append(store)
        except (AttributeError, exc.SQLAlchemyError, Exception) as e:
            raise e

    def _get_query_data(self, query_obj):
        """
        Returns query data from specific columns
        :param query_obj: Query object
        :type query_obj: Entity
        :return store: Query data from specific columns
        :rtype store: Dictionary
        """
        store = {}
        for n, prop in enumerate(self._data_service.columns):
            column = prop.values()[0]
            header = prop.keys()[0]
            if isinstance(column, dict):
                fk_name = column.keys()[0]
                if fk_name in self._fk_entity_name and hasattr(query_obj, fk_name):
                    value = self._get_value(query_obj, column, fk_name)
                    store[n] = self.cast_data(value)
                    self._append(header, self._headers)
                    continue
                store[n] = self._get_collection_value(query_obj, column)
                self._append(header, self._headers)
                continue
            elif hasattr(query_obj, column):
                value = self._get_value(query_obj, column)
                store[n] = self.cast_data(value)
                self._append(header, self._headers)
                continue
            store[n] = self.cast_data(column)
            self._append(header, self._headers)
        return store

    def _get_collection_value(self, query_obj, column):
        """
        Gets collection value(s)
        :param query_obj: Query object
        :type query_obj: Entity
        :param column: Column or related entity name
        :type column: Dictionary
        :return: Collection value
        :rtype: Multiple types
        """
        fk_name = column.keys()[0]
        for item in self._get_collection_item(query_obj, self._collection_name):
            if hasattr(item, fk_name) or hasattr(item, column.get(fk_name)):
                if isinstance(self._collection_filter, dict):
                    item_values = {
                        k: getattr(item, k, None) for k, v in
                        self._collection_filter.iteritems()
                    }
                    if item_values == self._collection_filter:
                        return self._get_item_value(item, column)
                else:
                    return self._get_item_value(item, column)
        return None

    def _get_item_value(self, item, column):
        """
        Returns collection item value
        :param item: Entity query object
        :type item: Entity
        :param column: Column as it appears in the database
        :type column: Dictionary
        :return: Collection value
        :rtype: Multiple types
        """
        fk_name = column.keys()[0]
        if self._is_mapped(getattr(item, fk_name, None)):
            value = self._get_value(item, column, fk_name)
            return self.cast_data(value)
        value = self._get_value(item, column.get(fk_name))
        return self.cast_data(value)


class Update(DataRoutine):
    """
    Update database record(s) on edit
    """

    def __init__(self, updates, model_items, data_service):
        """
        :param updates: Update items - values and column indexes
        :type updates: Dictionary
        :param model_items: Model items/records
        :type model_items: List
        :param data_service: Data service
        :type data_service: DataService
        """
        self._updates = updates
        self._model_items = model_items
        self._fk_entity_name = data_service.related_entities()
        self._collection_name = data_service.collections

    def update(self):
        """
        Update database record(s) on client edit
        :return count: Number of updated items
        :rtype count: Integer
        """
        try:
            query_obj, count = self._set_update()
            if query_obj:
                query_obj.update()
        except (AttributeError, exc.SQLAlchemyError, Exception) as e:
            raise e
        else:
            return count

    def _set_update(self):
        """
        Sets update attribute value for the appropriate field
        :return count: Number of updated items
        :rtype count: Integer
        """
        try:
            count = 0
            query_obj = None
            for row_idx, columns in self._updates.iteritems():
                updated = None
                query_obj = self._model_items[row_idx].get("data")
                for column, new_value, collection_filter in columns:
                    if isinstance(column, dict):
                        fk_name = column.keys()[0]
                        if fk_name in self._fk_entity_name and hasattr(query_obj, fk_name):
                            updated = self._set_update_value(
                                query_obj, column, new_value, fk_name
                            )
                            continue
                        updated = self._set_collection_value(
                            query_obj, column, new_value, collection_filter
                        )
                        continue
                    elif hasattr(query_obj, column):
                        updated = self._set_update_value(query_obj, column, new_value)
                        continue
                count = count + 1 if updated else count
        except (AttributeError, exc.SQLAlchemyError, Exception) as e:
            raise e
        else:
            return query_obj, count

    def _set_collection_value(self, query_obj, column, new_value, collection_filter):
        """
        Sets collection update attribute value
        :param query_obj: Query object
        :type query_obj: Entity object
        :param column: Column or related entity name
        :type column: Dictionary
        :param new_value: New value for update
        :type new_value: Multiple types
        :type collection_filter: Collection record data filter
        :type collection_filter: Dictionary
        :return: Entity query object or None
        :rtype: Entity, NoneType
        """
        fk_name = column.keys()[0]
        for item in self._get_collection_item(query_obj, self._collection_name):
            if hasattr(item, fk_name) or hasattr(item, column.get(fk_name)):
                if isinstance(collection_filter, dict):
                    item_values = {
                        k: getattr(item, k, None) for k, v in
                        collection_filter.iteritems()
                    }
                    if item_values == collection_filter:
                        column, fk_name = self._get_update_attr(item, column)
                        return self._set_update_value(item, column, new_value, fk_name)
                else:
                    column, fk_name = self._get_update_attr(item, column)
                    return self._set_update_value(item, column, new_value, fk_name)
        return None

    def _get_update_attr(self, item, column):
        """
        Return update item attribute (column name or
        related entity name)
        :param item: Entity query object
        :type item: Entity
        :param column: Column or related entity name
        :type column: Dictionary
        :return: Entity query object or value
        :rtype: Entity, Multiple types
        :return: Related entity column or None
        :rtype : String, NoneType
        """
        fk_name = column.keys()[0]
        if self._is_mapped(getattr(item, fk_name, None)):
            return column, fk_name
        return column.get(fk_name), None

    def _set_update_value(self, query_obj, column, value, attr=None):
        """"
        Sets update attribute value
        :param query_obj: Entity query object
        :type query_obj: Entity
        :param column: Column or related entity name
        :type column: String/Dictionary
        :param value: New value for update
        :type value: Multiple types
        :param attr: Related entity column or None
        :type attr: String, NoneType
        :return query_obj: Entity query object
        :rtype query_obj: Entity
        """
        if attr:
            query_obj = self._get_value(query_obj, attr)
            setattr(query_obj, column.get(attr), value)
            return query_obj
        setattr(query_obj, column, value)
        return query_obj


class WorkflowManagerModel(QAbstractTableModel):
    """
    Handles data for Scheme Establishment and First, Second
    and Third Examination FLTS modules
    """
    def __init__(self, data_service, collection_filter=None):
        super(WorkflowManagerModel, self).__init__()
        self._data_service = data_service
        self._collection_filter = collection_filter
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

        if role == Qt.DecorationRole and flag == Qt.DecorationRole:

            # TODO: Start refactor
            icon = None
            if isinstance(value, float):
                value = float(value)
                if value == 1:
                    icon = QIcon(":/plugins/stdm/images/icons/flts_approve.png")
                elif value == 2:
                    icon = QIcon(":/plugins/stdm/images/icons/flts_pending.png")
                elif value == 3:
                    icon = QIcon(":/plugins/stdm/images/icons/flts_disapprove.png")
                elif value == 4:
                    icon = QIcon(":/plugins/stdm/images/icons/flts_withdraw.png")
            elif value == "View":
                icon = QIcon(":/plugins/stdm/images/icons/flts_document_view.png")
            return icon
            # TODO: End refactor

        elif role == Qt.DisplayRole and (
                flag != Qt.ItemIsUserCheckable and flag != Qt.DecorationRole
        ):
            return value
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
        try:
            return len(self._headers)
        except IndexError as e:
            return 0

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
        self.dataChanged.emit(index, index)
        return True

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
        Load query results to be used in the table view
        """
        self.results, self._headers = Load(
            self._data_service, self._collection_filter
        ).load()

    def load_collection(self):
        """
        Load collection query results to be used in the table view
        """
        self.results, self._headers = Load(
            self._data_service, self._collection_filter
        ).load_collection()

    def update(self, updates):
        """
        Update database record(s) on client edit
        :param updates: Update items - values and column indexes
        :type updates: Dictionary
        :return: Number of updated items
        :rtype: Integer
        """
        updated = 0
        try:
            updated = Update(
                updates, self.results, self._data_service
            ).update()
        except (AttributeError, exc.SQLAlchemyError, Exception) as e:
            raise e
        else:
            self.refresh()
        finally:
            return updated

    def refresh(self):
        """
        Refresh model
        """
        self.layoutAboutToBeChanged.emit()
        self.results = []
        self._headers = []
        self.load()
        self.layoutChanged.emit()
