"""
/***************************************************************************
Name                 : SocialTenure
Description          : Defines the entities participating in a STR.
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
import logging

from stdm.data.configuration.columns import (
    ForeignKeyColumn,
    LookupColumn
)
from stdm.data.configuration.entity import Entity
from stdm.data.configuration.social_tenure_updater import view_updater
from stdm.data.configuration.value_list import ValueList

LOGGER = logging.getLogger('stdm')


class SocialTenure(Entity):
    """
    Represents the relationship between party and spatial unit entities
    through social tenure relationship. It also supports the attachment of
    supporting documents.
    Main class that represents 'people-land' relationships.
    """
    TYPE_INFO = 'SOCIAL_TENURE'
    PARTY, SPATIAL_UNIT, SOCIAL_TENURE_TYPE = range(0,3)
    BASE_STR_VIEW = 'vw_social_tenure_relationship'
    tenure_type_list = 'tenure_type'
    view_creator = view_updater

    def __init__(self, name, profile, supports_documents=True):
        Entity.__init__(self, name, profile,
                        supports_documents=supports_documents)

        self.user_editable = False

        self._party = None
        self._spatial_unit = None
        self._view_name = u'{0}_{1}'.format(self.profile.prefix,
                                 SocialTenure.BASE_STR_VIEW)

        self.party_foreign_key = ForeignKeyColumn('party_id', self)
        self.spatial_unit_foreign_key = ForeignKeyColumn('spatial_unit_id',
                                                         self)
        self.tenure_type_lookup = LookupColumn('tenure_type', self)

        self._value_list = self._prepare_tenure_type_value_list()

        #Add the value list to the table collection
        self.profile.add_entity(self._value_list)

        #Add columns to the collection
        self.add_column(self.party_foreign_key)
        self.add_column(self.spatial_unit_foreign_key)
        self.add_column(self.tenure_type_lookup)

        LOGGER.debug('Social Tenure Relationship initialized for %s profile.',
                     self.profile.name)

    @property
    def view_name(self):
        return self._view_name

    @property
    def party(self):
        return self._party

    @property
    def spatial_unit(self):
        return self._spatial_unit

    @property
    def tenure_type_collection(self):
        return self._value_list

    @tenure_type_collection.setter
    def tenure_type_collection(self, value_list):
        #Copy the look up values from the given value list
        value_list_entity = self._obj_from_str(value_list)
        self._value_list.copy_from(value_list_entity)

    @party.setter
    def party(self, party):
        party_entity = self._obj_from_str(party)

        if party_entity is None:
            return

        #Check if there is an 'id' column
        party_id = self._entity_id_column(party_entity)

        LOGGER.debug('Attempting to set %s entity as the party.',
                     party_entity.name)

        if party_id is None:
            err = self.tr('%s does not have an id column. This is required '
                          'in order to link it to the social tenure '
                          'relationship table.'%(party_entity.name))

            LOGGER.debug(err)

            raise AttributeError(err)

        self._party = party_entity

        #Set parent attributes
        self.party_foreign_key.set_entity_relation_attr('parent', self._party)
        self.party_foreign_key.set_entity_relation_attr('parent_column', 'id')

        LOGGER.debug('%s entity has been successfully set as the party in '
                     'the %s profile social tenure relationship.',
                     party_entity.name, self.profile.name)

    @spatial_unit.setter
    def spatial_unit(self, spatial_unit):
        """
        Sets the corresponding spatial unit entity in the social tenure
        relationship.
        :param spatial_unit: Spatial unit entity.
        .. note:: The spatial unit entity must contain a geometry column
        else it will not be set.
        """
        spatial_unit_entity = self._obj_from_str(spatial_unit)

        if spatial_unit_entity is None:
            return

        #check if there is an 'id' column
        sp_unit_id = self._entity_id_column(spatial_unit_entity)

        LOGGER.debug('Attempting to set %s entity as the spatial unit.',
                     spatial_unit_entity.name)

        if sp_unit_id is None:
            err = self.tr('%s does not have an id column. This is required '
                          'in order to link it to the social tenure '
                          'relationship table.'%(spatial_unit_entity.name))

            LOGGER.debug(err)

            raise AttributeError(err)

        if not spatial_unit_entity.has_geometry_column():
            err = self.tr('%s does not have a geometry column. This is required'
                          ' when setting the spatial unit entity in a '
                          'social tenure relationship definition.'
                          %(spatial_unit_entity.name))

            LOGGER.debug(err)

            raise AttributeError(err)

        self._spatial_unit = spatial_unit_entity

        #Set parent attributes
        self.spatial_unit_foreign_key.set_entity_relation_attr('parent',
                                                               self._spatial_unit)
        self.spatial_unit_foreign_key.set_entity_relation_attr(
            'parent_column', 'id')

        LOGGER.debug('%s entity has been successfully set as the spatial unit '
                     'in the %s profile social tenure relationship.',
                     spatial_unit_entity.name, self.profile.name)

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

    def _prepare_tenure_type_value_list(self):
        #Create tenure types lookup table
        tenure_value_list = ValueList(self.tenure_type_list, self.profile)

        #Set lookup column reference value list
        self.tenure_type_lookup.value_list = tenure_value_list

        return tenure_value_list

    def valid(self):
        """
        :return: Returns True if the party and spatial unit entities have
        been set, else returns False.
        :rtype: bool
        """
        if self._party is None:
            return False

        if self._spatial_unit is None:
            return False

        return True

    def create_view(self, engine):
        """
        Creates a basic view linking all the social tenure relationship
        entities.
        :param engine: SQLAlchemy connectable object.
        :type engine: Engine
        """
        self.view_creator(engine)

