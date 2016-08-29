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
import cStringIO
from collections import OrderedDict

from distutils import file_util

import errno
from PyQt4.QtCore import QFile, QIODevice, Qt, QTextStream, pyqtSignal
from PyQt4.QtGui import QMessageBox, QProgressBar, QDialog, QVBoxLayout, QLabel, QApplication, \
    QCheckBox, QDialogButtonBox, QFileDialog, QLineEdit
from PyQt4.QtXml import QDomDocument

from ..data.configuration.config_updater import ConfigurationSchemaUpdater
from ..data.configuration.exception import ConfigurationException
from ..data.configfile_paths import FilePaths
from ..data.configuration.stdm_configuration import StdmConfiguration
from ..data.pg_utils import export_data, import_data, pg_table_exists, \
    export_data_from_columns, fix_sequence
from ..settings.registryconfig import (
    RegistryConfig,
    CONFIG_UPDATED,
    source_documents_path,
    last_document_path,
    composer_template_path,
    NETWORK_DOC_RESOURCE,
    COMPOSER_OUTPUT,
    COMPOSER_TEMPLATE
)

from stdm.ui.notification import NotificationBar, ERROR, INFORMATION
from stdm.utils.util import simple_dialog
from stdm.ui.change_log import ChangeLog
from stdm.ui.ui_upgrade_paths import Ui_UpgradePaths

COLUMN_TYPE_DICT = {'character varying': 'VARCHAR', 'date': 'DATE',
                    'serial': 'SERIAL', 'integer': 'INT', 'lookup':
                    'LOOKUP', 'double precision': 'DOUBLE', 'GEOMETRY':
                    'GEOMETRY', 'FOREIGN_KEY': 'FOREIGN_KEY', 'boolean': 'BOOL'
                    , 'text': 'TEXT'}
COLUMN_PROPERTY_DICT = {'SERIAL': {"unique": "False", "tip": "",
                                    "minimum": "-9223372036854775808",
                                    "maximum": "9223372036854775807",
                                    "index": "False", "mandatory": "False"},
                        'VARCHAR': {"unique": "False", "tip": "",
                                    "minimum": "0", "maximum": "30",
                                    "index": "False", "mandatory": "False",
                                    "searchable": "True"},
                        'INT': {"unique": "False", "tip": "",
                                "minimum": "-9223372036854775806",
                                "maximum": "9223372036854775807",
                                "index": "False", "mandatory": "False"},
                        'DATE':   {"unique": "False", "tip": "",
                                   "minimum": "0", "maximum": "30",
                                   "index": "False", "mandatory": "False",
                                   "searchable": "False"},
                        'LOOKUP': {"unique": "False", "tip": "",
                                   "minimum": "0", "maximum": "30",
                                   "index": "False", "mandatory": "False",
                                   "searchable": "True"},
                        'DOUBLE': {"unique": "False", "tip": "",
                                   "minimum": "0", "maximum": "0",
                                   "index": "False", "mandatory": "False"},
                        'GEOMETRY': {"unique": "False", "tip": "",
                                     "minimum": "0",
                                     "maximum": "92233720368547",
                                     "index": "False", "mandatory": "False"},
                        'DEFAULT': {"unique": "False", "tip": "",
                                    "minimum": "0", "maximum":"0",
                                    "index": "False", "mandatory": "False"},
                        'FOREIGN_KEY': {"unique": "False", "tip": "",
                                        "minimum": "0", "maximum":"2147483647",
                                        "index": "False", "mandatory":
                                            "False"},
                        'TEXT': {"unique": "False", "tip": "",
                                        "minimum": "0", "maximum":"100",
                                        "index": "False", "mandatory":
                                            "False"},
                        'BOOL': {"unique": "False", "tip": "",
                                        "minimum": "0", "maximum":"10",
                                        "index": "False", "mandatory":
                                            "False"},
                        }
GEOMETRY_TYPES = {'LINESTRING': '1', 'POINT': '0', 'POLYGON': '2'}

IMPORT = "import"

STR_TABLES = OrderedDict([
                ('social_tenure_relationship',
                    OrderedDict([
                        ('old', ('id',
                                 'social_tenure_type',
                                 'party',
                                 'spatial_unit')),
                        ('new', ('id',
                                 'tenure_type',
                                 'party_id',
                                 'spatial_unit_id'))
                                 ])
                ),
                ('supporting_document',
                    OrderedDict([
                        ('old', ('id',
                                 'document_id',
                                 'filename',
                                 'doc_size')),
                        ('new', ('id',
                                 'document_identifier',
                                 'filename',
                                 'document_size',
                                 'source_entity'
                                 ))
                                 ])
                 ),
                ('str_relations',
                    OrderedDict([
                        ('old', ('id',
                                 'social_tenure_id',
                                 'source_doc_id')),
                        ('new', ('id',
                                 'social_tenure_relationship_id',
                                 'supporting_doc_id',
                                 'document_type'
                                 ))
                                 ])
                 )
            ])

from ..data.pg_utils import export_data

class ConfigurationFileUpdater(QDialog, Ui_UpgradePaths):
    """
    Updates configuration file to new format and migrates data
    """
    upgradeCanceled = pyqtSignal()

    def __init__(self, iface):
        QDialog.__init__(self, iface.mainWindow())
        self.iface = iface
        self.setupUi(self)
        self.file_handler = FilePaths()
        self.version = '1.2'
        self.config_profiles = []
        self.config_profiles_prefix = []
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
        self.exclusions = ('supporting_document',
                           'social_tenure_relationship',
                           'str_relations'
                           )
        self.parent = None
        self.upgrade = False
        self.old_data_folder_path = None
        self.new_data_folder_path = None
        self.reg_config = RegistryConfig()
        self.profiles_detail = {}
        self.progress = None
        self.log_file_path = '{}/logs/migration.log'.format(
            self.file_handler.localPath()
        )

    def create_log_file(self, file_path):
        """
        Create a new log file if it doesn't exist.
        :param file_path: The full path of the file.
        :type file_path: String
        :return:
        :rtype:
        """

        file_name = os.path.basename(file_path)
        try:
            info_file = open(file_name, 'a')
            info_file.close()
        except Exception:
            pass

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
        if os.path.isfile(os.path.join(
                self.file_handler.localPath(),
                config_file)
        ):

            return True
        else:
            return False

    def _get_doc_element(self, config_file_name):
        """
        Reads provided config file
        :returns QDomDocument, QDomDocument.documentElement()
        :rtype tuple
        """
        config_file_path = os.path.join(
            self.file_handler.localPath(), config_file_name
        )
        config_file_path = QFile(config_file_path)
        config_file = os.path.basename(config_file_name)
        if self._check_config_file_exists(config_file):

            doc = QDomDocument()

            status, msg, line, col = doc.setContent(config_file_path)
            if not status:
                error_message = u'Configuration file cannot be '
                u'loaded: {0}'.format(msg)
                self.append_log(str(error_message))

                raise ConfigurationException(error_message)

            doc_element = doc.documentElement()

            return doc, doc_element

    def _check_config_version(self):
        """
        Checks configuration version
        :returns True or False
        :rtype boolean
        """
        doc, doc_element = self._get_doc_element("configuration_upgraded.stc")

        config_version = doc_element.attribute('version')

        if config_version:
            config_version = float(config_version)
        else:
            self.append_log('Error extracting version '
                            'number from the '
                            'configuration file.'
                            )
            # Fatal error
            raise ConfigurationException('Error extracting version '
                                         'number from the '
                                         'configuration file.')
        if self.config.VERSION == config_version:
            return True
        else:
            return False

    def _copy_config_file_from_template(self):
        """
        Copies configuration from template
        """
        config_path = os.path.join(
            self.file_handler.defaultConfigPath(),
            'configuration.stc'
        )

        if os.path.isfile(config_path):
            shutil.copy(
                config_path,
                self.file_handler.localPath()
            )

    def _rename_old_config_file(self, old_config_file, path):
        """
        Renames old configuration file
        """
        old_file_wt_ext = "stdmConfig.xml".rstrip(".xml")
        dt = unicode(datetime.datetime.now())
        timestamp = time.strftime('%Y_%m_%d_%H_%M')
        new_file = os.path.join(path, "{0}_{1}.xml".format(old_file_wt_ext,
                                                           timestamp))
        os.rename(old_config_file, new_file)

    def _rename_new_config_file(self, path):
        """
        Renames old configuration file
        """
        config_file = "configuration"
        dt = unicode(datetime.datetime.now())
        timestamp = time.strftime('%Y_%m_%d_%H_%M')
        new_file = '{}/{}_{}.stc'.format(
            self.file_handler.localPath(),
            config_file,
            timestamp
        )

        file_util.copy_file(path, new_file)


    def _remove_old_config_file(self, config_file):
        """
        Delete config file
        :param config_file:
        """
        os.remove(os.path.join(self.file_handler.localPath(),
                               config_file))

    def _mkdir_p(self, path):
        try:
            os.makedirs(path)
        except OSError as exc:  # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):

                pass
            else:
                raise

    def _set_lookup_data(self, lookup_name, element):

        """
        Set look up information and data into dictionaries
        :param lookup_name:
        :param element:
        """
        lookup_dict = OrderedDict()
        # Used for import data conversion
        lookup_names = OrderedDict()

        # Loop through lookups
        for i in range(element.count()):
            lookup_nodes = element.item(i).toElement()

            # Loop through lookup attributes
            if lookup_nodes.tagName() == "data":
                lookup_node = lookup_nodes.childNodes()

                fk = 1
                for j in range(lookup_node.count()):
                    lookup = lookup_node.item(j).toElement().text()
                    code = lookup[0:2].upper()
                    if code in lookup_dict.keys():
                        code = lookup[0:3].upper()
                    else:
                        pass
                    lookup_dict[code] = lookup
                    lookup_names[lookup] = fk
                    fk += 1

        # Renames check lookup so that it conforms to new lookup type
        self.lookup_dict[lookup_name] = lookup_dict
        if lookup_name == "check_social_tenure_type":
            self.lookup_colum_name_values["tenure_type"] = lookup_names
        else:
            self.lookup_colum_name_values[
                lookup_name.lstrip("check_")] = lookup_names

    def _set_table_columns(self, table_name, element):
        """
        Sets table information to dictionary
        :param table_name:
        :param element:
        """
        relations_list = []
        # relation_dict = {}

        # Index to access table in self.table_list List
        # table_index = 0

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
                        lookup_no_list = []
                        lookup_val = unicode(
                            column_node.attribute('lookup'))

                        # Check to add lookup into value list if it only
                        # exists as a column and not as a lookup
                        for k, v in self.lookup_dict.items():
                            if lookup_val == k:
                                lookup_no_list.append(k)
                        if len(lookup_no_list) < 1:
                            self.lookup_dict[lookup_val] = {"G": "General"}
                            self.lookup_colum_name_values[lookup_val.lstrip(
                                "check_")] = OrderedDict([(u'General', 1)])
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

            # Extracts geometryz node to dictionary
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

        """
        Set table attributes
        :param element:
        """
        self.progress.progress_message('Creating', 'configuration')
        for i in range(element.count()):
            profile_child_node = element.item(i).toElement()

            if profile_child_node.tagName() == "lookup":
                lookup_name = unicode(profile_child_node.attribute('name'))
                lookup_nodes = profile_child_node.childNodes()
                self._set_lookup_data(lookup_name, lookup_nodes)

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

        # Adding new lookups for documents and participating strs
        for k, v in self.relations_dict.iteritems():
            if k == "social_tenure_relationship":
                for relation in v:
                    lookup = "check_{0}_document_type".format(relation[0])
                    lookup_code = {"G": "General"}
                    self.lookup_dict[lookup] =\
                        lookup_code
                    self.check_doc_relation_lookup_dict[relation[0]] = lookup

    def _set_version_profile(self, element):
        """
        Internal function to load version and profile to dictionary
        :param element:
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

        """
        Method to create configuration file
        :param config_file_name:
        :return:
        """
        self.progress.progress_message('Creating STDM 1.2 configuration file', '')
        self.config_file = QFile(os.path.join(self.file_handler.localPath(),
                                 config_file_name))

        if not self.config_file.open(QIODevice.ReadWrite | QIODevice.Truncate |
                                     QIODevice.Text):
            title = QApplication.translate(
                'ConfigurationFileUpdater',
                'Configuration Upgrade Error'
            )
            message = QApplication.translate(
                'ConfigurationFileUpdater',
                'Cannot write file {0}: \n {2}'.format(
                    self.config_file.fileName(),
                    self.config_file.errorString()
                )
            )

            QMessageBox.warning(
                self.iface.mainWindow(), title, message
            )
        return

    def append_profile_to_config_file(
            self, source_config, destination_config
    ):
        """
        Appends a profile from a source configuration into
        the destination configuration file.
        :param source_config: The source config/ configuration_updated.stc
        :type source_config: String
        :param config_file_name: The destination config / configuration.stc
        :type config_file_name: String
        """
        stdm_path = self.file_handler.localPath()
        doc, root = self._get_doc_element(
            source_config
        )
        config_doc, config_root = self._get_doc_element(
            destination_config
        )
        config_file_path = os.path.join(
            stdm_path, destination_config
        )
        config_file = QFile(config_file_path)
        config_file.copy(os.path.join(
            stdm_path, 'configuration_pre_merged.stc')
        )
        open_file = config_file.open(
            QIODevice.ReadWrite |
            QIODevice.Truncate |
            QIODevice.Text
        )

        if open_file:
            # upgraded config from stdmConfig.xml
            child_nodes = root.childNodes()
            # existing config/ default config
            c_child_nodes = config_root.childNodes()
            # look through upgraded node
            for child_i in range(child_nodes.count()):
                child_node = child_nodes.item(child_i).toElement()
                if child_node.tagName() == "Profile":
                    # if duplicate profile exists, remove it first before
                    # adding a new one with the same name
                    for child_j in range(c_child_nodes.count()):
                        c_child_node = c_child_nodes.item(0).toElement()
                        if c_child_node.tagName() == "Profile":
                            # remove if the same profile name exists
                            if child_node.attribute('name') ==\
                                    c_child_node.attribute('name'):

                                config_root.removeChild(c_child_node)
                    # Insert at the top of the configuration
                    first_c_child_node = c_child_nodes.item(0).toElement()
                    config_root.insertBefore(
                        child_node, first_c_child_node
                    )

            stream = QTextStream(config_file)
            stream << config_doc.toString()
            config_file.close()

    def _set_sp_unit_part_tables(self, relation_values):
        """
        Method determines which relation is either spatial unit type or party
        :param relation_values:
        :return: OrderedDict
        """
        sp_party_dict = OrderedDict()
        new_relation = []
        if relation_values:
                new_relation = [relation_values[0][0], relation_values[1][0]]
        if self.spatial_unit_table:
            for sp_table in self.spatial_unit_table:
                if sp_table in new_relation:
                    sp_party_dict['spatial_unit_table'] = sp_table
                    new_relation.remove(sp_table)
                    sp_party_dict['party_table'] = new_relation[0]
        return sp_party_dict

    def _create_entity_valuelist_relation_nodes(self, pref, profile,
                                                profile_element, values):

        # Entity relation lookup dict
        """
        Method that create new entity column and valuelist from extracted
        values from old configuration file
        :param pref:
        :param profile:
        :param profile_element:
        :param values:
        :return: QDomDocument Element
        """
        entity_relation_dict = {}
        template_dict = {'supporting_document': pref + "_supporting_document",
                         'social_tenure_relationship':
                             pref + "_social_tenure_relationship",
                         'social_tenure_relations':
                             '{}_vw_social_tenure_relationship'.format(profile.lower()),
                         'str_relations': pref + "_social_tenure_relationship_"
                                                 "supporting_document"}
        self.profiles_detail[profile] = template_dict

        for key, value in values.iteritems():
            if key.endswith("lookup") and value:
                value_lists = self.doc_old.createElement("ValueLists")
                for lookup_key, lookup_value in value.iteritems():
                    value_list = self.doc_old.createElement("ValueList")

                    template_dict[lookup_key] = pref + "_" + lookup_key

                    if lookup_key == "check_social_tenure_type":
                        template_dict[lookup_key] = pref + "_check_tenure_type"
                        lookup_key = "check_tenure_type"

                    # Place holder for

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
                        template_dict[entity_key] = entity_name
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
                                            for k, v in COLUMN_PROPERTY_DICT[
                                                    col_v].iteritems():
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
                                    entity_relation_dict[attribute] = [
                                        col_v, entity_key, unicode(
                                                    self.table_col_name)]
                                if col_k == 'parent':
                                    self.parent = col_v

                                if col_v == "FOREIGN_KEY":
                                    relation = self.doc_old.createElement(
                                        "Relation")
                                    relation.setAttribute(
                                        "name", "fk_{0}_{1}_id_{2}_ {3}_{"
                                        "4}".format(pref, self.parent, pref,
                                                    entity_key,
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
                            entity_relation.setAttribute(
                                "parent", relation[0])
                            entity_relation.setAttribute(
                                "childColumn", relation[2])
                            entity_relation.setAttribute(
                                "name", "fk_{0}_{1}_{2}_{3}_{4}_{5}".format(
                                    pref, relation[0], relation[1], pref,
                                    relation_key, relation[2]))
                            entity_relation.setAttribute(
                                "displayColumn", relation[3])
                            entity_relation.setAttribute(
                                "child", relation_key)
                            entity_relation.setAttribute(
                                "parentColumn", relation[1])

                            relationship.appendChild(entity_relation)

                    if relation_key == "social_tenure_relationship":

                        sp_party_dict = self._set_sp_unit_part_tables(
                            relation_values)

                        for relation in relation_values:
                            ###################################################
                            entity_relation = self.doc_old.createElement(
                                    "EntityRelation")
                            entity_relation.setAttribute("parent", relation[0])
                            for k, v in sp_party_dict.iteritems():
                                if k == "spatial_unit_table" and v == \
                                        relation[0]:
                                    entity_relation.setAttribute(
                                        "childColumn", "spatial_unit_id")
                                    entity_relation.setAttribute(
                                        "name", "fk_{0}_{1}_{2}_{3}_{4}_{"
                                        "5}".format(pref, relation[0],
                                                    relation[1], pref,
                                                    relation_key,
                                                    "spatial_unit_id"))
                                if k == "party_table" and v == \
                                        relation[0]:
                                    entity_relation.setAttribute(
                                        "childColumn", "party_id")
                                    entity_relation.setAttribute(
                                        "name", "fk_{0}_{1}_{2}_{3}_{4}_{"
                                        "5}".format(pref, relation[0],
                                                    relation[1], pref,
                                                    relation_key, "party_id"))
                            entity_relation.setAttribute(
                                'displayColumns', relation[3])
                            entity_relation.setAttribute(
                                "child", relation_key)
                            entity_relation.setAttribute(
                                "parentColumn", relation[1])
                            relationship.appendChild(entity_relation)

                            ##################################################
                            entity_relation = self.doc_old.createElement(
                                    "EntityRelation")
                            entity_relation.setAttribute(
                                "parent", "check_" + relation[0] +
                                          "_document_type")
                            entity_relation.setAttribute(
                                "child", relation[0] + "_supporting_document")
                            entity_relation.setAttribute(
                                    "name", "fk_" + pref + "_check_" +
                                            relation[0] +
                                    "_document_type_id_" + pref + "_" +
                                            relation[0]
                                    + "_supporting_document_document_type")
                            entity_relation.setAttribute(
                                'displayColumns', relation[3])
                            entity_relation.setAttribute(
                                "parentColumn", "id")
                            entity_relation.setAttribute(
                                    "childColumn", "document_type")
                            relationship.appendChild(entity_relation)

                            ##################################################
                            entity_relation = self.doc_old.createElement(
                                    "EntityRelation")
                            entity_relation.setAttribute(
                                "parent", relation[0])
                            entity_relation.setAttribute(
                                "child", relation[0] + "_supporting_document")
                            for k, v in sp_party_dict.iteritems():
                                if k == "spatial_unit_table" and v == \
                                        relation[0]:
                                    entity_relation.setAttribute(
                                        "childColumn", "spatial_unit_id")
                                    entity_relation.setAttribute(
                                        "name", "fk_" + pref + "_" +
                                                relation[0] + "_" +
                                                relation[1] + "_" + pref +
                                        "_" + relation[0] +
                                        "_supporting_document_" +
                                                "spatial_unit_id")
                                if k == "party_table" and v == \
                                        relation[0]:
                                    entity_relation.setAttribute(
                                        "childColumn", "party_id")
                                    entity_relation.setAttribute(
                                        "name", "fk_" + pref + "_" +
                                                relation[0] +
                                                "_" + relation[1] + "_" +
                                                pref + "_" + relation[0] +
                                        "_supporting_document_" + "party_id")
                            entity_relation.setAttribute(
                                'displayColumns', relation[3])
                            entity_relation.setAttribute(
                                    "parentColumn", "id")
                            relationship.appendChild(entity_relation)

                            ##################################################
                            entity_relation = self.doc_old.createElement(
                                    "EntityRelation")
                            entity_relation.setAttribute(
                                        "parent",  "supporting_document")
                            entity_relation.setAttribute(
                                "child", relation[0] + "_supporting_document")
                            entity_relation.setAttribute(
                                    "name", "fk_" + pref +
                                    "_supporting_document_id_" + pref +
                                    "_" + relation[0] +
                                    "_supporting_document_supporting_doc_id")
                            entity_relation.setAttribute(
                                'displayColumns', relation[3])
                            entity_relation.setAttribute(
                                "parentColumn", "id")
                            entity_relation.setAttribute(
                                    "childColumn", "supporting_doc_id")
                            relationship.appendChild(entity_relation)

                # Default relations
                entity_relation = self.doc_old.createElement("EntityRelation")
                entity_relation.setAttribute(
                    "parent", "check_social_tenure_relationship_document_type")
                entity_relation.setAttribute(
                    "child", "social_tenure_relationship_supporting_document")
                entity_relation.setAttribute(
                    "parentColumn", "id")
                entity_relation.setAttribute(
                    "childColumn", "document_type")
                entity_relation.setAttribute(
                    "name", "fk_" + pref + "_check_social_tenure_relationship_"
                                           "document_type_id_" + pref +
                            "_social_tenure_relationship_supporting_document_"
                            "document_type")
                entity_relation.setAttribute(
                    "displayColumns", "")

                relationship.appendChild(entity_relation)

                entity_relation = self.doc_old.createElement("EntityRelation")
                entity_relation.setAttribute(
                    "parent", "social_tenure_relationship")
                entity_relation.setAttribute(
                    "child", "social_tenure_relationship_supporting_document")
                entity_relation.setAttribute(
                    "parentColumn", "id")
                entity_relation.setAttribute(
                    "childColumn", "social_tenure_relationship_id")
                entity_relation.setAttribute(
                    "name", "fk_" + pref + "_social_tenure_relationship_id_" +
                            pref +
                            "_social_tenure_relationship_"
                            "supporting_document_social_tenure_relationship_id"
                            "")
                entity_relation.setAttribute(
                    "displayColumns", "")

                relationship.appendChild(entity_relation)

                entity_relation = self.doc_old.createElement("EntityRelation")
                entity_relation.setAttribute(
                    "parent", "supporting_document")
                entity_relation.setAttribute(
                    "child", "social_tenure_relationship_supporting_document")
                entity_relation.setAttribute(
                    "parentColumn", "id")
                entity_relation.setAttribute(
                    "childColumn", pref + "_supporting_doc_id")
                entity_relation.setAttribute(
                    "name", "fk_" + pref + "_supporting_document_id_" + pref +
                            "_social_tenure_relationship_supporting_"
                            "document_" + pref + "_supporting_doc_id")
                entity_relation.setAttribute(
                    "displayColumns", "")

                relationship.appendChild(entity_relation)

                entity_relation = self.doc_old.createElement("EntityRelation")
                entity_relation.setAttribute(
                    "parent", "check_tenure_type")
                entity_relation.setAttribute(
                    "child", "social_tenure_relationship")
                entity_relation.setAttribute(
                    "parentColumn", "id")
                entity_relation.setAttribute(
                    "childColumn", "tenure_type")
                entity_relation.setAttribute(
                    "name", "fk_" + pref + "_check_tenure_type_id_" + pref +
                            "_social_tenure_relationship_tenure_type")
                entity_relation.setAttribute(
                    "displayColumns", "")

                relationship.appendChild(entity_relation)

                # Adding relation that exists within column to Entity
                # relation nodes
                if entity_relation_dict:
                    for k, v in entity_relation_dict.iteritems():
                        entity_relation = self.doc_old.createElement(
                                "EntityRelation")
                        entity_relation.setAttribute("parent", v[0])
                        entity_relation.setAttribute("displayColumns", "")
                        entity_relation.setAttribute("child", v[1])
                        entity_relation.setAttribute("name", k)
                        entity_relation.setAttribute("parentColumn", "id")
                        entity_relation.setAttribute("childColumn", v[2])
                        relationship.appendChild(entity_relation)

                profile_element.appendChild(relationship)

                social_tenure = self.doc_old.createElement("SocialTenure")
                social_tenure.setAttribute(
                    "layerDisplay", profile.lower() + "_vw_social_tenure_relationship")
                social_tenure.setAttribute(
                    "tenureTypeList", "check_tenure_type")

                for relation_key, relation_values in value.iteritems():

                    if relation_key == "social_tenure_relationship":
                        sp_party_dict = self._set_sp_unit_part_tables(
                            relation_values)
                        social_tenure.setAttribute("spatialUnit",
                                                   sp_party_dict[
                                                       'spatial_unit_table'])
                        social_tenure.setAttribute("party", sp_party_dict[
                                                       'party_table'])

                profile_element.appendChild(social_tenure)

        return profile_element

    def _create_profile_value_lists_entity_nodes(self,
                                                 config_profile_values_dict,
                                                 config):

        """
        Create QtXML nodes
        :param config_profile_values_dict:
        :param config:
        :return: QDocument Element
        """
        for config_profile, values in config_profile_values_dict.iteritems():

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
                config_profile = config_profile
                conf_prefix = config_profile[:2].lower()
                self.config_profiles_prefix.append(conf_prefix)
                self.config_profiles.append(config_profile)
                profile_element = self.doc_old.createElement("Profile")
                profile_element.setAttribute("description", "")
                profile_element.setAttribute("name", config_profile)
                profile_element = self._create_entity_valuelist_relation_nodes(
                                    conf_prefix, config_profile,
                                    profile_element, values)
                config.appendChild(profile_element)

        return config

    def _populate_config_from_old_config(self):
        """
        Read old configuration file and uses it content to populate new
        config file
        """
        configuration = self.doc_old.createElement("Configuration")
        configuration.setAttribute("version", '1.2')
        self.doc_old.appendChild(configuration)

        # Create profile valuelists and entity nodes
        config = self._create_profile_value_lists_entity_nodes(
                    self.entities_lookup_relations, configuration)

        # configuration.appendChild(config)

        self.doc_old.appendChild(config)

        stream = QTextStream(self.config_file)
        stream << self.doc_old.toString()
        self.config_file.close()
        self.doc_old.clear()

    def load(self, plugin_path, progress, manual=False):

        """
        Executes the updater and creates configuration_upgraded.stc.
        :return:
        """
        self.progress = progress
        if self._check_config_folder_exists():
            # Check if old configuration file exists
            if self._check_config_file_exists("stdmConfig.xml"):
                # Get old and new config path from existing registry
                data_folder_path = source_documents_path()
                template_path = composer_template_path()
                if data_folder_path is None or template_path is None:
                    self.btn_template.clicked.connect(
                        self.set_template_path
                    )
                    self.btn_supporting_docs.clicked.connect(
                        self.set_document_path
                    )
                    self.btn_output.clicked.connect(
                        self.set_output_path
                    )
                    apply_btn = self.buttonBox.button(
                        QDialogButtonBox.Apply
                    )
                    apply_btn.clicked.connect(
                        self.validate_path_setting
                    )

                    self.exec_()

                # Set the document paths
                self.old_data_folder_path = os.path.join(
                    source_documents_path(), "2020"
                )
                self.new_data_folder_path = source_documents_path()

                self.append_log('stdmConfig.xml exists')
                self.config_updated_dic = self.reg_config.read(
                    [CONFIG_UPDATED]
                )

                # if config file exists, check if registry key exists
                if len(self.config_updated_dic) < 1:
                    # if it doesn't exist, create it with a value of False ('0')
                    self.reg_config.write({'ConfigUpdated': '0'})
                    self.config_updated_dic = self.reg_config.read(
                        [CONFIG_UPDATED]
                    )
                    config_updated_val = self.config_updated_dic[
                        CONFIG_UPDATED]

                else:
                    config_updated_val = self.config_updated_dic[CONFIG_UPDATED]

                if config_updated_val == '0':
                    self._copy_config_file_from_template()
                    self.create_log_file(self.log_file_path)

                    if not manual:
                        result, checkbox_result = simple_dialog(
                            self.iface.mainWindow(),
                            'Upgrade Information',
                            'Would you like to view the '
                            'new features and changes of STDM 1.2?'
                        )
                        if result:
                            change_log = ChangeLog(self.iface.mainWindow())
                            change_log.show_change_log(plugin_path)

                    self.progress.show()
                    self.progress.setValue(0)
                    self.upgrade = True
                    self.old_config_file = True
                    doc, root = self._get_doc_element("stdmConfig.xml")
                    child_nodes = root.childNodes()

                    # Parse old configuration to dictionary
                    self._set_version_profile(child_nodes)

                    # Create config file
                    self._create_config_file("configuration_upgraded.stc")

                    # Create configuration node and version
                    self._populate_config_from_old_config()
                    self.append_log(
                        'Created and populated configuration_upgraded.stc'
                    )
                    return self.upgrade

                else:
                    if not self._check_config_file_exists("configuration.stc"):
                        self._copy_config_file_from_template()

                    return False
        else:
            self._create_config_folder()
            self._copy_config_file_from_template()
            return False

    def closeEvent(self, event):
        if self.validate_path_setting():
            event.accept()
        else:
            event.reject()


    def validate_path_setting(self):
        notice = NotificationBar(
            self.notification_bar
        )

        error = QApplication.translate(
            'ConfigurationFileUpdater',
            'Please select all the three paths used by STDM.'
        )
        success = QApplication.translate(
            'ConfigurationFileUpdater',
            'You have successfully set STDM path settings.'
        )

        if self.text_template.text() != '' and \
                        self.text_document.text() != '' and \
                        self.text_output != '':

            notice.insertSuccessNotification(success)
            # Commit document path to registry
            self.reg_config.write(
                {NETWORK_DOC_RESOURCE:
                     self.text_document.text()
                 }
            )
            # Commit template path to registry
            self.reg_config.write(
                {COMPOSER_TEMPLATE:
                     self.text_template.text()
                 }
            )
            # Commit output path to registry
            self.reg_config.write(
                {COMPOSER_OUTPUT:
                     self.text_output.text()
                 }
            )
            self.close()
            return True
        else:
            notice.insertErrorNotification(error)
            return False



    def set_template_path(self):
        """
            Sets the templates path to the registry
            based on user's selection. This is required
            if the registry key doesn't exist.
            """
        template_str = QApplication.translate(
            'ConfigurationFileUpdater',
            'Specify the template folder '
            'the contains your document templates.'
        )

        template_path = QFileDialog.getExistingDirectory(
            self.iface.mainWindow(),
            template_str
        )
        self.text_template.setText(template_path)

        self.append_log(
            'The template path - {} is set by the user'.format(
                template_path
            )
        )

    def set_output_path(self):
        """
            Sets the output path to the registry
            based on user's selection. This is required
            if the registry key doesn't exist.
            """
        output_str = QApplication.translate(
            'ConfigurationFileUpdater',
            'Specify the template folder '
            'the contains your document templates.'
        )

        output_path = QFileDialog.getExistingDirectory(
            self.iface.mainWindow(),
            output_str
        )
        self.text_output.setText(output_path)

        self.append_log(
            'The template path - {} is set by the user'.format(
                output_path
            )
        )

    def set_document_path(self):
        """
        Sets the documents path to the registry
        based on user's selection. This is required
        if the registry key doesn't exist.
        """
        document_str = QApplication.translate(
            'ConfigurationFileUpdater',
            'Specify the document folder '
            'the contains the 2020 folder.'
        )
        last_path = last_document_path()

        if last_path is None:
            last_path = '/home'
        document_path = QFileDialog.getExistingDirectory(
            self.iface.mainWindow(),
            document_str,
            last_path
        )
        self.text_document.setText(document_path)

        self.append_log(
            'The document path - {} is set by the user'.format(
                document_path
            )
        )

    def check_version(self):
        """
        Check version of configuration.stc
        :return:
        """
        return self._check_config_version()

    def _add_missing_lookup_config(self, lookup, missing_lookup):
        """
        Add missing value_list to configuration file
        :param lookup:
        :param missing_lookup:
        """
        if self.old_config_file:

            doc, root = self._get_doc_element("configuration_upgraded.stc")
            child_nodes = root.childNodes()
            for child_i in range(child_nodes.count()):
                child_node = child_nodes.item(child_i).toElement()

                if child_node.tagName() == "Profile":
                    profile_child_nodes = child_node.childNodes()

                    for profile_i in range(profile_child_nodes.count()):
                        profile_nodes = profile_child_nodes.item(profile_i).\
                            toElement()
                        if profile_nodes.tagName() == "ValueLists":
                            value_list_nodes = profile_nodes.childNodes()

                            for value_list_i in range(
                                    value_list_nodes.count()):
                                value_list_node = value_list_nodes.item(
                                    value_list_i).toElement()
                                if value_list_node.tagName() == "ValueList":
                                    lookup_name = unicode(
                                        value_list_node.attribute('name'))

                                    if lookup_name == lookup:
                                        code_values_lists = []
                                        code_value_nodes = \
                                            value_list_node.childNodes()
                                        for code_v_i in range(
                                                code_value_nodes.count()):
                                            code_value_node = \
                                                    code_value_nodes.item(
                                                        code_v_i).toElement()
                                            code_value = unicode(
                                                code_value_node.attribute(
                                                    'value'))
                                            code_values_lists.append(
                                                code_value)

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
                                                        0:2].upper())

                                        if missing_lookup not in \
                                                code_values_lists:

                                            value_list_node.appendChild(
                                                code_value)

            self._create_config_file("configuration_upgraded.stc")
            stream = QTextStream(self.config_file)
            stream << doc.toString()
            self.config_file.close()
            doc.clear()

    def _match_lookup(self, values, lookup_data, lookup_col_index,
                      num_lookups, check_up):

        """
        Match look up values
        :param values:
        :param lookup_data:
        :param lookup_col_index:
        :param num_lookups:
        :param check_up:
        :return: list
        """

        # First run to elimiate existing lookups

        for value in values:
            for lookup_value, fk in \
                    lookup_data.iteritems():
                try:
                    if int(value[lookup_col_index]) == fk:
                        value[lookup_col_index] = int(fk)
                except (ValueError, TypeError):
                    if value[lookup_col_index] == unicode(lookup_value):
                        value[lookup_col_index] = int(fk)
                        break

        # Second run to add missing lookups
        for value in values:
            for lookup_value, fk in \
                    lookup_data.items():

                try:
                    if int(value[lookup_col_index]) == fk:
                        value[lookup_col_index] = int(fk)
                except (ValueError, TypeError):
                    if value[lookup_col_index] == unicode(lookup_value):
                        value[lookup_col_index] = int(fk)
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
        """
        Set social tenure relations tables
        :return:
        """
        for k, v in self.entities_lookup_relations.iteritems():
            for keys, values in v.iteritems():
                if keys.endswith("relations") and values:
                    for relation_key, relation_values in values.iteritems():
                        if relation_key == "social_tenure_relationship":
                            return keys, relation_values

    def _clean_data(self, values):
        """
        Cleans data from db removes apostrophes and converts datetime
        :param values:
        :return: list
        """
        new_data_list = []
        for data_value in values:
            inner_data_list = []
            for data in data_value:
                if not isinstance(data, int) and data is not None and not \
                        isinstance(data, datetime.date):

                        if data.find("\'") is not -1:
                            data = unicode(data)
                            data = data.replace("'", "`")

                            inner_data_list.append(data)
                        else:
                            inner_data_list.append(data)

                elif isinstance(data, datetime.date):
                    data = data.strftime('%Y-%m-%d')
                    inner_data_list.append(data)

                else:
                    inner_data_list.append(data)

            new_data_list.append(inner_data_list)

        return new_data_list

    def backup_data(self):
        """
        Method that backups data
        """

        if self.old_config_file:
            # Backup of entities participating in social tenure relationship
            keys, values = self._set_social_tenure_table()

            self.progress.setRange(0, len(values))
            self.progress.show()

            progress_i = 0
            for social_tenure_entity in values:

                social_tenure_table = \
                    self.config_profiles_prefix[0] + "_" + social_tenure_entity[0]

                if pg_table_exists(social_tenure_entity[0]):

                    data = export_data(social_tenure_entity[0])

                    columns = data.keys()

                    # Remove geom columns of line, point and
                    # polygon and replace with one column geom to fit new
                    # config
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
                        # Coverts to list
                        values = [list(i) for i in values]

                        # Only get geom columns with values and
                        # avoid none geom tables
                        new_values = []

                        # Converts Var Char lookup to foreign key and add to
                        #  config file if it dosen't exist
                        for check_up, lookup_data in \
                                self.lookup_colum_name_values.iteritems():
                            if check_up in columns:
                                lookup_col_index = columns.index(check_up)
                                num_lookups = len(lookup_data)
                                values = self._match_lookup(values,
                                                            lookup_data,
                                                            lookup_col_index,
                                                            num_lookups,
                                                            check_up)
                        config_updater = ConfigurationSchemaUpdater()
                        config_updater.exec_()

                        if len(new_keys) is not original_key_len:
                            for value in values:
                                first_v = value[:-3]
                                last_v = value[-3:]
                                new_last_v = []

                                for last in last_v:
                                    if last is not None:
                                        new_last_v.append(last)

                                l = tuple(list(first_v) + new_last_v)

                                new_values.append(l)
                            new_values = unicode(new_values).strip(
                                "[]")
                        else:

                            values = self._clean_data(values)

                            new_values = unicode(values).replace("[[", "(")
                            new_values = unicode(new_values).replace("]]", ")")
                            new_values = unicode(new_values).replace("[", "(")
                            new_values = unicode(new_values).replace("]", ")")
                            new_values = unicode(new_values).replace("None",
                                                                 "NULL")

                        # Remove Unicode
                        values = new_values.replace("u\'", "\'")
                        column_keys = ",".join(new_keys)
                        if not import_data(social_tenure_table, column_keys,
                                       values):
                            pass
                        else:
                            fix_sequence(social_tenure_table)
                    else:
                        pass

                else:
                    pass
                self.progress.setValue(progress_i)
                progress_i = progress_i + 1

            # Backup of social tenure relationship tables, str_relations and
            #  supporting documents.

            # TODO implement type check and return int
            # equivalent
            # social_tenure_type is vchar while tenure
            # type is integer

            self.progress.progress_message('Importing data to the new tables', '')

            self.progress.setRange(0, len(STR_TABLES))
            self.progress.show()

            progress_i = 0

            for STR_tables, v in STR_TABLES.iteritems():
                old_columns = unicode(v['old']).strip("()").replace("\'", "")
                new_columns = unicode(v['new']).strip("()").replace("\'", "")

                if STR_tables == 'social_tenure_relationship':
                    new_STR_table = self.config_profiles_prefix[0] + "_" + STR_tables
                    STR_data = export_data_from_columns(old_columns,
                                                  STR_tables).fetchall()

                    if len(STR_data) > 0:
                        new_STR_data_list = []
                        for data in STR_data:
                            list_data = list(data)
                            for tenure_name, tenure_fkey_value in \
                                    self.lookup_colum_name_values[
                                        'tenure_type'].iteritems():
                                if tenure_name == list_data[1]:
                                    list_data[1] = tenure_fkey_value
                                    break
                                else:
                                    continue

                            new_STR_data_list.append(tuple(list_data))

                        new_STR_data = unicode(new_STR_data_list).strip("[]").replace(
                            "u\'", "\'")

                        if not import_data(new_STR_table, new_columns,
                                           new_STR_data):
                            pass
                        else:
                            fix_sequence(new_STR_table)

                elif STR_tables == 'str_relations':
                    new_STR_table = self.config_profiles_prefix[0] + \
                                    "_social_tenure_relationship_supporting_" \
                                    "document"
                    STR_data = export_data_from_columns(old_columns,
                                                  STR_tables).fetchall()

                    if len(STR_data) > 0:

                        STR_data = [list(i) for i in STR_data]

                        for row in STR_data:
                            row.append(1)

                        STR_data = [tuple(i) for i in STR_data]

                        new_STR_data_list = unicode(STR_data).strip("[]").replace(
                            "u\'", "\'")

                        if not import_data(new_STR_table, new_columns,
                                           new_STR_data_list):
                            pass
                        else:
                            fix_sequence(new_STR_table)

                elif STR_tables == 'supporting_document':
                    new_STR_table = self.config_profiles_prefix[0] + "_" + \
                                    STR_tables

                    STR_data = export_data_from_columns(old_columns,
                                                  STR_tables).fetchall()

                    if len(STR_data) > 0:

                        STR_data = [list(i) for i in STR_data]

                        for row in STR_data:
                            row.append(self.config_profiles_prefix[0] +
                                       "_social_tenure_relationship")

                        STR_data = [tuple(i) for i in STR_data]

                        new_STR_data_list = unicode(STR_data).strip("[]").replace(
                            "u\'", "\'").replace("None", "NULL")

                        if not import_data(new_STR_table, new_columns,
                                           new_STR_data_list):
                            pass
                        else:
                            fix_sequence(new_STR_table)

                self.progress.setValue(progress_i)
                progress_i = progress_i + 1

            if os.path.isdir(self.old_data_folder_path):
                self.progress.progress_message('Moving documents from 2020 to general', 'folder')
                self.progress.setRange(0, len(os.listdir(self.old_data_folder_path)))
                self.progress.show()

                progress_i = 0

                if os.path.isdir(self.old_data_folder_path):
                    src_files = os.listdir(self.old_data_folder_path)
                    path_new_directory = os.path.join(
                        self.new_data_folder_path,
                        self.config_profiles[0].lower(),
                        self.config_profiles_prefix[0].lower() +
                        "_social_tenure_relationship", "general"
                    )
                    for file_name in src_files:
                        full_file_name = os.path.join(
                            self.old_data_folder_path,
                            file_name
                        )

                        self._mkdir_p(path_new_directory)
                        if os.path.isfile(full_file_name):
                            shutil.copy(full_file_name, path_new_directory)

                        self.progress.setValue(progress_i)
                        progress_i = progress_i + 1
                self.append_log('Moved supporting documents from {} to {}'.format(
                    self.old_data_folder_path, self.new_data_folder_path
                ))
            return self.profiles_detail
