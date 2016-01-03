"""
/***************************************************************************
Name                 : Profile
Description          : Logical grouping of related entities.
Date                 : 25/December/2015
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

from PyQt4.QtCore import (
    pyqtSignal,
    QObject
)

from .administative_spatial_unit import AdministrativeSpatialUnit
from .association_entity import (
    association_entity_factory,
    AssociationEntity
)
from .entity_relation import EntityRelation
from .entity import Entity
from .social_tenure import SocialTenure
from .supporting_document import SupportingDocument

LOGGER = logging.getLogger('stdm')


class Profile(QObject):
    """
    A profile represents a collection of related entities, of which some
    represent the party, spatial unit and STR in an overall social tenure
    relationship context.

    Examples of profiles include household, neighbourhood or even city
    profile.

    .. note:: A profile can have only one social tenure relationship defined.

    """
    entity_added = pyqtSignal(Entity)
    entity_removed = pyqtSignal(str)

    def __init__(self, name, configuration):
        """
        :param name: A unique name to identify the profile.
        :type name: str
        :param configuration: Parent configuration object.
        """
        QObject.__init__(self, configuration)
        self.name = name
        self.configuration = configuration
        self.prefix = self._prefix()
        self.social_tenure = self._create_social_tenure()
        self.entities = OrderedDict()
        self.relations = OrderedDict()
        self.supporting_document = SupportingDocument(self)
        self._admin_spatial_unit = AdministrativeSpatialUnit(self)

        #Add default entities to the entity collection
        self.add_entity(self.supporting_document)
        self.add_entity(self._admin_spatial_unit)

    def _prefix(self):
        prefixes = self.configuration.prefixes()

        prefix = self.name

        for i in range(2, len(self.name)):
            curr_prefix = self.name[0:i]

            if not curr_prefix in prefixes:
                prefix = curr_prefix

                LOGGER.debug('Prefix determined %s for %s profile', prefix, self.name)

                break

        return prefix

    def _create_social_tenure(self):
        """
        :return: Returns an instance of a social tenure object.
        :rtype: SocialTenure
        """
        return SocialTenure('social_tenure_relationship', self)

    def set_social_tenure_attr(self, attr, val):
        """
        Sets the specified property of the SocialTenure object.
        :param attr: Name of the attribute.
        :type attr: str
        :param value: Attribute value. A string or object can be passed; if
        it is the former then the corresponding entity will be used if it
        exists in the collection.
        :type value: str
        """
        LOGGER.debug('Attempting to set the value for %s attribute in %s '
                     'profile.', attr, self.name)

        if not hasattr(self.social_tenure, attr):
            LOGGER.debug('%s attribute not found.', attr)

            return

        if attr != 'supporting_docs':
            setattr(self.social_tenure, attr, val)

            LOGGER.debug('Value for %s attribute has been successfully set.', attr)

    def entity(self, name):
        """
        Get table item from the name.
        :param name: Name of the table item.
        :type name: str
        :returns: Entity with the corresponding name, returns None
        if not found.
        :rtype: Entity
        """
        return self.entities.get(name, None)

    def relation(self, name):
        """
        :param name: Name of the relation.
        :type name: str
        :returns: EntityRelation corresponding to the given name.
        :rtype: EntityRelation
        """
        return self.relations.get(name, None)

    def create_entity_relation(self, **kwargs):
        """
        Creates a new instances of an EntityRelation object.
        :param kwargs: Arguments sent to the EntityRelation constructor.
        :returns: Instance of an EntityRelation object
        :rtype: EntityRelation
        """
        return EntityRelation(self, **kwargs)

    def add_entity_relation(self, entity_relation):
        """
        Add an EntityRelation object to the collection
        :param entity_relation: EntityRelation object
        :type entity_relation: EntityRelation
        :returns: True if an EntityRelation was successfully added, else
        False if either there is an existing relation with a similar name or
        the relation contains an empty name.
        :rtype: bool
        """
        if not entity_relation.name:
            LOGGER.debug('Entity relation with empty name cannot be used.')

            return False

        valid, msg = entity_relation.valid()

        if not valid:
            err = 'Invalid EntityRelation object, cannot be added to the ' \
                  'collection. Message: ' + msg

            LOGGER.debug(err)

            return False

        if entity_relation.name in self.relations:
            LOGGER.debug('Entity relation with the name %s already exists.', entity_relation.name)

            return False

        self.relations[entity_relation.name] = entity_relation

        LOGGER.debug('%s entity relation added.', entity_relation.name)

        return True

    def remove_relation(self, name):
        """
        Remove the EntityRelation with the given name from the collection.
        :param name: Name of the EntityRelation object.
        :type name: str
        :returns: True if the relation was successfully removed, otherwise
        False.
        :rtype: bool
        """
        if not name in self.relations:
            LOGGER.debug('%s entity relation not found.', name)

            return False

        del self.relations[name]

        LOGGER.debug('%s entity relation removed from %s profile', name, self.name)

    def add_entity(self, item):
        """
        Add an entity object to the collection.
        :param item: Entity to add to the collection. If there is an
        existing item in the collection with the same name, then it will be
        replaced with this item.
        :type item: Entity
        """
        self.entities[item.short_name] = item

        LOGGER.debug('%s entity added to %s profile', item.short_name, self.name)

        #Raise entity added signal
        self.entity_added.emit(item)

    def remove_entity(self, name):
        """
        Removes an entity with the given name from the collection.
        :param name: Name of the entity. Should include the prefix that
        the entity belongs to.
        :type name: str
        :returns: True if the item was successfully removed, otherwise False.
        :rtype: bool
        """
        if not name in self.entities:
            LOGGER.debug('%s entity cannot be removed. Item does '
                         'not exist.', name)

            return False

        del self.entities[name]

        LOGGER.debug('%s entity removed from %s profile', name, self.name)

        self.entity_removed.emit(name)

        return True

    def create_entity(self, name, factory, **kwargs):
        """
        Creates an entity instance through the factory method.
        :param name: Name of the entity.
        :type name: str
        :param factory: Factory method which handles the specifics of
        creating an entity object.
        The first argument should be the name, followed by the profile object
        and finally any keyword arguments that are applicable to the specific
        entity.
        :return: Instance of an Entity class. Actual creation is done by the
        factory method.
        :rtype: Entity
        """
        return factory(name, self, **kwargs)

    def create_association_entity(self, name, **kwargs):
        """
        Creates an AssociationEntity object for defining an association
        relationship between two entities.
        :param name: Name of the association entity.
        :type name: str
        :param kwargs: See optional arguments for AssociationEntity class.
        :returns: Instance of an AssociationEntity.
        :rtype: AssociationEntity
        """
        return self.create_entity(name, association_entity_factory, **kwargs)