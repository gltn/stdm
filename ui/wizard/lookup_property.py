# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : lookup_property
Description          : Set properties for Lookup data type
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
from PyQt4.QtGui import *
from PyQt4.QtCore import *

#from PyQt4.QtGui import (
		#QDialog, 
		#QApplication, 
		#QMessageBox,
                #QStandardItemModel,
                #QStandardItem
		#)

from ui_lookup_property import Ui_LookupProperty
from stdm.data.configuration.entity_relation import EntityRelation
from create_lookup import LookupEditor

class LookupProperty(QDialog, Ui_LookupProperty):
    def __init__(self, parent, lookup='', profile=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self._lookup = lookup
        self._entity_relation = None
        self._profile = profile

        self.initGui()

    def initGui(self):
        #self.cboPrimaryEntity.currentIndexChanged.connect(self.load_entity_columns)
        self.edtNewlookup.clicked.connect(self.create_lookup)
        lookup_names = self.lookup_entities()
        self.fill_lookup_cbo(lookup_names)
        if self._lookup:
            pass
            # read elements from self._entity_relation and assign widgets

    def create_lookup(self):
        editor = LookupEditor(self, self._profile)
        result = editor.exec_()
        if result == 1:
            names = []
            names.append(editor.lookup.short_name)
            self.cboPrimaryEntity.insertItems(0, names)
            
    def lookup_entities(self):
        names = []
        for entity in self._profile.entities.values():
            if entity.TYPE_INFO not in ['SUPPORTING_DOCUMENT',
                    'ADMINISTRATIVE_SPATIAL_UNIT']:
                if entity.TYPE_INFO == 'VALUE_LIST':
                    names.append(entity.short_name)
        return names

    def fill_lookup_cbo(self, names):
        self.cboPrimaryEntity.clear()
        self.cboPrimaryEntity.insertItems(0, names)
        self.cboPrimaryEntity.setCurrentIndex(0)

    def add_values(self):
        self._lookup = unicode(self.cboPrimaryEntity.currentText())
        self._entity_relation = self.make_entity_relation()

    def make_entity_relation(self):
        er_fields = {}
        er_fields['parent'] = unicode(self.cboPrimaryEntity.currentText())
        er_fields['parent_column'] = None
        er_fields['display_columns'] = []
        er_fields['child'] = None
        er_fields['child_column'] = None
        
        er = EntityRelation(self._profile, **er_fields)
        return er

    def entity_relation(self):
        return self._entity_relation
	    
    def accept(self):
        self.add_values()
        self.done(1)

    def reject(self):
        self.done(0)
    
    def error_message(self, Message):
        # Error Message Box
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("STDM")
        msg.setText(Message)
        msg.exec_()  

