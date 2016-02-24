# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : create_lookup_value
Description          : Create new lookup values
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

from ui_lookup_value import Ui_LookupValue
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtCore import *
from PyQt4.QtGui import (
		QDialog, 
		QApplication, 
		QMessageBox
		)

#from stdm.data import (
		#writeTable, 
		#renameTable,
		#inheritTableColumn, 
		#writeTableColumn,
		#writeLookup,
		#checktableExist,
		#ConfigTableReader, 
		#table_column_exist
		#)

#from stdm.data.config_utils import setUniversalCode

from stdm.data.configuration.entity import *
from stdm.data.configuration.value_list import ValueList, CodeValue, value_list_factory

class ValueEditor(QDialog, Ui_LookupValue):
    def __init__(self, parent, lookup, code_value=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

	self.lookup = lookup
	self.code_value = code_value

        self.initGui()

    def initGui(self):
	code_regex = QtCore.QRegExp('^[A-Z0-9]{1,5}$')
	code_validator = QtGui.QRegExpValidator(code_regex)
	self.edtCode.setValidator(code_validator)
	if self.code_value:
		self.edtValue.setText(self.code_value.value)
		self.edtCode.setText(self.code_value.code)
	self.edtValue.setFocus()
	
    def add_value(self):
  	    value = unicode(self.edtValue.text())
	    code  = unicode(self.edtCode.text())
	    
	    # if its an edit, first remove the previous value
	    if self.code_value:
		    self.lookup.remove_value(self.code_value.value)

	    self.lookup.add_code_value(CodeValue(code,value))
	    
    def accept(self):
	    if self.edtValue.text()=='':
		    self.ErrorInfoMessage(QApplication.translate("ValueEditor","Lookup value is not given!"))
		    return

	    if self.edtCode.text()=='':
		    self.ErrorInfoMessage(QApplication.translate("ValueEditor","Value code is not given!"))
		    return

            self.add_value()
	    
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
