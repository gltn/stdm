import unittest
from unittest import (
    makeSuite,
    TestCase
)

from stdm.data.configuration.config_updater import ConfigurationSchemaUpdater
from stdm.data.configuration.stdm_configuration import StdmConfiguration
from stdm.tests.data.utils import (
    create_alchemy_engine,
    populate_configuration
)


@unittest.skip('written for local use only')
class TestConfigurationSchemaUpdater(TestCase):
    def setUp(self):
        self.config = StdmConfiguration.instance()
        populate_configuration(self.config)

    def tearDown(self):
        self.config = None

    def test_exec_(self):
        engine = create_alchemy_engine()
        config_updater = ConfigurationSchemaUpdater(engine)
        config_updater.update_completed.connect(self._on_complete)
        config_updater.exec_()

    def _on_complete(self, result):
        self.assertTrue(result)


def suite():
    suite = makeSuite(TestConfigurationSchemaUpdater, 'test')

    return suite
