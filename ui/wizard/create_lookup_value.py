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

from stdm.data.configuration.entity import *
from stdm.data.configuration.value_list import (
        ValueList, 
        CodeValue, 
        value_list_factory
        )

class ValueEditor(QDialog, Ui_LookupValue):
    """
    Form to add/edit values added to a lookup. Values are objects of type
    CodeValue
    """
    def __init__(self, parent, lookup, code_value=None):
        """
        :param parent: Owner of this dialog window
        :type parent: QWidget
        :param lookup: A value list object to add the value
        :type lookup: ValueList
        :param code_value: A value object to add to the lookup, if None this is a new
         value, else its an edit.
        :type code_value: CodeValue
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)

	self.lookup = lookup
	self.code_value = code_value

        self.init_gui()

    def init_gui(self):
        """
        initializes the form widgets
        """
	code_regex = QtCore.QRegExp('[A-Z0-9]{1,5}$')
	code_validator = QtGui.QRegExpValidator(code_regex)
	self.edtCode.setValidator(code_validator)
	if self.code_value:
            if self.code_value.updated_value == '':
                self.edtValue.setText(self.code_value.value)
                self.edtCode.setText(self.code_value.code)
            else:
                self.edtValue.setText(self.code_value.updated_value)
                self.edtCode.setText(self.code_value.updated_code)


        val_regex = QtCore.QRegExp('[A-Za-z0-9\s]{1,50}$')
        code_validator = QtGui.QRegExpValidator(val_regex)
        self.edtValue.setValidator(code_validator)
	self.edtValue.setFocus()
	
    def add_value(self):
        """
        Adds a code value to a lookup object. Checks first if a previous value
        exist then removes it and then adds the new one.
        """
        value = unicode(self.edtValue.text())
        code = unicode(self.edtCode.text())
        
        # if its an edit, first remove the previous value
        if self.code_value:
            self.lookup.rename(self.code_value.value, value, code)
        else:
            self.lookup.add_code_value(CodeValue(code, value))
	    
    def accept(self):
        if self.edtValue.text()=='':
                self.error_message(QApplication.translate("ValueEditor", "Please provide a Lookup value."))
                return

        self.add_value()
        
        self.done(1)

    def reject(self):
        self.done(0)
    
    def error_message(self, message):
        """
        Creates a message box and displays a message
        :param message: message to display
        :type message: str
        """
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("STDM")
        msg.setText(message)
        msg.exec_()  
