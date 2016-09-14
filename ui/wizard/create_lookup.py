# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : create_lookup
Description          : Create new lookup entities
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

from ui_lookup_entity import Ui_dlgLookup
from PyQt4 import QtCore
from PyQt4 import QtGui
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

class LookupEditor(QDialog, Ui_dlgLookup):
    """
    Form to add/edit lookup entities.
    """
    def __init__(self, parent, profile, lookup=None):
        """
        :param parent: Owner of this dialog
        :type parent: QWidget
        :param profile: A profile to add/edit lookup
        :type profile: Profile
        :type inplace: Flag to check if lookup creation is initiated from the
                       'normal' lookup creation process -inplace = False,
                       this is the normal state. If 'inplace' = True, then
                       creation is initiated from the the lookup selection dialog
        :param lookup: Value list to create, if None this is a new value list
         else its an edit
        :type lookup: ValueList
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)

	self.profile = profile
	self.lookup  = lookup

        self.init_gui()

    def init_gui(self):
        """
        Initializes form widgets
        """
        name_regex = QtCore.QRegExp('^[a-z][a-z0-9_]*$')
        validator = QtGui.QRegExpValidator(name_regex)
        self.edtName.setValidator(validator)
	self.edtName.setFocus()
        if self.lookup:
            self.edtName.setText(self.lookup.short_name)
	
    def format_lookup_name(self, name):
        """
        Replace spaces with underscore in a name string
        :param name: Name to replace spaces 
        :type name: str
        :rtype: str
        """
        formatted_name = str(name).strip()
        formatted_name = formatted_name.replace(' ', "_")
        return formatted_name.lower()
    
    def create_lookup(self, name):
        """
        Creates a lookup entity and add it to a profile.
        If this is an edit, first the previous lookup is removed before
        adding a new one.
        :param name: Name of the new/edited lookup
        :type name: str
        """
        name = self.format_lookup_name(name)
        new_lookup = self.profile.create_entity(name, value_list_factory)
        return new_lookup
	    
    def accept(self):
        if self.edtName.text()=='':
            self.error_message(QApplication.translate("LookupEditor","Lookup name is not given!"))
            return

        if self.edtName.text() == 'check':
            self.error_message(QApplication.translate("LookupEditor",
                "'check' is used internally by STDM! "
                "Select another name for the lookup"))
            return

        short_name = unicode(self.edtName.text())

        if self.lookup is None:  # new lookup
            if self.duplicate_check(short_name):
                self.show_message(self.tr("Lookup with the same name already exist in the current profile!"))
                return
            else:
                new_lookup = self.create_lookup(short_name)
                self.profile.add_entity(new_lookup)
                self.lookup = new_lookup
        else:
            self.edit_lookup(short_name)

        self.done(1)


    def duplicate_check(self, name):
        """
        Return True if we have an entity in the current profile with same 'name'
        :param name: entity short_name
        :type name: str
        :rtype:boolean
        """
        return self.profile.entities.has_key(name)

    def edit_lookup(self, short_name):
        self.lookup.short_name = short_name

    def reject(self):
        self.done(0)
    
    def error_message(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("STDM")
        msg.setText(message)
        msg.exec_()  
