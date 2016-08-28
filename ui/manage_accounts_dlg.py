"""
/***************************************************************************
Name                 : Manage Users Accounts and System Roles Dialog
Description          : Helps to manage user accounts and corresponding roles
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
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from stdm.security.user import User
from stdm.security.membership import Membership
from stdm.security.roleprovider import RoleProvider
from stdm.data.qtmodels import UsersRolesModel
from stdm.utils import *
from stdm.utils.util import getIndex
from ui_user_role_manage import Ui_frmSysManageAccounts
from .new_user_dlg import newUserDlg
from .new_role_dlg import newRoleDlg

class manageAccountsDlg(QDialog, Ui_frmSysManageAccounts):
    '''
    User- and Role-management dialog class
    '''
    def __init__(self,plugin):
        QDialog.__init__(self,plugin.iface.mainWindow())
        self.setupUi(self)  
        
        #Initialize the dialog
        self.initGui()
        
        #Load users
        self.loadUsers()
        
        #Load Roles
        self.loadRoles()
        
        #Load user mappings
        self.loadUserMappings()
        
        #Reference to the currently selected STDM role for which user mappings need to be defined
        self.currentRole = None
        
    def initGui(self):
        '''
        Set control properties
        '''  
        #Set properties for 'Users' button box
        btnUserNew = self.btnManageUsers.button(QDialogButtonBox.Ok)  
        btnUserNew.setText(QApplication.translate("manageAccountsDlg", "New") + "...")
        QObject.connect(btnUserNew, SIGNAL("clicked()"),self.onNewUser)
        
        btnUserEdit = self.btnManageUsers.button(QDialogButtonBox.Save)  
        btnUserEdit.setText(QApplication.translate("manageAccountsDlg", "Edit"))
        QObject.connect(btnUserEdit, SIGNAL("clicked()"),self.onEditUser)
        
        btnUserDelete = self.btnManageUsers.button(QDialogButtonBox.Cancel)  
        btnUserDelete.setText(QApplication.translate("manageAccountsDlg", "Delete"))
        QObject.connect(btnUserDelete, SIGNAL("clicked()"),self.onDeleteUser)
        
        #Set properties for 'Roles' button box
        btnRoleNew = self.btnManageRoles.button(QDialogButtonBox.Ok)  
        btnRoleNew.setText(QApplication.translate("manageAccountsDlg", "New") + "...")
        QObject.connect(btnRoleNew, SIGNAL("clicked()"),self.onNewRole)        
        
        btnRoleDelete = self.btnManageRoles.button(QDialogButtonBox.Cancel)  
        btnRoleDelete.setText(QApplication.translate("manageAccountsDlg", "Delete"))
        QObject.connect(btnRoleDelete, SIGNAL("clicked()"),self.onDeleteRole)     
        
        btnRoleSync = self.btnManageRoles.button(QDialogButtonBox.Apply)  
        btnRoleSync.setText(QApplication.translate("manageAccountsDlg", "Sync"))
        btnRoleSync.setToolTip(QApplication.translate("manageAccountsDlg", "Synchronize STDM roles with database roles"))
        QObject.connect(btnRoleSync, SIGNAL("clicked()"),self.onSyncRoles)
        
        #Data view signals
        QObject.connect(self.lstRoles, SIGNAL("clicked(const QModelIndex&)"),self.onRoleSelected)
        QObject.connect(self.lstRoles, SIGNAL("activated(const QModelIndex&)"),self.onRoleSelected)
        QObject.connect(self.lstMappingRoles, SIGNAL("activated(const QModelIndex&)"),self.onRoleMappingSelected)        
        QObject.connect(self.lstMappingRoles, SIGNAL("clicked(const QModelIndex&)"),self.onRoleMappingSelected)
        QObject.connect(self.lstMappingUsers, SIGNAL("activated(const QModelIndex&)"),self.onUserMappingSelected)        
        QObject.connect(self.lstMappingUsers, SIGNAL("clicked(const QModelIndex&)"),self.onUserMappingSelected)
        
        #Disable any action by the user in the user roles mapping list view
        self.lstMappingUsers.setEnabled(False)
        
    def onNewUser(self):
        '''
        Slot activated when the user requests to create a new user
        '''
        frmNewUser = newUserDlg(self)
        result = frmNewUser.exec_()
        
        #Add new user to dependent models
        if result == QDialog.Accepted:
            user = frmNewUser.user
            
            #Add new user to Users view
            numUsers = self.usersModel.rowCount()
            self.usersModel.insertRows(numUsers, 1)
            index = self.usersModel.index(numUsers)
            self.usersModel.setData(index,user.UserName)
            
            #Add the user to the user mappings list
            userItem = self._createNewUserMapping(user.UserName)
            numUsers = self.UserMappingsModel.rowCount()
            self.UserMappingsModel.setItem(numUsers, userItem)
            
            #Sort users
            self.sortUsers()            
        
    def loadUsers(self):
        '''
        Loads the names of existing users
        '''
        self.membership = Membership()
        users = self.membership.getAllUsers()
        self.usersModel = UsersRolesModel(users)
        self.sortUsers()
        self.lstUsers.setModel(self.usersModel)
        
    def loadRoles(self):
        '''
        Loads the roles of the database cluster
        '''
        self.roleProvider = RoleProvider()
        roles = self.roleProvider.GetAllRoles()
        roleNames = []
        #Remove the postgresql role if it exists
        for role in roles:
            if role.name != 'postgres':
                roleNames.append(role.name)
        self.rolesModel = UsersRolesModel(roleNames)
        self.sortRoles()
        self.lstRoles.setModel(self.rolesModel)
        
        #Load mapping roles view as well
        self.lstMappingRoles.setModel(self.rolesModel)
        
    def onEditUser(self):
        '''
        Slot activated for editing a selected user
        '''
        selItems = self.lstUsers.selectionModel().selectedRows()
        
        if len(selItems) == 0:
            msg = QApplication.translate("manageAccountsDlg", "Please select a user to edit.")
            QMessageBox.warning(self, QApplication.translate("manageAccountsDlg", "Select User"),msg)
            return
        
        #Get user from the first item in the selection
        username = selItems[0].data()
        user = self.membership.getUser(username)
        if user != None:
            frmUserUpdate = newUserDlg(self,user)
            frmUserUpdate.exec_()
            
    def onDeleteUser(self):
        '''
        Slot activated for deleting a selected user
        '''
        selItems = self.lstUsers.selectionModel().selectedRows()
        
        if len(selItems) == 0:
            msg = QApplication.translate("manageAccountsDlg", "Please select a user to delete.")
            QMessageBox.warning(self, QApplication.translate("manageAccountsDlg", "Select User"),msg)
            return
        
        #Get user from the first item in the selection
        userIndex = selItems[0]
        username = userIndex.data()       
        
        msg = QApplication.translate("manageAccountsDlg", 
                                     "Are you sure you want to delete '%s'?\nOnce deleted, this user account cannot be recovered."%(username,))
        result = QMessageBox.warning(self, QApplication.translate("manageAccountsDlg","Delete User"), msg,
                                     QMessageBox.Yes|QMessageBox.No, QMessageBox.No)
        
        if result == QMessageBox.Yes:                        
            #Delete the user
            self.membership.deleteUser(username)
            
            #Remove user from the list
            self.usersModel.removeRows(userIndex.row(), 1)
            
            #Remove corresponding item from the user mapping list view
            self.UserMappingsModel.removeRow(userIndex.row())
            
            #Sort users
            self.sortUsers()
            
    def onSyncRoles(self):
        '''
        Slot for synchronizing STDM roles with database cluster roles.
        This is very important especially on first time login by the superuser/'postgres' account
        '''
        self.roleProvider.syncSTDMRoles()
        
        #Update view
        self.loadRoles()
        
        #Reset role description label
        self.lblRoleDescription.setText("")
        
    def sortUsers(self):
        '''
        Sort users in ascending order
        '''
        self.usersModel.sort(0,Qt.AscendingOrder)
        
    def sortRoles(self):
        '''
        Sorts the roles in ascending order
        '''        
        self.rolesModel.sort(0,Qt.AscendingOrder)
        
    def onNewRole(self):
        '''
        Slot for creating new role
        '''
        frmNewRole = newRoleDlg(self)
        result = frmNewRole.exec_()
        
        if result == QDialog.Accepted:
            role = frmNewRole.role
            
            #Add new role to roles view
            numRoles = self.rolesModel.rowCount()
            self.rolesModel.insertRows(numRoles, 1)
            index = self.rolesModel.index(numRoles)
            self.rolesModel.setData(index,role.name)
            
            #Sort model contents
            self.sortRoles()

    def onRoleSelected(self,index):
        '''
        Slot activated when a role item in the view is selected to load the description text.
        '''
        roleName = index.data()
        role = self.roleProvider.GetRole(roleName)
        if role != None:
            self.lblRoleDescription.setText(role.description)
            
    def onDeleteRole(self):
        '''
        Slot for deleting the selected role
        '''
        selItems = self.lstRoles.selectionModel().selectedRows()
        
        if len(selItems) == 0:
            msg = QApplication.translate("manageAccountsDlg", "Please select a role to delete.")
            QMessageBox.warning(self, QApplication.translate("manageAccountsDlg", "Select Role"),msg)
            return
        
        #Get role from the first item in the selection
        roleIndex = selItems[0]
        rolename = roleIndex.data()       
        
        msg = QApplication.translate("manageAccountsDlg", 
                                     "Are you sure you want to delete '%s'?\nOnce deleted, this role cannot be recovered."%(rolename,))
        result = QMessageBox.warning(self, QApplication.translate("manageAccountsDlg","Delete Role"), msg,
                                     QMessageBox.Yes|QMessageBox.No, QMessageBox.No)
        
        if result == QMessageBox.Yes:                        
            #Delete the role
            self.roleProvider.DeleteSTDMRole(rolename)
            self.roleProvider.DeleteRole(rolename)
            
            #Remove user from the list and role mappings view
            self.rolesModel.removeRows(roleIndex.row(), 1)            
            
            self.lblRoleDescription.setText("")
            
            self.sortRoles()
            
    def loadUserMappings(self,rolename = ""):
        '''
        Loads checked/unchecked users in the user mappings list based on whether they are non/members
        of the specified group.
        If rolename is empty, then just load all users with the check state set to 'Unchecked'
        '''
        roleUsers = []
        if rolename != "":            
            roleUsers = self.roleProvider.GetUsersInRole(rolename)           
            
        sysUsers = self.usersModel._users
        
        #Initialize model
        self.UserMappingsModel = QStandardItemModel(len(sysUsers),1,self)
        
        #Create standard user items (checkable and with an icon) then add them to the list view
        for u in range(len(sysUsers)):
            user = sysUsers[u]
            userItem = self._createNewUserMapping(user)
            
            #If the user is in the given role then set checkstate to 'checked'
            sysIndex = getIndex(roleUsers,user)
            if sysIndex != -1:
                userItem.setCheckState(Qt.Checked)
            
            self.UserMappingsModel.setItem(u, userItem)
            
        self.lstMappingUsers.setModel(self.UserMappingsModel)
        
    def _createNewUserMapping(self,username):
        '''
        Adds a new user to the list of user mappings
        '''
        #Set icon
        icon = QIcon()
        icon.addPixmap(QPixmap(":/plugins/stdm/images/icons/user.png"), QIcon.Normal, QIcon.Off)
        
        userItem = QStandardItem(icon,username)
        userItem.setCheckable(True)
        userItem.setCheckState(Qt.Unchecked)
        
        return userItem
        
    def onRoleMappingSelected(self,index):
        '''
        Slot activated when a role item in the mapping view is selected to load the users
        in the specified role
        '''
        self.lstMappingUsers.setEnabled(True)
        roleName = index.data()
        self.currentRole = roleName
        self.loadUserMappings(roleName)
        
    def onUserMappingSelected(self,index):
        '''
        Slot which is called when a user item in the user mapping list has been clicked or selected to 
        add it to the currently selected role
        '''
        if self.currentRole != None:                        
            
            item = self.UserMappingsModel.itemFromIndex(index)
            username = item.text()
            
            self.blockSignals(True)
            
            #Add user to role if the item is selected  or remove if it was checked
            if item.checkState() == Qt.Checked:                 
                self.roleProvider.AddUsersToRoles([username], [self.currentRole])
            elif item.checkState() == Qt.Unchecked:
                self.roleProvider.RemoveUsersFromRoles([username], [self.currentRole])

            self.blockSignals(False)

























