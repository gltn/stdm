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

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QApplication,
    QDialog
)

from stdm.data.importexport.value_translators import MultipleEnumerationTranslator
from stdm.ui.gui_utils import GuiUtils
from stdm.ui.importexport.translator_widget_base import TranslatorDialogBase
from stdm.ui.notification import NotificationBar

__all__ = ["MultipleEnumerationDialog"]

WIDGET, BASE = uic.loadUiType(
    GuiUtils.get_ui_file_path('importexport/ui_multiple_enumeration_dialog.ui'))


class MultipleEnumerationDialog(TranslatorDialogBase, WIDGET, BASE):
    """
    Dialog for defining configuration settings for the MultipleEnumerationTranslator
    class implementation.
    """

    def __init__(self, parent, source_cols, dest_table, 
                 dest_col, src_col):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        TranslatorDialogBase.__init__(self, 
                                      source_cols, 
                                      dest_table, 
                                      dest_col, 
                                      src_col)

        self._notif_bar = NotificationBar(self.vl_notification)

        # Container of column names for an enumeration table
        self._enum_col_names = []

        self._load_separators()

        # Init user selection to the corresponding UI controls
        self.txt_source_col.setText(self._src_col)

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
                                         "Please specify a separator for the multiple select data.")
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
        col_pairs[self.txt_source_col.text()] = self._dest_col

        return col_pairs

    def value_translator(self):
        enum_translator = MultipleEnumerationTranslator()
        enum_translator.set_referencing_table(self._dest_table)
        enum_translator.set_referencing_column(self._dest_col)
        enum_translator.set_input_referenced_columns(self.column_pairings())
        enum_translator.set_separator(self.separator())

        return enum_translator

    def accept(self):
        """
        Validate before accepting user input.
        """
        if self.validate():
            super(MultipleEnumerationDialog, self).accept()
