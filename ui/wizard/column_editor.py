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

import os
import logging
import datetime
import collections

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from collections import OrderedDict

from ui_column_editor import Ui_ColumnEditor

from stdm.data.configuration.columns import BaseColumn
from stdm.data.configuration.entity_relation import EntityRelation

from varchar_property import VarcharProperty
from bigint_property import BigintProperty
from double_property import DoubleProperty
from date_property import DateProperty
from dtime_property import DTimeProperty
from geometry_property import GeometryProperty
from fk_property import FKProperty
from lookup_property import LookupProperty
from multi_select_property import MultiSelectProperty
from code_property import CodeProperty

from stdm.ui.notification import NotificationBar, INFORMATION

LOGGER = logging.getLogger('stdm')
LOGGER.setLevel(logging.DEBUG)

RESERVED_KEYWORDS = ['id', 'documents', 'spatial_unit', 'supporting_document',
        'social_tenure', 'social_tenure_relationship','geometry']

class ColumnEditor(QDialog, Ui_ColumnEditor):
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
        """
        
        self.form_parent = kwargs.get('parent', self)
        self.column  = kwargs.get('column', None)
        self.entity  = kwargs.get('entity', None)
        self.profile = kwargs.get('profile', None)
        self.in_db = kwargs.get('in_db', False)
        self.is_new = kwargs.get('is_new', True)

        QDialog.__init__(self, self.form_parent)

        self.FK_EXCLUDE = [u'supporting_document', u'admin_spatial_unit_set']

        self.EX_TYPE_INFO =  ['SUPPORTING_DOCUMENT', 'SOCIAL_TENURE', 
                'ADMINISTRATIVE_SPATIAL_UNIT', 'ENTITY_SUPPORTING_DOCUMENT',
                'VALUE_LIST', 'ASSOCIATION_ENTITY', 'AUTO_GENERATED']

        self.setupUi(self)
        self.dtypes = {}

        self.type_info = ''
        
        # dictionary to hold default attributes for each data type
        self.type_attribs = {}
        self.init_type_attribs()

        # dictionary to act as a work area for the form fields.
        self.form_fields = {}
        self.init_form_fields()

        self.fk_entities     = []
        self.lookup_entities = []

        if self.is_new:
            self.prop_set = None
        else:
            self.prop_set = True

        # the current entity should not be part of the foreign key parent table,
        # add it to the exclusion list
        self.FK_EXCLUDE.append(self.entity.short_name)

        self.type_names = \
                [unicode(name) for name in BaseColumn.types_by_display_name().keys()]

        self.cboDataType.currentIndexChanged.connect(self.change_data_type)
        self.btnColProp.clicked.connect(self.data_type_property)
        self.edtColName.textChanged.connect(self.validate_text)

        self.notice_bar = NotificationBar(self.notif_bar)
        self.init_controls()

    def show_notification(self, message):
        """
        Shows a warning notification bar message.
        :param message: The message of the notification.
        :type message: String
        """
        msg = self.tr(message)
        self.notice_bar.clear()
        self.notice_bar.insertErrorNotification(msg)

    def init_controls(self):
        """
        Initialize GUI controls default state when the dialog window is opened.
        """
        self.populate_data_type_cbo()
        #if self.column:
        if not self.column is None:
            self.column_to_form(self.column)
            self.column_to_wa(self.column)

        self.edtColName.setFocus()

        self.edtColName.setEnabled(not self.in_db)

        self.cboDataType.setEnabled(not self.in_db)

        self.buttonBox.button(QtGui.QDialogButtonBox.Ok).clicked.connect(self.accept)
        self.buttonBox.button(QtGui.QDialogButtonBox.Cancel).clicked.connect(self.cancel)

    def validate_text(self, text):
        """
        Validates and updates the entered text if necessary.
        Spaces are replaced by _ and capital letters are replaced by small.
        :param text: The text entered
        :type text: String
        """
        text_edit = self.sender()
        cursor_position = text_edit.cursorPosition()
        text_edit.setValidator(None)
        if len(text) == 0:
            return

        name_regex = QtCore.QRegExp('^(?=.{0,40}$)[ _a-zA-Z][a-zA-Z0-9_ ]*$')
        name_validator = QtGui.QRegExpValidator(name_regex)
        text_edit.setValidator(name_validator)
        QApplication.processEvents()
        last_character = text[-1:]

        state = name_validator.validate(text, text.index(last_character))[0]
        if state != QValidator.Acceptable:
            self.show_notification('"{}" is not allowed at this position.'.
                format(last_character)
            )
            text = text[:-1]
        else:
            # fix caps, _, and spaces
            if last_character.isupper():
                text = text.lower()
            if last_character == ' ':
                text = text.replace(' ', '_')
            if len(text) > 1:
                if text[0] == ' ' or text[0] == '_':
                    text = text[1:]
                text = text.replace(' ', '_').lower()

        self.blockSignals(True)
        text_edit.setText(text)
        text_edit.setCursorPosition(cursor_position)
        self.blockSignals(False)
        text_edit.setValidator(None)

    def column_to_form(self, column):
        """
        Initializes form controls with Column data.
        :param column: BaseColumn instance
        :type column: BaseColumn
        """
        text = column.display_name()
        self.cboDataType.setCurrentIndex(self.cboDataType.findText(text))

        self.edtColName.setText(column.name)
        self.edtColDesc.setText(column.description)
        self.edtUserTip.setText(column.user_tip)
        self.cbMandt.setChecked(column.mandatory)
        self.cbSearch.setCheckState(self.bool_to_check(column.searchable))
        self.cbUnique.setCheckState(self.bool_to_check(column.unique))
        self.cbIndex.setCheckState(self.bool_to_check(column.index))

        ti = self.current_type_info()
        ps = self.type_attribs[ti].get('prop_set', None)
        if ps is not None:
            self.type_attribs[ti]['prop_set']= self.prop_set

    def column_to_wa(self, column):
        """
        Initialize 'work area' form_fields with column data.
        :param column: BaseColumn instance
        :type column: BaseColumn
        """
        if column is not None:
            self.form_fields['colname'] = column.name
            self.form_fields['value']  = None
            self.form_fields['mandt']  = column.mandatory
            self.form_fields['search'] = column.searchable
            self.form_fields['unique'] = column.unique
            self.form_fields['index']  = column.index

            if hasattr(column, 'minimum'):
                self.form_fields['minimum'] = column.minimum
                self.form_fields['maximum'] = column.maximum

            if hasattr(column, 'srid'):
                self.form_fields['srid'] = column.srid
                self.form_fields['geom_type'] = column.geom_type

            if hasattr(column, 'entity_relation'):
                self.form_fields['entity_relation'] = column.entity_relation

            if hasattr(column, 'association'):
                self.form_fields['first_parent'] = column.association.first_parent
                self.form_fields['second_parent'] = column.association.second_parent

            if hasattr(column, 'min_use_current_date'):
                self.form_fields['min_use_current_date'] = column.min_use_current_date
                self.form_fields['max_use_current_date'] = column.max_use_current_date

            if hasattr(column, 'min_use_current_datetime'):
                self.form_fields['min_use_current_datetime'] = \
                        column.min_use_current_datetime
                self.form_fields['max_use_current_datetime'] = \
                        column.max_use_current_datetime

            if hasattr(column, 'prefix_source'):
                self.form_fields['prefix_source'] = column.prefix_source
                self.form_fields['leading_zero'] = column.leading_zero
                self.form_fields['separator'] = column.separator

            # Decimal properties
            if hasattr(column, 'precision'):
                self.form_fields['precision'] = column.precision
                self.form_fields['scale'] = column.scale

    def bool_to_check(self, state):
        """
        Converts a boolean to a Qt checkstate.
        :param state: True/False
        :type state: boolean
        :rtype: Qt.CheckState
        """
        if state:
            return Qt.Checked
        else:
            return Qt.Unchecked

    def init_form_fields(self):
        """
        Initializes work area 'form_fields' dictionary with default values.
        Used when creating a new column.
        """
        none = QApplication.translate('CodeProperty', 'None')
        self.form_fields['colname'] = ''
        self.form_fields['value']  = None
        self.form_fields['mandt']  = False
        self.form_fields['search'] = False
        self.form_fields['unique'] = False
        self.form_fields['index']  = False
        self.form_fields['minimum'] = self.type_attribs.get('minimum', 0) 
        self.form_fields['maximum'] = self.type_attribs.get('maximum', 0)
        self.form_fields['srid'] = self.type_attribs.get('srid', "")
        self.form_fields['geom_type'] = self.type_attribs.get('geom_type', 0)
        self.form_fields['in_db'] = self.in_db
        self.form_fields['prefix_source'] = self.type_attribs.get(
            'prefix_source', none
        )
        self.form_fields['leading_zero'] = self.type_attribs.get(
            'leading_zero', ''
        )
        self.form_fields['separator'] = self.type_attribs.get(
            'separator', ''
        )

        self.form_fields['precision'] = self.type_attribs.get(
            'precision', 18
        )
        self.form_fields['scale'] = self.type_attribs.get(
            'scale', 6
        )

        self.form_fields['entity_relation'] = \
                self.type_attribs['FOREIGN_KEY'].get('entity_relation', None)

        self.form_fields['entity_relation'] = \
                self.type_attribs['LOOKUP'].get('entity_relation', None)

        self.form_fields['first_parent'] = \
                self.type_attribs['MULTIPLE_SELECT'].get('first_parent', None)

        self.form_fields['second_parent'] = \
                self.type_attribs['MULTIPLE_SELECT'].get('second_parent', None)

        self.form_fields['min_use_current_date'] = \
                self.type_attribs['DATE'].get('min_use_current_date', None)

        self.form_fields['max_use_current_date'] = \
                self.type_attribs['DATE'].get('max_use_current_date', None)

        self.form_fields['min_use_current_datetime'] = \
                self.type_attribs['DATETIME'].get('min_use_current_datetime', None)

        self.form_fields['max_use_current_datetime'] = \
                self.type_attribs['DATETIME'].get('max_use_current_datetime', None)


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
                'mandt':{'check_state':False, 'enabled_state':True},
                'search':{'check_state':True, 'enabled_state':True},
                'unique':{'check_state':False, 'enabled_state':True},
                'index':{'check_state':False, 'enabled_state':True},
                'maximum':30,'property': self.varchar_property }

        self.type_attribs['INT'] = {
                'mandt':{'check_state':False, 'enabled_state':True},
                'search':{'check_state':True, 'enabled_state':True},
                'unique':{'check_state':False, 'enabled_state':True},
                'index':{'check_state':False, 'enabled_state':False},
                'minimum':0, 'maximum':0,
                'property':self.bigint_property }

        self.type_attribs['TEXT'] = {
                'mandt':{'check_state':False, 'enabled_state':True},
                'search':{'check_state':False, 'enabled_state':False},
                'unique':{'check_state':False, 'enabled_state':False},
                'index':{'check_state':False, 'enabled_state':False},
                } 

        self.type_attribs['DOUBLE' ] = {
                'mandt':{'check_state':False, 'enabled_state':True},
                'search':{'check_state':True, 'enabled_state':True},
                'unique':{'check_state':False, 'enabled_state':True},
                'index':{'check_state':False, 'enabled_state':True},
                'minimum':0.0, 'maximum':0.0,
                'precision': 18, 'scale': 6,
                'property':self.double_property }

        self.type_attribs['DATE'] =  {
                'mandt':{'check_state':False, 'enabled_state':True},
                'search':{'check_state':False, 'enabled_state':True},
                'unique':{'check_state':False, 'enabled_state':False},
                'index':{'check_state':False, 'enabled_state':False},
                'minimum':datetime.date.min,
                'maximum':datetime.date.max,
                'min_use_current_date':False,
                'max_use_current_date':False,
                'property':self.date_property }
               
        self.type_attribs['DATETIME'] = {
                'mandt':{'check_state':False, 'enabled_state':True},
                'search':{'check_state':False, 'enabled_state':True},
                'unique':{'check_state':False, 'enabled_state':False},
                'index':{'check_state':False, 'enabled_state':False},
                'minimum':datetime.datetime.min,
                'maximum':datetime.datetime.max,
                'min_use_current_datetime':False,
                'max_use_current_datetime':False,
                'property':self.dtime_property }

        self.type_attribs['FOREIGN_KEY'] = {
                'mandt':{'check_state':False, 'enabled_state':True},
                'search':{'check_state':False, 'enabled_state':False},
                'unique':{'check_state':False, 'enabled_state':False},
                'index':{'check_state':False, 'enabled_state':False},
                'entity_relation':None,
                'property':self.fk_property, 'prop_set':False }

        self.type_attribs['LOOKUP'] = {
                'mandt':{'check_state':False, 'enabled_state':True},
                'search':{'check_state':True, 'enabled_state':True},
                'unique':{'check_state':False, 'enabled_state':False},
                'index':{'check_state':False, 'enabled_state':False},
                'entity_relation':{},
                'property':self.lookup_property, 'prop_set':False }

        self.type_attribs['GEOMETRY'] = {
                'mandt':{'check_state':False, 'enabled_state':False},
                'search':{'check_state':False, 'enabled_state':False},
                'unique':{'check_state':True, 'enabled_state':False},
                'index':{'check_state':True, 'enabled_state':False},
                'srid':"", 'geom_type':0,
                'property':self.geometry_property, 'prop_set':False }

        self.type_attribs['BOOL'] = {
                'mandt':{'check_state':False, 'enabled_state':False},
                'search':{'check_state':False, 'enabled_state':False},
                'unique':{'check_state':False, 'enabled_state':False},
                'index':{'check_state':False, 'enabled_state':False}
                }
        self.type_attribs['PERCENT'] = {
            'mandt': {'check_state': False, 'enabled_state': False},
            'search': {'check_state': False, 'enabled_state': True},
            'unique': {'check_state': False, 'enabled_state': False},
            'index': {'check_state': False, 'enabled_state': False}
        }

        self.type_attribs['ADMIN_SPATIAL_UNIT'] = {
                'mandt':{'check_state':False, 'enabled_state':True},
                'search':{'check_state':True, 'enabled_state':True},
                'unique':{'check_state':False, 'enabled_state':False},
                'index':{'check_state':False, 'enabled_state':False},
                'entity_relation':None}

        self.type_attribs['MULTIPLE_SELECT'] = {
                'mandt':{'check_state':False, 'enabled_state':True},
                'search':{'check_state':False, 'enabled_state':True},
                'unique':{'check_state':False, 'enabled_state':False},
                'index':{'check_state':False, 'enabled_state':False},
                'first_parent':None, 'second_parent':self.entity,
                'property':self.multi_select_property, 'prop_set':False }

        self.type_attribs['AUTO_GENERATED'] = {
            'mandt': {'check_state': False, 'enabled_state': True},
            'search': {'check_state': True, 'enabled_state': True},
            'unique': {'check_state': True, 'enabled_state': False},
            'index': {'check_state': True, 'enabled_state': False},
            'prefix_source': '', 'leading_zero': '', 'separator':'',
            'property': self.code_property, 'prop_set': True}

    def data_type_property(self):
        """
        Executes the function assigned to the property attribute of 
        the current selected data type.
        """
        self.type_attribs[self.current_type_info()]['property']()

    def varchar_property(self):
        """
        Opens the property editor for the Varchar data type.
        If successful, set a minimum column in work area 'form fields'
        """
        editor = VarcharProperty(self, self.form_fields)
        result = editor.exec_()
        if result == 1:
            self.form_fields['maximum'] = editor.max_len()

    def bigint_property(self):
        """
        Opens a property editor for the BigInt data type.
        """
        editor = BigintProperty(self, self.form_fields)
        result = editor.exec_()
        if result == 1:
            self.form_fields['minimum'] = editor.min_val()
            self.form_fields['maximum'] = editor.max_val()

    def double_property(self):
        """
        Opens a property editor for the Double data type.
        """
        editor = DoubleProperty(self, self.form_fields)
        result = editor.exec_()
        if result == 1:
            self.form_fields['minimum'] = editor.min_val()
            self.form_fields['maximum'] = editor.max_val()

    def date_property(self):
        """
        Opens a property editor for the Date data type.
        """
        editor = DateProperty(self, self.form_fields)
        result = editor.exec_()
        if result == 1:
            self.form_fields['minimum'] = editor.min_val()
            self.form_fields['maximum'] = editor.max_val()
            self.form_fields['min_use_current_date'] = \
                    editor.min_use_current_date
            self.form_fields['max_use_current_date'] = \
                    editor.max_use_current_date

    def dtime_property(self):
        """
        Opens a property editor for the DateTime data type.
        """
        editor = DTimeProperty(self, self.form_fields)
        result = editor.exec_()
        if result == 1:
            self.form_fields['minimum'] = editor.min_val()
            self.form_fields['maximum'] = editor.max_val()
            self.form_fields['min_use_current_datetime'] = \
                    editor.min_use_current_datetime
            self.form_fields['max_use_current_datetime'] = \
                    editor.max_use_current_datetime

    def geometry_property(self):
        """
        Opens a property editor for the Geometry data type.
        If successful, set the srid(projection), geom_type (LINE, POLYGON...)
        and prop_set which is boolean flag to verify that all the geometry
        properties are set. 
        Constraint - If 'prop_set' is False column cannot be saved.
        """
        editor = GeometryProperty(self, self.form_fields)
        result = editor.exec_()
        if result == 1:
            self.form_fields['srid'] = editor.coord_sys()
            self.form_fields['geom_type'] = editor.geom_type()
            self.property_set()

    def admin_spatial_unit_property(self):
        """
        Sets entity relation property used when creating column of type
        ADMIN_SPATIAL_UNIT
        """
        er_fields = {}
        er_fields['parent'] = self.entity
        er_fields['parent_column'] = None
        er_fields['display_columns'] = []
        er_fields['child'] = None
        er_fields['child_column'] = None
        self.form_fields['entity_relation'] = EntityRelation(self.profile, **er_fields)

    def fk_property(self):
        """
        Opens a property editor for the ForeignKey data type.
        """
        if len(self.edtColName.displayText())==0:
            self.show_message("Please enter column name!")
            return

        # filter list of lookup tables, don't show internal 
        # tables in list of lookups
        fk_ent = [entity for entity in self.profile.entities.items() \
                if entity[1].TYPE_INFO not in self.EX_TYPE_INFO]

        fk_ent = [entity for entity in fk_ent if unicode(entity[0]) \
                not in self.FK_EXCLUDE]

        relation = {}
        relation['form_fields'] = self.form_fields
        relation['fk_entities'] = fk_ent
        relation['profile'] = self.profile
        relation['entity'] = self.entity
        relation['column_name'] = unicode(self.edtColName.text())

        editor = FKProperty(self, relation)
        result = editor.exec_()
        if result == 1:
            self.form_fields['entity_relation'] = editor.entity_relation()
            self.property_set()

    def lookup_property(self):
        """
        Opens a lookup type property editor
        """
        editor = LookupProperty(self, self.form_fields, profile=self.profile) 
        result = editor.exec_()
        if result == 1:
            self.form_fields['entity_relation'] = editor.entity_relation()
            self.property_set()

    def multi_select_property(self):
        """
        Opens a multi select property editor
        """
        if len(self.edtColName.displayText())==0:
           self.show_message("Please enter column name!")
           return
       
        editor = MultiSelectProperty(self, self.form_fields, self.entity, self.profile) 
        result = editor.exec_()
        if result == 1:
            self.form_fields['first_parent'] = editor.lookup()
            self.form_fields['second_parent'] = self.entity
            self.property_set()

    def code_property(self):
        """
        Opens the code data type property editor
        """
        editor = CodeProperty(self, self.form_fields, profile=self.profile)
        result = editor.exec_()
        if result == 1:
            self.form_fields['prefix_source'] = editor.prefix_source()
            self.form_fields['leading_zero'] = editor.leading_zero()
            self.form_fields['separator'] = editor.separator()
            self.property_set()

    def create_column(self):
        """
        Creates a new BaseColumn.
        """
        column = None

        if self.type_info <> "":
            if self.type_info == 'ADMIN_SPATIAL_UNIT':
                self.admin_spatial_unit_property()
                column = BaseColumn.registered_types[self.type_info] \
                        (self.form_fields['colname'], self.entity, **self.form_fields)
                return column

            if self.is_property_set(self.type_info):
                column = BaseColumn.registered_types[self.type_info] \
                        (self.form_fields['colname'], self.entity, 
                                self.form_fields['geom_type'],
                                self.entity, **self.form_fields)
            else:
                self.show_message(self.tr('Please set column properties.'))
                return
        else:
            raise self.tr("No type to create.")

        return column

    def property_set(self):
        self.prop_set = True
        self.type_attribs[self.current_type_info()]['prop_set'] = True

    def is_property_set(self, ti):
        """
        Checks if column property is set by reading the value of
        attribute 'prop_set'
        :param ti: Type info to check for prop set
        :type ti: BaseColumn.TYPE_INFO
        :rtype: boolean
        """
        return self.type_attribs[ti].get('prop_set', True)

    def property_by_name(self, ti, name):
        try:
            return self.dtype_property(ti)['property'][name]
        except:
            return None

    def populate_data_type_cbo(self):
        """
        Fills the data type combobox widget with BaseColumn type names
        """
        self.cboDataType.clear()
        for item in BaseColumn.types_by_display_name().keys():

            self.cboDataType.addItem(QApplication.translate('ColumnEditor', item))
        self.cboDataType.setCurrentIndex(0)

    def change_data_type(self, index):
        """
        Called by type combobox when you select a different data type.
        """
        text = self.cboDataType.itemText(index)
        ti = BaseColumn.types_by_display_name()[text].TYPE_INFO

        if ti not in self.type_attribs:
            msg = self.tr('Column type attributes could not be found.')
            self.notice_bar.clear()
            self.notice_bar.insertErrorNotification(msg)

            return

        self.btnColProp.setEnabled(self.type_attribs[ti].has_key('property'))
        self.type_info = ti
        opts = self.type_attribs[ti]
        self.set_optionals(opts)
        self.set_min_max_defaults(ti)

    def set_optionals(self, opts):
        """
        Enable/disables form controls based on selected 
        column data type attributes
        param opts: Dictionary type properties of selected column
        type opts: dict
        """
        self.cbMandt.setEnabled(opts['mandt']['enabled_state'])
        self.cbSearch.setEnabled(opts['search']['enabled_state'])
        self.cbUnique.setEnabled(opts['unique']['enabled_state'])
        self.cbIndex.setEnabled(opts['index']['enabled_state'])

        self.cbMandt.setCheckState(self.bool_to_check(opts['mandt']['check_state']))
        self.cbSearch.setCheckState(self.bool_to_check(opts['search']['check_state']))
        self.cbUnique.setCheckState(self.bool_to_check(opts['unique']['check_state']))
        self.cbIndex.setCheckState(self.bool_to_check(opts['index']['check_state']))

    def set_min_max_defaults(self, type_info):
        """
        sets the work area 'form_fields' default values (minimum/maximum)
        from the column's type attribute dictionary
        :param type_info: BaseColumn.TYPE_INFO
        :type type_info: str
        """
        self.form_fields['minimum'] = \
                self.type_attribs[type_info].get('minimum', 0)

        self.form_fields['maximum'] = \
                self.type_attribs[type_info].get('maximum', 0)

    def current_type_info(self):
        """
        Returns a TYPE_INFO of a data type
        :rtype: str
        """
        text = self.cboDataType.itemText(self.cboDataType.currentIndex())
        try:
            return BaseColumn.types_by_display_name()[text].TYPE_INFO
        except:
            return ''

    def fill_work_area(self):
        """
        Sets work area 'form_fields' with form control values
        """
        self.form_fields['colname'] = unicode(self.edtColName.text())
        self.form_fields['description'] = unicode(self.edtColDesc.text())
        self.form_fields['index'] = self.cbIndex.isChecked()
        self.form_fields['mandatory'] = self.cbMandt.isChecked()
        self.form_fields['searchable'] = self.cbSearch.isChecked()
        self.form_fields['unique'] = self.cbUnique.isChecked()
        self.form_fields['user_tip'] = unicode(self.edtUserTip.text())

    def show_message(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(QApplication.translate("AttributeEditor", "STDM"))
        msg.setText(message)
        msg.exec_()  

    def accept(self):
        col_name = unicode(self.edtColName.text()).strip()
        # column name is not empty
        if len(col_name)==0 or col_name == '_':
            self.show_message(self.tr('Please enter a valid column name.'))
            return False

        # check for STDM reserved keywords
        if col_name in RESERVED_KEYWORDS:
            self.show_message(
                self.tr(u"'{0}' is a reserved keyword used internally by STDM.\n"\
                "Please choose another column name.".format(col_name)) )
            return False

        new_column = self.make_column()

        if new_column is None:
            LOGGER.debug("Error creating column!")
            self.show_message('Unable to create column!')
            return False;

        if self.column is None:  # new column
            if self.duplicate_check(col_name):
                self.show_message(self.tr("Column with the same name already "
                "exist in this entity!"))
                return False

            self.entity.add_column(new_column)
            self.done(1)
        else:  # editing a column 
            self.column = new_column
            self.done(1)

    def cancel(self):
        self.done(0)

    def make_column(self):
        """
        Returns a newly created column
        :rtype: BaseColumn
        """
        self.fill_work_area()
        col = self.create_column()
        return col

    def duplicate_check(self, name):
        """
        Return True if we have a column in the current entity with same name
        as our new column
        :param col_name: column name
        :type col_name: str
        """
        # check if another column with the same name exist in the current entity
        if self.entity.columns.has_key(name):
            return True
        else:
            return False

    def rejectAct(self):
        self.done(0)

