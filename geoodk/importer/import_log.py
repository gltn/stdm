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

LOGGER_HOME = HOME + '/.stdm/geoodk'
IMPORT_SECTION = 'imports'

class ImportLogger:
    """
    Class constructor
    """
    def __init__(self):
        """
        Initialize vairables
        """
        self.config_logger = ConfigParser.RawConfigParser()
        self.logger_path()

    def logger_path(self):
        """
        Manage the path to the logger document
        :return:
        """
        if not os.access(LOGGER_HOME, os.F_OK):
            os.makedirs(unicode(LOGGER_HOME))

    def create_logger_doc(self):
        """
        Create the log file document
        :return:
        """
        try:
            config_location = LOGGER_HOME
            if os.path.isfile(config_location + '/history.ini'):
                return config_location + '/history.ini'
            else:
                return open(config_location + '/history.ini', 'w+')
        except:
            pass

    def add_log_info(self):
        """
        Create the log file document
        :return:
        """
        try:
            config_location = LOGGER_HOME
            if os.path.isfile(config_location + '/history.txt'):
                return config_location + '/history.txt'
            else:
                return open(config_location + '/history.txt', 'w+')
        except:
            pass

    def open_logger(self):
        """
        Open the logger text file so that we can write data
        :return:
        """
        return self.add_log_info()

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
            if self.config_logger.has_section(IMPORT_SECTION):
                return
            else:
                self.config_logger.add_section(IMPORT_SECTION)
            f.close()

    def check_file_exist(self, instance):
        """

        :return:
        """
        try:
            logger = self.read_logger()
            with open(logger, 'r') as f:
                self.config_logger.read(f)
                if self.config_logger.has_section(IMPORT_SECTION):
                    return self.config_logger.get(IMPORT_SECTION, instance)
                else:
                    return self.config_logger.add_section(IMPORT_SECTION)
                f.close()
        except:
            pass

    def write_section_data(self, path, file_name):
        """

        :return:
        """
        logger = self.read_logger()
        with open(logger, 'w') as f:
            self.config_logger.set(IMPORT_SECTION,path, file_name)
            self.config_logger.write(f)
            f.close()

    def onlogger_action(self, log_entry):
        """"
        Ensure the logger information is written to the file
        """
        log_info = self.open_logger()
        with open(log_info, 'a') as f:
            f.write('\n')
            f.write(log_entry)
            f.close()





