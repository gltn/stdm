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

from .columns import ForeignKeyColumn
from .entity import Entity

LOGGER = logging.getLogger('stdm')


class SocialTenure(Entity):
    """
    Represents the relationship between party and spatial unit entities
    through social tenure relationship. It also supports the attachment of
    supporting documents.
    Main class that represents 'people-land' relationships.
    """
    TYPE_INFO = 'SOCIAL_TENURE'
    PARTY, SPATIAL_UNIT = range(0,2)

    def __init__(self, name, profile, supports_documents=True):
        Entity.__init__(self, name, profile,
                        supports_documents=supports_documents)

        self._party = None
        self._spatial_unit = None

        self.party_foreign_key = None
        self.spatial_unit_foreign_key = None
        self.tenure_type_foreign_key = None

        LOGGER.debug('Social Tenure Relationship initialized for %s profile.',
                     self.profile.name)

    @property
    def party(self):
        return self._party

    @property
    def spatial_unit(self):
        return self._spatial_unit

    @party.setter
    def party(self, party):
        party_entity = self._obj_from_str(party)

        if party_entity is None:
            return

        #check if there is an 'id' column
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

        #Create foreign key reference
        self.party_foreign_key = ForeignKeyColumn('party_id', self)

        #Set parent attributes
        self.party_foreign_key.set_entity_relation_attr('parent', self._party)
        self.party_foreign_key.set_entity_relation_attr('parent_column', 'id')

        LOGGER.debug('%s entity has been successfully set as the party in '
                     'the %s profile social tenure relationship.',
                     party_entity.name, self.profile.name)

    @spatial_unit.setter
    def spatial_unit(self, spatial_unit):
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

        self._spatial_unit = spatial_unit_entity

        #Create foreign key reference
        self.spatial_unit_foreign_key = ForeignKeyColumn('spatial_unit_id',
                                                         self)

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

