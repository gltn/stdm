"""
/***************************************************************************
Name                 : Membership Service
Description          : Provides generic user management functions
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
from stdm.data.database import STDMDb
from exception import SecurityException
from user import User

from sqlalchemy.sql.expression import text
from PyQt4.QtGui import *

class Membership(object):
    '''
    Provides generic user management functionality
    '''    
    def __init__(self):
        self._engine = STDMDb.instance().engine
        
        #Define membership settings. In future, there will be a better way of defining these settings
        self._minUserLength = 6
        self._minPassLength = 6
        
    def createUser(self,user,isupdate = False):
        '''
        Creates a new user in the system.
        If 'isupdate' equal to True then system will issue
        an ALTER ROLE command 
        '''
        #Validate username and password
        if len(user.UserName) < self._minUserLength:
            self._raiseUserNameException()
            return
        if len(user.Password) < self._minPassLength:
            self._raisePasswordException()
            return
        
        #Validate if the user exists only if its a new user
        if not isupdate:            
            similarUser = self.getUser(user.UserName)
            if similarUser != None:
                self._raiseUserExistsException(user.UserName)
                return
        
        #Build SQL statement
        sql = []
        if isupdate == True:
            sql.append("ALTER")
        else:
            sql.append("CREATE")
        sql.append(" ROLE %s ")
        sql.append("WITH LOGIN PASSWORD :userpass ")
                
        if user.Validity != None:
            sql.append("VALID UNTIL :uservalid ") 
        
        sql.append("NOSUPERUSER INHERIT NOCREATEDB CREATEROLE NOREPLICATION")
        sql.append(";")
        
        sqlStr = ''.join(sql)
        
        #raise NameError(sqlStr + "," + str(user.Validity))
        
        #Execute query using SQLAlchemy connection object
        t = text(sqlStr%(user.UserName,))
        conn = self._engine.connect()
        result = conn.execute(t,userpass = user.Password,uservalid = str(user.Validity))
        conn.close()
 
    def getUser(self,username):
        '''
        Gets the user object based on the username. 
        Returns 'None' if not found
        '''
        user = None
        
        t = text("select valuntil from pg_user where usename = :uname")
        conn = self._engine.connect()
        result = conn.execute(t,uname = username).fetchone()
        
        if result != None:
            user = User(username)
            
            #Get the date component only - first ten characters
            valDate = result["valuntil"]
            if valDate != None:                
                valDate = valDate[:10]  
                          
            user.Validity = valDate
        
        return user
    
    def deleteUser(self,username):
        '''
        Drops the specified user from the database cluster
        '''
        #Check to see if the user exists 
        user = self.getUser(username)
        
        if user != None:
            t = text("DROP ROLE %s;"%(username,))
            conn = self._engine.connect()
            conn.execute(t)
    
    def getAllUsers(self):
        '''
        Returns the names of all user accounts in the cluster of the PostgreSQL server
        '''
        t = text("select usename from pg_user")
        conn = self._engine.connect()
        result = conn.execute(t)
        
        users = []
        for row in result:
            username = row["usename"]
            #Exclude the 'postres' account from this list
            if username != 'postgres':                
                users.append(username)
        
        return users
        
    def setPassword(self,username,password):
        '''
        Define a new password for the specified username
        '''
        if len(password) >= self._minPassLength:            
            #Get the SQLAlchemy connection object
            t = text("ALTER USER %s WITH PASSWORD :userpass"%(username,))
            conn = self._engine.connect()        
            result = conn.execute(t, userpass = password)
            conn.close()
        else:
            self._raisePasswordException()
                    
    def _raisePasswordException(self):
        '''
        Raised when a password condition is not met 
        '''
        msg = str(QApplication.translate("PasswordError","Password length must be equal to or greater than %s characters"%(str(self._minPassLength,))))
        raise SecurityException(msg)
    
    def _raiseUserNameException(self):
        '''
        Raised when a username condition is not met 
        '''
        msg = str(QApplication.translate("UsernameError","Username length must be equal to or greater than %s characters"%(str(self._minUserLength,))))
        raise SecurityException(msg)
    
    def _raiseUserExistsException(self,username):
        '''
        Raised when a user with the given username exists 
        '''
        msg = str(QApplication.translate("UserAccountError","'%s' account already exists.Please specify another username."%(username,)))
        raise SecurityException(msg)
            
            

        
        
        
        
        
        
        
        
        
        