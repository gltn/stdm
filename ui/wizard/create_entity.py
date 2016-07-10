# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : create_entity
Description          : Create an entity
Date                 : 20/January/2016
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

from ui_entity import Ui_dlgEntity
from PyQt4.QtCore import *
from PyQt4.QtGui import (
        QDialog, 
	QApplication, 
	QMessageBox
	)

from stdm.data.configuration.entity import *
from stdm.data.configuration.db_items import DbItem

class EntityEditor(QDialog, Ui_dlgEntity):
    """
    Dialog to add and edit entities
    """
    def __init__(self, parent, profile, entity=None, in_db=False):
        """
        :param parent: Owner of this dialog
        :param profile : current profile
        :param entity : current entity
        :param in_db : Boolean flag to check if entity exist in database
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)

	self.profile = profile
	self.form_parent = parent
        self.entity = entity
        self.in_db = in_db

        self.initGui()

    def initGui(self):
        self.edtTable.setFocus()
	self.setTabOrder(self.edtTable, self.edtDesc)
        if self.entity:
            self.edtTable.setText(self.entity.short_name)
            self.edtDesc.setText(self.entity.description)
            self.cbSupportDoc.setCheckState( \
                    self.bool_to_check(self.entity.supports_documents))
        self.edtTable.setEnabled(not self.in_db)
       
    def setLookupTable(self):
        '''def add lookup table'''
        tableName = self.format_table_name(unicode(self.edtTable.text()))
        if str(tableName).startswith("check"):
            self.table = tableName
        if not str(tableName).startswith("check"):
            self.table = 'check_'+tableName
        attrib={}
        tableDesc = str(self.edtDesc.text())
        attrib['name'] = self.table
        attrib['fullname'] = tableDesc
        
    def format_table_name(self, name):
	formatted_name = name.strip()
	formatted_name = formatted_name.replace(' ', "_")
	return formatted_name.lower()
    
    def bool_to_check(self, state):
        """
        Returns a check state given a boolean value
        :param state : Boolean value
        :type state: Boolean
        """
        if state:
            return Qt.Checked
        else:
            return Qt.Unchecked
	    
    def accept(self):
        if self.edtTable.text()=='':
            self.error_message(self.tr("Please enter an entity name"))
            return

        entity_short_name = unicode(self.edtTable.text()).capitalize()

        if self.entity is None:  # New entity
            if self.dup_check(entity_short_name):
                self.error_message(self.tr("Entity with the same name already exist!"))
                return
        else:
            self.profile.remove_entity(self.entity.short_name)

        if self.add_entity(entity_short_name):
            self.done(1)
        else:
            self.done(0)

    def add_entity(self, entity_short_name):
        """
        Creates and adds a new entity to a profile
        :param entity_name: name of the new entity
        :type entity_name: str
        """
        self.entity = self._create_entity(entity_short_name)
        self.profile.add_entity(self.entity)
        return True

    def _create_entity(self, short_name):
        entity = self.profile.create_entity(short_name, entity_factory,
                supports_documents=self.support_doc())
        entity.description = self.edtDesc.text()
        entity.column_added.connect(self.form_parent.add_column_item)
        entity.column_removed.connect(self.form_parent.delete_column_item)
        return entity

    def dup_check(self, name):
        """
        Return True if we have an entity in the current profile with same 'name'
        :param name: entity short_name
        :type name: str
        """
        return self.profile.entities.has_key(name)

    def support_doc(self):
        """
        Return boolean value representing the check state of supporting
        document checkbox
        """
        values = [False, None, True]
        return values[self.cbSupportDoc.checkState()]

    def reject(self):
        self.done(0)
    
    def error_message(self, Message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("STDM")
        msg.setText(Message)
        msg.exec_()  
