"""
/***************************************************************************
Name                 : STDM Database Connection Dialog
Description          : Database connection dialog for only capturing UserName
                        and Port
Date                 : 26/May/2013 
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

from ui_dbconn import Ui_frmDbConn
from stdm.data import DatabaseConnection, DatabaseConfig

class dbconnDlg(QDialog, Ui_frmDbConn):
    '''
    This dialog captures the database connection properties
    '''
    def __init__(self,parent):
        QDialog.__init__(self,parent)
        self.setupUi(self)
        
        #gui initialization
        self.initGui()
        
        #class property
        self.dbconn = None
        
    def initGui(self):
        '''
        Initialize GUI
        '''
        #Change the name of the OK button to Login
        btnSave = self.btnBox.button(QDialogButtonBox.Ok)
        btnSave.setText(QApplication.translate("DbConnectionDialog","Save"))
        
        #Set port integer validator
        intValidator = QIntValidator(1,60000,self)
        self.txtPort.setValidator(intValidator)
        
        #Connect slots
        QObject.connect(self.btnBox, SIGNAL("accepted()"), self.acceptdlg)        
                        
    def validateInput(self):
        '''
        Assert whether required fields have been entered
        '''        
        if self.txtHost.text() == "":
            QMessageBox.critical(self, QApplication.translate("DbConnectionDialog","Required field"), 
                                 QApplication.translate("DbConnectionDialog","Database server name/IP cannot be empty"))
            return False
        if self.txtPort.text() == "":
            QMessageBox.critical(self, QApplication.translate("DbConnectionDialog","Required field"), 
                                 QApplication.translate("DbConnectionDialog","Database port cannot be empty"))
            return False
        if self.txtDatabase.text() == "":
            QMessageBox.critical(self, QApplication.translate("DbConnectionDialog","Required field"), 
                                 QApplication.translate("DbConnectionDialog","Database name cannot be empty"))
            return False  
        else:
            return True       
        
    def acceptdlg(self):
        '''
        On user clicking the login button
        '''
        isValid = self.validateInput()
        if isValid:
            #Capture DB connection properties
            host = self.txtHost.text()
            port = self.txtPort.text()
            database = self.txtDatabase.text()
            dbconfig = DatabaseConfig()            
            self.dbconn = DatabaseConnection(host,port,database)
            #Write DB conn object to the registry
            dbconfig.write(self.dbconn)
            self.accept()
