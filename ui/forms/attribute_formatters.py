__author__ = 'SOLOMON'

from stdm.data.config_utils import setUniversalCode

class AttributeFormatters(object):
    def __init__(self, col_name, parent_table):
        self.col_name = col_name
        self.parent_table = parent_table
        self.table_formatters = {}
        self._display_name =""
        self.add_table_formatters()

    def table_unique_key(self):
        """
        :return setUniversalCode
        :return:
        """
        return setUniversalCode

    def set_display_name(self, new_name):
        """
        Set the display column name
        :param new_name:
        :return:
        """
        self._display_name = new_name
        return self._display_name

    def display_name(self):
        """
        Method to return the defined display column name
        :return:
        """
        return self._display_name

    def add_table_formatters(self):
        """
        Method to read all the foreign key columns and the reference table
        :return:
        """
        """Add unique key if the identification of column and parent table is confusing"""
        #self.table_formatters[self.col_name] = [self.parent_table, self.table_unique_key()]
        """Perhaps there is no conflicts when referencing foreign key, no need for unique Identifier"""
        self.table_formatters[self.col_name] = self.parent_table
        return self.table_formatters