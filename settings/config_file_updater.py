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
import datetime
import time

from collections import OrderedDict

from PyQt4.QtCore import QFile, QIODevice, Qt, QTextStream
from PyQt4.QtGui import QMessageBox, QProgressBar
from PyQt4.QtXml import QDomDocument

from ..data.configuration.exception import ConfigurationException
from ..data.configfile_paths import FilePaths
from ..data.configuration.stdm_configuration import StdmConfiguration
from ..data.pg_utils import export_data, import_data, pg_table_exists

COLUMN_TYPE_DICT = {'character varying': 'VARCHAR', 'date': 'DATE',
                    'serial': 'SERIAL', 'integer': 'INT', 'lookup':
                        'LOOKUP', 'double precision': 'DOUBLE', 'GEOMETRY':
                        'GEOMETRY', 'FOREIGN_KEY': 'FOREIGN_KEY'}
COLUMN_PROPERTY_DICT = {'SERIAL': {"unique": "False", "tip": "",
                                    "minimum": "-9223372036854775808",
                                    "maximum": "9223372036854775807",
                                    "index": "False", "mandatory": "False"},
                        'VARCHAR': {"unique": "False", "tip": "",
                                    "minimum": "0", "maximum": "30",
                                    "index": "False", "mandatory": "False"},
                        'INT': {"unique": "False", "tip": "",
                                    "minimum": "-9223372036854775806",
                                    "maximum":
                                    "9223372036854775807",
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
                        'FOREIGN_KEY': {"unique": "False", "tip": "",
                                    "minimum": "0", "maximum":"2147483647",
                                    "index": "False", "mandatory": "False"},
                        }
GEOMETRY_TYPES = {'LINESTRING': '1', 'POINT': '0', 'POLYGON': '2'}

IMPORT = "import"

from ..data.pg_utils import export_data


class ConfigurationFileUpdater(object):
    """
    Updates configuration file to new format and migrates data
    """

    def __init__(self, iface):
        self.iface = iface
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
        self.exclusions = ('supporting_document', 'social_tenure_relationship',
                           'str_relations')
        self.parent = None

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

    def _rename_old_config_file(self, old_config_file, path):
        old_file_wt_ext = "stdmConfig.xml".rstrip(".xml")
        dt = str(datetime.datetime.now())
        timestamp = time.strftime('%H%M%Y%m%d')
        new_file = os.path.join(path, "{0}_{1}.xml".format(old_file_wt_ext,
                                                      timestamp))
        os.rename(old_config_file, new_file)

    def _remove_old_config_file(self, config_file):
        os.remove(os.path.join(self.file_handler.localPath(),
                               config_file))

    def _set_lookup_data(self, lookup_name, element):

        lookup_dict = OrderedDict()
        # Used for import data conversion
        lookup_names = OrderedDict()

        # Loop through lookups
        for i in range(element.count()):
            lookup_nodes = element.item(i).toElement()

            # Loop through lookup attributes
            if lookup_nodes.tagName() == "data":
                lookup_node = lookup_nodes.childNodes()

                count = 1
                for j in range(lookup_node.count()):
                    lookup = lookup_node.item(j).toElement().text()
                    code = lookup[0:3].upper()
                    lookup_dict[code] = lookup
                    lookup_names[lookup] = count
                    count += 1

        # TODO remove this might rename the wrong column
        self.lookup_dict[lookup_name] = lookup_dict
        if lookup_name == "check_social_tenure_type":
            self.lookup_colum_name_values["tenure_type"] = lookup_names
        else:
            self.lookup_colum_name_values[lookup_name.lstrip("check_")] = \
            lookup_names

    def _set_table_columns(self, table_name, element):
        relations_list = []
        # relation_dict = {}

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
                    column_dict["parent"] = None
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

                nodes = relations_nodes.count()

                if nodes > 0:
                    for r in range(relations_nodes.count()):
                        relation_tables_list = []
                        relation_node = relations_nodes.item(r).toElement()
                        parent = unicode(relation_node.attribute(
                            'table'))
                        parent_column = unicode(relation_node.attribute(
                            'column'))
                        child_col = unicode(relation_node.attribute('fk'))
                        display_name = unicode(relation_node.attribute(
                            'display_name'))
                        relation_tables_list.append(parent)
                        relation_tables_list.append(parent_column)
                        relation_tables_list.append(child_col)
                        relation_tables_list.append(display_name)
                        # relation_dict['parent'] = relation_table
                        # relation_dict['display'] = display_name

                        # Adding column property for table
                        if table_name not in self.exclusions:
                            list_loc = r + nodes * -1
                            relation_table_name = unicode(
                                relation_node.attribute('table'))
                            relation_table_column = unicode(
                                relation_node.attribute('fk'))
                            self.table_list[list_loc]["parent"] = \
                                parent
                            self.table_list[list_loc]["col_type"] = \
                                'FOREIGN_KEY'
                            self.table_list[list_loc]["col_name"] = \
                                child_col
                            self.table_list[list_loc]["parent_id"] = \
                                parent_column
                            # self.table_list.append(column_dict)
                        relations_list.append(relation_tables_list)
                    self.relations_dict[table_name] = relations_list
                    # self.relations_dict[table_name] = relation_dict\

            if columns_node.tagName() == "geometryz":
                geometry_nodes = columns_node.childNodes()

                self.spatial_unit_table.append(table_name)

                for g in range(geometry_nodes.count()):
                    geometry_node = geometry_nodes.item(g).toElement()

                    column_dict = OrderedDict()
                    geom_dict = OrderedDict()
                    column_dict["col_name"] = unicode(
                            geometry_node.attribute('column'))
                    column_dict["col_search"] = 'no'
                    column_dict["col_descrpt"] = ''
                    column_dict["lookup"] = None
                    geom_dict["srid"] = unicode(
                                            geometry_node.attribute('srid'))
                    geom_dict["type"] = GEOMETRY_TYPES[unicode(
                                            geometry_node.attribute('type'))]
                    column_dict["col_type"] = geom_dict

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
                for relation in v[0]:
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
                profile = unicode(child_node.attribute('name')).\
                    replace(" ", "_")
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


    def _create_entity_valuelist_relation_nodes(self, pref, profile,
                                                profile_element, values):

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
                profile_element.appendChild(value_lists)

            if key.endswith("table") and value:
                for entity_key, entity_value in value.iteritems():
                    if entity_key not in self.exclusions:
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
                                    if isinstance(col_v, dict):
                                        for k, v in COLUMN_PROPERTY_DICT[
                                            'GEOMETRY'].\
                                                    iteritems():
                                                column.setAttribute(k, v)
                                        column.setAttribute("TYPE_INFO",
                                                            "GEOMETRY")
                                        geometry = self.doc_old.createElement(
                                                    "Geometry")
                                        geometry.setAttribute(
                                            "layerDisplay", "")
                                        for k, v in col_v.iteritems():
                                            geometry.setAttribute(k, v)
                                        column.appendChild(geometry)
                                    else:
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
                                if col_k == 'parent':
                                    self.parent = col_v

                                if col_v == "FOREIGN_KEY":
                                    relation = self.doc_old.createElement(
                                        "Relation")
                                    relation.setAttribute("name",
                                                          "fk_{0}_{1}_id_{2}_"
                                                          "{3}_{4}".format(pref,
                                                                           self.parent,
                                                                           pref, entity_key,
                                                                           self.table_col_name))
                                    column.appendChild(relation)
                            columns.appendChild(column)
                        entities.appendChild(columns)
                        profile_element.appendChild(entities)

            if key.endswith("relations"):
                relationship = self.doc_old.createElement("Relations")

                for relation_key, relation_values in value.iteritems():

                    if relation_key not in self.exclusions:

                        for relation in relation_values:
                            entity_relation = self.doc_old.createElement(
                                    "EntityRelation")
                            entity_relation.setAttribute("parent",
                                                             relation[0])
                            entity_relation.setAttribute("childColumn",
                                                             relation[2])
                            entity_relation.setAttribute(
                                "name", "fk_{0}_{1}_{2}_{3}_{4}_{5}".format(
                                    pref, relation[0], relation[1], pref,
                                    relation_key, relation[2]))
                            entity_relation.setAttribute("displayColumn",
                                                             relation[3])
                            entity_relation.setAttribute("child",
                                                relation_key)
                            entity_relation.setAttribute("parentColumn",
                                                         relation[1])

                            relationship.appendChild(entity_relation)

                    if relation_key == "social_tenure_relationship":

                        for relation in relation_values:
                            entity_relation = self.doc_old.createElement(
                                    "EntityRelation")
                            entity_relation.setAttribute("parent", relation[0])
                            entity_relation.setAttribute("childColumn",
                                                         relation[2])
                            entity_relation.setAttribute(
                                    "name", "fk_{0}_{1}_{2}_{3}_{4}_{"
                                            "5}".format(
                                    pref, relation[0], relation[1],
                                    pref, relation_key, relation[2]))
                            entity_relation.setAttribute('displayColumn',
                                                             relation[3])
                            entity_relation.setAttribute("child",
                                                relation_key)
                            entity_relation.setAttribute("parentColumn",
                                                         relation[2])
                            relationship.appendChild(entity_relation)

                            entity_relation = self.doc_old.createElement(
                                    "EntityRelation")
                            entity_relation.setAttribute("parent", "check_" +
                                                  relation[0] +
                                                         "_document_type")
                            entity_relation.setAttribute("child", relation[0] +
                                        "_supporting_document")
                            entity_relation.setAttribute(
                                    "name", "fk_" + pref + "_check_" +
                                            relation[0] +
                                    "_document_type_id_" + pref + "_" +
                                            relation[0]
                                    + "_supporting_document_document_type")
                            entity_relation.setAttribute('displayColumn',
                                                             relation[3])
                            entity_relation.setAttribute("parentColumn", "id")
                            entity_relation.setAttribute(
                                    "childColumn", "document_type")
                            relationship.appendChild(entity_relation)

                            entity_relation = self.doc_old.createElement(
                                    "EntityRelation")
                            entity_relation.setAttribute("parent", relation[0])
                            entity_relation.setAttribute("child", relation[0] +
                                        "_supporting_document")
                            entity_relation.setAttribute("childColumn",
                                                             relation[2])
                            entity_relation.setAttribute("name", "fk_" + pref +
                                        "_check_" + relation[0] + "_"
                                        + relation[1] + "_" + pref +
                                        "_" + relation[0] +
                                        "_supporting_document_" + relation[2])
                            entity_relation.setAttribute('displayColumn',
                                                             relation[3])
                            entity_relation.setAttribute(
                                    "parentColumn", "id")
                            relationship.appendChild(entity_relation)

                            entity_relation = self.doc_old.createElement(
                                    "EntityRelation")
                            entity_relation.setAttribute(
                                        "parent",  "supporting_document")
                            entity_relation.setAttribute( "child", relation[
                                0] + "_supporting_document")
                            entity_relation.setAttribute(
                                    "name", "fk_" + pref +
                                    "_supporting_document_id_" + pref +
                                    "_" + relation[0] +
                                    "_supporting_document_supporting_doc_id")
                            entity_relation.setAttribute('displayColumn',
                                                             relation[3])
                            entity_relation.setAttribute("parentColumn", "id")
                            entity_relation.setAttribute(
                                    "childColumn", "supporting_doc_id")
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
                entity_relation.setAttribute("displayColumn", "")

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
                entity_relation.setAttribute("displayColumn", "")

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
                entity_relation.setAttribute("displayColumn", "")

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
                entity_relation.setAttribute("displayColumn", "")

                relationship.appendChild(entity_relation)

                # Adding relation that exists within column to Entity
                # relation nodes
                if entity_relation_dict:
                    for k, v in entity_relation_dict.iteritems():
                        entity_relation = self.doc_old.createElement(
                                "EntityRelation")
                        entity_relation.setAttribute("parent", v[0])
                        entity_relation.setAttribute("displayColumn", "")
                        entity_relation.setAttribute("child", v[1])
                        entity_relation.setAttribute("name", k)
                        entity_relation.setAttribute("parentColumn", "id")
                        entity_relation.setAttribute("childColumn", v[2])
                        relationship.appendChild(entity_relation)

                profile_element.appendChild(relationship)

                social_tenure = self.doc_old.createElement("SocialTenure")
                social_tenure.setAttribute(
                    "layerDisplay", profile + "_vw_social_tenure_relationship")
                social_tenure.setAttribute(
                    "tenureTypeList", "check_tenure_type")
                # social_tenure.setAttribute(
                #     "spatialUnit", self.spatial_unit_table[0])

                for relation_key, relation_values in value.iteritems():

                    if relation_key == "social_tenure_relationship":
                        new_relation = []
                        for relation in relation_values:
                            if relation_values:
                                new_relation = [relation_values[0][0],
                                                relation_values[1][0]]
                            if self.spatial_unit_table:
                                for sp_table in self.spatial_unit_table:
                                    if sp_table in new_relation:
                                        social_tenure.setAttribute(
                                                "spatialUnit", sp_table)

                                    if sp_table is not relation[0]:
                                        social_tenure.setAttribute(
                                            "party", relation[0])

                profile_element.appendChild(social_tenure)

        return profile_element


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
                # Check if config already exists
                if self.config.profile(config_profile) is not None:
                    config_profile += "_1"
                    conf_prefix = config_profile[:2].lower() + "_1"
                else:
                    config_profile = config_profile
                    conf_prefix = config_profile[:2].lower()
                self.config_profiles.append(conf_prefix)
                profile_element = self.doc_old.createElement("Profile")
                profile_element.setAttribute("description", "")
                profile_element.setAttribute("name", config_profile)
                profile_element = self._create_entity_valuelist_relation_nodes(
                conf_prefix, config_profile, profile_element, values)
                config.appendChild(profile_element)

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

        # Rename the old configuration file after parsing it
        if self._check_config_file_exists("stdmConfig.xml"):
            # self._remove_old_config_file("stdmConfig.xml")
            old_config_file = os.path.join(
                        self.file_handler.localPath(), "stdmConfig.xml")
            path = self.file_handler.localPath()
            self._rename_old_config_file(old_config_file, path)

    def load(self):

        if self._check_config_folder_exists():

            # Check if old configuration file exists
            if self._check_config_file_exists("stdmConfig.xml"):

                if QMessageBox.information(None, "Update STDM Configuration",
                                        "Do you want to backup your "
                                        "configuration file?",
                                            QMessageBox.Yes |
                                        QMessageBox.No) == QMessageBox.Yes:
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
                    old_config_file = os.path.join(
                        self.file_handler.localPath(), "stdmConfig.xml")
                    path = self.file_handler.localPath()
                    self._rename_old_config_file(old_config_file, path)
                    self._copy_config_file_from_template()
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
                                        code_values_lists = []
                                        code_value_nodes = \
                                                value_list_node.childNodes()
                                        for i in range(code_value_nodes.count()):
                                            code_value_node = \
                                                    code_value_nodes.item(i).toElement()
                                            code_value = unicode(
                                                code_value_node.attribute(
                                                'value'))
                                            code_values_lists.append(code_value)

                                        code_value = doc.createElement(
                                            "CodeValue")
                                        code_value.setAttribute("value",
                                                                missing_lookup)

                                        code = missing_lookup

                                        if code == 0:
                                            code_value.setAttribute("code", "")
                                        else:
                                            code_value.setAttribute(
                                                "code", missing_lookup[
                                                        0:3].upper())

                                        if missing_lookup not in \
                                                code_values_lists:

                                            value_list_node.appendChild(code_value)

            self._create_config_file("configuration.stc")
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
                        value[lookup_col_index] = None
                    else:
                        if isinstance(missing_lookup, int) or missing_lookup\
                                is None:
                            pass
                        else:
                            num_lookups += 1
                            self._add_missing_lookup_config(
                                "check_{0}".format(check_up),
                                missing_lookup)

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
            no_tables = len(values)
            progress_message_bar = self.iface.messageBar().createMessage(
                "Importing data...")
            progress = QProgressBar()
            progress.setMaximum(no_tables)
            progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
            progress_message_bar.layout().addWidget(progress)
            self.iface.messageBar().pushWidget(progress_message_bar,
                                           self.iface.messageBar().INFO)

            for social_tenure_entity in values:
                i = 0
                social_tenure_table = self.config_profiles[0] + "_" + \
                                        social_tenure_entity[0]

                if pg_table_exists(social_tenure_entity[0]):

                    data = export_data(social_tenure_entity[0])

                    columns = data.keys()

                    # Remove geom columns of line, point and
                    # polygon and replace with one column geom to fit new config
                    original_key_len = len(columns)
                    new_keys = []
                    for ky in data.keys():
                        if not ky.startswith("-"):
                            new_keys.append(ky)
                    if len(new_keys) is not original_key_len:
                        new_keys.append('geom')

                    values = data.fetchall()

                    # Checks if exported data is empty
                    if len(values) > 0:
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

                        if len(new_keys) is not original_key_len:
                            for value in values:
                                first_v = value[:-3]
                                last_v = value[-3:]
                                new_last_v = []

                                for last in last_v:
                                    if last is not None:
                                        new_last_v.append(last)

                                l = tuple(list(first_v) + \
                                           new_last_v)

                                new_values.append(l)
                            new_values = str(new_values).strip(
                                "[]")
                        else:
                            new_values = str(values).replace("[[", "(")
                            new_values = str(new_values).replace("]]", ")")
                            new_values = str(new_values).replace("[", "(")
                            new_values = str(new_values).replace("]", ")")
                            new_values = str(new_values).replace("None", "NULL")

                        # Remove Unicode
                        values = new_values.replace("u\'", "\'")

                        column_keys = ",".join(new_keys)

                        import_data(social_tenure_table, column_keys, values)

                    else:
                        pass

                else:
                    pass

                time.sleep(1)
                progress.setValue(i + 1)
                i += 1
            self.iface.messageBar().clearWidgets()