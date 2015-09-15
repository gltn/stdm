# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name:                  table_propertyDlg
Description           : Table proprty dialog
                             -------------------
begin                : 2014-03-04
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
import collections

from PyQt4.QtGui import QDialog, QComboBox, QApplication, QMessageBox
from PyQt4.QtCore import QObject, SIGNAL, Qt
from stdm.data import actions,  writeTableColumn, ConfigTableReader, \
    setCollectiontypes
from ui_table_property import Ui_TableProperty
from data.config_utils import tableCols, UserData, formatColumnName


class TableProperty(QDialog, Ui_TableProperty):

    def __init__(self, usrProf, tableName, parent):
        QDialog.__init__(self, parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self._table_name = tableName
        self._user_profile = usrProf
        self.table_handler = ConfigTableReader()
        self.initControls()

        QObject.connect(self.cboTable, SIGNAL(
            "currentIndexChanged(int)"), self.relation_columns)
        # QObject.connect(
        # self.listView,SIGNAL('clicked(QModelIndex)'),self.selectedIndex)

    def initControls(self):
        """Initialize defualt dialog properties"""
        self.table_list(self.cboTable)
        setCollectiontypes(actions, self.cboDelAct)
        setCollectiontypes(actions, self.cboUpAct)
        self.table_column_model(self.cboColumn, self.cboTable.currentText())
        self.table_column_model(self.cboRefCol, self._table_name)
        self.table_column_model(self.cboType, self.cboTable.currentText())

    def table_list(self, combo_box):
        model = self.table_handler.table_list_model(self._user_profile)
        combo_box.setModel(model)
        index = combo_box.findText(self._table_name, Qt.MatchExactly)
        if index is not -1:
            combo_box.setCurrentIndex(index - 1)

    def table_column_model(self, combo, table_name):
        """
        Return a list of column as QAbstractListModel
        :param combo:
        :param table_name:
        :return:
        """
        col_list = tableCols(table_name)
        col_model = self.table_handler.column_labels(col_list)
        combo.setModel(col_model)

    def set_collection_types(self, collection_type, combo):
        """
        Method to read defult  to a sql relations and constraint type to
        combo box
        :param collection_type:
        :param combo:
        """
        ord_dict = collections.OrderedDict(collection_type)
        combo.clear()
        for k, v in ord_dict.iteritems():
            combo.addItem(k, v)
            combo.setInsertPolicy(QComboBox.InsertAlphabetically)
        combo.setMaxVisibleItems(len(collection_type))

    def relation_columns(self):
        """update columns set for the selected table"""
        referenceTable = self.cboTable.currentText()
        self.table_column_model(self.cboColumn, referenceTable)
        self.table_column_model(self.cboType, referenceTable)

    def local_columns(self):
        """update columns set for the selected table"""
        self.table_column_model(self.cboRefCol, self._table_name)

    def selected_data(self, combo_box):
        """
        Get the user data from the combo box display item
        :param combo_box:
        :return:
        """
        text = combo_box.currentText()
        index = combo_box.findText(text, Qt.MatchExactly)
        if index is not -1:
            user_data = combo_box.itemData(int(index))
            return user_data

    def set_table_relation(self):
        """add new relation to the table in the config file"""
        del_act = UserData(self.cboDelAct)
        update_act = UserData(self.cboUpAct)
        attrib_dict = {}
        attrib_dict['name'] = formatColumnName(self.txtName.text())
        attrib_dict['table'] = self.cboTable.currentText()
        attrib_dict['fk'] = self.cboRefCol.currentText()
        attrib_dict['column'] = self.cboColumn.currentText()
        attrib_dict['display_name'] = self.cboType.currentText()
        attrib_dict['ondelete'] = del_act
        attrib_dict['onupdate'] = update_act
        writeTableColumn(attrib_dict, self._user_profile,
                         'table', self._table_name, 'relations')

    def accept(self):
        if self.txtName.text() == '':
            self.error_info_message(QApplication.translate(
                "TableProperty", "Relation Name is not given"))
            return
        if self.cboTable.currentText() == "":
            self.error_info_message(QApplication.translate(
                "TableProperty", "Referenced Table is not selected"))
            return
        if self.cboTable.currentText() == self._table_name:
            self.error_info_message(QApplication.translate(
                "TableProperty", "Table cannot draw a reference from itself"))
            return
        self.set_table_relation()
        self.close()

    def error_info_message(self, message):
        """
        Error Message Box
        :param message:
        """
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(QApplication.translate("AttributeEditor", "STDM"))
        msg.setText(message)
        msg.exec_()
