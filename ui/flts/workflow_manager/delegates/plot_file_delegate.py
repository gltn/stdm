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
    QFileInfo
)
from PyQt4.QtGui import QComboBox
from stdm.ui.flts.workflow_manager.delegates.delegates import (
    GenericDelegate,
    IntegerColumnDelegate,
    ListTextColumnDelegate,
    PlainTextColumnDelegate
)


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
        self.items = data_source.import_as()
        file_extension = self._file_extension(index)
        combobox = QComboBox(parent)
        combobox.addItems(sorted(self.items))
        combobox.setEditable(False)
        if file_extension != "pdf":
            return combobox

        # data_source = index.model().data_source()
        # self.items = data_source.import_as()
        # return ListTextColumnDelegate.createEditor(self, parent, option, index)

    @staticmethod
    def _file_extension(index):
        """
        Returns file extension
        :param index: Model item index
        :type index: QModelIndex
        :return file_extension: QModelIndex
        :rtype file_extension: String
        """
        i = index.sibling(index.row(), 0)
        file_name = i.model().data(i, Qt.DisplayRole)
        file_extension = QFileInfo(file_name).completeSuffix()
        return file_extension


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
                self._import_type_delegate(column.name, i)
            elif column.type == "text":
                self._delegate.insert_column_delegate(
                    i, PlainTextColumnDelegate()
                )

    def _import_type_delegate(self, name, idx):
        """
        Sets import type column delegate
        :param name: Column name
        :type name: String
        :param idx: Column index
        :type idx: Integer
        """
        if name == "Import as":
            self._delegate.insert_column_delegate(
                idx, ImportTypeColumnDelegate()
            )

    def delegate(self):
        """
        Returns Plot import file delegate for
        table view presentation and editing
        :return _delegate: Plot import file delegate
        :rtype _delegate: GenericDelegate
        """
        return self._delegate

