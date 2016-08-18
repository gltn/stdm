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
import glob
import xml.etree.ElementTree as ET

from PyQt4.QtXml import QDomDocument
from PyQt4.QtCore import QFile, QIODevice
from PyQt4.QtGui import (
    QApplication, QProgressDialog, QLabel
)
from qgis.utils import (
    iface
)
from sqlalchemy.sql.expression import text

from registryconfig import composer_template_path
from stdm.data.pg_utils import (
    _execute, pg_views, table_column_names, pg_table_exists
)

class TemplateUpdater():
    def __init__(self, prefix='ba'):
        """
        Upgrades old profile templates to version 1.2 profiles.
        :param prefix: The profile prefix of the upgraded profile
        :type prefix: String
        :return: None
        :rtype: NoneType
        """
        self.old_new_tables = {
            'party': '{}_party'.format(prefix),
            'spatial_unit':
                '{}_spatial_unit'.format(prefix),
            'social_tenure_relationship':
                '{}_social_tenure_relationship'.format(prefix),
            'str_relations':
                '{}_social_tenure_relationship_supporting_document'.format(prefix)
        }

        self.supporting_doc_columns = {
            'social_tenure_id': 'social_tenure_relationship_id',
            'source_doc_id': 'supporting_doc_id'
        }
        self.get_templates()

        self.prog = self.overall_progress(iface.mainWindow())

    def get_templates(self):
        """
        Gets the list of templates in the the template path.
        :return: None
        :rtype: NoneType
        """
        self.templates = []
        os.chdir(composer_template_path())
        for file in glob.glob("*.sdt"):
           self.templates.append(file)

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
            return

        doc = QDomDocument()

        status, msg, line, col = doc.setContent(
            config_file
        )
        if not status:
            return

        doc_element = doc.documentElement()

        return doc, doc_element

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
            composer_template_path(),
            template
        )
        return template_path

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

        doc, root = self.get_template_element(
            template_path
        )
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
        # loop through the entire sdt
        for i in range(child_nodes.length()):
            if child_nodes.item(i).nodeName() == 'DataSource':
                attrs = child_nodes.item(i).attributes()
                value = {}
                # loop through dataSource
                for j in range(attrs.length()):
                    value[attrs.item(j).nodeName()] = \
                        attrs.item(j).nodeValue()

                #QApplication.processEvents()
                if 'View' in value.values() or \
                                'view' in value.values():

                    return 'view', value['name']

                elif 'Table' in value.values() or \
                                'table' in value.values():
                    return 'table', value['name']

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
            return
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
                    query_list.append(self.replace_all(q).strip())
                query = ' '.join(query_list)
                query = 'CREATE OR REPLACE VIEW new_{} AS {}'.format(
                    view, query
                )

            try:
                _execute(query, view_name=view)
                return 'new_{}'.format(view)
            except Exception as ex:
                print ex
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
            # update different usage of old tables
            text = text.replace(
                '{}.'.format(old), '{}.'.format(new)
            )
            text = text.replace(
                '{},'.format(old), '{},'.format(new)
            )
            text = text.replace(
                ' {}'.format(old), ' {}'.format(new)
            )
            text = text.replace(
                '({}'.format(old), '({}'.format(new)
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
            #print text
        return text

    def overall_progress(self, parent=None):
        """
        Initializes the progress dialog.
        :param parent: The parent of the dialog.
        :type parent: QWidget
        :return: The progress dialog initialized.
        :rtype: QProgressDialog
        """
        prog_dialog = QProgressDialog(
            parent
        )
        prog_dialog.setFixedWidth(380)
        prog_dialog.setFixedHeight(100)
        prog_dialog.setWindowTitle(
            QApplication.translate(
                "TemplateUpdater",
                'Updating templates...'
            )
        )

        label = QLabel()
        prog_dialog.setLabel(label)

        prog_dialog.setCancelButton(None)
        prog_dialog.show()

        return prog_dialog


    def progress_message(self, val, skip=False):
        """
        Shows progress message in the progress bar.
        :param val: The template name
        :type val: String
        :param skip: Shows Skipping text if True.
        :type skip: Boolean
        :return: None
        :rtype: NoneType
        """
        if skip:
            text = 'Skipping {}...'.format(val)
            self.prog.setLabelText(
                QApplication.translate(
                    'TemplateUpdater', text
                )

            )
        else:
            text = 'Updating {}...'.format(val)
            self.prog.setLabelText(
                QApplication.translate(
                    'TemplateUpdater', text
                )

            )

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
        :return: None
        :rtype: NoneType
        """
        path = self.template_file_path(template)
        with open(path) as f:

            tree = ET.parse(f)
            root = tree.getroot()

            old_new_cols = self.old_new_columns(
                old_source, new_source
            )
            #print old_new_cols
            # loop through each elements in the template
            for i, elem in enumerate(root.iter()):

                #TODO replace old view name with new view name
                if elem.tag == 'DataSource':
                    # view based template
                    if ref_table is not None:

                        if 'referencedTable' not in elem.attrib.keys():
                            elem.set('referencedTable', ref_table)
                        else:
                            # if the view has ref_table, it is updated already
                            return
                    # update the DataSource name if still using old_source
                    if elem.attrib['name'] == old_source:
                        elem.attrib['name'] = elem.attrib['name'].replace(
                            old_source, new_source
                        )
                    # return: the template is already updated
                    elif elem.attrib['name'] == new_source:
                        return

                    self.update_data_source_children(
                        elem, old_new_cols
                    )
                self.update_other_elements(
                    elem, old_source, new_source, old_new_cols
                )

        self.move_file(template, path)
        tree.write(template)

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
        # Replace old_col columns by new_col columns if different
        for old_col, new_col in old_new_cols.iteritems():
            # loop through each attributes
            # in an element
            for key, item in elem.attrib.iteritems():
                # if old_col column name is used,
                # update to new_col col
                if item == old_col:
                    elem.attrib[key] = new_col
                # Replace old_source by new_source if different
                if old_col in item and old_source in item:
                    elem.attrib[key] = item.replace(
                        old_source, new_source
                    ).replace(old_col, new_col)
        # Replace old_tables by new_tables if different
        for old_col, new_col in self.old_new_tables.iteritems():
            if old_col != new_col:
                # loop through each attributes
                # in an element
                for key, item in elem.attrib.iteritems():
                    # if old_col column name is used,
                    # update to new_col col
                    if item == old_col:
                        elem.attrib[key] = new_col

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
        :return: None
        :rtype: NoneType
        """
        for itm in list(elem):
            # print itm.attrib
            if len(itm.attrib) < 1:
                for it in list(itm):
                    for key, val in it.attrib.iteritems():
                        ref_old_new_cols = None
                        if key == 'table':
                            # if it is view, upgrade view and
                            # replace new view and cols
                            if it.attrib[key] in pg_views():
                                upgraded_view = self.upgrade_view(
                                    it.attrib[key]
                                )
                                it.attrib[key] = upgraded_view
                                ref_old_new_cols = self.old_new_columns(
                                    it.attrib[key],
                                    upgraded_view
                                )
                            # if it is table, get new table from dic
                            # replace old with new and get new cols, old cols
                            else:
                                if it.attrib[key] in self.old_new_tables.keys():
                                    ref_old_new_cols = self.old_new_columns(
                                        it.attrib[key],
                                        self.old_new_tables[
                                            it.attrib[key]
                                        ]
                                    )
                                    it.attrib[key] = self.old_new_tables[
                                        it.attrib[key]
                                    ]
                        # Update data source old col with new col
                        if key == 'referenced_field':
                            if it.attrib[key] in old_new_cols.keys():
                                it.attrib[key] = old_new_cols[
                                    it.attrib[key]
                                ]  # data source new col
                        # Update source of item table
                        # columns from old to new
                        if key == 'referencing_field':
                            if not ref_old_new_cols is None:
                                it.attrib[key] = ref_old_new_cols[
                                    it.attrib[key]
                                ]

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
        template_path = composer_template_path()
        old_path = '{}/old_templates'.format(
            template_path
        )
        old_template_path = '{}/{}'.format(
            old_path, template
        )

        if not os.path.exists(old_path):
            os.makedirs(old_path)
        try:
            os.rename(path, old_template_path)
        except WindowsError:
            os.remove(old_template_path)
            os.rename(path, old_template_path)

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
        old_columns = table_column_names(
            old_view, False, True
        )
        new_columns = table_column_names(
            new_view, False, True
        )
        old_new_cols = dict(
            zip(old_columns, new_columns)
        )
        old_new_cols = dict(
            list(old_new_cols.items()) +
            list(self.supporting_doc_columns.items())
        )

        return old_new_cols

    def process_update(self):
        """
        Updates each templates by creating views.
        :return: None
        :rtype: NoneType
        """
        self.prog.setRange(0, len(self.templates))
        self.prog.show()
        for i, template in enumerate(self.templates):

            if self.get_source(template) is None:
                continue

            type, old_source = self.get_source(
                template
            )
            # Process templates with view source
            if type == 'view':

                if old_source == 'social_tenure_relations':
                    upgraded_view = self.old_new_tables[
                        'social_tenure_relations'
                    ]
                else:
                    # if new view is already created, remove 'new_'
                    if 'new_' in old_source:
                        old_source = old_source.lstrip('new_')

                    upgraded_view = self.upgrade_view(
                        old_source
                    )

                if upgraded_view is None:
                    self.progress_message(template, True)
                    continue

                ref_table = self.get_referenced_table(
                    old_source
                )
                self.progress_message(template)
                self.update_template(
                    template,
                    old_source,
                    upgraded_view,
                    ref_table
                )
            # Process templates with table source
            elif type == 'table':
                if old_source in self.old_new_tables.keys():
                    new_table = self.old_new_tables[
                        old_source
                    ]

                    if not new_table is None:
                        self.progress_message(template)
                        self.update_template(
                            template, old_source, new_table
                        )
                    else:
                        self.progress_message(template, True)
                        continue
                else:
                    self.progress_message(template, True)
                    continue

            self.prog.setValue(i)
        self.prog.hide()
        self.prog.cancel()
    #
    # def process_view_template(self, template, old_source):
    #
    #     if old_source == 'social_tenure_relations':
    #         upgraded_view = self.old_new_tables[
    #             'social_tenure_relations'
    #         ]
    #     else:
    #         # if new view is already created, remove 'new_'
    #         if 'new_' in old_source:
    #             old_source = old_source.lstrip('new_')
    #
    #         upgraded_view = self.upgrade_view(
    #             old_source
    #         )
    #
    #     if upgraded_view is None:
    #         self.progress_message(template, True)
    #         return
    #
    #     ref_table = self.get_referenced_table(
    #         old_source
    #     )
    #     self.progress_message(template)
    #     self.update_template(
    #         template,
    #         old_source,
    #         upgraded_view,
    #         ref_table
    #     )