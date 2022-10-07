"""
"""
import os
import sys
import shutil
import subprocess
import json
from zipfile import ZipFile

from PyQt4.QtGui import (
        QDialog,
        QMessageBox,
        QFileDialog
)

from PyQt4.QtCore import (
        Qt,
        QDir,
        QDateTime
)

from stdm.data.config import DatabaseConfig
from stdm.data.configuration.stdm_configuration import StdmConfiguration
from stdm.data.connection import DatabaseConnection

from stdm.ui.ui_db_profile_backup import Ui_dlgDBProfileBackup
from stdm.utils.util import PLUGIN_DIR 

class StreamHandler:
    def log(self, msg):
        raise NotImplementedError

class StdOutHandler(StreamHandler):
    def log(self, msg):
        print(msg)

class FileHandler(StreamHandler):
    def __init__(self, msg):
        dtime = QDateTime.currentDataTime().toString('ddMMyyyy_HH.mm')
        filename ='/.stdm/logs/template_converter_{}.log'.format(dtime)
        self.log_file = '{}{}'.format(QDir.home().path(),  filename)

    def log(self, msg):
        with open(self.log_file, 'a') as lf:
            lf.write(msg)
            lf.write('\n')

class MessageLogger:
    def __init__(self, handler=StdOutHandler):
        self.stream_handler =  handler()

    def log_error(self, msg):
        log_msg = 'ERROR: {}'.format(msg)
        self.stream_handler.log(log_msg)

    def log_info(self, msg):
        log_msg = 'INFO: {}'.format(msg)
        self.stream_handler.log(log_msg)


class DBProfileBackupDialog(QDialog, Ui_dlgDBProfileBackup):
    """
    """
    def __init__(self, iface):
        QDialog.__init__(self, iface.mainWindow())
        self.setupUi(self)
        self.iface = iface

        self.tbBackupFolder.clicked.connect(self.backup_folder_clicked)
        self.btnBackup.clicked.connect(self.do_backup)
        self.btnOpenFolder.clicked.connect(self.open_backup_folder)
        self.btnClose.clicked.connect(self.close_dialog)

        self.btnOpenFolder.setEnabled(False)
        self.edtBackupFolder.textChanged.connect(self.folder_backup_changed)

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

    def _set_selected_directory(self, txt_box, title):
        def_path = txt_box.text()
        sel_doc_path = QFileDialog.getExistingDirectory(self, title, def_path)

        if sel_doc_path:
            normalized_path = QDir.fromNativeSeparators(sel_doc_path)
            txt_box.clear()
            txt_box.setText(normalized_path)

    def do_backup(self):
        if self.edtAdminPassword.text() == '':
            msg = self.tr('Please enter password for user `postgres`')
            self.show_message(msg)
            return False

        if self.edtBackupFolder.text() == '':
            msg = self.tr('Please select a backup folder')
            self.show_message(msg)
            return False

        db_con = DatabaseConnection(self.conn_prop.Host, self.conn_prop.Port,
                self.conn_prop.Database, 'postgres', self.edtAdminPassword.text())

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
            
            self.show_message('Backup completed successfully.')

    def folder_backup_changed(self, text):
        self.btnOpenFolder.setEnabled(False if self.edtBackupFolder.text() == '' else True)

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

    def _make_backup_filename(self, database_name):
        date_str = QDateTime.currentDateTime().toString('ddMMyyyyHHmm')
        backup_file = '{}{}{}{}'.format(database_name, '_', date_str,'.backup')
        return backup_file

    def backup_database(self, database, user, password, backup_filepath):
        backup_script = PLUGIN_DIR + '/scripts/dbbackup.bat {} {} {} {} {}'.format(
                database.Database, database.Host, database.Port, user,
                backup_filepath)
        #os.system(backup_script)
        try:
            subprocess.check_call(backup_script)
        except subprocess.CallProcessError:
            self.log_error('DB Backup Failed!')
            return False

        return True


    def backup_config_file(self, config_filepath, backup_filepath):
        shutil.copyfile(config_filepath, backup_filepath)

    def compress_backup(self, compressed_filename, backup_folder, files):
        """
        type files: list
        """
        dtime =QDateTime.currentDateTime().toString('ddMMyyyyHHmm')
        zip_filepath = '{}{}{}{}{}{}'.format(backup_folder, '/', 
                compressed_filename, '_',dtime,'.zip')

        print zip_filepath

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

    def _make_log(self, profiles, db_name, db_backup_filename, log_dtime,
            is_compressed):

        backup_log = {'configuration':{'filename':'configuration.stc',
                                       'profiles':profiles,
               'database':{'name':db_name,
                           'backup':db_backup_filename},
               'created_on':log_dtime,
               'compressed':is_compressed
              }}

        return backup_log

    def create_backup_log(self, log, log_file):
        with open(log_file, 'w') as lf:
            json.dump(log, lf, indent=4)

    def write_zip_file(self, file_list, zip_file):
        with ZipFile(zip_file, 'w') as zf:
            for file in file_list:
                zf.write(file)

    def show_message(self, msg):
        msg_box = QMessageBox()
        msg_box.setText(msg)
        msg_box.exec_()




