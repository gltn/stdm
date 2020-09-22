"""
/***************************************************************************
Name                 : UUIDExtractor
Description          : A class to read and extract the unique key for the file and rename it

Date                 : 16/June/2017
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
from PyQt4.QtCore import QFile, QIODevice
from PyQt4.QtXml import (
    QDomDocument,
    QDomNode
)

UUID = "uuid"
from collections import OrderedDict

class InstanceUUIDExtractor():
    """
    Class constructor
    """
    def __init__(self, path):
        """
        Initatlize class variables
        """
        self.file_path = path
        self.file = None
        self.new_list = []
        self.doc = QDomDocument()
        self.node = QDomNode()

    def set_file_path(self, path):
        """
        Update the path based on the new file being read
        :param path:
        :return:
        """
        self.file_path = path

    def unset_path(self):
        """Clear the current document path"""
        self.file_path = None


    def set_document(self):
        """
        :return:
        """
        self.file = QFile(self.file_path)
        if self.file.open(QIODevice.ReadOnly):
            self.doc.setContent(self.file)
        self.file.close()

    def update_document(self):
        '''Update the current instance by clearing the document in the cache '''
        self.doc.clear()
        self.set_document()

    def on_file_passed(self):
        """
        Pass the raw file to an xml document object and format the its filename to GeoODK standards
        :return:
        """
        try:
            self.set_document()
            self.read_uuid_element()
            self.doc.clear()
            self.file.close()
            self.rename_file()
        except:
            pass

    def read_uuid_element(self):
        """
        get the uuid element and text from the xml document from the mobile divice
        """
        node = self.doc.elementsByTagName("meta")
        for i in range(node.count()):
            node = node.item(i).firstChild().toElement()
            self.node = node.text()
        return self.node

    def document_entities(self, profile):
        """
        Get entities in the document
        :return:
        """
        self.set_document()
        node_list = []
        nodes = self.doc.elementsByTagName(profile)
        node = nodes.item(0).childNodes()
        if node:
            for j in range(node.count()):
                node_val = node.item(j)
                node_list.append(node_val.nodeName())
        return node_list

    def profile_entity_nodes(self, profile):
        '''
        Fetch and return QDomNodeList for entities of a
        profile
        :rtype: QDomNodeList
        '''
        self.set_document()
        nodes = self.doc.elementsByTagName(profile)
        return nodes.item(0).childNodes()

    def document_entities_with_data(self, profile, selected_entities):
        """
        Get entities in the dom document matching user
        selected entities
        :rtype: OrderedDict
        """

        instance_data = OrderedDict()
        self.set_document()
        nodes = self.doc.elementsByTagName(profile)
        entity_nodes = nodes.item(0).childNodes()
        for attrs in range(entity_nodes.count()):
            if entity_nodes.item(attrs).nodeName() in selected_entities:
                name_entity = entity_nodes.item(attrs).nodeName()
                attr_nodes = self.doc.elementsByTagName(name_entity)
                instance_data[attr_nodes] = name_entity
        return instance_data

    def attribute_data_from_nodelist(self, args_list):
        """
        process nodelist data before Importing  attribute data into db
        """
        repeat_instance_data = OrderedDict()
        attribute_data = OrderedDict()
        for attr_nodes, entity in args_list.iteritems():
            '''The assuption is that there are repeated entities from mobile sub forms. handle them separately'''
            if attr_nodes.count()>1:
                for i in range(attr_nodes.count()):
                    attrib_node = attr_nodes.at(i).childNodes()
                    attr_list = OrderedDict()
                    for j in range(attrib_node.count()):
                        field_name = attrib_node.at(j).nodeName()
                        field_value = attrib_node.at(j).toElement().text()
                        attr_list[field_name] = field_value
                    repeat_instance_data['{}'.format(i)+entity] = attr_list
            else:
                '''Entities must appear onces in the form'''
                node_list_var =OrderedDict()
                attr_node = attr_nodes.at(0).childNodes()
                for j in range(attr_node.count()):
                    field_name = attr_node.at(j).nodeName()
                    field_value = attr_node.at(j).toElement().text()
                    node_list_var[field_name] = field_value
                attribute_data[entity] = node_list_var
        return attribute_data, repeat_instance_data

    def read_attribute_data_from_node(self, node, entity_name):
        """Read attribute data from a node item"""
        node_list_var = OrderedDict()
        attributes = OrderedDict()
        attr_node = node.at(0).childNodes()
        for j in range(attr_node.count()):
            field_name = attr_node.at(j).nodeName()
            field_value = attr_node.at(j).toElement().text()
            node_list_var[field_name] = field_value
        attributes[entity_name] = node_list_var
        return attributes


    def str_definition(self, instance = None):
        """
        Check if the instance file has entry social tenure
        :return:
        """
        if instance:
            self.set_file_path(instance)
            self.set_document()
        attributes = {}
        nodes = self.doc.elementsByTagName('social_tenure')
        entity_nodes = nodes.item(0).childNodes()
        if entity_nodes:
            for j in range(entity_nodes.count()):
                node_val = entity_nodes.item(j).toElement()
                attributes[node_val.nodeName()] = node_val.text().rstrip()
        return attributes

    def has_str_captured_in_instance(self, instance):
        """
        Bool if the str inclusion is required based on whether is captured or not
        :return:
        """
        count = len(self.str_definition(instance))
        return True if count > 1 else False

    def entity_atrributes(self):
        """
        Get collected data from the entity in the document
        :return:
        """
        pass

    def uuid_element(self):
        """
        Format the guuid from the file
        :return:
        """
        return self.node.replace(":","")

    def rename_file(self):
        """
        Remane the existing instance file with Guuid from the mobile divice to conform with GeoODk naming
        convention
        :return:
        """
        if isinstance(self.file, QFile):
            dir_n, file_n = os.path.split(self.file_path)
            os.chdir(dir_n)
            if not file_n.startswith(UUID):
                new_file_name = self.uuid_element()+".xml"
                isrenamed = self.file.setFileName(new_file_name)
                os.rename(file_n, new_file_name)
                self.new_list.append(new_file_name)
                return isrenamed
            else:
                self.new_list.append(self.file.fileName())
            self.file.close()
        else:
            return

    def file_list(self):
        """
        check through the list of document to ensure they are complete file path
        """
        complete_file = []
        for fi in self.new_list:
            if os.path.isfile(fi):
                complete_file.append(fi)
            else:
                continue
        return complete_file


    def close_document(self):
        '''Close all the open documents and unset current paths'''
        self.file_path = None
        self.doc.clear()
        self.new_list = None
