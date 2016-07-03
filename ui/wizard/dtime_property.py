# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : dtime_property
Description          : Set properties for Datetime data type
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

from ui_dtime_property import Ui_DTimeProperty

class DTimeProperty(QDialog, Ui_DTimeProperty):
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

        self.min_use_current_datetime = form_fields['min_use_current_datetime']
        self.max_use_current_datetime = form_fields['max_use_current_datetime']

        self.init_gui()

    def init_gui(self):
        """
        Initializes form widgets
        """
        min_dtime = QtCore.QDateTime.currentDateTime()
        now = QtCore.QDateTime.currentDateTime()
        self.edtMinDTime.setDateTime(min_dtime)
        self.edtMaxDTime.setDateTime(now)
        
        self.edtMinDTime.setDateTime(self._min_val)
        self.edtMaxDTime.setDateTime(self._max_val)

        self.edtMinDTime.setFocus()

        self.rbMinFixed.setChecked(True)
        self.rbMaxFixed.setChecked(True)

        self.rbMinFixed.toggled.connect(self.min_fixed_toggle_handler)
        self.rbMaxFixed.toggled.connect(self.max_fixed_toggle_handler)

        self.rbMinCurr.toggled.connect(self.min_curr_toggle_handler)
        self.rbMaxCurr.toggled.connect(self.max_curr_toggle_handler)

        self.rbMinCurr.setChecked(self.min_use_current_datetime)
        self.rbMaxCurr.setChecked(self.max_use_current_datetime)


    def min_fixed_toggle_handler(self, checked):
        self.edtMinDTime.setEnabled(checked)
	
    def max_fixed_toggle_handler(self, checked):
        self.edtMaxDTime.setEnabled(checked)
	
    def min_curr_toggle_handler(self, checked):
        self.min_use_current_datetime = checked
	
    def max_curr_toggle_handler(self, checked):
        self.max_use_current_datetime = checked

    def add_values(self):
        """
        Sets min/max properties with values from form widgets
        """
        self._min_val = self.edtMinDTime.dateTime().toPyDateTime()
        self._max_val = self.edtMaxDTime.dateTime().toPyDateTime()

    def min_val(self):
        """
        Returns minimum datetime property
        :rtype: QDateTime 
        """
        return self._min_val
	    
    def max_val(self):
        """
        Returns maximum datetime property
        :rtype: QDateTime 
        """
        return self._max_val
	    
    def accept(self):
        self.add_values()
        self.done(1)

    def reject(self):
        self.done(0)
    
