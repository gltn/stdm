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
    QStandardItem, QStandardItemModel
from stdm.utils.util import (
    enable_drag_sort
)
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
        self._profile = profile
        self._entity = entity

        self._col_model = QStandardItemModel()
        self.column_code_view.setModel(self._col_model)

        self._checked_columns = []
        enable_drag_sort(self.column_code_view)
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

    def init_gui(self):
        """
        Initializes form widgets
        """
        source_names = self.prefix_source_names()
        self.populate_source_cbo(source_names)
        self.populate_leading_zero()
        self.populate_separator()
        self.populate_columns_list()
        if self._source:
            self.prefix_source_cbo.setCurrentIndex(
                self.prefix_source_cbo.findText(self._source)
            )
        if self._columns:
            self.set_columns()
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

    def _on_prefix_source_selected(self):
        """
        A slot raised when the prefix source is None. It sets the separator
        to be '' if the prefix is None and disable it. This is because, if
        there is no prefix code, separator has no effect.
        """
        index = self.prefix_source_cbo.currentIndex()
        self.separator_cbo.setDisabled(False)
        current_text = self.prefix_source_cbo.itemText(index)
        if current_text == self.none:
            none_index = self.separator_cbo.findData('')
            self.separator_cbo.setCurrentIndex(none_index)
            self.separator_cbo.setDisabled(True)

        enabled = current_text == self._column_name
        self.column_code_view.setEnabled(enabled)

    def prefix_source_names(self):
        """
        Returns a prefix source names in the current profile for
        the code prefix
        rtype: list
        """
        names = []
        names.append(self.none)
        names.append(self._column_name)
        names.append('admin_spatial_unit_set')

        for value_list in self._profile.value_lists():
            names.append(value_list.short_name)
        return names

    def populate_columns_list(self):
        self._col_model.clear()
        for i, col in enumerate(self._entity.columns.values()):

            if col.name == 'id':
                continue

            column_item = QStandardItem(col.header())
            column_item.setCheckable(True)
            column_item.setData(col.name)

            self._col_model.appendRow([column_item])

    def set_columns(self):
        """
        Check columns from the configuration. 
        :return:
        :rtype:
        .. versionadded:: 1.7.5
        """
        for index in range(self._col_model.rowCount()):
            item = self._col_model.item(index)
            if item.data() in self._columns:
                item.setCheckState(Qt.Checked)

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

    def populate_separator(self):
        """
        Populate the separator combobox with separators.
        """
        self.separator_cbo.clear()
        for separator, desc in self.separators.iteritems():
            self.separator_cbo.addItem(desc, separator)
        self.separator_cbo.setCurrentIndex(0)

    def add_prefix_source(self):
        """
        Set the prefix source.
        """
        self._source = unicode(self.prefix_source_cbo.currentText())

    def add_columns(self):
        """
        Set the prefix source.
        .. versionadded:: 1.7.5
        """
        self._columns[:] = []
        for index in range(self._col_model.rowCount()):
            item = self._col_model.item(index)
            if item.checkState() == Qt.Checked:
                self._columns.append(item.data())

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
        self.add_leading_zero()
        self.add_separator()
        self.done(1)

    def reject(self):
        """
        QDialog accept event.
        """
        self.done(0)
