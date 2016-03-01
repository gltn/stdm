# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : column_editor
Description          : STDM profile configuration wizard
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

from datetime import (
    date,
    datetime
)

class ColumnEditor(QDialog, Ui_ColumnEditor):
    def __init__(self, parent, **kwargs):
        QDialog.__init__(self, parent)
        self.form_parent = parent
        self.FK_EXCLUDE = [u'supporting_document', u'admin_spatial_unit_set']
        self.EX_TYPE_INFO =  ['SUPPORTING_DOCUMENT', 'SOCIAL_TENURE', 
                'ADMINISTRATIVE_SPATIAL_UNIT', 'ENTITY_SUPPORTING_DOCUMENT',
                'VALUE_LIST']
        self.setupUi(self)
        self.dtypes = {}

        self.column  = kwargs.get('column', None)
        self.entity  = kwargs.get('entity', None)
        self.profile = kwargs.get('profile', None)

        self.type_info = ''
        
        self.type_attribs = {}
        self.init_type_attribs()

        self.form_fields = {}
        self.init_form_fields()

        self.fk_entities     = []
        self.lookup_entities = []

        # the current entity should not be part of the foreign key parent table, add it to the exclusion list
        self.FK_EXCLUDE.append(self.entity.short_name)

        self.cboDataType.currentIndexChanged.connect(self.change_data_type)

        #self.btnTableList.clicked.connect(self.lookupDialog)
        self.btnColProp.clicked.connect(self.data_type_property)

        self.type_names = \
                [str(name) for name in BaseColumn.types_by_display_name().keys()]

        self.init_controls()

    def init_controls(self):
        self.popuplate_type_cbo()

        name_regex = QtCore.QRegExp('^[a-z][a-z0-9_]*$')
        name_validator = QtGui.QRegExpValidator(name_regex)
        self.edtColName.setValidator(name_validator)
        # if this an edit
        if self.column:
            self.column_to_form(self.column)

        self.edtColName.setFocus()

    def _get_cbo_id(self, types, text):
        for i, c in enumerate(types):
            if c == text:
                return i

    def column_to_form(self, column):
        self.edtColName.setText(column.name)
        self.edtColDesc.setText(column.description)
        self.edtUserTip.setText(column.user_tip)
        self.cbMandt.setCheckState(self.bool_to_check(column.mandatory))
        self.cbSearch.setCheckState(self.bool_to_check(column.searchable))
        self.cbUnique.setCheckState(self.bool_to_check(column.unique))
        self.cbIndex.setCheckState(self.bool_to_check(column.index))

        #cbo_id = self._get_cbo_id(self.type_names, column.display_name())
        #self.cboDataType.setCurrentIndex(cbo_id)

        self.cboDataType.setCurrentIndex( \
                self.cboDataType.findText(column.display_name()))

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

        #self.form_fields['entity_relation'] = {}

    def bool_to_check(self, state):
        if state:
            return Qt.Checked
        else:
            return Qt.Unchecked

    def init_form_fields(self):
        self.form_fields['colname'] = ''
        self.form_fields['value']  = None
        self.form_fields['mandt']  = False
        self.form_fields['search'] = False
        self.form_fields['unique'] = False
        self.form_fields['index']  = False
        self.form_fields['minimum'] = self.type_attribs.get('minimum', 0) 
        self.form_fields['maximum'] = self.type_attribs.get('maximum', 0)
        self.form_fields['srid'] = self.type_attribs.get('srid', "Select...")
        self.form_fields['geom_type'] = self.type_attribs.get('geom_type', 0)

        self.form_fields['entity_relation'] = \
                self.type_attribs.get('entity_relation', None)
		
    def init_type_attribs(self):
        self.type_attribs['VARCHAR'] = {
                'mandt':True,'search': True,
                'unique': False, 'index': True,
                'property': self.varchar_property }

        self.type_attribs['BIGINT'] = {
                'mandt':True, 'search': True,
                'unique': True, 'index': True,
                'minimum':0, 'maximum':0,
                'property':self.bigint_property }

        self.type_attribs['TEXT'] = {'mandt':False, 'search': False, 
                'unique': False, 'index': False } 

        self.type_attribs['DOUBLE' ] = {'mandt':True, 'search': True, 
                'unique': False, 'index': False, 
                'minimum':0.0, 'maximum':0.0,
                'property':self.double_property }

        self.type_attribs['DATE'] =  {'mandt':True, 'search': True,
                'unique': False, 'index': True,
                'minimum':QtCore.QDate.currentDate(),
                'maximum':QtCore.QDate.currentDate(),
                'property':self.date_property }
               
        self.type_attribs['DATETIME' ] = {'mandt':True, 'search': False,
                'unique': False, 'index': False,
                'minimum':QtCore.QDateTime.currentDateTime(),
                'maximum':QtCore.QDateTime.currentDateTime(),
                'property':self.dtime_property }

        self.type_attribs['FOREIGN_KEY' ] = {'mandt':True, 'search': False, 
                'unique': False, 'index': False,
                'entity_relation':None,
                'property':self.fk_property, 'prop_set':False }

        self.type_attribs['LOOKUP' ] = {'mandt':True, 'search': False,
                'unique': False, 'index': False,
                'property':self.lookup_property, 'prop_set':False }

        self.type_attribs['GEOMETRY' ] ={'mandt':False, 'search': False, 
                'unique': False, 'index': False,
                'srid':0, 'geom_type':0,
                'property':self.geometry_property, 'prop_set':False }

        self.type_attribs['ADMIN_SPATIAL_UNIT' ] ={'mandt':True, 'search': False,
                'unique': False, 'index': False }

        self.type_attribs['MULTIPLE_SELECT' ] ={'mandt':True, 'search': False, 
                'unique': False, 'index': False,
                'property':self.lookup_property, 'prop_set':False }
	
    def data_type_property(self):
        self.type_attribs[self.current_type_info()]['property']()

    def varchar_property(self):
        editor = VarcharProperty(self, self.form_fields)
        result = editor.exec_()
        if result == 1:
            self.form_fields['maximum'] = editor.max_len()

    def bigint_property(self):
        editor = BigintProperty(self, self.form_fields)
        result = editor.exec_()
        if result == 1:
            self.form_fields['minimum'] = editor.min_val()
            self.form_fields['maximum'] = editor.max_val()

    def double_property(self):
        editor = DoubleProperty(self, self.form_fields)
        result = editor.exec_()
        if result == 1:
            self.form_fields['minimum'] = editor.min_val()
            self.form_fields['maximum'] = editor.max_val()

    def date_property(self):
        editor = DateProperty(self, self.form_fields)
        result = editor.exec_()
        if result == 1:
            self.form_fields['minimum'] = editor.min_val()
            self.form_fields['maximum'] = editor.max_val()

    def dtime_property(self):
        editor = DTimeProperty(self, self.form_fields)
        result = editor.exec_()
        if result == 1:
            self.form_fields['minimum'] = editor.min_val()
            self.form_fields['maximum'] = editor.max_val()

    def geometry_property(self):
        editor = GeometryProperty(self, self.form_fields)
        result = editor.exec_()
        if result == 1:
            self.form_fields['srid'] = editor.coord_sys()
            self.form_fields['geom_type'] = editor.geom_type()
            self.type_attribs[self.type_info]['prop_set'] = True

    def fk_property(self):
        if len(self.edtColName.displayText())==0:
            self.error_message("Please enter column name!")
            return

        # filter list of lookup tables, don't show internal 
        # tables in list of lookups
        fk_ent = [entity for entity in self.profile.entities.items() \
                if entity[1].TYPE_INFO not in self.EX_TYPE_INFO]

        fk_ent = [entity for entity in fk_ent if unicode(entity[0]) \
                not in self.FK_EXCLUDE]

        relation = {}
        relation['entity_relation'] = self.form_fields['entity_relation']
        relation['fk_entities'] = fk_ent
        relation['profile'] = self.profile
        relation['entity'] = self.entity
        relation['column_name'] = unicode(self.edtColName.text())

        editor = FKProperty(self, relation)
        result = editor.exec_()
        if result == 1:
            self.form_fields['entity_relation'] = editor.entity_relation()
            self.type_attribs[self.type_info]['prop_set'] = True

    def lookup_property(self):
       editor = LookupProperty(self, profile=self.profile) 
       result = editor.exec_()
       if result == 1:
           self.form_fields['entity_relation'] = editor.entity_relation()
           self.type_attribs[self.type_info]['prop_set'] = True

    def create_column(self):
        column = None
        if self.type_info:
            if self.valid_type_properties(self.type_info):
                column = BaseColumn.registered_types[self.type_info] \
                        (self.form_fields['colname'], self.entity,
                                **self.form_fields)
            else:
                self.error_message('Please set column properties.')
        else:
            raise "No type to create!"

        return column

    def valid_type_properties(self, ti):
        if not self.type_attribs[ti].has_key('prop_set'):
            return True

        return self.type_attribs[ti]['prop_set']

    def property_by_name(self, ti, name):
        try:
                return self.dtype_property(ti)['property'][name]
        except:
                return None

    def load_entities(self, cbox, entities):
        cbox.clear()
        cbox.insertItems(0, [name[0] for name in entities])
        cbox.setCurrentIndex(0)

    def popuplate_type_cbo(self):
        self.cboDataType.clear()
        self.cboDataType.insertItems(0, BaseColumn.types_by_display_name().keys())
        self.cboDataType.setCurrentIndex(0)

    def change_data_type(self):
        ti = self.current_type_info()
        if ti=='':
            return
        self.btnColProp.setEnabled(self.type_attribs[ti].has_key('property'))
        self.type_info = ti
        opts = self.type_attribs[ti]
        self.set_optionals(opts)
        self.set_min_max_defaults(ti)

    def set_optionals(self, opts):
        self.cbMandt.setEnabled(opts['mandt'])
        self.cbSearch.setEnabled(opts['search'])
        self.cbUnique.setEnabled(opts['unique'])
        self.cbIndex.setEnabled(opts['index'])

    def set_min_max_defaults(self, type_info):
        '''
        sets the form defaults(minimum/maximum) from the column property
        dictionary

        '''
        self.form_fields['minimum'] = \
                self.type_attribs[type_info].get('minimum', 0)

        self.form_fields['maximum'] = \
                self.type_attribs[type_info].get('maximum', 0)

    def current_type_info(self):
        text = self.cboDataType.itemText(self.cboDataType.currentIndex())
        try:
                return BaseColumn.types_by_display_name()[text].TYPE_INFO
        except:
                return ''

    def append_attr(self, column_fields, attr, value):
        try:
                column_fields[attr] = \
                        self.property_by_name(self.current_type_info(), attr)
                return column_fields
        except:
                return column_fields

    def fill_form_data(self):
        self.form_fields['colname']    = self.edtColName.text()
        self.form_fields['description']= self.edtColDesc.text()
        self.form_fields['index']      = self.cbIndex.isChecked()
        self.form_fields['mandatory']  = self.cbMandt.isChecked()
        self.form_fields['searchable'] = self.cbSearch.isChecked()
        self.form_fields['unique']     = self.cbUnique.isChecked()
        self.form_fields['user_tip']   = self.edtUserTip.text()

    def error_message(self, Message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(QApplication.translate("AttributeEditor", "STDM"))
        msg.setText(Message)
        msg.exec_()  

    def accept(self):
        col_name = unicode(self.edtColName.text()).strip()

        # column name is not empty
        if len(col_name)==0:
            self.error_message('Please enter the column name!')
            return False

        # if column is initialized, this is an edit
        # delete old one then add a new one
        if self.column:
            self.entity.remove_column(self.column.name)

        # check if another column with the same name exist in the current entity
        if self.entity.columns.has_key(col_name):
            self.error_message(QApplication.translate("ColumnEditor",
                "Column with the same name already exist!"))
            return 

        self.fill_form_data()
        self.column = self.create_column()

        if self.column:
            self.entity.add_column(self.column)
            self.done(1)
        else:
            return

    def rejectAct(self):
        self.done(0)

