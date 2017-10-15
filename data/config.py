"""
/***************************************************************************
Name                 : Database Registry Configuration
Description          : Class for reading and writing database settings for
                       STDM stored in the registry
Date                 : 24/May/2013 
copyright            : (C) 2015 by UN-Habitat and Implementing partners
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

from .connection import DatabaseConnection
from stdm.settings.registryconfig import RegistryConfig

class DatabaseConfig(object):
    """
    Reads and writes database settings in the registry.
    """
    def __init__(self):
        self.host = "Host"
        self.port = "Port"    
        self.db_name = "Database"    
        self.reg_config = RegistryConfig()
        
    def read(self):
        '''
        Get the database connection properties
        '''
        db_props = self.reg_config.read([self.host, self.port, self.db_name])

        if len(db_props) < 3:
            return None
        else:            
            return DatabaseConnection(db_props[self.host], db_props[self.port], db_props[self.db_name])
        
    def write(self, db_connection):
        '''
        Writes the database connection settings to the registry
        '''
        db_settings = {}
        db_settings[self.host] = db_connection.Host
        db_settings[self.port] = db_connection.Port
        db_settings[self.db_name] = db_connection.Database

        self.reg_config.write(db_settings)
    
