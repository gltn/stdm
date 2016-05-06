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
    """
    Editor to create/edit Double column property
    """
    def __init__(self, parent, form_fields):
        """
        :param parent: Owner of the form
        :type parent: QWidget
        :param form_fields: Contains data from the column editor window
        :type form_field: dictionary
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self._min_val = form_fields['minimum']
        self._max_val = form_fields['maximum']

        self.init_gui()

    def init_gui(self):
        """
        Initializes form widgets
        """
        validator = QtGui.QDoubleValidator()
        self.edtMinVal.setValidator(validator)
        self.edtMaxVal.setValidator(validator)

        self.edtMinVal.setText(str(self._min_val))
        self.edtMaxVal.setText(str(self._max_val))

        self.edtMinVal.setFocus()
	
    def add_values(self):
        """
        Sets min/max properties with values from form widgets
        """
        self._min_val = float(self.edtMinVal.text())
        self._max_val = float(self.edtMaxVal.text())

    def min_val(self):
        """
        Returns minimum property
        :rtype: int
        """
        return self._min_val
	    
    def max_val(self):
        """
        Returns maximum property
        :rtype: int
        """
        return self._max_val
	    
    def accept(self):
        if self.edtMinVal.text()=='':
            self.show_message(QApplication.translate("DoublePropetyEditor",
                "Please set minimum value"))
            return

        if self.edtMaxVal.text()=='':
            self.show_message(QApplication.translate("DoublePropetyEditor",
                "Pleasei set maximum value."))
            return

        self.add_values()
        self.done(1)

    def reject(self):
        self.done(0)

    def show_message(self, message, msg_icon=QMessageBox.Critical):
        msg = QMessageBox(self)
        msg.setIcon(msg_icon)
        msg.setWindowTitle(QApplication.translate("STDM Configuration Wizard","STDM"))
        msg.setText(QApplication.translate("STDM Configuration Wizard",message))
        msg.exec_()
