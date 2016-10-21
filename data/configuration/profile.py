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
from copy import deepcopy

from PyQt4.QtCore import (
    pyqtSignal,
    QObject
)

from stdm.data.configuration.administative_spatial_unit import (
    AdministrativeSpatialUnit
)
from stdm.data.configuration.association_entity import (
    association_entity_factory,
    AssociationEntity
)
from stdm.data.configuration.entity_relation import EntityRelation
from stdm.data.configuration.entity import (
    Entity,
    EntitySupportingDocument
)
from stdm.data.configuration.db_items import DbItem
from stdm.data.configuration.social_tenure import SocialTenure
from stdm.data.configuration.supporting_document import SupportingDocument
from stdm.data.configuration.value_list import (
    value_list_factory,
    ValueList
)

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
    entity_removed = pyqtSignal(unicode)

    def __init__(self, name, configuration):
        """
        :param name: A unique name to identify the profile.
        :type name: str
        :param configuration: Parent configuration object.
        """
        QObject.__init__(self, configuration)
        self.name = name
        self.description = ''
        self.configuration = configuration
        self.prefix = self._prefix()
        self.entities = OrderedDict()
        self.relations = OrderedDict()
        self.removed_relations = []
        #Base entity for supporting documents within the profile
        self.supporting_document = SupportingDocument(self)

        #Init STR
        self.social_tenure = self._create_social_tenure()

        self._admin_spatial_unit = AdministrativeSpatialUnit(self)
        self.removed_entities = []

        #Add default entities to the entity collection
        self.add_entity(self.supporting_document)
        self.add_entity(self._admin_spatial_unit)

        self.add_entity(self.social_tenure)

    def _prefix(self):
        prefixes = self.configuration.prefixes()

        prefix = self.name

        for i in range(2, len(self.name)):
            curr_prefix = self.name[0:i]

            if not curr_prefix in prefixes:
                prefix = curr_prefix

                LOGGER.debug('Prefix determined %s for %s profile',
                             prefix.lower(), self.name)

                break

        return prefix.lower()

    def _create_social_tenure(self):
        """
        :return: Returns an instance of a social tenure object.
        :rtype: SocialTenure
        """
        return SocialTenure('social_tenure_relationship', self)

    @property
    def administrative_spatial_unit(self):
        """
        :return: Returns the entity corresponding to the administrative
        spatial unit.
        :rtype: AdministrativeSpatialUnit
        """
        return self._admin_spatial_unit

    @property
    def key(self):
        """
        :return: Returns the normalized name of the profile.
        :rtype: str
        """
        return self.name.replace(' ', '_').lower()

    def set_social_tenure_attr(self, entity_type, val):
        """
        Sets the specified property of the SocialTenure object.
        :param attr: Enumeration type of an social tenure relationship entity.
        :type attr: int
        :param value: Attribute value. A string or object can be passed; if
        it is the former then the corresponding entity will be used if it
        exists in the collection.
        :type value: str
        """
        if entity_type == SocialTenure.PARTY:
            attr = 'party'

        elif entity_type == SocialTenure.SPATIAL_UNIT:
            attr = 'spatial_unit'

        elif entity_type == SocialTenure.SOCIAL_TENURE_TYPE:
            attr = 'tenure_type_collection'

        else:
            LOGGER.debug('%s is an invalid enumeration for social tenure '
                         'entity type.', str(entity_type))

            return

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
        Get table item using its short name.
        :param name: Short name of the table item.
        :type name: str
        :returns: Entity with the corresponding name, returns None
        if not found.
        :rtype: Entity
        """
        return self.entities.get(name, None)

    def entity_by_name(self, name):
        """
        :param name: Name of the entity i.e. table name in the database.
        :type name: str
        :return: Return an entity object with the specified name attribute.
        ValueLists are also searched and returned.
        :rtype: Entity
        """
        items = [e for e in self.entities.values() if e.name == name]

        if len(items) == 0:
            return None
        
        else:
            return items[0]

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

    def user_entities(self):
        """
        :return: Returns a list of entities that are user editable i.e. those
        that have the attribute 'user_editable' set to True.
        :rtype: list
        """
        return [ent for ent in self.entities.values() if ent.user_editable]

    def parent_relations(self, item):
        """
        :param item: Entity object that is a parent in the collection of
        entity relations.
        :type item: Entity
        :return: Returns a list of entity relations whose parents match that
        of the specified argument.
        :rtype: EntityRelation
        """
        #Get corresponding entity
        if not isinstance(item, Entity):
            raise TypeError(self.tr('Entity object type expected.'))

        name = item.name

        return [er for er in self.relations.values()
                if er.parent.name == name]

    def child_relations(self, item):
        """
        :param parent: Entity object that is a child in the collection of
        entity relations.
        :type item: Entity
        :return: Returns a list of entity relations whose children match that
        of the specified argument.
        :rtype: EntityRelation
        """
        #Get corresponding entity
        if not isinstance(item, Entity):
            return []

        name = item.name

        return [er for er in self.relations.values()
                if er.child.name == name]

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
            LOGGER.debug('Entity relation with the name %s already exists.',
                         entity_relation.name)

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

        rel = self.relations[name]

        self.removed_relations.append(rel)

        LOGGER.debug('%s entity relation flagged to be removed from %s '
                     'profile', name, self.name)

        return True

    def add_entity(self, item, suppress_signal=False):
        """
        Add an entity object to the collection.
        :param item: Entity to add to the collection. If there is an
        existing item in the collection with the same name, then it will be
        replaced with this item.
        :type item: Entity
        :param suppress_signal: True to suppress the 'entity_added' signal
        from being emitted. Default behavior is to emit the signal.
        :type suppress_signal: bool
        """
        #If there is an existing item with the same name,
        # and that item action is not DROP, then do not add this.
        if item.short_name in self.entities:
            old_item = self.entities[item.short_name]
            if old_item.action <> DbItem.DROP:
                return

        self.entities[item.short_name] = item

        LOGGER.debug('%s entity added to %s profile', item.short_name, self.name)

        #Raise entity added signal if enabled
        if not suppress_signal:
            self.entity_added.emit(item)

    def remove_entity(self, name):
        """
        Removes an entity with the given short name from the collection.
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

        ent = self.entities[name]

        #Check existing entity relation where this entity is referenced
        parent_relations = self.parent_relations(ent)
        child_relations = self.child_relations(ent)
        remove_relations = parent_relations + child_relations

        #Check if the entity has supporting documents and remove references
        if ent.supports_documents:
            supporting_doc_ent = ent.supporting_doc
            if not supporting_doc_ent is None:
                #Some relations will be duplicated with ones in the main ent.
                doc_parent_relations = self.parent_relations(supporting_doc_ent)
                doc_child_relations = self.child_relations(supporting_doc_ent)

                remove_relations.extend(doc_parent_relations)
                remove_relations.extend(doc_child_relations)

        for er in remove_relations:
            self.remove_relation(er.name)

        #Remove association entities if any
        self.remove_association_entities(ent)

        #Now remove the entity from the collection
        del_entity = self.entities.pop(name, None)

        LOGGER.debug('%s entity removed from %s profile', name, self.name)

        if not del_entity is None:
            del_entity.action = DbItem.DROP
            self.removed_entities.append(del_entity)

        self.entity_removed.emit(name)

        return True

    def remove_association_entities(self, entity):
        """
        Removes association entities related to the specified primary
        entity. Searches for primary entity in both first and second
        parent entities in each association entity.
        :param entity: Primary entity whose association entities are to be
        removed.
        :type entity: Entity
        """
        assoc_entities = self.parent_association_entities(entity)

        #Remove association entities
        for ae in assoc_entities:
            self.remove_entity(ae.short_name)

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

    def create_value_list(self, name):
        """
        Creates a ValueList object.
        :param name: Name to use for the value list. A 'check_' prefix
        will be appended.
        :return: Returns an empty ValueList object.
        :rtype: ValueList
        """
        return self.create_entity(name, value_list_factory)

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

    def entities_by_type_info(self, type_info):
        """
        :param type_info: Entity TYPE_INFO
        :type type_info: str
        :returns: A list of entities based on the specified TYPE_INFO
        e.g. ENTITY, VALUE_LIST etc.
        :rtype: list(Entity)
        """
        return [entity for entity in self.entities.values()
                if entity.TYPE_INFO == type_info]

    def value_lists(self):
        """
        :return: A list of lookup entities contained in this profile.
        :rtype: list
        """
        return self.entities_by_type_info(ValueList.TYPE_INFO)

    def supporting_document_entities(self):
        """
        :return: Returns a list of supporting documents entities in the
        profile.
        :rtype: list
        """
        return self.entities_by_type_info(EntitySupportingDocument.TYPE_INFO)

    def association_entities(self):
        """
        :return: Returns all association entities in the profile.
        :rtype: list
        """
        return self.entities_by_type_info(AssociationEntity.TYPE_INFO)

    def parent_association_entities(
            self,
            entity,
            parent=AssociationEntity.FIRST_PARENT|AssociationEntity.SECOND_PARENT
    ):
        """
        :param entity: First or second parent association entity.
        :type entity: AssociationEntity
        :param parent: Specify whether to search for first, second or both
        parents. Default is bot first and second parents.
        :type parent: enum
        :return: Returns a list of association entities which reference the
        given entity as the first or second parent depending on the search
        configuration.
        :rtype: list
        """
        parents = []

        #Get first parent if specified
        if (parent & AssociationEntity.FIRST_PARENT) == AssociationEntity.FIRST_PARENT:
            first_parents = [ae for ae in self.association_entities()
                             if ae.first_parent.name == entity.name]

            parents.extend(first_parents)

        #Get second parent if specified
        if (parent & AssociationEntity.SECOND_PARENT) == AssociationEntity.SECOND_PARENT:
            second_parents = [ae for ae in self.association_entities()
                              if ae.second_parent.name == entity.name]

            parents.extend(second_parents)

        return parents

    def on_delete(self):
        """
        Cleans up the profile upon deleting by clearing the tables and
        corresponding entity relation/FK constraints.
        """
        for entity in self.entities.values():
            self.remove_entity(entity.short_name)

    def table_names(self):
        """
        :return: Returns a list of table names that belong to this profile
        object. Some tables might not actually exist in the database so it
        important to check if the table names exist.
        :rtype: list(str)
        """
        return [e.name for e in self.entities.values()]

    def rename(self, original_name, new_name):
        """
        Renames the entity with the given short name to use the new name.
        This only works if the entity has not yet been created in the
        database.
        :param original_name: Original short name of the entity to be
        renamed.
        :type original_name: str
        :param new_name: Updated entity short name.
        :type new_name: str
        :return: Returns True if the renaming succeeded, else False.
        """
        if not original_name in self.entities:
            LOGGER.debug('%s entity cannot be renamed. Item does '
                         'not exist.', original_name)

            return False

        #Check if the entity participates in either of the STR definitions
        update_party = False
        if not self.social_tenure.party is None:
            update_party = True \
                if self.social_tenure.party.short_name == original_name \
                else False

            print str(update_party)

        update_spatial_unit = False
        if not self.social_tenure.spatial_unit is None:
            update_spatial_unit = True \
                if self.social_tenure.spatial_unit.short_name == original_name \
                else False

        ent = self.entities[original_name]

        #Get entity relations and update entity references
        parent_relations = self.parent_relations(ent)
        child_relations = self.child_relations(ent)

        #Remove entity from the collection
        rn_entity = self.entities.pop(original_name)

        rn_entity.rename(new_name)

        #Re-insert the entity
        self.add_entity(rn_entity, True)

        #Update relations
        for pr in parent_relations:
            pr.parent = rn_entity

        for cr in child_relations:
            cr.child = rn_entity

        #Update entities in the STR definition
        if update_party:
            self.social_tenure.party = rn_entity

        if update_spatial_unit:
            self.social_tenure.spatial_unit = rn_entity

        return True