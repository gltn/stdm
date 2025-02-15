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
import copy

from typing import (
        Dict,
        List,
        Tuple,
        TypeVar
        )

from qgis.PyQt.QtCore import QFile, QIODevice
from qgis.PyQt.QtXml import (
    QDomDocument,
    QDomNode,
    QDomNodeList
)

UUID = "uuid"

from collections import OrderedDict

from stdm.exceptions import DummyException

# Type annotations
NodeName   = str
NodeValue  = str
EntityName = str
DictWithOrder = Dict
NodeData = DictWithOrder[NodeName, NodeValue]
EntityInstances = DictWithOrder[EntityName, NodeData]  # a.k.a OrderedDict
RepeatedEntityInstances = DictWithOrder[EntityName, NodeData]

Profile = TypeVar('Profile')  # Profile instance
ProfileName = str
EntityName  = str

class EntityNodeData:
    def __init__(self):
        self.entity_name = ''
        self.entity_nodes = QDomNodeList()


class InstanceUUIDExtractor():
    def __init__(self):
        self.file_path = None
        self.file = None
        self.xml_files = []
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

    def fix_name(self, xml_full_filepath: str) -> str:
        """
        Pass the raw file to an xml document object and format the its filename to GeoODK standards
        :return:
        """
        try:
            #self.set_document()
            dom_document = QDomDocument()
            file = QFile(xml_full_filepath)
            if file.open(QIODevice.ReadOnly):
                dom_document.setContent(file)
            file.close()

            uuid = self.get_uuid_text(dom_document)

            dir, filename = os.path.split(xml_full_filepath)

            if filename.startswith('uuid'):
                return xml_full_filepath

            old_filename = f'{dir}\{filename}'
            new_filename =f'{dir}\{uuid}.xml'
            os.rename(old_filename, new_filename)

            return new_filename


        except DummyException:
            pass

    def get_uuid_text(self, dom_document: QDomDocument) ->str:
        """
        get the uuid  text from the xml document
        """
        node = dom_document.elementsByTagName("meta")
        uuid = ""
        for i in range(node.count()):
            node = node.item(i).firstChild().toElement()
            uuid = node.text()
        return uuid.replace(":", "")

    def document_entities(self, profile : Profile) ->List[ProfileName]:
        """
        Get entities in the document
        :rtype: List of profile names
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

    def profile_entity_nodes(self, profile : Profile) ->QDomNodeList:
        '''
        Fetch and return QDomNodeList for entities of a
        profile
        :rtype: QDomNodeList
        '''
        self.set_document()
        nodes = self.doc.elementsByTagName(profile)
        return nodes.item(0).childNodes()

    def _make_dom_document(self, xml_filename: str):
        xml_file = QFile(xml_filename)
        dom_doc = QDomDocument()
        if xml_file.open(QIODevice.ReadOnly):
            dom_doc.setContent(xml_file)
        xml_file.close() 
        return dom_doc


    def process_node(self, node):
        nodes = OrderedDict() 
        current = node.firstChild()
        while not current.isNull():
            if current.isElement():
                nodes[current.nodeName()] = current.toElement().text()
                self.process_node(current)
            current = current.nextSibling()
        return nodes

    def process_dom_node(self, node):
        nodes = []
        current = node.firstChild()
        while not current.isNull():
            if current.isElement():
                nodes.append(current)
                self.process_node(current)
            current = current.nextSibling()
        return nodes

    def extract_entities_data(self, xml_filename:str, profile_name: str,
                               entities: List[str] ) -> List[EntityNodeData]:
        """
        Get entities in the dom document matching user
        selected entities
        """
        entities_data = []

        dom_doc = self._make_dom_document(xml_filename)

        dom_nodes = dom_doc.elementsByTagName(profile_name)

        entity_nodes = dom_nodes.item(0).childNodes()   # Dom Nodes

        for i in range(entity_nodes.count()):

            if entity_nodes.item(i).nodeName() in entities:
                node_data = EntityNodeData()

                node_data.entity_name = entity_nodes.item(i).nodeName()

                dnodes = self.process_dom_node(entity_nodes.item(i))

                node_data.entity_nodes = dnodes  #dom_doc.elementsByTagName(node_data.entity_name)

                entities_data.append(node_data)

        return entities_data


    def instance_data_from_nodelist(self, entity_node_data: List[EntityNodeData], 
                                    fk_relations: dict) -> dict:
        """
        Process nodelist data before importing attribute data into db
        """
        instances = OrderedDict()

        for node_data in entity_node_data:
            entity_nodes = node_data.entity_nodes
            entity_name  = node_data.entity_name

            fields = OrderedDict()

            for entity_node in entity_nodes:
                fields[entity_node.nodeName()] = entity_node.toElement().text()

            parent_name = self.child_parent(entity_name, fk_relations)

            if not parent_name:
                instances[entity_name] = {'data': fields, 'children': []}
            else:
                child_data ={'child_name': entity_name, 'data': fields}
                instances[parent_name]['children'].append(child_data)

        return instances   #, repeated_instances

    def child_parent(self, child_name: str, fk_relations: dict) -> str:
        for parent_name, child_data in fk_relations.items():
            if child_name in child_data:
                return parent_name
        return None

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

    def str_definition(self, instance=None):
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
        return self.node.replace(":", "")

    def rename_file(self, xml_full_filepath: str, uuid: str) ->str:
        """
        Remane the existing instance file with Guuid from the mobile divice to conform with GeoODk naming
        convention
        :return:
        """
        dir_n, file_n = os.path.split(xml_full_filepath)

        if file_n.startswith('uuid'):
            #self.xml_files.append(xml_full_filepath)
            return xml_full_filepath

        old_filename = f'{dir_n}\{file_n}'
        new_filename =f'{dir_n}\{uuid}.xml'

        os.rename(old_filename, new_filename)

        return new_filename

        #self.xml_files.append(new_filename)



    def get_xml_files(self) -> List[str]:
        """
        Check through the list of document to ensure they are complete file path
        Returns a list of filenames
        """
        return self.xml_files

        complete_file = []
        for fi in self.xml_files:
            if os.path.isfile(fi):
                complete_file.append(fi)
        return complete_file

    def close_document(self):
        '''Close all the open documents and unset current paths'''
        self.file_path = None
        self.doc.clear()
        self.xml_files = None
