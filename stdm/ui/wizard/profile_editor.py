# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : profile_editor
Description          : STDM profile editor
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
    QMessageBox)

from stdm.ui.notification import NotificationBar
from stdm.ui.wizard.ui_profile import Ui_Profile


class ProfileEditor(QDialog, Ui_Profile):
    def __init__(self, parent):
        QDialog.__init__(self, parent)

        self.profile_name = ''
        self.desc = ''

        self.setupUi(self)
        self.init_controls()
        self.notice_bar = NotificationBar(self.notif_bar)

    def init_controls(self):
        self.edtProfile.clear()
        self.edtDesc.clear()
        self.edtProfile.setFocus()
        self.edtProfile.textChanged.connect(self.validate_text)

    def format_name(self, txt):
        ''''remove any trailing spaces in the name and replace them underscore'''
        formatted_name = txt.strip().replace(' ', "_")
        return formatted_name

    def add_profile(self):
        self.profile_name = self.format_name(str(self.edtProfile.text()))
        self.desc = str(self.edtDesc.text())

    def show_notification(self, message):
        """
        Shows a warning notification bar message.
        :param message: The message of the notification.
        :type message: String
        """
        msg = self.trUtf8(message)
        self.notice_bar.clear()
        self.notice_bar.insertErrorNotification(msg)

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
                msg = '\'{0}\' is not allowed at this position.'.format(
                    last_character
                )
                self.show_notification(msg)
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

    def accept(self):
        '''listen to user action on the dialog'''
        if self.edtProfile.text() == '' or self.edtProfile.text() == ' ':
            self.error_info_message(
                QApplication.translate(
                    "ProfileEditor", "Please enter a valid Profile name."
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
