"""
/***************************************************************************
Name                 : Manage Users Accounts and System Roles Dialog
Description          : Helps to manage user accounts and corresponding roles
Date                 : 18/June/2013 
copyright            : (C) 2014 by UN-Habitat and implementing partners.
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

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ui_user_role_manage import Ui_frmSysManageAccounts
from .new_user_dlg import newUserDlg
from .new_role_dlg import newRoleDlg

from stdm.security import User, Membership, RoleProvider
from stdm.data import UsersRolesModel
from stdm.utils import *

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
        self.load_users()
        
        #Load Roles
        self.load_roles()
        
        #Load user mappings
        self.load_user_mappings()
        
        #Reference to the currently selected STDM role for which user mappings need to be defined
        self.currentRole = None
        
    def initGui(self):
        '''
        Set control properties
        '''  
        #Set properties for 'Users' button box
        btnUserNew = self.btnManageUsers.button(QDialogButtonBox.Ok)  
        btnUserNew.setText(QApplication.translate("manageAccountsDlg", "New") + "...")
        QObject.connect(btnUserNew, SIGNAL("clicked()"),self.on_new_user)
        
        btnUserEdit = self.btnManageUsers.button(QDialogButtonBox.Save)  
        btnUserEdit.setText(QApplication.translate("manageAccountsDlg", "Edit"))
        QObject.connect(btnUserEdit, SIGNAL("clicked()"),self.on_edit_user)
        
        btnUserDelete = self.btnManageUsers.button(QDialogButtonBox.Cancel)  
        btnUserDelete.setText(QApplication.translate("manageAccountsDlg", "Delete"))
        QObject.connect(btnUserDelete, SIGNAL("clicked()"),self.on_delete_user)
        
        #Set properties for 'Roles' button box
        btnRoleNew = self.btnManageRoles.button(QDialogButtonBox.Ok)  
        btnRoleNew.setText(QApplication.translate("manageAccountsDlg", "New") + "...")
        QObject.connect(btnRoleNew, SIGNAL("clicked()"),self.on_new_role)        
        
        btnRoleDelete = self.btnManageRoles.button(QDialogButtonBox.Cancel)  
        btnRoleDelete.setText(QApplication.translate("manageAccountsDlg", "Delete"))
        QObject.connect(btnRoleDelete, SIGNAL("clicked()"),self.on_delete_role)     
        
        btnRoleSync = self.btnManageRoles.button(QDialogButtonBox.Apply)  
        btnRoleSync.setText(QApplication.translate("manageAccountsDlg", "Sync"))
        btnRoleSync.setToolTip(QApplication.translate("manageAccountsDlg", "Synchronize STDM roles with database roles"))
        QObject.connect(btnRoleSync, SIGNAL("clicked()"),self.on_sync_roles)
        
        #Data view signals
        QObject.connect(self.lstRoles, SIGNAL("clicked(const QModelIndex&)"),self.on_role_selected)
        QObject.connect(self.lstRoles, SIGNAL("activated(const QModelIndex&)"),self.on_role_selected)
        QObject.connect(self.lstMappingRoles, SIGNAL("activated(const QModelIndex&)"),self.on_role_mapping_selected)        
        QObject.connect(self.lstMappingRoles, SIGNAL("clicked(const QModelIndex&)"),self.on_role_mapping_selected)
        QObject.connect(self.lstMappingUsers, SIGNAL("activated(const QModelIndex&)"),self.on_user_mapping_selected)        
        QObject.connect(self.lstMappingUsers, SIGNAL("clicked(const QModelIndex&)"),self.on_user_mapping_selected)
        
        #Disable any action by the user in the user roles mapping list view
        self.lstMappingUsers.setEnabled(False)
        
    def on_new_user(self):
        '''
        Slot activated when the user requests to create a new user
        '''
        frm_new_user = newUserDlg(self)
        result = frm_new_user.exec_()
        
        #Add new user to dependent models
        if result == QDialog.Accepted:
            user = frm_new_user.user
            
            #Add new user to Users view
            num_users = self.usersModel.rowCount()
            self.usersModel.insertRows(num_users, 1)
            index = self.usersModel.index(num_users)
            self.usersModel.setData(index, user.UserName)
            
            #Add the user to the user mappings list
            user_item = self._create_new_user_mapping(user.UserName)
            num_users = self.UserMappingsModel.rowCount()
            self.UserMappingsModel.setItem(num_users, user_item)
            
            #Sort users
            self.sort_users()            
        
    def load_users(self):
        '''
        Loads the names of existing users
        '''
        self.membership = Membership()
        users = self.membership.getAllUsers()
        self.usersModel = UsersRolesModel(users)
        self.sort_users()
        self.lstUsers.setModel(self.usersModel)
        
    def load_roles(self):
        '''
        Loads the roles of the database cluster
        '''
        self.roleProvider = RoleProvider()
        roles = self.roleProvider.GetAllRoles()
        role_names = []
        #Remove the postgresql role if it exists
        for role in roles:
            if role.name != 'postgres':
                role_names.append(role.name)
        self.rolesModel = UsersRolesModel(role_names)
        self.sort_roles()
        self.lstRoles.setModel(self.rolesModel)
        
        #Load mapping roles view as well
        self.lstMappingRoles.setModel(self.rolesModel)
        
    def on_edit_user(self):
        '''
        Slot activated for editing a selected user
        '''
        sel_items = self.lstUsers.selectionModel().selectedRows()
        
        if len(sel_items) == 0:
            msg = QApplication.translate("manageAccountsDlg", "Please select a user to edit.")
            QMessageBox.warning(self, QApplication.translate("manageAccountsDlg", "Select User"), msg)
            return
        
        #Get user from the first item in the selection
        username = sel_items[0].data()
        user = self.membership.getUser(username)
        if user != None:
            frm_user_update = newUserDlg(self, user)
            frm_user_update.exec_()
            
    def on_delete_user(self):
        '''
        Slot activated for deleting a selected user
        '''
        sel_items = self.lstUsers.selectionModel().selectedRows()
        
        if len(sel_items) == 0:
            msg = QApplication.translate("manageAccountsDlg", "Please select a user to delete.")
            QMessageBox.warning(self, QApplication.translate("manageAccountsDlg", "Select User"), msg)
            return
        
        #Get user from the first item in the selection
        user_index = sel_items[0]
        username = user_index.data()       
        
        msg = QApplication.translate("manageAccountsDlg", 
                                     "Are you sure you want to delete '%s'?\nOnce deleted, this user account cannot be recovered."%(username,))
        result = QMessageBox.warning(self, QApplication.translate("manageAccountsDlg","Delete User"), msg,
                                     QMessageBox.Yes|QMessageBox.No, QMessageBox.No)
        
        if result == QMessageBox.Yes:                        
            #Delete the user
            self.membership.deleteUser(username)
            
            #Remove user from the list
            self.usersModel.removeRows(user_index.row(), 1)
            
            #Remove corresponding item from the user mapping list view
            self.UserMappingsModel.removeRow(user_index.row())
            
            #Sort users
            self.sort_users()
            
    def on_sync_roles(self):
        '''
        Slot for synchronizing STDM roles with database cluster roles.
        This is very important especially on first time login by the superuser/'postgres' account
        '''
        self.roleProvider.syncSTDMRoles()
        
        #Update view
        self.load_roles()
        
        #Reset role description label
        self.lblRoleDescription.setText("")
        
    def sort_users(self):
        '''
        Sort users in ascending order
        '''
        self.usersModel.sort(0, Qt.AscendingOrder)
        
    def sort_roles(self):
        '''
        Sorts the roles in ascending order
        '''        
        self.rolesModel.sort(0, Qt.AscendingOrder)
        
    def on_new_role(self):
        '''
        Slot for creating new role
        '''
        frm_new_role = newRoleDlg(self)
        result = frm_new_role.exec_()
        
        if result == QDialog.Accepted:
            role = frm_new_role.role

            #Add new role to roles view
            num_roles = self.rolesModel.rowCount()
            self.rolesModel.insertRows(num_roles, 1)
            index = self.rolesModel.index(num_roles)
            self.rolesModel.setData(index, role.name)
            
            #Sort model contents
            self.sort_roles()

    def on_role_selected(self, index):
        '''
        Slot activated when a role item in the view is selected to load the description text.
        '''
        role_name = index.data()
        role = self.roleProvider.GetRole(role_name)
        if role != None:
            self.lblRoleDescription.setText(role.description)
            
    def on_delete_role(self):
        '''
        Slot for deleting the selected role
        '''
        sel_items = self.lstRoles.selectionModel().selectedRows()
        
        if len(sel_items) == 0:
            msg = QApplication.translate("manageAccountsDlg", "Please select a role to delete.")
            QMessageBox.warning(self, QApplication.translate("manageAccountsDlg", "Select Role"), msg)
            return
        
        #Get role from the first item in the selection
        role_index = sel_items[0]
        rolename = role_index.data()       
        
        msg = QApplication.translate("manageAccountsDlg", 
                                     "Are you sure you want to delete '%s'?\nOnce deleted, this role cannot be recovered."%(rolename,))
        result = QMessageBox.warning(self, QApplication.translate("manageAccountsDlg","Delete Role"), msg,
                                     QMessageBox.Yes|QMessageBox.No, QMessageBox.No)
        
        if result == QMessageBox.Yes:                        
            #Delete the role
            self.roleProvider.DeleteSTDMRole(rolename)
            self.roleProvider.DeleteRole(rolename)
            
            #Remove user from the list and role mappings view
            self.rolesModel.removeRows(role_index.row(), 1)            
            
            self.lblRoleDescription.setText("")
            
            self.sort_roles()
            
    def load_user_mappings(self, rolename=""):
        '''
        Loads checked/unchecked users in the user mappings list based on whether they are non/members
        of the specified group.
        If rolename is empty, then just load all users with the check state set to 'Unchecked'
        '''
        role_users = []
        if rolename != "":            
            role_users = self.roleProvider.GetUsersInRole(rolename)           
            
        sys_users = self.usersModel._users
        
        #Initialize model
        self.UserMappingsModel = QStandardItemModel(len(sys_users), 1, self)
        
        #Create standard user items (checkable and with an icon) then add them to the list view
        for u in range(len(sys_users)):
            user = sys_users[u]
            user_item = self._create_new_user_mapping(user)
            
            #If the user is in the given role then set checkstate to 'checked'
            sys_index = getIndex(role_users, user)
            if sys_index != -1:
                user_item.setCheckState(Qt.Checked)
            
            self.UserMappingsModel.setItem(u, user_item)
            
        self.lstMappingUsers.setModel(self.UserMappingsModel)
        
    def _create_new_user_mapping(self, username):
        '''
        Adds a new user to the list of user mappings
        '''
        #Set icon
        icon = QIcon()
        icon.addPixmap(QPixmap(":/plugins/stdm/images/icons/user.png"), QIcon.Normal, QIcon.Off)
        
        user_item = QStandardItem(icon, username)
        user_item.setCheckable(True)
        user_item.setCheckState(Qt.Unchecked)
        
        return user_item
        
    def on_role_mapping_selected(self, index):
        '''
        Slot activated when a role item in the mapping view is selected to load the users
        in the specified role
        '''
        self.lstMappingUsers.setEnabled(True)
        role_name = index.data()
        self.currentRole = role_name
        self.load_user_mappings(role_name)
        
    def on_user_mapping_selected(self, index):
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
