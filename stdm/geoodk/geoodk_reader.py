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
from collections import OrderedDict

from stdm.settings import current_profile

ColumnName = str
ColumnDataType = str

class GeoODKReader:
    """
    Class to read entity info from profile and return the entity data
    """

    def __init__(self, entity: str):
        """
        Iniatialize the class variables
        """
        self.entity_name = None
        self.user_entity = entity
        self.entity_attributes = OrderedDict()
        self.lookup_attributes = OrderedDict()
        self.lookup = []
        #self.profile()

    def profile(self):
        """
        :return:profile object
        :rtype: Object
        """
        return current_profile()

    def user_entity_name(self) ->str:
        return self.user_entity

    def set_user_entity_name(self, ent_name: str):
        """
        :return:entity
        :return entity_name
        :rtype:str
        """
        self.entity_name = self.profile().entity(ent_name).name
        # self.user_entity_name()
        # return self.entity_name

    def set_user_selected_entity(self):
        """
        Get user selected list of entities
        :param user_sel: string, list
        :return: string
        """
        self.entity_name = self.profile().entity(self.user_entity).name
        #return self.entity_name

    def entity_object(self):
        """
        Get the entity object from the table name
        :return:Entity object
        :rtype: Object
        """
        return self.profile().entity(self.user_entity)

    def entity_has_supporting_documents(self)->bool:
        """
        Check if supporting documents are enabled for this entity
        """
        entity = self.entity_object()
        # entity = current_profile().entity(entity_obj.name)
        return entity.supports_documents

    def entity_supported_document_types(self):
        """
        Get supported document types for particular entity
        :return: list
        :rtype: lookup values of the supported document type
        """
        if self.entity_object().supports_documents:
            return self.entity_object().document_types_non_hex()

    def entity_columns(self) ->dict[str, object]:
        """
        :param entity:
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

    def read_attributes(self) ->dict[ColumnName, ColumnDataType]:
        """
        Test implementation hand codes the entity but would need to be
        implemented on the dialog for user to make their own selection
        :param self:
        :return:dict of entity column and data type
        if column.display_name() == 'Related Entity' or column.name == 'id':
        """
        self.set_user_selected_entity()
        self.entity_attributes = OrderedDict()
        columns = list(self.entity_columns().values())
        for column in columns:
            # Don't include related entity columns and id columns
            # if column.display_name() == 'Related Entity' or column.name == 'id':
            if column.name == 'id':
                continue
            self.entity_attributes[column.name] = column.TYPE_INFO
        return self.entity_attributes

    def entity_columnsXX(self):
        """
        Entity attributes
        :return: dict
        """
        if 'id' in self.entity_attributes:
            del self.entity_attributes['id']
        return self.entity_attributes

    def format_lookup_items(self, col):
        """
        Get column lookup for the given lookup column type
        :param col:
        :return:
        """
        col_attributes = OrderedDict()
        if self.is_lookup_column(col):
            col_obj = self.entity_columns().get(col)
            value_list = col_obj.value_list
            for val in value_list.values.values():
                col_attributes[str(val.value)] = str(val.code)
            return col_attributes
        else:
            return None

    def is_lookup_column(self, column_name: str) ->bool:
        """
        Checks if a column type is a lookup
        """
        is_lookup = False
        column_type = self.entity_attributes.get(column_name)
        if column_type == "MULTIPLE_SELECT" or column_type == "LOOKUP" or column_type == "BOOL":
            is_lookup = True
        return is_lookup

    def column_lookup_mapping(self):
        """
        Check if the column has a lookup and get the associated lookup definition
        :return:
        """
        lk_attributes = OrderedDict()
        col_objs = list(self.entity_columns().values())
        for col in col_objs:
            if col.TYPE_INFO == "LOOKUP" or col.TYPE_INFO == "MULTIPLE_SELECT":
                value_list = col.value_list
                lk_attributes[col.name] = str(value_list.name)
        return lk_attributes

    def column_info(self, item_col):
        """
        get lookup associated with the column
        :param item_col:
        :return:
        """
        lk_val = self.entity_attributes.get(item_col)
        if lk_val == "LOOKUP" or lk_val == "MULTIPLE_SELECT":
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
        col_objs = list(self.entity_columns().values())
        for col in col_objs:
            if col.name == item_col:
                return col.mandatory

    def col_label(self, item_col):
        """
        Get the column label using the column name
        :param: column name
        :return: label name
        :rtype: string
        """
        col_objs = list(self.entity_columns().values())
        for obj in col_objs:
            if obj.name == item_col:
                return [obj.label if obj.label else
                        obj.name.replace('_', ' ').title()][0]

    def entity_lookup(self):
        """
        :param lookup:
        :return: list
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
        for obj in list(self.social_tenure().columns.values()):
            if str(obj.name).endswith('id'):
                continue
            str_attributes[obj.name] = obj.TYPE_INFO
        return str_attributes

    def field_is_social_tenure_lookup(self, cur_col):
        """
        Check if the social tenure column is a lookup
        :return:bool
        """
        is_lookup = False
        for key, col in self.social_tenure_attributes().items():
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

    def on_column_show_in_parent(self):
        """
        Check whether the foreign key column has flag show in parent.
        required to enable geoodk subform creation
        :return:
        """
        cols_obj = list(self.entity_columns().values())
        for col in cols_obj:
            if col.TYPE_INFO == 'FOREIGN_KEY':
                relations = col.entity_relation
                return relations.show_in_parent
