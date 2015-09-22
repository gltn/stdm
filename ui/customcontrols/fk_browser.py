"""
/***************************************************************************
Name                 : FK Browser
Description          :
Date                 : 16/April/2014
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


class FKBrowserProperty(object):

    def __init__(self, id, value, parent=None):
        """
        Initialize class variables
        :param id:
        :param value:
        :param parent:
        :return:
        """
        self._id = id
        self._display_value = value

    def base_id(self):
        """
        Method to return the base id of the model
        :return:
        """
        return self._id

    def set_base_id(self, new_id):
        """
        :param new_id:
        """
        self._id = new_id

    def display_value(self):
        """
        :rtype : str
        :return:
        """
        if not self._display_value:
            return 0
        else:
            return self._display_value

    def set_display_value(self, new_value):
        """

        :param new_value:
        :return:
        """
        self._display_value = new_value
