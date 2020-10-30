# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : varchar_property
Description          : Set properties for Varchar data type
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

from qgis.PyQt.QtCore import QRegExp
from qgis.PyQt.QtGui import QRegExpValidator
from qgis.PyQt.QtWidgets import (
    QDialog,
    QApplication,
    QMessageBox
)

from stdm.ui.wizard.ui_varchar_property import Ui_VarcharProperty


class VarcharProperty(QDialog, Ui_VarcharProperty):
    """
    Editor to create/edit varchar max len property
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

        self._max_len = form_fields['maximum']
        self.in_db = form_fields['in_db']

        self.init_gui()

    def init_gui(self):
        """
        Initializes form widgets
        """
        charlen_regex = QRegExp('^[0-9]{1,3}$')
        charlen_validator = QRegExpValidator(charlen_regex)
        self.edtCharLen.setValidator(charlen_validator)

        self.edtCharLen.setText(str(self._max_len))
        self.edtCharLen.setFocus()

        self.edtCharLen.setEnabled(not self.in_db)

    def add_len(self):
        """
        Sets the max_len property from the form widget.
        """
        self._max_len = int(self.edtCharLen.text())

    def max_len(self):
        """
        Returns the max_len property
        :rtype: int
        """
        return self._max_len

    def accept(self):
        if self.edtCharLen.text() == '':
            self.show_message(QApplication.translate("VarcharPropetyEditor",
                                                     "Please enter length for the column."))
            return

        self.add_len()
        self.done(1)

    def reject(self):
        self.done(0)

    def show_message(self, message, msg_icon=QMessageBox.Critical):
        msg = QMessageBox(self)
        msg.setIcon(msg_icon)
        msg.setWindowTitle(QApplication.translate("STDM Configuration Wizard", "STDM"))
        msg.setText(QApplication.translate("STDM Configuration Wizard", message))
        msg.exec_()
