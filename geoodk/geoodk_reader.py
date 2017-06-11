"""

"""
from PyQt4.QtCore import QObject
from stdm.settings import current_profile

class GeoODKReader():
    """
    Class to read entity info from profile and return the entity data
    """
    def __init__(self, entity):
        """

        """

        self.entity_name = None
        self.user_entity = entity
        self.entity_attributes = {}
        self.lookup_attributes = {}
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
        :return:
        """
        self.user_entity

    def profile_name(self):
       """

       :return:
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
        self.entity_attributes = {}
        col_objs = self.profile_entity_attribute().values()
        for obj in col_objs:
            self.entity_attributes[obj.name] = obj.TYPE_INFO
        del self.entity_attributes['id']
        return self.entity_attributes

    def create_unique_col_name(self, col):
        """
        Prepend entity name to column name for uniqueness in the Xform
        :param col:
        :return:
        """
        column = ""
        if isinstance(col, unicode):
            column = self.user_entity.lower() + "." + col
        elif isinstance(col, str):
            column = self.user_entity.lower() + "." + col
        elif isinstance(col, object):
            column = self.user_entity.lower() + "." + col.name
        else:
            column = col
        return column

    def entity_columns(self):
        """
        
        :return: 
        """
        if hasattr(self.entity_attributes, 'id'):
            del self.entity_attributes['id']
        return self.entity_attributes

    def format_lookup_items(self, col):
        """

        :param col:
        :return:
        """
        col_attributes ={}
        if self.on_column_info(col):
            col_obj = self.profile_entity_attribute().get(col)
            value_list = col_obj.value_list
            for val in value_list.values.values():
                col_attributes[val.value] = val.code
            return col_attributes
        else:
            return None

    def on_column_info(self, item_col):
        """
        get lookup associated with the column
        :param item_col:
        :return:
        """
        is_lookup = False
        lk_val = self.entity_attributes.get(item_col)
        if lk_val == "MULTIPLE_SELECT" or lk_val == "LOOKUP":
            is_lookup = True
        return is_lookup

    def column_lookup_mapping(self):
        """
        Check if the column has a lookup and get the associated lookup definition
        :return:
        """
        lk_attributes ={}
        col_objs = self.profile_entity_attribute().values()
        for col in col_objs:
            if col.TYPE_INFO == "LOOKUP" or col.TYPE_INFO == "MULTIPLE_SELECT":
                value_list = col.value_list
                lk_attributes[col] = value_list.name
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


