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
    PercentColumn,
    VarCharColumn
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
    CUSTOM_ATTRS_ENTITY = 'attrs'
    tenure_type_list = 'tenure_type'
    CUSTOM_TENURE_DUMMY_COLUMN = 'dummy_custom_str'
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
        self.spatial_unit_foreign_key = ForeignKeyColumn(
            'spatial_unit_id',
            self
        )
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
        self.add_column(self.tenure_type_lookup)
        self.add_column(self.validity_start_column)
        self.add_column(self.validity_end_column)
        self.add_column(self.tenure_share_column)

        # Added in v1.5
        self._party_fk_columns = OrderedDict()
        # Names of party entities that have been removed
        self.removed_parties = []

        # Added in v1.7
        self._spatial_unit_fk_columns = OrderedDict()

        # Mapping of spatial units and corresponding tenure types
        self._sp_units_tenure = {}

        # Mapping of tenure type lookup columns
        self._tenure_type_sec_lk_columns = {}

        # Tenure type custom attribute entities
        # key: tenure lookup short name
        # value: custom attributes entity
        self._custom_attr_entities = {}

        # Specify if a spatial unit should only be linked to one party
        self.multi_party = True

        LOGGER.debug('Social Tenure Relationship initialized for %s profile.',
                     self.profile.name)

    @property
    def custom_attribute_entities(self):
        """
        :return: Returns the collection of custom attribute entities.
        .. versionadded:: 1.7
        :rtype: dict(str, Entity)
        """
        return self._custom_attr_entities

    def has_custom_attribute_entities(self):
        """
        :return: Returns True if there exists a custom tenure attributes
        entity, otherwise False.
        .. versionadded:: 1.7
        :rtype: bool
        """
        if len(self.custom_attributes_entities) == 0:
            return False

        return True

    def _custom_attributes_entity_name(self, t_type_s_name):
        # Build entity name using tenure type short name
        return u'{0}_{1}_{2}'.format(
            t_type_s_name,
            'str',
            self.CUSTOM_ATTRS_ENTITY
        )

    def initialize_custom_attributes_entity(self, tenure_lookup):
        """
        Creates a custom user attributes entity and adds a foreign key
        column for linking the two entities.
        .. versionadded:: 1.7
        :param tenure_lookup: Valuelist containing tenure types.
        :type tenure_lookup: str or ValueList
        :return: Returns the custom attributes entity. A new one is created
        if did not exist otherwise the an existing one is returned. The
        entity needs to be added manually to the registry.
        :rtype: Entity
        """
        tenure_lookup = self._obj_from_str(tenure_lookup)
        custom_ent_name = self._custom_attributes_entity_name(
            tenure_lookup.short_name
        )
        custom_ent = self.profile.entity(custom_ent_name)

        # Created only if it does not exist
        if custom_ent is None:
            custom_ent = Entity(
                custom_ent_name,
                self.profile,
                supports_documents=False
            )
            custom_ent.user_editable = False
            # Column for linking with primary tenure table
            str_col = ForeignKeyColumn('social_tenure_relationship_id', custom_ent)
            str_col.set_entity_relation_attr('parent', self)
            str_col.set_entity_relation_attr('parent_column', 'id')
            custom_ent.add_column(str_col)

        # Validate existence of dummy column
        self._validate_custom_attr_dummy_column(custom_ent)

        return custom_ent

    def _validate_custom_attr_dummy_column(self, custom_entity):
        # Check if the dummy column has been added to the custom tenure entity
        # Insert dummy column so that the table is not flagged as a m2m
        dummy_col = custom_entity.column(self.CUSTOM_TENURE_DUMMY_COLUMN)
        if dummy_col is None:
            dummy_col = VarCharColumn(
                self.CUSTOM_TENURE_DUMMY_COLUMN,
                custom_entity,
                maximum=1
            )
            custom_entity.add_column(dummy_col)

    def add_tenure_attr_custom_entity(self, tenure_lookup, entity):
        """
        Adds a mapping that links the tenure lookup to the custom attributes
        entity.
        :param tenure_lookup: Valuelist containing tenure types.
        :type tenure_lookup: str or ValueList
        :param entity: Custom attributes entity.
        :type entity: str or Entity
        """
        tenure_lookup = self._obj_from_str(tenure_lookup)
        entity = self._obj_from_str(entity)

        # Validate existence of dummy column
        self._validate_custom_attr_dummy_column(entity)

        self._custom_attr_entities[tenure_lookup.short_name] = entity

    def custom_attribute_entity(self, tenure_lookup):
        """
        Get the custom attribute entity.
        .. versionadded:: 1.7
        :param tenure_lookup: Tenure type valuelist.
        :type tenure_lookup: str or ValueList
        :return: Returns the custom attributes entity corresponding to the
        given tenure type. None if not found.
        :rtype: Entity
        """
        t_type = self._obj_from_str(tenure_lookup)

        return self._custom_attr_entities.get(t_type.short_name, None)

    def spu_custom_attribute_entity(self, spu):
        """
        Retrieves the custom attributes entity for the given spatial unit.
        .. versionadded:: 1.7
        :param spu: Spatial unit entity.
        :type spu: str or Entity
        :return: Returns the custom attributes entity for the given spatial
        unit, None if not found.
        :rtype: Entity
        """
        t_type = self.spatial_unit_tenure_lookup(spu)

        if t_type is None:
            return None

        return self.custom_attribute_entity(t_type)

    def remove_custom_attributes_entity(self, tenure_lookup):
        """
        Removes the custom attributes entity that corresponds to the given
        tenure lookup.
        .. versionadded:: 1.7
        :param tenure_lookup: Tenure type valuelist.
        :type tenure_lookup: ValueList
        :returns: True if the entity was successfully removed, otherwise False.
        :rtype: bool
        """
        custom_ent_name = self._custom_attributes_entity_name(
            tenure_lookup.short_name
        )

        return self.profile.remove_entity(custom_ent_name)

    def remove_custom_attributes_entity_by_spu(self, spu):
        """
        Removes the custom attributes entity that corresponds to the given
        spatial unit.
        .. versionadded:: 1.7
        :param tenure_lookup: Spatial unit entity.
        :type tenure_lookup: Entity
        :returns: True if the entity was successfully removed, otherwise False.
        :rtype: bool
        """
        t_type = self.spatial_unit_tenure_lookup(spu)
        if t_type is None:
            return False

        return self.remove_custom_attributes_entity(t_type)

    def layer_display(self):
        """
        :return: Name to show in the Layers TOC.
        .. deprecated:: 1.5
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
    def spatial_units(self):
        """
        :return: Returns a collection of spatial unit entities.
        .. versionadded:: 1.7
        :rtype: list
        """
        return [sp.parent for sp in self._spatial_unit_fk_columns.values()
                if not sp.parent is None]

    @spatial_units.setter
    def spatial_units(self, sp_units):
        """
        Adds the collection of spatial units to the STR definition. Result
        will be suppressed.
        .. versionadded:: 1.7
        :param sp_units: Collection of spatial unit entities.
        :type sp_units: list
        """
        for sp in sp_units:
            self.add_spatial_unit(sp)

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

        # Include spatial units
        for sp in self.spatial_units:
            sp_view = self._view_name_from_entity(sp)
            v[sp_view] = sp

        return v

    @property
    def spatial_unit_columns(self):
        """
        :return: Returns a collection of STR spatial unit columns.
        .. versionadded: 1.7
        :rtype: OrderedDict(column_name, ForeignKeyColumn)
        """
        return self._spatial_unit_fk_columns

    def add_spatial_unit(self, spatial_unit):
        """
        Add a spatial unit entity to the collection of STR parties.
        .. versionadded:: 1.7
        :param spatial_unit: Spatial unit entity in STR relationship.
        :type spatial_unit: str or Entity
        :return: Returns True if the spatial unit was successfully added,
        otherwise False. If there is an existing spatial unit in the STR
        definition with the same name or no geometry column then the
        function returns False.
        :rtype: bool
        """
        sp_unit_entity = self._obj_from_str(spatial_unit)

        if sp_unit_entity is None:
            return False

        if self._sp_unit_in_sp_units(sp_unit_entity):
            return False

        if not sp_unit_entity.has_geometry_column():
            return False

        fk_col_name = self._foreign_key_column_name(sp_unit_entity)

        sp_unit_fk = ForeignKeyColumn(fk_col_name, self)
        sp_unit_fk.on_delete_action = ForeignKeyColumn.CASCADE
        sp_unit_fk.set_entity_relation_attr('parent', sp_unit_entity)
        sp_unit_fk.set_entity_relation_attr('parent_column', 'id')

        self._spatial_unit_fk_columns[fk_col_name] = sp_unit_fk
        self.add_column(sp_unit_fk)

        # Link spatial unit to the default tenure type lookup
        self.add_spatial_tenure_mapping(
            sp_unit_entity,
            self.tenure_type_collection
        )

        LOGGER.debug('%s entity has been successfully added as a spatial '
                     'unit in the %s profile social tenure relationship.',
                     sp_unit_entity.name, self.profile.name)

        return True

    def remove_spatial_unit(self, spatial_unit):
        """
        Remove a spatial unit entity from the STR collection.
        .. versionadded:: 1.7
        :param spatial_unit: Spatial unit entity in STR relationship
        :type spatial_unit: str or Entity
        :return: Returns True if the spatial unit was successfully removed,
        otherwise False. If there is no corresponding spatial unit in the
        collection then the function returns False.
        :rtype: bool
        """
        sp_unit_entity = self._obj_from_str(spatial_unit)

        if sp_unit_entity is None:
            return False

        if not self._sp_unit_in_sp_units(sp_unit_entity):
            return False

        fk_col_name = self._foreign_key_column_name(sp_unit_entity)

        # Remove tenure mapping associated with the spatial unit
        self.remove_spatial_unit_tenure_mapping(sp_unit_entity)

        # Remove column from the collection
        status = self.remove_column(fk_col_name)
        if not status:
            return False

        # Remove from internal collection
        if fk_col_name in self._spatial_unit_fk_columns:
            del self._spatial_unit_fk_columns[fk_col_name]

        return True

    @property
    def spatial_units_tenure(self):
        """
        :return: Returns a collection of spatial unit names and the
        corresponding lookup tables containing the valid tenure types.
        :rtype: dict
        """
        return self._sp_units_tenure

    def add_spatial_tenure_mapping(self, spatial_unit, tenure_lookup):
        """
        Sets the tenure type lookup for the specified spatial unit. Any
        previous mapping for the spatial unit is overridden.
        .. versionadded:: 1.7
        :param spatial_unit: Spatial unit entity
        :type spatial_unit: str or Entity
        :param tenure_lookup: Tenure type lookup
        :type tenure_lookup: str or ValueList
        """
        sp_unit = self._obj_from_str(spatial_unit)

        if sp_unit is None:
            sp_unit_name = spatial_unit
        else:
            sp_unit_name = sp_unit.short_name
        tenure_vl = self._obj_from_str(tenure_lookup)

        # Use short name as key in the collection
        self._sp_units_tenure[sp_unit_name] = tenure_vl

        # Add tenure type lookup column to the collection
        if tenure_vl == self.tenure_type_collection:
            tenure_lk_col = self.tenure_type_lookup
        else:
            tenure_lk_col = self._create_tenure_type_lookup_column(tenure_vl)
            self.add_column(tenure_lk_col)

        self._tenure_type_sec_lk_columns[tenure_vl.short_name] = tenure_lk_col

    def _create_tenure_type_lookup_column(self, tenure_vl):
        # Returns a lookup column whose parent is the given tenure value list.
        col_name = tenure_vl.short_name.replace('check_', '').replace(
            ' ',
            '_'
        ).lower()
        tenure_lookup_col = LookupColumn(col_name, self)
        tenure_lookup_col.value_list = tenure_vl

        return tenure_lookup_col

    def spatial_unit_tenure_lookup(self, spatial_unit):
        """
        Retrieves the tenure lookup for the given spatial unit.
        .. versionadded:: 1.7
        :param spatial_unit: Spatial unit whose corresponding tenure lookup
        is to be retrieved.
        :type spatial_unit: str or Entity
        :return: Returns the tenure lookup for the given spatial unit,
        otherwise None.
        :rtype: ValueList
        """
        sp_unit = self._obj_from_str(spatial_unit)

        return self._sp_units_tenure.get(sp_unit.short_name, None)

    def remove_spatial_unit_tenure_mapping(self, spatial_unit):
        """
        Removes the tenure lookup linkage for the given spatial unit.
        .. versionadded:: 1.7
        :param spatial_unit: Spatial unit whose corresponding tenure lookup
        reference is to be removed.
        :type spatial_unit: str or Entity
        :return: Returns True is the delinking was successful, otherwise
        False. False if there was no existing link to be removed.
        :rtype: False
        """
        sp_unit = self._obj_from_str(spatial_unit)

        if sp_unit.short_name in self._sp_units_tenure:
            tenure_vl = self._sp_units_tenure[sp_unit.short_name]

            del self._sp_units_tenure[sp_unit.short_name]

            # Remove custom attributes entity associated with the tenure type
            self.remove_custom_attributes_entity_by_spu(sp_unit)

            # Check if the tenure value list is defined for other spatial
            # units.
            remove_column = True
            for tvl in self._sp_units_tenure.values():
                if tvl.name == tenure_vl.name:
                    remove_column = False

            # Remove tenure lookup column
            if remove_column:
                vl_short_name = tenure_vl.short_name
                if vl_short_name in self._tenure_type_sec_lk_columns:
                    rm_lk_col = self._tenure_type_sec_lk_columns[vl_short_name]

                    # Delink column
                    del self._tenure_type_sec_lk_columns[vl_short_name]

                    self.remove_column(rm_lk_col)

            return True

        return False

    def spatial_unit_tenure_column(self, spatial_unit):
        """
        Search and retrieve the lookup column corresponding to the given
        spatial unit.
        .. versionadded:: 1.7
        :param spatial_unit: Spatial unit entity
        :type spatial_unit: str or Entity
        :return: Returns the tenure lookup column corresponding to the
        given spatial unit, otherwise None if there is no existing mapping.
        :rtype: LookupColumn
        """
        tenure_vl = self.spatial_unit_tenure_lookup(spatial_unit)

        if tenure_vl is None:
            return None

        return self._tenure_type_sec_lk_columns.get(
            tenure_vl.short_name,
            None
        )

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

        if party_entity is None:
            return False

        if self._party_in_parties(party_entity):
            return False

        fk_col_name = self._foreign_key_column_name(party_entity)

        party_fk = ForeignKeyColumn(fk_col_name, self)
        party_fk.on_delete_action = ForeignKeyColumn.CASCADE
        party_fk.set_entity_relation_attr('parent', party_entity)
        party_fk.set_entity_relation_attr('parent_column', 'id')

        self._party_fk_columns[fk_col_name] = party_fk
        self.add_column(party_fk)

        LOGGER.debug('%s entity has been successfully added as a party in '
                     'the %s profile social tenure relationship.',
                     party_entity.name, self.profile.name)

        return True

    def _foreign_key_column_name(self, entity):
        # Appends 'id' suffix to the entity's short name.

        fk_col_name = u'{0}_id'.format(entity.short_name.lower()).replace(
            ' ', '_'
        )

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

        if party_entity is None:
            return False

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
        # Check if a party is in the STR collection.
        if party is None:
            return False
        party = self._obj_from_str(party)
        party_names = [p.name for p in self.parties]

        if party.name in party_names:
            return True

        return False

    def _sp_unit_in_sp_units(self, spatial_unit):
        # Check if a party is in the STR collection.
        spatial_unit = self._obj_from_str(spatial_unit)
        sp_unit_names = [s.name for s in self.spatial_units]

        if spatial_unit.name in sp_unit_names:
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

    def is_str_spatial_unit_entity(self, entity):
        """
        Checks if the specified entity is a spatial unit entity in the
        social tenure relationship definition.
        .. versionadded:: 1.7
        :param entity: Entity to assert if its part of the STR spatial unit
        definition.
        :type entity: Entity
        :return:  Returns True if the entity is part of the spatial unit
        collection in the STR definition, otherwise False.
        :rtype: bool
        """
        return self._sp_unit_in_sp_units(entity)

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

        if self.is_str_spatial_unit_entity(entity):
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
        """
        .. deprecated:: 1.7
        Use :func:`spatial_units` instead to get a list of spatial unit
        entities.
        """
        return self._spatial_unit

    @property
    def tenure_type_collection(self):
        """
        :return: Returns the primary tenure lookup.
        :rtype: ValueList
        """
        return self._value_list

    @tenure_type_collection.setter
    def tenure_type_collection(self, value_list):
        # Copy the look up values from the given value list
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
        .. deprecated:: 1.7
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

        if isinstance(item, str):
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

        if len(self._spatial_unit_fk_columns) == 0:
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

