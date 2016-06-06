"""
/***************************************************************************
Name                 : ConfigurationWriter
Description          : Reads/writes configuration object from/to file.
Date                 : 15/February/2016
copyright            : (C) 2015 by UN-Habitat and implementing partners.
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

import os
import shutil

from PyQt4.QtCore import QFile, QIODevice
from PyQt4.QtGui import QMessageBox
from PyQt4.QtXml import QDomDocument

from ..data.configuration.exception import ConfigurationException
from ..data.configfile_paths import FilePaths
from ..data.configuration.stdm_configuration import StdmConfiguration


class ConfigurationFileUpdater(object):
    """
    Updates configuration file to new format and migrates data
    """

    def __init__(self):
        self.file_handler = FilePaths()

    def _check_config_folder_exists(self):
        """
        Checks if .stdm folder exists
        :returns True if folder exists else False
        :rtype bool
        """
        if os.path.isdir(self.file_handler.localPath()):
            return True
        else:
            return False

    def _create_config_folder(self):
        """
        Creates .stdm folder if it doesn't exist
        """
        self.file_handler.createDir(self.file_handler.localPath())

    def _check_config_file_exists(self, config_file):
        """
        Checks if config file exists
        :returns True if folder exists else False
        :rtype bool
        """
        if os.path.isfile(os.path.join(self.file_handler.localPath(),
                                       config_file)):
            return True
        else:
            return False

    def _check_config_version(self):
        stc_config_file = os.path.join(self.file_handler.localPath(),
                                       "configuration.stc")
        config_file = QFile(stc_config_file)
        if not config_file.open(QIODevice.ReadOnly):
            raise IOError('Cannot read configuration file. Check read '
                          'permissions.')
        config_doc = QDomDocument()

        status, msg, line, col = config_doc.setContent(config_file)
        if not status:
            raise ConfigurationException(u'Configuration file cannot be '
                                         u'loaded: {0}'.format(msg))

        config = StdmConfiguration.instance()

        doc_element = config_doc.documentElement()

        config_version = doc_element.attribute('version')

        if config_version:
            config_version = float(config_version)
        else:
            #Fatal error
            raise ConfigurationException('Error extracting version '
                                         'number from the '
                                         'configuration file.')
        if config.VERSION == config_version:
            return True
        else:
            return False

    def _copy_config_file_from_template(self):
        shutil.copy(os.path.join(self.file_handler.defaultConfigPath(),
                                     "configuration.stc"),
                        self.file_handler.localPath())

    def load(self):
        if self._check_config_folder_exists():
            # Check if old configuration file exists
            if self._check_config_file_exists("stdmConfig.xml"):
                QMessageBox.information(None,"STDM","{0}".format(
                    "stdmConfig.xml exists"))
            else:
                if self._check_config_file_exists("configuration.stc"):
                    return True
                else:
                    self._copy_config_file_from_template()
                    return True
        else:
            self._create_config_folder()
            self._copy_config_file_from_template()
        return True

    def check_version(self):
        return self._check_config_version()