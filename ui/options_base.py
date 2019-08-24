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
    QCursor,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QIntValidator
)
from PyQt4.QtCore import(
    Qt,
    QDir,
    QTimer,
    SIGNAL
)
from qgis.core import QgsApplication

from stdm.data.configuration.stdm_configuration import StdmConfiguration
from stdm.data.config import DatabaseConfig
from stdm.data.connection import DatabaseConnection
from stdm.settings import (
    current_profile,
    save_configuration,
    save_current_profile,
    get_entity_browser_record_limit,
    save_entity_browser_record_limit
)

from stdm.settings.registryconfig import (
    cmis_atom_pub_url,
    cmis_auth_config_id,
    composer_output_path,
    composer_template_path,
    debug_logging,
    holders_config_path,
    set_cmis_atom_pub_url,
    set_cmis_auth_config_id,
    set_debug_logging,
    set_holders_config_path,
    source_documents_path,
    QGISRegistryConfig,
    RegistryConfig,
    COMPOSER_OUTPUT,
    COMPOSER_TEMPLATE,
    NETWORK_DOC_RESOURCE,
    CONFIG_UPDATED,
    WIZARD_RUN
)

from stdm.security.auth_config import (
    config_entries
)
from stdm.network.cmis_manager import (
    CmisManager
)

from stdm.utils.util import setComboCurrentIndexWithText, version_from_metadata
from stdm.ui.login_dlg import loginDlg
from stdm.ui.notification import NotificationBar
from stdm.ui.customcontrols.validating_line_edit import INVALIDATESTYLESHEET
from stdm.ui.ui_options import Ui_DlgOptions

MAX_LIMIT = 500 # Maximum records in a entity browser
DEF_HOLDERS_CONFIG_PATH = QDir.home().path()+ '/.stdm/holders_config.ini'

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

        # Connect signals
        self._apply_btn.clicked.connect(self.apply_settings)
        self.buttonBox.accepted.connect(self.on_accept)
        self.chk_pg_connections.toggled.connect(self._on_use_pg_connections)
        self.cbo_pg_connections.currentIndexChanged.connect(
            self._on_pg_profile_changed)
        self.btn_db_conn_clear.clicked.connect(self.clear_properties)
        self.btn_test_db_connection.clicked.connect(self._on_test_db_connection)
        self.btn_template_folder.clicked.connect(
            self._on_choose_doc_designer_template_path
        )
        self.btn_composer_out_folder.clicked.connect(
            self._on_choose_doc_generator_output_path
        )
        self.btn_test_docs_repo_conn.clicked.connect(
            self._on_test_cmis_connection
        )
        self.txt_atom_pub_url.textChanged.connect(
            self._on_cmis_url_changed
        )
        self.btn_holders_conf_file.clicked.connect(
            self._on_choose_holders_config_file
        )

        self._config = StdmConfiguration.instance()
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

        # Load document repository-related settings
        self._load_cmis_config()

        # Load holders configuration file path
        self._load_holders_configuration_file()

        # Debug logging
        lvl = debug_logging()
        if lvl:
            self.chk_logging.setCheckState(Qt.Checked)
        else:
            self.chk_logging.setCheckState(Qt.Unchecked)

    def _load_cmis_config(self):
        """
        Load configuration names and IDs in the combobox then select
        the user specified ID.
        """
        # Load CMIS atom pub URL
        self.txt_atom_pub_url.setText(cmis_atom_pub_url())

        self.cbo_auth_config_name.clear()
        self.cbo_auth_config_name.addItem('')

        config_ids = config_entries()
        for ci in config_ids:
            id = ci[0]
            name = ci[1]
            display = u'{0} ({1})'.format(name, id)
            self.cbo_auth_config_name.addItem(display, id)

        # Then select the user specific config ID if specified
        conf_id = cmis_auth_config_id()
        if conf_id:
            id_idx = self.cbo_auth_config_name.findData(conf_id)
            if id_idx != -1:
                self.cbo_auth_config_name.setCurrentIndex(id_idx)

    def _load_holders_configuration_file(self):
        # Load the path of the holders configuration file.
        holders_config = holders_config_path()
        if not holders_config:
            # Use the default path
            holders_config = DEF_HOLDERS_CONFIG_PATH

        self.txt_holders_config.setText(holders_config)

    def _on_choose_holders_config_file(self):
        # Slot raised to browse the holders config file
        holders_config = self.txt_holders_config.text()
        if not holders_config:
            holders_config = QDir.home().path()

        conf_file = QFileDialog.getOpenFileName(
            self,
            self.tr('Browse Holders Configuration File'),
            holders_config,
            'Holders INI file (*.ini)'
        )
        if conf_file:
            self.txt_holders_config.setText(conf_file)

    def _on_cmis_url_changed(self, new_text):
        # Slot raised when text for CMIS URL changes. Basically updates
        # the tooltip so as to display long URLs
        self.txt_atom_pub_url.setToolTip(new_text)

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

        if not comp_out_path is None:
            self.txt_output_dir.setText(comp_out_path)

        if not comp_temp_path is None:
            self.txt_template_dir.setText(comp_temp_path)

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

    def _on_choose_doc_designer_template_path(self):
        #Slot raised to select directory for document designer templates.
        self._set_selected_directory(self.txt_template_dir, self.tr(
            'Document Designer Templates Directory')
        )

    def _on_choose_doc_generator_output_path(self):
        #Slot raised to select directory for doc generator outputs.
        self._set_selected_directory(self.txt_output_dir, self.tr(
            'Document Generator Output Directory')
        )

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

        # Create database connection object
        db_conn = DatabaseConnection(host, port, database)

        return db_conn

    def _on_test_db_connection(self):
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
            self.notif_bar.insertSuccessNotification(msg)

    def _on_test_cmis_connection(self):
        # Slot raised to test connection to CMIS service
        status = self._validate_cmis_properties()
        if not status:
            return

        self.notif_bar.clear()

        atom_pub_url = self.txt_atom_pub_url.text()
        auth_conf_id = self.cbo_auth_config_name.itemData(
            self.cbo_auth_config_name.currentIndex()
        )

        cmis_mgr = CmisManager(
            url=atom_pub_url,
            auth_config_id=auth_conf_id
        )

        QgsApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        status = cmis_mgr.connect()
        QgsApplication.restoreOverrideCursor()

        if status:
            msg = self.tr(
                'Connection to the CMIS server succeeded.'
            )
            self.notif_bar.insertSuccessNotification(msg)
        else:
            msg = self.tr(
                'Failed to connect to the CMIS server. Check URL and/or '
                'credentials.'
            )
            self.notif_bar.insertErrorNotification(msg)

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

        save_current_profile(profile_name)

        return True

    def set_cmis_properties(self):
        """
        Saves the CMIS atom pub URL and authentication configuration ID.
        """
        if not self._validate_cmis_properties():
            return False

        atom_pub_url = self.txt_atom_pub_url.text()
        set_cmis_atom_pub_url(atom_pub_url)

        curr_idx = self.cbo_auth_config_name.currentIndex()
        config_id = self.cbo_auth_config_name.itemData(curr_idx)
        set_cmis_auth_config_id(config_id)

        return True

    def _validate_cmis_properties(self):
        # Assert if user has specified URL and authentication config ID.
        atom_pub_url = self.txt_atom_pub_url.text()
        config_name_id = self.cbo_auth_config_name.currentText()

        status = True

        if not atom_pub_url:
            msg = self.tr('Please specify the URL of the CMIS atom pub service.')
            self.notif_bar.insertErrorNotification(msg)
            status = False

        if not config_name_id:
            msg = self.tr('Please select the configuration ID containing the CMIS authentication.')
            self.notif_bar.insertErrorNotification(msg)
            status = False

        return status

    def set_holders_config_file(self):
        # Save the path to the holders configuration file
        holders_config_file = self.txt_holders_config.text()
        if not holders_config_file:
            msg = self.tr(
                'Please set the path to the holders configuration file.'
            )
            self.notif_bar.insertErrorNotification(msg)
            return False

        set_holders_config_path(holders_config_file)

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

        # Validate path
        if not self._check_path_exists(path, self.txt_template_dir):
            return False

        # Commit to registry
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

    def apply_debug_logging(self):
        # Save debug logging
        logger = logging.getLogger('stdm')

        if self.chk_logging.checkState() == Qt.Checked:
            logger.setLevel(logging.DEBUG)
            set_debug_logging(True)
        else:
            logger.setLevel(logging.ERROR)
            set_debug_logging(False)

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

        # Set CMIS properties
        if not self.set_cmis_properties():
            return False

        # Set holders configuration file path
        if not self.set_holders_config_file():
            return False

        #Set document designer templates path
        if not self.set_document_templates_path():
            return False

        #Set document generator output path
        if not self.set_document_output_path():
            return False

        self.apply_debug_logging()

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
