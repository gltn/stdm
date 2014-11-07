"""
/***************************************************************************
Name                 : Create New User Dialog
Description          : Dialog for entering new user information
Date                 : 18/June/2013 
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
from ui_new_user import Ui_frmNewUser
from stdm.security import User, Membership, SecurityException

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from datetime import date

class newUserDlg(QDialog, Ui_frmNewUser):
    '''
    Create New User Dialog
    '''
    def __init__(self,parent = None,User = None):
        QDialog.__init__(self,parent)
        self.setupUi(self)  
        
        self.user = User
        
        #Initialize the dialog
        self.initGui()
        
    def initGui(self):
        '''
        Set control properties based on the mode
        '''           
        #Set the minimum date to current
        self.dtValidity.setMinimumDate(date.today())
        
        #Set 'Create User' button properties
        btnCreateUser = self.buttonBox.button(QDialogButtonBox.Ok)
        btnCreateUser.setText(QApplication.translate("newUserDlg", "Create User"))
        QObject.connect(btnCreateUser, SIGNAL("clicked()"),self.acceptdlg)
        
        #Set validator for preventing username from having whitespace
        rx = QRegExp("\\S+")
        rxValidator = QRegExpValidator(rx,self)
        self.txtUserName.setValidator(rxValidator)
        
        #Connect signals
        QObject.connect(self.chkValidity, SIGNAL("stateChanged(int)"),self.validityChanged)       
        
        if self.user != None:
            self.txtUserName.setText(self.user.UserName)
            self.txtUserName.setEnabled(False)
            btnCreateUser.setText(QApplication.translate("newUserDlg", "Update User"))
            
            self.setWindowTitle(QApplication.translate("newUserDlg", "Update User Account"))
            
            self.groupBox.setTitle(QApplication.translate("newUserDlg", "User Account Information"))
            
            if self.user.Validity != None:
                if self.user.Validity == 'infinity':
                    self.chkValidity.setCheckState(Qt.Checked)
                else:                    
                    #Try convert the date from string                
                    expDate = QDateTime.fromString(self.user.Validity, "yyyy-MM-dd")
                    self.dtValidity.setDate(expDate.date())
                    self.chkValidity.setCheckState(Qt.Unchecked)
                
            else:                
                self.chkValidity.setCheckState(Qt.Checked)
                    
        self.txtUserName.setFocus()            
        
    def validityChanged(self,state):
        '''
        Slot raised when the user checks/unchecks the 'Infinite Validity Period' checkbox
        '''
        if state == Qt.Checked:
            self.dtValidity.setEnabled(False)
        else:
            self.dtValidity.setEnabled(True)
            
    def validateInput(self):
        '''
        Assert whether required fields have been entered
        '''        
        if str(self.txtUserName.text()) == "":
            QMessageBox.critical(self, QApplication.translate("newUserDlg","Required field"), 
                                 QApplication.translate("LoginDialog","UserName cannot be empty"))
            self.txtUserName.setFocus()
            return False
        
        if str(self.txtPass.text()) == "":
            QMessageBox.critical(self, QApplication.translate("newUserDlg","Required field"), 
                                 QApplication.translate("newUserDlg","Password cannot be empty"))
            self.txtPass.setFocus()
            return False
        
        if str(self.txtConfirmPass.text()) == "":
            QMessageBox.critical(self, QApplication.translate("newUserDlg","Required field"), 
                                 QApplication.translate("newUserDlg","Confirm Password cannot be empty"))
            self.txtConfirmPass.setFocus()
            return False  
        
        if self.txtPass.text() != self.txtConfirmPass.text():
            QMessageBox.critical(self,QApplication.translate("newUserDlg","Password Compare"),
                                 QApplication.translate("newUserDlg","Passwords do not match"))
            self.txtConfirmPass.setFocus()
            return False
        
        else:
            return True 
        
    def _setUser(self):
        '''
        Create/update the user object based on the user input
        '''      
        username = self.txtUserName.text()
        password = self.txtPass.text()
        
        if self.user == None:            
            self.user = User(username,password)                    
            
        else:
            self.user.Password = password
        
        #Set validity if specified
        if self.chkValidity.checkState() == Qt.Unchecked:
            self.user.Validity = self.dtValidity.date().toPyDate()
        else:            
            #Set password to never expire
            self.user.Validity = 'infinity'
            
    def acceptdlg(self):
        '''
        On user clicking the create user button
        '''
        if self.validateInput():           
            
            member = Membership()  
                      
            try:
                #Create new or update user
                if self.user == None:
                    self._setUser()                    
                    member.createUser(self.user)
                    
                else:
                    self._setUser()                   
                    #Update user  
                    member.createUser(self.user,True)                          
                              
                self.accept()
                
            except SecurityException as se:
                QMessageBox.critical(self, 
                                     QApplication.translate("newUserDlg","Create User Error"), str(se)) 
                self.user = None               
            
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
            
        
        
        
        
        
        
        
        
        
        
        
        