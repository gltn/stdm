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
from ..data.pg_utils import export_data, import_data

COLUMN_TYPE_DICT = {'character varying': 'VARCHAR', 'date': 'DATE',
                    'serial': 'SERIAL', 'integer': 'BIGINT', 'lookup':
                        'LOOKUP', 'double precision': 'DOUBLE', 'GEOMETRY':
                        'GEOMETRY'}
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
                                    "index": "False", "mandatory": "False"},
                        'GEOMETRY': {"unique": "False", "tip": "",
                                    "minimum": "0", "maximum":"92233720368547",
                                    "index": "False", "mandatory": "False"},
                        'DEFAULT': {"unique": "False", "tip": "",
                                    "minimum": "0", "maximum":"0",
                                    "index": "False", "mandatory": "False"},
                        }

IMPORT = "import"

from ..data.pg_utils import export_data


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
        self.table_col_name = None
        self.relations_dict = {}
        self.doc_old = QDomDocument()
        self.spatial_unit_table = []
        self.check_doc_relation_lookup_dict = {}
        self.config = StdmConfiguration.instance()
        self.old_config_file = False
        self.entities = []
        self.lookup_colum_name_values = {}

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

    def _get_doc_element(self, path):
        config_file = os.path.join(self.file_handler.localPath(), path)
        config_file = QFile(config_file)
        if not config_file.open(QIODevice.ReadOnly):
            raise IOError('Cannot read configuration file. Check read '
                          'permissions.')
        doc = QDomDocument()

        status, msg, line, col = doc.setContent(config_file)
        if not status:
            raise ConfigurationException(u'Configuration file cannot be '
                                         u'loaded: {0}'.format(msg))

        doc_element = doc.documentElement()

        return (doc, doc_element)

    def _check_config_version(self):
        doc, doc_element = self._get_doc_element("configuration.stc")

        config_version = doc_element.attribute('version')

        if config_version:
            config_version = float(config_version)
        else:

            # Fatal error
            raise ConfigurationException('Error extracting version '
                                         'number from the '
                                         'configuration file.')
        if self.config.VERSION == config_version:
            return True
        else:
            return False

    def _copy_config_file_from_template(self):

        shutil.copy(os.path.join(self.file_handler.defaultConfigPath(),
                                 "configuration.stc"),
                    self.file_handler.localPath())

    def _remove_old_config_file(self, config_file):
        os.remove(os.path.join(self.file_handler.localPath(),
                               config_file))

    def _set_lookup_data(self, lookup_name, element):

        lookup_dict = OrderedDict()
        # Used for import data conversion
        lookup_names = {}

        # Loop through lookups
        for i in range(element.count()):
            lookup_nodes = element.item(i).toElement()

            # Loop through lookup attributes
            if lookup_nodes.tagName() == "data":
                lookup_node = lookup_nodes.childNodes()

                count = 1
                for j in range(lookup_node.count()):
                    lookup = lookup_node.item(j).toElement().text()
                    code = lookup[0:2].upper()
                    lookup_dict[code] = lookup
                    lookup_names[lookup] = count
                    count += 1

        self.lookup_dict[lookup_name] = lookup_dict
        if lookup_name == "check_social_tenure_type":
            self.lookup_colum_name_values["type"] = lookup_names
        else:
            self.lookup_colum_name_values[lookup_name.lstrip("check_")] = \
            lookup_names

    def _set_table_columns(self, table_name, element):
        relations_list = []

        # Index to access table in self.table_list List
        table_index = 0

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

            if columns_node.tagName() == "geometryz":
                self.spatial_unit_table.append(table_name)
                column_dict = OrderedDict()
                column_dict["col_name"] = 'geom'
                column_dict["col_search"] = 'no'
                column_dict["col_descrpt"] = ''
                column_dict["col_type"] = 'GEOMETRY'
                column_dict["lookup"] = None
                column_dict["srid"] = '4326'
                column_dict["type"] = '0'

                self.table_list.append(column_dict)

                self.table_dict[table_name] = self.table_list


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
                self.entities.append(table_name)

            if profile_child_node.tagName() == "lookup":
                lookup_name = unicode(profile_child_node.attribute('name'))
                lookup_nodes = profile_child_node.childNodes()
                self._set_lookup_data(lookup_name, lookup_nodes)

        # Adding new lookups for documents and participating strs
        for k, v in self.relations_dict.iteritems():
            if k == "social_tenure_relationship":
                for relation in v:
                    lookup = "check_{0}_document_type".format(relation)
                    lookup_code = {"G": "General"}
                    self.lookup_dict[lookup] =\
                        lookup_code
                    self.check_doc_relation_lookup_dict[relation] = lookup

    def _set_version_profile(self, element):
        """
        Internal function to load version and profile to dictionary
        """
        for i in range(element.count()):
            # Reset values for different profiles
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

        if not self.config_file.open(QIODevice.ReadWrite | QIODevice.Truncate |
                                     QIODevice.Text):
            QMessageBox.warning(None, "Config Error", "Cannot write file {"
                                "0}: \n {2}".format(
                                 self.config_file.fileName(),
                                 self.config_file.errorString()))
        return


    def _create_entity_valuelist_relation_nodes(self, pref, profile, values):

        # Entity relation lookup dict
        entity_relation_dict = {}

        for key, value in values.iteritems():
            if key.endswith("lookup") and value:
                value_lists = self.doc_old.createElement("ValueLists")
                for lookup_key, lookup_value in value.iteritems():
                    value_list = self.doc_old.createElement("ValueList")
                    if lookup_key == "check_social_tenure_type":
                        lookup_key = "check_tenure_type"
                    value_list.setAttribute("name", lookup_key)

                    for k, v in lookup_value.iteritems():
                        code_value = self.doc_old.createElement("CodeValue")
                        code_value.setAttribute("code", k)
                        code_value.setAttribute("value", v)
                        value_list.appendChild(code_value)

                    value_lists.appendChild(value_list)

                # Default value list for check_social_tenure_relationship_
                # document_type
                value_list = self.doc_old.createElement("ValueList")
                value_list.setAttribute("name", "check_social_tenure_"
                                                "relationship_document_type")
                code_value = self.doc_old.createElement("CodeValue")
                code_value.setAttribute("code", "G")
                code_value.setAttribute("value", "General")
                value_list.appendChild(code_value)
                value_lists.appendChild(value_list)
                profile.appendChild(value_lists)

            if key.endswith("table") and value:
                for entity_key, entity_value in value.iteritems():
                    if entity_key not in ('supporting_document',
                                             'social_tenure_relationship',
                                             'str_relations'):
                        entity_name = pref + "_" + entity_key
                        entities = self.doc_old.createElement("Entity")
                        entities.setAttribute("name", entity_name)
                        entities.setAttribute("description", entity_value[0])
                        entities.setAttribute("shortName", entity_key)
                        entities.setAttribute("editable", "True")
                        entities.setAttribute("global", "False")
                        entities.setAttribute("associative", "False")
                        entities.setAttribute("proxy", "False")
                        entities.setAttribute("createId", "True")

                        # Adds supporting document check
                        for k, v in self.check_doc_relation_lookup_dict.\
                                iteritems():
                            if k == entity_key:
                                entities.setAttribute("documentTypeLookup", v)
                                entities.setAttribute("supportsDocuments",
                                                      "True")
                                break
                            else:
                                entities.setAttribute("supportsDocuments",
                                                      "False")
                                pass

                        column_properties = entity_value[2:]
                        columns = self.doc_old.createElement("Columns")
                        for i in column_properties:
                            column = self.doc_old.createElement("Column")
                            for col_k, col_v in i.iteritems():
                                if col_k == "col_name":
                                    column.setAttribute("name", col_v)
                                    self.table_col_name = col_v
                                elif col_k == "col_descrpt":
                                    column.setAttribute("description", col_v)
                                elif col_k == "col_type":
                                    column.setAttribute("TYPE_INFO", col_v)
                                    if COLUMN_PROPERTY_DICT[col_v]:
                                        for k, v in COLUMN_PROPERTY_DICT[col_v].\
                                                iteritems():
                                            column.setAttribute(k, v)
                                    else:
                                        for k, v in COLUMN_PROPERTY_DICT[
                                            'DEFAULT'].\
                                                iteritems():
                                            column.setAttribute(k, v)

                                elif col_k == "lookup" and col_v is not None:
                                    relation = self.doc_old.createElement(
                                        "Relation")
                                    attribute = "fk_{0}_{1}_id_{2}_{3}".format(
                                        pref, col_v, entity_name, unicode(
                                            self.table_col_name))
                                    relation.setAttribute("name", attribute)
                                    column.appendChild(relation)
                                    entity_relation_dict[attribute] = [col_v,
                                                                   entity_key,
                                                                   unicode(
                                                    self.table_col_name)]
                                if col_v == "GEOMETRY":
                                    geometry =  self.doc_old.createElement(
                                        "Geometry")
                                    geometry.setAttribute("type", '0')
                                    geometry.setAttribute("srid", '4326')
                                    geometry.setAttribute("layerDisplay", '')
                                    column.appendChild(geometry)
                                columns.appendChild(column)
                        entities.appendChild(columns)
                        profile.appendChild(entities)

            if key.endswith("relations"):
                relationship = self.doc_old.createElement("Relations")

                for relation_key, relation_values in value.iteritems():

                    if relation_key == "social_tenure_relationship":

                        for relation_v in relation_values:
                            entity_relation = self.doc_old.createElement(
                                    "EntityRelation")
                            entity_relation.setAttribute("parent", relation_v)
                            entity_relation.setAttribute("child",
                                                "social_tenure_relationship")
                            entity_relation.setAttribute("parentColumn", "id")
                            entity_relation.setAttribute("childColumn",
                                                             relation_v +
                                                         "_id")
                            entity_relation.setAttribute(
                                "name", "fk_{0}_{1}_id_{"
                                        "2}_social_tenure_relationship_{"
                                        "3}_id".format(pref, relation_v,
                                                        pref, relation_v))
                            relationship.appendChild(entity_relation)

                            entity_relation = self.doc_old.createElement(
                                    "EntityRelation")
                            entity_relation.setAttribute(
                                    "parent", "check_" +
                                              relation_v +
                                    "_document_type")
                            entity_relation.setAttribute(
                                    "child", relation_v +
                                    "_supporting_document")
                            entity_relation.setAttribute(
                                    "parentColumn", "id")
                            entity_relation.setAttribute(
                                    "childColumn", "document_type")
                            entity_relation.setAttribute(
                                    "name", "fk_" + pref +
                                    "_check_" + relation_v +
                                            "_document_type_id_"
                                    + pref +
                                    "_" + relation_v +
                                    "_supporting_document_document_type")

                            relationship.appendChild(entity_relation)

                            entity_relation = self.doc_old.createElement(
                                    "EntityRelation")
                            entity_relation.setAttribute(
                                    "parent", relation_v)
                            entity_relation.setAttribute(
                                    "child", relation_v +
                                    "_supporting_document")
                            entity_relation.setAttribute(
                                    "parentColumn", "id")
                            entity_relation.setAttribute(
                                    "childColumn", relation_v + "_id")
                            entity_relation.setAttribute(
                                    "name", "fk_" + pref +
                                    "_check_" + relation_v +
                                            "_id_"
                                    + pref +
                                    "_" + relation_v +
                                    "_supporting_document_" + relation_v + "_id")

                            relationship.appendChild(entity_relation)

                            entity_relation = self.doc_old.createElement(
                                    "EntityRelation")
                            entity_relation.setAttribute(
                                    "parent",  "supporting_document")
                            entity_relation.setAttribute(
                                    "child", relation_v +
                                    "_supporting_document")
                            entity_relation.setAttribute(
                                    "parentColumn", "id")
                            entity_relation.setAttribute(
                                    "childColumn", "supporting_doc_id")
                            entity_relation.setAttribute(
                                    "name", "fk_" + pref +
                                    "_supporting_document_id_" + pref +
                                    "_" + relation_v +
                                    "_supporting_document_supporting_doc_id")

                            relationship.appendChild(entity_relation)

                # Default relations
                entity_relation = self.doc_old.createElement("EntityRelation")
                entity_relation.setAttribute("parent",
                                                     "check_social_tenure_"
                                                     "relationship_document_type")
                entity_relation.setAttribute("child",
                                                     "social_tenure_relationship_"
                                                     "supporting_document")
                entity_relation.setAttribute("parentColumn", "id")
                entity_relation.setAttribute("childColumn",
                                                     "document_type")
                entity_relation.setAttribute("name",
                                                 "fk_" + pref +
                                                 "_check_social_tenure_"
                                                 "relationship_document_type_id_"
                                                 + pref + "_social_tenure_"
                                                "relationship_supporting_document_"
                                                "document_type")

                relationship.appendChild(entity_relation)

                entity_relation = self.doc_old.createElement("EntityRelation")
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

                entity_relation = self.doc_old.createElement("EntityRelation")
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

                entity_relation = self.doc_old.createElement("EntityRelation")
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

                # Adding relation that exists within column to Entity
                # relation nodes
                if entity_relation_dict:
                    for k, v in entity_relation_dict.iteritems():
                        entity_relation = self.doc_old.createElement(
                                "EntityRelation")
                        entity_relation.setAttribute("parent", v[0])
                        entity_relation.setAttribute("child", v[1])
                        entity_relation.setAttribute("name", k)
                        entity_relation.setAttribute("parentColumn", "id")
                        entity_relation.setAttribute("childColumn", v[2])
                        relationship.appendChild(entity_relation)

                profile.appendChild(relationship)

                social_tenure = self.doc_old.createElement("SocialTenure")
                social_tenure.setAttribute(
                    "layerDisplay", pref + "_vw_social_tenure_relationship")
                social_tenure.setAttribute(
                    "tenureTypeList", "check_tenure_type")
                social_tenure.setAttribute(
                    "spatialUnit", self.spatial_unit_table[0])
                for relation_key, relation_values in value.iteritems():

                    if relation_key == "social_tenure_relationship":

                        for relation_v in relation_values:
                            if self.spatial_unit_table[0] == relation_v:
                                pass

                            if self.spatial_unit_table[0] != relation_v:
                                social_tenure.setAttribute(
                                    "party", relation_v)

                profile.appendChild(social_tenure)

        return profile


    def _create_profile_valuelists_entity_nodes(self, dict, config):

        for config_profile, values in dict.iteritems():

            # Empty list to hold values to confirm if profile is empty
            empty_list = []

            # Test if a profile content is empty
            for k, v in values.iteritems():
                if not v:
                    break
                else:
                    empty_list.append(k)

            if empty_list:
                conf_prefix = config_profile[:2]
                self.config_profiles.append(conf_prefix)
                profile = self.doc_old.createElement("Profile")
                profile.setAttribute("description", "")
                profile.setAttribute("name", config_profile)
                profile = self._create_entity_valuelist_relation_nodes(
                conf_prefix, profile, values)
                config.appendChild(profile)

        return config

    def _populate_config_from_old_config(self):
        configuration = self.doc_old.createElement("Configuration")
        configuration.setAttribute("version", self.version)
        self.doc_old.appendChild(configuration)

        # Create profile valuelists and entity nodes
        config = self._create_profile_valuelists_entity_nodes(
                    self.entities_lookup_relations, configuration)

        # configuration.appendChild(config)

        self.doc_old.appendChild(config)

        stream = QTextStream(self.config_file)
        stream << self.doc_old.toString()
        self.config_file.close()
        self.doc_old.clear()

        # Delete the old configuration file after parsing it
        if self._check_config_file_exists("stdmConfig.xml"):
            self._remove_old_config_file("stdmConfig.xml")

    def load(self):

        if self._check_config_folder_exists():

            # Check if old configuration file exists
            if self._check_config_file_exists("stdmConfig.xml"):
                self.old_config_file = True
                doc, root = self._get_doc_element(os.path.join(
                    self.file_handler.localPath(), "stdmConfig.xml"))
                child_nodes = root.childNodes()

                # Parse old configuration to dictionary
                self._set_version_profile(child_nodes)

                # Create config file
                self._create_config_file("configuration.stc")

                # Create configuration node and version
                self._populate_config_from_old_config()

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

    def update_config_file_version(self):
        if self.old_config_file:
            self.version = unicode(self.config.VERSION)
            self._create_config_file("configuration.stc")
            self._populate_config_from_old_config()
        else:
            doc, root = self._get_doc_element(os.path.join(
                self.file_handler.localPath(), "configuration.stc"))

            if not root.isNull() and root.hasAttribute('version'):
                self._create_config_file("configuration.stc")
                if float(root.attribute('version')) < self.config.VERSION:
                    root.setAttribute('version', '1.2')
                    stream = QTextStream(self.config_file)
                    stream << doc.toString()
                    self.config_file.close()
                    doc.clear()

    def _add_missing_lookup_config(self, lookup, missing_lookup):
        if self.old_config_file:
            self.version = unicode(self.config.VERSION)
            self._create_config_file("configuration.stc")
            self._populate_config_from_old_config()

            doc, root = self._get_doc_element(os.path.join(
                self.file_handler.localPath(), "configuration.stc"))
            child_nodes = root.childNodes()
            for i in range(child_nodes.count()):
                child_node = child_nodes.item(i).toElement()

                if child_node.tagName() == "Profile":
                    profile_child_nodes = child_node.childNodes()

                    for i in range(profile_child_nodes.count()):
                        profile_nodes = profile_child_nodes.item(i).toElement()
                        if profile_nodes.tagName() == "ValueLists":
                            value_list_nodes = profile_nodes.childNodes()

                            for i in range(value_list_nodes.count()):
                                value_list_node = value_list_nodes.item(
                                    i).toElement()
                                if value_list_node.tagName() == "ValueList":
                                    lookup_name = unicode(
                                        value_list_node.attribute(
                                        'name'))

                                    if lookup_name == lookup:
                                        code_value = doc.createElement(
                                            "CodeValue")
                                        code_value.setAttribute("value",
                                                                missing_lookup)

                                        code = missing_lookup

                                        if code == 0:
                                            code_value.setAttribute("code", "")
                                        else:
                                            code_value.setAttribute("code",
                                                                    missing_lookup[0:2].upper())
                                        value_list_node.appendChild(code_value)

            stream = QTextStream(self.config_file)
            stream << doc.toString()
            self.config_file.close()
            doc.clear()

    def _match_lookup(self, values, lookup_data, lookup_col_index,
                      num_lookups, check_up):

        # First run to elimiate existing lookups
        for value in values:
            for lookup_value, code in \
                    lookup_data.iteritems():
                if str(lookup_value) == value[lookup_col_index]:
                    value[lookup_col_index] = int(code)
                    break

        # Second run to add missing lookups
        for value in values:
            for lookup_value, code in \
                    lookup_data.items():
                if str(lookup_value) == value[lookup_col_index]:
                    value[lookup_col_index] = int(code)
                    break
                else:
                    missing_lookup = value[lookup_col_index]
                    if missing_lookup is None:
                        value[lookup_col_index] = 0
                    else:
                        if isinstance(missing_lookup, int):
                            pass
                        else:
                            num_lookups += 1
                            QMessageBox.information(None, "Lookupdata",
                                                            str(lookup_data))
                            # self._add_missing_lookup_config("check_{0}".format(check_up), missing_lookup)

                            # Add missing lookup to lookup data
                            lookup_data[missing_lookup] = num_lookups

                            # Add converted lookup integer to row
                            value[lookup_col_index] = num_lookups


        return values

    def _set_social_tenure_table(self):
        for k, v in self.entities_lookup_relations.iteritems():
            for keys, values in v.iteritems():
                if keys.endswith("relations") and values:
                    for relation_key, values in values.iteritems():
                        if relation_key == "social_tenure_relationship":
                            return keys, values


    def backup_data(self):
        if self.old_config_file:
            keys, values = self._set_social_tenure_table()
            for social_tenure_entity in values:
                social_tenure_table = self.config_profiles[0] + "_" + \
                                        social_tenure_entity
                data = export_data(social_tenure_entity)

                columns = data.keys()

                # Remove geom columns of line, point and
                # polygon and replace with on column geom
                original_key_len = len(columns)
                new_keys = []
                for ky in keys:
                    if not ky.startswith("geom"):
                        new_keys.append(ky)
                if len(new_keys) is not original_key_len:
                    new_keys.append('geom')

                values = data.fetchall()

                values = [list(i) for i in values]

                # Only get geom columns with values and
                # avoid none geom tables
                new_values = []

                # Converts Var Char lookup to foreign key and add to config
                # file if it dosen't exist
                for check_up, lookup_data in \
                        self.lookup_colum_name_values.iteritems():
                    if check_up in columns:
                        if check_up == "type":
                            lookup_col_index = columns.index(check_up)
                            check_up = "tenure_{0}".format(check_up)
                            num_lookups = len(lookup_data)
                            values = self._match_lookup(values,
                                                        lookup_data,
                                                        lookup_col_index,
                                                        num_lookups,
                                                        check_up)
                        else:
                            lookup_col_index = columns.index(check_up)
                            num_lookups = len(lookup_data)
                            values = self._match_lookup(values,
                                                        lookup_data,
                                                        lookup_col_index,
                                                        num_lookups,
                                                        check_up)

                QMessageBox.information(None, "T", str(values))
                #
                #
                #
                #
                # if len(new_keys) is not original_key_len:
                #     for value in values:
                #         first_v = value[:-3]
                #         last_v = value[-3:]
                #         new_last_v = []
                #
                #         for last in last_v:
                #             if last is not None:
                #                 new_last_v.append(last)
                #
                #         l = tuple(list(first_v) + \
                #                    new_last_v)
                #
                #         new_values.append(l)
                #     new_values = str(new_values).strip(
                #         "[]")
                # else:
                #     new_values = str(values).strip("[]")
                #
                # # Remove Unicode
                # values = new_values.replace("u\'", "\'")
                #
                # keys = ",".join(new_keys)


                # import_data(social_tenure_table, keys,
                #             values)