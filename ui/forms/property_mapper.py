"""
/***************************************************************************
Name                 : Generic application for forms
Description          : forms generator functions
Date                 : 30/June/2013
copyright            : (C) 2014 by UN-Habitat and implementing partners.
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
from collections import OrderedDict
from PyQt4.QtGui import QMessageBox

from lookup_dlg import LookupModeller
from attribute_datatype import AttributePropretyType
from .widgets import WidgetCollection

from stdm.ui.forms.attribute_formatters import AttributeFormatters
from stdm.data.config_utils import foreign_key_table_reference
from stdm.utils import *
from stdm.data import STDMDb
from stdm.ui.stdmdialog import DeclareMapping

class TypePropertyMapper(object):
    def __init__(self, model = None):
        """ Class to read and match the datatype to respective control on the form"""
        self._modeller = LookupModeller()
        self._model = model
        self._mapper = DeclareMapping.instance()
        self._attribute_mapper = AttributePropretyType(self._model)
        self._attr = self._attribute_mapper.attribute_type()
        self.widgetList = OrderedDict()
        self.hideGUID()

    def hideGUID(self):
        try:
            for keys in self._attr.keys():
                if keys == 'id':
                    self._attr.pop(keys)
        except KeyError as ex:
            raise ex.message

    def widget(self):
        isLookup = False
        lk_items = None
        self.formatters = None
        widget_collection = WidgetCollection()
        for attr, attr_data_type in self._attr.iteritems():
            if attr_data_type[1]:
                attr_data_type[0] = 'choice'
                lkModel = self._modeller.lookupModel(attr_data_type[1])
                lk_items = self.lookup_items(lkModel)
                if lk_items:
                    isLookup = True
            control_widget = widget_collection.widget_control_type(attr_data_type[0])
            if attr_data_type[0] == 'foreign key':
                source_table = foreign_key_table_reference(self._model)
                self.formatters = AttributeFormatters(attr, source_table[0])
                self.formatters.set_display_name(source_table[1])
            self.widgetList[attr] = [control_widget, isLookup, lk_items, self.formatters]

    def setProperty(self):
            self.widget()
            return self.widgetList

    def user_lookup_options(self, db_model):
        """
        Fetch lookup values from the DB.
        """
        lkup_model = readComboSelections(db_model)
        return lkup_model

    def lookup_items(self, model):
        model_items = self.user_lookup_options(model)
        return model_items

    def clear_mapping(self):
        STDMDb.instance().session.rollback()

    def display_mapping(self):
        #use the mapped table properties
        self._mapper.tableMapping(self._model)
