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


class DelegateRoutine:
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
        file_name = self._file_name(index)
        if data_source.is_pdf(file_name):
            return True

    @staticmethod
    def _file_name(index):
        """
        Returns file name
        :param index: Model item index
        :type index: QModelIndex
        :return file_name: File name
        :rtype file_name: String
        """
        i = index.sibling(index.row(), 0)
        file_name = i.model().data(i, Qt.DisplayRole)
        return file_name


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
        combobox.setEditable(False)
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
        self.items = self._delimiter_name(data_source)
        regex = QRegExp(r"^[\w\W]{1}$")
        validator = QRegExpValidator(regex, parent)
        combobox = QComboBox(parent)
        combobox.addItems(sorted(self.items))
        combobox.setEditable(True)
        combobox.setValidator(validator)
        return combobox

    def _delimiter_name(self, data_source):
        """
        Returns delimiters full name
        :param data_source: Plot file object
        :type data_source: PlotFile
        :return names: Delimiters full name
        :return names: String
        """
        names = []
        delimiters = data_source.delimiters
        for k, d in sorted(delimiters.items()):
            delimiter = "{0} {1}".format(d, k)
            if k != "\t":
                names.append(delimiter)
            else:
                names.append(d)
        return names

    def setModelData(self, editor, model, index):
        """
        Reimplementation of generic list column
        QItemDelegate setModelData method
        """
        value = editor.currentText()
        if value not in self.items:
            value = "Custom {}".format(value)
        model.setData(index, value)


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
        file_path = data_source.file_path
        row_count = data_source.row_count(file_path)
        if row_count:
            self.minimum = 1
            self.maximum = row_count
        return IntegerColumnDelegate.createEditor(self, parent, option, index)


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
        for i, column in enumerate(self._data_service.columns):
            if column.type == "list":
                delegate = self._list_text_delegate(column.name)
                if delegate:
                    self._delegate.insert_column_delegate(i, delegate())
            elif column.name == "Header row" and column.type == "integer":
                self._delegate.insert_column_delegate(
                    i, HeaderRowColumnDelegate()
                )
            elif column.name == "Name" and column.type == "text":
                self._delegate.insert_column_delegate(
                    i, PlainTextColumnDelegate()
                )

    @staticmethod
    def _list_text_delegate(name):
        """
        Returns list text column
        delegate based on a column name
        :param name: Column name
        :type name: String
        :return: List text column delegate
        :rtype: QItemDelegate
        """
        delegate = {
            "Import as": ImportTypeColumnDelegate,
            "Delimiter": DelimiterColumnDelegate
        }
        return delegate.get(name)

    def delegate(self):
        """
        Returns Plot import file delegate for
        table view presentation and editing
        :return _delegate: Plot import file delegate
        :rtype _delegate: GenericDelegate
        """
        return self._delegate

