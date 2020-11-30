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
from typing import Optional, Union

import sqlalchemy
from qgis.core import QgsDataSourceUri
from sqlalchemy import create_engine


class DatabaseConnection:
    """
    Class for capturing the minimum database connection properties
    """

    def __init__(self, Host: str, Port: Union[str, int], Database: str):
        self.Host = Host
        self.Port = int(Port)
        self.Database = Database
        self.User = None

    def toAlchemyConnection(self) -> Optional[str]:
        """
        Returns the corresponding connection string in SQLAlchemy format
        """
        if self.User:
            return "postgresql+psycopg2://%s:%s@%s:%s/%s" % (
                self.User.UserName, self.User.Password, self.Host, self.Port, self.Database)
        else:
            return None

    def toPsycopg2Connection(self):
        """
        Returns the corresponding connection string in Psycopg2 format
        """
        pass

    def validateConnection(self):
        """
        Return whether the connection is valid or not
        """
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
            errMsg = str(oe)
        except Exception as e:
            errMsg = str(e)

        return isValid, errMsg

    def toQgsDataSourceUri(self) -> QgsDataSourceUri:
        """
        Returns a QgsDataSourceURI object with database connection properties
        defined.
        """
        dt_source = QgsDataSourceUri()
        dt_source.setConnection(self.Host, str(self.Port), self.Database,
                                self.User.UserName, str(self.User.Password))

        return dt_source
