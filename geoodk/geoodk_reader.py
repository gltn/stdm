"""
/***************************************************************************
Name                 : GeoODK Reader
Description          : class to read profile and entity details.
Date                 : 26/May/2017
copyright            : (C) 2017 by UN-Habitat and implementing partners.
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
from PyQt4.QtCore import QObject
from stdm.settings import current_profile
from collections import OrderedDict
class GeoODKReader():
    """
    Class to read entity info from profile and return the entity data
    """
    def __init__(self, entity):
        """

        """

        self.entity_name = None
        self.user_entity = entity
        self.entity_attributes = OrderedDict()
        self.lookup_attributes = OrderedDict()
        self.lookup =[]
        self.profile()

    def profile(self):
        """

        :return:
        """
        return current_profile()

    def user_entity_name(self):
        """

        :return:
        """
        return self.user_entity

    def set_user_entity_name(self, ent_name):
        """

        :param name:
        :return:
        """
        self.entity_name = self.profile().entity(ent_name).name
        self.user_entity_name()
        return self.entity_name


    def get_user_selected_entity(self):
        """
        Get user selected list of entities
        :param user_sel: string, list
        :return: string
        """
        self.entity_name = self.profile().entity(self.user_entity).name
        return self.entity_name

    def entity_object(self):
        """
        Get the entity object from the table name
        :return:
        """
        return self.profile().entity(self.user_entity)

    def entity_has_supporting_documents(self):
        """
        Check if supporting documents are enabled for this entity and
        include them in the form
        :return: bool
        """
        entity = self.entity_object()
        return entity.supports_documents

    def entity_supported_document_types(self):
        """
        Get supported document types for particular entity
        :return: list
        :rtype: lookup values of the supported document type
        """
        if self.entity_object().supports_documents:
            return self.entity_object().document_types()

    def profile_entity_attribute(self):
        """
        :param entity:
        :return:
        """
        cols = current_profile().entity_by_name(self.entity_name).columns
        return cols

    def default_entity(self):
        """
        Use to select an entity that will be treated as default
        :return: str
        """
        return self.entity_name

    def entity_fullname(self):
        """
        Return the full name of the table as defined in the configuration
        :return: Entity name
        :rtype str
        """
        self.user_entity

    def profile_name(self):
       """
        Return the profile name
       :return:str
       """
       return current_profile().name

    def read_attributes(self):
        """
        Test implementation hand codes the entity but would need to be
        implemented on the dialog for user to make their own selection
        :param self:
        :return:dict of entity column and data type
        """
        self.get_user_selected_entity()
        self.entity_attributes = OrderedDict()
        col_objs = self.profile_entity_attribute().values()
        for obj in col_objs:
            self.entity_attributes[obj.name] = obj.TYPE_INFO
        del self.entity_attributes['id']
        return self.entity_attributes

    def entity_columns(self):
        """
        Entity attributes
        :return: dict
        """
        if self.entity_attributes.has_key('id'):
            del self.entity_attributes['id']
        return self.entity_attributes

    def format_lookup_items(self, col):
        """
        Get column lookup for the given lookup column type
        :param col:
        :return:
        """
        col_attributes = OrderedDict()
        if self.on_column_info(col):
            col_obj = self.profile_entity_attribute().get(col)
            value_list = col_obj.value_list
            for val in value_list.values.values():
                col_attributes[unicode(val.value)] = unicode(val.code)
            return col_attributes
        else:
            return None

    def on_column_info(self, item_col):
        """
        get lookup associated with the column
        :param item_col:
        :return:bool
        """
        is_lookup = False
        lk_val = self.entity_attributes.get(item_col)
        if lk_val == "MULTIPLE_SELECT" or lk_val == "LOOKUP" or lk_val == "BOOL":
            is_lookup = True
        return is_lookup

    def column_lookup_mapping(self):
        """
        Check if the column has a lookup and get the associated lookup definition
        :return:
        """
        lk_attributes = OrderedDict()
        col_objs = self.profile_entity_attribute().values()
        for col in col_objs:
            if col.TYPE_INFO == "LOOKUP" or col.TYPE_INFO == "MULTIPLE_SELECT":
                value_list = col.value_list
                lk_attributes[col] = unicode(value_list.name)
        return lk_attributes

    def column_info(self, item_col):
        """
        get lookup associated with the column
        :param item_col:
        :return: 
        """
        lk_val = self.entity_attributes.get(item_col)
        if lk_val == "LOOKUP" or lk_val =="MULTIPLE_SELECT":
            return lk_val

    def column_info_multiselect(self, item_col):
        """
        get lookup associated with the column
        :param item_col:
        :return:
        """
        ismulti = False
        mt_val = self.entity_attributes.get(item_col)
        if mt_val == "MULTIPLE_SELECT":
            ismulti = True
        return ismulti


    def col_is_mandatory(self, item_col):
        """
        Check if the column is mandatory to enforce the same on the Xform
        :param: column name
        :return: bool
        """
        col_objs = self.profile_entity_attribute().values()
        for col in col_objs:
            if col.name == item_col:
                return col.mandatory

    def entity_lookup(self):
        """
        
        :param lookup: 
        :return: 
        """
        return self.lookup

    def social_tenure(self):
        """
        Get the social tenure entity in the current profile
        :return: social tenure entity
        """
        return self.profile().social_tenure

    def social_tenure_attributes(self):
        """
        Get social tenure attributes
        :return: column obj
        :rtype dict
        """
        str_attributes = OrderedDict()
        for obj in self.social_tenure().columns.values():
            if str(obj.name).endswith('id'):
                continue
            str_attributes[obj.name] = obj.TYPE_INFO
        #del str_attributes['id']
        return str_attributes

    def social_tenure_lookup(self, cur_col):
        """
        Check if the social tenure column is a lookup
        :return:bool
        """
        is_lookup = False
        for key, col in self.social_tenure_attributes().iteritems():
            if key == cur_col and col == 'LOOKUP':
                is_lookup = True
        return is_lookup

    def social_tenure_lkup_from_col(self, col):
        """
        Get lookup values from the column name passed if it is a lookup
        :param col:
        :return: valuelist
        :rtype: dict
        """
        str_lk_values = OrderedDict()
        cols_obj = self.social_tenure().columns

        column_isnt = cols_obj[col]
        value_list = column_isnt.value_list
        for val in value_list.values.values():
            str_lk_values[val.value] = val.code
        return str_lk_values





