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
    """
    Editor to create/edit ForeignKey column property
    """
    def __init__(self, parent, relation={}):
        """
        :param parent: Owner of the form
        :type parent: QWidget
        :param relation: Dictionary holding fields used to build foreign key column
         *entity_relation - EntityRelation object, if its None then 
         this is a new column else its an edit
         *fk_entities - entities used for ForeignKey selection
         *profile - current profile
         *entity - current entity you are creating column for.
         *column_name - name of the column
        :type form_field: dictionary
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self._entity_relation = relation['form_fields']['entity_relation']
        self.fk_entities = relation['fk_entities']
        self.profile = relation['profile']
        self.entity = relation['entity']
        self.column_name = relation['column_name']
        self.in_db = relation['form_fields']['in_db']

        self.show_in_parent = relation['show_in_parent']
        self.show_in_child = relation['show_in_child']

        self.column_model = QStandardItemModel()
        self.lvDisplayCol.setModel(self.column_model)

        self.init_gui()

    def init_gui(self):
        """
        Initializes form fields
        """
        self.cboPrimaryEntity.currentIndexChanged.connect(
                self.load_entity_columns)

        self.load_fk_entities()
        if self._entity_relation:
            parent = self._entity_relation.parent.short_name
            parent_column = self._entity_relation.parent_column
            display_cols = self._entity_relation.display_cols

            self.cboPrimaryEntity.setCurrentIndex(
                    self.cboPrimaryEntity.findText(parent))

            self.cboPrimaryUKey.setCurrentIndex(
                    self.cboPrimaryUKey.findText(parent_column))

            self.show_display_cols(display_cols)
            self.set_show_in_child()
            self.set_show_in_parent()

        # Disable controls if column exists in the database
        self.cboPrimaryEntity.setEnabled(not self.in_db)
        self.cboPrimaryUKey.setEnabled(not self.in_db)

    def show_display_cols(self, display_cols):
        """
        checks previously selected display columns
        """
        for row in range(self.column_model.rowCount()):
            if unicode(self.column_model.item(row).text()) in display_cols:
                self.column_model.item(row).setCheckState(Qt.Checked)

    def load_fk_entities(self):
        """
        populates combobox with entities to select primary entity for the
        foreign key
        """
        self.cboPrimaryEntity.clear()
        self.cboPrimaryEntity.insertItems(0,
                [name[0] for name in self.fk_entities])

        self.cboPrimaryEntity.setCurrentIndex(0)
	
    def entity_columns(self):
        """
        returns: A list used to select child entity column when building
        a foreign key
        rtype: list
        """
        index = self.cboPrimaryEntity.currentIndex()

        entity_columns = \
                [column for column in self.fk_entities[index][1].columns.items()]

        column_names = [column[0] for column in entity_columns]
        
        return column_names

    def fk_display_columns(self):
        """ 
        returns: A list of columns used to select display columns
        in foreign key
        rtype: list
        """ 
        index = self.cboPrimaryEntity.currentIndex()
        entity_columns = \
                [column for column in self.fk_entities[index][1].columns.items()]

        columns = [column[0] for column in entity_columns \
                if column[1].TYPE_INFO <>'SERIAL']

        return columns

    def load_entity_columns(self):
        """

        """
        columns = self.entity_columns()
        self.populate_column_combobox(columns)

        disp_columns = self.fk_display_columns()
        self.populate_column_listview(disp_columns)

    def set_show_in_parent(self):
        """
        Sets the checkbox value check state based on the configuration default or
        saved configuration value.
        :return:
        :rtype:
        """
        if self.show_in_parent == '0':
            self.show_in_parent_chk.setCheckState(Qt.Unchecked)
        if self.show_in_parent == '1':
            self.show_in_parent_chk.setCheckState(Qt.Checked)
        if self.show_in_parent is None:
            self.show_in_parent_chk.setCheckState(Qt.Unchecked)
        # for old versions, set checked as that is the default
        if self.show_in_parent == '':
            self.show_in_parent_chk.setCheckState(Qt.Checked)

    def set_show_in_child(self):
        """
        Sets the checkbox value check state based on the configuration default or
        saved configuration value.
        :return:
        :rtype:
        """
        if self.show_in_child == '0':
            self.show_in_child_chk.setCheckState(Qt.Unchecked)
        if self.show_in_child == '1':
            self.show_in_child_chk.setCheckState(Qt.Checked)
        if self.show_in_child is None:
            print 'is None'
            self.show_in_child_chk.setCheckState(Qt.Unchecked)
        # for old versions, set checked as that is the default
        if self.show_in_child == '':
            self.show_in_child_chk.setCheckState(Qt.Checked)

    def populate_column_combobox(self, columns):
        """
        Populate combobox with column names
        param columns: List of entity columns to select your primary unique
        column for the foreign key
        type columns: list
        """
        self.cboPrimaryUKey.clear()
        self.cboPrimaryUKey.insertItems(0, columns)

    def populate_column_listview(self, columns):
        """ 
        Populates list view with columns used in selecting 
        display columns for foreign key
        param columns: A list of column names
        type columns: list
        """
        self.column_model.clear()
        for column in columns:
            item = QStandardItem(column)
            item.setCheckable(True)
            self.column_model.appendRow(item)

    def add_values(self):
        """
        Construct an EntityRelation instance from form fields
        """
        er_fields = {}
        er_fields['parent'] = unicode(self.cboPrimaryEntity.currentText())
        er_fields['parent_column'] = unicode(self.cboPrimaryUKey.currentText())
        er_fields['display_columns'] = self.display_columns()
        er_fields['child'] = self.entity
        er_fields['child_column'] = self.column_name
        er_fields['show_in_parent'] = self.show_in_parent()
        er_fields['show_in_child'] = self.show_in_child()

        self._entity_relation = EntityRelation(self.profile, **er_fields)

    def display_columns(self):
        """ 
        Scans StandardItemModel for display columns, and returns a list of
        selected/checked columns for display in foreign key
        rtype: list
        """
        return [unicode(self.column_model.item(row).text()) \
                for row in range(self.column_model.rowCount()) \
                if self.column_model.item(row).checkState()==Qt.Checked]

    def show_in_parent(self):
        """
        Returns show in parent
        :return: Show in parent property - 0 = no and 1 = yes.
        :rtype: Unicode
        """
        if self.show_in_parent_chk.isChecked():
            self.show_in_parent = '1'
        else:
            self.show_in_parent = '0'
            
        return self.show_in_parent

    def show_in_child(self):
        """
        Returns show in child
        :return: Show in child property - 0 = no and 1 = yes.
        :rtype: Unicode
        """
        if self.show_in_child_chk.isChecked():
            self.show_in_child = '1'
        else:
            self.show_in_child = '0'

        return self.show_in_child

    def entity_relation(self):
        """
        returns: entity relation instance
        rtype: EntityRelation
        """
        return self._entity_relation
	    
    def accept(self):
        self.add_values()
        self.done(1)

    def reject(self):
        self.done(0)

