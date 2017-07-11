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

CONFIG_FILE = HOME + '/.stdm/downloads'


class ImportLogger:
    """
    Class constructor
    """
    def __init__(self):
        """
        Initialize vairables
        """
        self.config_logger = ConfigParser.RawConfigParser()

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

        config_location = self.logger_path()
        if os.path.isfile(config_location + '/history.ini'):
            return config_location + '/history.ini'
        else:
           return open(config_location + '/history.ini', 'r')

    def read_logger(self,):
        """
        """
        logger = self.create_logger_doc()
        return logger

    def logger_document(self):
        """

        :return:
        """
        return self.create_logger_doc()

    def logger_sections(self):
        """
        Create sections in the logger document
        :return:
        """
        logger = self.read_logger()
        with open(logger, 'r') as f:
            self.config_logger.read(f)
            if self.config_logger.has_section('imports'):
                return
            else:
                self.config_logger.add_section('imports')
            f.close()

    def check_file_exist(self, instance):
        """

        :return:
        """
        logger = self.read_logger()
        with open(logger, 'r') as f:
            self.config_logger.read(f)
            if self.config_logger.has_section('imports'):
                return self.config_logger.get('imports', instance)
            f.close()

    def write_section_data(self, path, file_name):
        """

        :return:
        """
        logger = self.read_logger()
        with open(logger, 'w') as f:
            self.config_logger.set('imports',path, file_name)
            self.config_logger.write(f)
            f.close()



