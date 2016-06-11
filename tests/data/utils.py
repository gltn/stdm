from stdm import data

from sqlalchemy import create_engine

from stdm.data.configuration.columns import (
    ForeignKeyColumn,
    GeometryColumn,
    IntegerColumn,
    LookupColumn,
    MultipleSelectColumn,
    VarCharColumn
)
from stdm.data.configuration.entity import entity_factory
from stdm.data.configuration.value_list import value_list_factory
from stdm.data.configuration.social_tenure import SocialTenure

from stdm.data.connection import DatabaseConnection
from stdm.security.user import User

BASIC_PROFILE = 'Basic'
PERSON_ENTITY = 'person'
SPATIAL_UNIT_ENTITY = 'spatial_unit'
HOUSEHOLD_ENTITY = 'household'
SURVEYOR_ENTITY = 'suveyor'

DB_USER = 'postgres'
DB_PASS = 'admin'
DB_PORT = 5467
DB_SERVER = 'localhost'
DB_NAME = 'stdm'

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

def create_surveyor_entity(profile):
    return create_entity(profile, SURVEYOR_ENTITY, **full_entity_opt_args)

def add_surveyor_entity(profile):
    surveyor = create_surveyor_entity(profile)
    profile.add_entity(surveyor)

    return surveyor

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

def create_gender_lookup(entity):
    gender_value_list = create_value_list(entity.profile, 'gender')
    gender_value_list.add_value('Male')
    gender_value_list.add_value('Female')

    return gender_value_list

def append_person_columns(entity):
    household_id = IntegerColumn('household_id', entity)
    first_name = VarCharColumn('first_name', entity, maximum=30)
    last_name = VarCharColumn('last_name', entity, maximum=30)

    #Create gender lookup column and attach value list
    gender = LookupColumn('gender', entity)
    gender_value_list = create_gender_lookup(entity)
    gender.value_list = gender_value_list

    entity.add_column(household_id)
    entity.add_column(first_name)
    entity.add_column(last_name)
    entity.add_column(gender)

def append_surveyor_columns(surveyor):
    first_name = VarCharColumn('first_name', surveyor, maximum=30)
    last_name = VarCharColumn('last_name', surveyor, maximum=30)
    surveyor.add_column(first_name)
    surveyor.add_column(last_name)

def populate_configuration(config):
    profile = add_basic_profile(config)

    rel = create_relation(profile)
    person_entity = add_person_entity(profile)
    append_person_columns(person_entity)
    household_entity = add_household_entity(profile)

    rel.parent = household_entity
    rel.child = person_entity
    rel.child_column = 'household_id'
    rel.parent_column = 'id'

    profile.add_entity_relation(rel)

    #Add save option lookup
    save_options = create_value_list(profile, 'save_options')
    save_options.add_value('House')
    save_options.add_value('Bank')
    save_options.add_value('SACCO')
    profile.add_entity(save_options)

    #Add save options to multiple select column to person entity
    save_options_column = MultipleSelectColumn('save_location', person_entity)
    save_options_column.value_list = save_options
    person_entity.add_column(save_options_column)

    #Append surveyor columns
    surveyor = add_surveyor_entity(profile)
    append_surveyor_columns(surveyor)

    spatial_unit = add_spatial_unit_entity(profile)

    #Add foreign key linking spatial unit to surveyor
    surveyor_id_col = ForeignKeyColumn('surveyor_id', spatial_unit)
    surveyor_id_col.set_entity_relation_attr('parent', surveyor)
    surveyor_id_col.set_entity_relation_attr('parent_column', 'id')
    spatial_unit.add_column(surveyor_id_col)

    #Set STR entities
    profile.set_social_tenure_attr(SocialTenure.PARTY, person_entity)
    profile.set_social_tenure_attr(SocialTenure.SPATIAL_UNIT, spatial_unit)


def create_db_connection():
    db_conn = DatabaseConnection(DB_SERVER, DB_PORT, DB_NAME)
    user = User(DB_USER, DB_PASS)
    db_conn.User = user

    return db_conn

def create_alchemy_engine():
    db_conn = create_db_connection()
    connection_str = db_conn.toAlchemyConnection()

    #Set STDMDb instance
    data.app_dbconn = db_conn

    return create_engine(connection_str, echo=False)

