"""
/***************************************************************************
Name                 : EntityAttributesEditor
Description          : Dialog for editing an entity's attributes.
Date                 : 13/July/2017
copyright            : (C) 2017 by UN-Habitat and implementing partners.
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
from collections import OrderedDict
from PyQt4.QtGui import (
    QDialog,
    QDialogButtonBox,
    QMessageBox
)

from stdm.data.configuration.entity import Entity
from stdm.ui.notification import NotificationBar
from stdm.ui.wizard.column_editor import ColumnEditor
from stdm.ui.wizard.ui_entity_attributes_editor import Ui_EntityAttributesEditor


class TenureCustomAttributesEditor(QDialog, Ui_EntityAttributesEditor):
    """
    Dialog for editing an entity's attributes.
    """
    def __init__(
            self,
            profile,
            tenure_custom_entities,
            parent=None,
            editable=True,
            exclude_columns=None
    ):
        """
        Class constructor.
        :param profile: Profile object.
        :type profile: Profile
        :param tenure_custom_entities: Collection of tenure types and 
        corresponding custom attribute entities.
        :type tenure_custom_entities: OrderedDict
        :param proxy_name: Name of the entity which will be used to create 
        a proxy table.The attributes of the entity can then be copied to the 
        target entity which shares the same name as the proxy entity.
        :type proxy_name: str
        :param parent: Parent object.
        :type parent: QWidget
        :param editable: True if the attributes can be edited, otherwise 
        False.
        :type editable: bool
        :param exclude_columns: List of column names to exclude.
        :type exclude_columns: list
        """
        super(TenureCustomAttributesEditor, self).__init__(parent)
        self.setupUi(self)

        self._notifBar = NotificationBar(self.vlNotification)

        self._profile = profile
        self._exclude_names = exclude_columns
        if self._exclude_names is None:
            self._exclude_names = []

        # Attributes for each tenure type
        # Tenure type: list of attributes
        self._tenure_custom_entities = tenure_custom_entities

        # Populate attributes minus excluded columns
        self._tenure_custom_attrs = {}
        for tt, custom_ent in self._tenure_custom_entities.iteritems():
            attrs = custom_ent.columns.values()
            self._tenure_custom_attrs[tt] = [
                a for a in attrs if a.name not in self._exclude_names
            ]

        # Column types to omit
        self._exc_cols = [
            'GEOMETRY',
            'FOREIGN_KEY'
        ]

        # Connect signals
        self.btnAddColumn.clicked.connect(self.on_new_column)
        self.btnEditColumn.clicked.connect(self.on_edit_column)
        self.btnDeleteColumn.clicked.connect(self.on_delete_column)

        if not editable:
            self._disable_editing()

        # Update excluded columns
        self._update_excluded_columns()

        # Load tenure types
        self._load_tenure_types()

        # Connect tenure type signal
        self.cbo_tenure_type.currentIndexChanged.connect(
            self._on_tenure_type_changed
        )

        # Load attributes for current tenure type
        if self.cbo_tenure_type.count() > 0:
            c_tenure_type = self.cbo_tenure_type.currentText()
            self._tenure_custom_attrs_entity(c_tenure_type)

    @property
    def custom_tenure_attributes(self):
        """
        :return: Returns a collection containing the attributes for each 
        entity corresponding to the tenure types. Key is tenure type lookup 
        name, value is a list of tenure attributes.
        :rtype: dict(str, list)
        """
        return self._tenure_custom_attrs

    def exclude_column_names(self, names):
        """
        Set the list of columns to be excluded from the view only, not from 
        the collection.
        :param names: List containing column names that will be excluded 
        from the view. If there are already existing columns in the view 
        which are also in the list of excluded columns then they will be 
        removed from the view but reference will remain in the collection.
        :type names: list
        """
        self._exclude_names = names

    def _load_tenure_types(self):
        # Load tenure types
        t_types = self._tenure_custom_attrs.keys()

        if len(t_types) > 0:
            self.cbo_tenure_type.clear()

        for t_name in t_types:
            self.cbo_tenure_type.addItem(t_name)

    def _on_tenure_type_changed(self, idx):
        # Slot raised when the index of the tenure type combo changes
        if idx == -1:
            return

        t_type = self.cbo_tenure_type.itemText(idx)
        if t_type:
            self._tenure_custom_attrs_entity(t_type)

    def _tenure_custom_attrs_entity(self, tenure_type):
        # Loads the custom attributes entity. Creates if it does not exist.
        c_ent_attrs = self._tenure_custom_attrs.get(tenure_type, None)
        if c_ent_attrs is None:
            QMessageBox.critical(
                self,
                self.tr('Custom Tenure Attributes'),
                self.tr('Attributes entity is not available.')
            )

            return

        self.load_attributes(c_ent_attrs)

    def _update_excluded_columns(self):
        # Remove excluded columns.
        for n in self._exclude_names:
            self.tb_view.remove_item(n)

    def _get_current_entity(self):
        # Returns the custom attributes entity corresponding to the
        # currently selected tenure type.
        tenure_type = self.cbo_tenure_type.currentText()

        return self._tenure_custom_entities.get(tenure_type, None)

    def _get_attribute(self, tenure_type, name):
        # Get attribute by name and index otherwise None.
        attr, idx = None, -1
        attrs = self._tenure_custom_attrs.get(tenure_type, None)
        if attrs is None:
            return attr, idx

        for i, a in enumerate(attrs):
            if a.name == name:
                attr = a
                idx = i

                break

        return attr, idx

    def _disable_editing(self):
        # Disable editing
        self.btnAddColumn.setEnabled(False)
        self.btnEditColumn.setEnabled(False)
        self.btnDeleteColumn.setEnabled(False)
        self.tb_view.setEnabled(False)
        ok_btn = self.buttonBox.button(QDialogButtonBox.Ok)
        ok_btn.setEnabled(False)

    def _column_editor_params(self):
        # Constructor params for column editor
        params = {}
        params['parent'] = self
        params['entity'] = self._get_current_entity()
        params['profile'] = self._profile

        return params

    def _on_column_added(self, column):
        # Slot raised when a new column has been added to the entity.
        if self._validate_excluded_column(column.name):
            self.add_column(column)

    def _get_tenure_type_attrs(self, tenure_type):
        # Returns a list of attributes matching to the given tenure type.
        # Creates an empty list if None is found.
        if not tenure_type in self._tenure_custom_attrs:
            self._tenure_custom_attrs[tenure_type] = []

        return self._tenure_custom_attrs[tenure_type]

    def add_column(self, column):
        """
        Adds a new column to the view.
        :param tenure_type: Name of tenure type lookup.
        :type tenure_type: str
        :param column: Column object.
        :type column: BaseColumn
        """
        tenure_type = self.cbo_tenure_type.currentText()

        attrs = self._get_tenure_type_attrs(tenure_type)

        # Check if the column is already in the list
        attr, idx = self._get_attribute(tenure_type, column.name)
        if idx == -1:
            attrs.append(column)

        self.tb_view.add_item(column)

    def edit_column(self, original_name, column):
        """
        Updates the edited column in the view.
        :param original_name: Original name of the column.
        :type original_name: str
        :param column: Column object.
        :type column: BaseColumn
        :return: Returns True if the operation succeeded, otherwise False 
        if the column does not exist.
        :rtype: bool
        """
        tenure_type = self.cbo_tenure_type.currentText()

        col, idx = self._get_attribute(tenure_type, original_name)
        if idx == -1:
            return False

        attrs = self._get_tenure_type_attrs(tenure_type)
        col = attrs.pop(idx)
        attrs.insert(idx, column)

        self.tb_view.update_item(original_name, column)

    def on_new_column(self):
        """
        Slot for showing New column dialog.
        """
        editor_params = self._column_editor_params()
        editor_params['is_new'] = True

        editor = ColumnEditor(**editor_params)
        editor.exclude_column_types(self._exc_cols)
        editor_title = self.tr('Create New Column')
        editor.setWindowTitle(editor_title)

        if editor.exec_() == QDialog.Accepted:
            # Do nothing since we are connecting to the signal
            self.add_column(editor.column)

    def selected_column(self):
        """
        :return: Returns the selected column object in the view otherwise 
        None if there is no row selected.
        :rtype: BaseColumn
        """
        tenure_type = self.cbo_tenure_type.currentText()

        sel_col_name = self.tb_view.selected_column()
        if not sel_col_name:
            return None

        col, idx = self._get_attribute(tenure_type, sel_col_name)
        if idx == -1:
            return None

        return col

    def on_edit_column(self):
        """
        Slot for showing a dialog for editing the selected column.
        """
        self._notifBar.clear()

        sel_col = self.selected_column()
        if sel_col is None:
            msg = self.tr('Please select a column to edit.')
            self._notifBar.insertWarningNotification(msg)

            return

        original_name = sel_col.name

        editor_params = self._column_editor_params()
        editor_params['column'] = sel_col
        editor_params['is_new'] = False

        editor = ColumnEditor(**editor_params)
        editor.exclude_column_types(self._exc_cols)
        editor_title = self.tr('Edit Column')
        editor.setWindowTitle(editor_title)

        if editor.exec_() == QDialog.Accepted:
            if self._validate_excluded_column(editor.column.name):
                self.edit_column(original_name, editor.column)

    def _validate_excluded_column(self, name):
        # Check name against list of excluded names
        if name in self._exclude_names:
            msg = self.tr(
                'column has been defined as an excluded column, it will not '
                'be added.'
            )
            msg = '\'{0}\' {1}'.format(name, msg)
            QMessageBox.critical(self, self.tr('Excluded column'), msg)

            return False

        return True

    def on_delete_column(self):
        """
        Slot for deleting the selected column.
        """
        sel_col = self.selected_column()
        if sel_col is None:
            self._notifBar.clear()
            msg = self.tr('Please select a column to delete.')
            self._notifBar.insertWarningNotification(msg)

            return

        msg = self.tr(
            'Are you sure you want to permanently delete the attribute?'
        )
        result = QMessageBox.warning(
            self,
            self.tr('Delete Attribute'),
            msg,
            QMessageBox.Yes | QMessageBox.No
        )

        if result == QMessageBox.Yes:
            self.delete_column(sel_col.name)

    def delete_column(self, name):
        """
        Removes the column with the given name from the view.
        :param name: Column name.
        :type name: str
        :return: Return True if the column was successfully deleted, 
        otherwise False if the column does not exist.
        :rtype: bool
        """
        tenure_type = self.cbo_tenure_type.currentText()
        attr, idx = self._get_attribute(tenure_type, name)
        if idx == -1:
            return False

        attrs = self._get_tenure_type_attrs(tenure_type)
        col = attrs.pop(idx)

        return self.tb_view.remove_item(attr.name)

    def load_attributes_from_entity(self, entity):
        """
        Loads the view with the attributes of the specified entity. Any 
        previous attributes will be removed.
        :param entity: Entity whose attributes will be loaded.
        :type entity: Entity
        """
        self.load_attributes(entity.columns)

    def load_attributes(self, attributes):
        """
        Loads the collection of attibutes to the view. Any previous 
        attributes will be removed. The collection should not be empty.
        :param attributes: Collection of attributes to be loaded to te view.
        :type attributes: OrderedDict
        """
        # Clear view
        self.tb_view.clear_view()

        if len(attributes) > 0:
            for a in attributes:
                self.add_column(a)

            # Refresh excluded columns
            self._update_excluded_columns()