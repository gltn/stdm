from unittest import (
    makeSuite,
    TestCase
)

from stdm.data.configuration.stdm_configuration import StdmConfiguration
from stdm.data.configuration import entity_model
from stdm.settings.config_serializer import ConfigurationFileSerializer

from stdm.tests.data.utils import (
    create_alchemy_engine,
    populate_configuration
)

config_path = 'C:/Users/John/.stdm/configuration.stc'

class TestEntityModelFunc(TestCase):
    def setUp(self):
        self.config = StdmConfiguration.instance()
        self.serializer = ConfigurationFileSerializer(config_path)

    def tearDown(self):
        self.config = None

    def test_exec_(self):
        engine = create_alchemy_engine()
        self.serializer.load()

        profile = self.config.profile('Rural')
        party_ent = profile.social_tenure.party

        #Map entity to SQLAlchemy class
        party_cls = entity_model(party_ent)
        party = party_cls()

        #Set attributes
        party.number = 'FK09'
        party.first_name = 'Jermaine'
        party.last_name = 'Jackson'

        #party.save()

        read_result = False
        #Hardwire result
        self.assertTrue(read_result)


def suite():
    suite = makeSuite(TestEntityModelFunc, 'test')

    return suite