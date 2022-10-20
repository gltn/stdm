"""
/***************************************************************************
Name                 : DBProfileBackupDialog
Description          : Dialog for doing profile and database backup
Date                 : 01/10/2022
copyright            : (C) 2016 by UN-Habitat and implementing partners.
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
        QLineEdit
)

from qgis.PyQt.QtCore import (
        Qt,
        QDir,
        QDateTime
)

from qgis.gui import QgsGui

from stdm.ui.gui_utils import GuiUtils
from stdm.data.config import DatabaseConfig
from stdm.data.configuration.stdm_configuration import StdmConfiguration
from stdm.data.connection import DatabaseConnection
from stdm.security.user import User

from stdm.utils.util import PLUGIN_DIR 

class StreamHandler:
    def log(self, msg: str):
        raise NotImplementedError

class StdOutHandler(StreamHandler):
    def log(self, msg: str):
        print(msg)

class FileHandler(StreamHandler):
    def __init__(self, msg: str):
        dtime = QDateTime.currentDataTime().toString('ddMMyyyy_HH.mm')
        filename ='/.stdm/logs/template_converter_{}.log'.format(dtime)
        self.log_file = '{}{}'.format(QDir.home().path(),  filename)

    def log(self, msg: str):
        with open(self.log_file, 'a') as lf:
            lf.write(msg)
            lf.write('\n')

class MessageLogger:
    def __init__(self, handler:StreamHandler=StdOutHandler):
        self.stream_handler =  handler()

    def log_error(self, msg: str):
        log_msg = 'ERROR: {}'.format(msg)
        self.stream_handler.log(log_msg)

    def log_info(self, msg: str):
        log_msg = 'INFO: {}'.format(msg)
        self.stream_handler.log(log_msg)

WIDGET, BASE = uic.loadUiType(
        GuiUtils.get_ui_file_path('ui_db_profile_backup.ui'))

class DBProfileBackupDialog(WIDGET, BASE):
    def __init__(self, iface):
        QDialog.__init__(self, iface.mainWindow())
        self.setupUi(self)
        self.iface = iface

        self.tbBackupFolder.clicked.connect(self.backup_folder_clicked)
        self.btnBackup.clicked.connect(self.do_backup)
        self.btnClose.clicked.connect(self.close_dialog)

        self.db_config = DatabaseConfig();

        self.conn_prop = self.db_config.read()
        self.txtDBName.setText(self.conn_prop.Database)
        self.txtAdmin.setText('postgres')
        self.stdm_config = StdmConfiguration.instance()
        self.load_profiles()

        self.msg_logger = MessageLogger(StdOutHandler)

    def load_profiles(self):
        profiles = self.stdm_config.profiles.keys()
        self.lwProfiles.addItems(profiles)

    def backup_folder_clicked(self):
        self._set_selected_directory(self.edtBackupFolder, 
                self.tr('Configuration file and DB backup folder')
            )

    def _set_selected_directory(self, txt_box: QLineEdit, title: str):
        def_path = txt_box.text()
        sel_doc_path = QFileDialog.getExistingDirectory(self, title, def_path)

        if sel_doc_path:
            normalized_path = QDir.fromNativeSeparators(sel_doc_path)
            txt_box.clear()
            txt_box.setText(normalized_path)

    def do_backup(self):
        if self.edtAdminPassword.text() == '':
            msg = self.tr('Please enter password for user `postgres`')
            self.show_message(msg, QMessageBox.Critical)
            return False

        if self.edtBackupFolder.text() == '':
            msg = self.tr('Please select a backup folder')
            self.show_message(msg, QMessageBox.Critical)
            return False

        db_con = DatabaseConnection(self.conn_prop.Host, self.conn_prop.Port,
                self.conn_prop.Database)

        user = User('postgres', self.edtAdminPassword.text())
        db_con.User = user

        validity, msg = db_con.validateConnection()

        if validity == False:
            error_type = self.tr('Authentication Failed!')
            error_msg = '{}: `{}`'.format(error_type, msg)
            QMessageBox.critical(self, self.tr('BackupDialog', error_type),
                    error_msg)

            self.msg_logger.log_error(error_msg)
            return False

        db_name = self.conn_prop.Database
        db_backup_filename = self._make_backup_filename(db_name)

        db_backup_filepath ='{}{}{}'.format(self.edtBackupFolder.text(),
                '/', db_backup_filename)

        if self.backup_database(self.conn_prop, 'postgres',
                self.edtAdminPassword.text(), db_backup_filepath):

            config_filepath = QDir.home().path()+ '/.stdm/configuration.stc'
            config_backup_filepath = self.edtBackupFolder.text()+'/configuration.stc'

            self.backup_config_file(config_filepath, config_backup_filepath)

            log_dtime = self._dtime()
            log_filename = 'backuplog_{}{}'.format(log_dtime,'.json')
            log_filepath = '{}{}{}'.format(self.edtBackupFolder.text(), '/', log_filename)

            backup_log = self._make_log(self.stdm_config.profiles.keys(), db_name,
                    db_backup_filename, log_dtime, self.cbCompress.isChecked())

            self.create_backup_log(backup_log, log_filepath)

            if self.cbCompress.isChecked():
                if self.compress_backup(db_name, self.edtBackupFolder.text(),
                        [db_backup_filepath, config_backup_filepath, log_filepath]):

                    compressed_files  = []
                    compressed_files.append(db_backup_filepath)
                    compressed_files.append(config_backup_filepath)
                    compressed_files.append(log_filepath)

                    self._remove_compressed_files(compressed_files)
            
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setText(self.tr('Backup completed successfully.'))
            msg_box.setInformativeText(self.tr('Do you want to open the backup folder?'))
            msg_box.setStandardButtons(QMessageBox.Save | QMessageBox.Close)
            msg_box.setDefaultButton(QMessageBox.Close)
            save_btn = msg_box.button(QMessageBox.Save)
            save_btn.setText('Open Backup Folder')
            close_btn = msg_box.button(QMessageBox.Close)

            msg_box.exec_()
            if msg_box.clickedButton() == save_btn:
                self.open_backup_folder()
            if msg_box.clickedButton() == close_btn:
                self.close_dialog()

    def open_backup_folder(self):
        backup_folder = self.edtBackupFolder.text();

        # windows
        if sys.platform.startswith('win32'):
            os.startfile(backup_folder)

        # *nix systems
        if sys.platform.startswith('linux'):
            subprocess.Popen(['xdg-open', backup_folder])

        # macOS
        if sys.platform.startswith('darwin'):
            subprocess.Popen(['open', backup_folder])

    def close_dialog(self):
        self.done(0)

    def _make_backup_filename(self, database_name) -> str:
        date_str = QDateTime.currentDateTime().toString('ddMMyyyyHHmm')
        backup_file = '{}{}{}{}'.format(database_name, '_', date_str,'.backup')
        return backup_file

    def backup_database(self, database, user, password, backup_filepath) -> bool:
        script_name = PLUGIN_DIR + '/scripts/dbbackup.bat'

        startup_info = subprocess.STARTUPINFO()
        startup_info.dwFlags |=subprocess.STARTF_USESHOWWINDOW
        process = subprocess.Popen([script_name, database.Database, 
            database.Host, str(database.Port), user, backup_filepath], startupinfo=startup_info)

        stdout, stderr = process.communicate()
        process.wait()

        result_code = process.returncode

        return True if result_code == 0 else False


    def backup_config_file(self, config_filepath, backup_filepath):
        shutil.copyfile(config_filepath, backup_filepath)

    def compress_backup(self, compressed_filename, backup_folder, files) -> bool:
        """
        param: files
        type: list
        """
        dtime =QDateTime.currentDateTime().toString('ddMMyyyyHHmm')
        zip_filepath = '{}{}{}{}{}{}'.format(backup_folder, '/', 
                compressed_filename, '_',dtime,'.zip')

        try:
            self.write_zip_file(files, zip_filepath)
        except BadZipfile:
            self.log_error('Failed to compress backup!')
            return False
        return True

    def _remove_compressed_files(self, files):
        for file in files:
            if os.path.isfile(file):
                os.remove(file)


    def _dtime(self):
        return QDateTime.currentDateTime().toString('dd-MM-yyyy HH.mm')

    def _make_log(self, profiles: list, db_name: str, db_backup_filename: str,
            log_dtime: str, is_compressed: bool) -> dict:

        backup_log = {'configuration':{'filename':'configuration.stc',
                                       'profiles':profiles,
               'database':{'name':db_name,
                           'backup':db_backup_filename},
               'created_on':log_dtime,
               'compressed':is_compressed
              }}

        return backup_log

    def create_backup_log(self, log: dict, log_file: str):
        with open(log_file, 'w') as lf:
            json.dump(list(log), lf, indent=4)

    def write_zip_file(self, file_list: list, zip_file: str):
        with ZipFile(zip_file, 'w') as zf:
            for file in file_list:
                zf.write(file)

    def show_message(self, msg: str, icon_type):
        msg_box = QMessageBox()
        msg_box.setText(msg)
        msg_box.setIcon(icon_type)
        msg_box.exec_()




