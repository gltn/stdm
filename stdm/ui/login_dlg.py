"""
/***************************************************************************
Name                 : STDM Login Dialog
Description          : Display the dialog window for users to login in order
                        to access STDM tools and modules
Date                 : 24/May/2013
copyright            : (C) 2013 by John Gitau
email                : gkahiu@gmail.com
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
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QDialog,
    QApplication,
    QDialogButtonBox,
    QMessageBox
)
from qgis.PyQt.QtCore import QDir

from qgis.gui import QgsGui

from stdm.data.config import DatabaseConfig
from stdm.data.connection import DatabaseConnection
from stdm.security.user import User
from stdm.settings.registryconfig import RegistryConfig
from stdm.ui.db_conn_dlg import dbconnDlg
from stdm.ui.gui_utils import GuiUtils
from stdm.ui.notification import NotificationBar

SUPERUSER = 'postgres'

WIDGET, BASE = uic.loadUiType(
    GuiUtils.get_ui_file_path('ui_login.ui'))


class loginDlg(WIDGET, BASE):
    '''
    This class handles user authentication for accessing STDM resources
    '''

    def __init__(self, parent=None, test_connect_mode=False):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        QgsGui.enableAutoGeometryRestore(self)

        self.btn_db_settings.setIcon(GuiUtils.get_icon('db_server_settings.png'))

        # If dialog is used in the context of testing database connections
        self._test_connect_mode = test_connect_mode

        # gui initialization
        self.initGui()

        # class properties
        self.user = None
        self.dbConn = None
        self.found_db_settings = True

        self.setting_data = self.reg_setting()

    def initGui(self):
        '''
        Initialize GUI
        '''
        # Change the name of the OK button to Login
        btnLogin = self.btnBox.button(QDialogButtonBox.Ok)

        if self._test_connect_mode:
            btnLogin.setText(QApplication.translate("LoginDialog", "Test"))
            self.setWindowTitle(QApplication.translate("LoginDialog",
                                                       "STDM Database "
                                                       "Connection"))
            self.btn_db_settings.setVisible(False)

        else:
            btnLogin.setText(QApplication.translate("LoginDialog", "Login"))
            self.btn_db_settings.setVisible(True)

        # Connect slots
        self.btn_db_settings.clicked.connect(self.settingsDialog)
        self.btnBox.accepted.connect(self.acceptdlg)

        # Configure notification bar
        self.notifBar = NotificationBar(self.vlNotification)


        if self._test_connect_mode:
            self.txtUserName.setFocus()

        else:
            self.txtUserName.setText('postgres')
            self.txtPassword.setFocus()

    def test_connect_mode(self):
        return self._test_connect_mode

    def set_database_connection(self, db_connection):
        """
        Set database connection object. User object will be overwritten
        as it will be derived from the username and password controls.
        :param db_connection: Database connection object
        :type db_connection: DatabaseConnection
        """
        self.dbConn = db_connection

    def validateInput(self):
        '''
        Assert whether required fields have been entered
        '''
        self.notifBar.clear()

        if self.txtUserName.text() == "":
            self.notifBar.insertErrorNotification(
                QApplication.translate("loginDlg", "UserName field cannot be empty"))
            self.txtUserName.setFocus()

            return False

        if self.txtPassword.text() == "":
            self.notifBar.insertErrorNotification(
                QApplication.translate("loginDlg", "Password field cannot be empty"))
            self.txtPassword.setFocus()

            return False

        else:
            return True

    def test_mode(self) ->int:
        self.txtUserName.setText('postgres')
        self.txtPassword.setText('abc123')
        self.acceptdlg()
        return 1

    def _set_user(self):
        '''
        Create the user object based on the user input
        '''
        username = self.txtUserName.text()
        password = self.txtPassword.text()
        self.user = User(username, password)

    def settingsDialog(self):
        '''
        In case the user clicks reset button to change the settings
        '''
        #setting_data = self.reg_setting()

        dbDlg = dbconnDlg(self, self.setting_data)

        if 'Database' in self.setting_data.keys():
            dbDlg.txtDatabase.setText(str(self.setting_data['Database']))
        if 'Host' in self.setting_data.keys():
            dbDlg.txtHost.setText(str(self.setting_data['Host']))
        if 'Port' in self.setting_data.keys():
            dbDlg.txtPort.setText(str(self.setting_data['Port']))

        if dbDlg.exec_() == QDialog.Accepted:
            self.setting_data['Host'] = dbDlg.txtHost.text()
            self.setting_data['Port'] = dbDlg.txtPort.text()
            self.setting_data['Database'] = dbDlg.txtDatabase.text()

    def reg_setting(self) ->dict:
        connSettings = ['Host', 'Database', 'Port']
        set_conn = RegistryConfig()
        settings = set_conn.read(connSettings)

        if len(settings) == 0:
            self.found_db_settings = False
            settings = self.read_local_cache()

        return settings

    def read_local_cache(self) -> dict:
        db_cache_file = QDir.home().path() + '/.stdm/db_settings.ini'

        settings = {}
        key=0
        value=1

        try:
            with open(db_cache_file) as f:
                for line in f:
                    data = line.split('=')
                    settings[data[key]] = data[value].replace('\n','')
        except:
            return {}
        return settings

    def acceptdlg(self):
        '''
        On user clicking the login button
        '''
        isValid = self.validateInput()

        if isValid:
            # Set user object
            self._set_user()

            # Get mode and corresponding database connection object
            if not self._test_connect_mode:
                # Get DB connection
                dbconfig = DatabaseConfig(self.setting_data)
                dbconn = dbconfig.read()
                if dbconn is None:
                    msg = QApplication.translate("loginDlg", "The STDM database "
                                                             "connection has not "
                                                             "been configured in "
                                                             "your system.\nWould "
                                                             "you like to configure "
                                                             "it now?")
                    response = QMessageBox.warning(self,
                                                   QApplication.translate(
                                                       "LoginDialog",
                                                       "Database Connection"),
                                                   msg,
                                                   QMessageBox.Yes | QMessageBox.No,
                                                   QMessageBox.Yes)
                    if response == QMessageBox.Yes:
                        dbDlg = dbconnDlg(self, self.setting_data)
                        if dbDlg.exec_() == QDialog.Accepted:
                            # set the partial database connection properties
                            dbconn = dbDlg.dbconn

            else:
                dbconn = self.dbConn

            # Whatever the outcome of the database settings definition process
            if dbconn is None:
                return

            dbconn.User = self.user

            # Test connection
            success, msg = dbconn.validateConnection()

            if success:
                self.dbConn = dbconn
                if not self.found_db_settings:
                    db_config = DatabaseConfig(self.setting_data)
                    db_conn = DatabaseConnection(self.setting_data['Host'],
                                                 self.setting_data['Port'],
                                                 self.setting_data['Database'])
                    db_config.write(db_conn)
                
                self.accept()

            else:
                QMessageBox.critical(self, QApplication.translate(
                    "LoginDialog", "Authentication Failed"), msg)
                self.txtPassword.setFocus()
                self.txtPassword.selectAll()
