"""
/***************************************************************************
Name                 : DBProfileBackupDialog
Description          : Dialog for doing profile and database backup
Date                 : 01/10/2022
copyright            : (C) 2022 by UN-Habitat and implementing partners.
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
import os
import sys
import shutil
import json
from zipfile import ZipFile

import subprocess
from subprocess import Popen

from qgis.PyQt import uic

from qgis.PyQt.QtWidgets import (
        QDialog,
        QMessageBox,
        QFileDialog,
        QLineEdit,
        QTreeWidgetItem
)

from qgis.PyQt.QtCore import (
        Qt,
        QDir,
        QDateTime,
        QCoreApplication
)

from qgis.gui import QgsGui

from stdm.ui.gui_utils import GuiUtils
from stdm.data.config import DatabaseConfig
from stdm.data.configuration.stdm_configuration import StdmConfiguration
from stdm.data.configuration.entity import Entity
from stdm.data.connection import DatabaseConnection
from stdm.data.configuration.profile import Profile
from stdm.security.user import User
from stdm.composer.document_template import DocumentTemplate

from stdm.ui.config_backup_handler import ConfigBackupHandler

from stdm.settings.registryconfig import RegistryConfig

WIDGET, BASE = uic.loadUiType(
        GuiUtils.get_ui_file_path('ui_db_profile_backup.ui'))

PG_ADMIN = 'postgres'

class DBProfileBackupDialog(WIDGET, BASE):
    total_backup_steps = 6
    def __init__(self, iface):
        QDialog.__init__(self, iface.mainWindow())
        self.setupUi(self)
        self.iface = iface

        reg_config = RegistryConfig()
        settings = reg_config.read(['Host', 'Database', 'Port'])
        self.db_config  = DatabaseConfig(settings)

        l_mode = reg_config.read(['LogMode'])
        self.backup_handler = ConfigBackupHandler(log_mode=l_mode['LogMode'])

        self.tbBackupFolder.clicked.connect(self.backup_folder_clicked)
        self.btnBackup.clicked.connect(self.do_backup)

        self.btnClose.clicked.connect(self.close_dialog)
        self.backup_handler.update_status.connect(self.update_status)

        self.db_conn = self.db_config.read() 
        self.txtDBName.setText(self.db_conn.Database)
        self.txtAdmin.setText(PG_ADMIN)
        self.lblStatus.setText('')
        self.edtBackupFolder.setEnabled(False)
        self.pbStatus.setAlignment(Qt.AlignCenter)

        self.config_templates = []

        self.twProfiles.setColumnCount(1)
        self.build_profiles_tree()

    def build_profiles_tree(self):
        for profile in self.backup_handler.profiles():
            profile_item = QTreeWidgetItem()
            profile_item.setText(0, profile.key.capitalize())
            profile_item.setIcon(0, GuiUtils.get_icon("folder.png"))

            entity_node = QTreeWidgetItem()
            entity_node.setText(0, "Entities")
            profile_item.addChild(entity_node)

            entity_items =  self._entity_items(self._profile_entities(profile))
            entity_node.addChildren(entity_items)

            template_node = QTreeWidgetItem()
            template_node.setText(0, "Templates")
            profile_item.addChild(template_node)
            
            profile_templates, count = self.backup_handler.profile_templates(profile)

            if len(profile_templates) > 0:
                templates = self._template_items(list(profile_templates.values())[0])
                template_node.addChildren(templates)

            # self.config_templates.append(profile_templates)

            self.twProfiles.insertTopLevelItem(0, profile_item)

    def _profile_entities(self, profile: Profile) ->list[Entity]:
        entities = []
        for entity in profile.entities.values():
            if not entity.user_editable:
                continue
            entities.append(entity)
        return entities

    def _entity_items(self, entities: list[Entity]) ->list[QTreeWidgetItem]:
        entity_items = []
        for entity in entities:
            entity_item = QTreeWidgetItem()
            entity_item.setText(0, entity.short_name)
            entity_item.setIcon(0, GuiUtils.get_icon("Table02.png"))
            entity_items.append(entity_item)
        return entity_items

    def _template_items(self, templates: list[tuple[str, str]]) ->list[QTreeWidgetItem]:
        template_items = []
        TEMPLATE_NAME = 0
        for template in templates:
            template_item = QTreeWidgetItem()
            template_item.setText(0, template[TEMPLATE_NAME])
            template_item.setIcon(0, GuiUtils.get_icon("record02.png"))
            template_items.append(template_item)

        return template_items

    def backup_folder_clicked(self):
        self._set_selected_directory(self.edtBackupFolder, 
                self.tr('Configuration file and DB backup folder')
            )

    def _set_selected_directory(self, txt_box: QLineEdit, title: str):
        def_path = txt_box.text()
        sel_doc_path = QFileDialog.getExistingDirectory(self, title, def_path)
        if sel_doc_path:
            normalized_path = f"{QDir.fromNativeSeparators(sel_doc_path)}/{self.db_conn.Database}_{self._dtime_str()}"
            txt_box.clear()
            txt_box.setText(normalized_path)

    def do_backup(self):
        if self.edtAdminPassword.text() == '':
            msg = f"Please enter password for user `{PG_ADMIN}`"
            self.show_message(msg, QMessageBox.Critical)
            return False

        if self.edtBackupFolder.text() == '':
            msg = self.tr('Please select a backup folder')
            self.show_message(msg, QMessageBox.Critical)
            return False

        backup_mode = 'FLAT-FILE'
        if self.cbCompress.isChecked():
            backup_mode = 'ZIP-FILE'

        self.btnBackup.setEnabled(False)

        backup_result, msg = self.backup_handler.do_configuration_backup(
            PG_ADMIN,
            self.edtAdminPassword.text(),
            self.edtBackupFolder.text(),
            backup_mode)

        self.btnBackup.setEnabled(True)

        if not backup_result:
            self.show_message(msg, QMessageBox.Critical)
            return False

        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(self.tr('Backup completed successfully.'))
        msg_box.setInformativeText(self.tr('Would you like to open the backup folder?'))
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.Close)

        yes_btn = msg_box.button(QMessageBox.Yes)
        no_btn = msg_box.button(QMessageBox.No)

        msg_box.exec_()
        if msg_box.clickedButton() == yes_btn:
            self.open_backup_folder()
            self.close_dialog()

        if msg_box.clickedButton() == no_btn:
            self.close_dialog()


    def open_backup_folder(self):
        backup_folder = self.edtBackupFolder.text()

        # windows
        if sys.platform.startswith('win32'):
            os.startfile(backup_folder)

        # *nix systems
        if sys.platform.startswith('linux'):
            subprocess.Popen(['xdg-open', backup_folder])

        # macOS
        if sys.platform.startswith('darwin'):
            subprocess.Popen(['open', backup_folder])

    def _dtime_str(self):
        return QDateTime.currentDateTime().toString('ddMMyyyyHHmm')

    def show_message(self, msg:str, icon_type):
        msg_box = QMessageBox()
        msg_box.setText(msg)
        msg_box.setIcon(icon_type)
        msg_box.exec_()

    def update_status(self, msg: str, step: int):
       percent = ((step + 1)/(self.total_backup_steps))*100 
       self.pbStatus.setValue(percent)
       self.lblStatus.setText(msg)

    def close_dialog(self):
        self.done(0)

