# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : double_property
Description          : Set properties for Double data type
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

from ui_double_property import Ui_DoubleProperty

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtCore import *
from PyQt4.QtGui import (
		QDialog, 
		QApplication, 
		QMessageBox
		)

class DoubleProperty(QDialog, Ui_DoubleProperty):
    def __init__(self, parent, min_val=None, max_val=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self._min_val = min_val
        self._max_val = max_val

        self.initGui()

    def initGui(self):
        val_regex = QtCore.QRegExp('^[0-9]{1,9}$')
        val_validator = QtGui.QRegExpValidator(val_regex)
        self.edtMinVal.setValidator(val_validator)
        self.edtMaxVal.setValidator(val_validator)

        if self._min_val:
            self.edtMinVal.setText(self._min_val)
        if self._max_val:
            self.edtMaxVal.setText(self._max_val)

        self.edtMinVal.setFocus()
	
    def add_values(self):
        # if its an edit, first remove the previous value
        self._min_val = self.edtMinVal.text()
        self._max_val = self.edtMaxVal.text()

    def min_val(self):
        return self._min_val
	    
    def max_val(self):
        return self._max_val
	    
    def accept(self):
        if self.edtMinVal.text()=='':
            self.ErrorInfoMessage(QApplication.translate("DoublePropetyEditor","Minimum value is not given!"))
            return

        if self.edtMaxVal.text()=='':
            self.ErrorInfoMessage(QApplication.translate("DoublePropetyEditor","Maximum value is not given!"))
            return

        self.add_values()
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

