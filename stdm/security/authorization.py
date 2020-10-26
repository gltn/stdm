"""
/***************************************************************************
Name                 : Auhtorization Service
Description          : Checks whether the logged in user has permissions to
                        access the particular content item
Date                 : 2/June/2013
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
from stdm.security.roleprovider import RoleProvider
from stdm.data.database import Content
from stdm.utils.util import getIndex


class RoleMapper(object):
    pass

class Authorizer(object):
    '''
    This class has the responsibility of asserting whether an account with
    the given user name has permissions to access a particular content item
    '''
    def __init__(self, username):
        self.username = username
        self.userRoles = []
        self._getUserRoles()

    def _getUserRoles(self):
        '''
        Get roles that the user belongs to
        '''
        roleProvider = RoleProvider()
        self.userRoles = roleProvider.GetRolesForUser(self.username)
        '''
        If user name is postgres then add it to the list of user roles since
        it is not a group role in PostgreSQL but content is initialized by
        morphing it as a role in registering content items
        '''
        pg_account = 'postgres'
        if self.username == pg_account:
            self.userRoles.append(pg_account)

    def CheckAccess(self, contentCode):
        '''
        Assert whether the given user has permissions to access a content
        item with the gien code.
        '''
        hasPermission = False
        #Get roles with permission
        try:
            cnt = Content()
            qo = cnt.queryObject()
            '''            
            cntRef = qo.filter(Content.code == contentCode).first()            
            '''
            cntRef = qo.filter(Content.code == contentCode).first()
            if cntRef != None:
                cntRoles =cntRef.roles
                for rl in cntRoles:
                    if getIndex(self.userRoles,rl.name) != -1:
                        hasPermission = True
                        break
        except Exception:
            '''
            Current user does not have permission to access the content tables.
            Catches all errors
            '''
            #pass
            raise
        return hasPermission












