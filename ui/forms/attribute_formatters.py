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

    def display_name(self, new_name):
        self._display_name = new_name
        return self._display_name

    def add_table_formatters(self):
        """
        :return:
        """
        self.table_formatters[self.col_name] = [self.parent_table, self.table_unique_key()]
        return self.table_formatters