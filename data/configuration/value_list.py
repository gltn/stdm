"""
/***************************************************************************
Name                 : ValueList
Description          : Represents a table containing lookup values.
Date                 : 28/December/2015
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
import logging
from collections import OrderedDict

from stdm.data.configuration.columns import (
    VarCharColumn
)
from stdm.data.configuration.entity import Entity
from stdm.data.configuration.entity_updaters import value_list_updater

LOGGER = logging.getLogger('stdm')


def value_list_factory(name, profile, **kwargs):
    """
    Factory method for creating an instance of a ValueList object. This
    function is passed on to a profile instance to create the Entity.
    :param name: Entity name.
    :type name: str
    :param profile: Profile that the ValueList will belong to.
    :type profile: Profile
    :returns: Instance of a ValueList object.
    :rtype: ValueList
    """
    return ValueList(name, profile)


class CodeValue(object):
    """
    Represents a code and corresponding value for use in a ValueList object.
    """
    def __init__(self, code='', value=''):
        self.code = code
        self.value = value
        self.updated_value = ''


class ValueList(Entity):
    """
    Corresponds to a database table object which contains a list of
    enumeration values that are referenced by different tables across
    the schema. Examples include gender, marital status, level of
    education etc.
    """
    TYPE_INFO = 'VALUE_LIST'
    PREFIX = 'check'
    sql_updater = value_list_updater

    def __init__(self, name, profile):
        #Assert if 'check' prefix has been appended.
        name = self._append_check(name)

        Entity.__init__(self, name, profile, supports_documents=False)

        self.user_editable = False

        self.code_column = VarCharColumn('code', self, minimum=0, maximum=5)
        self.value_column = VarCharColumn('value', self, minimum=2, maximum=50)
        self.values = OrderedDict()

        #Attach columns
        self.add_column(self.code_column)
        self.add_column(self.value_column)

        LOGGER.debug('%s ValueList initialized.', self.name)

    def _append_check(self, name):
        #Appends a 'check_prefix' to the name.
        idx = name.find(self.PREFIX)

        if idx != -1:
            return name

        return u'{0}_{1}'.format(self.PREFIX, name)

    def add_value(self, value, code=''):
        """
        Add a string value to the CodeValue collection.
        :param value: Lookup value.
        :type value: str
        """
        self.add_code_value(CodeValue(value=value, code=code))

    def add_code_value(self, code_value):
        """
        Add a CodeValue object to the collection.
        :param code_value: CodeValue object.
        :type code_value: CodeValue
        """
        self.values[code_value.value] = code_value

    def is_empty(self):
        """
        return: Returns True if the ValueList contains items else 
        False.
        :rtype: bool
        """
        return len(self.values) == 0

    def copy_from(self, value_list, clear_first=False):
        """
        Appends the code value collection from the given value list.
        :param value_list: Collection to copy code values from.
        :type value_list: ValueList
        :param clear_first: Removes previous code values
        before copying the new ones
        :type clear_first: Boolean
        """
        #Test if it is a ValueList object
        if value_list.TYPE_INFO != ValueList.TYPE_INFO:
            return

        #Check if clear_first is True
        if clear_first:
            for cv in self.values.values():
                self.remove_value(cv)

        for cv in value_list.values.values():
            self.add_code_value(cv)

    def rename(self, old_value, new_value):
        """
        Rename a value in the lookup collection.
        :param old_value: Previous value.
        :type old_value: str
        :param new_value: Updated value.
        :type new_value: str
        :returns: True if the value was successfully replaced, otherwise
        False.
        :rtype: bool
        """
        if not old_value in self.values:
            LOGGER.debug('%s lookup value could not be found in the %s value '
                         'list.', old_value, self.name)

            return False

        code_value = self.values[old_value]
        code_value.updated_value = new_value

        LOGGER.debug('%s lookup value has been updated to %s in the %s value '
                     'list.', old_value, new_value, self.name)

        return True

    def code_value(self, value):
        """
        :param value: Value whose corresponding CodeValue object will be
        retrieved.
        :type value: str
        :returns: Returns a CodeValue object whose 'value' or 'updated_value'
        attributes correspond to the specified value; else returns None if
        not found.
        :rtype: CodeValue
        """
        cv = None

        if value in self.values:
            cv = self.values[value]

        else:
            remapped_code_values = self._values_by_updates()

            if value in remapped_code_values:
                cv = remapped_code_values[value]

        return cv

    def _values_by_updates(self):
        #Remap the CodeValue collection to be indexed by updated value.
        updated_values = OrderedDict()

        for v, cv in self.values.iteritems():
            uv = cv.updated_value
            if uv:
                updated_values[cv.updated_value] = cv

        return updated_values

    def remove_value(self, value):
        """
        Remove the given lookup value from the collection.
        :param value: Value to be removed.
        :type value: str
        :returns: True if the value was successfully removed, else False.
        :rtype: bool
        """
        cv = self.code_value(value)

        if cv is None:
            LOGGER.debug('%s lookup value could not be found in the %s value '
                         'list.', value, self.name)

            return False

        del self.values[cv.value]

        LOGGER.debug('%s lookup value removed from the %s value list.',
                     value, self.name)

        return True



