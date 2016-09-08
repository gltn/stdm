"""
/***************************************************************************
Name                 : AssociationEntity
Description          : Represents an association table that enables a
                       many-to-many relationship between two entities.
Date                 : 29/December/2015
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

from stdm.data.configuration.entity import Entity
from stdm.data.configuration.columns import (
    ForeignKeyColumn
)

LOGGER = logging.getLogger('stdm')


def association_entity_factory(name, profile, **kwargs):
    """
    Factory method for creating an instance of an Entity object. This
    function is passed on to a profile instance to create the Entity.
    :param name: Entity name.
    :type name: str
    :param profile: Profile that the entity will belong to.
    :type profile: Profile
    :returns: Instance of an Entity object.
    :rtype: Entity
    """
    return AssociationEntity(name, profile, **kwargs)


class AssociationEntity(Entity):
    """
    Represents an association table that enables a many-to-many relationship
    between two entities.
    """
    TYPE_INFO = 'ASSOCIATION_ENTITY'
    FIRST_PARENT, SECOND_PARENT = range(0, 2)

    def __init__(self, name, profile, **kwargs):
        Entity.__init__(self, name, profile, supports_documents=False)

        self.user_editable = False
        self.is_associative = True

        self.first_reference_column = None
        self.second_reference_column = None

        self.first_parent = kwargs.get('first_parent', None)
        self.second_parent = kwargs.get('second_parent', None)

    @property
    def first_parent(self):
        if self.first_reference_column is None:
            return None

        return self.first_reference_column.entity_relation.parent

    @property
    def second_parent(self):
        if self.second_reference_column is None:
            return None

        return self.second_reference_column.entity_relation.parent

    @first_parent.setter
    def first_parent(self, parent):
        self.first_reference_column = self._set_parent(parent)

        #Add column to the collection
        if self.first_reference_column:
            self.add_column(self.first_reference_column)

    @second_parent.setter
    def second_parent(self, parent):
        self.second_reference_column = self._set_parent(parent)

        if self.second_reference_column:
            self.add_column(self.second_reference_column)

    def _set_parent(self, parent):
        parent_entity = self._obj_from_str(parent)

        if parent_entity is None:
            LOGGER.debug('Failed to set the parent property in %s association '
                         'entity.', self.name)

            return

        #check if there is an 'id' column
        parent_id = self._entity_id_column(parent_entity)

        LOGGER.debug('Attempting to set %s entity as the party.',
                     parent_entity.name)

        if parent_id is None:
            err = self.tr('%s does not have an id column. This is required '
                          'in order to link it to the social tenure '
                          'relationship table.'%(parent_entity.name))

            LOGGER.debug(err)

            raise AttributeError(err)

        #Set foreign key reference
        fk_name = u'{0}_{1}'.format(parent_entity.name, 'id')
        foreign_key_reference = ForeignKeyColumn(fk_name, self)

        #Set parent attributes
        foreign_key_reference.set_entity_relation_attr('parent', parent_entity)
        foreign_key_reference.set_entity_relation_attr('parent_column', 'id')

        LOGGER.debug('%s entity has been successfully set as the parent in '
                     'the %s association entity in the %s profile.',
                     parent_entity.name, self.name, self.profile.name)

        return foreign_key_reference

    def _obj_from_str(self, item):
        """Create corresponding table item from string."""
        obj = item

        if isinstance(item, (str, unicode)):
            if not item:
                return None

            obj = self.profile.entity(item)

        return obj

    def _entity_id_column(self, entity):
        """
        Check if the entity has an ID column and return it, else returns None.
        """
        return entity.column('id')