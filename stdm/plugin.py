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
import shutil
from collections import OrderedDict

from qgis.PyQt.QtCore import (
    QSettings,
    QFile,
    QFileInfo,
    QTranslator,
    QCoreApplication,
    Qt,
    QStandardPaths,
    QDir
)
from qgis.PyQt.QtGui import (
    QKeySequence
)
from qgis.PyQt.QtWidgets import (
    QApplication,
    QAction,
    QMenu,
    QLabel,
    QMessageBox,
    QToolButton,
    QDialog,
    QComboBox
)
from qgis.core import (
    QgsProject,
    QgsMapLayer,
    QgsApplication,
    QgsTask
)
from qgis.gui import (
    QgsLayoutDesignerInterface
)
from sqlalchemy.exc import SQLAlchemyError

from stdm.composer.composer_wrapper import ComposerWrapper
from stdm.composer.custom_layout_items import StdmCustomLayoutItems
from stdm.composer.document_template import DocumentTemplate
from stdm.data import globals
from stdm.data.configfile_paths import FilePaths
from stdm.data.configuration.column_updaters import varchar_updater
from stdm.data.configuration.config_updater import ConfigurationSchemaUpdater
from stdm.data.configuration.exception import ConfigurationException
from stdm.data.configuration.stdm_configuration import StdmConfiguration
from stdm.data.database import (
    STDMDb
)
from stdm.data.database import alchemy_table
from stdm.data.pg_utils import (
    pg_table_exists,
    spatial_tables,
    postgis_exists,
    create_postgis,
    table_column_names
)
from stdm.exceptions import DummyException
from stdm.mapping.utils import pg_layerNamesIDMapping
from stdm.navigation.components import STDMAction
from stdm.navigation.container_loader import (
    QtContainerLoader,
    ContentGroup)
from stdm.navigation.content_group import TableContentGroup
from stdm.security.privilege_provider import SinglePrivilegeProvider
from stdm.security.roleprovider import RoleProvider
from stdm.security.user import User
from stdm.settings import current_profile, save_current_profile
from stdm.settings.config_file_updater import ConfigurationFileUpdater
from stdm.settings.config_serializer import ConfigurationFileSerializer
from stdm.settings.registryconfig import (
    RegistryConfig,
    WIZARD_RUN,
    STDM_VERSION,
    CONFIG_UPDATED,
    HOST,
    composer_template_path,
    run_template_converter_on_startup
)
from stdm.settings.startup_handler import copy_startup
from stdm.settings.template_updater import TemplateFileUpdater
from stdm.ui.about import AboutSTDMDialog
from stdm.ui.admin_unit_selector import AdminUnitSelector
from stdm.ui.change_log import ChangeLog
from stdm.ui.change_pwd_dlg import changePwdDlg
from stdm.ui.composer.custom_item_gui import StdmCustomLayoutGuiItems
from stdm.ui.composer.layout_gui_utils import LayoutGuiUtils
from stdm.ui.content_auth_dlg import contentAuthDlg
from stdm.ui.doc_generator_dlg import (
    DocumentGeneratorDialogWrapper
)
from stdm.ui.entity_browser import (
    ContentGroupEntityBrowser
)
from stdm.ui.export_data import ExportData
from stdm.ui.feature_details import (
    DetailsDockWidget
)
from stdm.ui.geoodk_converter_dialog import GeoODKConverter
from stdm.ui.geoodk_profile_importer import ProfileInstanceRecords
from stdm.ui.gui_utils import GuiUtils
from stdm.ui.import_data import ImportData
from stdm.ui.license_agreement import LicenseAgreement
from stdm.ui.login_dlg import loginDlg
from stdm.ui.manage_accounts_dlg import manageAccountsDlg
from stdm.ui.options_base import OptionsDialog
from stdm.ui.db_profile_backup import DBProfileBackupDialog
from stdm.ui.profile_backup_restore import ProfileBackupRestoreDialog
from stdm.ui.switch_config import SwitchConfiguration
from stdm.ui.progress_dialog import STDMProgressDialog
from stdm.ui.social_tenure.str_editor import STREditor
from stdm.ui.spatial_unit_manager import SpatialUnitManagerDockWidget
from stdm.ui.stdmdialog import DeclareMapping
from stdm.ui.view_str import ViewSTRWidget
from stdm.ui.wizard.wizard import ConfigWizard
from stdm.utils.layer_utils import LayerUtils
from stdm.utils.util import (
    getIndex,
    db_user_tables,
    format_name,
    value_from_metadata,
    documentTemplates,
    user_non_profile_views
)
from stdm.utils.util import simple_dialog

from stdm.composer.template_converter import (
        TemplateConverterTask
)

LOGGER = logging.getLogger('stdm')

TEST = False

class STDMQGISLoader:
    viewSTRWin = None

    def __init__(self, iface):
        self.iface = iface

        # Initialize loader
        self.toolbarLoader = None
        self.menubarLoader = None
        self.details_dock_widget = None
        self.combo_action = None
        self.stdmInitToolbar = None
        self.stdmMenu = None
        self.progress = None
        self.spatialLayerManagerDockWidget = self

        # Setup locale
        self.plugin_dir = os.path.dirname(__file__)
        localePath = ""
        locale = (QSettings().value("locale/userLocale") or 'en-US')[0:2]
        if QFileInfo(self.plugin_dir).exists():
            # Replace forward slash with backslash
            self.plugin_dir = self.plugin_dir.replace("\\", "/")
            localePath = self.plugin_dir + "/i18n/stdm_%s.qm" % (locale,)
        if QFileInfo(localePath).exists():
            self.translator = QTranslator()
            self.translator.load(localePath)
            QCoreApplication.installTranslator(self.translator)

        StdmCustomLayoutItems.add_custom_item_types()
        StdmCustomLayoutGuiItems.register_gui()

        # STDM Tables
        self.stdmTables = []
        self.stdm_config = StdmConfiguration.instance()
        self.reg_config = RegistryConfig()
        self.spatialLayerMangerDockWidget = None

        self._user_logged_in = False
        self.current_profile = None

        self.profile_templates = []

        self.action_cache = {}

        # Profile status label showing the current profile
        self.profile_status_label = None
        LOGGER.debug('STDM plugin has been initialized.')
        self.entity_browser = None
        # Load configuration file
        self.config_path = QStandardPaths.standardLocations(QStandardPaths.HomeLocation)[0] \
                           + '/.stdm/configuration.stc'
        self.config_serializer = ConfigurationFileSerializer(self.config_path)
        self.configuration_file_updater = ConfigurationFileUpdater(self.iface)
        copy_startup()


    def initGui(self):
        # Initial actions on starting up the application
        self._menu_items()
        self.loginAct = STDMAction(GuiUtils.get_icon('login.png'),
                                   QApplication.translate("LoginToolbarAction",
                                                          "Login"),
                                   self.iface.mainWindow(),
                                   "CAA4F0D9-727F-4745-A1FC-C2173101F711")
        self.loginAct.setShortcut(QKeySequence(Qt.Key_F2))

        self.aboutAct = STDMAction(GuiUtils.get_icon('info.png'),
                                   QApplication.translate("AboutToolbarAction", "About"),
                                   self.iface.mainWindow(),
                                   "137FFB1B-90CD-4A6D-B49E-0E99CD46F784")
        # Define actions that are available to all logged in users
        self.logoutAct = STDMAction(GuiUtils.get_icon('logout.png'),
                                    QApplication.translate("LogoutToolbarAction", "Logout"),
                                    self.iface.mainWindow(),
                                    "EF3D96AF-F127-4C31-8D9F-381C07E855DD")

        self.changePasswordAct = STDMAction(GuiUtils.get_icon('change_password.png'),
                                            QApplication.translate("ChangePasswordToolbarAction", "Change Password"),
                                            self.iface.mainWindow(),
                                            "8C425E0E-3761-43F5-B0B2-FB8A9C3C8E4B")
        self.helpAct = STDMAction(GuiUtils.get_icon("help-content.png"),
                                  QApplication.translate("STDMQGISLoader", "Help Contents"),
                                  self.iface.mainWindow(),
                                  "7A61CEA9-2A64-45F6-A40F-D83987D416EB")
        self.helpAct.setShortcut(Qt.Key_F10)
        

        # connect the actions to their respective methods
        self.loginAct.triggered.connect(self.login)
        self.changePasswordAct.triggered.connect(self.changePassword)
        self.logoutAct.triggered.connect(self.logout)
        self.aboutAct.triggered.connect(self.about)
        self.helpAct.triggered.connect(self.help_contents)

        self.iface.layoutDesignerOpened.connect(self.on_designer_opened)
        self.iface.layoutDesignerWillBeClosed.connect(self.on_designer_closed)
        self.iface.currentLayerChanged.connect(self.on_layer_changed)

        self.initToolbar()
        self.initMenuItems()

        self.init_qgis_hooks()

    def init_qgis_hooks(self):
        """
        Initialises hooks into QGIS gui signals
        """
        QgsProject.instance().layerWasAdded.connect(self._on_layer_added)

    def _on_layer_added(self, layer: QgsMapLayer):
        """
        Triggered when a layer is added to the project
        """
        if layer is None:
            return

        if layer.type() != QgsMapLayer.VectorLayer or not LayerUtils.is_layer_stdm_layer(layer):
            # we don't care about this layer, users can edit however they want...
            return

        # this is an STDM layer, and user is not logged in -- prevent editing of the layer
        if not self._user_logged_in:
            layer.setReadOnly(True)

    def _menu_items(self):
        # Create menu and menu items on the menu bar
        self.stdmMenu = QMenu()
        self.stdmMenu.setTitle(
            QApplication.translate(
                "STDMQGISLoader", "STDM"
            )
        )
        # Initialize the menu bar item
        self.menu_bar = self.iface.mainWindow().menuBar()
        # Create actions
        actions = self.menu_bar.actions()
        currAction = actions[len(actions) - 1]
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

    def initToolbar(self):
        # Load initial STDM toolbar
        self.stdmInitToolbar = self.iface.addToolBar("STDM")
        self.stdmInitToolbar.setObjectName("STDM")
        # Add actions to the toolbar
        self.stdmInitToolbar.addAction(self.loginAct)

        self.stdmInitToolbar.addSeparator()
        self.stdmInitToolbar.addAction(self.helpAct)
        self.stdmInitToolbar.addAction(self.aboutAct)

        self.git_branch = QLabel(self.iface.mainWindow())
        self.git_branch.setText(self.active_branch_name())
        self.stdmInitToolbar.addWidget(self.git_branch)

    def active_branch_name(self):
        home = QStandardPaths.standardLocations(QStandardPaths.HomeLocation)[0]
        branch_file = '{}/.stdm/.branch180'.format(home)
        branch_name = ''
        if QFile.exists(branch_file):
            with open(branch_file) as bf:
                bf.seek(0)
                # Get first character to see if file is empty
                first_char = bf.read(1)
                if first_char:
                    # Reset cursor position
                    bf.seek(0)
                    branch_name = ' [' + [line.strip() for line in open(branch_file)][0] + ']'

        return branch_name

    def initMenuItems(self):
        self.stdmMenu.addAction(self.loginAct)
        self.stdmMenu.addSeparator()
        self.stdmMenu.addAction(self.helpAct)
        self.stdmMenu.addAction(self.aboutAct)

    def unload(self):
        # Remove the STDM toolbar
        if self.stdmInitToolbar is not None:
            self.stdmInitToolbar.deleteLater()
            self.stdmInitToolbar = None

        if self.stdmMenu is not None:
            self.stdmMenu.deleteLater()
            self.stdmMenu = None

        if self.details_dock_widget is not None:
            self.details_dock_widget.remove_connections()
            self.details_dock_widget.deleteLater()
            self.details_dock_widget = None

        self.remove_spatial_unit_mgr()

        if self.profile_status_label is not None:
            self.profile_status_label.deleteLater()
            self.profile_status_label = None

        self.iface.layoutDesignerOpened.disconnect(self.on_designer_opened)

        # Remove connection info
        self.logoutCleanUp()

    def login(self):
        """
        Show login dialog
        """
        frmLogin = loginDlg(self.iface.mainWindow())

        login_status = 0

        if TEST:
            login_status = frmLogin.test_mode()
        else:
            login_status = frmLogin.exec_()

        if login_status == QDialog.Accepted:

            # Assign the connection object
            globals.APP_DBCONN = frmLogin.dbConn

            User.CURRENT_USER = frmLogin.dbConn.User

            # Initialize the whole STDM database
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
                            "STDM", "Spatial Extension Error"
                        ),
                        err_msg
                    )

                    return

            # Checks if the license is accepted and stops loading
            # modules if the terms and conditions are never accepted.
            license_status = self.load_license_agreement()
            if not license_status:
                return

            # Load logout and change password actions
            self.stdmInitToolbar.insertAction(self.loginAct,
                                              self.logoutAct)
            self.stdmInitToolbar.insertAction(self.loginAct,
                                              self.changePasswordAct)

            self.stdmMenu.insertAction(self.loginAct, self.logoutAct)
            self.stdmMenu.insertAction(self.loginAct, self.changePasswordAct)

            self.loginAct.setEnabled(False)

            # Fetch STDM tables
            self.stdmTables = spatial_tables()

            # Load the configuration from file
            config_load_status = self.load_configuration_from_file(
                self.iface.mainWindow()
            )

            # Exit if the load failed
            if not config_load_status:
                return
            try:
                self.show_change_log()
                # Set current profile
                self.current_profile = current_profile()
                self._user_logged_in = True
                if self.current_profile is None:
                    result = self.default_profile()
                    if not result:
                        return

                LayerUtils.enable_editing_of_stdm_layers(True)
                self.create_custom_tenure_dummy_col()

                self.loadModules()
                self.default_profile()
                self.run_wizard()

                self.copy_designer_template()

                # Start QGIS2 to QGIS3 template converter
                if run_template_converter_on_startup():
                    self.start_q2toq3_template_conversion()

            except DummyException as pe:
                title = QApplication.translate(
                    "STDMQGISLoader",
                    "Error Loading Modules"
                )

                self.reset_content_modules_id(title, pe)

    def start_q2toq3_template_conversion(self):
        template_path = '{}{}'.format(composer_template_path(),'/')
        template_conversion_task = TemplateConverterTask(template_path)

        qgs_app = QgsApplication.instance()
        task_manager = qgs_app.taskManager()
        task_manager.addTask(template_conversion_task)

        template_conversion_task.statusChanged.connect(
                self.template_conversion_status_changed
                )

        QgsApplication.processEvents()


    def template_conversion_status_changed(self, status):
        # Show message in the status bar
        title = QApplication.translate(
                'STDMQGISLoader', 'Template Conversion')

        message_bar = self.iface.messageBar()
        message_bar.clearWidgets()
        if status == QgsTask.Running:
            message_bar.pushInfo(title, 
                    QApplication.translate('STDMQGISLoader',
                        'Process started...'))

        elif status == QgsTask.Terminated:
            message_bar.pushWarning(title, 
                    QApplication.translate('STDMQGISLoader',
                        'Process terminated due to an error.'))

        elif status == QgsTask.Complete:
            message_bar.pushSuccess(title, 
                    QApplication.translate('STDMQGISLoader',
                        'Process completed successfully'))


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
                'The system has detected that '
                'a required database table - \n'
                '{} is missing. \n'
                'Do you want to re-run the '
                'Configuration Wizard now?'.format(
                    entity.name
                ),
                None
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
            'The system has detected that '
            'a required database table - \n'
            '{} is missing. \n'
            'Do you want to re-run the '
            'Configuration Wizard now?'.format(
                entity.short_name
            ),
            None
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

        if host_val not in ['localhost', '127.0.0.1']:
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
                profile_name = list(profiles.keys())[0]
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
        if self.progress is not None:
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

        if self.progress is not None:
            self.progress.deleteLater()
            self.progress = None

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
                                 str(io_err))

            return False

        except ConfigurationException as c_ex:
            QMessageBox.critical(
                self.iface.mainWindow(),
                QApplication.translate(
                    'STDM',
                    'Load Configuration Error'
                ),
                str(c_ex)
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
        version = value_from_metadata('version')
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

        if templates_path is None:
            return

        for temp_file in template_files:
            destination_file = os.path.join(
                templates_path, os.path.basename(temp_file))

            if not os.path.isfile(destination_file):
                try:
                    shutil.copyfile(temp_file, destination_file)
                except IOError:
                    os.makedirs(templates_path)
                    shutil.copyfile(temp_file, destination_file)

    def load_configuration_from_file(self, parent, manual=False) -> bool:
        """
        Load configuration object from the file.
        :return: True if the file was successfully loaded. Otherwise, False.
        """
        if self.progress is not None:
            self.progress.deleteLater()
            self.progess = None

        self.progress = STDMProgressDialog(parent)
        self.progress.overall_progress('Upgrading STDM Configuration...')

        home = QStandardPaths.standardLocations(QStandardPaths.HomeLocation)[0]

        config_path = '{}/.stdm/configuration.stc'.format(home)

        if manual:
            #parent.upgradeButton.setEnabled(False)
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

                self.configuration_file_updater. \
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
                for profile, tables in profile_details_dict.items():
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
                first_profile = list(profile_details_dict.keys())[0]
                if manual:
                    #parent.upgradeButton.setEnabled(True)
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
            if manual:
                #parent.upgradeButton.setEnabled(False)
                parent.manage_upgrade()
            self.configuration_file_updater. \
                _copy_config_file_from_template()

            result = self.load_configuration_to_serializer()
            if self.progress is not None:
                self.progress.deleteLater()
            self.progress = None
            return result

    def loadModules(self):
        """
        Define and add modules to the menu and/or toolbar using the module loader
        """

        self.toolbarLoader = QtContainerLoader(self.iface.mainWindow(),
                                               self.stdmInitToolbar, self.logoutAct)
        self.menubarLoader = QtContainerLoader(self.iface.mainWindow(),
                                               self.stdmMenu, self.logoutAct)
        # Connect to the content added signal
        # self.toolbarLoader.contentAdded.connect(self.onContentAdded)

        # Define containers for grouping actions
        adminBtn = QToolButton()
        adminObjName = QApplication.translate("ToolbarAdminSettings", "Admin Settings")
        # Required by module loader for those widgets that need to be inserted into the container
        adminBtn.setObjectName(adminObjName)
        adminBtn.setToolTip(adminObjName)
        adminBtn.setIcon(GuiUtils.get_icon("settings.png"))
        adminBtn.setPopupMode(QToolButton.InstantPopup)

        adminMenu = QMenu(adminBtn)
        adminBtn.setMenu(adminMenu)

        # Settings menu container in STDM's QGIS menu
        stdmAdminMenu = QMenu(self.stdmMenu)
        stdmAdminMenu.setIcon(GuiUtils.get_icon("settings.png"))
        stdmAdminMenu.setObjectName("STDMAdminSettings")
        stdmAdminMenu.setTitle(QApplication.translate("ToolbarAdminSettings", "Admin Settings"))

        # Configuration Manager
        config_managmt_menu = QMenu(self.stdmMenu)
        config_managmt_menu.setIcon(GuiUtils.get_icon("settings.png"))
        config_managmt_menu.setObjectName("ConfigManagmt")
        config_managmt_menu.setTitle(QApplication.translate("TollbarConfigManagmt", "Configuration Management"))
        
        config_managmt_menu.addSeparator()

        adminMenu.addMenu(config_managmt_menu)
        stdmAdminMenu.addMenu(config_managmt_menu)
        

        # Create content menu container
        contentBtn = QToolButton()

        contentObjName = QApplication.translate("ToolbarAdminSettings", "Entities")
        # Required by module loader for those widgets that need to be inserted into the container
        contentBtn.setObjectName(contentObjName)
        contentBtn.setToolTip(contentObjName)
        contentBtn.setIcon(GuiUtils.get_icon("entity_management.png"))
        contentBtn.setPopupMode(QToolButton.InstantPopup)

        contentMenu = QMenu(contentBtn)
        contentBtn.setMenu(contentMenu)

        stdmEntityMenu = QMenu(self.stdmMenu)
        stdmEntityMenu.setObjectName("STDMEntityMenu")
        stdmEntityMenu.setIcon(GuiUtils.get_icon("entity_management.png"))
        stdmEntityMenu.setTitle(QApplication.translate("STDMEntityMenu", "Entities"))

        # Mobile menu container
        # Mobile content menu container
        geoodk_mobile_dataMenu = QMenu(self.stdmMenu)
        geoodk_mobile_dataMenu.setObjectName("MobileMenu")
        geoodk_mobile_dataMenu.setIcon(GuiUtils.get_icon("mobile_data_management.png"))
        geoodk_mobile_dataMenu.setTitle(QApplication.translate("GeoODKMobileSettings", "Mobile Data Forms"))

        geoodkBtn = QToolButton()
        adminObjName = QApplication.translate("MobileToolbarSettings", "Mobile Data Forms")
        # Required by module loader for those widgets that need to be inserted into the container
        geoodkBtn.setObjectName(adminObjName)
        geoodkBtn.setToolTip(adminObjName)
        geoodkBtn.setIcon(GuiUtils.get_icon("mobile_data_management.png"))
        geoodkBtn.setPopupMode(QToolButton.InstantPopup)

        geoodkMenu = QMenu(geoodkBtn)
        geoodkBtn.setMenu(geoodkMenu)
        # Define actions

        self.contentAuthAct = QAction(
            GuiUtils.get_icon("content_auth.png"),
            QApplication.translate(
                "ContentAuthorizationToolbarAction",
                "Content Authorization"
            ),
            self.iface.mainWindow()
        )

        self.usersAct = QAction(GuiUtils.get_icon("users_manage.png"),
                                QApplication.translate("ManageUsersToolbarAction", "Manage Users-Roles"),
                                self.iface.mainWindow())

        self.options_act = QAction(GuiUtils.get_icon("options.png"),
                                   QApplication.translate("OptionsToolbarAction", "Options"),
                                   self.iface.mainWindow())

        self.profile_db_backup_act = QAction(GuiUtils.get_icon("export.png"),
                                 QApplication.translate("ProfileBackupAction", "Backup"),
                                 self.iface.mainWindow())

        self.profile_backup_restore_act = QAction(GuiUtils.get_icon("import.png"),
                                 QApplication.translate("ProfileBackupRestoreAction", "Restore"),
                                 self.iface.mainWindow())

        self.switch_config_act = QAction(GuiUtils.get_icon("switch.png"),
                                         QApplication.translate("ProfileBackupRestoreAction", "Switch Configuration"),
                                         self.iface.mainWindow())

        self.manageAdminUnitsAct = QAction(
            GuiUtils.get_icon("manage_admin_units.png"),
            QApplication.translate(
                "ManageAdminUnitsToolbarAction",
                "Manage Administrative Units"
            ),
            self.iface.mainWindow()
        )

        self.importAct = QAction(GuiUtils.get_icon("import.png"),
                                 QApplication.translate("ImportAction", "Import Data"), self.iface.mainWindow())

        self.exportAct = QAction(GuiUtils.get_icon("export.png"),
                                 QApplication.translate("ReportBuilderAction", "Export Data"), self.iface.mainWindow())

        self.docDesignerAct = QAction(GuiUtils.get_icon("cert_designer.png"),
                                      QApplication.translate("DocumentDesignerAction", "Document Designer"),
                                      self.iface.mainWindow())
        self.docDesignerAct.setShortcut(QKeySequence(Qt.Key_F3))

        self.docGeneratorAct = QAction(GuiUtils.get_icon("generate_document.png"),
                                       QApplication.translate("DocumentGeneratorAction", "Document Generator"),
                                       self.iface.mainWindow())
        self.docGeneratorAct.setShortcut(QKeySequence(Qt.Key_F4))

        # Spatial Layer Manager
        self.spatialLayerManager = QAction(GuiUtils.get_icon("spatial_unit_manager.png"),
                                           QApplication.translate("SpatialEditorAction", "Spatial Unit Manager"),
                                           self.iface.mainWindow())
        self.spatialLayerManager.setCheckable(True)

        # Spatial Layer Manager
        self.feature_details_act = QAction(GuiUtils.get_icon("feature_details.png"),
                                           QApplication.translate("SpatialEditorAction", "Spatial Entity Details"),
                                           self.iface.mainWindow())
        self.feature_details_act.setCheckable(True)

        self.viewSTRAct = QAction(GuiUtils.get_icon("view_str.png"),
                                  QApplication.translate("ViewSTRToolbarAction", "View Social Tenure Relationship"),
                                  self.iface.mainWindow())

        self.wzdAct = QAction(GuiUtils.get_icon("table_designer.png"),
                              QApplication.translate("ConfigWizard", "Configuration Wizard"), self.iface.mainWindow())
        self.wzdAct.setShortcut(Qt.Key_F7)
        self.ModuleAct = QAction(GuiUtils.get_icon("table_designer.png"),
                                 QApplication.translate("WorkspaceConfig", "Entities"), self.iface.mainWindow())

        self.mobile_form_act = QAction(GuiUtils.get_icon("mobile_collect.png"),
                                       QApplication.translate("MobileFormGenerator", "Generate Mobile Form"),
                                       self.iface.mainWindow())
        self.mobile_form_import = QAction(GuiUtils.get_icon("mobile_import.png"),
                                          QApplication.translate("MobileFormGenerator", "Import Mobile Data"),
                                          self.iface.mainWindow())

        self.details_dock_widget = DetailsDockWidget(map_canvas=self.iface.mapCanvas(), plugin=self)
        self.details_dock_widget.setToggleVisibilityAction(self.feature_details_act)
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.details_dock_widget)
        self.details_dock_widget.setUserVisible(False)
        self.details_dock_widget.init_connections()

        # Add current profiles to profiles combobox
        self.load_profiles_combobox()

        # Connect the slots for the actions above
        self.contentAuthAct.triggered.connect(self.contentAuthorization)
        self.usersAct.triggered.connect(self.manageAccounts)
        self.options_act.triggered.connect(self.on_sys_options)
        self.profile_db_backup_act.triggered.connect(self.on_profile_db_backup)
        self.profile_backup_restore_act.triggered.connect(self.on_profile_backup_restore)
        self.switch_config_act.triggered.connect(self.on_switch_config)
        self.manageAdminUnitsAct.triggered.connect(self.onManageAdminUnits)
        self.exportAct.triggered.connect(self.onExportData)
        self.importAct.triggered.connect(self.onImportData)
        self.docDesignerAct.triggered.connect(self.onDocumentDesigner)
        self.docGeneratorAct.triggered.connect(self.onDocumentGenerator)
        self.spatialLayerManager.triggered.connect(self.spatialLayerMangerActivate)

        self.mobile_form_act.triggered.connect(self.mobile_form_generator)
        self.mobile_form_import.triggered.connect(self.mobile_form_importer)

        contentMenu.triggered.connect(self.widgetLoader)
        self.wzdAct.triggered.connect(self.load_config_wizard)
        self.viewSTRAct.triggered.connect(self.onViewSTR)

        # Create content items
        contentAuthCnt = ContentGroup.contentItemFromQAction(self.contentAuthAct)
        contentAuthCnt.code = "E59F7CC1-0D0E-4EA2-9996-89DACBD07A83"

        userRoleMngtCnt = ContentGroup.contentItemFromQAction(self.usersAct)
        userRoleMngtCnt.code = "0CC4FB8F-70BA-4DE8-8599-FD344A564EB5"

        options_cnt = ContentGroup.contentItemFromQAction(self.options_act)
        options_cnt.code = "1520B989-03BA-4B05-BC50-A4C3EC7D79B6"

        profile_db_backup_cnt = ContentGroup.contentItemFromQAction(self.profile_db_backup_act)
        profile_db_backup_cnt.code = "9660f5ab-2ac5-44df-881d-4f2d21ce0632"

        profile_backup_restore_cnt = ContentGroup.contentItemFromQAction(self.profile_backup_restore_act)
        profile_backup_restore_cnt.code = "845699c9-0b3b-9524-ccb7-779efd7a30e8"

        switch_config_cnt = ContentGroup.contentItemFromQAction(self.switch_config_act)
        switch_config_cnt.code = "895bdad0-2dbc-42b6-9d07-9025b32318f6"

        adminUnitsCnt = ContentGroup.contentItemFromQAction(self.manageAdminUnitsAct)
        adminUnitsCnt.code = "770EAC75-2BEC-492E-8703-34674054C246"

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

        strViewCnt = ContentGroup.contentItemFromQAction(self.viewSTRAct)
        strViewCnt.code = "D13B0415-30B4-4497-B471-D98CA98CD841"

        mobileFormgeneratorCnt = ContentGroup.contentItemFromQAction(self.mobile_form_act)
        mobileFormgeneratorCnt.code = "d93981ef-dec4-4597-8495-2941ec2e9a52"

        mobileFormImportCnt = ContentGroup.contentItemFromQAction(self.mobile_form_import)
        mobileFormImportCnt.code = "1394547d-fb6c-4f6e-80d2-53407cf7b7d4"

        username = globals.APP_DBCONN.User.UserName

        if username == 'postgres':
            self.grant_privilege_base_tables(username)

        self.moduleCntGroup = None
        self.moduleContentGroups = []
        self._moduleItems = OrderedDict()
        self._reportModules = OrderedDict()

        for attrs in self.user_entities():
            self._moduleItems[attrs[2]] = attrs[0]

        for k, v in self._moduleItems.items():
            moduleCntGroup = self._create_table_content_group(
                k, username, 'table.png'
            )
            self._reportModules[k] = v
            self.moduleContentGroups.append(moduleCntGroup)

        # create a separator
        tbSeparator = QAction(self.iface.mainWindow())
        tbSeparator.setSeparator(True)
        if self.current_profile is not None:
            if pg_table_exists(self.current_profile.social_tenure.name):
                # add separator to menu
                separator_group = TableContentGroup(username, 'separator', tbSeparator)
                # separator_group.register()
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

        self.profile_db_backup_group = ContentGroup(username)
        self.profile_db_backup_group.addContentItem(profile_db_backup_cnt)
        self.profile_db_backup_group.setContainerItem(self.profile_db_backup_act)
        self.profile_db_backup_group.register()

        self.profile_backup_restore_group = ContentGroup(username)
        self.profile_backup_restore_group.addContentItem(profile_backup_restore_cnt)
        self.profile_backup_restore_group.setContainerItem(self.profile_backup_restore_act)
        self.profile_backup_restore_group.register()

        self.config_separator = ContentGroup(username)
        self.config_separator.addContentItem(self._action_separator())

        self.switch_config_group = ContentGroup(username)
        self.switch_config_group.addContentItem(switch_config_cnt)
        self.switch_config_group.setContainerItem(self.switch_config_act)
        self.switch_config_group.register()

        config_managmt_group = []
        config_managmt_group.append(self.profile_db_backup_group)
        config_managmt_group.append(self.profile_backup_restore_group)
        config_managmt_group.append(self.config_separator)
        config_managmt_group.append(self.switch_config_group)

        # Group admin settings content groups
        adminSettingsCntGroups = []
        #adminSettingsCntGroups.append(self.contentAuthCntGroup)
        #adminSettingsCntGroups.append(self.userRoleCntGroup)
        adminSettingsCntGroups.append(self.options_content_group)

        self.adminUnitsCntGroup = ContentGroup(username)
        self.adminUnitsCntGroup.addContentItem(adminUnitsCnt)
        self.adminUnitsCntGroup.setContainerItem(self.manageAdminUnitsAct)
        self.adminUnitsCntGroup.register()

        self.spatialUnitManagerCntGroup = ContentGroup(username, self.spatialLayerManager)
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

        self.importCntGroup = ContentGroup(username, self.importAct)
        self.importCntGroup.addContentItem(importCnt)
        self.importCntGroup.register()

        self.exportCntGroup = ContentGroup(username, self.exportAct)
        self.exportCntGroup.addContentItem(exportCnt)
        self.exportCntGroup.register()

        # Create mobile content group
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
        for name, path in templates.items():
            doc_temp = DocumentTemplate.build_from_path(name, path)
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
            # template_content = ContentGroup.contentItemFromName(template.name)
            template_content = self._create_table_content_group(
                template.name,
                User.CURRENT_USER.UserName,
                'templates'
            )
            # template_content.code = template_content_group.hash_code(unicode(template.name))
            # template_content_group.addContentItem(template_content)
            # template_content.name = template.name
        # template_content_group.register()

        # Add Design Forms menu and tool bar actions
        self.toolbarLoader.addContent(self.wzdConfigCntGroup)
        self.menubarLoader.addContent(self.wzdConfigCntGroup)

        #self.toolbarLoader.addContent(self.contentAuthCntGroup, [adminMenu, adminBtn])
        #self.toolbarLoader.addContent(self.userRoleCntGroup, [adminMenu, adminBtn])

        self.toolbarLoader.addContent(self.options_content_group, [adminMenu,
                                                                   adminBtn])

        self.toolbarLoader.addContent(self.profile_db_backup_group, [config_managmt_menu,
                                                                      adminBtn])

        self.toolbarLoader.addContent(self.profile_backup_restore_group, [config_managmt_menu,
                                                                    adminBtn])

        self.toolbarLoader.addContent(self.switch_config_group, [config_managmt_menu,
                                                                  adminBtn])

        self.menubarLoader.addContents(adminSettingsCntGroups, [stdmAdminMenu,
                                                                stdmAdminMenu])

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

        self.toolbarLoader.addContent(self.importCntGroup)
        self.menubarLoader.addContent(self.importCntGroup)

        self.toolbarLoader.addContent(self.exportCntGroup)
        self.menubarLoader.addContent(self.exportCntGroup)

        # Add mobile content to tool bar and menu
        self.menubarLoader.addContents(geoodkSettingsCntGroup, [geoodk_mobile_dataMenu, geoodk_mobile_dataMenu])
        self.toolbarLoader.addContents(geoodkSettingsCntGroup, [geoodkMenu, geoodkBtn])

        self.menubarLoader.addContent(self._action_separator())
        self.toolbarLoader.addContent(self._action_separator())

        self.toolbarLoader.addContent(self.docDesignerCntGroup)
        self.menubarLoader.addContent(self.docDesignerCntGroup)

        self.toolbarLoader.addContent(self.docGeneratorCntGroup)
        self.menubarLoader.addContent(self.docGeneratorCntGroup)

        # Load all the content in the container
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

        privilege_provider = SinglePrivilegeProvider('', current_profile())
        for role in roles:
            privilege_provider.grant_privilege_base_table(role)

    def load_profiles_combobox(self):
        """
        Create a combobox and load existing profiles.
        """
        self.profiles_combobox = QComboBox(self.iface.mainWindow())
        if self.current_profile is None:
            return

        profile_names = list(self.stdm_config.profiles.keys())

        self.profiles_combobox.clear()

        self.profiles_combobox.addItems(profile_names)

        GuiUtils.set_combo_current_index_by_text(
            self.profiles_combobox, self.current_profile.name
        )
        self.profiles_combobox.currentIndexChanged[str].connect(
            self.reload_plugin
        )

    def _create_table_content_group(self, k, username, icon):
        content_action = QAction(
            GuiUtils.get_icon(icon),
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
        if self.current_profile is not None:
            config_entities = self.current_profile.entities
            self.geom_entities = [
                ge for ge in config_entities.values()
                if ge.TYPE_INFO == 'ENTITY' and ge.has_geometry_column()
            ]

            self.sp_tables = spatial_tables()
            # Check whether the geometry tables
            # specified in the config exist
            missing_tables = [
                geom_entity.name
                for geom_entity in self.geom_entities
                if geom_entity.name not in self.sp_tables
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

    def onActionAuthorised(self, name):
        """
        This slot is raised when a toolbar action
        is authorised for access by the currently
        logged in user.
        """
        pass

    def manageAccounts(self):
        """
        Slot for showing the user and
        role accounts management window
        """
        frmUserAccounts = manageAccountsDlg(self)
        frmUserAccounts.exec_()

    def contentAuthorization(self):
        """
        Slot for showing the content authorization dialog
        """
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

        #opt_dlg.upgradeButton.clicked.connect(
            #lambda: self.load_configuration_from_file(
                #opt_dlg, True
            #)
        #)

        opt_dlg.exec_()

    def on_profile_db_backup(self):
        """
        Opens a backup dialog.
        """
        db_profile_backup_dlg = DBProfileBackupDialog(self.iface)
        db_profile_backup_dlg.exec_()

    def on_profile_backup_restore(self):
        profile_backup_restore_dlg = ProfileBackupRestoreDialog(self.iface)
        profile_backup_restore_dlg.exec_()

    def on_switch_config(self):
        switch_config_dlg = SwitchConfiguration(self.iface)
        if switch_config_dlg.exec_() == 1:
            self.logoutAct.activate(QAction.Trigger)

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
            self.iface.statusBarIface().addPermanentWidget(
                self.profile_status_label,
                0
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
            if self.profiles_combobox:
                self.profiles_combobox.deleteLater()
                self.profiles_combobox = None

        if self.menubarLoader is not None:
            self.menubarLoader.unloadContent()
            self.stdmMenu.clear()
        if self.entity_browser is not None:
            self.entity_browser.close()

        if self.profile_status_label is not None:
            self.profile_status_label.deleteLater()
            self.profile_status_label = None

        self.logoutCleanUp(True)
        if load_from_stc:
            self.config_serializer.load()
        # Set current profile based on the selected
        # profile in the wizard
        if sel_profile is not None:
            if len(sel_profile) > 1:
                save_current_profile(sel_profile)

        self.current_profile = current_profile()

        if self.current_profile is not None:
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

        except DummyException as ex:
            LOGGER.debug(
                'Error Loading Modules: {}'.format(str(ex))
            )
            self.loadModules()

    def load_config_wizard(self):
        """
        """
        self.wizard = ConfigWizard(
            self.iface.mainWindow()
        )

        # Reload all modules
        self.wizard.wizardFinished.connect(self.reload_plugin)
        try:
            self.wizard.exec_()
        except DummyException as ex:
            QMessageBox.critical(self.iface.mainWindow(),
                                 QApplication.translate(
                                     "STDMPlugin",
                                     "Error Loading the Configuration Wizard"
                                 ),
                                 str(ex)
                                 )

    def changePassword(self):
        """
        Slot for changing password
        """
        # Load change password dialog
        frmPwdDlg = changePwdDlg(self)
        frmPwdDlg.exec_()

    def newSTR(self):
        """
        Slot for showing the wizard for
        defining a new social
        tenure relationship
        """
        try:

            str_editor = STREditor()
            str_editor.open()

        except DummyException as ex:
            QMessageBox.critical(
                self.iface.mainWindow(),
                QApplication.translate(
                    'STDMQGISLoader',
                    'Error Loading the STR Editor'
                ),
                str(ex)
            )

    def onManageAdminUnits(self):
        """
        Slot for showing administrative
        unit selector dialog.
        """

        if self.current_profile is None:
            self.default_profile()
            return
        admin_spatial_unit = [
            e
            for e in
            list(self.current_profile.entities.values())
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

        print('>> current Profile: ', self.current_profile)

        if self.current_profile is None:
            self.default_profile()
            return
        
        print('LEN: ',len(db_user_tables(self.current_profile)))

        if len(db_user_tables(self.current_profile)) < 1:
            self.minimum_table_checker()
            return

        layout = LayoutGuiUtils.create_unique_named_layout()
        layout.initializeDefaults()

        self.iface.openLayoutDesigner(layout)


    def on_designer_opened(self, designer_interface: QgsLayoutDesignerInterface):
        """
        Triggered when a layout designer window is opened
        """
        print('Current Profile: ', current_profile())
        print('APP_DBCONN: ', globals.APP_DBCONN)

        if current_profile() is None or globals.APP_DBCONN is None:
            ComposerWrapper.disable_stdm_items(designer_interface)
            return

        # Embed STDM customizations
        composer_wrapper = ComposerWrapper(
            designer_interface, self.iface
        )

        composer_wrapper.configure()

    def on_designer_closed(self, designer: QgsLayoutDesignerInterface):
        composer_wrapper = ComposerWrapper(designer, self.iface)
        composer_wrapper.close_designer()

    def on_layer_changed(self, layer:QgsMapLayer):
        print('* Layer changed *')

    def onDocumentGenerator(self):
        """
        """
        if self.current_profile is None:
            self.default_profile()
            return

        if len(db_user_tables(self.current_profile)) < 1:
            self.minimum_table_checker()
            return

        access_templates = []
        for pt in self.profile_templates:
            tcg = TableContentGroup(User.CURRENT_USER.UserName, pt.name)
            if tcg.canRead():
                access_templates.append(pt.name)

        doc_gen_wrapper = DocumentGeneratorDialogWrapper(
            self.iface,
            access_templates,
            self.iface.mainWindow(),
            plugin=self
        )

        doc_gen_wrapper.exec_()

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
                    if active_layer is not None:
                        canvas.zoomToFullExtent()
                        extent = active_layer.extent()
                        canvas.setExtent(extent)
        except DummyException as ex:
            LOGGER.debug(str(ex))

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

    def onToggleSpatialUnitManger(self, toggled):
        """
        Slot raised on toggling to activate/deactivate
        editing, and load corresponding
        spatial tools.
        """
        self.spatialLayerManager.setChecked(False)

    def onViewSTR(self):
        """
        Slot for showing widget that enables users to browse
        existing STRs.
        """
        if self.current_profile is None:
            self.default_profile()
            return
        db_status = self.entity_table_checker(
            self.current_profile.social_tenure
        )

        if self.viewSTRWin is not None:
            del self.viewSTRWin
            self.viewSTRWin = None

        self.viewSTRWin = ViewSTRWidget(self)
        self.viewSTRWin.show()


    def isSTDMLayer(self, layer):
        """
        Return whether the layer is an STDM layer.
        """
        if layer.id() in pg_layerNamesIDMapping().reverse:
            return True
        return False

    def widgetLoader(self, QAction):
        # Method to load custom forms
        tbList = list(self._moduleItems.values())

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
                        list(self._reportModules.keys()), dispName
                    )

                    table_content = TableContentGroup(User.CURRENT_USER.UserName, dispName)
                    self.entity_browser = ContentGroupEntityBrowser(
                        sel_entity, table_content, rec_id=0, parent=self.iface.mainWindow(), plugin=self)
                    if sel_entity.has_geometry_column():
                        self.entity_browser.show()
                    else:
                        self.entity_browser.exec_()
                else:
                    return

            except DummyException as ex:
                QMessageBox.critical(
                    self.iface.mainWindow(),
                    QApplication.translate(
                        "STDMPlugin", "Error Loading Entity Browser"
                    ),
                    QApplication.translate(
                        "STDMPlugin",
                        "Unable to load the entity in the browser. "
                        "Check if the entity is configured correctly. "
                        "Error: %s") % str(ex))
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
            self.stdmInitToolbar.removeAction(self.profile_db_backup_act)
            self.stdmInitToolbar.removeAction(self.profile_backup_restore_act)
            self.stdmInitToolbar.removeAction(self.switch_config_act)
            self.stdmInitToolbar.removeAction(self.manageAdminUnitsAct)
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
            LayerUtils.enable_editing_of_stdm_layers(False)

        except DummyException as ex:
            LOGGER.debug(str(ex))

    def removeSTDMLayers(self):
        """
        Remove all STDM layers from the map registry.
        """
        mapLayers = list(QgsProject.instance().mapLayers().values())

        for layer in mapLayers:
            if self.isSTDMLayer(layer):
                QgsProject.instance().removeMapLayer(layer.id())

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

            # Remove STDM layers
            self.removeSTDMLayers()

            # Remove Spatial Unit Manager
            self.remove_spatial_unit_mgr()

            if not reload_plugin:
                if self.profile_status_label is not None:
                    self.profile_status_label.deleteLater()
                    self.profile_status_label = None

                # Clear current profile combobox
                self.profiles_combobox.deleteLater()
                self.profiles_combobox = None

                # Clear singleton ref for SQLAlchemy connections
                if globals.APP_DBCONN is not None:
                    STDMDb.cleanUp()
                    DeclareMapping.cleanUp()
                # Remove database reference
                globals.APP_DBCONN = None
            else:
                if self.profile_status_label:
                    self.profile_status_label.setText('')

            # Reset View STR Window
            if self.viewSTRWin is not None:
                del self.viewSTRWin
                self.viewSTRWin = None

            self.current_profile = None

        except DummyException as ex:
            LOGGER.debug(str(ex))

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
                list(self.current_profile.entities.values())
                if (e.TYPE_INFO == 'ENTITY') and (e.user_editable)
            ]
        return entities

    def help_contents(self):
        """
        Load and open documentation manual
        """
        help_manual = '{0}/stdm.chm'.format(self.plugin_dir)

        try:
            os.startfile(
                help_manual, 'open'
            )
        except FileNotFoundError as ex:
            QMessageBox.critical(
                self.iface.mainWindow(),
                QApplication.translate(
                    "STDMQGISLoader",
                    'Open File Error'
                ), str("Error trying to open help file (stdm.chm), file is missing."))

    def reset_content_modules_id(self, title, message_text):
        return QMessageBox.critical(
            self.iface.mainWindow(), title,
            QApplication.translate(
                "STDMQGISLoader",
                str(message_text)
            )
        )

    def _action_separator(self) ->QAction:
        """
        :return: Toolbar or menu separator
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
