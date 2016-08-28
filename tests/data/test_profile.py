from unittest import (
    makeSuite,
    TestCase
)

from stdm.tests.utils import qgis_app

from stdm.data.configuration.stdm_configuration import StdmConfiguration
from stdm.data.configuration.association_entity import AssociationEntity

from stdm.tests.data.utils import (
    add_basic_profile,
    add_household_entity,
    add_person_entity,
    add_spatial_unit_entity,
    append_person_columns,
    BASIC_PROFILE,
    create_person_entity,
    create_relation,
    PERSON_ENTITY,
    set_profile_social_tenure
)


class TestProfile(TestCase):
    def setUp(self):
        self.config = StdmConfiguration.instance()
        self.profile = add_basic_profile(self.config)

    def test_set_social_tenure_attr(self):
        #Add STR entities then define the relationship.
        set_profile_social_tenure(self.profile)

        valid = self.profile.social_tenure.valid()
        self.assertTrue(valid, 'The social tenure relationship in the profile '
                               'is invalid.')

    def test_create_entity_relation(self):
        rel = create_relation(self.profile)
        valid, msg = rel.valid()

        self.assertFalse(valid, msg)

    def _add_household_person_relation(self):
        rel = create_relation(self.profile)
        person_entity = add_person_entity(self.profile)
        append_person_columns(person_entity)
        household_entity = add_household_entity(self.profile)
        rel.parent = household_entity
        rel.child = person_entity
        rel.child_column = 'household_id'
        rel.parent_column = 'id'

        return rel

    def test_add_entity_relation(self):
        rel = self._add_household_person_relation()
        status = self.profile.add_entity_relation(rel)

        self.assertTrue(status, 'Relation was not added.')

    def test_remove_relation(self):
        rel = self._add_household_person_relation()
        self.profile.add_entity_relation(rel)

        status = self.profile.remove_relation(rel.name)

        self.assertTrue(status, 'Relation was not removed.')

    def test_add_entity(self):
        person_entity = add_person_entity(self.profile)
        person_item = self.profile.entity(PERSON_ENTITY)
        self.assertIsNotNone(person_item)

    def test_remove_entity(self):
        person_entity = add_person_entity(self.profile)
        status = self.profile.remove_entity(PERSON_ENTITY)

        self.assertTrue(status)

    def test_create_entity(self):
        entity = create_person_entity(self.profile)
        self.assertIsNotNone(entity, 'None entity created by profile.')

    def test_create_association_entity(self):
        person_entity = add_person_entity(self.profile)
        household_entity = add_household_entity(self.profile)
        assoc_ent = self.profile.create_association_entity('person_household')
        assoc_ent.first_parent = person_entity
        assoc_ent.second_parent = household_entity

        self.profile.add_entity(assoc_ent)

        profile_assoc_entities = self.profile.entities_by_type_info(
            AssociationEntity.TYPE_INFO)

        self.assertGreater(profile_assoc_entities, 0, 'There are no '
                                                      'association entities '
                                                      'in the collection.')

    def test_entities_by_type_info(self):
        person_entity = add_person_entity(self.profile)
        entities = self.profile.entities_by_type_info('ENTITY')
        self.assertGreater(len(entities), 0, 'There no entities of ENTITY '
                                             'type info in the collection.')

    def tearDown(self):
        self.config.remove_profile(BASIC_PROFILE)
        self.profile = None
        self.config = None


def suite():
    suite = makeSuite(TestProfile, 'test')

    return suite