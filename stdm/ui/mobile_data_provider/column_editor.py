# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : column_editor
Description          : Editor to create/edit entity columns
Date                 : 24/January/2016
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

import datetime
import logging

from qgis.PyQt import uic
from qgis.PyQt.QtCore import (
    Qt,
    QRegExp,
    QSettings,
    QEvent,
)
from qgis.PyQt.QtGui import (
    QRegExpValidator,
    QValidator
)
from qgis.PyQt.QtWidgets import (
    QDialog,
    QApplication,
    QDialogButtonBox,
    QMessageBox
)

from stdm.data.configuration.columns import BaseColumn
from stdm.ui.gui_utils import GuiUtils
from stdm.ui.notification import NotificationBar

WIDGET, BASE = uic.loadUiType(
    GuiUtils.get_ui_file_path('mobile_data_provider/ui_mobile_provider_column_editor.ui'))

LOGGER = logging.getLogger('stdm')
LOGGER.setLevel(logging.DEBUG)

RESERVED_KEYWORDS = [
    'id', 'documents', 'spatial_unit', 'supporting_document',
    'social_tenure', 'social_tenure_relationship', 'geometry',
    'social_tenure_relationship_id'
]


class AppearanceColumnEditor(WIDGET, BASE):
    """
    Dialog to add/edit entity columns
    """

    def __init__(self, **kwargs):
        """
        :param parent: Owner of this dialog
        :type parent: QWidget
        :param kwargs: Keyword dictionary of the following parameters;
         column  - Column you editing, None if its a new column
         entity  - Entity you are adding the column to
         profile - Current profile
         in_db   - Boolean flag to indicate if a column has been created in
                   the database
         auto_add- True to automatically add a new column to the entity,
                   default is False.
        """

        self.form_parent = kwargs.get('parent', self)
        self.column = kwargs.get('column', None)
        self.entity = kwargs.get('entity', None)
        self.profile = kwargs.get('profile', None)
        self.in_db = kwargs.get('in_db', False)
        self.is_new = kwargs.get('is_new', True)
        self.auto_entity_add = kwargs.get('auto_add', False)
        self.entity_has_records = kwargs.get('entity_has_records', False)

        QDialog.__init__(self, self.form_parent)

        self.FK_EXCLUDE = ['supporting_document', 'admin_spatial_unit_set']

        self.EX_TYPE_INFO = ['SUPPORTING_DOCUMENT', 'SOCIAL_TENURE',
                             'ADMINISTRATIVE_SPATIAL_UNIT', 'ENTITY_SUPPORTING_DOCUMENT',
                             'VALUE_LIST', 'ASSOCIATION_ENTITY', 'AUTO_GENERATED']

        self.setupUi(self)
        self.dtypes = {}

        self.type_info = ''

        # dictionary to hold default attributes for each data type
        self.type_attribs = {}
        self.init_type_attribs()

        self.appearanceColumnDataType.currentIndexChanged.connect(self.change_data_type)

        self.notice_bar = NotificationBar(self.notif_bar)
        self._exclude_col_type_info = []
        self.init_controls()

    def init_type_attribs(self):
        """
        Initializes data type attributes. The attributes are used to
        set the form controls state when a particular data type is selected.
        mandt - enables/disables checkbox 'Mandatory'
        search - enables/disables checkbox 'Searchable'
        unique - enables/disables checkbox 'Unique'
        index - enables/disables checkbox 'Index'
        *property - function to execute when a data type is selected.
        """
        self.type_attribs['VARCHAR'] = {
            'mandt': {'check_state': False, 'enabled_state': True},
            'search': {'check_state': True, 'enabled_state': True},
            'unique': {'check_state': False, 'enabled_state': True},
            'index': {'check_state': False, 'enabled_state': True}
        }

        self.type_attribs['INT'] = {
            'mandt': {'check_state': False, 'enabled_state': True},
            'search': {'check_state': True, 'enabled_state': True},
            'unique': {'check_state': False, 'enabled_state': True},
            'index': {'check_state': False, 'enabled_state': False},
            'minimum': 0, 'maximum': 0
        }

        self.type_attribs['TEXT'] = {
            'mandt': {'check_state': False, 'enabled_state': True},
            'search': {'check_state': False, 'enabled_state': False},
            'unique': {'check_state': False, 'enabled_state': False},
            'index': {'check_state': False, 'enabled_state': False},
        }

        self.type_attribs['DOUBLE'] = {
            'mandt': {'check_state': False, 'enabled_state': True},
            'search': {'check_state': True, 'enabled_state': True},
            'unique': {'check_state': False, 'enabled_state': True},
            'index': {'check_state': False, 'enabled_state': True},
            'minimum': 0.0, 'maximum': 0.0,
            'precision': 18, 'scale': 6}

        self.type_attribs['DATE'] = {
            'mandt': {'check_state': False, 'enabled_state': True},
            'search': {'check_state': False, 'enabled_state': True},
            'unique': {'check_state': False, 'enabled_state': False},
            'index': {'check_state': False, 'enabled_state': False},
            'minimum': datetime.date.min,
            'maximum': datetime.date.max,
            'min_use_current_date': False,
            'max_use_current_date': False
        }

        self.type_attribs['DATETIME'] = {
            'mandt': {'check_state': False, 'enabled_state': True},
            'search': {'check_state': False, 'enabled_state': True},
            'unique': {'check_state': False, 'enabled_state': False},
            'index': {'check_state': False, 'enabled_state': False},
            'minimum': datetime.datetime.min,
            'maximum': datetime.datetime.max,
            'min_use_current_datetime': False,
            'max_use_current_datetime': False}

        self.type_attribs['LOOKUP'] = {
            'mandt': {'check_state': False, 'enabled_state': True},
            'search': {'check_state': True, 'enabled_state': True},
            'unique': {'check_state': False, 'enabled_state': False},
            'index': {'check_state': False, 'enabled_state': False}
        }

        self.type_attribs['GEOMETRY'] = {
            'mandt': {'check_state': False, 'enabled_state': False},
            'search': {'check_state': False, 'enabled_state': False},
            'unique': {'check_state': False, 'enabled_state': False},
            'index': {'check_state': False, 'enabled_state': False}
            }

        self.type_attribs['BOOL'] = {
            'mandt': {'check_state': False, 'enabled_state': False},
            'search': {'check_state': False, 'enabled_state': False},
            'unique': {'check_state': False, 'enabled_state': False},
            'index': {'check_state': False, 'enabled_state': False}
        }
        self.type_attribs['PERCENT'] = {
            'mandt': {'check_state': False, 'enabled_state': False},
            'search': {'check_state': False, 'enabled_state': True},
            'unique': {'check_state': False, 'enabled_state': False},
            'index': {'check_state': False, 'enabled_state': False}
        }

        self.type_attribs['ADMIN_SPATIAL_UNIT'] = {
            'mandt': {'check_state': False, 'enabled_state': True},
            'search': {'check_state': True, 'enabled_state': True},
            'unique': {'check_state': False, 'enabled_state': False},
            'index': {'check_state': False, 'enabled_state': False}
        }

        self.type_attribs['MULTIPLE_SELECT'] = {
            'mandt': {'check_state': False, 'enabled_state': True},
            'search': {'check_state': False, 'enabled_state': True},
            'unique': {'check_state': False, 'enabled_state': False},
            'index': {'check_state': False, 'enabled_state': False}
        }

        self.type_attribs['AUTO_GENERATED'] = {
            'mandt': {'check_state': False, 'enabled_state': True},
            'search': {'check_state': True, 'enabled_state': True},
            'unique': {'check_state': True, 'enabled_state': True},
            'index': {'check_state': True, 'enabled_state': True},
            'prefix_source': '', 'columns': [], 'column_separators': [],
            'leading_zero': '', 'separator': '',
            'disable_auto_increment': False, 'enable_editing': False,
            'hide_prefix': False, 'prop_set': True}

        self.type_attribs['EXPRESSION'] = {
            'mandt': {'check_state': False, 'enabled_state': True},
            'search': {'check_state': False, 'enabled_state': True},
            'unique': {'check_state': False, 'enabled_state': True},
            'index': {'check_state': False, 'enabled_state': True}
        }

    def init_controls(self):
        """
        Initialize GUI controls default state when the dialog window is opened.
        """
        self.populate_data_type_cbo()

        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.accept)
        self.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.cancel)

    def populate_data_type_cbo(self):
        """
        Fills the data type combobox widget with BaseColumn type names.
        """
        self.appearanceColumnDataType.clear()

        appearance_dictionary = {
            'text': ['none', 'numbers', 'ex.*', 'url'],
            'integer': ['none', 'thousands-sep'],
            'decimal': ['none', 'thousands-sep'],
            'date': ['none', 'no-calendar', 'month-year', 'year', 'coptic', 'ethiopian', 'islamic', 'bikram-sambat',
                     'myanmar', 'persian'],
            'select_one': ['minimal', 'quick', 'autocomplete', 'columns-pack', 'columns'],
            'select_multiple': ['none'],
            'select_one_from_file': ['none'],
            'geopoint': ['none', 'maps', 'placement-map'],
            'geotrace': ['none'],
            'geoshape': ['none']
        }

        col_type = self._column_type_info(self.column)

        if col_type == 'VARCHAR':
            for appearance in appearance_dictionary['text']:
                self.appearanceColumnDataType.addItem(appearance)

        elif col_type == 'INT':
            for appearance in appearance_dictionary['integer']:
                self.appearanceColumnDataType.addItem(appearance)

        elif col_type == 'DOUBLE':
            for appearance in appearance_dictionary['decimal']:
                self.appearanceColumnDataType.addItem(appearance)

        elif col_type == 'DATE':
            for appearance in appearance_dictionary['date']:
                self.appearanceColumnDataType.addItem(appearance)

        elif col_type == 'LOOKUP':
            for appearance in appearance_dictionary['select_one']:
                self.appearanceColumnDataType.addItem(appearance)

        elif col_type == 'MULTIPLE_SELECT':
            for appearance in appearance_dictionary['select_multiple']:
                self.appearanceColumnDataType.addItem(appearance)

        elif col_type == 'GEOMETRY':
            for appearance in appearance_dictionary['geopoint']:
                self.appearanceColumnDataType.addItem(appearance)

        if self.appearanceColumnDataType.count() > 0:
            self.appearanceColumnDataType.setCurrentIndex(0)

    def change_data_type(self, index):
        """
        Called by type combobox when you select a different data type.
        """
        text = self.appearanceColumnDataType.itemText(index)
        col_cls = BaseColumn.types_by_display_name().get(text, None)
        if col_cls is None:
            return

        ti = col_cls.TYPE_INFO
        if ti not in self.type_attribs:
            msg = self.tr('Column type attributes could not be found.')
            self.notice_bar.clear()
            self.notice_bar.insertErrorNotification(msg)
            return

        self.type_info = ti
        opts = self.type_attribs[ti]
        self.set_optionals(opts)

    def set_optionals(self, opts):
        """
        Enable/disables form controls based on selected
        column data type attributes
        param opts: Dictionary type properties of selected column
        type opts: dict
        """
        pass

    def _column_type_info(self, column):
        """
        Check if column has TYPE_INFO attribute
        :param column: Entity column object
        :return: Column type. Otherwise None
        :rtype: String or None
        """
        try:
            return column.TYPE_INFO
        except AttributeError:
            return None

    def cancel(self):
        self.done(0)

    def accept(self):
        self.done(1)
