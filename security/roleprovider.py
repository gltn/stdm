"""
/***************************************************************************
Name                 : STDM Role Provider
Description          : Provides role management for existing users in the
                        STDM database
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
from stdm.data.database import STDMDb, Role
from stdm.utils import *
from exception import SecurityException

from sqlalchemy.sql.expression import text

from PyQt4.QtGui import *

class RoleProvider(object):
    '''
    Provides full role management functionality by implementing the 
    underlying PostgreSQL role-based security model
    '''
    #Actions
    ADD = "GRANT"
    REMOVE = "REVOKE"
    
    def __init__(self):
        #Create internal reference to database engine
        self._engine = STDMDb.instance().engine
                
    def syncSTDMRoles(self):
        '''
        Synchronizes STDM roles with the database cluster roles.
        By default, this method is executed when an instance of this
        class is created. 
        '''
        sysRoles = self.GetSysRoles()        
        stdmRoles = [role.name for role in self.GetAllRoles()]
                
        #Add missing sysroles to STDM roles
        for sysRole in sysRoles:
            roleIndex = getIndex(stdmRoles,sysRole)                    
            
            if roleIndex == -1:                
                self.AddSTDMRole(sysRole)
              
        #Remove obsolete roles from the STDM roles table
        for stdmRole in stdmRoles:
            roleIndex = getIndex(sysRoles,stdmRole)
            
            if roleIndex == -1:
                self.DeleteSTDMRole(stdmRole)   
                
    def syncSysRoles(self):
        '''
        Ensure system roles are upto-date with STDM roles (latter as the reference).
        Reverse of 'syncSTDMRoles'.
        '''
        sysRoles = self.GetSysRoles()        
        stdmRoles = [role.name for role in self.GetAllRoles()]
                
        #Add missing STDMRoles to sysRoles
        for stdmRole in stdmRoles:
            roleIndex = getIndex(sysRoles,stdmRole)                    
            
            if roleIndex == -1:                
                self.CreateRole(stdmRole)
              
        #Remove obsolete system roles 
        for sysRole in sysRoles:
            roleIndex = getIndex(stdmRoles,sysRole)
            
            if roleIndex == -1:
                self.DeleteRole(sysRole) 
                         
    def GetSysRoles(self):
        '''
        Get the database cluster roles
        '''
        t = text("select rolname from pg_roles where rolcanlogin='False'")
        result = self._execute(t)
        #Iterate through resultset
        sysRoles = []
        for row in result:
            sysRoles.append(row["rolname"])
        
        #Include default postgres account in the sys roles
        sysRoles.append("postgres")
           
        return sysRoles
    
    def IsUserInRole(self,userName,roleName):
        '''
        Does the specified username belong to the given role
        '''
        #Get the roles that the user belongs to
        uRoles = self.GetRolesForUser(userName)
        roleIndex = getIndex(uRoles,roleName)
        exist = False if roleIndex == -1 else True
        return exist
    
    def GetRolesForUser(self,userName):
        '''
        Get all the roles that the user, with the given username, belongs to.
        '''
        #Create string builder object
        sb = []
        sb.append("select rolname from pg_user ")
        sb.append("join pg_auth_members on (pg_user.usesysid=pg_auth_members.member) ")
        sb.append("join pg_roles on (pg_roles.oid=pg_auth_members.roleid) ")
        sb.append("where pg_user.usename=:uname")
        sql = ''.join(sb)
        t = text(sql)
        result = self._execute(t,uname = userName)
        #Iterate through result proxy to get the rolenames
        userRoles = []
        for row in result:
            userRoles.append(row["rolname"])
                            
        return userRoles
    
    def CreateRole(self,roleName,description='',grantSchema = 'public'):
        '''
        Create a new role
        '''
        sql = []
        sql.append("CREATE ROLE %s CREATEROLE;"%(roleName,))
        if description != "":
            sql.append("COMMENT ON ROLE %s is '%s';"%(roleName,description))
            
        '''
        Grant privileges to the new role so that users in this role can be able
        to access the tables and relations.
        The specified schema will have all the tables and relations granted with
        all privileges.                 
        '''
        sql.append("GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA %s TO %s;"%(grantSchema,roleName))
        sqlStr = ''.join(sql)
        t = text(sqlStr)
        self._execute(t)
        
    def AddSTDMRole(self,rolename,description = ""):
        '''
        Add role to STDM roles table
        '''
        rl = Role()
        existRole = rl.queryObject().filter(Role.name == rolename).first()        
        if existRole == None:
            rl.name = rolename 
            rl.description = description   
            rl.save()    
            
    def DeleteSTDMRole(self,rolename):
        '''
        Delete STDM role
        '''
        rl = Role()
        existRole = rl.queryObject().filter(Role.name == rolename).first()
        if existRole != None:
            existRole.delete()            
        
    def DeleteRole(self,roleName):
        '''
        Remove any database objects owned by the given rolename plus the 
        cascading dependencies then delete the role.
        '''
        t = text("DROP OWNED BY %s CASCADE;DROP ROLE %s;"%(roleName,roleName))
        self._execute(t)
    
    def RoleExists(self,roleName):
        '''
        Assert whether the given role exists
        '''
        #Get role objects
        rolesObj = self.GetAllRoles()
        roles = []
        for roleObj in rolesObj:
            roles.append(roleObj.name)
        roleIndex = getIndex(roles,roleName)
        
        return False if roleIndex == -1 else True
    
    def GetRole(self,rolename):
        '''
        Get the STDM role object based on the rolename
        '''
        rl = Role()
        role = rl.queryObject().filter(Role.name == rolename).first()
        return role
    
    def AddUsersToRoles(self,userNames,roleNames):
        '''
        Add the list of roles to the given user names
        '''
        self._manageUsersInRoles(userNames, roleNames, self.ADD)
    
    def RemoveUsersFromRoles(self,userNames,roleNames):
        '''
        Delete the list of roles from the given user names
        '''
        self._manageUsersInRoles(userNames, roleNames, self.REMOVE)
    
    def _manageUsersInRoles(self,userNames,roleNames,action):
        '''
        Internal function for granting or revoking users 
        to/from roles
        '''       
        refkeyword = "TO" if action == self.ADD else "FROM"
        for role in roleNames:
            usersConcat = ','.join(userNames) 
            '''
            Postgres wierdness where grant command needs an explicit COMMIT
            command issues immediately afterwards.
            '''
            t = text("BEGIN;%s %s %s %s;COMMIT;"%(action,role,refkeyword,usersConcat))            
            result = self._execute(t)                            
    
    def GetUsersInRole(self,roleName):
        '''
        Get all users in the given role
        '''
        users = []
        
        sb = []
        sb.append("select usename from pg_user ")
        sb.append("join pg_auth_members on (pg_user.usesysid = pg_auth_members.member) ")
        sb.append("join pg_roles on (pg_roles.oid = pg_auth_members.roleid) ")
        sb.append("where pg_roles.rolname = :rlname")
        sql = ''.join(sb)
        t = text(sql)
        result = self._execute(t,rlname = roleName)
                
        for row in result:
            users.append(row["usename"])
        
        return users
    
    def GetAllRoles(self):
        '''
        Get all the roles objects in the database server
        '''
        rl = Role()
        qo = rl.queryObject()
        return qo.all()
    
    def _execute(self,sql,**kwargs):
        '''
        Execute the passed in sql statement
        '''        
        conn = self._engine.connect()        
        result = conn.execute(sql,**kwargs)
        conn.close()
        return result
    
    def _raiseRoleExistsException(self,rolename):
        '''
        Raised when a user with the given username exists 
        '''
        msg = str(QApplication.translate("RoleNameError","'%s' role already exists."
                                                         "Please specify another name for the role."%(rolename,)))
        raise SecurityException(msg)
    
    
        
        
        
        
        
        
        
    
    
    
    
    
    
    
    
    