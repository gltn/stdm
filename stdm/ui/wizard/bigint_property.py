# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : bigint_property
Description          : Set properties for BigInt data type
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
from qgis.PyQt.QtGui import QIntValidator
from qgis.PyQt.QtWidgets import (
    QDialog,
    QApplication,
    QMessageBox
)

from stdm.ui.gui_utils import GuiUtils

WIDGET, BASE = uic.loadUiType(
    GuiUtils.get_ui_file_path('wizard/ui_bigint_property.ui'))


class BigintProperty(WIDGET, BASE):
    """
    Editor to create/edit integer column property
    """

    def __init__(self, parent, form_fields):
        """
        :param parent: Owner of the form
        :type parent: QWidget
        :param form_fields: Contains data from the column editor window
        :type form_field: dictionary
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self._min_val = form_fields['minimum']
        self._max_val = form_fields['maximum']
        self.in_db = form_fields['in_db']

        self.init_gui()

    def init_gui(self):
        """
        Initializes form widgets
        """
        validator = QIntValidator()
        self.edtMinVal.setValidator(validator)
        self.edtMaxVal.setValidator(validator)

        self.edtMinVal.setText(str(self._min_val))
        self.edtMaxVal.setText(str(self._max_val))

        self.edtMinVal.setFocus()

        self.edtMinVal.setEnabled(not self.in_db)
        self.edtMaxVal.setEnabled(not self.in_db)

    def add_values(self):
        """
        Sets min/max properties with values from form widgets
        """
        self._min_val = int(self.edtMinVal.text())
        self._max_val = int(self.edtMaxVal.text())

    def min_val(self):
        """
        Returns minimum property
        :rtype: int
        """
        return self._min_val

    def max_val(self):
        """
        Returns maximum property
        :rtype: int
        """
        return self._max_val

    def accept(self):
        if self.edtMinVal.text() == '':
            self.show_message(QApplication.translate("BigintPropetyEditor",
                                                     "Please set minimum value."))
            return

        if self.edtMaxVal.text() == '':
            self.show_message(QApplication.translate("BigintPropetyEditor",
                                                     "Please set maximum value."))
            return

        self.add_values()
        self.done(1)

    def reject(self):
        self.done(0)

    def show_message(self, message, msg_icon=QMessageBox.Critical):
        msg = QMessageBox(self)
        msg.setIcon(msg_icon)
        msg.setWindowTitle(QApplication.translate("STDM Configuration Wizard", "STDM"))
        msg.setText(QApplication.translate("STDM Configuration Wizard", message))
        msg.exec_()
