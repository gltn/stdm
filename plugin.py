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

from stdm.settings.config_serializer import ConfigurationFileSerializer
from stdm.settings import current_profile

from stdm.data.configuration.exception import ConfigurationException
from stdm.data.configuration.stdm_configuration import StdmConfiguration

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
    EntityBrowser,
    STDMEntityBrowser
)
from stdm.ui.about import AboutSTDMDialog
from stdm.ui.stdmdialog import DeclareMapping

from stdm.ui.workspace_config import WorkspaceLoader
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

from navigation import (
    STDMAction,
    QtContainerLoader,
    ContentGroup,
    TableContentGroup
)
from mapping import (
    StdmMapToolCreateFeature
)

from stdm.utils.util import (
    getIndex,
    profile_user_tables
)
from mapping.utils import pg_layerNamesIDMapping

from composer import ComposerWrapper

LOGGER = logging.getLogger('stdm')

class STDMQGISLoader(object):

    viewSTRWin = None

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
            self.plugin_dir = string.replace(self.plugin_dir, "\\", "/")
            localePath = self.plugin_dir + "/i18n/stdm_%s.qm" % (locale,)
        if QFileInfo(localePath).exists():
            self.translator = QTranslator()
            self.translator.load(localePath)
            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Initialize the property management window
        self.propManageWindow = None

        # STDM Tables
        self.stdmTables = []
        self.spatialLayerMangerDockWidget = None

        self._user_logged_in = False
        self.current_profile = None

        LOGGER.debug('STDM plugin has been initialized.')

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
        myQrcPath = ":/plugins/stdm/" + theName;
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
        #Remove the STDM toolbar
        del self.stdmInitToolbar

        #Remove connection info
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
            config_load_status = self.load_configuration_from_file()

            #Exit if the load failed
            if not config_load_status:
                return

            try:
                #Set current profile
                self.current_profile = current_profile()
                self.loadModules()
                self._user_logged_in = True

                self.default_profile()

            except Exception as pe:
                title = QApplication.translate(
                    "STDMQGISLoader",
                    "Error reading profile settings"
                )
                self.reset_content_modules_id(
                    title,
                    pe.message
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
        title = QApplication.translate(
            "STDMQGISLoader",
            'Database Table Error'
        )
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
                    'The system has detected that database table(s) required in \n'
                    'in the Social Tenure Relationship is/are missing.\n'
                    'Missing table(s) - '+missing_tables+'\n'+
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
                else:
                    return False
            else:
                return True
        else:
            if not pg_table_exists(entity.name):
                message = QApplication.translate(
                    "STDMQGISLoader",
                    'The system has detected that a required database table - \n'
                    +entity.short_name+ ' is missing. \n'+
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
                else:
                    return False
            else:
                return True


    def default_profile(self):
        """
        Checks if the current profile exists and if it doesn't,
        asks the user to run Configuration Wizard.
        Returns: None
        """
        if self.current_profile is None:
            title = QApplication.translate(
                "STDMQGISLoader",
                'Default Profile Error'
            )
            message = QApplication.translate(
                "STDMQGISLoader",
                'The system has detected that there '
                'is no default profile. \n'
                'Do you want to run the '
                'Configuration Wizard now?'
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

    def load_configuration_from_file(self):
        """
        Load configuration object from the file.
        :return: True if the file was successfully
        loaded. Otherwise, False.
        :rtype: bool
        """
        config_path = QDesktopServices.storageLocation(
            QDesktopServices.HomeLocation) +\
                      '/.stdm/configuration.stc'
        config_serializer = ConfigurationFileSerializer(
            config_path
        )

        try:
            config_serializer.load()

        except IOError as io_err:
            QMessageBox.critical(self.iface.mainWindow(),
                QApplication.translate(
                    'STDM', 'Load Configuration Error'
                ),
                unicode(io_err)
            )

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

        return True

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

        #Separator definition
        tbSeparator = QAction(self.iface.mainWindow())
        tbSeparator.setSeparator(True)

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
                           QApplication.translate("OptionsToolbarAction", "Options..."),
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

        self.surveyAct = QAction(QIcon(":/plugins/stdm/images/icons/survey.png"), \
        QApplication.translate("NewSurveyToolbarAction","Survey"), self.iface.mainWindow())

        self.farmerAct = QAction(QIcon(":/plugins/stdm/images/icons/farmer.png"), \
        QApplication.translate("NewFarmerToolbarAction","Content"), self.iface.mainWindow())

        self.docDesignerAct = QAction(QIcon(":/plugins/stdm/images/icons/cert_designer.png"), \
        QApplication.translate("DocumentDesignerAction","Document Designer"), self.iface.mainWindow())

        self.docGeneratorAct = QAction(QIcon(":/plugins/stdm/images/icons/generate_document.png"), \
        QApplication.translate("DocumentGeneratorAction","Document Generator"), self.iface.mainWindow())

        #Activate spatial unit management tools
        self.spatialEditorAct = QAction(QIcon(":/plugins/stdm/images/icons/edit24.png"), \
        QApplication.translate("SpatialEditorAction","Toggle Spatial Unit Editing"), self.iface.mainWindow())
        self.spatialEditorAct.setCheckable(True)

        #Spatial Layer Manager
        self.spatialLayerManager = QAction(QIcon(":/plugins/stdm/images/icons/spatial_unit_manager.png"), \
        QApplication.translate("SpatialEditorAction","Spatial Unit Manager"), self.iface.mainWindow())
        self.spatialLayerManager.setCheckable(True)
        self.spatialLayerManager.setChecked(True)

        self.createFeatureAct = QAction(QIcon(":/plugins/stdm/images/icons/create_feature.png"), \
        QApplication.translate("CreateFeatureAction","Create Spatial Unit"), self.iface.mainWindow())
        self.createFeatureAct.setCheckable(True)
        self.createFeatureAct.setVisible(False)

        #SaveEdits action; will not be registered since it is associated with the
        self.saveEditsAct = QAction(QIcon(":/plugins/stdm/images/icons/save_tb.png"), \
        QApplication.translate("CreateFeatureAction","Save Edits"), self.iface.mainWindow())

        self.newSTRAct = QAction(QIcon(":/plugins/stdm/images/icons/new_str.png"), \
        QApplication.translate("NewSTRToolbarAction","New Social Tenure Relationship"), self.iface.mainWindow())

        self.viewSTRAct = QAction(QIcon(":/plugins/stdm/images/icons/view_str.png"), \
        QApplication.translate("ViewSTRToolbarAction","View Social Tenure Relationship"),
        self.iface.mainWindow())

        self.wzdAct = QAction(QIcon(":/plugins/stdm/images/icons/table_designer.png"),\
                    QApplication.translate("WorkspaceConfig","Design Forms"), self.iface.mainWindow())
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
        self.surveyAct.triggered.connect(self.onManageSurvey)
        self.docDesignerAct.triggered.connect(self.onDocumentDesigner)
        self.docGeneratorAct.triggered.connect(self.onDocumentGenerator)
        self.spatialEditorAct.triggered.connect(self.onToggleSpatialEditing)
        self.spatialLayerManager.triggered.connect(self.spatialLayerMangerActivate)
        self.saveEditsAct.triggered.connect(self.onSaveEdits)
        self.createFeatureAct.triggered.connect(self.onCreateFeature)
        contentMenu.triggered.connect(self.widgetLoader)

        self.wzdAct.triggered.connect(self.load_config_wizard)

        self.newSTRAct.triggered.connect(self.newSTR)
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

        surveyCnt = ContentGroup.contentItemFromQAction(self.surveyAct)
        surveyCnt.code = "5620049B-983A-4F85-B0D6-9D83925CC45E"

        farmerCnt = ContentGroup.contentItemFromQAction(self.farmerAct)
        farmerCnt.code = "99EA7671-85CF-40D6-B417-A3CC49D5A594"

        documentDesignerCnt = ContentGroup.contentItemFromQAction(self.docDesignerAct)
        documentDesignerCnt.code = "C4826C19-2AE3-486E-9FF0-32C00A0A517F"

        documentGeneratorCnt = ContentGroup.contentItemFromQAction(self.docGeneratorAct)
        documentGeneratorCnt.code = "4C0C7EF2-5914-4FDE-96CB-089D44EDDA5A"

        spatialEditingCnt = ContentGroup.contentItemFromQAction(self.spatialEditorAct)
        spatialEditingCnt.code = "4E945EE7-D6F9-4E1C-A4AA-0C7F1BC67224"

        spatialLayerManagerCnt = ContentGroup.contentItemFromQAction(self.spatialLayerManager)
        spatialLayerManagerCnt.code = "4E945EE7-D6F9-4E1C-X4AA-0C7F1BC67224"

        createFeatureCnt = ContentGroup.contentItemFromQAction(self.createFeatureAct)
        createFeatureCnt.code = "71CFDB15-EDB5-410D-82EA-0E982971BC51"

        wzdConfigCnt = ContentGroup.contentItemFromQAction(self.wzdAct)
        wzdConfigCnt.code = "F16CA4AC-3E8C-49C8-BD3C-96111EA74206"

        strViewCnt=ContentGroup.contentItemFromQAction(self.viewSTRAct)
        strViewCnt.code="D13B0415-30B4-4497-B471-D98CA98CD841"

        username = data.app_dbconn.User.UserName
        self.moduleCntGroup = None
        self.moduleContentGroups = []
        self._moduleItems = OrderedDict()
        self._reportModules = OrderedDict()

        #    map the user tables to sqlalchemy model object

        # add the tables to the stdm toolbar
        # Format the table names to freiendly format before adding them

        if self.user_entities() is not None:
            user_entities = dict(self.user_entities())
            for name, short_name in user_entities.iteritems():
                display_name = QT_TRANSLATE_NOOP("Entities",
                                    unicode(short_name).replace("_", " ").title())
                self._moduleItems[display_name] = name

        for k, v in self._moduleItems.iteritems():

            content_action = QAction(QIcon(":/plugins/stdm/images/icons/table.png"),
                                    k, self.iface.mainWindow())

            # capabilities = contentGroup(self._moduleItems[k])
            #
            # if capabilities:
            moduleCntGroup = TableContentGroup(username, k, content_action)
                # moduleCntGroup.createContentItem().code = capabilities[0]
                # moduleCntGroup.readContentItem().code = capabilities[1]
                # moduleCntGroup.updateContentItem().code = capabilities[2]
                # moduleCntGroup.deleteContentItem().code = capabilities[3]
            moduleCntGroup.register()
            self._reportModules[k] = self._moduleItems.get(k)
            self.moduleContentGroups.append(moduleCntGroup)
            # Add core modules to the report configuration

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

        self.spatialEditingCntGroup = ContentGroup(username, self.spatialEditorAct)
        self.spatialEditingCntGroup.addContentItem(spatialEditingCnt)
        self.spatialEditingCntGroup.register()

        self.spatialUnitManagerCntGroup = ContentGroup(username,self.spatialLayerManager)
        self.spatialUnitManagerCntGroup.addContentItem(spatialLayerManagerCnt)
        self.spatialUnitManagerCntGroup.register()

        self.createFeatureCntGroup = ContentGroup(username,self.createFeatureAct)
        self.createFeatureCntGroup.addContentItem(createFeatureCnt)
        self.createFeatureCntGroup.register()

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

        self.surveyCntGroup = TableContentGroup(username,
                                                self.surveyAct.text(),
                                                self.surveyAct)
        self.surveyCntGroup.createContentItem().code = "A7783C39-1A5B-4F79-81C2-639C2EA3E8A3"
        self.surveyCntGroup.readContentItem().code = "CADFC838-DA3C-44C5-A6A8-3B2FC4CA8464"
        self.surveyCntGroup.updateContentItem().code = "B42AC2C5-7CF5-48E6-A37F-EAE818FBC9BC"
        self.surveyCntGroup.deleteContentItem().code = "C916ACF3-30E6-45C3-B8E1-22E56D0AFB3E"
        self.surveyCntGroup.register()

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

        #Group spatial editing tools together
        self.spatialEditingGroup = QActionGroup(self.iface.mainWindow())
        self.spatialEditingGroup.addAction(self.createFeatureAct)

        self.configureMapTools()

        #Load all the content in the container
        self.toolbarLoader.loadContent()
        self.menubarLoader.loadContent()

        self.create_spatial_unit_manager()

    def create_spatial_unit_manager(self):
        self.spatialLayerMangerDockWidget = SpatialUnitManagerDockWidget(self.iface)
        self.spatialLayerMangerDockWidget.setWindowTitle(
            QApplication.translate("STDMQGISLoader", 'Spatial Unit Manager'))
        self.iface.addDockWidget(Qt.LeftDockWidgetArea,
                                 self.spatialLayerMangerDockWidget)
        self.spatialLayerMangerDockWidget.show()

    def configureMapTools(self):
        '''
        Configure properties of STDM map tools.
        '''
        self.mapToolCreateFeature = StdmMapToolCreateFeature(self.iface)
        self.mapToolCreateFeature.setAction(self.createFeatureAct)

    def onActionAuthorised(self,name):
        '''
        This slot is raised when a toolbar action is authorised for access by the currently
        logged in user.
        '''
        pass

    def onContentAdded(self,stdmAction):
        '''
        Slot raised when an STDMAction has been added to its corresponding container.
        '''
        if stdmAction.Name == self.createFeatureAct.Name:
            #Insert SaveEdits action
            self.stdmInitToolbar.insertAction(
                self.createFeatureAct,
                self.saveEditsAct
            )

    def onFinishedLoadingContent(self):
        '''
        This slot is raised once the module
        loader has finished loading content items.
        '''
        if self.propManageWindow != None:
            self.iface.addDockWidget(
                Qt.RightDockWidgetArea,
                self.propManageWindow
            )

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
        opt_dlg.exec_()

    def workspaceLoader(self):
        '''
        Slot for customizing user forms
        '''
        self.wkspDlg = WorkspaceLoader(
            self.iface.mainWindow()
        )
        self.wkspDlg.exec_()

    def load_config_wizard(self):
        '''
        '''
        self.wizard = ConfigWizard(
            self.iface.mainWindow()
        )
        status = self.wizard.exec_()

        #Reload profile upon successfully
        # running the config wizard
        if status == QDialog.Accepted:
            self.reload_profile()

    def reload_profile(self):
        """
        Reload the current profile.
        """
        #Reload the spatial unit manager
        if not self.spatialLayerMangerDockWidget is None:
            self.spatialLayerMangerDockWidget.reload()

    def changePassword(self):
        '''
        Slot for changing password
        '''
        #Load change password dialog
        frmPwdDlg = changePwdDlg(self)
        frmPwdDlg.exec_()

    def onShowHidePropertyWindow(self,visible):
        '''
        Slot raised when the user checks or unchecks the action for
        showing/hiding the property manager window
        '''
        if visible:
            self.propMngtAct.setChecked(True)
        else:
            self.propMngtAct.setChecked(False)

    def newSTR(self):
        '''
        Slot for showing the wizard for defining a new social
        tenure relationship
        '''
        try:
            frmNewSTR = newSTRWiz(self)
            frmNewSTR.exec_()
        except Exception as ex:
            QMessageBox.critical(self.iface.mainWindow(),
                QApplication.translate(
                    "STDMPlugin",
                    "Loading dialog..."),
                str(ex.message)
            )

    def onManageAdminUnits(self):
        '''
        Slot for showing administrative unit selector dialog.
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

    def onManageSurvey(self):
        '''
        Slot raised to show form for entering new survey.
        '''
        surveyBrowser = SurveyEntityBrowser(
            self.surveyCntGroup,
            self.iface.mainWindow()
        )
        surveyBrowser.exec_()

    def onDocumentDesigner(self):
        """
        Slot raised to show new print
        composer with additional tools for designing
        map-based documents.
        """
        if self.current_profile is None:
            self.default_profile()
            return
        if len(profile_user_tables(self.current_profile)) < 1:
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
        if len(profile_user_tables(self.current_profile)) < 1:
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
        if len(profile_user_tables(self.current_profile)) < 1:
            self.minimum_table_checker()
            return
        importData = ImportData(self.iface.mainWindow())
        importData.exec_()

    def onExportData(self):
        """
        Show export data dialog.
        """
        if self.current_profile is None:
            self.default_profile()
            return
        if len(profile_user_tables(self.current_profile)) < 1:
            self.minimum_table_checker()
            return
        exportData = ExportData(self.iface.mainWindow())
        exportData.exec_()

    def onSaveEdits(self):
        '''
        Slot raised to save changes to STDM layers.
        '''
        currLayer = self.iface.activeLayer()

        if currLayer == None:
            return

        if not isinstance(currLayer, QgsVectorLayer):
            return

        #Assert if layer is from the SDTM database
        if not self.isSTDMLayer(currLayer):
            return

        if not currLayer.commitChanges():
            self.iface.messageBar().clearWidgets()
            self.iface.messageBar().pushMessage(
                QApplication.translate(
                    "STDMPlugin", "Save STDM Layer"),
                QApplication.translate(
                    "STDMPlugin",
                    "Could not commit changes to {0} layer." .format(
                        currLayer.name()
                    )
                ),
                level=QgsMessageBar.CRITICAL)

        currLayer.startEditing()
        currLayer.triggerRepaint()

    def onToggleSpatialEditing(self,toggled):
        '''
        Slot raised on toggling to activate/deactivate
        editing, and load corresponding
        spatial tools.
        '''
        currLayer = self.iface.activeLayer()

        if currLayer != None:
            self.toggleEditing(currLayer)

        else:
            self.spatialEditorAct.setChecked(False)

        if not toggled:
            self.createFeatureAct.setChecked(False)
            self.createFeatureAct.setVisible(False)

    def onToggleSpatialUnitManger(self,toggled):
        '''
        Slot raised on toggling to activate/deactivate
        editing, and load corresponding
        spatial tools.
        '''
        currLayer = self.iface.activeLayer()

        if currLayer != None:
            self.spatialUnitMangerToggleEditing(currLayer)

        else:
            self.spatialLayerManager.setChecked(False)

        if not toggled:
            self.createFeatureAct.setChecked(False)
            self.createFeatureAct.setVisible(False)

    def toggleEditing(self,layer):
        '''
        Actual implementation which validates and
        creates/ends edit sessions.
        '''
        if not isinstance(layer,QgsVectorLayer):
            return False

        teResult = True

        #Assert if layer is from the SDTM database
        if not self.isSTDMLayer(layer):
            self.spatialLayerManager.setChecked(False)
            self.iface.messageBar().clearWidgets()
            self.iface.messageBar().pushMessage(
                QApplication.translate(
                    "STDMPlugin",
                    "Non-SDTM Layer"
                ),
                QApplication.translate(
                    "STDMPlugin",
                    "Selected layer is not from"
                    " the STDM database."),
                level=QgsMessageBar.CRITICAL
            )
            return False

        if not layer.isEditable() and not layer.isReadOnly():
            if not (layer.dataProvider().capabilities() &
                        QgsVectorDataProvider.EditingCapabilities):
                self.spatialLayerManager.setChecked(False)
                self.spatialLayerManager.setEnabled(False)
                self.iface.messageBar().pushMessage(
                    QApplication.translate(
                        "STDMPlugin",
                        "Start Editing Failed"
                    ),
                    QApplication.translate(
                        "STDMPlugin",
                        "Provider cannot be opened for editing"
                    ),
                    level=QgsMessageBar.CRITICAL
                )

                return False

            #Enable/show spatial editing tools
            self.createFeatureAct.setVisible(True)

            layer.startEditing()

        elif layer.isModified():
            saveResult = QMessageBox.information(
                self.iface.mainWindow(),
                QApplication.translate(
                    "STDMPlugin",
                    "Stop Editing"
                ),
                QApplication.translate(
                    "STDMPlugin",
                    "Do you want to save "
                    "changes to {0} layer?" .format(
                        layer.name())
                ),
                QMessageBox.Save|QMessageBox.Discard|QMessageBox.Cancel
            )

            if saveResult == QMessageBox.Cancel:
                teResult = False

            elif saveResult == QMessageBox.Save:
                QApplication.setOverrideCursor(Qt.WaitCursor)

                if not layer.commitChanges():
                    teResult = False

                layer.triggerRepaint()

                QApplication.restoreOverrideCursor()

            else:
                QApplication.setOverrideCursor(Qt.WaitCursor)

                self.iface.mapCanvas().freeze(True)

                if not layer.rollBack():
                    self.iface.messageBar().pushMessage(
                        QApplication.translate(
                            "STDMPlugin", "Error"
                        ),
                        QApplication.translate(
                            "STDMPlugin",
                            "Problems during rollback"
                        ),
                        level = QgsMessageBar.CRITICAL
                    )
                    teResult = False

                self.iface.mapCanvas().freeze(False)

                layer.triggerRepaint()

                QApplication.restoreOverrideCursor()

        #Layer has not been modified
        else:
            self.iface.mapCanvas().freeze(True)
            layer.rollBack()
            self.iface.mapCanvas().freeze(False)
            teResult = True
            layer.triggerRepaint()

        return teResult

    def spatialUnitMangerToggleEditing(self,layer):
        '''
        Actual implementation which validates
        and creates/ends edit sessions.
        '''
        if not isinstance(layer,QgsVectorLayer):
            return False

        teResult = True

        #Assert if layer is from the SDTM database
        if not self.isSTDMLayer(layer):
            self.postGISLayerEditor.setChecked(False)
            self.iface.messageBar().clearWidgets()
            self.iface.messageBar().pushMessage(
                QApplication.translate(
                    "STDMPlugin","Non-SDTM Layer"
                ),
                QApplication.translate(
                    "STDMPlugin",
                    "Selected layer is not from "
                    "the STDM database."
                ),
                level=QgsMessageBar.CRITICAL
            )

            return False

        if not layer.isEditable() and not layer.isReadOnly():
            if not (layer.dataProvider().capabilities() &
                        QgsVectorDataProvider.EditingCapabilities):
                self.postGISLayerEditor.setChecked(False)
                self.postGISLayerEditor.setEnabled(False)
                self.iface.messageBar().pushMessage(
                    QApplication.translate(
                        "STDMPlugin","Start Editing Failed"),
                    QApplication.translate(
                        "STDMPlugin",
                        "Provider cannot be opened for editing"),
                    level=QgsMessageBar.CRITICAL
                )

                return False

            #Enable/show spatial editing tools
            self.createFeatureAct.setVisible(True)

            layer.startEditing()

        elif layer.isModified():
            saveResult = QMessageBox.information(
                self.iface.mainWindow(),
                QApplication.translate("STDMPlugin","Stop Editing"),
                QApplication.translate(
                    "STDMPlugin",
                    "Do you want to save changes to {0} layer?")
                ).format(
                layer.name(),
                    QMessageBox.Save|QMessageBox.Discard|QMessageBox.Cancel
                )

            if saveResult == QMessageBox.Cancel:
                teResult = False

            elif saveResult == QMessageBox.Save:
                QApplication.setOverrideCursor(Qt.WaitCursor)

                if not layer.commitChanges():
                    teResult = False

                layer.triggerRepaint()

                QApplication.restoreOverrideCursor()

            else:
                QApplication.setOverrideCursor(Qt.WaitCursor)

                self.iface.mapCanvas().freeze(True)

                if not layer.rollBack():
                    self.iface.messageBar().pushMessage(
                        QApplication.translate(
                            "STDMPlugin","Error"
                        ),
                        QApplication.translate(
                            "STDMPlugin",
                            "Problems during rollback"
                        ),
                        level=QgsMessageBar.CRITICAL
                    )
                    teResult = False

                self.iface.mapCanvas().freeze(False)

                layer.triggerRepaint()

                QApplication.restoreOverrideCursor()

        #Layer has not been modified
        else:
            self.iface.mapCanvas().freeze(True)
            layer.rollBack()
            self.iface.mapCanvas().freeze(False)
            teResult = True
            layer.triggerRepaint()

        return teResult

    def onCreateFeature(self):
        '''
        Slot raised to activate the digitization
        process of creating a new feature.
        '''
        self.iface.mapCanvas().setMapTool(
            self.mapToolCreateFeature
        )

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

    def widgetLoader(self,QAction):
        #Method to load custom forms
        tbList = self._moduleItems.values()

        dispName=QAction.text()

        if dispName == 'Social Tenure Relationship':
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
            sel_entity = self.current_profile.entity_by_name(table_name)
            database_status = self.entity_table_checker(sel_entity)

            try:
                if table_name in tbList and database_status:
                    cnt_idx = getIndex(
                        self._reportModules.keys(), dispName
                    )
                    main = STDMEntityBrowser(
                        self.moduleContentGroups[cnt_idx],
                        table_name,
                        self.iface.mainWindow()
                    )
                    main.exec_()

                else:
                    return

            except Exception as ex:
                QMessageBox.critical(
                    self.iface.mainWindow(),
                    QApplication.translate(
                        "STDMPlugin","Loading dialog..."
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
        abtDlg = AboutSTDMDialog(self.iface.mainWindow())
        abtDlg.exec_()

    def logout(self):
        """
        Logout the user and remove default user buttons when logged in
        """
        try:
            self.stdmInitToolbar.removeAction(self.logoutAct)
            self.stdmInitToolbar.removeAction(self.changePasswordAct)
            self.loginAct.setEnabled(True)
            self.stdmInitToolbar.removeAction(self.wzdAct)
            self.stdmInitToolbar.removeAction(self.spatialLayerManager)
            # self.spatialLayerMangerActivate()
            self.logoutCleanUp()
            self.initMenuItems()
        except:
            pass

    def removeSTDMLayers(self):
        """
        Remove all STDM layers from the map registry.
        """
        mapLayers = QgsMapLayerRegistry.instance().mapLayers().values()

        for layer in mapLayers:
            if self.isSTDMLayer(layer):
                QgsMapLayerRegistry.instance().removeMapLayer(layer.id())

        self.stdmTables = []

    def logoutCleanUp(self):
        '''
        Clear database connection references and content items
        '''
        try:
            if not self._user_logged_in:
                return

            #Remove STDM layers
            self.removeSTDMLayers()

            #Clear singleton ref for SQLALchemy connections
            if not data.app_dbconn is None:
                #clear_mappers()
                STDMDb.cleanUp()
                DeclareMapping.cleanUp()

            #Remove database reference
            data.app_dbconn = None

            if not self.toolbarLoader is None:
                self.toolbarLoader.unloadContent()
            if not self.menubarLoader is None:
                self.menubarLoader.unloadContent()
                self.stdmMenu.clear()
            #Reset property management window
            if not self.propManageWindow is None:
                self.iface.removeDockWidget(
                    self.propManageWindow
                )
                del self.propManageWindow
                self.propManageWindow = None

            #Reset View STR Window
            if not self.viewSTRWin is None:
                del self.viewSTRWin
                self.viewSTRWin = None

            #Remove Spatial Unit Manager
            if self.spatialLayerMangerDockWidget:
                self.spatialLayerMangerDockWidget.close()

            self.spatialLayerMangerDockWidget = None
            self.current_profile = None
        except:
            pass

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
                if (e.TYPE_INFO == 'ENTITY' or
                    e.TYPE_INFO == 'SOCIAL_TENURE') and
                not e.has_geometry_column()
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
            message_text
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
        if self.spatialLayerMangerDockWidget.isVisible():
            self.spatialLayerMangerDockWidget.hide()
        else:
            self.spatialLayerMangerDockWidget.show()
