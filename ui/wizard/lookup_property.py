# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : lookup_property
Description          : Set properties for Lookup data type
Date                 : 02/January/2016
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
from PyQt4.QtGui import *
from PyQt4.QtCore import *

from ui_lookup_property import Ui_LookupProperty
from stdm.data.configuration.entity_relation import EntityRelation
from create_lookup import LookupEditor

class LookupProperty(QDialog, Ui_LookupProperty):
    """
    Editor to create/edit Lookup column property
    """
    def __init__(self, parent, entity_relation, profile=None):
        """
        :param parent: Owner of this form
        :type parent: QWidget
        :param entity_relation: EntityRelation object
        :type entity_relation: EntityRelation
        :param profile: Current configuration profile
        :type profile: Profile
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self._entity_relation = entity_relation
        self._lookup_name = ''
        self._profile = profile

        self.init_gui()

    def init_gui(self):
        """
        Initializes form widgets
        """
        self.edtNewlookup.clicked.connect(self.create_lookup)
        lookup_names = self.lookup_entities()
        self.fill_lookup_cbo(lookup_names)
        if self._entity_relation:
            self._lookup_name = self._entity_relation.parent.short_name
            self.cboPrimaryEntity.setCurrentIndex( \
                    self.cboPrimaryEntity.findText(self._lookup_name))

    def create_lookup(self):
        """
        Creates a new lookup entity, insert it to the current lookup combobox 
        and make it the current lookup
        """
        editor = LookupEditor(self, self._profile)
        result = editor.exec_()
        if result == 1:
            name = editor.lookup.short_name
            names = []
            names.append(name)
            self.cboPrimaryEntity.insertItems(0, names)
            self.cboPrimaryEntity.setCurrentIndex( \
                    self.cboPrimaryEntity.findText(name))
            
    def lookup_entities(self):
        """
        Returns a list of ValueList (a.k.a lookup) names in the current profile
        rtype: list
        """
        names = []
        for value_list in self._profile.value_lists():
            names.append(value_list.short_name)
        return names

    def fill_lookup_cbo(self, names):
        """
        Fill combobox with entity names
        :param names: List of entity names
        """
        self.cboPrimaryEntity.clear()
        self.cboPrimaryEntity.insertItems(0, names)
        self.cboPrimaryEntity.setCurrentIndex(0)

    def add_values(self):
        """
        Construct an EntityRelation instance
        """
        lookup_name = unicode(self.cboPrimaryEntity.currentText())
        self._lookup_name = lookup_name

        er_fields = {}
        er_fields['parent'] = lookup_name
        er_fields['parent_column'] = None
        er_fields['display_columns'] = []
        er_fields['child'] = None
        er_fields['child_column'] = None
        self._entity_relation = EntityRelation(self._profile, **er_fields)

    def entity_relation(self):
        """
        Returns an instance of EntityRelation
        rtype: EntityRelation
        """
        return self._entity_relation
	    
    def accept(self):
        self.add_values()
        self.done(1)

    def reject(self):
        self.done(0)
