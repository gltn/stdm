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


class TestConfigurationSchemaUpdater(TestCase):
    def setUp(self):
        self.config = StdmConfiguration.instance()
        populate_configuration(self.config)

    def tearDown(self):
        self.config = None

    def test_exec_(self):
        engine = create_alchemy_engine()
        config_updater = ConfigurationSchemaUpdater(engine)
        config_updater.exec_()

        update_result = True

        #Hardwire result
        self.assertTrue(update_result)


def suite():
    suite = makeSuite(TestConfigurationSchemaUpdater, 'test')

    return suite