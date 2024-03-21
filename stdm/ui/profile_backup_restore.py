"""
/***************************************************************************
Name                 : ProfileBackupRestoreDialog
Description          : Dialog for doing restoring profile backup
Date                 : 01/05/2023
copyright            : (C) 2023 by UN-Habitat and implementing partners.
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
import shutil
import glob
import json
from zipfile import ZipFile

from qgis.PyQt.QtCore import(
     Qt,
     QFile,
     QDir,
     QTime
)

from qgis.PyQt import uic

from qgis.PyQt.QtWidgets import (
    QDialog,
    QFileDialog,
    QTreeWidgetItem,
    QMessageBox
)

from stdm.ui.gui_utils import GuiUtils
from stdm.data.configuration.stdm_configuration import StdmConfiguration
from stdm.data.configuration.profile import Profile
from stdm.data.connection import DatabaseConnection
from stdm.security.user import User

from stdm.ui.backup_restore_handler import BackupRestoreHandler

from stdm.utils.util import (
    PLUGIN_DIR
)
from stdm.settings.registryconfig import (
    RegistryConfig,
    COMPOSER_TEMPLATE
)

WIDGET, BASE = uic.loadUiType(
    GuiUtils.get_ui_file_path('ui_profile_backup_restore.ui')
)

class ProfileBackupRestoreDialog(WIDGET, BASE):
    total_restore_steps = 8
    def __init__(self, iface):
        QDialog.__init__(self, iface.mainWindow())
        self.setupUi(self)
        self.setWindowTitle("Restore Backup")
        self.iface = iface
        self.backup_info_file = ""

        reg_config = RegistryConfig()
        l_mode = reg_config.read(['LogMode'])
        self.backup_restore_handler = BackupRestoreHandler(log_mode=l_mode['LogMode'])

        self.connect_signals()
        self.initialize_ui_controls()

    def initialize_ui_controls(self):
        self.rbBackupFolder.setChecked(True)
        self.lblLogFile.setText("")
        self.edtDBName.setText("")
        self.lblDBAdmin.setText("postgres")
        self.edtPassword.setText("")
        self.edtBackupMedia.setEnabled(False)
        self.btnRestore.setEnabled(False)
        self.lblBackupFile.setText("")
        self.lblDateCreated.setText("")
        self.lblStatus.setText("")
        self.pbStatus.setAlignment(Qt.AlignCenter)

    def connect_signals(self):
        self.tbBackupFolder.clicked.connect(self.open_backup_media)
        self.btnClose.clicked.connect(self.close_window)
        self.btnRestore.clicked.connect(self.restore_backup)
        self.rbBackupFolder.toggled.connect(self.folder_selected)
        self.rbZipFile.toggled.connect(self.zip_selected)
        self.backup_restore_handler.update_status.connect(self.update_status)

    def close_window(self):
        self.done(0)

    def open_backup_media(self) ->str:
        if self.rbBackupFolder.isChecked():
            self._open_backup_folder()
        
        if self.rbZipFile.isChecked():
            self._open_zipfile()

    def _open_backup_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Backup Folder", "")
        if not folder:
            return

        self.edtBackupMedia.setText(folder)

        # find backup log file
        backup_folder = os.path.join(folder, '*.json')
        json_files = glob.glob(backup_folder)

        if len(json_files) == 0:
            msg = self.tr("Invalid backup folder! Backup info file missing.")
            self.show_popup_message(msg, QMessageBox.Critical)
            return

        self.backup_info_file = json_files[0]
        
        if self.backup_restore_handler.read_backup_info_file(self.backup_info_file):
            self.show_backup_info()
            self.btnRestore.setEnabled(True)
        else:
            msg = self.tr("Error reading backup info file. Check log file for details.")
            self.show_popup_message(msg, QMessageBox.Critical)

    def show_backup_info(self):
        self.edtDBName.setText(self.backup_restore_handler.db_name)
        self.lblBackupFile.setText(self.backup_restore_handler.db_backup_file)
        self.lblDateCreated.setText(self.backup_restore_handler.backup_date)
        self.lblLogFile.setText(os.path.basename(self.backup_restore_handler.backup_info_file))
        # self.lblStatus.setText(self.backup_restore_handler.backup_info_file)

        self._display_profiles(self.backup_restore_handler.profiles)

    def _display_profiles(self, profiles:list):
        self.twProfiles.clear()
        for profile in profiles:
            profile_item = QTreeWidgetItem()
            profile_item.setText(0, profile['name'])
            profile_item.setIcon(0, GuiUtils.get_icon("folder.png"))

            entity_node = QTreeWidgetItem()
            entity_node.setText(0, "Entities")
            profile_item.addChild(entity_node)
            entity_node.addChildren(self._entity_items(profile['entities']))
            
            templates = self._template_items(profile['templates'])
            if len(templates) > 0:
                template_node = QTreeWidgetItem()
                template_node.setText(0, "Templates")
                profile_item.addChild(template_node)
                template_node.addChildren(templates)

            self.twProfiles.insertTopLevelItem(0, profile_item)

    def _entity_items(self, entities: list[str]) -> list[QTreeWidgetItem]:
        entity_items = []
        for entity in entities:
            entity_item = QTreeWidgetItem()
            entity_item.setText(0, entity)
            entity_item.setIcon(0, GuiUtils.get_icon("Table02.png"))
            entity_items.append(entity_item)
        return entity_items

    def _template_items(self, templates: list[str]) ->list[QTreeWidgetItem]:
        template_items = []
        for template in templates:
            template_item = QTreeWidgetItem()
            template_item.setText(0, template)
            template_item.setIcon(0, GuiUtils.get_icon("record02.png"))
            template_items.append(template_item)
        return template_items

    def folder_selected(self, is_selected: bool):
        if is_selected:
            self.lblMedia.setText('Folder: ')

    def zip_selected(self, is_selected: bool):
        if is_selected:
            self.lblMedia.setText('Zip File: ')

    def _open_zipfile(self):
        filename = QFileDialog.getOpenFileName(self, self.tr("Open Zip File"),
                                               "", self.tr("Zip File (*.zip)" ))
        if filename[0] == '':
            return

        zip_filepath = filename[0]

        self.edtBackupMedia.setText(zip_filepath)
        # STEP 0: Decompress the Zip File

        # Make name for the temp folder
        base_filename = os.path.basename(zip_filepath).split('.')[0]
        hr = QTime.currentTime().hour()
        min = QTime.currentTime().minute()
        sec = QTime.currentTime().second()

        temp_base_folder_name =f'stdm_{base_filename}_{hr}{min}{sec}'
        temp_dir_path = f'{QDir.tempPath()}/{temp_base_folder_name}'
        temp_dir = QDir(temp_dir_path)
        if temp_dir.exists():
            shutil.rmtree(temp_dir_path)
        temp_dir.mkpath(temp_dir_path)

        with ZipFile(zip_filepath) as zf:
             zf.extractall(temp_dir_path)

        # find backup instruction file
        backup_folder = os.path.join(temp_dir_path, '*.json')

        json_files = glob.glob(backup_folder)

        if len(json_files) == 0:
            msg = self.tr("Invalid backup folder! Backup info file missing.")
            self.show_popup_message(msg, QMessageBox.Critical)
            return

        self.backup_info_file = json_files[0]

        if self.backup_restore_handler.read_backup_info_file(self.backup_info_file):
            self.show_backup_info()
            self.btnRestore.setEnabled(True)
        else:
            msg = self.tr("Error reading backup info file. Check log file for details.")
            self.show_popup_message(msg, QMessageBox.Critical)

    def restore_backup(self):
        if self.edtPassword.text() == '':
            msg = self.tr('Please enter password for user `postgres` ')
            self.show_popup_message(msg, QMessageBox.Critical)
            return 

        if self.edtDBName.text() == '':
            msg = self.tr('Please enter database name.')
            self.show_popup_message(msg, QMessageBox.Critical)
            return

        db_name = self.edtDBName.text()
        if len(db_name) < 4:
            msg = self.tr('Database name should be greater than four characters!')
            self.show_popup_message(msg, QMessageBox.Critical)
            return

        self.btnRestore.setEnabled(False)
        msg, status = self.backup_restore_handler.restore_backup('postgres',
                                                                 self.edtPassword.text(),
                                                                 self.edtDBName.text().lower())
        self.btnRestore.setEnabled(True)

        if not status:
            self.show_popup_message(msg, QMessageBox.Critical)
        else:
            print(msg)

    def show_popup_message(self, msg: str, icon_type):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("STDM")
        msg_box.setText(msg)
        msg_box.setIcon(icon_type)
        msg_box.exec_()

    def update_status(self, msg: str, step: int):
        percent = ((step + 1)/(self.total_restore_steps))*100
        self.pbStatus.setValue(percent)
        self.lblStatus.setText(msg)
