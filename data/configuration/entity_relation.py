"""
/***************************************************************************
Name                 : EntityRelation
Description          : Information on the relationship between 2 entities.
Date                 : 26/December/2015
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
from PyQt4.QtCore import (
    QCoreApplication
)


def tr(text):
    """
    Alias for translating column display names so that they can be in the
    same context i.e. 'BaseColumn'.
    :param text: String to be translated.
    :type text: str
    :returns: Translated text if available, else the original string will be
    returned.
    :rtype: str
    """
    return QCoreApplication.translate('EntityRelation', text)

class EntityRelation(object):

    def __init__(self, profile, **kwargs):
        """
        :param profile: The profile that the this object belongs to.
        This class should not be directly instantiated but rather created
        through a profile object.
        """
        self.profile = profile
        self._parent = None
        self._child = None
        self.parent = kwargs.get('parent', '')
        self.child = kwargs.get('child', '')
        self.parent_column = kwargs.get('parent_column', '')
        self.child_column = kwargs.get('child_column', '')
        self.display_cols = kwargs.get('display_columns', [])

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, entity):
        self._parent =  self._obj_from_str(entity)

    @property
    def child(self):
        return self._child

    @child.setter
    def child(self, entity):
        self._child = self._obj_from_str(entity)

    @property
    def name(self):
        """
        :returns: A simple unique identifier of this EntityRelation object.
        :rtype: str
        """
        rel_name = ''

        if not self.parent is None:
            rel_name += u'fk_{0}_{1}'.format(self.parent.name,
                                             self.parent_column)

        if not self.child is None:
            rel_name += u'_{0}_{1}'.format(self.child.name, self.child_column)

        return rel_name

    def _obj_from_str(self, item):
        """Create corresponding table item from string."""
        obj = item

        if isinstance(item, (str, unicode)):
            if not item:
                return None

            obj = self.profile.entity(item)

        return obj

    def valid(self):
        """
        :return: True if all the main properties have been set i.e. parent,
        parent_column, child, child_column.
        :rtype: (bool, unicode)
        """
        if self.parent is None:
            return False, tr('The parent entity has not been set.')

        if self.child is None:
            return False, tr('The child entity has not been set.')

        if not self.parent_column:
            return False, tr('The parent column has not been defined.')

        if not self.child_column:
            return False, tr('The child column has not been defined.')

        return True