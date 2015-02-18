"""
/***************************************************************************
Name                 : CheckableComboBox
Description          : subclasses QComboboxt to support a multiple section

Date                 : 13/February/2015
copyright            : (C) 2015 by UN-Habitat and implementing partners.
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
from PyQt4.QtGui import *
from PyQt4.QtCore import  *

class MultipleChoiceCombo(QComboBox):
    """Class initialization"""
    def __init__(self, parent):
        super(MultipleChoiceCombo, self).__init__()
        self.view().pressed.connect(self.current_item_state)
        self.setModel(QStandardItemModel(self))
        self._cur_list = []

    def current_item_state(self, index):
        """
        If the current item state is checked,
        set the state to False else set the state to True
        :param index:
        :return:
        """
        current_index = self.model().itemFromIndex(index)
        if current_index.checkState() == Qt.Checked:
            current_index.setCheckState(Qt.Unchecked)
        else:
            current_index.setCheckState(Qt.Checked)

        self.check_items_2list(current_index)

    def check_items_2list(self, item):
        """
        Keep a list of all the selected item
        :return:
        """

        if item.checkState() == Qt.Checked:
            if item.text() in self._cur_list:
                pass
            else:
                self._cur_list.append(item.text())
        if item.checkState() == Qt.Unchecked:
            if item.text() in self._cur_list:
                self._cur_list.remove(item.text())
        return self._cur_list

    def values(self):
        """
        Convert a list to a string,
        convinent menthod for adding selected items to database
        :return:
        """
        string_values =""
        if len(self._cur_list)>0:
            for item in self._cur_list:
                string_values+=item+','
            return string_values[:len(string_values)-1]
        else:
            return None

    def set_values(self, data):
        """
        Get alist and match on the Combobox items,
        if value exist, ensure it is checked
        :param data:
        :return:
        """
        for val in (data.split(',')):
            item = QStandardItem()
            item.setText(val)
            index = self.model().indexFromItem(item)
            if index.data() is not None:
                pass
            else:
                item.setCheckState(Qt.Unchecked)
                self.model().appendRow(item)

class Dialog(QDialog):
    def __init__(self):
        super(Dialog,self).__init__()

        boxLayout = QVBoxLayout()
        self.setLayout(boxLayout)

        self.combo = MultipleChoiceCombo(self)
        self.button = QPushButton(self)
        self.button1 = QPushButton(self)
        self.button1.setText("join")
        self.button.clicked.connect(self.setdataset)
        self.button1.clicked.connect(self.joined)
        for i in range(3):
            self.combo.addItem("added item "+ str(i))
            #self.combo.model().appendRow("added item "+ str(i))
            item = self.combo.model().item(i,0)
            item.setCheckState(Qt.Unchecked)
        #self.combo.setModel(self.model())
        boxLayout.addWidget(self.combo)
        boxLayout.addWidget(self.button)
        boxLayout.addWidget(self.button1)
        self.resize(100,300)

    def setdataset(self):
        list = "solomon, njogu, njoroge"
        self.combo.set_values(list)

    def joined(self):
        listed = self.combo.values()
        QMessageBox.information(None,"Value",str(listed))
