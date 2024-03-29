import unittest
from unittest import (
    makeSuite,
    TestCase
)

from stdm.data.configuration.stdm_configuration import StdmConfiguration
from stdm.settings.config_serializer import ConfigurationFileSerializer
from stdm.tests.data.utils import (
    populate_configuration
)

config_path = 'D:/Temp/Templates/test_writer.stc'


@unittest.skip('written for local use only')
class TestConfigurationSerializer(TestCase):
    def setUp(self):
        self.config = StdmConfiguration.instance()
        self.serializer = ConfigurationFileSerializer(config_path)

    def tearDown(self):
        self.config = None

    def test_save(self):
        populate_configuration(self.config)

        self.serializer.save()

        update_result = True

        self.assertTrue(update_result)

    def test_load(self):
        self.serializer.load()

        read_result = True

        self.assertTrue(read_result)


def suite():
    suite = makeSuite(TestConfigurationSerializer, 'test')

    return suite
