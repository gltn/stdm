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

from collections import OrderedDict

from stdm.data.configuration.columns import (
    DateColumn,
    ForeignKeyColumn,
    LookupColumn,
    PercentColumn
)
from stdm.data.configuration.exception import ConfigurationException
from stdm.data.configuration.entity import Entity
from stdm.data.configuration.social_tenure_updater import (
    view_deleter,
    view_updater
)
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
    PARTY, SPATIAL_UNIT, SOCIAL_TENURE_TYPE, START_DATE, END_DATE = range(
        0, 5
    )
    BASE_STR_VIEW = 'vw_social_tenure_relationship'
    tenure_type_list = 'tenure_type'
    view_creator = view_updater
    view_remover = view_deleter

    def __init__(self, name, profile, supports_documents=True,
                 layer_display=''):
        Entity.__init__(self, name, profile,
                        supports_documents=supports_documents)

        self.user_editable = False

        self._party = None
        self._spatial_unit = None
        self._view_name = None

        self.party_foreign_key = ForeignKeyColumn('party_id', self)
        self.spatial_unit_foreign_key = ForeignKeyColumn('spatial_unit_id',
                                                         self)
        self.tenure_type_lookup = LookupColumn('tenure_type', self)

        # Added in v1.5
        self.validity_start_column = DateColumn(
            'validity_start',
            self,
            index=True
        )
        self.validity_end_column = DateColumn(
            'validity_end',
            self,
            index=True
        )
        self.tenure_share_column = PercentColumn('tenure_share', self)

        self.layer_display_name = layer_display
        self._value_list = self._prepare_tenure_type_value_list()

        # Add the value list to the table collection
        self.profile.add_entity(self._value_list)

        # Add columns to the collection
        self.add_column(self.spatial_unit_foreign_key)
        self.add_column(self.tenure_type_lookup)
        self.add_column(self.validity_start_column)
        self.add_column(self.validity_end_column)
        self.add_column(self.tenure_share_column)

        # Added in v1.5
        self._party_fk_columns = OrderedDict()
        #Names of party entities that have been removed
        self.removed_parties = []

        # Specify if a spatial unit should only be linked to one party
        self.multi_party = True

        LOGGER.debug('Social Tenure Relationship initialized for %s profile.',
                     self.profile.name)

    def layer_display(self):
        """
        :return: Name to show in the Layers TOC.
        :rtype: str
        """
        if self.layer_display_name:
            return self.layer_display_name

        return self._view_name_from_entity(self.spatial_unit)

    @property
    def parties(self):
        """
        :return: Returns a collection of party entities.
        .. versionadded:: 1.5
        :rtype: list
        """
        return [pc.parent for pc in self._party_fk_columns.values()
                if not pc.parent is None]

    @parties.setter
    def parties(self, parties):
        """
        Adds the collection of parties to the STR definition. Result will
        be suppressed.
        .. versionadded:: 1.5
        :param parties: Collection of party entities.
        :type parties: list
        """
        for p in parties:
            self.add_party(p)

    @property
    def start_date(self):
        """
        :return: Returns a tuple of the minimum and maximum start dates.
        .. versionadded:: 1.5
        ":rtype: tuple(min_start_date, max_start_date)
        """
        return self.validity_start_column.minimum, \
               self.validity_start_column.maximum

    @property
    def end_date(self):
        """
        :return: Returns a tuple of the minimum and maximum end dates.
        .. versionadded:: 1.5
        ":rtype: tuple(min_end_date, max_end_date)
        """
        return self.validity_end_column.minimum, \
               self.validity_end_column.maximum

    @start_date.setter
    def start_date(self, start_date_range):
        """
        Set the minimum and maximum validity start dates.
        :param start_date_range: A tuple containing the minimum and maximum
        dates respectively. This will only be applied in the database if the
        columns have not yet been created.
        .. versionadded:: 1.5
        :type start_date_range: tuple(min_start_date, max_start_date)
        """
        if len(start_date_range) < 2:
            raise ConfigurationException(
                'A tuple of minimum and maximum start dates expected.'
            )
        min_date, max_date = start_date_range[0], start_date_range[1]
        if min_date > max_date:
            raise ConfigurationException(
                'Minimum start date is greater than maximum start date.'
            )

        self.validity_start_column.minimum = min_date
        self.validity_start_column.maximum = max_date

    @end_date.setter
    def end_date(self, end_date_range):
        """
        Set the minimum and maximum validity end dates.
        :param end_date_range: A tuple containing the minimum and maximum
        dates respectively. This will only be applied in the database if the
        columns have not yet been created.
        .. versionadded:: 1.5
        :type end_date_range: tuple(min_end_date, max_end_date)
        """
        if len(end_date_range) < 2:
            raise ConfigurationException(
                'A tuple of minimum and maximum end dates expected.'
            )

        min_date, max_date = end_date_range[0], end_date_range[1]
        if min_date > max_date:
            raise ConfigurationException(
                'Minimum end date is greater than maximum end date.'
            )

        self.validity_end_column.minimum = min_date
        self.validity_end_column.maximum = max_date

    def _view_name_from_entity(self, entity):
        # Construct view name from entity name
        if entity is not None:
            return u'{0}_{1}'.format(
                entity.name,
                SocialTenure.BASE_STR_VIEW
            )

    @property
    def views(self):
        """
        :return: Returns a collection of view names and corresponding primary
        entities for each view. The primary entities include the respective
        party and spatial unit entities in the STR definition.
        .. versionadded:: 1.5
        :rtype: dict(view_name, primary entity)
        """
        v = {}

        for p in self.parties:
            view_name = self._view_name_from_entity(p)
            v[view_name] = p

        #Include spatial unit
        if not self.spatial_unit is None:
            sp_view = self._view_name_from_entity(self.spatial_unit)
            v[sp_view] = self.spatial_unit

        return v

    @property
    def party_columns(self):
        """
        :return: Returns a collection of STR party columns.
        .. versionadded:: 1.5
        :rtype: OrderedDict(column_name, ForeignKeyColumn)
        """
        return self._party_fk_columns

    def add_party(self, party):
        """
        Add a party entity to the collection of STR parties.
        .. versionadded:: 1.5
        :param party: Party entity in STR relationship
        :type party: str or Entity
        :return: Returns True if the party was successfully added, otherwise
        False. If there is an existing party in the STR definition with the
        same name then the function returns False.
        :rtype: bool
        """
        party_entity = self._obj_from_str(party)

        if self._party_in_parties(party_entity):
            return False

        fk_col_name = self._foreign_key_column_name(party_entity)

        party_fk = ForeignKeyColumn(fk_col_name, self)
        party_fk.set_entity_relation_attr('parent', party_entity)
        party_fk.set_entity_relation_attr('parent_column', 'id')

        self._party_fk_columns[fk_col_name] = party_fk
        self.add_column(party_fk)

        LOGGER.debug('%s entity has been successfully added as a party in '
                     'the %s profile social tenure relationship.',
                     party_entity.name, self.profile.name)

    def _foreign_key_column_name(self, party_entity):
        #Appends 'id' suffix to the entity's short name.
        fk_col_name = u'{0}_id'.format(party_entity.short_name.lower())

        return fk_col_name

    def clear_removed_parties(self):
        """
        Clears the collection of STR party entities that have been removed
        from the collection.
        """
        self.removed_parties = []

    def remove_party(self, party):
        """
        Remove a party entity from the existing STR collection.
        .. versionadded:: 1.5
        :param party: Party entity in STR relationship
        :type party: str or Entity
        :return: Returns True if the party was successfully removed,
        otherwise False. If there is no corresponding party in the collection
        then the function returns False.
        :rtype: bool
        """
        party_entity = self._obj_from_str(party)

        if not self._party_in_parties(party_entity):
            return False

        fk_col_name = self._foreign_key_column_name(party_entity)

        #Remove column from the collection
        status = self.remove_column(fk_col_name)
        if not status:
            return False

        #Remove from internal collection
        if fk_col_name in self._party_fk_columns:
            del self._party_fk_columns[fk_col_name]

        self.removed_parties.append(party_entity.short_name)

        return True

    def _party_in_parties(self, party):
        #Check if a party is in the STR collection.
        party_names = [p.name for p in self.parties]

        if party.name in party_names:
            return True

        return False

    def is_str_party_entity(self, entity):
        """
        Checks if the specified entity is a party entity in the social
        tenure relationship definition.
        .. versionadded:: 1.5
        :param entity: Entity to assert if its part of the STR party
        definition.
        :type entity: Entity
        :return: True if the entity is part of the party collection in the
        STR definition, otherwise False.
        :rtype: bool
        """
        return self._party_in_parties(entity)

    def is_str_entity(self, entity):
        """
        Checks if the entity is a spatial or party entity in the STR
        collection.
        :param entity: Entity to assert if its a party or spatial unit.
        :type entity: Entity
        :return:True if the entity is an STR entity in the STR definition,
        otherwise False.
        :rtype: bool
        """
        if self.is_str_party_entity(entity):
            return True

        if entity == self.spatial_unit:
            return True

        return False

    @property
    def view_name(self):
        """
        .. deprecated:: 1.5
        Use :func:`views` instead to get a list of view names.
        """
        return self._view_name

    @property
    def party(self):
        """
        .. deprecated:: 1.5
        Use :func:`parties` instead to get a list of party entities.
        """
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
        """
        .. deprecated:: 1.5
        Use :func:`add_party` instead to get a list of party entities.
        """
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
            spatial_unit_entity = None
            return
            #err = self.tr('%s does not have a geometry column. This is required'
                           #' when setting the spatial unit entity in a '
                           #'social tenure relationship definition.'
                           #%(spatial_unit_entity.name))

            #LOGGER.debug(err)

            #raise AttributeError(err)

        self._spatial_unit = spatial_unit_entity

        #Set parent attributes
        self.spatial_unit_foreign_key.set_entity_relation_attr(
            'parent',
            self._spatial_unit
        )
        self.spatial_unit_foreign_key.set_entity_relation_attr(
            'parent_column',
            'id'
        )

        LOGGER.debug('%s entity has been successfully set as the spatial '
                     'unit in the %s profile social tenure relationship.',
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
        if len(self._party_fk_columns) == 0:
            return False

        if self._spatial_unit is None:
            return False

        return True

    def delete_view(self, engine):
        """
        Deletes the basic view associated with the current social tenure
        object.
        :param engine: SQLAlchemy connectable object.
        :type engine: Engine
        """
        self.view_remover(engine)

    def create_view(self, engine):
        """
        Creates a basic view linking all the social tenure relationship
        entities.
        :param engine: SQLAlchemy connectable object.
        :type engine: Engine
        """
        self.view_creator(engine)

