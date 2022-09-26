"""
/***************************************************************************
Name                 : Database Connection
Description          : Class that represents the minimum properties for
                        connecting to a PostgreSQL database. The username and
                        password will not be persisted in this class
Date                 : 25/May/2013 
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
import sqlalchemy
from sqlalchemy import create_engine
from qgis.core import QgsDataSourceURI

class DatabaseConnection(object):
    '''
    Class for capturing the minimum database connection properties
    '''
    def __init__(self, Host, Port, Database, user='postgres', password=''):
        self.Host = Host
        self.Port = Port
        self.Database = Database
        self._user = user
        self._password = password
        self.User = None
        
    def toAlchemyConnection(self):
        '''
        Returns the corresponding connection string in SQLAlchemy format
        '''
        if self.User:
            user = self.User.UserName
            password = self.User.Password
        else:
            user = self._user
            password = self._password

        return "postgresql+psycopg2://{}:{}@{}:{}/{}".format(
                user, password, self.Host, self.Port, self.Database)
    
    def toPsycopg2Connection(self):
        '''
        Returns the corresponding connection string in Psycopg2 format
        '''
        pass
    
    def validateConnection(self):
        '''
        Return whether the connection is valid or not
        '''
        isValid = False
        errMsg = ""
        engine = create_engine(
            self.toAlchemyConnection(),
            echo=False
        )

        try:
            conn = engine.connect()
            conn.close()
            isValid = True
        except sqlalchemy.exc.OperationalError as oe:
            errMsg = oe.message
        except Exception as e:
            errMsg = unicode(e)

        return isValid, errMsg

    def toQgsDataSourceUri(self):
        """
        Returns a QgsDataSourceURI object with database connection properties
        defined.
        """
        dt_source = QgsDataSourceURI()
        dt_source.setConnection(self.Host, unicode(self.Port), self.Database,
                                self.User.UserName, unicode(self.User.Password))

        return dt_source
        
        
        
        
        
        
    
    
