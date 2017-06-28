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

    def set_document(self):
        """

        :return:
        """
        self.file = QFile(self.file_path)
        if self.file.open(QIODevice.ReadOnly):
            self.doc.setContent(self.file)

    def on_file_passed(self):
        """
        Pass the row file to an xml document and format the name to GeoODK standards
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
        Get enities in the document
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
        else:
            return
