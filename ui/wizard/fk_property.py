# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : fk_property
Description          : Set properties for ForeignKey data type
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

from ui_fk_property import Ui_FKProperty
from stdm.data.configuration.entity_relation import EntityRelation

class FKProperty(QDialog, Ui_FKProperty):
    def __init__(self, parent, relation={}):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self._entity_relation = relation['entity_relation']
        self.fk_entities = relation['fk_entities']
        self.profile = relation['profile']
        self.entity = relation['entity']
        self.column_name = relation['column_name']

        self.column_model = QStandardItemModel()
        self.lvDisplayCol.setModel(self.column_model)

        self.initGui()

    def initGui(self):
        self.cboPrimaryEntity.currentIndexChanged.connect( \
                self.load_entity_columns)

        self.load_fk_entities()
        if self._entity_relation:
            parent = self._entity_relation.parent.short_name
            parent_column = self._entity_relation.parent_column
            display_cols = self._entity_relation.display_cols

            self.cboPrimaryEntity.setCurrentIndex( \
                    self.cboPrimaryEntity.findText(parent))

            self.cboPrimaryUKey.setCurrentIndex( \
                    self.cboPrimaryUKey.findText(parent_column))

            self.show_display_cols(display_cols)
            

    def show_display_cols(self, display_cols):
        '''
        checks previously selected display columns
        '''
        for row in range(self.column_model.rowCount()):
            if unicode(self.column_model.item(row).text()) in display_cols:
                self.column_model.item(row).setCheckState(Qt.Checked)

    def load_fk_entities(self):
        '''
        populates combobox with entities to select primary entity for the
        foreign key
        '''
        self.cboPrimaryEntity.clear()
        self.cboPrimaryEntity.insertItems(0,
                [name[0] for name in self.fk_entities])

        self.cboPrimaryEntity.setCurrentIndex(0)
	
    def entity_columns(self):
        '''
        returns list used to select child entity column when building
        a foreign key
        rtype: list
        '''
        index = self.cboPrimaryEntity.currentIndex()

        entity_columns = \
                [column for column in self.fk_entities[index][1].columns.items()]

        column_names = [column[0] for column in entity_columns]
        
        return column_names

    def fk_display_columns(self):
        '''
        returns a list of columns used to select display columns
        in foreign key
        rtype: list
        '''
        index = self.cboPrimaryEntity.currentIndex()
        entity_columns = \
                [column for column in self.fk_entities[index][1].columns.items()]

        columns = [column[0] for column in entity_columns \
                if column[1].TYPE_INFO <>'SERIAL']

        return columns

    def load_entity_columns(self):
        columns = self.entity_columns()
        self.populate_column_combobox(columns)

        disp_columns = self.fk_display_columns()
        self.populate_column_listview(disp_columns)

    def populate_column_combobox(self, columns):
        self.cboPrimaryUKey.clear()
        self.cboPrimaryUKey.insertItems(0, columns)

    def populate_column_listview(self, columns):
        '''
        Populates list view with columns used in selecting 
        display columns for foreign key

        '''
        self.column_model.clear()
        for column in columns:
            item = QStandardItem(column)
            item.setCheckable(True)
            self.column_model.appendRow(item)

    def add_values(self):
        self._entity_relation = self.make_entity_relation()

    def display_columns(self):
        '''
        returns a list of selected/checked columns for display in 
        foreign key
        rtype: list
        '''
        return [unicode(self.column_model.item(row).text()) \
                for row in range(self.column_model.rowCount()) \
                if self.column_model.item(row).checkState()==Qt.Checked]

    def make_entity_relation(self):
        '''
        returns a fully constructed EntityRelation column
        rtype: EntityRelation
        '''
        er_fields = {}
        er_fields['parent'] = unicode(self.cboPrimaryEntity.currentText())
        er_fields['parent_column'] = unicode(self.cboPrimaryUKey.currentText())
        er_fields['display_columns'] = self.display_columns()
        er_fields['child'] = self.entity
        er_fields['child_column'] = self.column_name

        er = EntityRelation(self.profile, **er_fields)
        return er

    def entity_relation(self):
        return self._entity_relation
	    
    def accept(self):
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

