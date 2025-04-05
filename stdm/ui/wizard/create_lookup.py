# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : create_lookup
Description          : Create new lookup entities
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
from qgis.PyQt.QtCore import (
    QSettings,
    QRegExp
)
from qgis.PyQt.QtGui import (
    QValidator,
    QRegExpValidator
)
from qgis.PyQt.QtWidgets import (
    QDialog,
    QApplication,
    QMessageBox,
    QDialogButtonBox
)

from stdm.data.configuration.value_list import (
    ValueList,
    value_list_factory
)
from stdm.ui.gui_utils import GuiUtils
from stdm.ui.notification import NotificationBar

WIDGET, BASE = uic.loadUiType(
    GuiUtils.get_ui_file_path('wizard/ui_lookup_entity.ui'))


class LookupEditor(WIDGET, BASE):
    """
    Form to add/edit lookup entities.
    """

    def __init__(self, parent, profile, lookup=None):
        """
        :param parent: Owner of this dialog
        :type parent: QWidget
        :param profile: A profile to add/edit lookup
        :type profile: Profile
        :type inplace: Flag to check if lookup creation is initiated from the
                       'normal' lookup creation process -inplace = False,
                       this is the normal state. If 'inplace' = True, then
                       creation is initiated from the the lookup selection dialog
        :param lookup: Value list to create, if None this is a new value list
         else its an edit
        :type lookup: ValueList
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.profile = profile
        self.lookup = lookup
        self.notice_bar = NotificationBar(self.notif_bar)
        self.init_gui()

    def init_gui(self):
        """
        Initializes form widgets
        """
        self.edtName.setFocus()
        if self.lookup:
            self.edtName.setText(
                self.lookup.short_name.replace('check_', ''))
            self.edtName.setEnabled(not self.lookup.entity_in_database)
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(not self.lookup.entity_in_database)
        self.edtName.textChanged.connect(self.validate_text)

    def show_notification(self, message):
        """
        Shows a warning notification bar message.
        :param message: The message of the notification.
        :type message: String
        """
        msg = self.tr(message)
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
        locale = (QSettings().value("locale/userLocale") or 'en-US')[0:2]
        last_character = text[-1:]
        if locale == 'en':
            name_regex = QRegExp('^(?=.{0,40}$)[ _a-zA-Z][a-zA-Z0-9_ ]*$')
            name_validator = QRegExpValidator(name_regex)
            text_edit.setValidator(name_validator)
            QApplication.processEvents()

            state = name_validator.validate(text, text.index(last_character))[0]
            if state != QValidator.Acceptable:
                self.show_notification('"{}" is not allowed at this position.'.
                                       format(last_character)
                                       )
                text = text[:-1]

        # fix caps, underscores, and spaces
        if last_character.isupper():
            text = text.lower()
        if last_character == ' ':
            text = text.replace(' ', '_')

        if len(text) > 1:
            if text[0] == ' ' or text[0] == '_':
                text = text[1:]
            text = text.replace(' ', '_').lower()

        self.blockSignals(True)
        text_edit.setText(text)
        text_edit.setCursorPosition(cursor_position)
        self.blockSignals(False)
        text_edit.setValidator(None)

    def format_lookup_name(self, name):
        """
        Replace spaces with underscore in a name string
        :param name: Name to replace spaces
        :type name: str
        :rtype: str
        """
        formatted_name = str(name).strip()
        formatted_name = formatted_name.replace(' ', "_")
        return formatted_name.lower()

    def create_lookup(self, name):
        """
        Creates a lookup entity and add it to a profile.
        If this is an edit, first the previous lookup is removed before
        adding a new one.
        :param name: Name of the new/edited lookup
        :type name: Unicode
        """
        name = self.format_lookup_name(name)
        new_lookup = self.profile.create_entity(name, value_list_factory)
        return new_lookup

    def accept(self):
        if self.edtName.text() == '' or self.edtName.text() == '_':
            self.error_message(
                QApplication.translate(
                    "LookupEditor", "Please enter a valid lookup name."
                )
            )
            return

        if self.edtName.text() == 'check':
            self.error_message(QApplication.translate("LookupEditor",
                                                      "'check' is used internally by STDM! "
                                                      "Select another name for the lookup"))
            return

        short_name = str(self.edtName.text())

        if self.lookup is None:  # new lookup
            if self.duplicate_check(short_name):
                self.error_message(
                    self.tr(
                        "Lookup with the same name already "
                        "exist in the current profile!"
                    )
                )
                return
            else:
                new_lookup = self.create_lookup(short_name)
                self.profile.add_entity(new_lookup)
                self.lookup = new_lookup
        else:
            self.edit_lookup(short_name)

        self.done(1)

    def duplicate_check(self, name):
        """
        Return True if we have an entity in the current profile with same 'name'
        :param name: entity short_name
        :type name: Unicode
        :rtype:boolean
        """
        return name in self.profile.entities

    def edit_lookup(self, short_name):
        short_name = short_name.replace('check_', '')
        self.lookup.short_name = '{0}_{1}'.format('check', short_name)

    def reject(self):
        self.done(0)

    def error_message(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("STDM")
        msg.setText(message)
        msg.exec_()
