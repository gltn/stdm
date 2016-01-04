"""
/***************************************************************************
Name                 : Change Password Dialog
Description          : Dialog that enables the current logged in user to
                        change the password
Date                 : 31/May/2013 
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
from ui_changepwd import Ui_frmChangePwd

#from stdm.security import User, Membership, SecurityException
#import stdm.data

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class changePwdDlg(QDialog, Ui_frmChangePwd):
    
    def __init__(self,plugin):
        QDialog.__init__(self,plugin.iface.mainWindow())
        self.setupUi(self)
                
        #gui initialization
        self.initGui()            
        
    def initGui(self):
        '''
        Initialize GUI
        '''
        #Change the name of the OK button to Login
        btnLogin=self.btnBox.button(QDialogButtonBox.Ok)
        btnLogin.setText(QApplication.translate("ChangePasswordDialog","Save"))
        #Connect slots
        QObject.connect(self.btnBox, SIGNAL("accepted()"), self.acceptdlg)
                        
    def validateInput(self):
        '''
        Assert whether required fields have been entered
        '''        
        if self.txtNewPass.text() == "":
            QMessageBox.critical(self, QApplication.translate("ChangePasswordDialog","Required field"), 
                                 QApplication.translate("ChangePasswordDialog","New Password cannot be empty"))
            return False
        if self.txtConfirmPass.text() == "":
            QMessageBox.critical(self, QApplication.translate("ChangePasswordDialog","Required field"), 
                                 QApplication.translate("ChangePasswordDialog","Confirm Password field cannot be empty"))
            return False 
        if self.txtNewPass.text() != self.txtConfirmPass.text():
            QMessageBox.critical(self,QApplication.translate("ChangePasswordDialog","Password Compare"),
                                 QApplication.translate("ChangePasswordDialog","Passwords do not match"))
            return False
        else:
            return True 
    
    
        
    def acceptdlg(self):
        '''
        On user clicking the login button
        '''
        if self.validateInput():
            member = Membership()
            newPwd = self.txtConfirmPass.text()
            try:
                #Set new password
                member.setPassword(stdm.data.app_dbconn.User.UserName,newPwd)
                QMessageBox.information(self, QApplication.translate("ChangePasswordDialog","Change Password"), 
                                        QApplication.translate("ChangePasswordDialog","Your password has successfully been changed"))
                self.accept()
            except SecurityException as se:
                QMessageBox.critical(self, 
                                     QApplication.translate("ChangePasswordDialog","Password Error"), str(se))
                self.txtNewPass.selectAll()
                
        
            
        
        
        
        
        
        
        
        
        
        
        
        