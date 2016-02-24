# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : date_property
Description          : Set properties for Date data type
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
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtCore import *
from PyQt4.QtGui import (
		QDialog, 
		QApplication, 
		QMessageBox
		)

from ui_date_property import Ui_DateProperty

class DateProperty(QDialog, Ui_DateProperty):
    def __init__(self, parent, min_val=None, max_val=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self._min_val = min_val
        self._max_val = max_val

        self.initGui()

    def initGui(self):
        min_date = QtCore.QDate(1900, 1, 1)
        today = QtCore.QDate.currentDate()
        self.edtMinDate.setDate(min_date)
        self.edtMaxDate.setDate(today)
        
        if self._min_val:
            self.edtMinDate.setDate(self._min_val)
        if self._max_val:
            self.edtMaxDate.setDate(self._max_val)

        self.edtMinDate.setFocus()
	
    def add_values(self):
        # if its an edit, first remove the previous value
        self._min_val = self.edtMinDate.date()
        self._max_val = self.edtMaxDate.date()

    def min_val(self):
        return self._min_val
	    
    def max_val(self):
        return self._max_val
	    
    def accept(self):
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

