"""
/***************************************************************************
Name                 : database Connection
Description          : Class that represents the minimum properties for
                       connecting to a PostgreSQL database. The username and
                       password will not be persisted in this class
Date                 : 25/May/2013 
copyright            : C) 2014 by UN-Habitat and implementing partners.
                       See the accompanying file CONTRIBUTORS.txt in the root
email                : stdm@unhabitat.com
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
import sqlalchemy
from sqlalchemy import create_engine
from qgis.core import QgsDataSourceURI

class databaseConnection(object):
    '''
    Class for capturing the minimum database connection properties
    '''
    def __init__(self, host, port, database):
        self.host = host
        self.port = port
        self.database = database
        self.user = None
        
    def to_alchemy_connection(self):
        '''
        Returns the corresponding connection string in SQLAlchemy format
        '''
        if self.user:
            return "postgresql+psycopg2://%s:%s@%s:%s/%s" % (self.user.userName, self.user.Password, self.host, self.port, self.database)
        else:
            return None
    
    def to_psycopg2_connection(self):
        '''
        Returns the corresponding connection string in Psycopg2 format
        '''
        pass
    
    def validate_connection(self):
        '''
        Return whether the connection is valid or not
        '''
        isvalid = False
        errmsg = ""
        engine = create_engine(self.to_alchemy_connection(), echo=False)

        try:
            conn = engine.connect()
            conn.close()
            isvalid = True
        except sqlalchemy.exc.OperationalError as oe:
            errmsg = oe.message
        except Exception as e:
            errmsg = unicode(e)

        return isvalid, errmsg

    def to_qgs_datasource_Uri(self):
        """
        Returns a QgsDataSourceURI object with database connection properties
        defined.
        """
        dt_source = QgsDataSourceURI()
        dt_source.setConnection(self.host, self.port, self.database,
                                self.user.userName, self.user.Password)

        return dt_source
    
