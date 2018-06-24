# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : code_property
Description          : Set properties for Lookup data type
Date                 : 09/February/2017
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
from PyQt4.QtCore import Qt
from collections import OrderedDict

from PyQt4.QtGui import QApplication, QFontMetrics, QDialog, QListWidgetItem, \
    QStandardItem, QStandardItemModel, QComboBox, QHeaderView
from stdm.utils.util import (
    enable_drag_sort,
    code_columns,
    string_to_boolean
)
from stdm.ui.customcontrols.generic_delegate import GenericDelegate
from ui_code_property import Ui_CodeProperty

class CodeProperty(QDialog, Ui_CodeProperty):
    """
    Editor to create/edit Lookup column property
    """

    def __init__(self, parent, form_fields, entity, profile=None):
        """
        :param parent: Owner of this form
        :type parent: QWidget
        :param form_fields: form field dictionary containing values from
        the configuration file if it exists.
        :type form_fields: Dictionary
        :param entity: The entity of the current column
        :type entity: Entity
        :param profile: Current configuration profile
        :type profile: Profile
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)

        # self.in_db = form_fields['in_db']
        self._source = form_fields['prefix_source']
        self._columns = form_fields['columns']

        self._leading_zero = form_fields['leading_zero']
        self._separator = form_fields['separator']
        self._hide_prefix =  string_to_boolean(form_fields['hide_prefix'], False)
        self._parent_column_name = form_fields['colname']
        self._disable_auto_increment = string_to_boolean(
            form_fields['disable_auto_increment'], False)

        self._enable_editing = string_to_boolean(
            form_fields['enable_editing'], False
        )
        self._column_separators = form_fields['column_separators']

        self._profile = profile
        self._entity = entity

        self._col_model = QStandardItemModel()

        self.code_columns = code_columns(entity, self._parent_column_name)
        self._checked_columns = []
        # enable_drag_sort(self.column_code_view)
        self.none = QApplication.translate('CodeProperty', 'None')
        self._column_name = QApplication.translate('CodeProperty', 'columns')
        self.space = QApplication.translate('CodeProperty', 'Single space')
        self.hyphen = QApplication.translate('CodeProperty', 'Hyphen')
        self.forward_slash = QApplication.translate('CodeProperty', 'Forward slash')
        self.backward_slash = QApplication.translate('CodeProperty', 'Backward slash')
        self.underscore = QApplication.translate('CodeProperty', 'Underscore')

        self.separators = {
            '':self.none, '/':'{} (/)'.format(self.forward_slash),
            '\\':'{} (\\)'.format(self.backward_slash),
            '-':'{} (-)'.format(self.hyphen),
            '_':'{} (_)'.format(self.underscore), ' ':self.space
        }

        self.zeros = [self.none, '0', '00', '000', '0000', '00000']
        self.init_gui()
        self.prefix_source_cbo.currentIndexChanged.connect(
            self._on_prefix_source_selected
        )

        self._on_prefix_source_selected()
        # self.column_code_view.__class__.dropEvent = self.drop_end

    def init_gui(self):
        """
        Initializes form widgets
        """
        source_names = self.prefix_source_names()
        self.populate_source_cbo(source_names)
        self.populate_leading_zero()
        self.populate_separator(self.separator_cbo)

        self.populate_columns_list()
        column_header = QApplication.translate('CodeProperty', 'Columns')
        separator_header = QApplication.translate('CodeProperty', 'Separator')
        self.column_code_view.model().setHorizontalHeaderLabels(
            [column_header, separator_header]
        )
        header = self.column_code_view.horizontalHeader()
        header.setResizeMode(0, QHeaderView.Stretch)
        header.setResizeMode(1, QHeaderView.ResizeToContents)

        if self._source:
            self.prefix_source_cbo.setCurrentIndex(
                self.prefix_source_cbo.findText(self._source)
            )
        if self._columns:
            self.set_columns()

        self.set_disable_auto_increment()
        self.set_enable_editing()
        self.set_hide_prefix()
        if self._leading_zero:
            self.leading_zero_cbo.setCurrentIndex(
                self.leading_zero_cbo.findData(self._leading_zero)
            )

        if self._separator:
            self.separator_cbo.setCurrentIndex(
                self.separator_cbo.findData(self._separator)
            )

        longest_item = max(source_names, key=len)
        font_meter = QFontMetrics(self.fontMetrics())
        item_width = font_meter.width(longest_item) + 18
        self.prefix_source_cbo.setStyleSheet(
            '''*
                QComboBox QAbstractItemView{
                    min-width: 150px;
                    width: %spx;
                }
            ''' % item_width
        )

        # Link checkbox and label
        self.disable_auto_increment_lbl.setBuddy(self.disable_auto_increment_chk)
        self.enable_editing_lbl.setBuddy(self.enable_editing_chk)
        self.hide_prefix_lbl.setBuddy(self.hide_prefix_chk)

    def drop_end(self, event):
        for row in range(self.column_code_view.model().rowCount()):
            self.column_code_view.openPersistentEditor(
                self.column_code_view.model().index(row, 1)
            )
        # event.accept()

    def _on_prefix_source_selected(self):
        """
        A slot raised when the prefix source is None. It sets the separator
        to be '' if the prefix is None and disable it. This is because, if
        there is no prefix code, separator has no effect.
        """
        index = self.prefix_source_cbo.currentIndex()
        self.separator_cbo.setDisabled(False)
        self.leading_zero_cbo.setDisabled(False)
        current_text = self.prefix_source_cbo.itemText(index)
        if current_text == self.none or current_text == self._column_name:
            none_index = self.separator_cbo.findData('')
            self.separator_cbo.setCurrentIndex(none_index)
            self.separator_cbo.setDisabled(True)

        if current_text in self.code_columns:
            none_index_sp = self.separator_cbo.findData('')
            self.separator_cbo.setCurrentIndex(none_index_sp)
            self.separator_cbo.setDisabled(True)
            none_index_lo = self.leading_zero_cbo.findData('')
            self.leading_zero_cbo.setCurrentIndex(none_index_lo)
            self.leading_zero_cbo.setDisabled(True)

        if current_text == self._column_name and \
                self.disable_auto_increment_chk.isChecked():
            none_index_lo = self.leading_zero_cbo.findData('')
            self.leading_zero_cbo.setCurrentIndex(none_index_lo)
            self.leading_zero_cbo.setDisabled(True)

        enabled = current_text == self._column_name
        self.column_code_view.setEnabled(enabled)

    def code_columns(self, entity):
        code_columns = []
        for col in entity.columns.values():
            if col.name != self._parent_column_name:
                if col.TYPE_INFO == 'AUTO_GENERATED':
                    code_columns.append(col.name)
        return code_columns

    def prefix_source_names(self):
        """
        Returns a prefix source names in the current profile for
        the code prefix
        rtype: list
        """
        names = []
        names.append(self.none)
        names.append(self._column_name)
        names.extend(self.code_columns)
        names.append('admin_spatial_unit_set')

        for value_list in self._profile.value_lists():
            names.append(value_list.short_name)
        return names

    def populate_columns_list(self):
        """
        Populate the columns view.
        :return:
        :rtype:
        """
        options = {}
        options['type'] = 'combobox'
        delegate = GenericDelegate(
            self.separators, options, self.column_code_view)
        # Set delegate to add widget
        self.column_code_view.setItemDelegate(
            delegate
        )
        self.column_code_view.setItemDelegateForColumn(
            1, delegate
        )

        model = QStandardItemModel(2, 2)
        i = 0
        for row, col in enumerate(self._columns):

            column_item = QStandardItem(self._entity.columns[col].header())
            column_item.setCheckable(True)

            model.setItem(i, 0, column_item)

            column_item.setData(col)
            self.column_code_view.setModel(model)
            i = i + 1

        for col in self._entity.columns.values():
            if col.name == 'id':
                continue

            if col.name not in self._columns:
                # Correct row by reducing by one due to removal of id

                column_item = QStandardItem(col.header())
                column_item.setCheckable(True)

                model.setItem(i, 0, column_item)

                column_item.setData(col.name)
                self.column_code_view.setModel(model)
                i = i + 1

    def set_columns(self):
        """
        Check columns from the configuration. 
        :return:
        :rtype:
        .. versionadded:: 1.7.5
        """
        model = self.column_code_view.model()

        for row in range(model.rowCount()):
            col_item = model.item(row, 0)

            if col_item.data() in self._columns:
                col_idx = self._columns.index(col_item.data())
                separator = self._column_separators[col_idx]
                separator_item = QStandardItem(self.separators[separator])
                model.setItem(row, 1, separator_item)
                separator_item.setData(separator)

                col_item.setCheckState(Qt.Checked)

    def set_disable_auto_increment(self):
        """
        Check if serial is enabled from the configuration.
        :return:
        :rtype:
        .. versionadded:: 1.7.5
        """
        self.disable_auto_increment_chk.setChecked(self._disable_auto_increment)


    def set_hide_prefix(self):
        """
        Check if serial is enabled from the configuration.
        :return:
        :rtype:
        .. versionadded:: 1.7.5
        """
        self.hide_prefix_chk.setChecked(self._hide_prefix)

    def set_enable_editing(self):
        """
        Check if editing is enabled from the configuration.
        :return:
        :rtype:
        .. versionadded:: 1.7.5
        """
        self.enable_editing_chk.setChecked(self._enable_editing)

    def disable_auto_increment(self):
        """
        Returns serial is enabled from the configuration.
        :return:
        :rtype:
        .. versionadded:: 1.7.5
        """
        return self._disable_auto_increment

    def enable_editing(self):
        """
        Returns editing is enabled from the configuration.
        :return:
        :rtype:
        .. versionadded:: 1.7.5
        """
        return self._enable_editing


    def hide_prefix(self):
        """
        Returns the state of prefix hide option.
        :return:
        :rtype:
        .. versionadded:: 1.7.5
        """
        return self._hide_prefix


    def add_enable_auto_increment(self):
        """
        Gets serial is enabled from the configuration.
        :return:
        :rtype:
        .. versionadded:: 1.7.5
        """
        self._disable_auto_increment = self.disable_auto_increment_chk.isChecked()

    def add_hide_prefix(self):
        """
        Gets the state of hide prefix and set it to the property..
        :return:
        :rtype:
        .. versionadded:: 1.7.5
        """
        self._hide_prefix = self.hide_prefix_chk.isChecked()

    def add_enable_editing(self):
        """
        Gets editing is enabled from the configuration.
        :return:
        :rtype:
        .. versionadded:: 1.7.5
        """
        self._enable_editing = self.enable_editing_chk.isChecked()

    def populate_source_cbo(self, names):
        """
        Populate combobox with entity names
        :param names: List of entity names
        :type names: List
        """
        self.prefix_source_cbo.clear()
        self.prefix_source_cbo.insertItems(0, names)
        self.prefix_source_cbo.setCurrentIndex(0)

    def populate_leading_zero(self):
        """
        Populate combobox with entity names
        """
        self.leading_zero_cbo.clear()
        for zero in self.zeros:
            if zero == self.none:
                self.leading_zero_cbo.addItem(zero, '')
            else:
                self.leading_zero_cbo.addItem(zero, zero)
        self.leading_zero_cbo.setCurrentIndex(0)

    def populate_separator(self, combo):
        """
        Populate the separator combobox with separators.
        """
        combo.clear()
        for separator, desc in self.separators.iteritems():
            combo.addItem(desc, separator)
        combo.setCurrentIndex(0)

    def add_prefix_source(self):
        """
        Set the prefix source.
        """
        self._source = unicode(self.prefix_source_cbo.currentText())

    def add_columns(self):
        """
        Set the columns.
        .. versionadded:: 1.7.5
        """
        self._columns[:] = []
        model = self.column_code_view.model()

        row_data = []
        for row in range(model.rowCount()):
            item = model.item(row)
            if item.checkState() == Qt.Checked:
                id_idx = model.index(row, 0)
                row_data.append(id_idx.data(Qt.UserRole + 1))

        self._columns = row_data

    def add_column_separators(self):
        """
        Set column separators.
        .. versionadded:: 1.7.5
        """
        self._column_separators[:] = []
        model = self.column_code_view.model()

        row_data = []
        for row in range(model.rowCount()):
            item = model.item(row)
            if item.checkState() == Qt.Checked:
                id_idx = model.index(row, 1)
                separator = id_idx.data(Qt.UserRole + 1)
                if separator is None:
                    separator = ''
                row_data.append(separator)
       
        self._column_separators = row_data

    def add_leading_zero(self):
        """
        Set the prefix source.
        """
        current_index = self.leading_zero_cbo.currentIndex()
        current_data = self.leading_zero_cbo.itemData(current_index)
        self._leading_zero = unicode(current_data)

    def add_separator(self):
        """
        Set the prefix source.
        """
        current_index = self.separator_cbo.currentIndex()
        current_data = self.separator_cbo.itemData(current_index)
        self._separator = unicode(current_data)

    def prefix_source(self):
        """
        Returns the prefix source
        rtype: String
        """
        return self._source

    def columns(self):
        """
        Returns the columns
        rtype: List
        """
        current_text = self.prefix_source_cbo.currentText()
        if current_text != self._column_name:
            return []
        return self._columns

    def column_separators(self):
        """
        Returns the columns
        rtype: List
        """
        current_text = self.prefix_source_cbo.currentText()
        if current_text != self._column_name:
            return []
        return self._column_separators

    def leading_zero(self):
        """
        Returns the selected leading_zero
        rtype: String
        """
        return self._leading_zero

    def separator(self):
        """
        Returns the selected separator
        rtype: String
        """
        return self._separator

    def accept(self):
        """
        QDialog accept event.
        """
        self.add_prefix_source()
        self.add_columns()
        self.add_column_separators()
        self.add_leading_zero()
        self.add_separator()
        self.add_enable_auto_increment()
        self.add_enable_editing()
        self.add_hide_prefix()
        self.done(1)

    def reject(self):
        """
        QDialog accept event.
        """
        self.done(0)
