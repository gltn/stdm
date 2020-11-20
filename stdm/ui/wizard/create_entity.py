# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : create_entity
Description          : Create an entity
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
    Qt,
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
)

from stdm.data.configuration.entity import entity_factory
from stdm.data.pg_utils import pg_table_exists
from stdm.ui.gui_utils import GuiUtils
from stdm.ui.notification import NotificationBar

WIDGET, BASE = uic.loadUiType(
    GuiUtils.get_ui_file_path('wizard/ui_entity.ui'))


class EntityEditor(WIDGET, BASE):
    """
    Dialog to add and edit entities
    """

    def __init__(self, **kwargs):
        """
        :param parent: Owner of this dialog
        :param profile : current profile
        :param entity : current entity
        :param in_db : Boolean flag to check if entity exist in database
        """
        self.form_parent = kwargs.get('parent', self)
        self.profile = kwargs.get('profile', None)
        self.entity = kwargs.get('entity', None)
        self.in_db = kwargs.get('in_db', False)

        QDialog.__init__(self, self.form_parent)
        self.setupUi(self)
        self.notice_bar = NotificationBar(self.notif_bar)
        self.init_gui_controls()

    def init_gui_controls(self):
        self.edtTable.setFocus()
        self.setTabOrder(self.edtTable, self.edtDesc)
        if self.entity:
            self.edtTable.setText(self.entity.short_name)
            self.edtDesc.setText(self.entity.description)
            self.txt_display_name.setText(self.entity.label)

            self.cbSupportDoc.setCheckState(
                self.bool_to_check(self.entity.supports_documents)
            )

            if self.entity.supports_documents and self.supporting_document_exists():
                self.cbSupportDoc.setEnabled(False)

        self.edtTable.textChanged.connect(self.validate_text)
        self.edtTable.setEnabled(not self.in_db)

    def supporting_document_exists(self):
        sd_name = '{0}_{1}_{2}'.format(self.profile.prefix,
                                       self.entity.short_name.lower(), 'supporting_document')
        return pg_table_exists(sd_name)

    def show_notification(self, message):
        """
        Shows a warning notification bar message.
        :param message: The message of the notification.
        :type message: String
        """

        self.notice_bar.clear()
        self.notice_bar.insertErrorNotification(message)

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

        name_regex = QRegExp('^(?=.{0,40}$)[ _a-zA-Z][a-zA-Z0-9_ ]*$')
        name_validator = QRegExpValidator(name_regex)
        text_edit.setValidator(name_validator)
        QApplication.processEvents()
        last_character = text[-1:]
        state = name_validator.validate(text, text.index(last_character))[0]
        msg = QApplication.translate(
            'EntityEditor', 'is not allowed at this position.'
        )

        if state != QValidator.Acceptable:
            self.show_notification('"{}" {}'.format(last_character, msg))
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

    def bool_to_check(self, state):
        """
        Returns a check state given a boolean value
        :param state : Boolean value
        :type state: Boolean
        """
        if state:
            return Qt.Checked
        else:
            return Qt.Unchecked

    def accept(self):
        if self.edtTable.text() == '' or self.edtTable.text() == ' ':
            self.show_message(self.tr("Please enter a valid entity name."))
            return

        sn = str(self.edtTable.text().strip())
        short_name = sn[0].upper() + sn[1:]

        if self.entity is None:  # New entity
            if self.duplicate_check(short_name):
                self.show_message(
                    self.tr(
                        "Entity with the same name already "
                        "exist in the current profile!"
                    )
                )
                return
            else:
                self.add_entity(short_name)
                self.done(0)
        else:
            self.edit_entity(short_name)
            self.done(1)

    def add_entity(self, short_name):
        """
        Creates and adds a new entity to a profile
        :param entity_name: name of the new entity
        :type entity_name: str
        """
        self.entity = self._create_entity(short_name)
        self.profile.add_entity(self.entity)
        # return True

    def _create_entity(self, short_name):
        entity = self.profile.create_entity(short_name, entity_factory,
                                            supports_documents=self.support_doc())
        entity.description = self.edtDesc.text()
        entity.label = self.txt_display_name.text()
        entity.column_added.connect(self.form_parent.add_column_item)
        entity.column_removed.connect(self.form_parent.delete_column_item)

        return entity

    def edit_entity(self, short_name):
        # remove old entity
        old_short_name = self.entity.short_name

        if old_short_name != short_name:
            status = self.profile.rename(old_short_name, short_name)
            self.entity.short_name = short_name

        self.entity.description = self.edtDesc.text()
        self.entity.label = self.txt_display_name.text()
        self.entity.supports_documents = self.support_doc()

    def duplicate_check(self, name):
        """
        Return True if we have an entity in the current profile with same 'name'
        :param name: entity short_name
        :type name: str
        """
        return name in self.profile.entities

    def support_doc(self):
        """
        Return boolean value representing the check state of supporting
        document checkbox
        """
        values = [False, None, True]
        cs = values[self.cbSupportDoc.checkState()]
        return cs

    def format_internal_name(self, short_name):
        """
        Returns a table name used internally by the entity
        :param short_name: Entity name entered by user
        :type short_name: str
        :rtype: str
        """
        name = str(short_name).strip()
        name = name.replace(' ', "_")
        name = name.lower()
        # Ensure prefix is not duplicated in the names
        prfx = self.profile.prefix
        prefix_idx = name.find(prfx, 0, len(prfx))

        # If there is no prefix then append
        if prefix_idx == -1:
            name = '{0}_{1}'.format(self.profile.prefix, name)

        return name

    def reject(self):
        self.done(0)

    def show_message(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("STDM")
        msg.setText(message)
        msg.exec_()
