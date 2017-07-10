"""
/***************************************************************************
Name                 : ImportLogger
Description          : A class to read and enumerate imported data to avoid
                    duplications and manage related entities data

Date                 : 03/07/2017
copyright            : (C) 2017 by UN-Habitat and implementing partners.
                       See the accompanying file CONTRIBUTORS.txt in the root
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
import ConfigParser
import os
from PyQt4.QtCore import QDir

HOME = QDir.home().path()

CONFIG_FILE = HOME + '/.stdm/Downloads'


class ImportLogger:
    """
    Class constructor
    """
    def __init__(self):
        """
        Initialize vairables
        """

    def logger_path(self):
        """
        Manage the path to the logger document
        :return:
        """
        logger_path = CONFIG_FILE + '/instance'
        if not os.access(logger_path, os.F_OK):
            os.makedirs(unicode(logger_path))
        else:
            return logger_path

    def create_logger_doc(self):
        """
        Create the log file document
        :return:
        """
        config_logger = ConfigParser.ConfigParser()
        config_location  = self.logger_path()
        if os.path.isfile(config_location + '/history.ini'):
            with open(config_location + '/history.ini', 'w+') as logger:
                config_logger.read(logger)
            return config_logger
        else:
            return None

    def logger_sections(self):
        """
        Create sections in the logger document
        :return:
        """

