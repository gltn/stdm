"""
/***************************************************************************
Name                 : Database Registry Configuration
Description          : Class for reading and writing database settings for
                        STDM stored in the registry
Date                 : 24/May/2013 
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

from stdm.settings import RegistryConfig
from connection import DatabaseConnection

class DatabaseConfig(object):
    '''
    Reads and writes database settings in the registry
    '''
    def __init__(self):
        self.dbHost = "Host"
        self.dbPort = "Port"    
        self.dbName = "Database"    
        self.regConfig = RegistryConfig()
        
    def read(self):
        '''
        Get the database connection properties
        '''
        dbProps = self.regConfig.read([self.dbHost,self.dbPort,self.dbName])
        if len(dbProps) < 3:
            return None
        else:            
            return DatabaseConnection(dbProps[self.dbHost], dbProps[self.dbPort], dbProps[self.dbName])
        
    def write(self,dbconnection):
        '''
        Writes the database connection settings to the registry
        '''
        dbSettings = {}
        dbSettings[self.dbHost] = dbconnection.Host
        dbSettings[self.dbPort] = dbconnection.Port
        dbSettings[self.dbName] = dbconnection.Database
        #Write dictionary to registry
        self.regConfig.write(dbSettings)
        
    
        
    