"""
Test for asserting spatial unit mapping to the corresponding tenure lookup colum
"""

from unittest import (
    TestCase
)

from stdm.data.configuration.stdm_configuration import StdmConfiguration

from stdm.tests.data.utils import (
    populate_configuration,
    SPATIAL_UNIT_ENTITY_2
)


class TestConfigurationSchemaUpdater(TestCase):
    def setUp(self):
        self.config = StdmConfiguration.instance()
        populate_configuration(self.config)

    def test_spatial_unit_tenure_lookup_column(self):
        # See spatial unit-tenure list mapping defn. in populate_configuration
        social_tenure = list(self.config.profiles.values())[0].social_tenure

        # Get tenure value list
        sec_tenure_vl = social_tenure.spatial_unit_tenure_lookup(
            SPATIAL_UNIT_ENTITY_2
        )
        tenure_col_name = sec_tenure_vl.short_name.replace(
            'check_',
            ''
        ).replace(
            ' ',
            '_').lower()

        # Get tenure lookup column for spatial unit 2
        sec_tenure_lk_col = social_tenure.spatial_unit_tenure_column(
            SPATIAL_UNIT_ENTITY_2
        )

        self.assertEqual(sec_tenure_lk_col.name, tenure_col_name)

    def tearDown(self):
        self.config = None