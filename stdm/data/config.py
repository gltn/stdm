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
from typing import Optional

from stdm.data.connection import DatabaseConnection
from stdm.settings.registryconfig import RegistryConfig


class DatabaseConfig:
    """
    Reads and writes database settings in the registry.
    """
    HOST = "Host"
    PORT = "Port"
    DB_NAME = "Database"

    def __init__(self):
        self.reg_config = RegistryConfig()

    def read(self) -> Optional[DatabaseConnection]:
        """
        Get the database connection properties
        """
        db_props = self.reg_config.read([DatabaseConfig.HOST, DatabaseConfig.PORT, DatabaseConfig.DB_NAME])

        if len(db_props) < 3:
            return None
        else:
            return DatabaseConnection(db_props[DatabaseConfig.HOST],
                                      db_props[DatabaseConfig.PORT],
                                      db_props[DatabaseConfig.DB_NAME])

    def write(self, db_connection):
        """
        Writes the database connection settings to the registry
        """
        db_settings = {DatabaseConfig.HOST: db_connection.Host,
                       DatabaseConfig.PORT: db_connection.Port,
                       DatabaseConfig.DB_NAME: db_connection.Database}

        self.reg_config.write(db_settings)
