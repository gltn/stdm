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
import logging
import os.path
import platform
from collections import OrderedDict

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *
import qgis.utils
from sqlalchemy.exc import SQLAlchemyError
from stdm.settings.config_serializer import ConfigurationFileSerializer
from stdm.settings import current_profile, save_current_profile

from stdm.data.configuration.exception import ConfigurationException
from stdm.data.configuration.stdm_configuration import StdmConfiguration
from stdm.settings.config_file_updater import ConfigurationFileUpdater
from stdm.data.configuration.config_updater import ConfigurationSchemaUpdater

from stdm.ui.change_pwd_dlg import changePwdDlg
from stdm.ui.doc_generator_dlg import (
    DocumentGeneratorDialogWrapper,
    EntityConfig
)
from stdm.ui.login_dlg import loginDlg
from stdm.ui.manage_accounts_dlg import manageAccountsDlg
from stdm.ui.content_auth_dlg import contentAuthDlg
from stdm.ui.options_base import OptionsDialog
from stdm.ui.new_str_wiz import newSTRWiz
from stdm.ui.view_str import ViewSTRWidget
from stdm.ui.admin_unit_selector import AdminUnitSelector
from stdm.ui.entity_browser import (
    EntityBrowserWithEditor
)
from stdm.ui.about import AboutSTDMDialog
from stdm.ui.stdmdialog import DeclareMapping

from stdm.ui.wizard.wizard import ConfigWizard

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
    spatial_tables
)
from stdm.settings.registryconfig import (
    RegistryConfig,
    WIZARD_RUN,
    CONFIG_UPDATED
)
from stdm.ui.license_agreement import LicenseAgreement
from navigation import (
    STDMAction,
    QtContainerLoader,
    ContentGroup,
    TableContentGroup
)
from mapping import (
    StdmMapToolCreateFeature
)

from stdm.settings.template_updater import TemplateFileUpdater

from stdm.utils.util import (
    getIndex,
    db_user_tables,
    format_name
)
from mapping.utils import pg_layerNamesIDMapping

from composer import ComposerWrapper
from stdm.ui.progress_dialog import STDMProgressDialog

LOGGER = logging.getLogger('stdm')


class STDMQGISLoader(object):

    viewSTRWin = None
    STR_DISPLAY = QApplication.translate(
        'STDMQGISLoader',
        'New Social Tenure Relationship'
    )

    def __init__(self, iface):
        self.iface = iface

        # Initialize loader
        self.toolbarLoader = None
        self.menubarLoader = None

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


        self.spatialLayerMangerDockWidget = None

        self._user_logged_in = False
        self.current_profile = None
        # Profile status label showing the current profile
        self.profile_status_label = None
        LOGGER.debug('STDM plugin has been initialized.')

        # Load configuration file
        self.config_path = QDesktopServices.storageLocation(
            QDesktopServices.HomeLocation) \
                      + '/.stdm/configuration.stc'
        self.config_serializer = ConfigurationFileSerializer(self.config_path)
        self.configuration_file_updater = ConfigurationFileUpdater(self.iface)

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
        self.logoutAct.setShortcut(QKeySequence(Qt.Key_Delete))

        self.changePasswordAct = STDMAction(QIcon(":/plugins/stdm/images/icons/change_password.png"), \
        QApplication.translate("ChangePasswordToolbarAction","Change Password"), self.iface.mainWindow(),
        "8C425E0E-3761-43F5-B0B2-FB8A9C3C8E4B")
        self.helpAct = STDMAction(QIcon(":/plugins/stdm/images/icons/help-content.png"), \
        QApplication.translate("ConfigTableReader","Help Contents"), self.iface.mainWindow(),
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
        #add actions to the menu bar
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

            #Initialize the whole STDM database
            try:
                db = STDMDb.instance()

            except NoPostGISError:
                err_msg = QApplication.translate(
                    "STDM",
                    "STDM cannot be loaded because the system has "
                    "detected that the PostGIS extension is missing "
                    "in '{0}' database.\nCheck that PostGIS has been "
                    "installed and that the extension has been enabled "
                    "in the STDM database. Please contact the system "
                    "administrator for more information."
                                        .format(frmLogin.dbConn.Database))
                QMessageBox.critical(self.iface.mainWindow(),
                    QApplication.translate("STDM","Spatial Extension Error"),
                    err_msg)

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
                #Set current profile
                self.current_profile = current_profile()

                self.loadModules()
                self.default_profile()
                self.run_wizard()
                self._user_logged_in = True

            except Exception as pe:
                title = QApplication.translate(
                    "STDMQGISLoader",
                    "Error Loading Modules"
                )
                self.reset_content_modules_id(
                    title,
                    pe
                )

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
        :type entity: Class
        :return: True if there is no missing table and false
        if there is a missing table.
        :rtype: Boolean
        """
        title = QApplication.translate(
            "STDMQGISLoader",
            'Database Table Error'
        )
        if None in [self.current_profile.social_tenure.party,
                    self.current_profile.social_tenure.spatial_unit]:
            return
        # Check for social tenure entity
        if entity == self.current_profile.social_tenure:
            str_table_status = [
                (
                    str(entity.party.short_name),
                    pg_table_exists(entity.party.name)
                ),
                (
                    str(entity.spatial_unit.short_name),
                    pg_table_exists(entity.spatial_unit.name)
                ),
                (
                    str(entity.short_name),
                    pg_table_exists(entity.name)
                )
            ]
            str_table_status = dict(str_table_status)
            missing_tables = [
                 key
                 for key, value in str_table_status.iteritems()
                 if not value
            ]
            if len(missing_tables) > 0:
                missing_tables = str(missing_tables).strip("[]")
                missing_tables = missing_tables.replace("'", "")

                message = QApplication.translate(
                    "STDMQGISLoader",
                    'The system has detected that '
                    'database table(s) required in \n'
                    'in the Social Tenure Relationship '
                    'is/are missing.\n'
                    'Missing table(s) - {}\n'
                    'Do you want to re-run the '
                    'Configuration Wizard now?'.
                    format(missing_tables)
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
            else: # If no table is missing, return True
                return True
        # Check for other entities
        else:
            if not pg_table_exists(entity.name):
                message = QApplication.translate(
                    "STDMQGISLoader",
                    'The system has detected that '
                    'a required database table - \n'
                    '{} is missing. \n'
                    'Do you want to re-run the '
                    'Configuration Wizard now?'.format(
                        entity.short_name
                    )
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

    def run_wizard(self):
        """
        Checks if the configuration wizard was run before.
        :return:
        :rtype:
        """
        reg_config = RegistryConfig()
        wizard_key = reg_config.read(
            [WIZARD_RUN]
        )
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
            stdm_config = StdmConfiguration.instance()
            profiles = stdm_config.profiles

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
                else:
                    return

    def load_configuration_to_serializer(self):
        try:
            self.config_serializer.load()
            return True
        except IOError as io_err:
            QMessageBox.critical(self.iface.mainWindow(),
                    QApplication.translate('STDM', 'Load Configuration Error'),
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


    def load_configuration_from_file(self, parent, manual=False):
        """
        Load configuration object from the file.
        :return: True if the file was successfully
        loaded. Otherwise, False.
        :rtype: bool
        """
        progress = STDMProgressDialog(parent)
        progress.overall_progress(
            'Upgrading STDM Configuration...',
        )

        home = QDesktopServices.storageLocation(
            QDesktopServices.HomeLocation
        )

        config_path = '{}/.stdm/configuration.stc'.format(home)

        if manual:
            parent.upgradeButton.setEnabled(False)
            upgrade_status = self.configuration_file_updater.load(
                self.plugin_dir, progress, True
            )

        else:
            upgrade_status = self.configuration_file_updater.load(
                self.plugin_dir, progress
            )

        if upgrade_status:
            # Append configuration_upgraded.stc profiles

            if os.path.isfile(config_path):
                progress.progress_message(
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
                        self.plugin_dir, profile_details, progress
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
                    parent.upgradeButton.setEnabled(True)
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
                    'Successfully upgraded to STDM 1.2 configuration!'
                )
                return True

        else:
            if manual:
                parent.upgradeButton.setEnabled(False)
                parent.manage_upgrade()
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

        self.manageAdminUnitsAct = QAction(
            QIcon(":/plugins/stdm/images/icons/manage_admin_units.png"),
            QApplication.translate(
                "ManageAdminUnitsToolbarAction",
                "Manage Administrative Units"
            ),
            self.iface.mainWindow()
        )

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

        self.viewSTRAct = QAction(QIcon(":/plugins/stdm/images/icons/view_str.png"), \
        QApplication.translate("ViewSTRToolbarAction","View Social Tenure Relationship"),
        self.iface.mainWindow())

        self.wzdAct = QAction(QIcon(":/plugins/stdm/images/icons/table_designer.png"),\
                    QApplication.translate("ConfigWizard","Configuration Wizard"), self.iface.mainWindow())
        self.wzdAct.setShortcut(Qt.Key_F7)
        self.ModuleAct = QAction(QIcon(":/plugins/stdm/images/icons/table_designer.png"),\
                    QApplication.translate("WorkspaceConfig","Entities"), self.iface.mainWindow())


        #Connect the slots for the actions above
        self.contentAuthAct.triggered.connect(self.contentAuthorization)
        self.usersAct.triggered.connect(self.manageAccounts)
        self.options_act.triggered.connect(self.on_sys_options)
        self.manageAdminUnitsAct.triggered.connect(self.onManageAdminUnits)
        self.exportAct.triggered.connect(self.onExportData)
        self.importAct.triggered.connect(self.onImportData)
        self.docDesignerAct.triggered.connect(self.onDocumentDesigner)
        self.docGeneratorAct.triggered.connect(self.onDocumentGenerator)
        self.spatialLayerManager.triggered.connect(self.spatialLayerMangerActivate)
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

        wzdConfigCnt = ContentGroup.contentItemFromQAction(self.wzdAct)
        wzdConfigCnt.code = "F16CA4AC-3E8C-49C8-BD3C-96111EA74206"

        strViewCnt=ContentGroup.contentItemFromQAction(self.viewSTRAct)
        strViewCnt.code="D13B0415-30B4-4497-B471-D98CA98CD841"

        username = data.app_dbconn.User.UserName

        self.moduleCntGroup = None
        self.moduleContentGroups = []
        self._moduleItems = OrderedDict()
        self._reportModules = OrderedDict()

        # add the tables to the stdm toolbar
        # Format the table names to friendly format before adding them

        if self.user_entities() is not None:
            user_entities = dict(self.user_entities())
            for i, (name, short_name) in enumerate(user_entities.iteritems()):
                display_name = QApplication.translate(
                    "Entities",
                    unicode(short_name).replace("_", " ").title()
                )
                self._moduleItems[display_name] = name

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
                separator_group.register()
                self.moduleContentGroups.append(separator_group)

                moduleCntGroup = self._create_table_content_group(
                    self.STR_DISPLAY, username, 'new_str.png'
                )
                self.moduleContentGroups.append(moduleCntGroup)

        #Create content groups and add items
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

        #Group admin settings content groups
        adminSettingsCntGroups = []
        adminSettingsCntGroups.append(self.contentAuthCntGroup)
        adminSettingsCntGroups.append(self.userRoleCntGroup)
        adminSettingsCntGroups.append(self.options_content_group)

        self.adminUnitsCntGroup = ContentGroup(username)
        self.adminUnitsCntGroup.addContentItem(adminUnitsCnt)
        self.adminUnitsCntGroup.setContainerItem(self.manageAdminUnitsAct)
        self.adminUnitsCntGroup.register()

        self.spatialUnitManagerCntGroup = ContentGroup(username,self.spatialLayerManager)
        self.spatialUnitManagerCntGroup.addContentItem(spatialLayerManagerCnt)
        self.spatialUnitManagerCntGroup.register()

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

        #Add Design Forms menu and tool bar actions
        self.toolbarLoader.addContent(self.wzdConfigCntGroup)
        self.menubarLoader.addContent(self.wzdConfigCntGroup)

        self.toolbarLoader.addContent(self.contentAuthCntGroup, [adminMenu, adminBtn])
        self.toolbarLoader.addContent(self.userRoleCntGroup, [adminMenu, adminBtn])
        self.toolbarLoader.addContent(self.options_content_group, [adminMenu,
                                                                   adminBtn])

        self.menubarLoader.addContents(adminSettingsCntGroups, [stdmAdminMenu, stdmAdminMenu])

        self.menubarLoader.addContent(self._action_separator())
        self.toolbarLoader.addContent(self._action_separator())

        self.menubarLoader.addContents(self.moduleContentGroups, [stdmEntityMenu, stdmEntityMenu])
        self.toolbarLoader.addContents(self.moduleContentGroups, [contentMenu, contentBtn])

        self.menubarLoader.addContent(self.spatialUnitManagerCntGroup)
        self.toolbarLoader.addContent(self.spatialUnitManagerCntGroup)

        self.toolbarLoader.addContent(self.STRCntGroup)
        self.menubarLoader.addContent(self.STRCntGroup)

        self.toolbarLoader.addContent(self.adminUnitsCntGroup)
        self.menubarLoader.addContent(self.adminUnitsCntGroup)

        self.toolbarLoader.addContent(self.importCntGroup)
        self.menubarLoader.addContent(self.importCntGroup)

        self.toolbarLoader.addContent(self.exportCntGroup)
        self.menubarLoader.addContent(self.exportCntGroup)

        self.menubarLoader.addContent(self._action_separator())
        self.toolbarLoader.addContent(self._action_separator())

        self.toolbarLoader.addContent(self.docDesignerCntGroup)
        self.menubarLoader.addContent(self.docDesignerCntGroup)

        self.toolbarLoader.addContent(self.docGeneratorCntGroup)
        self.menubarLoader.addContent(self.docGeneratorCntGroup)

        #Load all the content in the container
        self.toolbarLoader.loadContent()
        self.menubarLoader.loadContent()

        self.create_spatial_unit_manager()

        self.profile_status_message()

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

        opt_dlg.upgradeButton.clicked.connect(
            lambda :self.load_configuration_from_file(
                opt_dlg, True
            )
        )

        opt_dlg.exec_()


    def profile_status_message(self):
        """
        Shows the name of the loaded profile in QGIS
        status bar.
        :return: None
        :rtype: NoneType
        """
        if self.current_profile is None:
            return
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


    def reload_plugin(self, sel_profile):
        """
        Reloads stdm plugin without logging out.
        This is to allow modules capture changes
        made by the Configuration Wizard and Options.
        :param sel_profile: the selected profile name
        on the configuration wizard.
        :type: string
        :return: None
        :rtype: NoneType
        """
        if self.toolbarLoader is not None:
            self.toolbarLoader.unloadContent()
        if self.menubarLoader is not None:
            self.menubarLoader.unloadContent()
            self.stdmMenu.clear()
        self.logoutCleanUp(True)

        # Set current profile based on the selected
        # profile in the wizard
        if sel_profile is not None:
            if len(sel_profile) > 1:
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
        self.wizard.wizardFinished.connect(
            self.reload_plugin
        )
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
            frmNewSTR = newSTRWiz(self)
            frmNewSTR.exec_()
        except Exception as ex:
            QMessageBox.critical(
                self.iface.mainWindow(),
                QApplication.translate(
                    "STDMPlugin",
                    "Error Loading New STR Wizard"
                ),
                unicode(ex.message)
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
        doc_gen_wrapper = DocumentGeneratorDialogWrapper(
            self.iface,
            self.iface.mainWindow()
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
                    self.refresh_layers()
        except Exception as ex:
            LOGGER.debug(unicode(ex))

    def refresh_layers(self):
        """
        Refresh all database layers.
        :return: None
        :rtype: NoneType
        """
        layers = qgis.utils.iface.legendInterface().layers()
        for layer in layers:
            layer.dataProvider().forceReload()
            layer.triggerRepaint()
        if not qgis.utils.iface.activeLayer() is None:
            canvas = qgis.utils.iface.mapCanvas()
            canvas.setExtent(
                qgis.utils.iface.activeLayer().extent()
            )
            qgis.utils.iface.mapCanvas().refresh()

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

        dispName=QAction.text()

        if dispName == self.STR_DISPLAY:

            if self.current_profile is None:
                self.default_profile()
                return

            database_status = self.entity_table_checker(
                self.current_profile.social_tenure
            )
            if database_status:
                self.newSTR()


        else:
            table_name = self._moduleItems.get(dispName)
            if self.current_profile is None:
                self.default_profile()
                return
            sel_entity = self.current_profile.entity_by_name(
                table_name
            )
            database_status = self.entity_table_checker(
                sel_entity
            )

            try:
                if table_name in tbList and database_status:
                    cnt_idx = getIndex(
                        self._reportModules.keys(), dispName
                    )
                    et_browser = EntityBrowserWithEditor(
                        sel_entity,
                        self.iface.mainWindow()
                    )
                    et_browser.exec_()

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
            self.stdmInitToolbar.removeAction(self.spatialLayerManager)
            self.stdmInitToolbar.removeAction(self.contentAuthAct)
            self.stdmInitToolbar.removeAction(self.usersAct)
            self.stdmInitToolbar.removeAction(self.options_act)
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

    def logoutCleanUp(self, reload=False):
        '''
        Clear database connection references and content items
        '''
        try:
            if not self._user_logged_in:
                return

            #Remove STDM layers
            self.removeSTDMLayers()
            # Remove Spatial Unit Manager
            self.remove_spatial_unit_mgr()
            # Clear current profile status text

            if reload == False:
                self.profile_status_label.deleteLater()
                self.profile_status_label = None
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
        if self.current_profile is not None:
            return [
                (e.name, e.short_name)
                for e in
                self.current_profile.entities.values()
                if (e.TYPE_INFO == 'ENTITY')
            ]

    def help_contents(self):
        """
        Load and open documentation manual
        """
        help_manual = self.plugin_dir+'/%s'%"stdm.chm"
        os.startfile(
            help_manual,'open'
        )

    def reset_content_modules_id(self, title, message_text):
        return QMessageBox.critical(
            self.iface.mainWindow(),
            QApplication.translate(
                "STDMQGISLoader",
                title
            ),
            unicode(message_text)
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
                err_msg =QApplication.translate("STDMQGISLoader",
                                                     "STDM has detected that "
                                                     "the version of config "
                                                     "installed is old and "
                                                     "outdated. Delete "
                                                     "existing configuration "
                                                     "folder or xml file and "
                                                     "restart QGIS.")
                raise ConfigVersionException(err_msg)
