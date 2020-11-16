# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : copy_editor
Description          : STDM copy editor
Date                 : 20/January/2016
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
from qgis.PyQt.QtCore import (
    QSettings,
    QRegExp
)
from qgis.PyQt.QtGui import (
    QRegExpValidator,
    QValidator
)
from qgis.PyQt.QtWidgets import (
    QDialog,
    QApplication,
    QMessageBox
)

from stdm.ui.gui_utils import GuiUtils

WIDGET, BASE = uic.loadUiType(
    GuiUtils.get_ui_file_path('wizard/ui_copy_profile.ui'))


class CopyProfileEditor(WIDGET, BASE):
    def __init__(self, parent, orig_name, orig_desc, profile_names):
        QDialog.__init__(self, parent)

        self.orig_name = orig_name
        self.orig_desc = orig_desc
        self.copy_name = orig_name + '_copy'
        self.copy_desc = ''
        self.profile_names = profile_names

        self.setupUi(self)
        self.init_controls()

    def init_controls(self):
        self.edtFromProfile.setText(self.orig_name)
        self.edtDesc.setText(self.orig_desc)
        self.edtName.setText(self.copy_name)
        self.edtName.setFocus()
        self.edtName.textChanged.connect(self.validate_text)

    def validate_text(self, text):
        """
        Validates and updates the entered text if necessary.
        Spaces are replaced by _ and capital letters are replaced by small.
        :param text: The text entered
        :type text: String
        """
        text_edit = self.sender()
        cursor_position = text_edit.cursorPosition()
        text_edit.setValidator(None)
        if len(text) == 0:
            return
        locale = QSettings().value("locale/userLocale")[0:2]

        if locale == 'en':
            name_regex = QRegExp('^(?=.{0,40}$)[ _a-zA-Z][a-zA-Z0-9_ ]*$')
            name_validator = QRegExpValidator(name_regex)
            text_edit.setValidator(name_validator)
            QApplication.processEvents()
            last_character = text[-1:]
            state = name_validator.validate(text, text.index(last_character))[0]
            if state != QValidator.Acceptable:
                self.show_notification('"{}" is not allowed at this position.'.
                                       format(last_character)
                                       )
                text = text[:-1]

        # remove space and underscore at the beginning of the text
        if len(text) > 1:
            if text[0] == ' ' or text[0] == '_':
                text = text[1:]

        self.blockSignals(True)
        text_edit.setText(text)
        text_edit.setCursorPosition(cursor_position)
        self.blockSignals(False)
        text_edit.setValidator(None)

    def format_name(self, txt):
        ''''remove any trailing spaces in the name and replace them underscore'''
        formatted_name = txt.strip().replace(' ', "_")
        return formatted_name

    def add_profile(self):
        self.copy_name = self.format_name(str(self.edtName.text()))
        self.copy_desc = self.edtDesc.text()

    def accept(self):
        '''
        listen to user OK action
        '''
        if self.edtName.text() == '':
            self.error_info_message(
                QApplication.translate(
                    "CopyEditor", "Please enter a profile name."
                )
            )
            return

        # avoid existing profile names
        if self.edtName.text() in self.profile_names:
            self.error_info_message(
                QApplication.translate(
                    "CopyEditor",
                    "Entered name is already in use. "
                    "Please enter another profile name."
                )
            )
            return

        self.add_profile()
        self.done(1)

    def reject(self):
        self.done(0)

    def error_info_message(self, Message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("STDM")
        msg.setText(Message)
        msg.exec_()
