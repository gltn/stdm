# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : varchar_property
Description          : Set properties for VarChar data type
Date                 : 02/January/2016
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

from ui_varchar_property import Ui_VarcharProperty
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtCore import *
from PyQt4.QtGui import (
		QDialog, 
		QApplication, 
		QMessageBox
		)

from stdm.data.configuration.entity import *
from stdm.data.configuration.value_list import ValueList, CodeValue, value_list_factory

class VarcharProperty(QDialog, Ui_VarcharProperty):
    def __init__(self, parent, char_len=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self._char_len = char_len

        self.initGui()

    def initGui(self):
        charlen_regex = QtCore.QRegExp('^[0-9]{1,3}$')
        charlen_validator = QtGui.QRegExpValidator(charlen_regex)
        self.edtCharLen.setValidator(charlen_validator)

        if self._char_len:
            self.edtCharLen.setText(self._char_len)
            self.edtCharLen.setFocus()
	
    def add_len(self):
        # if its an edit, first remove the previous value
        self._char_len = self.edtCharLen.text()

    def char_len(self):
        return self._char_len
        
    def accept(self):
        if self.edtCharLen.text()=='':
            self.ErrorInfoMessage(QApplication.translate("VarcharPropetyEditor","Varchar len is not given!"))
            return

        self.add_len()
        self.done(1)

    def reject(self):
        self.done(0)

    def ErrorInfoMessage(self, Message):
        # Error Message Box
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("STDM")
        msg.setText(Message)
        msg.exec_()  
