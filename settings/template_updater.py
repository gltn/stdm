# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Template Updater
Description          : A tool used to update old document template with the
                        new tables and views.
Date                 : 13/August/2016
copyright            : (C) 2016 by UN-Habitat and implementing partners.
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
import re
from distutils import dir_util
from distutils.errors import DistutilsFileError
import glob
import xml.etree.ElementTree as ET

from PyQt4.QtXml import QDomDocument
from PyQt4.QtCore import QFile, QIODevice
from PyQt4.QtGui import (
    QApplication,  QMessageBox
)

from qgis.utils import (
    iface
)
from qgis.core import QgsApplication

from sqlalchemy.sql.expression import text

from registryconfig import (
    composer_template_path,
    source_documents_path
)
from stdm.data.pg_utils import (
    _execute,
    pg_views,
    table_column_names,
    pg_table_exists,
    foreign_key_parent_tables
)
from stdm.data.configuration.stdm_configuration import StdmConfiguration

from config_file_updater import ConfigurationFileUpdater

class TemplateFileHandler:
    def __init__(self):
        """
        Handles all template file operations such as
        populating, moving, and formatting full path.
        :return:
        :rtype:
        """
        self.template_path = composer_template_path()
        self.templates = []
        self.populate_templates()
        self.updater = ConfigurationFileUpdater(iface)

    def populate_templates(self):
        """
        Gets the list of templates in the the template path.
        """
        os.chdir(self.template_path)
        for file in glob.glob('*.sdt'):
           self.templates.append(file)

    def template_file_path(self, template):
        """
        Creates the template file path using
        the template file name.
        :param template: The template file name.
        :type template: String
        :return: The full file path of a template.
        :rtype: String
        """
        template_path = os.path.join(
            self.template_path,
            template
        )
        return template_path

    def move_file(self, template, path):
        """
        Moves old template files to old_templates path.
        :param template: the template file name
        :type template: String
        :param path: The path of the template
        :type path: String
        :return: None
        :rtype: NoneType
        """
        old_path = '{}/old_templates'.format(
            self.template_path
        )

        old_template_path = '{}/{}'.format(
            old_path, template
        )

        if not os.path.exists(old_path):
            os.makedirs(old_path)
        try:
            os.rename(path, old_template_path)
        except WindowsError as ex:
            self.updater.append_log(str(ex))
            os.remove(old_template_path)
            os.rename(path, old_template_path)

    def move_back_templates(self):
        """
        Moves back the template files from
        the old_template folder. This is needed
        for manual update.
        """
        old_path = '{}/old_templates'.format(
            self.template_path
        )
        error_title = QApplication.translate(
            'TemplateContentReader',
            'Old Template Restore Error'
        )
        error_access = QApplication.translate(
            'TemplateContentReader',
            'Failed to restore the old template for re-updating. \n'
            'The system cannot access the file because \n'
            'it is being used by another process'
        )


        if os.path.exists(old_path):
            try:
                dir_util.copy_tree(old_path, self.template_path)
            except DistutilsFileError as ex:
                QMessageBox.critical(
                    iface.mainWindow(),
                    error_title,
                    error_access
                )
                self.updater.append_log(str(ex))
            except Exception as ex:
                self.updater.append_log(str(ex))

class TemplateContentReader(
    TemplateFileHandler
):

    def __init__(self):
        """
        Reads template content and gets
        the source table of a template.
        """
        TemplateFileHandler.__init__(self)

    def get_template_element(self, path):
        """
        Gets the template element.
        :param path: The path of the template
        :type path: String
        :return: QDomDocument,
        QDomDocument.documentElement()
        :rtype: Tuple
        """
        config_file = os.path.join(path)
        config_file = QFile(config_file)
        if not config_file.open(QIODevice.ReadOnly):
            template = os.path.basename(path)
            self.prog.setLabelText(
                QApplication.translate(
                    'TemplateUpdater',
                    'Failed to update {}'.format(
                        template
                    )
                )

            )
            error_title = QApplication.translate(
                'TemplateContentReader',
                'File Reading Error'
            )
            error_message = QApplication.translate(
                'TemplateContentReader',
                'Failed to update {0}. '
                'Check the file permission of {0}'.format(
                    template
                )
            )

            QMessageBox.critical(
                iface.mainWindow(),
                error_title,
                error_message
            )
            return None

        doc = QDomDocument()

        status, msg, line, col = doc.setContent(
            config_file
        )
        if not status:
            return None

        doc_element = doc.documentElement()

        return doc_element

    def read_sdt(self, template):
        """
        Reads the template and returns
        the branch child nodes.
        :param template: The name of the template
        :type template: String
        :return: The child nodes.
        :rtype: QDomNodeList
        """
        template_path = self.template_file_path(
            template
        )

        root = self.get_template_element(
            template_path
        )
        if root is None:
            return None
        child_nodes = root.childNodes()
        return child_nodes

    def get_source(self, template):
        """
        Gets the template source view or table name.
        :param template: The name of the template
        :type template: String
        :return: The source type and name of the source
        :rtype: Tuple
        """
        child_nodes = self.read_sdt(template)
        if child_nodes is None:
            return None
        # loop through the entire sdt
        for i in range(child_nodes.length()):
            if child_nodes.item(i).nodeName() == 'DataSource':
                attrs = child_nodes.item(i).attributes()
                value = {}
                # loop through dataSource
                for j in range(attrs.length()):
                    value[attrs.item(j).nodeName()] = \
                        attrs.item(j).nodeValue()

                if 'View' in value.values() or \
                                'view' in value.values():

                    return 'view', value['name']

                elif 'Table' in value.values() or \
                                'table' in value.values():
                    return 'table', value['name']


class TemplateViewHandler:
    def __init__(self, old_new_tables):
        """
        Updates template views.
        :param old_new_tables: Dictionary of old and new tables.
        :type old_new_tables: Dictionary
        :return:
        :rtype:
        """
        if len(old_new_tables) < 1:
            return

        self.profile_name = old_new_tables.keys()[0].lower()
        self.prefix = self.profile_name[:2]
        self.old_new_tables = old_new_tables.values()[0]

        self.documents_path = source_documents_path()

        self.supporting_doc_columns = {
            'social_tenure_id': 'social_tenure_relationship_id',
            'source_doc_id': 'supporting_doc_id'
        }
        config = StdmConfiguration.instance()
        self.updater = ConfigurationFileUpdater(iface)
        self.all_profiles = config.profiles.keys()

    def view_details(self, view):
        """
        Gets the view definition/query
        used to create it.
        :param view: The name of the view.
        :type view: String
        :return: The definition/query.
        :rtype: String
        """
        if view in pg_views():
            t = text('SELECT definition '
                'FROM pg_views '
                'WHERE viewname=:view_name;'
            )

            result = _execute(t, view_name=view)

            definition = []
            for row in result:
                definition.append(row[0])
            return definition[0]

    def get_referenced_table(self, view):
        """
        Returns the referenced table name
        from an old view definition.
        :param view: The view name
        :type view: String
        :return: Referenced table name
        :rtype: String
        """
        definition = self.view_details(view)
        if definition is None:
            return None
        lo_def = definition.lower().strip().lstrip('select')
        query_lines = lo_def.splitlines()
        ref_table = None
        for q in query_lines:
            if ' id ' in q:
                q = q.split('.')
                ref_table = q[0].strip()
                break
            if '.id' in q and 'as' not in q.lower():
                q = q.split('.')
                q = q[0].split(' ')
                ref_table = q[-1].strip()

                break
        # if view is based on the new templates, use ref_table
        if 'new' in view:
            return ref_table
        else:
            return self.old_new_tables[ref_table]

    def extract_view_tables_columns(self, view_definition):
        """
        Extract view tables and columns with a
        format of table.column.
        :param view_definition: The Query used to
        created the view.
        :type view_definition: String
        :return: List containing table.column
        :rtype: List
        """
        pattern = re.compile(ur'[a-z]+\w+\.\w+')

        table_cols = re.findall(pattern, view_definition)
        return table_cols

    def return_lookup(self, table_col):
        """
        Returns a lookup table if a column is lookup column.
        :param table_col: table and column concatenated by '.'
        :type table_col: String
        :return: List containing the lookup table name
        :rtype: List
        """
        table_col_list = table_col.split('.')
        table = table_col_list[0]
        col = table_col_list[1]

        parent_lookup = [
            a[1]
            for a in foreign_key_parent_tables(table)
            if a[0] == col and 'check_' in a[1]
        ]

        return parent_lookup

    def covert_to_lookup_value(self, view_definition):
        """
        Converts a view definition containing lookups
        with no id to values for better presentation.
        :param view_definition: The Query used to
        created the view.
        :type view_definition: String
        :return: An updated view definition
        :rtype: String
        """
        table_cols = self.extract_view_tables_columns(
            view_definition
        )

        for table_col in table_cols:

            lookup_table_list = self.return_lookup(table_col)
            table_col_list = table_col.split('.')
            table = table_col_list[0]
            column = table_col_list[1]
            if len(lookup_table_list) > 0:
                lookup_table = lookup_table_list[0]
                # if lookup column is used in the beginning or middle
                if '{},'.format(table_col) in view_definition:

                    select_value = '(SELECT {0}.value ' \
                       'FROM {0} ' \
                       'WHERE {0}.id =' \
                       ' {1}) AS {2},'.format(
                        lookup_table,
                        table_col,
                        column
                    )
                    view_definition = view_definition.replace(
                        '{},'.format(table_col), select_value
                    )
                # if lookup column is used at the end
                elif ', {}'.format(table_col) in view_definition:
                    select_value = ', (SELECT {0}.value ' \
                                   'FROM {0} ' \
                                   'WHERE {0}.id =' \
                                   ' {1})'.format(
                                        lookup_table,
                                        table_col
                                    )
                    view_definition = view_definition.replace(
                        ', {}'.format(table_col), select_value
                    )
                # if lookup column has alias
                elif '{} AS'.format(table_col) in view_definition:

                    select_value = '(SELECT {0}.value ' \
                                   'FROM {0} ' \
                                   'WHERE {0}.id =' \
                                   ' {1})'.format(
                        lookup_table,
                        table_col
                    )
                    view_definition = view_definition.replace(
                        table_col, select_value
                    )
                # For ordered rows based on lookup
                # if the join has braces
                if ') ORDER BY CASE' in view_definition:
                    order_statement = ' JOIN {0} ON ' \
                        '({0}.id = {1})) ' \
                        'ORDER BY CASE {0}.value WHEN'.format(
                            lookup_table, table_col
                        )
                    view_definition = view_definition.replace(
                        ') ORDER BY CASE {} WHEN'.format(table_col),
                        order_statement
                    )
                # if the join has no braces
                elif ') ORDER BY CASE' not in view_definition and \
                                'ORDER BY CASE' in view_definition:
                    order_statement = ' JOIN {0} ON ' \
                                      '({0}.id = {1}) ' \
                                      'ORDER BY CASE {0}.value WHEN'.format(
                        lookup_table, table_col
                    )
                    view_definition = view_definition.replace(
                        'ORDER BY CASE {} WHEN'.format(table_col),
                        order_statement
                    )

        return view_definition

    def upgrade_view(self, view):
        """
        Upgrades the view with the new
        tables and adds new_ prefix to the view.
        :param view: Tee name of the view
        :type view: String
        :return: The newly created view name
        :rtype: String
        """
        view_def = self.view_details(view)

        # exclude str view of the new configuration
        if view in self.old_new_tables.values():
            return
        if not view_def is None:
            query_lines = view_def.splitlines()
            query_list = []

            if 'new' in view:
                for q in query_lines:
                    query_list.append(q.strip())
                query = ' '.join(query_list)
                query = 'CREATE OR REPLACE VIEW {} AS {}'.format(
                    view, query
                )

            else:
                for q in query_lines:
                    query_list.append(
                        self.replace_all(q).strip()
                    )

                query = ' '.join(query_list)

                query = 'CREATE OR REPLACE VIEW new_{} AS {}'.format(
                    view, query
                )

                # convert lookup id to value
                query = self.covert_to_lookup_value(query)

            try:
                _execute(query, view_name=view)
                return 'new_{}'.format(view)
            except Exception as ex:
                self.updater.append_log(str(ex))
                return None

    def replace_all(self, text):
        """
        Replaces view definition rows with
        new columns and table names.
        :param text: The row of the view definition
        :type text: String
        :return: Updated view definition
        :rtype: String
        """
        for old, new in self.old_new_tables.iteritems():

            text = text.replace(
                '{}.'.format(old), '{}.'.format(new)
            )
            text = text.replace(
                '{},'.format(old), '{},'.format(new)
            )
            if '{}_id'.format(old) in text:
                text = text.replace(
                    ' {}'.format(old), ' {}'.format(old)
                )



            text = text.replace(
                ' {} '.format(old), ' {} '.format(new)
            )
            text = text.replace(
                '({}'.format(old), '({}'.format(new)
            )
            text = text.replace(
                '{})'.format(old), '{})'.format(new)
            )
            # update column names
            text = text.replace(
                'social_tenure_type', 'tenure_type'
            )

            if '.spatial_unit_id' not in text:
                text = text.replace(
                    '.spatial_unit', '.spatial_unit_id'
                )
            if '.party_id' not in text:
                text = text.replace(
                    '.party', '.party_id'
                )
            text = text.replace(
                'social_tenure_id', 'social_tenure_relationship_id'
            )
            # remove text, integer from the query
            # this is needed to remove data type error
            text = text.replace(
                '::text', ''
            )
            text = text.replace(
                '::integer', ''
            )

            if 'social_tenure_relationship_{}_supporting_document'.format(
                    self.prefix) in text \
                    and old == 'supporting_document':
                text = text.replace(
                    '{}_{}'.format(self.prefix, old), '{}'.format(old)
                )

        return text


class TemplateFileUpdater(
    TemplateContentReader,
    TemplateViewHandler
):

    def __init__(self, plugin_dir, old_new_tables, progress):
        """
         Upgrades old profile templates to version 1.2 profiles.
        :param plugin_dir: The directory of STDM plugin
        :type plugin_dir: String
        :param prefix: The profile prefix of the upgraded profile
        :type prefix: String
        :param profile: The profile name that is upgraded
        :type profile: String
        """
        TemplateContentReader.__init__(self)
        TemplateViewHandler.__init__(self, old_new_tables)


        self.prog = progress
        # self.prog.overall_progress(
        #     'Updating Templates...',
        #     iface.mainWindow()
        # )
        # self.prog.show()
        self.old_new_cols_list = []
        self.plugin_dir = plugin_dir


    def update_template(
            self, template, old_source, new_source, ref_table=None
    ):
        """
        Updates a template using new source and reference table.
        It creates a new template in the template directory
        using the same name and move the old template
        to old_templates folder under the template directory.
        :param template: The template file name to be updated
        :type template: String
        :param old_source: Old source table or view
        :type old_source: String
        :param new_source: New source table or view
        :type new_source: String
        :param ref_table: The reference table name of the source
        :type ref_table: String
        """
        path = self.template_file_path(template)
        with open(path) as f:

            self.old_new_cols_list[:] = []
            tree = ET.parse(f)
            root = tree.getroot()

            old_new_cols = self.old_new_columns(
                old_source, new_source
            )

            # loop through each elements in the template
            for i, elem in enumerate(root.iter()):

                if elem.tag == 'DataSource':
                    # view based template
                    if ref_table is not None:

                        if 'referencedTable' not in elem.attrib.keys():
                            elem.set('referencedTable', ref_table)
                        else:
                            # if the view has ref_table,
                            # it is updated already
                            return

                    # return: the template is already updated
                    elif elem.attrib['name'] == new_source:
                        return
                    # update the DataSource name if
                    #  still using old_source
                    if elem.attrib['name'] == old_source:

                        elem.attrib['name'] = elem.attrib['name'].replace(
                            old_source, new_source
                        )
                    self.update_data_source_children(
                        elem, old_new_cols
                    )


            other_old_new_col_dic = {
                k: v
                for old_new in self.old_new_cols_list
                for k, v in old_new.items()
                }
            if len(other_old_new_col_dic) > 0:

                old_new_cols.update(
                    other_old_new_col_dic
                )
            # Update other elements
            for i, elem in enumerate(root.iter()):
                self.update_other_elements(
                    elem, old_source, new_source, old_new_cols
                )

        self.move_file(template, path)
        tree.write(template)

    def update_path_items(self, elem, key, pattern, splitter, path):
        """
        Updates old version path with new version path of items.
        :param elem: The element holding the item.
        :type elem:  xml.etree.ElementTree.Element
        :param key: The key of the path item
        :type key: String
        :param pattern: The pattern to be searched in the item
        :type pattern: String
        :param splitter: The string splitting the path to
        exclude old path.
        :type splitter: String
        :param path: The new absolute path excluding the
        item unchanged path
        :type path: String
        """
        if pattern in elem.attrib[key]:
            temp_attrib = elem.attrib[key]
            if splitter != '':
                temp_attrib = temp_attrib.split(
                    splitter
                )

                if len(temp_attrib) > 0:
                    new_path = ''.join([
                        path,
                        temp_attrib[1]
                    ])

                    elem.attrib[key] = new_path
            else:
                new_path = path
                elem.attrib[key] = new_path

    def update_other_elements(
            self, elem, old_source, new_source, old_new_cols
    ):
        """
        Updates all nodes except the data source node to the
        new tables and columns.
        :param elem: The DataSource element
        :type elem: xml.etree.ElementTree.Element
        :param old_source: Old source table or view
        :type old_source: String
        :param new_source: New source table or view
        :type new_source: String
        :param old_new_cols: Old and new columns list
        :type old_new_cols: Dictionary
        :return:
        :rtype:
        """
        # loop through each attributes
        # in an element

        for key, item in elem.attrib.iteritems():

            # Replace old columns by new columns if different
            for old_col, new_col in old_new_cols.iteritems():
                # if old column name is used,
                # update to new col
                if item == old_col:
                    elem.attrib[key] = new_col
                # Replace old_source by new_source if different
                if old_col in item and old_source in item:
                    elem.attrib[key] = item.replace(
                        old_source, new_source
                    ).replace(old_col, new_col)
            # Replace old_tables by new_tables if different
            for old_table, new_table in self.old_new_tables.iteritems():
                if old_table != new_table:
                    # if old_col column name is used,
                    # update to new_col col
                    if item == old_table:
                        elem.attrib[key] = old_table

            # replace static items in QGIS directory
            #If svg files are used, replace them with the new version
            qgis_path = QgsApplication.prefixPath().rstrip('.')
            self.update_path_items(
                elem,
                key,
                '/QGISWI~1.3)F/apps/qgis/svg',
                '/QGISWI~1.3)F/apps/qgis',
                qgis_path
            )

            new_path = '{0}/{1}/General'.format(
                self.documents_path,
                self.profile_name
            )

            self.update_path_items(
                elem,
                key,
                '/2020',
                '',
                new_path
            )
            # If plugin files are used, replace them
            # with the new version directory
            self.update_path_items(
                elem,
                key,
                '/plugins/stdm/',
                '/plugins/stdm',
                self.plugin_dir
            )

    def children_generator(self, elem):
        """
        A generator method used to go deep into the
        DataSource element.
        :param elem: The DataSource element
        :type elem: xml.etree.ElementTree.Element
        """
        for itm in list(elem):
            # target photo, tables, chart elements
            if len(itm.attrib) < 1:
                # access each children under photo, table, etc
                for it in list(itm):
                    yield it

    def update_table(self, key, child):
        """
        Updates the table attribute in sub-child of
        the dataSource node of the template.
        :param key: The attribute name inside a
        child element(table).
        :type key: String
        :param child: The sub-child element of the
        DataSource element.
        :type child:
        """
        # if it is view, upgrade the view and
        # replace new view and cols
        ref_old_new_cols = None
        if child.attrib[key] in pg_views():
            old_view = child.attrib[key]
            if 'new_' in old_view:
                old_view = old_view.lstrip(
                    'new_'
                )

            upgraded_view = self.upgrade_view(
                old_view
            )
            if not upgraded_view is None:
                ref_old_new_cols = self.old_new_columns(
                    child.attrib[key],
                    upgraded_view
                )
                child.attrib[key] = upgraded_view
                self.old_new_cols_list.append(ref_old_new_cols)

        # if it is table, get new table from dic
        # replace old with new and get new cols, old cols
        else:
            if child.attrib[key] in self.old_new_tables.keys():
                ref_old_new_cols = self.old_new_columns(
                    child.attrib[key],
                    self.old_new_tables[
                        child.attrib[key]
                    ]
                )
                child.attrib[key] = self.old_new_tables[
                    child.attrib[key]
                ]
        return ref_old_new_cols

    def update_referenced(self, key, child, old_new_cols):
        """
        Updates the referenced attribute in sub-child of
        the dataSource node of the template.
        :param key: The attribute name inside a child
        element (referenced_field)
        :type key: String
        :param child: The sub-child element of the
        DataSource element.
        :type child: xml.etree.ElementTree.Element
        :param old_new_cols: Dictionary of
        old and new tables.
        :type old_new_cols: Dictionary
        """
        if child.attrib[key] in old_new_cols.keys():
            child.attrib[key] = old_new_cols[
                child.attrib[key]
            ]  # data source new col

    def update_referencing(
            self, key, child, ref_old_new_cols
    ):
        """
        Updates the referencing attribute in sub-child of
        the dataSource node of the template.
        :param key: The attribute name inside a child element
         (referencing_field).
        :type key: String
        :param child: The sub-child element of the
        DataSource element.
        :type child: xml.etree.ElementTree.Element
        :param ref_old_new_cols: Dictionary of
        old and new tables of the reference table.
        :type ref_old_new_cols: Dictionary
        """
        child.attrib[key] = ref_old_new_cols[
            child.attrib[key]
        ]

    def update_data_source_children(
            self, elem, old_new_cols
    ):
        """
        Updates data source node children to the
        new tables and columns.
        :param elem: The DataSource element
        :type elem: xml.etree.ElementTree.Element
        :param old_new_cols: Old and new columns list
        :type old_new_cols: Dictionary
        """
        child_item = self.children_generator(elem)

        for child in child_item:
            for key, value in child.attrib.iteritems():
                ref_old_new_cols = None
                if key == 'table':

                    ref_old_new_cols = self.update_table(
                        key, child
                    )
                # Update data source old col with new col
                if key == 'referenced_field':
                    self.update_referenced(
                        key, child, old_new_cols
                    )

                if key == 'referencing_field':
                    if not ref_old_new_cols is None:
                        self.update_referencing(
                            key, child, ref_old_new_cols
                        )

    def old_new_columns(self, old_view, new_view):
        """
        Create a dictionary out of the old and
        new view columns.
        :param old_view: Old view name
        :type old_view: String
        :param new_view: New View name
        :type new_view: Strong
        :return: Dictionary of old and new view columns
        :rtype: Dictionary
        """
        if 'new_' in old_view:
            old_view = old_view.lstrip('new_')

        old_columns = table_column_names(
            old_view, False, True
        )
        new_columns = table_column_names(
            new_view, False, True
        )
        old_new_cols = dict(
            zip(old_columns, new_columns)
        )

        old_new_cols.update(
            self.supporting_doc_columns
        )

        return old_new_cols

    def process_view_template(self, template, old_source):
        """
        Updates templates based on a view data source.
        :param template: The template file name to be updated.
        :type template: String
        :param old_source: The view name of
        the old template data source
        :type old_source: String
        """

        new_profile_views = [
            p for p in self.all_profiles
            if p.lower() in old_source
        ]

        if old_source == 'social_tenure_relations':
            upgraded_view = self.old_new_tables[
                'social_tenure_relations'
            ]
        # if old str view is updated already use the new one
        elif self.profile_name in old_source:
            upgraded_view = None

        elif len(new_profile_views) > 0:
            upgraded_view = None
        # if new view is already created, remove 'new_'
        elif 'new_' in old_source:
            old_source = old_source.lstrip('new_')
            upgraded_view = self.upgrade_view(
                old_source
            )
        else:
            upgraded_view = self.upgrade_view(
                old_source
            )

        if upgraded_view is not None:

            ref_table = self.get_referenced_table(
                old_source
            )
            self.prog.progress_message('Updating', template)
            self.update_template(
                template,
                old_source,
                upgraded_view,
                ref_table
            )

        else:
            self.prog.progress_message('Skipping', template)

    def process_table_template(self, template, old_source):
        """
        Updates templates based on a table data source.
        :param template: The template file name to be updated.
        :type template: String
        :param old_source: The table name of
        the old template data source
        :type old_source: String
        """
        if old_source in self.old_new_tables.keys():
            new_table = self.old_new_tables[
                old_source
            ]

            if not new_table is None:
                self.prog.progress_message('Upgrading', template)
                self.update_template(
                    template, old_source, new_table
                )

            else:
                self.prog.progress_message('Skipping', template)

        else:
            self.prog.progress_message('Skipping', template)


    def process_update(self, force_update=False):
        """
        Updates each templates by creating views.
        :param force_update: forces templates to be
        updated even if they have the new tables.
        :param type: Boolean
        :return: None
        :rtype: NoneType
        """
        self.prog.setRange(0, len(self.templates))

        self.prog.show()
        if force_update:
            self.move_back_templates()

        for i, template in enumerate(self.templates):

            if self.get_source(template) is None:
                continue

            type, old_source = self.get_source(
                template
            )
            try:
                # Process templates with view source
                if type == 'view':
                    self.updater.append_log(
                        'Trying to upgrade {}'.format(
                            template
                        )
                    )
                    self.process_view_template(
                        template, old_source
                    )

                # Process templates with table source
                elif type == 'table':
                    self.updater.append_log(
                        'Trying to upgrade {}'.format(
                            template
                        )
                    )
                    self.process_table_template(
                        template, old_source
                    )


            except Exception as ex:
                self.updater.append_log(
                    'Failed to upgrade {}'.format(
                        template
                    )
                )
                self.updater.append_log(str(ex))
                error_title = QApplication.translate(
                    'TemplateContentReader',
                    'Error Updating Template'
                )
                error_message = QApplication.translate(
                    'TemplateContentReader',
                    'Something went wrong while '
                    'updating the template - {}.'.format(
                        template
                    )
                )

                QMessageBox.critical(
                    iface.mainWindow(),
                    error_title,
                    error_message
                )
            else:
                self.updater.append_log(
                    'Successfully upgraded {}'.format(
                        template
                    )
                )

            self.prog.setValue(i)
        self.prog.hide()
        self.prog.cancel()
