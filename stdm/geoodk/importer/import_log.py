"""
/***************************************************************************
Name                 : ImportLogger
Description          : A class to read and enumerate imported data to avoid
                    duplications and checking errors when importing entities data

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
import json
import os
from configparser import RawConfigParser
from datetime import datetime

from qgis.PyQt.QtCore import QDir

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
        self.config_logger = RawConfigParser()
        self.logger_path()

    def logger_path(self):
        """
        Manage the path to the logger document
        :return:
        """
        if not os.access(LOGGER_HOME, os.F_OK):
            os.makedirs(str(LOGGER_HOME))

    def start_json_file(self):
        """
        Create the log file document
        :return:
        """
        try:
            file_n = 'import_log.json'
            if not os.path.isfile(os.path.normpath(LOGGER_HOME + '/' + file_n)):
                return open(LOGGER_HOME + '/' + file_n, 'w+')
            else:
                return os.path.normpath(LOGGER_HOME + '/' + file_n)
        except IOError as ex:
            raise str(ex)

    def enable_logger_document(self):
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
        return self.enable_logger_document()

    def json_file(self):
        """
        Update method to work with Json instead of txt file
        return: Json file
        """
        return self.start_json_file()

    def log_action(self, action):
        """"
        Ensure the logger information is written to the file
        """
        log_file = self.open_logger()
        with open(log_file, 'a') as f:
            f.write('\n')
            f.write(action)
            f.close()

    def write_log_data(self, data):
        """
        :param: data
        :type: dictionary
        """
        raw_file = self.json_file()
        with open(raw_file, "w") as write_file:
            json.dump(data, write_file)
            write_file.close()

    def read_log_data(self):
        """
        rtype: dictionary
        """
        data = {}
        raw_file = self.json_file()
        if os.path.isfile(raw_file):
            try:
                with open(raw_file, "r") as read_file:
                    data = json.load(read_file)
                    read_file.close()
            except:
                pass
        return data

    def log_data_name(self, full_name):
        """
        rtype: str
        """
        base = os.path.basename(full_name)
        short_name = os.path.splitext(base)[0]
        return short_name

    def log_date(self):
        """
        rtype: str
        """
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")
