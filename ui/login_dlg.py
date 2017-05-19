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
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from .ui_login import Ui_frmLogin
from .db_conn_dlg import dbconnDlg
from .notification import NotificationBar,ERROR

from stdm.data.config import DatabaseConfig
from stdm.data.connection import DatabaseConnection
from stdm.settings.registryconfig import RegistryConfig
from stdm.security.user import User

SUPERUSER = 'postgres'

class loginDlg(QDialog, Ui_frmLogin):
    '''
    This class handles user authentication for accessing STDM resources
    '''
    def __init__(self, parent=None, test_connect_mode=False):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        #If dialog is used in the context of testing database connections
        self._test_connect_mode = test_connect_mode
        
        #gui initialization
        self.initGui()
        
        #class properties
        self.User = None
        self.dbConn = None
        
    def initGui(self):
        '''
        Initialize GUI
        '''
        #Change the name of the OK button to Login
        btnLogin = self.btnBox.button(QDialogButtonBox.Ok)

        if self._test_connect_mode:
            btnLogin.setText(QApplication.translate("LoginDialog", "Test"))
            self.setWindowTitle(QApplication.translate("LoginDialog",
                                                       "STDM Database "
                                                       "Connection"))
            self.btn_db_settings.setVisible(False)

        else:
            btnLogin.setText(QApplication.translate("LoginDialog","Login"))
            self.btn_db_settings.setVisible(True)

        #Connect slots
        self.btn_db_settings.clicked.connect(self.settingsDialog)
        self.btnBox.accepted.connect(self.acceptdlg)
        
        #Configure notification bar
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
                QApplication.translate("loginDlg","UserName field cannot be empty"))
            self.txtUserName.setFocus()

            return False
        
        if self.txtPassword.text() == "":
            self.notifBar.insertErrorNotification(
                QApplication.translate("loginDlg","Password field cannot be empty"))
            self.txtPassword.setFocus()

            return False 
        
        else:
            return True 
        
    def _set_user(self):
        '''
        Create the user object based on the user input
        '''      
        username = self.txtUserName.text()
        password = self.txtPassword.text()
        self.User = User(username, password)

    def settingsDialog(self):
        '''
        In case the user clicks reset button to change the settings
        '''
        setting_data = self.reg_setting()
        dbDlg = dbconnDlg(self)

        if 'Database' in setting_data.keys():
            dbDlg.txtDatabase.setText(unicode(setting_data['Database']))
        if 'Host' in setting_data.keys():
            dbDlg.txtHost.setText(unicode(setting_data['Host']))
        if 'Port' in setting_data.keys():
            dbDlg.txtPort.setText(unicode(setting_data['Port']))
        dbDlg.exec_()

    def reg_setting(self):
        connSettings = ['Host', 'Database', 'Port']
        set_conn = RegistryConfig()
        settings = set_conn.read(connSettings)

        return settings

    def acceptdlg(self):
        '''
        On user clicking the login button
        '''
        isValid = self.validateInput()

        if isValid:
            #Set user object
            self._set_user()

            #Get mode and corresponding database connection object
            if not self._test_connect_mode:
                #Get DB connection
                dbconfig = DatabaseConfig()
                dbconn = dbconfig.read()
                if  dbconn is None:
                    msg = QApplication.translate("loginDlg","The STDM database "
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
                                                   QMessageBox.Yes|QMessageBox.No,
                                                   QMessageBox.Yes)
                    if response == QMessageBox.Yes:
                        dbDlg = dbconnDlg(self)
                        if dbDlg.exec_() == QDialog.Accepted:
                            #set the partial database connection properties
                            dbconn = dbDlg.dbconn

            else:
                dbconn = self.dbConn

            #Whatever the outcome of the database settings definition process
            if dbconn is None:
                return

            dbconn.User = self.User

            #Test connection
            success, msg = dbconn.validateConnection()

            if success:
                self.dbConn = dbconn
                self.accept()

            else:
                QMessageBox.critical(self, QApplication.translate(
                    "LoginDialog", "Authentication Failed"), msg)
                self.txtPassword.setFocus()
                self.txtPassword.selectAll()

