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
    def __init__(self, parent, form_fields):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self._min_val = form_fields['minimum']
        self._max_val = form_fields['maximum']

        self.initGui()

    def initGui(self):
        validator = QtGui.QDoubleValidator()
        self.edtMinVal.setValidator(validator)
        self.edtMaxVal.setValidator(validator)

        self.edtMinVal.setText(str(self._min_val))
        self.edtMaxVal.setText(str(self._max_val))

        self.edtMinVal.setFocus()
	
    def add_values(self):
        self._min_val = float(self.edtMinVal.text())
        self._max_val = float(self.edtMaxVal.text())

    def min_val(self):
        return self._min_val
	    
    def max_val(self):
        return self._max_val
	    
    def accept(self):
        if self.edtMinVal.text()=='':
            self.error_message(QApplication.translate("DoublePropetyEditor",
                "Please set minimum value"))
            return

        if self.edtMaxVal.text()=='':
            self.error_message(QApplication.translate("DoublePropetyEditor",
                "Pleasei set maximum value."))
            return

        self.add_values()
        self.done(1)

    def reject(self):
        self.done(0)
    
    def error_message(self, Message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("STDM")
        msg.setText(Message)
        msg.exec_()  

