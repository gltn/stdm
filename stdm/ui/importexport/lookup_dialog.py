"""
/***************************************************************************
Name                 : Lookup Dialog
Description          : Dialog for defining configuration settings for the
                       lookup translation implementation.
Date                 : 16/January/2017
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

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QApplication,
    QDialog
)

from stdm.data.importexport.value_translators import LookupValueTranslator
from stdm.ui.gui_utils import GuiUtils
from stdm.ui.importexport.translator_widget_base import TranslatorDialogBase
from stdm.ui.notification import NotificationBar
#from stdm.ui.importexport.ui_lookup_dialog import Ui_LookupTranslatorDialog

WIDGET, BASE = uic.loadUiType(
    GuiUtils.get_ui_file_path('importexport/ui_lookup_dialog.ui'))


class LookupDialog(TranslatorDialogBase, WIDGET, BASE):
    """
    Dialog for defining configuration settings for the lookup translation
    implementation.
    """
    def __init__(self, parent, source_cols, dest_table, 
                 dest_col, src_col):
        QDialog.__init__(self, parent)

        self.setupUi(self)

        TranslatorDialogBase.__init__(
            self,
            source_cols,
            dest_table,
            dest_col,
            src_col
        )

        self._notif_bar = NotificationBar(self.vl_notification)

        # Populate controls
        self._load_lookup_tables()

        # Connect signals
        self.cbo_lookup.currentIndexChanged.connect(
            self._on_lookup_table_name_changed
        )

        curr_title = self.windowTitle()
        title = f"{curr_title}- {dest_col}"
        self.setWindowTitle(title)


    def _load_lookup_tables(self):
        # Load lookup table names
        c_profile = self._current_profile
        if c_profile is None:
            msg = QApplication.translate(
                'LookupDialog',
                'Current profile could not be determined.'
            )
            self._notif_bar.clear()
            self._notif_bar.insertErrorNotification(msg)

            return

        lookups = [e.name for e in c_profile.value_lists()]

        self.cbo_lookup.clear()
        self.cbo_lookup.addItem('')
        self.cbo_lookup.addItems(lookups)

    def _on_lookup_table_name_changed(self, idx):
        # Slot raised when the lookup table name changes.
        self.cbo_default.clear()

        if idx == -1:
            return

        t_name = self.cbo_lookup.currentText()
        self.load_lookup_values(t_name)

    def load_lookup_values(self, table_name):
        """
        Load the default value combobox with values from the specified lookup
        table name.
        :param table_name: Lookup table name.
        :type table_name: str
        """
        self.cbo_default.clear()

        if not table_name:
            return

        # Get lookup entity
        lk_ent = self._current_profile.entity_by_name(table_name)
        if lk_ent is None:
            msg = QApplication.translate(
                'LookupDialog',
                'Lookup values could not be loaded.'
            )
            self._notif_bar.clear()
            self._notif_bar.insertErrorNotification(msg)

            return

        lk_values = lk_ent.lookups()

        self.cbo_default.addItem('')

        for lk_value in lk_values:
            text_value = None
            for k, v in lk_ent.values.items():
                if v.value == lk_value:
                    text_value = v.value
            if text_value is not None:
                self.cbo_default.addItem(text_value)

    def value_translator(self):
        """
        :return: Returns the lookup value translator object.
        :rtype: LookupValueTranslator
        """
        lookup_translator = LookupValueTranslator()
        lookup_translator.set_referencing_table(self._dest_table)
        lookup_translator.set_referencing_column(self._dest_col)
        lookup_translator.set_referenced_table(self.cbo_lookup.currentText())
        lookup_translator.add_source_reference_column(
            self._src_col,
            self._dest_col
        )
        lookup_translator.set_default_value(self.cbo_default.currentText())

        return lookup_translator

    def validate(self):
        """
        Check user configuration and validate if they are correct.
        :return: Returns True if user configuration is correct, otherwise
        False.
        :rtype: bool
        """
        if not self.cbo_lookup.currentText():
            msg = QApplication.translate(
                'LookupDialog',
                'Please select the referenced lookup table.'
            )
            self._notif_bar.clear()
            self._notif_bar.insertWarningNotification(msg)

            return False

        return True

    def accept(self):
        """
        Validate before accepting user input.
        """
        if self.validate():
            super(LookupDialog, self).accept()
