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

COLUMN_TYPE_DICT = {'character varying': 'VARCHAR', 'date': 'DATE',
                    'serial': 'SERIAL', 'integer': 'BIGINT', 'lookup':
                        'LOOKUP', 'double precision': 'DOUBLE'}
COLUMN_PROPERTY_DICT = {'SERIAL': {"unique": "False", "tip": "",
                                    "minimum": "-9223372036854775808",
                                    "maximum": "9223372036854775807",
                                    "index": "False", "mandatory": "False"},
                        'VARCHAR': {"unique": "False", "tip": "",
                                    "minimum": "0", "maximum": "30",
                                    "index": "False", "mandatory": "False"},
                        'BIGINT': {"unique": "False", "tip": "",
                                    "minimum": "0", "maximum": "100000000",
                                    "index": "False", "mandatory": "False"},
                        'DATE':   {"unique": "False", "tip": "",
                                    "minimum": "0", "maximum": "30",
                                    "index": "False", "mandatory": "False"},
                        'LOOKUP': {"unique": "False", "tip": "",
                                    "minimum": "0", "maximum": "30",
                                    "index": "False", "mandatory": "False"},
                        'DOUBLE': {"unique": "False", "tip": "",
                                    "minimum": "0", "maximum": "0",
                                    "index": "False", "mandatory": "False"}}


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
        self.lookup_dict = OrderedDict()
        self.config_file = None
        self.profile_dict = OrderedDict()
        self.profile_list = []
        self.entities_lookup_relations = OrderedDict()
        self.table_name = None
        self.relations_dict = {}
        self.doc = QDomDocument()

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

    def _set_lookup_data(self, lookup_name, element):

        lookup_dict = OrderedDict()

        for i in range(element.count()):
            lookup_nodes = element.item(i).toElement()

            if lookup_nodes.tagName() == "data":
                lookup_node = lookup_nodes.childNodes()

                for j in range(lookup_node.count()):
                    lookup = lookup_node.item(j).toElement().text()
                    code = lookup[0:2].upper()
                    lookup_dict[code] = lookup

            self.lookup_dict[lookup_name] = lookup_dict

    def _set_table_columns(self, table_name, element):
        relations_list = []

        for i in range(element.count()):
            columns_node = element.item(i).toElement()

            if columns_node.tagName() == "columns":
                column_nodes = columns_node.childNodes()

                for j in range(column_nodes.count()):
                    column_dict = OrderedDict()
                    column_node = column_nodes.item(j).toElement()
                    col_name = unicode(column_node.attribute('name'))
                    column_dict["col_name"] = col_name
                    col_search = unicode(column_node.attribute('searchable'))
                    column_dict["col_search"] = col_search
                    col_description = unicode(
                        column_node.attribute('fullname'))
                    column_dict["col_descrpt"] = col_description
                    xml_file_col_type = unicode(column_node.attribute('type'))
                    try:
                        stc_file_col_type = COLUMN_TYPE_DICT[xml_file_col_type]
                        column_dict["col_type"] = stc_file_col_type
                    except KeyError:
                        column_dict["col_type"] = xml_file_col_type
                    if len(unicode(column_node.attribute('lookup'))) != 0:
                        column_dict["lookup"] = unicode(
                            column_node.attribute('lookup'))
                        column_dict["col_type"] = COLUMN_TYPE_DICT['lookup']
                    else:
                        column_dict["lookup"] = None
                    self.table_list.append(column_dict)

            self.table_dict[table_name] = self.table_list

            if columns_node.tagName() == "relations":
                relations_nodes = columns_node.childNodes()

                for r in range(relations_nodes.count()):
                    relation_node = relations_nodes.item(r).toElement()
                    relation_table = unicode(relation_node.attribute('table'))
                    relations_list.append(relation_table)
                self.relations_dict[table_name] = relations_list

    def _set_table_attributes(self, element):

        for i in range(element.count()):
            self.table_list = []
            profile_child_node = element.item(i).toElement()

            if profile_child_node.tagName() == "table":
                table_name = unicode(profile_child_node.attribute('name'))
                table_descrpt = unicode(profile_child_node.attribute(
                                        'fullname'))
                self.table_list.append(table_descrpt)
                table_shortname = unicode(profile_child_node.attribute(
                                    'fullname'))
                self.table_list.append(table_shortname)
                columns_nodes = profile_child_node.childNodes()
                self._set_table_columns(table_name, columns_nodes)

            if profile_child_node.tagName() == "lookup":
                lookup_name = unicode(profile_child_node.attribute('name'))
                lookup_nodes = profile_child_node.childNodes()
                self._set_lookup_data(lookup_name, lookup_nodes)

    def _set_version_profile(self, element):
        """
        Internal function to load version and profile to dictionary
        """
        for i in range(element.count()):
            self.table_dict = OrderedDict()
            self.lookup_dict = OrderedDict()
            self.profile_dict = OrderedDict()
            self.relations_dict = {}
            child_node = element.item(i).toElement()

            if child_node.hasAttribute('version'):
                self.version = unicode(child_node.attribute('version'))

            if child_node.tagName() == "profile":
                profile = unicode(child_node.attribute('name')).lower()
                profile_child_nodes = child_node.childNodes()
                self._set_table_attributes(profile_child_nodes)
                self.profile_dict[profile + "_table"] = self.table_dict
                self.profile_dict[profile + "_lookup"] = self.lookup_dict
                self.profile_dict[profile + "_relations"] = self.relations_dict
                self.entities_lookup_relations[profile] = self.profile_dict

    def _create_config_file(self, config_file_name):

        self.config_file = QFile(os.path.join(self.file_handler.localPath(),
                                 config_file_name))

        if not self.config_file.open(QFile.WriteOnly | QFile.Text):
            QMessageBox.warning(None, "Config Error", "Cannot write file {"
                                "0}: \n {2}".format(
                                 self.config_file.fileName(),
                                 self.config_file.errorString()))
        return


    def _create_entity_valuelist_relation_nodes(self, pref, profile, values,
                                                value_lists):

        for key, value in values.iteritems():
            if key.endswith("lookup"):
                for lookup_key, lookup_value in value.iteritems():
                    value_list = self.doc.createElement("ValueList")
                    if lookup_key == "check_social_tenure_type":
                        lookup_key = "check_tenure_type"
                    value_list.setAttribute("name", lookup_key)

                    for k, v in lookup_value.iteritems():
                        code_value = self.doc.createElement("CodeValue")
                        code_value.setAttribute("code", k)
                        code_value.setAttribute("value", v)
                        value_list.appendChild(code_value)

                    value_lists.appendChild(value_list)

            profile.appendChild(value_lists)

            if key.endswith("table"):
                for entity_key, entity_value in value.iteritems():
                    entities = self.doc.createElement("Entity")
                    entities.setAttribute("name", pref + "_" + entity_key)
                    entity_name = pref + "_" + entity_key
                    entities.setAttribute("description", entity_value[0])
                    entities.setAttribute("shortName", entity_value[1])
                    entities.setAttribute("editable", "True")
                    entities.setAttribute("global", "False")
                    entities.setAttribute("associative", "False")
                    entities.setAttribute("proxy", "False")
                    entities.setAttribute("createId", "True")
                    entities.setAttribute("supportsDocuments", "False")
                    column_properties = entity_value[2:]
                    columns = self.doc.createElement("Columns")
                    for i in column_properties:
                        column = self.doc.createElement("Column")
                        for col_k, col_v in i.iteritems():
                            if col_k == "col_name":
                                column.setAttribute("name", col_v)
                                self.table_name = col_v
                            elif col_k == "col_descrpt":
                                column.setAttribute("description", col_v)
                            elif col_k == "col_type":
                                column.setAttribute("TYPE_INFO", col_v)
                                if COLUMN_PROPERTY_DICT[col_v]:
                                    for k, v in COLUMN_PROPERTY_DICT[col_v].\
                                            iteritems():
                                        column.setAttribute(k, v)

                            elif col_k == "lookup" and col_v is not None:
                                relation = self.doc.createElement("Relation")
                                relation.setAttribute("name", "fk_" + pref
                                                     + "_" + col_v + "_id_"
                                                     + entity_name + "_" +
                                                     str(self.table_name))
                                column.appendChild(relation)
                            columns.appendChild(column)
                    entities.appendChild(columns)
                    profile.appendChild(entities)

            if key.endswith("relations"):
                relationship = self.doc.createElement("Relations")

                for relation_key, relation_values in value.iteritems():

                    if relation_key == "social_tenure_relationship":

                        for relation_v in relation_values:
                            entity_relation = self.doc.createElement(
                                "EntityRelation")
                            entity_relation.setAttribute("parent", relation_v)
                            entity_relation.setAttribute("child",
                                            "social_tenure_relationship")
                            entity_relation.setAttribute("parentColumn", "id")
                            entity_relation.setAttribute("childColumn",
                                                         relation_v + "_" +
                                                         "id")
                            entity_relation.setAttribute(
                                "name", "fk_" + pref + "_" + relation_v +
                                "_" + pref + "_" + "social_tenure_relationship"
                                + "_" + relation_v + "_" + "id")
                            relationship.appendChild(entity_relation)

                if value:

                    entity_relation = self.doc.createElement("EntityRelation")
                    entity_relation.setAttribute("parent",
                                                 "social_tenure_relationship")
                    entity_relation.setAttribute("child",
                                                 "social_tenure_relationship_"
                                                 "supporting_document")
                    entity_relation.setAttribute("parentColumn", "id")
                    entity_relation.setAttribute("childColumn",
                                                 "social_tenure_relationship_"
                                                 "id")
                    entity_relation.setAttribute("name",
                                                 "fk_" + pref + "_social_"
                                                "tenure_relationship_id_"
                                                 + pref +
                                                 "_social_tenure_relationship_"
                                                 "supporting_document_social_"
                                                 "tenure_relationship_id")

                    relationship.appendChild(entity_relation)

                    entity_relation = self.doc.createElement("EntityRelation")
                    entity_relation.setAttribute("parent",
                                                 "supporting_document")
                    entity_relation.setAttribute("child",
                                                 "social_tenure_relationship_"
                                                 "supporting_document")
                    entity_relation.setAttribute("parentColumn", "id")
                    entity_relation.setAttribute("childColumn", pref +
                                                 "_supporting_doc_id")
                    entity_relation.setAttribute("name", "fk_" + pref +
                                                "_supporting_document_id_" +
                                                pref + "_social_tenure_"
                                                "relationship_supporting_"
                                                "document_" + pref +
                                                 "_supporting_doc_id")

                    relationship.appendChild(entity_relation)

                    entity_relation = self.doc.createElement("EntityRelation")
                    entity_relation.setAttribute("parent",
                                                 "check_tenure_type")
                    entity_relation.setAttribute("child",
                                                 "social_tenure_relationship")
                    entity_relation.setAttribute("parentColumn", "id")
                    entity_relation.setAttribute("childColumn", "tenure_type")
                    entity_relation.setAttribute("name", "fk_" + pref +
                                                 "_check_tenure_type_id_" +
                                                 pref + "_social_tenure_"
                                                 "relationship_tenure_type")

                    relationship.appendChild(entity_relation)

                profile.appendChild(relationship)

        return profile


    def _create_profile_valuelists_entity_nodes(self, dict, config):

        for config_profile, values in dict.iteritems():
            conf_prefix = config_profile[:2]
            profile = self.doc.createElement("Profile")
            profile.setAttribute("description", "")
            profile.setAttribute("name", config_profile)
            value_lists = self.doc.createElement("ValueLists")

            profile = self._create_entity_valuelist_relation_nodes(conf_prefix,
                                                         profile, values,
                                                         value_lists)
            config.appendChild(profile)

        return config

    def _populate_config_file(self):
        configuration = self.doc.createElement("Configuration")
        configuration.setAttribute("version", self.version)
        self.doc.appendChild(configuration)

        # Create profile valuelists and entity nodes
        config = self._create_profile_valuelists_entity_nodes(
                    self.entities_lookup_relations, configuration)

        # configuration.appendChild(config)

        self.doc.appendChild(config)

        stream = QTextStream(self.config_file)
        stream << self.doc.toString()

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

                # Create configuration node and version
                self._populate_config_file()

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