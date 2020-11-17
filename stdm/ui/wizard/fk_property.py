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
from qgis.PyQt import uic
from qgis.PyQt.QtCore import (
    Qt
)
from qgis.PyQt.QtGui import (
    QStandardItem,
    QStandardItemModel
)
from qgis.PyQt.QtWidgets import (
    QDialog
)

from stdm.data.configuration.entity_relation import EntityRelation
from stdm.ui.gui_utils import GuiUtils

WIDGET, BASE = uic.loadUiType(
    GuiUtils.get_ui_file_path('wizard/ui_fk_property.ui'))


class FKProperty(WIDGET, BASE):
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
        self._show_in_parent = relation['show_in_parent']
        self._show_in_child = relation['show_in_child']
        self.column_model = QStandardItemModel()
        self.lvDisplayCol.setModel(self.column_model)

        self.init_gui()

    def init_gui(self):
        """
        Initializes form fields
        """
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

        # Disable controls if column exists in the database
        self.cboPrimaryEntity.setEnabled(not self.in_db)
        self.cboPrimaryUKey.setEnabled(not self.in_db)
        self.lvDisplayCol.setEnabled(not self.in_db)

        self.show_in_parent_chk.clicked.connect(self.on_show_in_parent_clicked)
        self.show_in_child_chk.clicked.connect(self.on_show_in_child_clicked)

    def on_show_in_parent_clicked(self):
        """
        A slot raised when show in parent is clicked.
        :return:
        :rtype:
        """
        if self.show_in_parent_chk.isChecked():
            self.show_in_child_chk.setChecked(False)
            self._show_in_parent = True

    def on_show_in_child_clicked(self):
        """
        A slot raised when show in child is clicked.
        :return:
        :rtype:
        """
        if self.show_in_child_chk.isChecked():
            self.show_in_parent_chk.setChecked(False)
            self._show_in_child = True

    def show_in_parent(self):
        """
        Returns show in parent.
        :return: Returns show in parent.
        :rtype: Boolean
        """
        return self._show_in_parent

    def show_in_child(self):
        """
        Returns show in child.
        :return: Returns show in child.
        :rtype: Boolean
        """
        return self._show_in_child

    def show_display_cols(self, display_cols):
        """
        checks previously selected display columns
        """
        for row in range(self.column_model.rowCount()):
            if str(self.column_model.item(row).text()) in display_cols:
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
                   if column[1].TYPE_INFO != 'SERIAL']

        return columns

    def load_entity_columns(self):
        """

        """
        columns = self.entity_columns()
        self.populate_column_combobox(columns)

        disp_columns = self.fk_display_columns()
        self.populate_column_listview(disp_columns)

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
        er_fields['parent'] = str(self.cboPrimaryEntity.currentText())
        er_fields['parent_column'] = str(self.cboPrimaryUKey.currentText())
        er_fields['display_columns'] = self.display_columns()
        er_fields['child'] = self.entity
        er_fields['child_column'] = self.column_name

        self._entity_relation = EntityRelation(self.profile, **er_fields)

    def display_columns(self):
        """
        Scans StandardItemModel for display columns, and returns a list of
        selected/checked columns for display in foreign key
        rtype: list
        """
        return [str(self.column_model.item(row).text()) \
                for row in range(self.column_model.rowCount()) \
                if self.column_model.item(row).checkState() == Qt.Checked]

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
