from stdm.data.configuration.columns import (
    GeometryColumn,
    IntegerColumn
)
from stdm.data.configuration.entity import entity_factory
from stdm.data.configuration.value_list import value_list_factory
from stdm.data.configuration.social_tenure import SocialTenure

BASIC_PROFILE = 'Basic'
PERSON_ENTITY = 'person'
SPATIAL_UNIT_ENTITY = 'spatial_unit'
HOUSEHOLD_ENTITY = 'household'

full_entity_opt_args = {
    'create_id_column': True,
    'supports_documents': True,
    'is_global': False,
    'is_proxy': False
}

def create_profile(config, name):
    return config.create_profile(name)

def create_entity(profile, name, **kwargs):
    return profile.create_entity(name, entity_factory, **kwargs)

def create_value_list(profile, name):
    return profile.create_entity(name, value_list_factory)

def create_basic_profile(config):
    return create_profile(config, 'Basic')

def add_basic_profile(config):
    basic_profile = create_basic_profile(config)
    config.add_profile(basic_profile)

    return basic_profile

def create_person_entity(profile):
    entity = create_entity(profile, PERSON_ENTITY, **full_entity_opt_args)

    return entity

def create_spatial_unit_entity(profile):
    entity = create_entity(profile, SPATIAL_UNIT_ENTITY, **full_entity_opt_args)
    add_geometry_column('geom_poly', entity)

    return entity

def add_person_entity(profile):
    entity = create_person_entity(profile)
    profile.add_entity(entity)

    return entity

def add_spatial_unit_entity(profile):
    entity = create_spatial_unit_entity(profile)
    profile.add_entity(entity)

    return entity

def add_geometry_column(name, entity):
    geom_col = GeometryColumn(name, entity, GeometryColumn.POLYGON)
    entity.add_column(geom_col)

    return geom_col

def set_profile_social_tenure(profile):
    party = add_person_entity(profile)
    spatial_unit = add_spatial_unit_entity(profile)

    profile.set_social_tenure_attr(SocialTenure.PARTY, party)
    profile.set_social_tenure_attr(SocialTenure.SPATIAL_UNIT, spatial_unit)

def create_relation(profile, **kwargs):
    return profile.create_entity_relation(**kwargs)

def create_household_entity(profile):
    entity = create_entity(profile, HOUSEHOLD_ENTITY, **full_entity_opt_args)

    return entity

def add_household_entity(profile):
    entity = create_household_entity(profile)
    profile.add_entity(entity)

    return entity

def append_person_columns(entity):
    household_id = IntegerColumn('household_id', entity)
    entity.add_column(household_id)