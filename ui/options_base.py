"""
/***************************************************************************
Name                 : Options Dialog
Description          : Container for editing STDM settings.
Date                 : 26/May/20146
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
import logging

from PyQt4.QtGui import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QIntValidator,
    QMessageBox,
    QApplication)
from PyQt4.QtCore import(
    Qt,
    QDir,
    QTimer,
    SIGNAL
)

from stdm.data.configuration.stdm_configuration import StdmConfiguration
from stdm.data.config import DatabaseConfig
from stdm.data.connection import DatabaseConnection
from stdm.settings import (
    current_profile,
    save_configuration,
    save_current_profile,
    get_entity_browser_record_limit,
    save_entity_browser_record_limit,
    get_primary_mapfile,
    save_import_mapfile,
)

from stdm.settings.registryconfig import (
    composer_output_path,
    composer_template_path,
    config_file_name,
    BACKUP_PATH,
    backup_path,
    PG_BIN_PATH,
    pg_bin_path,

    AUTOBACKUP_DATE,
    autobackup_date,
    AUTOBACKUP_NEXT,
    autobackup_next,
    AUTOBACKUP_KEY,
    autobackup_key,


    debug_logging,
    set_debug_logging,
    source_documents_path,
    QGISRegistryConfig,
    RegistryConfig,
    COMPOSER_OUTPUT,
    COMPOSER_TEMPLATE,
    NETWORK_DOC_RESOURCE,
    CONFIG_UPDATED,
    WIZARD_RUN
)

from stdm.utils.util import setComboCurrentIndexWithText, version_from_metadata
from stdm.ui.login_dlg import loginDlg
from stdm.ui.notification import NotificationBar
from stdm.ui.customcontrols.validating_line_edit import INVALIDATESTYLESHEET
from stdm.ui.ui_options import Ui_DlgOptions

#to be moved later to seperate window - start

from datetime import (
    datetime,
    timedelta
)
from stdm.data.backup_utils import (
    backup_config,
    backup_database,
    AUTOBACKUP_KEYS
)    
from stdm.data.stdm_reqs_sy_ir import autochange_profile_configfile

from datetime import datetime

import gzip
import os
import shutil
import subprocess

#to be moved later to seperate window - end

MAX_LIMIT = 500 # Maximum records in a entity browser

def pg_profile_names():
    """/
    :return: List containing tuple of PostgreSQL database connection names
    and full path stored by QGIS.
    :rtype: list
    """
    pg_connection_path = "/PostgreSQL/connections"
    q_config = QGISRegistryConfig(pg_connection_path)

    pg_connections = q_config.group_children()

    profiles = [(conn_name, u"{0}/{1}".format(pg_connection_path, conn_name))
                for conn_name in pg_connections]

    return profiles

class OptionsDialog(QDialog, Ui_DlgOptions):
    """
    Dialog for editing STDM settings.
    """
    def __init__(self, iface):
        QDialog.__init__(self, iface.mainWindow())
        self.setupUi(self)
        self.iface = iface

        self.notif_bar = NotificationBar(self.vlNotification, 6000)
        self._apply_btn = self.buttonBox.button(QDialogButtonBox.Apply)
        self._reg_config = RegistryConfig()
        self._db_config = DatabaseConfig()

        #version = version_from_metadata()
        #upgrade_label_text = self.label_9.text().replace('1.4', version)
        #self.label_9.setText(upgrade_label_text)

        #Connect signals
        self._apply_btn.clicked.connect(self.apply_settings)
        self.buttonBox.accepted.connect(self.on_accept)
        self.chk_pg_connections.toggled.connect(self._on_use_pg_connections)
        self.cbo_pg_connections.currentIndexChanged.connect(
            self._on_pg_profile_changed)
        self.btn_db_conn_clear.clicked.connect(self.clear_properties)
        self.btn_test_db_connection.clicked.connect(self._on_test_connection)
        self.btn_supporting_docs.clicked.connect(
            self._on_choose_supporting_docs_path
        )
        self.btn_backup.clicked.connect(
            self._on_run_backup
        )
        self.btn_backup_folder.clicked.connect(
            self._on_choose_backup_path
        )
        self.btn_pgbin_folder.clicked.connect(
            self._on_choose_pgbin_path
        )

        self.cbo_autobackup.currentIndexChanged.connect(
            self._on_autobackup_changed)


        self.btn_template_folder.clicked.connect(
            self._on_choose_doc_designer_template_path
        )
        self.btn_composer_out_folder.clicked.connect(
            self._on_choose_doc_generator_output_path
        )

        #self.upgradeButton.toggled.connect(
            #self.manage_upgrade
        #)

        self.upgradeButton.setVisible(False)

        self.btnMapfile.clicked.connect(self.on_set_mapfile)

        self._config = StdmConfiguration.instance()
        self._default_style_sheet = self.txtRepoLocation.styleSheet()

        self.manage_upgrade()

        self.init_gui()

    def init_gui(self):
        #Set integer validator for the port number
        int_validator = QIntValidator(1024, 49151)
        self.txtPort.setValidator(int_validator)

        #Load profiles
        self.load_profiles()

        #Set current profile in the combobox
        curr_profile = current_profile()
        if not curr_profile is None:
            setComboCurrentIndexWithText(self.cbo_profiles, curr_profile.name)

        #Load current database connection properties
        self._load_db_conn_properties()

        #Load existing PostgreSQL connections
        self._load_qgis_pg_connections()

        #Load directory paths
        self._load_directory_paths()

        self.edtEntityRecords.setMaximum(MAX_LIMIT)
        self.edtEntityRecords.setValue(get_entity_browser_record_limit())

        self.edtMapfile.setText(get_primary_mapfile())
        self.load_autoback_info()

    def load_profiles(self):
        """
        Load existing profiles into the combobox.
        """
        profile_names = self._config.profiles.keys()

        self.cbo_profiles.clear()
        self.cbo_profiles.addItem('')
        self.cbo_profiles.addItems(profile_names)

    def _load_db_conn_properties(self):
        #Load database connection properties from the registry.
        db_conn = self._db_config.read()

        if not db_conn is None:
            self.txtHost.setText(db_conn.Host)
            self.txtPort.setText(db_conn.Port)
            self.txtDatabase.setText(db_conn.Database)

    def _load_qgis_pg_connections(self):
        """
        Load QGIS postgres connections.
        """
        self.cbo_pg_connections.addItem('')

        profiles = pg_profile_names()
        for profile in profiles:
            self.cbo_pg_connections.addItem(profile[0], profile[1])

    def _load_directory_paths(self):
        #Load paths to various directory settings.
        comp_out_path = composer_output_path()
        comp_temp_path = composer_template_path()
        source_doc_path = source_documents_path()
        backup_out_path = backup_path()
        pgbin_path = pg_bin_path()

        if not source_doc_path is None:
            self.txtRepoLocation.setText(source_doc_path)

        if not comp_out_path is None:
            self.txt_output_dir.setText(comp_out_path)

        if not comp_temp_path is None:
            self.txt_template_dir.setText(comp_temp_path)

        if not backup_out_path is None:
            self.edt_backup_folder.setText(backup_out_path)

        if not pgbin_path is None:
            self.edt_pgbin_folder.setText(pgbin_path)

    def _on_use_pg_connections(self, state):
        #Slot raised when to (not) use existing pg connections
        if not state:
            self.cbo_pg_connections.setCurrentIndex(0)
            self.cbo_pg_connections.setEnabled(False)

            #Restore current connection in registry
            self._load_db_conn_properties()

        else:
            self.cbo_pg_connections.setEnabled(True)

    def _on_pg_profile_changed(self, index):
        """
        Slot raised when the index of the pg profile changes. If the
        selection is valid then the system will attempt to extract
        the database connection properties of the selected profile
        stored in the registry.
        """
        if index == 0:
            return

        profile_path = self.cbo_pg_connections.itemData(index)

        q_config = QGISRegistryConfig(profile_path)
        db_items = q_config.read(['Database', 'Host', 'Port'])

        if len(db_items) > 0:
            self.txtDatabase.setText(db_items['Database'])
            self.txtHost.setText(db_items['Host'])
            self.txtPort.setText(db_items['Port'])

    def clear_properties(self):
        """
        Clears the host, database name and port number values from the
        respective controls.
        """
        self.txtDatabase.clear()
        self.txtHost.clear()
        self.txtPort.clear()

    def _on_choose_supporting_docs_path(self):
        #Slot raised to select directory for supporting documents.
        self._set_selected_directory(self.txtRepoLocation, self.tr(
            'Supporting Documents Directory')
        )

    def _on_choose_doc_designer_template_path(self):
        #Slot raised to select directory for document designer templates.
        self._set_selected_directory(self.txt_template_dir, self.tr(
            'Document Designer Templates Directory')
        )

    #To move this part of code to new window later - start
    def _on_choose_backup_path(self):
        #Slot raised to select directory for backup.
        self._set_selected_directory(
            self.edt_backup_folder,
            self.tr('Backup Directory')
        )
    
    def _on_choose_pgbin_path(self):
        #Slot raised to select PostgreSQL/bin directory.
        self._set_selected_directory(
            self.edt_pgbin_folder,
            self.tr('PostgreSQL/bin Directory')
        )

    def _on_run_backup(self):


        #in case want to save multi backup files / different dates

        datetime_prfx = datetime.now().strftime('%Y%m%d%H%M%S%f_')
        config_file = config_file_name()
        if not os.path.exists(self.edt_pgbin_folder.text()):
            ErrMessage(
                self.tr('Can not find PostgreSQL/bin Directory')
            )
            return


        cmd_dump = self.edt_pgbin_folder.text() + '/pg_dump'

        if not self.txtHost.text():
            ErrMessage(
                self.tr('Please specify the database host address.')
            )
            return
        if not self.txtPort.text():
            ErrMessage(
                self.tr('Please specify the port number.')
            )
            return
        if not self.txtDatabase.text():
            ErrMessage(
                self.tr('Please specify the database name.')
            )
            return

        backup_config(  
            datetime_prfx, 
            config_file, 
            self.edt_backup_folder.text()
        )
        p_host = self.txtHost.text()
        p_port = self.txtPort.text()
        p_database = self.txtDatabase.text()
        backup_database(
            datetime_prfx,
            self.edt_pgbin_folder.text(),
            p_host,
            p_port,
            p_database,
            self.edt_backup_folder.text()
        )

    def set_autobackup_comment(self):
        txt = '<NOT SET>'
        combobox_txt = self.cbo_autobackup.currentText()
        if combobox_txt in ['Never', 'Each Login']: 
            pass
        else:
            abd = autobackup_date()
            abn = autobackup_next()
            if abd is None:
                abd = 'Last backup: <NOT SET>'
            if abn is None:
                if combobox_txt == 'Daily': 
                    abn = (datetime.now() + timedelta(days=1)).strftime('%d-%m-%Y')
                if combobox_txt == 'Weekly': 
                    abn = (datetime.now() + timedelta(days=7)).strftime('%d-%m-%Y')
                if combobox_txt == 'Monthly': 
                    abn = (datetime.now() + timedelta(days=30)).strftime('%d-%m-%Y')
            txt = '{}, Next Backup: <{}>'.format(
                abd, 
                abn
            )

        self.lbl_autobackup_comment.setText(txt)

    def load_autoback_info(self):
        self.cbo_autobackup.clear()
        self.cbo_autobackup.addItems(AUTOBACKUP_KEYS) 
        self.set_autobackup_comment()

    def load_autoback_info(self):
        self.cbo_autobackup.clear()
        self.cbo_autobackup.addItems(AUTOBACKUP_KEYS) 
        txt = autobackup_key()
        if not (txt is None):
            self.cbo_autobackup.setCurrentIndex(
                self.cbo_autobackup.findText(txt)
            )

    def set_autobackup_key(self):
        """
        Set the AutoBackup Parameters.
        :return: True if the key was set in the registry,
        otherwise False.
        :rtype: bool
        """
        key = self.cbo_autobackup.currentText()
        #Commit Key to registry
        self._reg_config.write({AUTOBACKUP_KEY: key})

        if key in ['Never', 'Each Login']:
            self._reg_config.write({AUTOBACKUP_NEXT: None})
            return True

        abn = autobackup_next()
        if not(abn is None):
            return True
        if key == 'Daily': 
            abn = (datetime.now() + timedelta(days=1)).strftime('%d-%m-%Y')
        if key == 'Weekly': 
            abn = (datetime.now() + timedelta(days=7)).strftime('%d-%m-%Y')
        if key == 'Monthly': 
            abn = (datetime.now() + timedelta(days=30)).strftime('%d-%m-%Y')

        if not (abn is None):
            #Commit Next AutoBackup Date to registry
            self._reg_config.write({AUTOBACKUP_NEXT: abn})
            return True

    def _on_autobackup_changed(self):
        self.set_autobackup_comment()

        p_host = self.txtHost.text()
        p_port = self.txtPort.text()
        p_database = self.txtDatabase.text()
        dest_db_filename = (self.edt_backup_folder.text()
                           + '//bkup_' 
                           + datetime_prfx 
                           + p_database 
                           + '.backup')
        dest_config_file = (self.edt_backup_folder.text()
                           + '//bkup_' 
                           + datetime_prfx 
                           + 'configuration.stc')

        if not os.path.exists(self.edt_backup_folder.text()):
            os.makedirs(self.edt_backup_folder.text())
        shutil.copy(config_file, dest_config_file)

        cmd = cmd_dump + ' -f {} -F c -h {} -U {} -p {} {}'.format(
            dest_db_filename,
            p_host,
            'postgres',
            p_port,
            p_database
        )
        
        with gzip.open(dest_db_filename, 'wb') as f:
            popen = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                universal_newlines=True
            )
        for stdout_line in iter(popen.stdout.readline, ''):
            f.write(stdout_line.encode('utf-8'))
        popen.stdout.close()
        popen.wait()
        popen = None

        self.set_backup_path()
        self.set_pgbin_path()

        return

    def set_backup_path(self):
        """
        Set the directory of backup output.
        :return: True if the directory was set in the registry,
        otherwise False.
        :rtype: bool
        """
        path = self.edt_backup_folder.text()

        if not path:
            msg = self.tr('Please set the backup output directory.')
            self.notif_bar.insertErrorNotification(msg)
            return False

        #Validate path
        if not self._check_path_exists(path, self.edt_backup_folder):
            return False

        #Commit to registry
        self._reg_config.write({BACKUP_PATH: path})
        return True

    def set_pgbin_path(self):
        """
        Set the PostgreSQl/bin directory.
        :return: True if the directory was set in the registry,
        otherwise False.
        :rtype: bool
        """
        path = self.edt_pgbin_folder.text()

        if not path:
            msg = self.tr('Please set the PostgreSQL/bin directory.')
            self.notif_bar.insertErrorNotification(msg)
            return False

        #Validate path
        if not self._check_path_exists(path, self.edt_pgbin_folder):
            return False

        #Commit to registry
        self._reg_config.write({PG_BIN_PATH: path})
        return True

# To move this part of code to new window later - end

    def _on_choose_doc_generator_output_path(self):
        #Slot raised to select directory for doc generator outputs.
        self._set_selected_directory(self.txt_output_dir, self.tr(
            'Document Generator Output Directory')
        )

    def on_set_mapfile(self):
        def_path = self.edtMapfile.text()
        title = self.tr("Import map file")
        mapfile = QFileDialog.getOpenFileName(self, title, def_path)
        if mapfile:
            self.edtMapfile.setText(mapfile)

    def _set_selected_directory(self, txt_box, title):
        def_path= txt_box.text()
        sel_doc_path = QFileDialog.getExistingDirectory(self, title, def_path)

        if sel_doc_path:
            normalized_path = QDir.fromNativeSeparators(sel_doc_path)
            txt_box.clear()
            txt_box.setText(normalized_path)

    def _validate_db_props(self):
        #Test if all properties have been specified
        status = True

        self.notif_bar.clear()

        if not self.txtHost.text():
            msg = self.tr('Please specify the database host address.')
            self.notif_bar.insertErrorNotification(msg)

            status = False

        if not self.txtPort.text():
            msg = self.tr('Please specify the port number.')
            self.notif_bar.insertErrorNotification(msg)

            status = False

        if not self.txtDatabase.text():
            msg = self.tr('Please specify the database name.')
            self.notif_bar.insertErrorNotification(msg)

            status = False

        return status

    def _database_connection(self):
        #Creates a databaase connection object from the specified args
        host = self.txtHost.text()
        port = self.txtPort.text()
        database = self.txtDatabase.text()

        #Create database connection object
        db_conn = DatabaseConnection(host, port, database)

        return db_conn

    def _on_test_connection(self):
        """
        Slot raised to test database connection.
        """
        status = self._validate_db_props()

        if not status:
            return

        login_dlg = loginDlg(self, True)
        db_conn = self._database_connection()
        login_dlg.set_database_connection(db_conn)

        res = login_dlg.exec_()
        if res == QDialog.Accepted:
            msg = self.tr(u"Connection to '{0}' database was "
                          "successful.".format(db_conn.Database))
            QMessageBox.information(self, self.tr('Database Connection'), msg)

    def autochange_profile_configfile(self, new_profilename):
        autochange_profile_configfile(
            new_profilename,
            current_profile().name
        )
            
    def set_current_profile(self):
        """
        Saves the given profile name as the current profile.
        """
        profile_name = self.cbo_profiles.currentText()

        if not profile_name:
            self.notif_bar.clear()

            msg = self.tr('Profile name is empty, current profile will not '
                          'be set.')
            self.notif_bar.insertErrorNotification(msg)

            return False

        self.autochange_profile_configfile(profile_name)
        save_current_profile(profile_name)

        return True

    def save_database_properties(self):
        """
        Saves the specified database connection properties to the registry.
        :return: True if the connection properties were successfully saved.
        :rtype: bool
        """
        if not self._validate_db_props():
            return False

        #Create a database object and write it to the registry
        db_conn = self._database_connection()
        self._db_config.write(db_conn)

        return True

    def set_supporting_documents_path(self):
        """
        Set the directory of supporting documents.
        :return: True if the directory was set in the registry, otherwise
        False.
        :rtype: bool
        """
        path = self.txtRepoLocation.text()

        if not path:
            msg = self.tr('Please set the supporting documents directory.')
            self.notif_bar.insertErrorNotification(msg)

            return False

        #Validate path
        if not self._check_path_exists(path, self.txtRepoLocation):
            return False

        #Commit to registry
        self._reg_config.write({NETWORK_DOC_RESOURCE: path})

        return True

    def set_document_templates_path(self):
        """
        Set the directory of document designer templates.
        :return: True if the directory was set in the registry, otherwise
        False.
        :rtype: bool
        """
        path = self.txt_template_dir.text()

        if not path:
            msg = self.tr('Please set the document designer templates '
                          'directory.')
            self.notif_bar.insertErrorNotification(msg)

            return False

        #Validate path
        if not self._check_path_exists(path, self.txt_template_dir):
            return False

        #Commit to registry
        self._reg_config.write({COMPOSER_TEMPLATE: path})

        return True

    def set_document_output_path(self):
        """
        Set the directory of document generator outputs.
        :return: True if the directory was set in the registry, otherwise
        False.
        :rtype: bool
        """
        path = self.txt_output_dir.text()

        if not path:
            msg = self.tr('Please set the document generator output directory'
                          '.')
            self.notif_bar.insertErrorNotification(msg)

            return False

        #Validate path
        if not self._check_path_exists(path, self.txt_output_dir):
            return False

        #Commit to registry
        self._reg_config.write({COMPOSER_OUTPUT: path})

        return True

    def _check_path_exists(self, path, text_box):
        #Validates if the specified folder exists
        dir = QDir()

        if not dir.exists(path):
            msg = self.tr(u"'{0}' directory does not exist.".format(path))
            self.notif_bar.insertErrorNotification(msg)

            #Highlight textbox control
            text_box.setStyleSheet(INVALIDATESTYLESHEET)

            timer = QTimer(self)
            #Sync interval with that of the notification bar
            timer.setInterval(self.notif_bar.interval)
            timer.setSingleShot(True)

            #Remove previous connected slots (if any)
            receivers = timer.receivers(SIGNAL('timeout()'))
            if receivers > 0:
                self._timer.timeout.disconnect()

            timer.start()
            timer.timeout.connect(lambda:self._restore_stylesheet(
                text_box)
            )

            return False

        return True

    def _restore_stylesheet(self, textbox):
        # Slot raised to restore the original stylesheet of the textbox control
        textbox.setStyleSheet(self._default_style_sheet)

        # Get reference to timer and delete
        sender = self.sender()
        if not sender is None:
            sender.deleteLater()

    def apply_settings(self):
        """
        Save settings.
        :return: True if the settings were successfully applied, otherwise
        False.
        :rtype: bool
        """
        #Set current profile
        if not self.set_current_profile():
            return False

        #Set db connection properties
        if not self.save_database_properties():
            return False

        #Set supporting documents directory
        if not self.set_supporting_documents_path():
            return False

        #Set document designer templates path
        if not self.set_document_templates_path():
            return False

        #Set document generator output path
        if not self.set_document_output_path():
            return False

        #Set backup output path
        if not self.set_backup_path():
            return False

        #Set PostgreSQL/bin path
        if not self.set_pgbin_path():
            return False


        #Set AutoBackup Key
        if not self.set_autobackup_key():
            return False



        # Set Entity browser record limit
        save_entity_browser_record_limit(self.edtEntityRecords.value())

        save_import_mapfile(self.edtMapfile.text())

        msg = self.tr('Settings successfully saved.')
        self.notif_bar.insertSuccessNotification(msg)

        return True

    def on_accept(self):
        """
        Slot raised to save the settings of the current widget and close the
        widget.
        """
        if not self.apply_settings():
            return

        self.accept()

    def manage_upgrade(self):
        """
        A slot raised when the upgrade button is clicked.
        It disables or enables the upgrade
        button based on the ConfigUpdated registry value.
        """

        self.config_updated_dic = self._reg_config.read(
            [CONFIG_UPDATED]
        )

        # if config file exists, check if registry key exists
        #if len(self.config_updated_dic) > 0:
            #config_updated_val = self.config_updated_dic[
                #CONFIG_UPDATED
            #]
            # If failed to upgrade, enable the upgrade button
            #if config_updated_val == '0' or config_updated_val == '-1':
                #self.upgradeButton.setEnabled(True)

            ## disable the button if any other value.
            #else:
                #self.upgradeButton.setEnabled(False)
        #else:
            #self.upgradeButton.setEnabled(False)

def ErrMessage(message):
    #Error Message Box
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText(message)
    msg.exec_()