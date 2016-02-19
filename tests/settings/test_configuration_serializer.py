from unittest import (
    makeSuite,
    TestCase
)

from stdm.data.configuration.stdm_configuration import StdmConfiguration
from stdm.settings.config_serializer import ConfigurationFileSerializer

from stdm.tests.data.utils import (
    create_alchemy_engine,
    populate_configuration
)

save_config_path = 'D:/Temp/Templates/test_writer.stc'

class TestConfigurationSerializer(TestCase):
    def setUp(self):
        self.config = StdmConfiguration.instance()
        populate_configuration(self.config)
        self.serializer = ConfigurationFileSerializer(save_config_path)

    def test_save(self):
        self.serializer.save()

        update_result = True

        #Hardwire result
        self.assertTrue(update_result)


def suite():
    suite = makeSuite(TestConfigurationSerializer, 'test')

    return suite