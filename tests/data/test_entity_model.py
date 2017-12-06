from unittest import (
    makeSuite,
    TestCase
)
from datetime import datetime

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

        savings_col = party_ent.column('savings')
        savings_ent = savings_col.value_list

        #Create savings value list object
        savings_cls = entity_model(savings_ent)
        savings_obj = savings_cls()
        savings = []

        res = savings_obj.queryObject().all()
        savings = [r for r in res]

        #Set attributes
        party.number = 'FK09'
        party.first_name = 'Jermaine'
        party.last_name = 'Jackson'

        #Append all savings options
        setattr(party, 'ru_check_saving_options_collection', savings)

        #party.save()

        #Hardwire result
        read_result = False
        self.assertTrue(read_result)
`

def populate_supporting_document(supporting_document):
    #Set basic attributes of the supporting document
    supporting_document.creation_date = datetime.now()
    supporting_document.document_identifier = 'E183E0CC-6BBF-4A80-A3D8-38C162EAE225'
    supporting_document.document_size = '543908'
    supporting_document.filename = 'Sample Document.png'

def suite():
    suite = makeSuite(TestEntityModelFunc, 'test')

    return suite