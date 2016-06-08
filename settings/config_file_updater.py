"""
/***************************************************************************
Name                 : Configuration File Updater and Backup
Description          : Updates and backups up the content of either old
                        configuration or new configuration
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

from collections import OrderedDict

from PyQt4.QtCore import QFile, QIODevice, QTextStream
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
        self.version = None
        self.config_profiles = []
        self.table_dict = OrderedDict()
        self.table_list = []
        self.config_file = None

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

    def _get_doc_root(self, path):
        config_file = os.path.join(self.file_handler.localPath(), path)
        config_file = QFile(config_file)
        if not config_file.open(QIODevice.ReadOnly):
            raise IOError('Cannot read configuration file. Check read '
                          'permissions.')
        config_doc = QDomDocument()

        status, msg, line, col = config_doc.setContent(config_file)
        if not status:
            raise ConfigurationException(u'Configuration file cannot be '
                                         u'loaded: {0}'.format(msg))

        doc_element = config_doc.documentElement()

        return doc_element

    def _check_config_version(self):
        doc_element = self._get_doc_root("configuration.stc")

        config_version = doc_element.attribute('version')

        config = StdmConfiguration.instance()

        if config_version:
            config_version = float(config_version)
        else:

            # Fatal error
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

    def _set_table_columns(self, table_name, element):

        for i in range(element.count()):
            column_dict = {}
            columns_node = element.item(i).toElement()
            if columns_node.tagName() == "columns":
                column_nodes = columns_node.childNodes()
                for i in range(column_nodes.count()):
                    column_node = column_nodes.item(i).toElement()
                    col_name = unicode(column_node.attribute('name'))
                    column_dict["col_name"] = col_name
                    col_search = unicode(column_node.attribute('searchable'))
                    column_dict["col_search"] = col_search
                    col_description = unicode(
                        column_node.attribute('fullname'))
                    column_dict["col_descrpt"] = col_description
                    col_type = unicode(column_node.attribute('type'))
                    column_dict["col_type"] = col_type
                self.table_list.append(column_dict)
        self.table_dict[table_name] = self.table_list

    def _set_table_attributes(self, element):

        for i in range(element.count()):
            profile_child_node = element.item(i).toElement()
            if profile_child_node.tagName() == "table":
                table_name = unicode(profile_child_node.attribute('name'))
                self.table_dict["table_name"] = table_name
                table_descrpt = unicode(profile_child_node.attribute(
                                        'fullname'))
                self.table_list.append(table_descrpt)
                table_shortname = unicode(profile_child_node.attribute(
                                    'fullname'))
                self.table_list.append(table_shortname)
                columns_nodes = profile_child_node.childNodes()
                self._set_table_columns(table_name, columns_nodes)

            if profile_child_node.tagName() == "lookup":
                pass

    def _set_version_profile(self, element):
        """
        Internal function to load version and profile to dictionary
        """
        for i in range(element.count()):
            child_node = element.item(i).toElement()
            if child_node.hasAttribute('version'):
                self.version = unicode(child_node.attribute('version'))
            if child_node.tagName() == "profile":
                self.config_profiles.append(unicode(child_node.attribute('name')))
                profile_child_nodes = child_node.childNodes()
                self._set_table_attributes(profile_child_nodes)

    def _create_config_file(self, config_file_name):
        self.config_file = QFile(os.path.join(self.file_handler.localPath(),
                                   config_file_name))

        if not self.config_file.open(QFile.WriteOnly | QFile.Text):
            QMessageBox.warning(None, "Config Error", "Cannot write file {"
                                "0}: \n {2}".format(
                                 self.config_file.fileName(),
                                 self.config_file.errorString()))
        return

    def load(self):
        if self._check_config_folder_exists():

            # Check if old configuration file exists
            if self._check_config_file_exists("stdmConfig.xml"):
                root = self._get_doc_root(os.path.join(
                    self.file_handler.localPath(), "stdmConfig.xml"))
                child_nodes = root.childNodes()

                # Parse old configuration to dictionary
                self._set_version_profile(child_nodes)

                # Create config file
                self._create_config_file("configuration.stc")
                doc = QDomDocument()
                configuration = doc.createElement("Configuration")
                configuration.setAttribute("version", self.version)

                for config_profile in self.config_profiles:
                    profile = doc.createElement("Profile")
                    profile.setAttribute("description", "")
                    profile.setAttribute("name", config_profile)
                    configuration.appendChild(profile)

                doc.appendChild(configuration)

                stream = QTextStream(self.config_file)
                stream << doc.toString()

                return True
            else:
                # Check of new config format exists
                if self._check_config_file_exists("configuration.stc"):
                    return True
                else:
                    # if new config format doesn't exist copy from template
                    self._copy_config_file_from_template()
                    return True
        else:
            self._create_config_folder()
            self._copy_config_file_from_template()
        return True

    def check_version(self):
        return self._check_config_version()