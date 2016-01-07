"""
/***************************************************************************
Name                 : Multiple Enumeration Configuration Dialog
Description          : Dialog for defining configuration settings for the
                       MultipleEnumerationTranslator implementation.
Date                 : 11/October/2014
copyright            : (C) 2014 by UN-Habitat and implementing partners.
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
    QApplication,
    QDialog,
    QMessageBox
)

from stdm.data.pg_utils import (
   table_column_names,
   pg_tables,
   spatial_tables
)
from stdm.data.importexport import MultipleEnumerationTranslator
from stdm.utils import getIndex

from ..notification import NotificationBar
from .translator_widget_base import TranslatorDialogBase
from .ui_multiple_enumeration_dialog import Ui_EnumerationTranslatorDialog

__all__ = ["MultipleEnumerationDialog"]

class MultipleEnumerationDialog(QDialog, Ui_EnumerationTranslatorDialog, TranslatorDialogBase):
    """
    Dialog for defining configuration settings for the MultipleEnumerationTranslator
    class implementation.
    """
    def __init__(self, parent, source_cols, dest_table, dest_col, src_col):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        TranslatorDialogBase.__init__(self, source_cols, dest_table, dest_col, src_col)

        self._notif_bar = NotificationBar(self.vl_notification)

        #Container of column names for an enumeration table
        self._enum_col_names = []

        self._load_separators()

        #Init user selection to the corresponding UI controls
        self.txt_source_col.setText(self._src_col)

        #Remove selected column name from the 'other column' list
        sel_col_idx = getIndex(self._source_cols, self._src_col)
        if sel_col_idx != -1:
            self._source_cols.remove(self._src_col)

        #Load source columns
        self.cbo_src_other_col.addItem("")
        self.cbo_src_other_col.addItems(self._source_cols)

        #Load database tables
        self.cbo_enum_table.addItem("")
        self.cbo_enum_table.addItems(self.db_tables())

        #Connect signals
        self.cbo_enum_table.currentIndexChanged.connect(self._on_enum_table_changed)
        self.cbo_primary_col.currentIndexChanged.connect(self._on_primary_col_changed)

    def _load_separators(self):
        separators = []

        comma_sep = (QApplication.translate("MultipleEnumerationDialog",
                    "Comma (,)"), ",")
        separators.append(comma_sep)

        colon_sep = (QApplication.translate("MultipleEnumerationDialog",
                    "Colon (:)"), ":")
        separators.append(colon_sep)

        semi_colon_sep = (QApplication.translate("MultipleEnumerationDialog",
                    "Semi-colon (;)"), ";")
        separators.append(semi_colon_sep)

        asterisk_sep = (QApplication.translate("MultipleEnumerationDialog",
                    "Asterisk (*)"), "*")
        separators.append(asterisk_sep)

        self.cbo_separator.addItem("")

        for sep in separators:
            self.cbo_separator.addItem(sep[0], sep[1])

    def _on_enum_table_changed(self, index):
        """
        Slot raised when an enumeration table is selected.
        :param index: Index of currently selected item.
        :type index: int
        """
        enum_table = self.cbo_enum_table.currentText()

        self.cbo_primary_col.clear()
        self.cbo_other_col.clear()

        self._enum_col_names = []

        if enum_table:
            self._enum_col_names = table_column_names(enum_table)

            #Remove id column name
            id_col = "id"
            id_idx = getIndex(self._enum_col_names, id_col)
            if id_idx != -1:
                self._enum_col_names.remove(id_col)

            self.cbo_primary_col.addItem("")
            self.cbo_primary_col.addItems(self._enum_col_names)

    def _on_primary_col_changed(self, index):
        """
        When the primary column of the enumeration is selected, remove it
        from the 'other column' items/
        :param index: Index of currently selected item.
        :type index: int
        """
        self.cbo_other_col.clear()

        primary_enum_col = self.cbo_primary_col.currentText()
        if primary_enum_col:
            other_cols = list(self._enum_col_names)

            #Remove the currently selected column name for the primary column
            other_cols.remove(primary_enum_col)

            self.cbo_other_col.addItem("")
            self.cbo_other_col.addItems(other_cols)

    def validate(self):
        """
        :return: Check user entries.
        :rtype: bool
        """
        if not self.txt_source_col.text():
            msg = QApplication.translate("MultipleEnumerationDialog",
                    "Source column does not exist.")
            self._notif_bar.clear()
            self._notif_bar.insertErrorNotification(msg)

            return False

        if not self.cbo_separator.currentText():
            msg = QApplication.translate("MultipleEnumerationDialog",
                    "Please specify a separator for the enumeration series.")
            self._notif_bar.clear()
            self._notif_bar.insertErrorNotification(msg)

            return False

        if not self.cbo_enum_table.currentText():
            msg = QApplication.translate("MultipleEnumerationDialog",
                    "Please specify the linked enumeration table.")
            self._notif_bar.clear()
            self._notif_bar.insertErrorNotification(msg)

            return False

        if not self.cbo_primary_col.currentText():
            msg = QApplication.translate("MultipleEnumerationDialog",
                    "Please specify the primary enumeration column in the enumeration table.")
            self._notif_bar.clear()
            self._notif_bar.insertErrorNotification(msg)

            return False

        '''
        You cannot specify enum other column if a corresponding one in the source table
        has not been selected.
        '''
        other_source_col = self.cbo_src_other_col.currentText()
        other_enum_table_col = self.cbo_other_col.currentText()

        if other_enum_table_col and not other_source_col:
            msg = QApplication.translate("MultipleEnumerationDialog",
                    "Please select the 'Other' column reference for the the source table.")
            self._notif_bar.clear()
            self._notif_bar.insertErrorNotification(msg)

            return False

        return True

    def separator(self):
        sep_idx = self.cbo_separator.currentIndex()

        if sep_idx == 0:
            return ""

        else:
            return self.cbo_separator.itemData(sep_idx)

    def column_pairings(self):
        """
        Format of dict - source column name: matching enumeration table column.
        Primary enum column is the first item in the dictionary.
        """
        col_pairs = OrderedDict()

        col_pairs[self.txt_source_col.text()] = self.cbo_primary_col.currentText()

        #Other column pairings
        other_source_col = self.cbo_src_other_col.currentText()
        other_enum_table_col = self.cbo_other_col.currentText()

        if other_source_col and other_enum_table_col:
            col_pairs[other_source_col] = other_enum_table_col

        return col_pairs

    def value_translator(self):
        enum_translator = MultipleEnumerationTranslator()
        enum_translator.set_referencing_table(self._dest_table)
        enum_translator.set_referencing_column(self._dest_col)
        enum_translator.set_referenced_table(self.cbo_enum_table.currentText())
        enum_translator.set_input_referenced_columns(self.column_pairings())
        enum_translator.set_separator(self.separator())

        return enum_translator

    def accept(self):
        """
        Validate before accepting user input.
        """
        if self.validate():
            super(MultipleEnumerationDialog, self).accept()