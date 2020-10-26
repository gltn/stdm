# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Configuration Utilities
Description          : Utility class for STDM configuration.
Date                 : 10/January/2017
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
import os
from collections import OrderedDict
import datetime
from qgis.PyQt.QtCore import QFile
from qgis.PyQt.QtXml import QDomDocument
from stdm.data.configuration.exception import ConfigurationException

from stdm.data.configfile_paths import FilePaths


class ConfigurationUtils():
    PROFILE = 'Profile'
    SOCIAL_TENURE = 'SocialTenure'
    CONFIGURATION = 'Configuration'

    def __init__(self, document):
        """
        A utility class for STDM configuration.
        :param document: The configuration
        :type document: QDomDocument
        """
        self.file_handler = FilePaths()
        self.log_file_path = '{}/logs/migration.log'.format(
            self.file_handler.localPath()
        )
        self.document = document

    def append_log(self, info):
        """
        Append info to a single file
        :param info: update information to save to file
        :type info: str
        """
        info_file = open(self.log_file_path, "a")
        time_stamp = datetime.datetime.now().strftime(
            '%d-%m-%Y %H:%M:%S'
        )
        info_file.write('\n')
        info_file.write('{} - '.format(time_stamp))
        info_file.write(info)
        info_file.write('\n')
        info_file.close()

    def check_config_file_exists(self, config_file):
        """
        Checks if config file exists
        :returns True if folder exists else False
        :rtype bool
        """
        if os.path.isfile(os.path.join(
                self.file_handler.localPath(),
                config_file)
        ):

            return True
        else:
            return False

    def read_stc(self, config_file_name):
        """
        Reads provided config file
        :returns QDomDocument, QDomDocument.documentElement()
        :rtype tuple
        """
        config_file_path = os.path.join(
            self.file_handler.localPath(),
            config_file_name
        )

        config_file_path = QFile(config_file_path)
        config_file = os.path.basename(config_file_name)
        if self.check_config_file_exists(config_file):

            self.document = QDomDocument()

            status, msg, line, col = self.document.setContent(config_file_path)
            if not status:
                error_message = u'Configuration file cannot be loaded: {0}'.\
                    format(msg)
                self.append_log(str(error_message))

                raise ConfigurationException(error_message)

            self.doc_element = self.document.documentElement()

    def find_node(self, name):
        """
        Get nodes inside a document by a tag name.
        :param document: The xml document
        :type document: QDomDocument
        :param name: the tag name
        :type name: String
        :return: The nodes list
        :rtype: List
        """
        node_list = self.document.elementsByTagName(name)
        nodes = []
        for i in range(node_list.length()):
            node = node_list.item(i)
            nodes.append(node)
        return nodes

    def add_attribute_to_nodes(self, nodes, attr, value):
        """
        Adds an attribute with value to node lists.
        :param nodes: List of nodes
        :type nodes: QNodeList
        :param attr: The attribute text
        :type attr: String
        :param value: The value of the attribute.
        :type value: String
        :return:
        :rtype:
        """
        for node in nodes:
            element = node.toElement()
            element.setAttribute(attr, value)

    def add_attribute_by_node_name(self, node_name, attr, value):
        """
        Add attribute with value to nodes by node name.
        :param node_name: The name of the node.
        :type node_name: Strong
        :param attr: The attribute text
        :type attr: String
        :param value: The value of the attribute.
        :type value: String
        :return:
        :rtype:
        """
        nodes = self.find_node(node_name)
        self.add_attribute_to_nodes(nodes, attr, value)

    def profile_first_child(self, tag_name):
        """
        Gets the first child of profile node
        with a specified tag name.
        :param tag_name: The tag name to be used
        to search the child.
        :type tag_name: String
        :return: Dictionary of parent (profile node) and
        the child element.
        :rtype: OrderedDict
        """
        profile_nodes = self.find_node(self.PROFILE)
        first_child = OrderedDict()
        for profile_node in profile_nodes:
            profile_child = profile_node.firstChildElement(
                tag_name
            )
            first_child[profile_node] = profile_child
        return first_child

    def social_tenure_elements(self):
        """
        Get all social tenure element in a dom_document.
        :return: List of social tenure element
        :rtype: OrderedDict
        """
        social_tenure_nodes = self.profile_first_child(
            self.SOCIAL_TENURE
        )
        return social_tenure_nodes


    def run(self):
        nodes = self.find_node('Entity')

        self.add_attribute_to_nodes(nodes, 'Test', 'One')
