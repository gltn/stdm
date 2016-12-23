import os

import datetime
from PyQt4.QtCore import QFile
from PyQt4.QtXml import QDomDocument
from stdm.data.configuration.exception import ConfigurationException

from stdm.data.configfile_paths import FilePaths


class UpdateUtils():
    def __init__(self, stc_file):

        self.file_handler = FilePaths()
        self.log_file_path = '{}/logs/migration.log'.format(
            self.file_handler.localPath()
        )
        self.read_stc(stc_file)

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

    def set_attribute(self, nodes, attr, value):
        for node in nodes:
            element = node.toElement()
            element.setAttribute(attr, value)
        #print self.document.toString()

    def set_attribute_to_node(self, node_name, attr, value):
        nodes = self.find_node(node_name)
        self.set_attribute(nodes, attr, value)

    def run(self):
        nodes = self.find_node('Entity')
        self.set_attribute(nodes, 'Wondie', 'Tesfaye')
