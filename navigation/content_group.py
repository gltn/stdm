"""
/***************************************************************************
Name                 : ContentGroup
Description          : Groups related content items together
Date                 : 29/April/2014
copyright            : (C) 2014 by John Gitau
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
import hashlib

from PyQt4.QtGui import QApplication
from PyQt4.QtCore import pyqtSignal,QObject

from sqlalchemy import (
        Table,
        and_
        )

from stdm.data.database import (
    Content,
    Role,
    STDMDb,
    Base
)

from stdm.utils.util import randomCodeGenerator
from stdm.utils.hashable_mixin import HashableMixin

__all__ = ["ContentGroup,TableContentGroup"]

class ContentGroup(QObject,HashableMixin):
    """
    Groups related content items together.
    """
    contentAuthorized = pyqtSignal(Content)
    
    def __init__(self,username,containerItem = None,parent = None):
        from stdm.security.authorization import Authorizer

        QObject.__init__(self,parent)
        HashableMixin.__init__(self)
        self._username = username
        self._contentItems = []
        self._authorizer = Authorizer(self._username)
        self._containerItem = containerItem
        
    def hasPermission(self,content):
        """
        Checks whether the currently logged in user has permissions to access
        the given content item.
        """
        return self._authorizer.CheckAccess(content.code)
    
    @staticmethod
    def contentItemFromQAction(qAction):
        """
        Creates a Content object from a QAction object.
        """
        cnt = Content()
        cnt.name = qAction.text()
        
        return cnt
    
    def contentItems(self):
        """
        Returns a list of content items in the group.
        """
        return self._contentItems
    
    def addContent(self,name,code):
        """
        Create a new Content item and add it to the collection.
        """
        cnt = Content()
        cnt.name = name
        cnt.code = code
        
        self._contentItems.append(cnt)
        
    def addContentItems(self,contents):
        """
        Append list of content items to the group's collection.
        """
        self._contentItems.extend(contents)
        
    def addContentItem(self,content):
        """
        Adds a Content instance to the collection.
        """
        self._contentItems.append(content)
    
    def setContainerItem(self,containerItem):
        """
        ContainerItem can be a QAction, QListWidgetItem, etc. that can be associated with the group.
        """
        self._containerItem = containerItem
        
    def containerItem(self):
        """
        Returns an instance of a ContainerItem associated with this group.
        """
        return self._containerItem
    
    def checkContentAccess(self):
        """
        Asserts whether each content item(s) in the group has access permissions.
        For each item that has permission then a signal is raised containing the
        Content item as an argument.
        Those items which have been granted permission will be returned in a list.
        """
        allowedContent = []
        
        for c in self.contentItems():
            hasPerm = self.hasPermission(c)
            if hasPerm:
                allowedContent.append(c)
                self.contentAuthorized.emit(c)
            
        return allowedContent
    
    def hash_code(self, name):
        ht = hashlib.sha1(name.encode('utf-8'))
        return ht.hexdigest()

    def register(self):
        """
        Registers the content items into the database. Registration only works for a 
        postgres user account.
        """
        PG_ACCOUNT = "postgres"   
        
        if self._username == PG_ACCOUNT:
            for c in self.contentItems():
                if isinstance(c,Content):
                    cnt = Content()
                    qo = cnt.queryObject()

                    if c.code is None:
                        code = self.hash_code(unicode(c.name))
                        cn = c
                    else:
                        code = c.code

                    cn = qo.filter(Content.code == code).first()

                    #If content not found then add
                    if cn is None:
                        #Check if the 'postgres' role is defined, if not then create one
                        rl = Role()
                        rolequery = rl.queryObject()
                        role = rolequery.filter(Role.name == PG_ACCOUNT).first()
                        
                        if role is None:
                            rl.name = PG_ACCOUNT
                            rl.contents = [c]
                            rl.save()                     
                        else:
                            existingContents = role.contents
                            #Append new content to existing 
                            if c.code is None:
                                c.code = code 

                            if len([e_cont for e_cont in existingContents if e_cont.name ==  c.name])==0:
                                existingContents.append(c)
                                role.contents = existingContents
                                role.update()
        else:
            for c in self.contentItems():
                if isinstance(c,Content):
                    cnt = Content()
                    qo = cnt.queryObject()
                    cn = qo.filter(Content.name == c.name).first()
                    c.code = cn.code


            
class TableContentGroup(ContentGroup):
    """
    For grouping CRUD operations for a specific model corresponding
    to a given database table.
    """
    create_op = QApplication.translate("DatabaseContentGroup", "Create")
    read_op = QApplication.translate("DatabaseContentGroup", "Select")
    update_op = QApplication.translate("DatabaseContentGroup", "Update")
    delete_op = QApplication.translate("DatabaseContentGroup", "Delete")
    
    def __init__(self, username, groupName, action=None):
        ContentGroup.__init__(self, username, action)
        self._groupName = groupName
        self._createDbOpContent()
        
    def _createDbOpContent(self):
        """
        Create content for database operations.
        The code for each content needs to be set by the caller.
        """
        self._createCnt = Content()
        self._createCnt.name = self._buildName(self.create_op)
        self.addContentItem(self._createCnt)
        
        self._readCnt = Content()
        self._readCnt.name = self._buildName(self.read_op)
        self.addContentItem(self._readCnt)
        
        self._updateCnt = Content()
        self._updateCnt.name = self._buildName(self.update_op)
        self.addContentItem(self._updateCnt)
        
        self._deleteCnt = Content()
        self._deleteCnt.name = self._buildName(self.delete_op)
        self.addContentItem(self._deleteCnt)
        
    def _buildName(self, db_operation):
        """
        Appends group name to the database operation 
        `Create Person`
        """
        return u"{0} {1}".format(db_operation, self._groupName)
        
    def createContentItem(self):
        """
        Returns Create content item.
        """
        return self._createCnt
    
    def readContentItem(self):
        """
        Returns Read/Select content item.
        """
        return self._readCnt
    
    def updateContentItem(self):
        """
        Returns Update content item.
        """
        return self._updateCnt
    
    def deleteContentItem(self):
        """
        Returns Delete content item.
        """
        return self._deleteCnt
    
    def canRead(self):
        """
        Returns whether the current user has read permissions.
        """
        return self.hasPermission(self._readCnt)
    
    def canCreate(self):
        """
        Returns whether the current user has create permissions.
        """
        return self.hasPermission(self._createCnt)
    
    def canUpdate(self):
        """
        Returns whether the current user has update permissions.
        """
        return self.hasPermission(self._updateCnt)
    
    def canDelete(self):
        """
        Returns whether the current user has delete permissions.
        """
        return self.hasPermission(self._deleteCnt)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
