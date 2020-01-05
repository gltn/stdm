"""
/***************************************************************************
Name                 : Plot Delegate
Description          : Plot delegate for handling presentation
                       and editing of table view data.
Date                 : 24/December/2019
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
from PyQt4.QtCore import (
    Qt,
    QRegExp
)
from PyQt4.QtGui import (
    QComboBox,
    QRegExpValidator
)
from stdm.ui.flts.workflow_manager.delegates.delegates import (
    GenericDelegate,
    IntegerColumnDelegate,
    ListTextColumnDelegate,
    PlainTextColumnDelegate
)

NAME, IMPORT_AS, DELIMITER, HEADER_ROW, \
GEOM_FIELD, GEOM_TYPE, CRS_ID = range(7)


class DelegateRoutine(object):
    """
    Common delegate manipulation methods
    """
    def is_pdf(self, data_source, index):
        """
        Checks if the file extension is PDF
        :param data_source: Plot file object
        :type data_source: PlotFile
        :param index: Item index identifier
        :type index: QModelIndex
        :return True: Returns true if the file extension is PDF
        :rtype True: Boolean
        """
        file_name = self.file_path(index)
        if data_source.is_pdf(file_name):
            return True

    @staticmethod
    def file_path(index):
        """
        Returns plot import file absolute path
        :param index: Item index identifier
        :type index: QModelIndex
        :return: Plot import file absolute path
        :rtype: Unicode
        """
        results = index.model().results
        results = results[index.row()]
        return results["fpath"]


class ImportTypeColumnDelegate(ListTextColumnDelegate):
    """
    Generic plot import type column delegate
    """
    def createEditor(self, parent, option, index):
        """
        Reimplementation of generic list column
        QItemDelegate createEditor method
        """
        data_source = index.model().data_source()
        if DelegateRoutine().is_pdf(data_source, index):
            return
        import_types = data_source.import_as()
        combobox = QComboBox(parent)
        combobox.addItems(sorted(import_types))
        return combobox


class DelimiterColumnDelegate(ListTextColumnDelegate):
    """
    Generic plot import file delimiter column delegate
    """
    def createEditor(self, parent, option, index):
        """
        Reimplementation of generic list column
        QItemDelegate createEditor method
        """
        data_source = index.model().data_source()
        if DelegateRoutine().is_pdf(data_source, index):
            return
        self.items = data_source.delimiter_names()
        regex = QRegExp(r"^[\w\W]{1}$")
        validator = QRegExpValidator(regex, parent)
        combobox = QComboBox(parent)
        combobox.addItems(sorted(self.items.values()))
        combobox.setEditable(True)
        combobox.setValidator(validator)
        return combobox

    def setModelData(self, editor, model, index):
        """
        Reimplementation of generic list column
        QItemDelegate setModelData method
        """
        delimiter = self._editor_delimiters(editor)
        model.setData(index, delimiter)

    def _editor_delimiters(self, editor):
        """
        Returns editor delimiters
        :param editor: UI editor
        :type editor: QCombobox
        :return delimiter: Delimiter
        :rtype delimiter: String
        """
        delimiter = editor.currentText()
        char = delimiter.split(" ")[0]
        char = char.strip()
        if char and len(char) == 1 and \
                char not in self.items:
            delimiter = "{0} {1}".format(char, "Custom")
        else:
            delimiter = self.items.get(char)
            if not delimiter:
                delimiter = self.items[","]
        return delimiter


class HeaderRowColumnDelegate(IntegerColumnDelegate):
    """
    Generic plot import file header row column delegate
    """
    def createEditor(self, parent, option, index):
        """
        Reimplementation of generic list column
        QItemDelegate createEditor method
        """
        data_source = index.model().data_source()
        if DelegateRoutine().is_pdf(data_source, index):
            return
        self.minimum, self.maximum = self._editor_range(index)
        return IntegerColumnDelegate.createEditor(self, parent, option, index)

    def _editor_range(self, index):
        """
        Returns editor value range
        :param index: Item index identifier
        :type index: QModelIndex
        :return: Value range
        :rtype: Integer
        """
        file_path = DelegateRoutine().file_path(index)
        data_source = index.model().data_source()
        row_count = data_source.row_count(file_path)
        if row_count:
            return 1, row_count
        return 0, 0


class GeometryFieldColumnDelegate(ListTextColumnDelegate):
    """
    Generic plot import file geometry field column delegate
    """
    def createEditor(self, parent, option, index):
        """
        Reimplementation of generic list column
        QItemDelegate createEditor method
        """
        data_source = index.model().data_source()
        if DelegateRoutine().is_pdf(data_source, index):
            return
        self.items = self._editor_geometry_fields(index)
        return ListTextColumnDelegate.createEditor(self, parent, option, index)

    def _editor_geometry_fields(self, index):
        """
        Returns editor geometry fields
        :param index: Item index identifier
        :type index: QModelIndex
        :return: Editor geometry fields
        :rtype: List
        """
        fpath = DelegateRoutine().file_path(index)
        hrow = self._header_row(index)
        delimiter = self._delimiter(index)
        data_source = index.model().data_source()
        return data_source.get_csv_fields(fpath, hrow, delimiter)

    @staticmethod
    def _header_row(index):
        """
        Returns user set header row number
        :param index: Item index identifier
        :type index: QModelIndex
        :return hrow: Header row number
        :rtype hrow: Integer
        """
        i = index.sibling(index.row(), HEADER_ROW)
        hrow = i.model().data(i, Qt.DisplayRole)
        hrow = int(hrow) - 1
        return hrow

    @staticmethod
    def _delimiter(index):
        """
        Returns user set delimiter
        :param index: Item index identifier
        :type index: QModelIndex
        :return delimiter: Header row number
        :rtype delimiter: Integer
        """
        i = index.sibling(index.row(), DELIMITER)
        delimiter = i.model().data(i, Qt.DisplayRole)
        delimiter = delimiter.split(" ")[0]
        delimiter = delimiter.strip()
        return str(delimiter)


class GeometryTypeColumnDelegate(ListTextColumnDelegate):
    """
    Generic plot import file geometry type column delegate
    """
    def createEditor(self, parent, option, index):
        """
        Reimplementation of generic list column
        QItemDelegate createEditor method
        """
        data_source = index.model().data_source()
        if DelegateRoutine().is_pdf(data_source, index):
            return
        data_source = index.model().data_source()
        self.items = data_source.geometry_options.values()
        return ListTextColumnDelegate.createEditor(self, parent, option, index)


class PlotFileDelegate:
    """
    Plot import file delegate for table view presentation and editing
    """
    def __init__(self, data_service, parent=None):
        self._data_service = data_service
        self._delegate = GenericDelegate(parent)
        self._set_column_delegate()

    def _set_column_delegate(self):
        """
        Sets column delegate based on type
        """
        for pos, column in enumerate(self._data_service.columns):
            if column.type == "list":
                delegate = self._list_text_delegate(pos)
                if delegate:
                    self._delegate.insert_column_delegate(pos, delegate())
            elif pos == HEADER_ROW and column.type == "integer":
                self._delegate.insert_column_delegate(
                    pos, HeaderRowColumnDelegate()
                )
            elif pos == NAME and column.type == "text":
                self._delegate.insert_column_delegate(
                    pos, PlainTextColumnDelegate()
                )

    @staticmethod
    def _list_text_delegate(pos):
        """
        Returns list text column
        delegate based on a column name
        :param pos: Column position in the table view
        :type pos: String
        :return: List text column delegate
        :rtype: QItemDelegate
        """
        delegate = {
            IMPORT_AS: ImportTypeColumnDelegate,
            DELIMITER: DelimiterColumnDelegate,
            GEOM_FIELD: GeometryFieldColumnDelegate,
            GEOM_TYPE: GeometryTypeColumnDelegate
        }
        return delegate.get(pos)

    def delegate(self):
        """
        Returns Plot import file delegate for
        table view presentation and editing
        :return _delegate: Plot import file delegate
        :rtype _delegate: GenericDelegate
        """
        return self._delegate

