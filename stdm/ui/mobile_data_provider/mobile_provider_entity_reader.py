from collections import OrderedDict

from qgis._core import QgsMessageLog

from stdm.settings import current_profile


class EntityReader:
    """
    Class to read entity info from profile and return the entity data
    """

    def __init__(self, entity: str):

        self.entity_name = None
        self.user_entity = entity

    def profile(self):
        """
        :return:profile object
        :rtype: Object
        """
        return current_profile()

    def entity_columns(self):
        """
        :param entity:
        """
        cols = current_profile().entity_by_name(self.entity_name).columns
        return cols

    def read_attributes(self):
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
            if column.display_name() == 'Related Entity' or column.name == 'id':
                continue
            self.entity_attributes[column.name] = column.TYPE_INFO
        return self.entity_attributes

    def set_user_selected_entity(self):
        """
        Get user selected list of entities
        :param user_sel: string, list
        :return: string
        """
        self.entity_name = self.profile().entity(self.user_entity).name

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

    def default_entity(self):
        """
        Use to select an entity that will be treated as default
        :return: str
        """
        return self.entity_name

    # def column_lookup_mapping(self):
    #     """
    #     Check if the column has a lookup and get the associated lookup definition
    #     :return:
    #     """
    #     lk_attributes = OrderedDict()
    #     col_objs = list(self.entity_columns().values())
    #     for col in col_objs:
    #         if col.TYPE_INFO == "LOOKUP" or col.TYPE_INFO == "MULTIPLE_SELECT" or col.TYPE_INFO == "BOOL":
    #             value_list = col.value_list
    #             lk_attributes[col.name] = str(value_list.name)
    #     return lk_attributes

    def format_lookup_items(self, col):
        """
        Get column lookup for the given lookup column type
        :param col:
        :return:
        """
        col_attributes = OrderedDict()
        if self.on_column_info(col):
            col_obj = self.entity_columns().get(col)
            value_list = col_obj.value_list
            for val in value_list.values.values():
                col_attributes[str(val.value)] = str(val.code)
            return col_attributes
        else:
            return None