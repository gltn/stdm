"""
/***************************************************************************
Name                 : Authorize Content Dialog
Description          : Provides an interface for authorizing STDM content
                       by granting/revoking permissions based on db cluster
                       roles.
Date                 : 1/July/2013 
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

from sqlalchemy.orm import clear_mappers
from sqlalchemy import Table

from stdm import resources_rc

from stdm.security.roleprovider import RoleProvider
from stdm.data.database import (
    Content,
    Role,
    STDMDb,
    Base
)
from stdm.data.qtmodels import UsersRolesModel
from stdm.utils import *
from stdm.utils.util import getIndex
from ui_content_auth import Ui_frmContentAuth

from stdm.settings import current_profile

class contentAuthDlg(QDialog, Ui_frmContentAuth):
    '''
    Content authorization dialog
    '''
    def __init__(self,plugin):
        QDialog.__init__(self,plugin.iface.mainWindow())
        self.setupUi(self)  
        
        #Initialize the dialog
        self.initGui()
        
        #Load users
        self.loadContent()
        
        #Load Roles
        self.loadRoles()            
        
        #Reference to the currently selected STDM content item
        self.currentContent = None
        
    def initGui(self):
        '''
        Initialize GUI properties
        '''
        #Disable any action by the user in the roles view
        self.lstRoles.setEnabled(False)  
        
        #Connect signals
        QObject.connect(self.lstContent, SIGNAL("activated(const QModelIndex&)"),self.onContentClicked)      
        QObject.connect(self.lstContent, SIGNAL("clicked(const QModelIndex&)"),self.onContentClicked)
        QObject.connect(self.lstRoles, SIGNAL("activated(const QModelIndex&)"),self.onRoleSelected)      
        QObject.connect(self.lstRoles, SIGNAL("clicked(const QModelIndex&)"),self.onRoleSelected)

    def loadContent(self):
        '''
        Loads STDM content items
        '''
        self.content = Content()
        #self.content=Table('content_base',Base.metadata,autoload=True,autoload_with=STDMDb.instance().engine)
        cntItems = self.content.queryObject().all()
        '''
        self.content=Table('content_base',Base.metadata,autoload=True,autoload_with=STDMDb.instance().engine)
        
        session= STDMDb.instance().session
        cntItems=session.query(self.content)
        '''
        cnts = [cntItem.name for cntItem in cntItems]
        self.contentModel = UsersRolesModel(cnts)        
        self.lstContent.setModel(self.contentModel)
        
    def loadRoles(self,contentname = ""):
        '''
        Loads the roles in the database cluster
        '''
        self.roleProvider = RoleProvider()
        sysRoles = self.roleProvider.GetAllRoles()
        roles = []
        
        #Load the corresponding roles for the specified content item
        cnt=Content()
        if contentname != "":
            self.currentContent = self.content.queryObject().filter(Content.name == contentname).first()
            if self.currentContent:                
                roles = [rl.name for rl in self.currentContent.roles]
        
        #Initialize model
        self.roleMappingsModel = QStandardItemModel(self)
        self.roleMappingsModel.setColumnCount(1)
        
        #Add role items into the standard item model
        for r in range(len(sysRoles)):
            role = sysRoles[r]
            if role.name != "postgres":
                roleItem = self._createNewRoleItem(role.name)
                
                #Check if the db role is in the approved for the current content item
                roleIndex = getIndex(roles,role.name)
                if roleIndex != -1:
                    roleItem.setCheckState(Qt.Checked)
                
                self.roleMappingsModel.appendRow(roleItem)
             
        self.lstRoles.setModel(self.roleMappingsModel)       
        
    def _createNewRoleItem(self,rolename):
        '''
        Creates a custom role item for use in a QStandardItemModel
        '''
        #Set icon
        icon = QIcon()
        icon.addPixmap(QPixmap(":/plugins/stdm/images/icons/roles.png"), QIcon.Normal, QIcon.Off)
        
        roleItem = QStandardItem(icon,rolename)
        roleItem.setCheckable(True)
        roleItem.setCheckState(Qt.Unchecked)
        
        return roleItem
    
    def onContentClicked(self,index):
        '''
        Slot activated when a content item is selected to load the roles for the specified content items
        '''
        self.lstRoles.setEnabled(True)
        contentName = index.data()
        self.loadRoles(contentName)
        self.auth = Auth(contentName)
        
    def onRoleSelected(self,index):
        '''
        Slot which is called when a user checks/unchecks to add/remove a role for the 
        specified content item.
        '''
        if self.currentContent != None:
            
            item = self.roleMappingsModel.itemFromIndex(index)
            rolename = item.text()

            self.auth.role = rolename
            
            #Get role object from role name
            role = Role()
            rl = role.queryObject().filter(Role.name == rolename).first()
            
            self.blockSignals(True)            
            
            #Add role to the content item if the item is selected  or remove if it was previosuly checked
            if item.checkState() == Qt.Checked:    
                self.currentContent.roles.append(rl)             
                self.auth.grant_rights()
                
            elif item.checkState() == Qt.Unchecked:
                self.currentContent.roles.remove(rl)
                #self.auth.deny_rights()
                
            self.currentContent.update()
                
            self.blockSignals(False)
    
    

class Auth(object):
    def __init__(self, content_name):
        self.content_name = content_name
        self.fk_tables = set()
        self.role = ''
        self.profile = current_profile()
        self.content_short_name =''
        self.action = ''
        self.set_content_name_action(self.content_name)
        self.content_table_name = self.table_name(self.content_short_name)
        self.fetch_fk_tables(self.content_short_name)

    def fmt_name(self, name, action):
        return name.strip(action).replace(' ','_')

    def table_name(self, short_name):
        table_name = ''
        if short_name in self.profile.entities:
            table_name = self.profile.entities[short_name].name
        return table_name

    def set_content_name_action(self, cnt_name):
        if cnt_name.find('Create') == 0:
            self.action, self.content_short_name = 'Create', self.fmt_name(cnt_name, 'Create ')

        if cnt_name.find('Select') == 0:
            self.action, self.content_short_name = 'Select', self.fmt_name(cnt_name, 'Select ')

        if cnt_name.find('Update') == 0:
            self.action, self.content_short_name = 'Update', self.fmt_name(cnt_name,'Update ')

        if cnt_name.find('Delete') == 0:
            self.action, self.content_short_name = 'Delete', self.fmt_name(cnt_name,'Delete ')

    def fetch_fk_tables(self, short_name):
        if short_name in self.profile.entities:
            for column in self.profile.entities[short_name].columns.values():
                if hasattr(column, 'entity_relation'):
                    self.fk_tables.add(column.entity_relation.parent.name)

    def grant_rights(self):
        print "Grant rights to Role", self.role
        for fkt in self.fk_tables:
            print fkt

    def grant_fk_rights(self):
        pass
    

