from unittest import (
    makeSuite,
    TestCase
)

from stdm import StdmConfiguration

from .utils import (
    add_basic_profile,
    create_basic_profile
)

class TestStdmConfiguration(TestCase):
    def setUp(self):
        self.config = StdmConfiguration.instance()

    def test_add_profile(self):
        add_basic_profile(self.config)
        self.assertEqual(len(self.config.profiles), 1)

    def test_create_profile(self):
        profile = create_basic_profile(self.config)
        self.assertEqual(profile.name, 'Basic')

    def test_remove_profile(self):
        add_basic_profile(self.config)
        status = self.config.remove_profile('Basic')
        self.assertTrue(status)

    def test_profile(self):
        add_basic_profile(self.config)
        profile = self.config.profile('Basic')
        self.assertEqual(profile.name, 'Basic')

    def test_prefixes(self):
        add_basic_profile(self.config)
        prefixes = self.config.prefixes()
        prfx = prefixes[0]
        self.assertEqual(prfx, 'ba')

    def tearDown(self):
        self.config = None

def suite():
    suite = makeSuite(TestStdmConfiguration, 'test')

    return suite