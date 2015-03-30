__author__ = 'SOLOMON'


class FKBrowserProperty(object):
    def __init__(self,id, value, parent=None):
        """
        Initialize class variables
        :param id:
        :param value:
        :param parent:
        :return:
        """
        self._id = id
        self._display_value = value

    def baseid(self):
        """
        Method to return the base id of the model
        :return:
        """
        return self._id

    def set_baseid(self, newid):
        self._id = newid

    def display_value(self):
        """

        :return:
        """
        return self._display_value

    def set_display_value(self,newvalue):
        """

        :param newvalue:
        :return:
        """
        self._display_value = newvalue





