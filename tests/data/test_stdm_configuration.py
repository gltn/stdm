from unittest import TestCase

from stdm.data.configuration.stdm_configuration import StdmConfiguration

class TestStdmConfiguration(TestCase):
    def setUp(self):
        self.config = StdmConfiguration.instance()

    def test_add_profile(self):
        self._add_profile()
        self.assertEqual(len(self.config.profiles), 1)

    def test_create_profile(self):
        profile = self._create_basic_profile()
        self.assertEqual(profile.name, 'Basic')

    def test_remove_profile(self):
        self._add_profile()
        status = self.config.remove_profile('Basic')
        self.assertTrue(status)

    def test_profile(self):
        self._add_profile()
        profile = self.config.profile('Basic')
        self.assertEqual(profile.name, 'Basic')

    def test_prefixes(self):
        self._add_profile()
        prefixes = self.config.prefixes()
        prfx = prefixes[0]
        self.assertEqual(prfx, 'ba')

    def tearDown(self):
        self.config.cleanUp()

    def _create_basic_profile(self):
        return self.config.create_profile('Basic')

    def _add_profile(self):
        profile = self._create_basic_profile()
        self.config.add_profile(profile)