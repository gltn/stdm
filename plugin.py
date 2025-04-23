"""
/***************************************************************************
Name                 : STDM QGIS Loader
Description          : STDM QGIS Loader
Date                 : 04-01-2015
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
import glob
import logging
import os.path
import platform
import shutil
from collections import OrderedDict

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *
import qgis.utils
from sqlalchemy.exc import SQLAlchemyError
from stdm.settings.config_serializer import ConfigurationFileSerializer
from stdm.settings import current_profile, save_current_profile
from stdm.settings.startup_handler import copy_startup
from stdm.data.configfile_paths import FilePaths
from stdm.data.configuration.exception import ConfigurationException
from stdm.data.configuration.stdm_configuration import StdmConfiguration
from stdm.settings.config_file_updater import ConfigurationFileUpdater
from stdm.data.configuration.config_updater import ConfigurationSchemaUpdater
from stdm.data.configuration.column_updaters import varchar_updater

from stdm.ui.change_pwd_dlg import changePwdDlg
from stdm.ui.doc_generator_dlg import (
    DocumentGeneratorDialogWrapper,
    EntityConfig
)
from stdm.data.database import alchemy_table
from stdm.ui.login_dlg import loginDlg
from stdm.ui.manage_accounts_dlg import manageAccountsDlg
from stdm.ui.content_auth_dlg import contentAuthDlg
from stdm.ui.options_base import OptionsDialog

from stdm.ui.view_str import ViewSTRWidget
from stdm.ui.admin_unit_selector import AdminUnitSelector
from stdm.ui.entity_browser import (
    EntityBrowserWithEditor,
    ContentGroupEntityBrowser
)
from stdm.ui.about import AboutSTDMDialog
from stdm.ui.stdmdialog import DeclareMapping

from stdm.ui.wizard.wizard import ConfigWizard

from stdm.ui.document_downloader_win import DocumentDownloader

from stdm.ui.import_data import ImportData
from stdm.ui.export_data import ExportData

from stdm.ui.spatial_unit_manager import SpatialUnitManagerDockWidget

import data

from stdm.data.database import (
    Base,
    NoPostGISError,
    STDMDb
)
from stdm.data.pg_utils import (
    pg_table_exists,
    spatial_tables,
    postgis_exists,
    create_postgis,
    table_column_names
)
from stdm.settings.registryconfig import (
    RegistryConfig,
    WIZARD_RUN,
    STDM_VERSION,
    CONFIG_UPDATED,
    HOST,
    composer_template_path
)
from stdm.ui.license_agreement import LicenseAgreement

from navigation import (
    STDMAction,
    QtContainerLoader,
    ContentGroup,
    TableContentGroup
)

from stdm.utils.util import simple_dialog
from stdm.ui.change_log import ChangeLog
from stdm.settings.template_updater import TemplateFileUpdater

from stdm.utils.util import (
    getIndex,
    db_user_tables,
    format_name,
    setComboCurrentIndexWithText,
    version_from_metadata,
    documentTemplates,
    user_non_profile_views
)

from stdm.composer.composer_data_source import composer_data_source

from mapping.utils import pg_layerNamesIDMapping

from composer import ComposerWrapper
from stdm.ui.progress_dialog import STDMProgressDialog
from stdm.ui.feature_details import (
        DetailsTreeView,
        DetailsDockWidget
        )
from stdm.ui.social_tenure.str_editor import STREditor

from stdm.ui.geoodk_converter_dialog import GeoODKConverter
from stdm.ui.geoodk_profile_importer import ProfileInstanceRecords

from stdm.security.privilege_provider import SinglePrivilegeProvider
from stdm.security.roleprovider import RoleProvider

from stdm.data.backup_utils import (
    perform_autobackup,
    backup_config,
    backup_database
)
from stdm.data.stdm_reqs_sy_ir import autochange_profile_configfile
LOGGER = logging.getLogger('stdm')

class _DocumentTemplate(object):
    """
    Contains basic information about a document template.
    """
    def __init__(self, **kwargs):
        self.name = kwargs.get('name', '')
        self.path = kwargs.get('path', '')
        self.data_source = kwargs.get('data_source', None)

    @property
    def referenced_table_name(self):
        """
        :return: Returns the referenced table name.
        :rtype: str
        """
        if self.data_source is None:
            return ''

        return self.data_source.referenced_table_name

    @staticmethod
    def build_from_path(name, path):
        """
        Creates an instance of the _DocumentTemplate class from the path of
        a document template.
        :param name: Template name.
        :type name: str
        :param path: Absolute path to the document template.
        :type path: str
        :return: Returns an instance of the _DocumentTemplate class from the
        absolute path of the document template.
        :rtype: _DocumentTemplate
        """
        data_source = composer_data_source(path)
        kwargs = {
            'name': name,
            'path': path,
            'data_source': data_source
        }

        return _DocumentTemplate(**kwargs)


class STDMQGISLoader(object):

    viewSTRWin = None

    def __init__(self, iface):
        self.iface = iface

        # Initialize loader
        self.toolbarLoader = None
        self.menubarLoader = None
        self.details_tree_view = None
        self.combo_action = None
        self.spatialLayerManagerDockWidget = self

        # Setup locale
        self.plugin_dir = os.path.dirname(__file__)
        localePath = ""
        locale = QSettings().value("locale/userLocale")[0:2]
        if QFileInfo(self.plugin_dir).exists():
            # Replace forward slash with backslash
            self.plugin_dir = self.plugin_dir.replace("\\", "/")
            localePath = self.plugin_dir + "/i18n/stdm_%s.qm" % (locale,)
        if QFileInfo(localePath).exists():
            self.translator = QTranslator()
            self.translator.load(localePath)
            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # STDM Tables
        self.stdmTables = []
        self.entity_formatters = {}
        self.entity_table_model = {}
        self.stdm_config = StdmConfiguration.instance()
        self.reg_config = RegistryConfig()
        self.spatialLayerMangerDockWidget = None

        self._user_logged_in = False
        self.current_profile = None

        # current logged-in user
        self.current_user = None
        self.profile_templates = []

        # Profile status label showing the current profile
        self.profile_status_label = None
        LOGGER.debug('STDM plugin has been initialized.')
        self.entity_browser = None
        # Load configuration file
        self.config_path = QDesktopServices.storageLocation(
            QDesktopServices.HomeLocation) \
                      + '/.stdm/configuration.stc'
        self.config_serializer = ConfigurationFileSerializer(self.config_path)
        self.configuration_file_updater = ConfigurationFileUpdater(self.iface)
        copy_startup()

    def initGui(self):
        # Initial actions on starting up the application
        self._menu_items()
        self.loginAct = STDMAction(QIcon(":/plugins/stdm/images/icons/login.png"),
                                   QApplication.translate("LoginToolbarAction",
                                                          "Login"),
                                   self.iface.mainWindow(),
                                   "CAA4F0D9-727F-4745-A1FC-C2173101F711")
        self.loginAct.setShortcut(QKeySequence(Qt.Key_F2))

        self.aboutAct = STDMAction(QIcon(":/plugins/stdm/images/icons/info.png"),
        QApplication.translate("AboutToolbarAction","About"), self.iface.mainWindow(),
        "137FFB1B-90CD-4A6D-B49E-0E99CD46F784")
        #Define actions that are available to all logged in users
        self.logoutAct = STDMAction(QIcon(":/plugins/stdm/images/icons/logout.png"), \
        QApplication.translate("LogoutToolbarAction","Logout"), self.iface.mainWindow(),
        "EF3D96AF-F127-4C31-8D9F-381C07E855DD")

        self.changePasswordAct = STDMAction(QIcon(":/plugins/stdm/images/icons/change_password.png"), \
        QApplication.translate("ChangePasswordToolbarAction","Change Password"), self.iface.mainWindow(),
        "8C425E0E-3761-43F5-B0B2-FB8A9C3C8E4B")
        self.helpAct = STDMAction(QIcon(":/plugins/stdm/images/icons/help-content.png"), \
        QApplication.translate("STDMQGISLoader","Help Contents"), self.iface.mainWindow(),
        "7A61CEA9-2A64-45F6-A40F-D83987D416EB")
        self.helpAct.setShortcut(Qt.Key_F10)

        # connect the actions to their respective methods
        self.loginAct.triggered.connect(self.login)
        self.changePasswordAct.triggered.connect(self.changePassword)
        self.logoutAct.triggered.connect(self.logout)
        self.aboutAct.triggered.connect(self.about)
        self.helpAct.triggered.connect(self.help_contents)
        self.initToolbar()
        self.initMenuItems()

    def _menu_items(self):
        #Create menu and menu items on the menu bar
        self.stdmMenu=QMenu()
        self.stdmMenu.setTitle(
            QApplication.translate(
                "STDMQGISLoader","STDM"
            )
        )
        #Initialize the menu bar item
        self.menu_bar=self.iface.mainWindow().menuBar()
        #Create actions
        actions=self.menu_bar.actions()
        currAction=actions[len(actions)-1]
        # add actions to the menu bar
        self.menu_bar.insertMenu(
            currAction,
            self.stdmMenu
        )
        self.stdmMenu.setToolTip(
            QApplication.translate(
                "STDMQGISLoader",
                "STDM plugin menu"
            )
        )


    def getThemeIcon(self, theName):
        # get the icon from the best available theme
        myCurThemePath = QgsApplication.activeThemePath() + "/plugins/" + theName
        myDefThemePath = QgsApplication.defaultThemePath() + "/plugins/" + theName
        myQrcPath = ":/plugins/stdm/" + theName
        if QFile.exists(myCurThemePath):
            return QIcon(myCurThemePath)
        elif QFile.exists(myDefThemePath):
            return QIcon(myDefThemePath)
        elif QFile.exists(myQrcPath):
            return QIcon(myQrcPath)
        else:
            return QIcon()

    def initToolbar(self):
        #Load initial STDM toolbar
        self.stdmInitToolbar = self.iface.addToolBar("STDM")
        self.stdmInitToolbar.setObjectName("STDM")
        #Add actions to the toolbar
        self.stdmInitToolbar.addAction(self.loginAct)

        self.stdmInitToolbar.addSeparator()
        self.stdmInitToolbar.addAction(self.helpAct)
        self.stdmInitToolbar.addAction(self.aboutAct)

        self.git_branch = QLabel(self.iface.mainWindow())
        self.git_branch.setText(self.active_branch_name())
        self.stdmInitToolbar.addWidget( self.git_branch)

    def active_branch_name(self):
        try:
            home = QDesktopServices.storageLocation(QDesktopServices.HomeLocation)
            branch_file = '{}/.stdm/.branch'.format(home)
            name = '('+[line.strip() for line in open(branch_file)][0]+')'
        except:
            name = ''
        return name

    def initMenuItems(self):
        self.stdmMenu.addAction(self.loginAct)
        self.stdmMenu.addSeparator()
        self.stdmMenu.addAction(self.helpAct)
        self.stdmMenu.addAction(self.aboutAct)

    def unload(self):
        # Remove the STDM toolbar
        del self.stdmInitToolbar
        # Remove connection info
        self.logoutCleanUp()

    def login(self):
        '''
        Show login dialog
        '''
        frmLogin = loginDlg(self.iface.mainWindow())
        retstatus = frmLogin.exec_()

        if retstatus == QDialog.Accepted:
            #Assign the connection object
            data.app_dbconn = frmLogin.dbConn

            self.current_user = frmLogin.dbConn.User

            #Initialize the whole STDM database

            db = STDMDb.instance()

            if not db.postgis_state:
                if not postgis_exists():
                    create_postgis()
                else:
                    err_msg = QApplication.translate(
                        "STDM",
                        "STDM cannot be loaded because the system has "
                        "detected that the PostGIS extension is missing "
                        "in '{0}' database.\nCheck that PostGIS has been "
                        "installed. Please contact the system "
                        "administrator for more information.".format(
                            frmLogin.dbConn.Database)
                    )
                    QMessageBox.critical(
                        self.iface.mainWindow(),
                        QApplication.translate(
                            "STDM","Spatial Extension Error"
                        ),
                        err_msg
                    )

                    return

            # Checks if the license is accepted and stops loading
            # modules if the terms and conditions are never accepted.
            license_status = self.load_license_agreement()
            if not license_status:
                return

            #Load logout and change password actions
            self.stdmInitToolbar.insertAction(self.loginAct,
                                              self.logoutAct)
            self.stdmInitToolbar.insertAction(self.loginAct,
                                              self.changePasswordAct)

            self.stdmMenu.insertAction(self.loginAct,self.logoutAct)
            self.stdmMenu.insertAction(self.loginAct,self.changePasswordAct)

            self.loginAct.setEnabled(False)

            #Fetch STDM tables
            self.stdmTables = spatial_tables()

            #Load the configuration from file
            config_load_status = self.load_configuration_from_file(
                self.iface.mainWindow()
            )

            #Exit if the load failed
            if not config_load_status:
                return

            try:
                self.show_change_log()
                #Set current profile
                self.current_profile = current_profile()
                self._user_logged_in = True
                if self.current_profile is None:
                    result = self.default_profile()
                    if not result:
                        return
                self.create_custom_tenure_dummy_col()

                self.loadModules()
                self.default_profile()
                self.run_wizard()
                self.copy_designer_template()

            except Exception as pe:
                title = QApplication.translate(
                    "STDMQGISLoader",
                    "Error Loading Modules"
                )

                self.reset_content_modules_id( title, pe)
        perform_autobackup()

    def create_custom_tenure_dummy_col(self):
        """
        Creates custom tenure entity dummy column if it does not exist.
        :return:
        :rtype:
        """
        social_tenure = self.current_profile.social_tenure
        for spatial_unit in social_tenure.spatial_units:
            custom_entity = social_tenure.spu_custom_attribute_entity(
                spatial_unit
            )
            if custom_entity is None:
                continue
            if pg_table_exists(custom_entity.name):
                custom_ent_cols = table_column_names(custom_entity.name)

                if social_tenure.CUSTOM_TENURE_DUMMY_COLUMN \
                        not in custom_ent_cols:
                    dummy_col = custom_entity.columns[
                        social_tenure.CUSTOM_TENURE_DUMMY_COLUMN]
                    custom_table = alchemy_table(custom_entity.name)
                    varchar_updater(dummy_col, custom_table,
                                    custom_ent_cols)

    def minimum_table_checker(self):

        title = QApplication.translate(
            "STDMQGISLoader",
            'Database Table Error'
        )

        message = QApplication.translate(
            "STDMQGISLoader",
            'The system has detected that database tables \n'
            'required in this module are missing.\n'
            'Do you want to re-run the Configuration Wizard now?'
        )

        database_check = QMessageBox.critical(
            self.iface.mainWindow(),
            title,
            message,
            QMessageBox.Yes,
            QMessageBox.No
        )
        if database_check == QMessageBox.Yes:
            self.load_config_wizard()

    def entity_table_checker(self, entity):
        """
        Checks if the database table for a given entity exists.
        In case the table doesn't exists, it shows an error message.
        :param entity: Entity
        :type entity: Object
        :return: True if there is no missing table and false
        if there is a missing table.
        :rtype: Boolean
        """
        title = QApplication.translate(
            "STDMQGISLoader",
            'Database Table Error'
        )

        if not pg_table_exists(entity.name):
            message = QApplication.translate(
                "STDMQGISLoader",
                u'The system has detected that '
                'a required database table - \n'
                '{} is missing. \n'
                'Do you want to re-run the '
                'Configuration Wizard now?'.format(
                    entity.name
                ),
                None,
                QCoreApplication.UnicodeUTF8
            )
            database_check = QMessageBox.critical(
                self.iface.mainWindow(),
                title,
                message,
                QMessageBox.Yes,
                QMessageBox.No
            )
            if database_check == QMessageBox.Yes:
                self.load_config_wizard()
            else:
                return False
        else:
            return True
        message = QApplication.translate(
            "STDMQGISLoader",
            u'The system has detected that '
            'a required database table - \n'
            '{} is missing. \n'
            'Do you want to re-run the '
            'Configuration Wizard now?'.format(
                entity.short_name
            ),
            None,
            QCoreApplication.UnicodeUTF8
        )
        database_check = QMessageBox.critical(
            self.iface.mainWindow(),
            title,
            message,
            QMessageBox.Yes,
            QMessageBox.No
        )

        if database_check == QMessageBox.Yes:
            self.load_config_wizard()
        else:
            return False

    def run_wizard(self):
        """
        Checks if the configuration wizard was run before.
        :return:
        :rtype:
        """
        host = self.reg_config.read([HOST])
        host_val = host[HOST]

        if host_val not in [u'localhost', u'127.0.0.1']:
            return

        wizard_key = self.reg_config.read([WIZARD_RUN])

        title = QApplication.translate(
            "STDMQGISLoader",
            'Configuration Wizard Error'
        )
        message = QApplication.translate(
            "STDMQGISLoader",
            'The system has detected that you did not run \n'
            'the Configuration Wizard so far. \n'
            'Do you want to run it now? '
        )
        if len(wizard_key) > 0:
            wizard_value = wizard_key[WIZARD_RUN]

            if wizard_value == 0 or wizard_value == '0':

                default_profile = QMessageBox.critical(
                    self.iface.mainWindow(),
                    title,
                    message,
                    QMessageBox.Yes,
                    QMessageBox.No
                )

                if default_profile == QMessageBox.Yes:
                    self.load_config_wizard()

        else:
            default_profile = QMessageBox.critical(
                self.iface.mainWindow(),
                title,
                message,
                QMessageBox.Yes,
                QMessageBox.No
            )

            if default_profile == QMessageBox.Yes:
                self.load_config_wizard()

    def default_profile(self):
        """
        Checks if the current profile exists.
        If there is only one profile, it sets
        it and run reload_plugin(). If there
        is more than one profile, it asks the
        user the set a profile using Options.
        If no profile exists, it asks the user
        to run Configuration Wizard.
        :return: None
        :rtype: NoneType
        """
        if self.current_profile is None:
            profiles = self.stdm_config.profiles

            title = QApplication.translate(
                "STDMQGISLoader",
                'Default Profile Error'
            )
            if len(profiles) > 0:
                profile_name = profiles.keys()[0]
                save_current_profile(profile_name)
                self.reload_plugin(profile_name)

            else:
                solution = 'Do you want to run the ' \
                           'Configuration Wizard now?'

                message = QApplication.translate(
                    "STDMQGISLoader",
                    'The system has detected that there '
                    'is no default profile. \n {}'.format(
                        solution
                    )

                )
                default_profile = QMessageBox.critical(
                    self.iface.mainWindow(),
                    title,
                    message,
                    QMessageBox.Yes,
                    QMessageBox.No
                )

                if default_profile == QMessageBox.Yes:

                    self.load_config_wizard()
                    return True
                else:
                    return False

    def on_update_progress(self, message):
        """
        A slot raised when update_progress signal is emitted
        in ConfigurationSerializer, ConfigurationUpdater and
        and of the Updaters.
        :param message: The progress message.
        :type message: String
        :return:
        :rtype:
        """
        self.progress.show()
        self.progress.setRange(0, 0)
        self.progress.progress_message(message)

    def on_update_complete(self, document):
        """
        A slot raised when the update_complete signal is emitted.
        It runs post update tasks such as closing progress dialog
        and showing a success message.
        :param document: The updated dom document
        :type document: QDomDocument
        :return:
        :rtype:
        """
        # TODO remove this line below when schema updater is refactored
        self.config_serializer.on_version_updated(document)

        self.reg_config.write(
            {WIZARD_RUN: 1}
        )

        self.progress.hide()
        self.progress.cancel()

    def load_configuration_to_serializer(self):
        try:
            self.config_serializer.update_complete.connect(
                self.on_update_complete
            )
            self.config_serializer.update_progress.connect(
                self.on_update_progress
            )
            self.config_serializer.db_update_progress.connect(
                self.on_update_progress
            )
            self.config_serializer.load()

            return True

        except IOError as io_err:
            QMessageBox.critical(self.iface.mainWindow(),
                    QApplication.translate(
                        'STDM', 'Load Configuration Error'
                    ),
                    unicode(io_err))

            return False

        except ConfigurationException as c_ex:
            QMessageBox.critical(
                self.iface.mainWindow(),
                QApplication.translate(
                    'STDM',
                    'Load Configuration Error'
                ),
                unicode(c_ex)
            )

            return False

    def stdm_reg_version(self, metadata_version):
        """
        Checks and set STDM registry version using metadata version.
        :param metadata_version: The metadata version
        :type metadata_version: String
        :return: Result of the check or update.
        If reg_version is different from metadata returns 'updated'
        If reg_version is same as metadata returns 'non-updated'
        :rtype: String
        """
        reg_version_dict = self.reg_config.read(
            [STDM_VERSION]
        )

        if STDM_VERSION in reg_version_dict.keys():
            reg_version = reg_version_dict[STDM_VERSION]

        else:
            reg_version = None

        if reg_version is None:
            self.reg_config.write(
                {STDM_VERSION: metadata_version}
            )
            return 'updated'
        elif metadata_version != reg_version:
            self.reg_config.write(
                {STDM_VERSION: metadata_version}
            )
            # compare major versions and mark it return 'updated' if major update.
            md_major_version = metadata_version.rsplit('.', 1)[0]
            reg_major_version = reg_version.rsplit('.', 1)[0]

            if md_major_version != reg_major_version:
                return 'updated'
            else:
                return 'non-updated'
        elif metadata_version == reg_version:
            return 'non-updated'

    def show_change_log(self):
        """
        Shows the change log the new version of STDM.
        """
        version = version_from_metadata()
        # Get the big releases only not minor ones.
        major_version = version.rsplit('.', 1)[0]
        result = self.stdm_reg_version(version)

        if result == 'updated':
            title = QApplication.translate(
                'ConfigurationFileUpdater',
                'Upgrade Information'
            )

            message = QApplication.translate(
                'ConfigurationFileUpdater',
                'Would you like to view the '
                'new features and changes of STDM {}?'.format(major_version)
            )

            result, checkbox_result = simple_dialog(
                self.iface.mainWindow(),
                title,
                message
            )
            if result:
                change_log = ChangeLog(self.iface.mainWindow())
                change_log.show_change_log(self.plugin_dir)

    def copy_designer_template(self):
        """
        Copies designer templates from the templates folder in the plugin.
        :return:
        :rtype:
        """
        template_files = glob.glob('{}*.sdt'.format(
            FilePaths().defaultConfigPath()
        ))
        templates_path = composer_template_path()
        for temp_file in template_files:
            destination_file = os.path.join(
                templates_path, os.path.basename(temp_file))
            if not os.path.isfile(destination_file):
                try:
                    shutil.copyfile(temp_file, destination_file)
                except IOError:
                    os.makedirs(templates_path)
                    shutil.copyfile(temp_file, destination_file)

    def load_configuration_from_file(self, parent, manual=False):
        """
        Load configuration object from the file.
        :return: True if the file was successfully
        loaded. Otherwise, False.
        :rtype: bool
        """
        self.progress = STDMProgressDialog(parent)
        self.progress.overall_progress('Upgrading STDM Configuration...')

        home = QDesktopServices.storageLocation(QDesktopServices.HomeLocation)

        config_path = '{}/.stdm/configuration.stc'.format(home)

        if manual:
            upgrade_status = self.configuration_file_updater.load(
                self.progress, True
            )

        else:
            upgrade_status = self.configuration_file_updater.load(
                self.progress
            )

        if upgrade_status:
            # Append configuration_upgraded.stc profiles
            if os.path.isfile(config_path):
                self.progress.progress_message(
                    'Appending the upgraded profile', ''
                )

                self.configuration_file_updater.\
                    append_profile_to_config_file(
                    'configuration_upgraded.stc',
                    'configuration.stc'
                )

            load_result = self.load_configuration_to_serializer()

            if load_result:
                config_updater = ConfigurationSchemaUpdater()
                config_updater.exec_()
                profile_details_dict = \
                    self.configuration_file_updater.backup_data()

                profile_details = {}
                # upgrade profile for each profiles
                for profile, tables in profile_details_dict.iteritems():
                    profile_details[profile] = tables
                    upgrade_template = TemplateFileUpdater(
                        self.plugin_dir, profile_details, self.progress
                    )

                    upgrade_template.process_update(True)

                QMessageBox.information(
                    self.iface.mainWindow(),
                    QApplication.translate(
                        'STDMQGISLoader',
                        'Upgrade STDM Configuration'
                    ),
                    QApplication.translate(
                        'STDMQGISLoader',
                        'Your configuration has been '
                        'successfully upgraded!'
                    )
                )
                # Upgrade from options behavior
                first_profile = profile_details_dict.keys()[0]
                if manual:
                    parent.close()
                    self.reload_plugin(first_profile)
                else:
                    save_current_profile(first_profile)

                self.configuration_file_updater.reg_config.write(
                    {CONFIG_UPDATED: '1'}
                )
                self.configuration_file_updater.reg_config.write(
                    {WIZARD_RUN: 1}
                )
                self.configuration_file_updater.append_log(
                    'Successfully migrated STDM '
                    'Configuration to version 1.2!'
                )
                return True

        else:
            self.configuration_file_updater.\
                _copy_config_file_from_template()
            result = self.load_configuration_to_serializer()
            return result

    def loadModules(self):

        '''
        Define and add modules to the menu and/or toolbar using the module loader
        '''


        self.toolbarLoader = QtContainerLoader(self.iface.mainWindow(),
                                               self.stdmInitToolbar,self.logoutAct)
        self.menubarLoader = QtContainerLoader(self.iface.mainWindow(),
                                               self.stdmMenu, self.logoutAct)
        #Connect to the content added signal
        #self.toolbarLoader.contentAdded.connect(self.onContentAdded)

        #Define containers for grouping actions
        adminBtn = QToolButton()
        adminObjName = QApplication.translate("ToolbarAdminSettings","Admin Settings")
        #Required by module loader for those widgets that need to be inserted into the container
        adminBtn.setObjectName(adminObjName)
        adminBtn.setToolTip(adminObjName)
        adminBtn.setIcon(QIcon(":/plugins/stdm/images/icons/settings.png"))
        adminBtn.setPopupMode(QToolButton.InstantPopup)

        adminMenu = QMenu(adminBtn)
        adminBtn.setMenu(adminMenu)

        #Settings menu container in STDM's QGIS menu
        stdmAdminMenu = QMenu(self.stdmMenu)
        stdmAdminMenu.setIcon(QIcon(":/plugins/stdm/images/icons/settings.png"))
        stdmAdminMenu.setObjectName("STDMAdminSettings")
        stdmAdminMenu.setTitle(QApplication.translate("ToolbarAdminSettings","Admin Settings"))

        #Create content menu container
        contentBtn = QToolButton()

        contentObjName = QApplication.translate("ToolbarAdminSettings","Entities")
        #Required by module loader for those widgets that need to be inserted into the container
        contentBtn.setObjectName(contentObjName)
        contentBtn.setToolTip(contentObjName)
        contentBtn.setIcon(QIcon(":/plugins/stdm/images/icons/entity_management.png"))
        contentBtn.setPopupMode(QToolButton.InstantPopup)

        contentMenu = QMenu(contentBtn)
        contentBtn.setMenu(contentMenu)

        stdmEntityMenu = QMenu(self.stdmMenu)
        stdmEntityMenu.setObjectName("STDMEntityMenu")
        stdmEntityMenu.setIcon(QIcon(":/plugins/stdm/images/icons/entity_management.png"))
        stdmEntityMenu.setTitle(QApplication.translate("STDMEntityMenu","Entities"))

        #Mobile menu container
        # Mobile content menu container
        geoodk_mobile_dataMenu = QMenu(self.stdmMenu)
        geoodk_mobile_dataMenu.setObjectName("MobileMenu")
        geoodk_mobile_dataMenu.setIcon(QIcon(":/plugins/stdm/images/icons/mobile_data_management.png"))
        geoodk_mobile_dataMenu.setTitle(QApplication.translate("GeoODKMobileSettings", "Mobile Data Forms"))

        geoodkBtn = QToolButton()
        adminObjName = QApplication.translate("MobileToolbarSettings", "Mobile Data Forms")
        # Required by module loader for those widgets that need to be inserted into the container
        geoodkBtn.setObjectName(adminObjName)
        geoodkBtn.setToolTip(adminObjName)
        geoodkBtn.setIcon(QIcon(":/plugins/stdm/images/icons/mobile_data_management.png"))
        geoodkBtn.setPopupMode(QToolButton.InstantPopup)

        geoodkMenu = QMenu(geoodkBtn)
        geoodkBtn.setMenu(geoodkMenu)
        #Define actions

        self.contentAuthAct = QAction(
            QIcon(":/plugins/stdm/images/icons/content_auth.png"),
            QApplication.translate(
                "ContentAuthorizationToolbarAction",
                "Content Authorization"
            ),
            self.iface.mainWindow()
        )

        self.usersAct = QAction(QIcon(":/plugins/stdm/images/icons/users_manage.png"), \
        QApplication.translate("ManageUsersToolbarAction","Manage Users-Roles"), self.iface.mainWindow())


        self.options_act = QAction(QIcon(":/plugins/stdm/images/icons/options.png"), \
                           QApplication.translate("OptionsToolbarAction", "Options"),
                           self.iface.mainWindow())
                           
        self.backupAct = QAction(QIcon(":/plugins/stdm/images/icons/save.png"), \
                          QApplication.translate("BackupToolbarAction", "Backup Database"), 
                          self.iface.mainWindow())

        self.manageAdminUnitsAct = QAction(
            QIcon(":/plugins/stdm/images/icons/manage_admin_units.png"),
            QApplication.translate(
                "ManageAdminUnitsToolbarAction",
                "Manage Administrative Units"
            ),
            self.iface.mainWindow()
        )

        self.downloadAct = QAction(QIcon(":/plugins/stdm/images/icons/docdownload.png"), \
        QApplication.translate("DownloadAction","Download and Upload Documents"), self.iface.mainWindow())

        self.importAct = QAction(QIcon(":/plugins/stdm/images/icons/import.png"), \
        QApplication.translate("ImportAction","Import Data"), self.iface.mainWindow())

        self.exportAct = QAction(QIcon(":/plugins/stdm/images/icons/export.png"), \
        QApplication.translate("ReportBuilderAction","Export Data"), self.iface.mainWindow())

        self.docDesignerAct = QAction(QIcon(":/plugins/stdm/images/icons/cert_designer.png"), \
        QApplication.translate("DocumentDesignerAction","Document Designer"), self.iface.mainWindow())

        self.docGeneratorAct = QAction(QIcon(":/plugins/stdm/images/icons/generate_document.png"), \
        QApplication.translate("DocumentGeneratorAction","Document Generator"), self.iface.mainWindow())

        #Spatial Layer Manager
        self.spatialLayerManager = QAction(QIcon(":/plugins/stdm/images/icons/spatial_unit_manager.png"), \
        QApplication.translate("SpatialEditorAction","Spatial Unit Manager"), self.iface.mainWindow())
        self.spatialLayerManager.setCheckable(True)

        #Spatial Layer Manager
        self.feature_details_act = QAction(QIcon(":/plugins/stdm/images/icons/feature_details.png"), \
        QApplication.translate("SpatialEditorAction","Spatial Entity Details"), self.iface.mainWindow())
        self.feature_details_act.setCheckable(True)

        self.viewSTRAct = QAction(QIcon(":/plugins/stdm/images/icons/view_str.png"), \
        QApplication.translate("ViewSTRToolbarAction","View Social Tenure Relationship"),
        self.iface.mainWindow())

        self.wzdAct = QAction(QIcon(":/plugins/stdm/images/icons/table_designer.png"),\
                    QApplication.translate("ConfigWizard","Configuration Wizard"), self.iface.mainWindow())
        self.wzdAct.setShortcut(Qt.Key_F7)
        self.ModuleAct = QAction(QIcon(":/plugins/stdm/images/icons/table_designer.png"),\
                    QApplication.translate("WorkspaceConfig","Entities"), self.iface.mainWindow())

        self.mobile_form_act = QAction(QIcon(":/plugins/stdm/images/icons/mobile_collect.png"), \
                                       QApplication.translate("MobileFormGenerator", "Generate Mobile Form"),
                                       self.iface.mainWindow())
        self.mobile_form_import = QAction(QIcon(":/plugins/stdm/images/icons/mobile_import.png"), \
                                          QApplication.translate("MobileFormGenerator", "Import Mobile Data"),
                                          self.iface.mainWindow())

        dock_widget = DetailsDockWidget(self.iface, self)
        self.details_tree_view = DetailsTreeView(self.iface, self, dock_widget)

        # Add current profiles to profiles combobox
        self.load_profiles_combobox()

        #Connect the slots for the actions above
        self.contentAuthAct.triggered.connect(self.contentAuthorization)
        self.usersAct.triggered.connect(self.manageAccounts)
        self.options_act.triggered.connect(self.on_sys_options)
        self.backupAct.triggered.connect(self.manual_backup)
        self.manageAdminUnitsAct.triggered.connect(self.onManageAdminUnits)
        self.exportAct.triggered.connect(self.onExportData)
        self.downloadAct.triggered.connect(self.onDownload)
        self.importAct.triggered.connect(self.onImportData)
        self.docDesignerAct.triggered.connect(self.onDocumentDesigner)
        self.docGeneratorAct.triggered.connect(self.onDocumentGenerator)
        self.spatialLayerManager.triggered.connect(self.spatialLayerMangerActivate)

        self.feature_details_act.triggered.connect(self.details_tree_view.activate_feature_details)

        self.mobile_form_act.triggered.connect(self.mobile_form_generator)
        self.mobile_form_import.triggered.connect(self.mobile_form_importer)

        self.iface.mapCanvas().currentLayerChanged.connect(
            lambda :self.details_tree_view.activate_feature_details(False)
        )
        contentMenu.triggered.connect(self.widgetLoader)
        self.wzdAct.triggered.connect(self.load_config_wizard)
        self.viewSTRAct.triggered.connect(self.onViewSTR)


        #Create content items
        contentAuthCnt = ContentGroup.contentItemFromQAction(self.contentAuthAct)
        contentAuthCnt.code = "E59F7CC1-0D0E-4EA2-9996-89DACBD07A83"

        userRoleMngtCnt = ContentGroup.contentItemFromQAction(self.usersAct)
        userRoleMngtCnt.code = "0CC4FB8F-70BA-4DE8-8599-FD344A564EB5"

        options_cnt = ContentGroup.contentItemFromQAction(self.options_act)
        options_cnt.code = "1520B989-03BA-4B05-BC50-A4C3EC7D79B6"
        
        backup_cnt = ContentGroup.contentItemFromQAction(self.backupAct)
        backup_cnt.code = "7BF21F68-A77C-4FC1-84F2-77B2DE27ED22"

        adminUnitsCnt = ContentGroup.contentItemFromQAction(self.manageAdminUnitsAct)
        adminUnitsCnt.code = "770EAC75-2BEC-492E-8703-34674054C246"

        downloadCnt = ContentGroup.contentItemFromQAction(self.downloadAct)
        downloadCnt.code = "bc6e22b1abfd3185d16cd3ba71cd80011ea3186c"

        importCnt = ContentGroup.contentItemFromQAction(self.importAct)
        importCnt.code = "3BBD6347-4A37-45D0-9B41-36D68D2CA4DB"

        exportCnt = ContentGroup.contentItemFromQAction(self.exportAct)
        exportCnt.code = "D0C34436-619D-434E-928C-2CBBDA79C060"

        documentDesignerCnt = ContentGroup.contentItemFromQAction(self.docDesignerAct)
        documentDesignerCnt.code = "C4826C19-2AE3-486E-9FF0-32C00A0A517F"

        documentGeneratorCnt = ContentGroup.contentItemFromQAction(self.docGeneratorAct)
        documentGeneratorCnt.code = "4C0C7EF2-5914-4FDE-96CB-089D44EDDA5A"

        spatialLayerManagerCnt = ContentGroup.contentItemFromQAction(self.spatialLayerManager)
        spatialLayerManagerCnt.code = "4E945EE7-D6F9-4E1C-X4AA-0C7F1BC67224"

        feature_details_cnt = ContentGroup.contentItemFromQAction(self.feature_details_act)
        feature_details_cnt.code = '2adff3f8-bda9-49f9-b37d-caeed9889ab6'

        wzdConfigCnt = ContentGroup.contentItemFromQAction(self.wzdAct)
        wzdConfigCnt.code = "F16CA4AC-3E8C-49C8-BD3C-96111EA74206"

        strViewCnt=ContentGroup.contentItemFromQAction(self.viewSTRAct)
        strViewCnt.code="D13B0415-30B4-4497-B471-D98CA98CD841"

        mobileFormgeneratorCnt = ContentGroup.contentItemFromQAction(self.mobile_form_act)
        mobileFormgeneratorCnt.code = "d93981ef-dec4-4597-8495-2941ec2e9a52"

        mobileFormImportCnt = ContentGroup.contentItemFromQAction(self.mobile_form_import)
        mobileFormImportCnt.code = "1394547d-fb6c-4f6e-80d2-53407cf7b7d4"

        username = data.app_dbconn.User.UserName

        if username == 'postgres':
            self.grant_privilege_base_tables(username)

        self.moduleCntGroup = None
        self.moduleContentGroups = []
        self._moduleItems = OrderedDict()
        self._reportModules = OrderedDict()

        for attrs in self.user_entities():
            self._moduleItems[attrs[2]] = attrs[0]

        for k, v in self._moduleItems.iteritems():
            moduleCntGroup = self._create_table_content_group(
                k, username, 'table.png'
            )
            self._reportModules[k] = v
            self.moduleContentGroups.append(moduleCntGroup)

        #create a separator
        tbSeparator = QAction(self.iface.mainWindow())
        tbSeparator.setSeparator(True)
        if not self.current_profile is None:
            if pg_table_exists(self.current_profile.social_tenure.name):
                # add separator to menu
                separator_group = TableContentGroup(username, 'separator', tbSeparator)
                #separator_group.register()
                self.moduleContentGroups.append(separator_group)

                moduleCntGroup = self._create_table_content_group(
                    QApplication.translate(
                        'STDMQGISLoader',
                        'New Social Tenure Relationship'
                    ),
                    username,
                    'new_str.png'
                )
                self.moduleContentGroups.append(moduleCntGroup)

        # Create content groups and add items
        self.contentAuthCntGroup = ContentGroup(username)
        self.contentAuthCntGroup.addContentItem(contentAuthCnt)
        self.contentAuthCntGroup.setContainerItem(self.contentAuthAct)
        self.contentAuthCntGroup.register()

        self.userRoleCntGroup = ContentGroup(username)
        self.userRoleCntGroup.addContentItem(userRoleMngtCnt)
        self.userRoleCntGroup.setContainerItem(self.usersAct)
        self.userRoleCntGroup.register()

        self.options_content_group = ContentGroup(username)
        self.options_content_group.addContentItem(options_cnt)
        self.options_content_group.setContainerItem(self.options_act)
        self.options_content_group.register()
        
        self.backup_content_group = ContentGroup(username)
        self.backup_content_group.addContentItem(backup_cnt)
        self.backup_content_group.setContainerItem(self.backupAct)
        self.backup_content_group.register()

        #Group admin settings content groups
        adminSettingsCntGroups = []
        adminSettingsCntGroups.append(self.contentAuthCntGroup)
        adminSettingsCntGroups.append(self.userRoleCntGroup)
        adminSettingsCntGroups.append(self.options_content_group)
        adminSettingsCntGroups.append(self.backup_content_group)

        self.adminUnitsCntGroup = ContentGroup(username)
        self.adminUnitsCntGroup.addContentItem(adminUnitsCnt)
        self.adminUnitsCntGroup.setContainerItem(self.manageAdminUnitsAct)
        self.adminUnitsCntGroup.register()

        self.spatialUnitManagerCntGroup = ContentGroup(username,self.spatialLayerManager)
        self.spatialUnitManagerCntGroup.addContentItem(spatialLayerManagerCnt)
        self.spatialUnitManagerCntGroup.register()

        self.feature_details_cnt_group = ContentGroup(username, self.feature_details_act)
        self.feature_details_cnt_group.addContentItem(feature_details_cnt)
        self.feature_details_cnt_group.register()

        self.wzdConfigCntGroup = ContentGroup(username, self.wzdAct)
        self.wzdConfigCntGroup.addContentItem(wzdConfigCnt)
        self.wzdConfigCntGroup.register()

        self.STRCntGroup = TableContentGroup(username,
                                             self.viewSTRAct.text(),
                                             self.viewSTRAct)
        self.STRCntGroup.createContentItem().code = "71EC2ED8-5D7F-4A27-8514-CFFE94E1294F"
        self.STRCntGroup.readContentItem().code = "ED607F24-11A2-427C-B395-2E2A3EBA4EBD"
        self.STRCntGroup.updateContentItem().code = "5D45A49D-F640-4A48-94D9-A10F502655F5"
        self.STRCntGroup.deleteContentItem().code = "15E27A59-28F7-42B4-858F-C070E2C3AE10"
        self.STRCntGroup.register()

        self.docDesignerCntGroup = ContentGroup(username, self.docDesignerAct)
        self.docDesignerCntGroup.addContentItem(documentDesignerCnt)
        self.docDesignerCntGroup.register()

        self.docGeneratorCntGroup = ContentGroup(username, self.docGeneratorAct)
        self.docGeneratorCntGroup.addContentItem(documentGeneratorCnt)
        self.docGeneratorCntGroup.register()

        self.downloadCntGroup = ContentGroup(username, self.downloadAct)
        self.downloadCntGroup.addContentItem(downloadCnt)
        self.downloadCntGroup.register()

        self.importCntGroup = ContentGroup(username, self.importAct)
        self.importCntGroup.addContentItem(importCnt)
        self.importCntGroup.register()

        self.exportCntGroup = ContentGroup(username, self.exportAct)
        self.exportCntGroup.addContentItem(exportCnt)
        self.exportCntGroup.register()

        #Create mobile content group
        self.mobileXformgenCntGroup = ContentGroup(username, self.mobile_form_act)
        self.mobileXformgenCntGroup.addContentItem(mobileFormgeneratorCnt)
        self.mobileXformgenCntGroup.register()

        self.mobileXFormImportCntGroup = ContentGroup(username, self.mobile_form_import)
        self.mobileXFormImportCntGroup.addContentItem(mobileFormImportCnt)
        self.mobileXFormImportCntGroup.register()

        # Group geoodk actions to one menu
        geoodkSettingsCntGroup = []
        geoodkSettingsCntGroup.append(self.mobileXformgenCntGroup)
        geoodkSettingsCntGroup.append(self.mobileXFormImportCntGroup)

        # Register document templates
        # Get templates for the current profile
        templates = documentTemplates()
        profile_tables = self.current_profile.table_names()
        for name, path in templates.iteritems():
            doc_temp = _DocumentTemplate.build_from_path(name, path)
            if doc_temp.data_source is None:
                continue
            if doc_temp.data_source.referenced_table_name in profile_tables:
                if not self._doc_temp_exist(doc_temp, self.profile_templates):
                    self.profile_templates.append(doc_temp)

            if doc_temp.data_source._dataSourceName in user_non_profile_views():
                if not self._doc_temp_exist(doc_temp, self.profile_templates):
                    self.profile_templates.append(doc_temp)

        template_content_group = ContentGroup(username)
        for template in self.profile_templates:
            #template_content = ContentGroup.contentItemFromName(template.name)
            template_content = self._create_table_content_group(
                    template.name,
                    self.current_user.UserName,
                    'templates'
                    )
            #template_content.code = template_content_group.hash_code(unicode(template.name))
            #template_content_group.addContentItem(template_content)
            #template_content.name = template.name
        #template_content_group.register()


        # Add Design Forms menu and tool bar actions
        self.toolbarLoader.addContent(self.wzdConfigCntGroup)
        self.menubarLoader.addContent(self.wzdConfigCntGroup)

        self.toolbarLoader.addContent(self.contentAuthCntGroup, [adminMenu, adminBtn])
        self.toolbarLoader.addContent(self.userRoleCntGroup, [adminMenu, adminBtn])
        self.toolbarLoader.addContent(self.options_content_group, [adminMenu, adminBtn])
        self.toolbarLoader.addContent(self.backup_content_group, [adminMenu, adminBtn])

        self.menubarLoader.addContents(adminSettingsCntGroups, [stdmAdminMenu, stdmAdminMenu])

        self.menubarLoader.addContent(self._action_separator())
        self.toolbarLoader.addContent(self._action_separator())

        self.menubarLoader.addContents(self.moduleContentGroups, [stdmEntityMenu, stdmEntityMenu])
        self.toolbarLoader.addContents(self.moduleContentGroups, [contentMenu, contentBtn])

        self.menubarLoader.addContent(self.spatialUnitManagerCntGroup)
        self.toolbarLoader.addContent(self.spatialUnitManagerCntGroup)

        self.toolbarLoader.addContent(self.feature_details_cnt_group)
        self.menubarLoader.addContent(self.feature_details_cnt_group)

        self.toolbarLoader.addContent(self.STRCntGroup)
        self.menubarLoader.addContent(self.STRCntGroup)

        self.toolbarLoader.addContent(self.adminUnitsCntGroup)
        self.menubarLoader.addContent(self.adminUnitsCntGroup)

        self.menubarLoader.addContent(self._action_separator())
        self.toolbarLoader.addContent(self._action_separator())

        self.toolbarLoader.addContent(self.downloadCntGroup)
        self.menubarLoader.addContent(self.downloadCntGroup)

        self.toolbarLoader.addContent(self.importCntGroup)
        self.menubarLoader.addContent(self.importCntGroup)

        self.toolbarLoader.addContent(self.exportCntGroup)
        self.menubarLoader.addContent(self.exportCntGroup)

        #Add mobile content to tool bar and menu
        self.menubarLoader.addContents(geoodkSettingsCntGroup, [geoodk_mobile_dataMenu, geoodk_mobile_dataMenu])
        self.toolbarLoader.addContents(geoodkSettingsCntGroup, [geoodkMenu, geoodkBtn])

        self.menubarLoader.addContent(self._action_separator())
        self.toolbarLoader.addContent(self._action_separator())

        self.toolbarLoader.addContent(self.docDesignerCntGroup)
        self.menubarLoader.addContent(self.docDesignerCntGroup)

        self.toolbarLoader.addContent(self.docGeneratorCntGroup)
        self.menubarLoader.addContent(self.docGeneratorCntGroup)

        #Load all the content in the container
        self.toolbarLoader.loadContent()
        self.menubarLoader.loadContent()

        # Add profiles_combobox in front of the configuration wizard
        self.combo_action = self.stdmInitToolbar.insertWidget(
            self.wzdAct, self.profiles_combobox
        )

        self.create_spatial_unit_manager()

        self.profile_status_message()

    def _doc_temp_exist(self, doc_temp, profile_templates):
        doc_exist = False
        for template in profile_templates:
            if template.name == doc_temp.name:
                doc_exist = True
                break
        return doc_exist

    def grant_privilege_base_tables(self, username):
        roles = []
        roleProvider = RoleProvider()
        roles = roleProvider.GetSysRoles()

        privilege_provider = SinglePrivilegeProvider('', current_profile() )
        for role in roles:
            privilege_provider.grant_privilege_base_table(role)


    def load_profiles_combobox(self):
        """
        Create a combobox and load existing profiles.
        """
        self.profiles_combobox = QComboBox(self.iface.mainWindow())
        if self.current_profile is None:
            return

        profile_names = self.stdm_config.profiles.keys()

        self.profiles_combobox.clear()

        self.profiles_combobox.addItems(profile_names)

        self.profiles_combobox.setStyleSheet(
            """
        QComboBox {
                border: 2px solid #4b85ca;
                border-radius: 0px;
                padding: 1px 3px 1px 3px;
                min-width: 6em;
            }
         QComboBox:editable {
             background: white;
         }

         QComboBox:!editable, QComboBox::drop-down:editable {
                 background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #f8f8f8, stop: 0.4 #eeeeee,
                                          stop: 0.5 #e6e6e6, stop: 1.0 #cecece);
         }

         /* QComboBox gets the "on" state when the popup is open */
         QComboBox:!editable:on, QComboBox::drop-down:editable:on {
                     background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                    stop: 0 #D3D3D3, stop: 0.4 #D8D8D8,
                                                    stop: 0.5 #DDDDDD, stop: 1.0 #E1E1E1);
         }

         QComboBox:on { /* shift the text when the popup opens */
             padding-top: 3px;
             padding-left: 4px;
         }

         QComboBox::drop-down {
             subcontrol-origin: padding;
             subcontrol-position: top right;
             width: 15px;

             border-left-width: 1px;
             border-left-color: darkgray;
             border-left-style: solid; /* just a single line */
             border-top-right-radius: 3px; /* same radius as the QComboBox */
             border-bottom-right-radius: 3px;
         }

         QComboBox::down-arrow {
             image: url(:/plugins/stdm/images/icons/down_arrow.png);
         }

         QComboBox::down-arrow:on { /* shift the arrow when popup is open */
             top: 1px;
             left: 1px;
         }
            """
        )
        setComboCurrentIndexWithText(
            self.profiles_combobox, self.current_profile.name
        )
        self.profiles_combobox.currentIndexChanged[str].connect(
            self.reload_plugin
        )

    def _create_table_content_group(self, k, username, icon):
        content_action = QAction(
            QIcon(":/plugins/stdm/images/icons/{}".format(icon)),
            k,
            self.iface.mainWindow()
        )
        moduleCntGroup = TableContentGroup(username, k, content_action)
        moduleCntGroup.register()
        return moduleCntGroup

    def check_spatial_tables(self, show_message=False):
        """
        Checks if spatial tables exist in the database.
        :param show_message: If true, shows an error message.
        :type show_message: Boolean
        :return: True if spatial tables exist and False with or
        without error message if it doesn't exist.
        :rtype: Boolean
        """
        # Get entities containing geometry
        # columns based on the config info
        if not self.current_profile is None:
            config_entities = self.current_profile.entities
            self.geom_entities = [
                ge for ge in config_entities.values()
                if ge.TYPE_INFO == 'ENTITY' and
                ge.has_geometry_column()
                ]


            self.sp_tables = spatial_tables()
            # Check whether the geometry tables
            # specified in the config exist
            missing_tables = [
                geom_entity.name
                for geom_entity in self.geom_entities
                if not geom_entity.name in self.sp_tables
            ]

            # Notify user of missing tables
            if len(missing_tables) > 0:
                if show_message:
                    msg = QApplication.translate(
                        'Spatial Unit Manager',
                        'The following spatial tables '
                        'are missing in the database:'
                        '\n {0}\n Do you want to re-run the '
                        'Configuration Wizard now?'.format(
                                '\n'.join(
                                missing_tables
                            )
                        )
                    )
                    title = QApplication.translate(
                        'STDMQGISLoader',
                        'Spatial Table Error'
                    )
                    database_check = QMessageBox.critical(
                        self.iface.mainWindow(),
                        title,
                        msg,
                        QMessageBox.Yes,
                        QMessageBox.No
                    )
                    if database_check == QMessageBox.Yes:
                        self.load_config_wizard()

                return False
            else:
                return True

    def create_spatial_unit_manager(
            self, menu_enable=False
    ):
        """
        Loads spatial unit manager after checking if
        spatial tables exist. If enabled from STDM toolbar
        and spatial tables don't exist show error message.
        :param menu_enable: Weather it is activated from the
        Menu or not. If True, an error could be show if spatial
        tables don't exist.
        :type menu_enable: Boolean
        :return: None
        :rtype: NoneType
        """
        self.remove_spatial_unit_mgr()
        if self.check_spatial_tables():
            self.spatialLayerMangerDockWidget = \
                SpatialUnitManagerDockWidget(
                    self.iface, self
                )
            self.spatialLayerMangerDockWidget.setWindowTitle(
                QApplication.translate(
                    "STDMQGISLoader",
                    'Spatial Unit Manager'
                )
            )
            self.iface.addDockWidget(
                Qt.LeftDockWidgetArea,
                self.spatialLayerMangerDockWidget
            )

            self.spatialLayerMangerDockWidget.show()
            self.spatialLayerManager.setChecked(True)
        else:
            if menu_enable:
                self.spatialLayerManager.setChecked(False)
                self.check_spatial_tables(True)

    def onActionAuthorised(self,name):
        '''
        This slot is raised when a toolbar action
        is authorised for access by the currently
        logged in user.
        '''
        pass

    def manageAccounts(self):
        '''
        Slot for showing the user and
        role accounts management window
        '''
        frmUserAccounts = manageAccountsDlg(self)
        frmUserAccounts.exec_()

    def contentAuthorization(self):
        '''
        Slot for showing the content authorization dialog
        '''
        frmAuthContent = contentAuthDlg(self)
        frmAuthContent.exec_()

    def on_sys_options(self):
        """
        Loads the dialog for settings STDM options.
        """
        opt_dlg = OptionsDialog(self.iface)
        opt_dlg._apply_btn.clicked.connect(
            lambda: self.reload_plugin(None)
        )
        opt_dlg.buttonBox.accepted.connect(
            lambda: self.reload_plugin(None)
        )

        opt_dlg.exec_()

    def profile_status_message(self):
        """
        Shows the name of the loaded profile in QGIS status bar.
        :return: None
        :rtype: NoneType
        """
        if self.current_profile is None:
            return
        if self.profile_status_label is None:
            self.profile_status_label = QLabel()
        profile_name = format_name(
            self.current_profile.name
        )
        message = QApplication.translate(
            'STDMPlugin',
            'Current STDM Profile: {}'.format(
                profile_name
            )
        )

        if self.profile_status_label.parent() is None:
            self.iface.mainWindow().statusBar().insertPermanentWidget(
                0,
                self.profile_status_label,
                10
            )
        self.profile_status_label.setText(message)

    def reload_plugin(self, sel_profile, load_from_stc=False):
        """
        Reloads STDM plugin without logging out.
        This is to allow modules capture changes
        made by the Configuration Wizard and Options.
        :param sel_profile: the selected profile name
        on the configuration wizard.
        :type: string
        """
        if not self._user_logged_in:
            return
        if self.toolbarLoader is not None:
            self.toolbarLoader.unloadContent()
            # Clear current profile combobox
            self.profiles_combobox.deleteLater()
            self.profiles_combobox = None

        if self.menubarLoader is not None:
            self.menubarLoader.unloadContent()
            self.stdmMenu.clear()
        if self.entity_browser is not None:
            self.entity_browser.close()

        self.logoutCleanUp(True)
        if load_from_stc:
            self.config_serializer.load()
        # Set current profile based on the selected
        # profile in the wizard
        if sel_profile is not None:
            if len(sel_profile) > 1:
                if not sel_profile is None:
                    new_profile_name = sel_profile
                current_profile_name = ''
                if not self.current_profile is None:
                    current_profile_name = self.current_profile.name 
                autochange_profile_configfile(
                    new_profile_name,
                    current_profile_name
                )
                save_current_profile(sel_profile)

        self.current_profile = current_profile()

        if not self.current_profile is None:

            LOGGER.debug(
                'Successfully changed '
                'the current profile to {}'.format(
                    self.current_profile.name
                )
            )
        try:
            self.loadModules()

            LOGGER.debug(
                'Successfully reloaded all modules.'
            )
        except SQLAlchemyError as ex:
            LOGGER.debug(
                str(ex)
            )
            STDMDb.instance().session.rollback()
            self.loadModules()

        except Exception as ex:
            LOGGER.debug(
                'Error Loading Modules: {}'.format(str(ex))
            )
            self.loadModules()

    def load_config_wizard(self):
        '''
        '''
        self.wizard = ConfigWizard(
            self.iface.mainWindow()
        )

        # Reload all modules
        self.wizard.wizardFinished.connect(self.reload_plugin)
        try:
            self.wizard.exec_()
        except Exception as ex:
            QMessageBox.critical(self.iface.mainWindow(),
                 QApplication.translate(
                     "STDMPlugin",
                     "Error Loading the Configuration Wizard"
                 ),
                 unicode(ex)
            )

    def changePassword(self):
        '''
        Slot for changing password
        '''
        #Load change password dialog
        frmPwdDlg = changePwdDlg(self)
        frmPwdDlg.exec_()

    def newSTR(self):
        '''
        Slot for showing the wizard for
        defining a new social
        tenure relationship
        '''
        try:

            str_editor = STREditor()
            str_editor.open()

        except Exception as ex:
            QMessageBox.critical(
                self.iface.mainWindow(),
                QApplication.translate(
                    'STDMQGISLoader',
                    'Error Loading the STR Editor'
                ),
                str(ex)
            )

    def onManageAdminUnits(self):
        '''
        Slot for showing administrative
        unit selector dialog.
        '''

        if self.current_profile is None:
            self.default_profile()
            return
        admin_spatial_unit = [
            e
            for e in
                self.current_profile.entities.values()
            if e.TYPE_INFO == 'ADMINISTRATIVE_SPATIAL_UNIT'
        ]
        db_status = self.entity_table_checker(
            admin_spatial_unit[0]
        )

        if db_status:
            frmAdminUnitSelector = AdminUnitSelector(
                self.iface.mainWindow()
            )
            frmAdminUnitSelector.setManageMode(True)
            frmAdminUnitSelector.exec_()
        else:
            return


    def onDocumentDesigner(self):
        """
        Slot raised to show new print
        composer with additional tools for designing
        map-based documents.
        """
        if self.current_profile is None:
            self.default_profile()
            return
        if len(db_user_tables(self.current_profile)) < 1:
            self.minimum_table_checker()
            return
        title = QApplication.translate(
            "STDMPlugin",
            "STDM Document Designer"
        )
        documentComposer = self.iface.createNewComposer(
            title
        )
        #Embed STDM customizations
        composerWrapper = ComposerWrapper(
            documentComposer, self.iface
        )
        composerWrapper.configure()

    def onDocumentGenerator(self):
        """
        Document generator by person dialog.
        """
        if self.current_profile is None:
            self.default_profile()
            return
        if len(db_user_tables(self.current_profile)) < 1:
            self.minimum_table_checker()
            return

        access_templates = []
        for pt in self.profile_templates:
            tcg = TableContentGroup(self.current_user.UserName, pt.name)
            if tcg.canRead():
                access_templates.append(pt.name)

        doc_gen_wrapper = DocumentGeneratorDialogWrapper(
            self.iface,
            access_templates,
            self.iface.mainWindow(),
            plugin=self
        )
        doc_gen_wrapper.exec_()

    def onDownload(self):
        doc_downloader = DocumentDownloader(self)
        doc_downloader.show()

    def onImportData(self):
        """
        Show import data wizard.
        """
        if self.current_profile is None:
            self.default_profile()
            return

        if len(db_user_tables(self.current_profile)) < 1:
            self.minimum_table_checker()
            return
        try:
            importData = ImportData(
                self.iface.mainWindow()
            )
            status = importData.exec_()
            if status == 1:
                if importData.geomClm.isEnabled():
                    canvas = self.iface.mapCanvas()
                    active_layer = self.iface.activeLayer()
                    if not active_layer is None:
                        canvas.zoomToFullExtent()
                        extent = active_layer.extent()
                        canvas.setExtent(extent)
        except Exception as ex:
            LOGGER.debug(unicode(ex))

    def onExportData(self):
        """
        Show export data dialog.
        """
        if self.current_profile is None:
            self.default_profile()
            return
        if len(db_user_tables(self.current_profile)) < 1:
            self.minimum_table_checker()
            return
        exportData = ExportData(self.iface.mainWindow())
        exportData.exec_()

    def onToggleSpatialUnitManger(self,toggled):
        '''
        Slot raised on toggling to activate/deactivate
        editing, and load corresponding
        spatial tools.
        '''
        self.spatialLayerManager.setChecked(False)

    def onViewSTR(self):
        '''
        Slot for showing widget that enables users to browse
        existing STRs.
        '''
        if self.current_profile == None:
            self.default_profile()
            return
        db_status = self.entity_table_checker(
            self.current_profile.social_tenure
        )

        if db_status:
            if self.viewSTRWin is None:
                self.viewSTRWin = ViewSTRWidget(self)
                self.viewSTRWin.show()
            else:
                self.viewSTRWin.showNormal()
                self.viewSTRWin.setFocus()


    def isSTDMLayer(self,layer):
        '''
        Return whether the layer is an STDM layer.
        '''
        if layer.id() in pg_layerNamesIDMapping().reverse:
            return True
        return False

    def widgetLoader(self, QAction):
        #Method to load custom forms
        tbList = self._moduleItems.values()

        dispName = QAction.text()
        if dispName == QApplication.translate(
                'STDMQGISLoader',
                'New Social Tenure Relationship'
        ):

            if self.current_profile is None:
                self.default_profile()
                return

            database_status = self.entity_table_checker(
                self.current_profile.social_tenure
            )

            if database_status:
                self.newSTR()
        else:
            table_name = self._moduleItems[dispName]
            if self.current_profile is None:
                self.default_profile()
                return
            sel_entity = self.current_profile.entity_by_name(
                table_name
            )

            database_status = self.entity_table_checker(
                sel_entity
            )

            QApplication.processEvents()

            try:
                if table_name in tbList and database_status:
                    cnt_idx = getIndex(
                        self._reportModules.keys(), dispName
                    )

                    table_content = TableContentGroup(self.current_user.UserName, dispName)
                    self.entity_browser = ContentGroupEntityBrowser(
                            sel_entity, table_content, self.iface.mainWindow(),  plugin=self)
                           
                    #self.entity_browser = EntityBrowserWithEditor(
                        #sel_entity,
                        #self.iface.mainWindow(),
                        #plugin=self
                    #)

                    if sel_entity.has_geometry_column():
                        self.entity_browser.show()
                    else:
                        self.entity_browser.exec_()
                else:
                    return

            except Exception as ex:
                QMessageBox.critical(
                    self.iface.mainWindow(),
                    QApplication.translate(
                        "STDMPlugin","Error Loading Entity Browser"
                    ),
                    QApplication.translate(
                        "STDMPlugin",
                        "Unable to load the entity in the browser. "
                        "Check if the entity is configured correctly. "
                        "Error: %s")%unicode(ex.message))
            finally:
                STDMDb.instance().session.rollback()

    def about(self):
        """
        STDM Description
        """
        plugin_manager = self.iface.pluginManagerInterface()
        stdm_metadata = plugin_manager.pluginMetadata('stdm')
        abtDlg = AboutSTDMDialog(self.iface.mainWindow(), stdm_metadata)
        abtDlg.exec_()

    def load_license_agreement(self):
        """
        Loads the license agreement dialog if the user
        have never accepted the terms and conditions.
        :return: True if the license agreement is
        accepted already and false if not accepted.
        :rtype: Boolean
        """
        license_agreement = LicenseAgreement(
            self.iface.mainWindow()
        )
        license_agreement.show_license()
        if license_agreement.accepted:
            return True
        else:
            return False

    def logout(self):
        """
        Logout the user and remove default user buttons when logged in
        """
        try:

            self.stdmInitToolbar.removeAction(self.logoutAct)
            self.stdmInitToolbar.removeAction(self.changePasswordAct)
            self.stdmInitToolbar.removeAction(self.wzdAct)
            self.stdmInitToolbar.removeAction(self.combo_action)
            self.stdmInitToolbar.removeAction(self.spatialLayerManager)
            self.feature_details_act.setChecked(False)
            self.stdmInitToolbar.removeAction(self.feature_details_act)
            self.stdmInitToolbar.removeAction(self.contentAuthAct)
            self.stdmInitToolbar.removeAction(self.usersAct)
            self.stdmInitToolbar.removeAction(self.options_act)
            self.stdmInitToolbar.removeAction(self.backupAct)
            self.stdmInitToolbar.removeAction(self.manageAdminUnitsAct)
            self.stdmInitToolbar.removeAction(self.downloadAct)
            self.stdmInitToolbar.removeAction(self.importAct)
            self.stdmInitToolbar.removeAction(self.exportAct)
            self.stdmInitToolbar.removeAction(self.docDesignerAct)
            self.stdmInitToolbar.removeAction(self.docGeneratorAct)
            self.stdmInitToolbar.removeAction(self.viewSTRAct)

            if self.toolbarLoader is not None:
                self.toolbarLoader.unloadContent()
            if self.menubarLoader is not None:
                self.menubarLoader.unloadContent()
                self.stdmMenu.clear()

            self.logoutCleanUp()
            self.initMenuItems()
            self.loginAct.setEnabled(True)
            self._user_logged_in = False
        except Exception as ex:
            LOGGER.debug(unicode(ex))


    def removeSTDMLayers(self):
        """
        Remove all STDM layers from the map registry.
        """
        mapLayers = QgsMapLayerRegistry.instance().mapLayers().values()

        for layer in mapLayers:
            if self.isSTDMLayer(layer):
                QgsMapLayerRegistry.instance().removeMapLayer(layer.id())

        self.stdmTables = []

    def logoutCleanUp(self, reload_plugin=False):
        """
        Clear database connection references and content items.
        :param reload_plugin: A boolean determining if the cleanup is
        called from reload_plugin method or not.
        :type reload_plugin: Boolean
        """
        try:
            if not self._user_logged_in:
                return

            #Remove STDM layers
            self.removeSTDMLayers()

            # Remove Spatial Unit Manager
            self.remove_spatial_unit_mgr()

            self.details_dock.close_dock()

            if not reload_plugin:
                self.profile_status_label.deleteLater()
                self.profile_status_label = None
                # Clear current profile combobox
                self.profiles_combobox.deleteLater()
                self.profiles_combobox = None
                #Clear singleton ref for SQLAlchemy connections
                if not data.app_dbconn is None:
                    STDMDb.cleanUp()
                    DeclareMapping.cleanUp()
                #Remove database reference
                data.app_dbconn = None
            else:
                self.profile_status_label.setText('')

            #Reset View STR Window
            if not self.viewSTRWin is None:
                del self.viewSTRWin
                self.viewSTRWin = None

            self.current_profile = None

        except Exception as ex:
            LOGGER.debug(unicode(ex))

    def remove_spatial_unit_mgr(self):
        """
        Removes spatial Unit Manger DockWidget.
        :return: None
        :rtype: NoneType
        """
        if self.spatialLayerMangerDockWidget:
            self.spatialLayerManager.setChecked(False)
            self.spatialLayerMangerDockWidget.close()
            self.spatialLayerMangerDockWidget.deleteLater()
        self.spatialLayerMangerDockWidget = None

    def user_entities(self):
        """
        Create a handler to read the current profile
        and return the table list
        """
        entities = []
        if self.current_profile is not None:
            entities = [
                (e.name, e.short_name, e.ui_display())
                for e in
                self.current_profile.entities.values()
                if (e.TYPE_INFO == 'ENTITY') and (e.user_editable)
            ]
        return entities

    def help_contents(self):
        """
        Load and open documentation manual
        """
        help_manual = u'{0}/stdm.chm'.format(self.plugin_dir)
        try:
            os.startfile(
                help_manual,'open'
            )
        except Exception as ex:
            QMessageBox.critical(
                self.iface.mainWindow(),
                QApplication.translate(
                    "STDMQGISLoader",
                    'Open Error'
                ),
                unicode(ex)
            )
            
    def manual_backup(self):
        """
        Perform a manual backup of the database and configuration when the backup button is clicked.
        """
        try:
            # Ask for confirmation
            result = QMessageBox.question(
                self.iface.mainWindow(),
                QApplication.translate("STDMQGISLoader", "Database Backup"),
                QApplication.translate("STDMQGISLoader", "Do you want to backup the database and configuration now?"),
                QMessageBox.Yes | QMessageBox.No
            )
            
            if result == QMessageBox.No:
                return
                
            # Get required parameters for backup
            from datetime import datetime
            from stdm.settings.registryconfig import config_file_name, backup_path, pg_bin_path
            from stdm.data.config import DatabaseConfig
            
            datetime_prfx = datetime.now().strftime('%Y%m%d%H%M%S%f_')
            config_file = config_file_name()
            backup_out_path = backup_path()
            pgbin_path = pg_bin_path()
            
            # Get database connection info
            db_conn = DatabaseConfig().read()
            if db_conn is None:
                QMessageBox.critical(
                    self.iface.mainWindow(),
                    QApplication.translate("STDMQGISLoader", "Backup Error"),
                    QApplication.translate("STDMQGISLoader", "Unable to read database connection info.")
                )
                return
                
            # Perform the backup
            progress = QProgressDialog(
                QApplication.translate("STDMQGISLoader", "Backing up database and configuration..."),
                QApplication.translate("STDMQGISLoader", "Cancel"),
                0, 0, 
                self.iface.mainWindow()
            )
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            
            # Backup config file
            backup_config(datetime_prfx, config_file, backup_out_path)
            
            # Backup database
            backup_database(
                datetime_prfx,
                pgbin_path,
                db_conn.Host,
                db_conn.Port,
                db_conn.Database,
                backup_out_path
            )
            
            progress.close()
            
            # Show success message with backup location
            QMessageBox.information(
                self.iface.mainWindow(),
                QApplication.translate("STDMQGISLoader", "Backup Completed"),
                QApplication.translate("STDMQGISLoader", 
                    "Database and configuration successfully backed up to:\n{}").format(backup_out_path)
            )
            
        except Exception as ex:
            QMessageBox.critical(
                self.iface.mainWindow(),
                QApplication.translate("STDMQGISLoader", "Backup Error"),
                QApplication.translate("STDMQGISLoader", "An error occurred during backup:\n{}").format(str(ex))
            )

    def reset_content_modules_id(self, title, message_text):
        return QMessageBox.critical(
            self.iface.mainWindow(), title,
            QApplication.translate(
                "STDMQGISLoader",
                unicode(message_text)
            )
        )

    def _action_separator(self):
        """
        :return: Toolbar or menu separator
        :rtype: QAction
        """
        separator = QAction(self.iface.mainWindow())
        separator.setSeparator(True)

        return separator

    def spatialLayerMangerActivate(self):
        if self.spatialLayerMangerDockWidget is None:
            self.create_spatial_unit_manager(True)
        else:
            if self.spatialLayerMangerDockWidget.isVisible():
                self.spatialLayerMangerDockWidget.hide()
            else:
                self.spatialLayerMangerDockWidget.show()

    def config_loader(self):
        """
        Method to provide access to config elements through the handler class
        :return:class: config handler class
        """
        handler = ConfigTableReader()
        return handler

    def mobile_form_generator(self):
        """
        Load the dialog to generate form for mobile data collection
        :return:
        """
        converter_dlg = GeoODKConverter(self.iface.mainWindow())
        converter_dlg.exec_()

    def mobile_form_importer(self):
        """
        Load the dialog to generate form for mobile data collection
        :return:
        """
        importer_dialog = ProfileInstanceRecords(self.iface.mainWindow())
        importer_dialog.exec_()

    def default_config_version(self):
        handler = self.config_loader()
        config_version = handler.read_config_version()
        if float(config_version) < 1.2:
            msg_title = QApplication.translate("STDMQGISLoader",
                                                    "Config file version")
            msg = QApplication.translate("STDMQGISLoader",
                                             "Your configuration file is "
                                             "older than the current stdm "
                                             "version, do you want to backup"
                                             "the configuration and database"
                                             "data")
            if QMessageBox.information(None, msg_title, msg,
                                            QMessageBox.Yes |
                                            QMessageBox.No) == QMessageBox.Yes:
                pass

        if config_version is None:
            msg_title = QApplication.translate("STDMQGISLoader",
                                                    "Update config file")
            msg = QApplication.translate("STDMQGISLoader", "The config "
                                              "version installed is old and "
                                              "outdated STDM will try to "
                                              "apply the required updates")
            if QMessageBox.information(None, msg_title, msg,
                                            QMessageBox.Yes |
                                            QMessageBox.No) == QMessageBox.Yes:
                handler.update_config_file()
            else:
                err_msg = QApplication.translate("STDMQGISLoader",
                                                     "STDM has detected that "
                                                     "the version of config "
                                                     "installed is old and "
                                                     "outdated. Delete "
                                                     "existing configuration "
                                                     "folder or xml file and "
                                                     "restart QGIS.")
                raise ConfigVersionException(err_msg)

