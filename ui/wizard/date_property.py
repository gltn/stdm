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
    """
    Editor to create/edit date column property
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

        self.min_use_current_date = form_fields['min_use_current_date']
        self.max_use_current_date = form_fields['max_use_current_date']

        self.init_gui()

    def init_gui(self):
        """
        Initializes form widgets
        """
        min_date = QtCore.QDate.currentDate()
        today = QtCore.QDate.currentDate()
        self.edtMinDate.setDate(min_date)
        self.edtMaxDate.setDate(today)
        self.edtMinDate.setDate(self._min_val)
        self.edtMaxDate.setDate(self._max_val)

        self.edtMinDate.setFocus()

        self.rbMinFixed.setChecked(True)
        self.rbMaxFixed.setChecked(True)

        self.rbMinFixed.toggled.connect(self.min_fixed_toggle_handler)
        self.rbMaxFixed.toggled.connect(self.max_fixed_toggle_handler)

        self.rbMinCurr.toggled.connect(self.min_curr_toggle_handler)
        self.rbMaxCurr.toggled.connect(self.max_curr_toggle_handler)

        self.rbMinCurr.setChecked(self.min_use_current_date)
        self.rbMaxCurr.setChecked(self.max_use_current_date)

    def min_fixed_toggle_handler(self, checked):
        self.edtMinDate.setEnabled(checked)
	
    def max_fixed_toggle_handler(self, checked):
        self.edtMaxDate.setEnabled(checked)

    def min_curr_toggle_handler(self, checked):
        self.min_use_current_date = checked
	
    def max_curr_toggle_handler(self, checked):
        self.max_use_current_date = checked

    def add_values(self):
        """
        Sets min/max properties with values from form widgets
        """
        self._min_val = self.edtMinDate.date().toPyDate()
        self._max_val = self.edtMaxDate.date().toPyDate()

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
        self.add_values()
        self.done(1)

    def reject(self):
        self.done(0)
    
