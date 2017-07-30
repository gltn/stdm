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


class EntityAttributesEditor(QDialog, Ui_EntityAttributesEditor):
    """
    Dialog for editing an entity's attributes.
    """
    def __init__(
            self,
            profile,
            proxy_name,
            parent=None,
            editable=True,
            exclude_columns=None
    ):
        """
        Class constructor.
        :param profile: Profile object.
        :type profile: Profile
        :param proxy_name: Name of the entity which will be used to create 
        a proxy table.The attributes of the entity can then be copied to the 
        target entity which shares the same name as the proxy entity.
        :type proxy_name: str
        :param parent: Parent object.
        :type parent: QWidget
        :param editable: True if the attributes can be edited, otherwise 
        False.
        :param exclude_columns: List of column names to exclude.
        :type exclude_columns: list
        """
        super(EntityAttributesEditor, self).__init__(parent)
        self.setupUi(self)

        self._notifBar = NotificationBar(self.vlNotification)

        self._profile = profile
        self._entity = Entity(proxy_name, self._profile)
        self._attrs = []
        self._exclude_names = exclude_columns
        if self._exclude_names is None:
            self._exclude_names = []

        # Column types to omit
        self._exc_cols = [
            'GEOMETRY',
            'FOREIGN_KEY'
        ]

        # Connect signals
        self.btnAddColumn.clicked.connect(self.on_new_column)
        self.btnEditColumn.clicked.connect(self.on_edit_column)
        self.btnDeleteColumn.clicked.connect(self.on_delete_column)
        self._entity.column_added.connect(
            self._on_column_added
        )

        # Update view with entity attributes
        self.load_attributes_from_entity(self._entity)

        if not editable:
            self._disable_editing()

        # Update excluded columns
        self._update_excluded_column()

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

    def _update_excluded_column(self):
        # Remove excluded columns.
        for n in self._exclude_names:
            self.tb_view.remove_item(n)

    def _get_attribute(self, name):
        # Get attribute by name and index otherwise None.
        attr, idx = None, -1
        for i, a in enumerate(self._attrs):
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
        params['entity'] = self._entity
        params['profile'] = self._profile

        return params

    def _on_column_added(self, column):
        # Slot raised when a new column has been added to the entity.
        if self._validate_excluded_column(column.name):
            self.add_column(column)

    def add_column(self, column):
        """
        Adds a new column to the view.
        :param column: Column object.
        :type column: BaseColumn
        """
        self._attrs.append(column)
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
        col, idx = self._get_attribute(original_name)
        if idx == -1:
            return False

        col = self._attrs.pop(idx)
        self._attrs.insert(idx, column)

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
            pass

    def selected_column(self):
        """
        :return: Returns the selected column object in the view otherwise 
        None if there is no row selected.
        :rtype: BaseColumn
        """
        sel_col_name = self.tb_view.selected_column()
        if not sel_col_name:
            return None

        col, idx = self._get_attribute(sel_col_name)
        print idx
        if idx == -1:
            return None

        return col

    def on_edit_column(self):
        """
        Slot for showing a dialog for editing the selected column.
        """
        sel_col = self.selected_column()
        if sel_col is None:
            self._notifBar.clear()
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
        :rtype: False
        """
        name, idx = self._get_attribute(name)
        if idx == -1:
            return False

        col = self._attrs.pop(idx)

        return self.tb_view.remove_item(name)

    @property
    def attributes(self):
        """
        :return: Returns a collection of attributes specified in the view.
        :rtype: OrderedDict(name, BaseColumn)
        """
        attrs = OrderedDict()

        for a in self._attrs:
            attrs[a.name] = a

        return attrs

    def load_attributes_from_entity(self, entity):
        """
        Loads the view with the attributes of the specified entity. Any 
        previous attributes will be removed.
        :param entity: Entity whose attributes will be loaded.
        :type entity: Entity
        """
        self.load_attributes(entity.columns)

    def clear(self):
        """
        Removes all columns from the view.
        """
        for a in self._attrs:
            self.delete_column(a.name)

    def load_attributes(self, attributes):
        """
        Loads the collection of attibutes to the view. Any previous 
        attributes will be removed. The collection should not be empty.
        :param attributes: Collection of attributes to be loaded to te view.
        :type attributes: OrderedDict
        """
        if len(attributes) > 0:
            # Clear view
            self.clear()

            for a in attributes.values():
                self.add_column(a)