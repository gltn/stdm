"""
/***************************************************************************
Name                 : Related Table Dialog
Description          : Dialog for defining configuration settings for the
                       RelatedTableTranslator implementation.
Date                 : 24/October/2014
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
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QApplication,
    QDialog
)

from stdm.data.importexport.value_translators import RelatedTableTranslator
from stdm.data.pg_utils import (
    table_column_names
)
from stdm.ui.gui_utils import GuiUtils
from stdm.ui.importexport.translator_widget_base import TranslatorDialogBase
from stdm.ui.notification import NotificationBar

__all__ = ["RelatedTableDialog"]

WIDGET, BASE = uic.loadUiType(
    GuiUtils.get_ui_file_path('importexport/ui_related_table_dialog.ui'))


class RelatedTableDialog(TranslatorDialogBase, WIDGET, BASE):
    """
    Dialog for defining configuration settings for the
    RelatedTableTranslator class implementation.
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

        self._set_source_table_headers()

        # Set UI values
        self.txt_table_name.setText(dest_table)
        self.txt_column_name.setText(dest_col)

        # Load STDM tables exluding views
        self._load_tables()

        # Connect signals
        self.cbo_source_tables.currentIndexChanged.connect(self._on_source_table_changed)

    def _load_tables(self):
        """
        Loads both textual and spatial tables into the user list.
        """
        self.cbo_source_tables.addItem("")
        self.cbo_source_tables.addItems(self.db_tables())

    def value_translator(self):
        rel_tab_translator = RelatedTableTranslator()
        rel_tab_translator.set_referencing_table(self.txt_table_name.text())
        rel_tab_translator.set_referencing_column(self.txt_column_name.text())
        rel_tab_translator.set_referenced_table(self.cbo_source_tables.currentText())
        rel_tab_translator.set_output_reference_column(self.cbo_output_column.currentText())
        rel_tab_translator.set_input_referenced_columns(self.column_pairings())

        return rel_tab_translator

    def _set_source_table_headers(self):
        labels = [QApplication.translate("RelatedTableDialog", "Source Table"),
                  QApplication.translate("RelatedTableDialog",
                                         "Referenced Table")]
        self.tb_source_trans_cols.set_header_labels(labels)

    def _on_source_table_changed(self, index):
        source_table = self.cbo_source_tables.currentText()

        self.cbo_output_column.clear()

        if source_table:
            ref_table_cols = table_column_names(source_table)

            self.tb_source_trans_cols.set_combo_selection([self._source_cols,
                                                           ref_table_cols])

            # self.cbo_output_column.addItem("")
            self.cbo_output_column.addItems(ref_table_cols)

        else:
            self.tb_source_trans_cols.clear_view()

    def column_pairings(self):
        """
        :return: Source and reference table column matchings.
        :rtype: dict
        """
        return self.tb_source_trans_cols.column_pairings()

    def validate(self):
        """
        :return: Check user entries.
        :rtype: bool
        """
        if self.cbo_source_tables.currentText() == "":
            msg = QApplication.translate("RelatedTableDialog", "Please select "
                                                               "the reference table name.")
            self._notif_bar.clear()
            self._notif_bar.insertWarningNotification(msg)

            return False

        if self.cbo_output_column.currentText() == "":
            msg = QApplication.translate("RelatedTableDialog", "Please select "
                                                               "the output column name.")
            self._notif_bar.clear()
            self._notif_bar.insertWarningNotification(msg)

            return False

        if len(self.column_pairings()) == 0:
            msg = QApplication.translate("RelatedTableDialog", "Please specify "
                                                               "at least one column pairing.")
            self._notif_bar.clear()
            self._notif_bar.insertWarningNotification(msg)

            return False

        return True

    def accept(self):
        """
        Validate before accepting user input.
        """
        if self.validate():
            super(RelatedTableDialog, self).accept()
