from qgis.PyQt.QtGui import QDesktopServices

from stdm.settings.config_serializer import ConfigurationFileSerializer
from stdm.settings.registryconfig import (
    CURRENT_PROFILE,
    RegistryConfig,
    ENTITY_BROWSER_RECORD_LIMIT,
    ENTITY_SORT_ORDER
)


def current_profile():
    """
    :return: Returns text on current profile in the configuration currently
    being used.
    :rtype: Profile
    """
    from stdm.data.configuration.stdm_configuration import StdmConfiguration

    reg_config = RegistryConfig()
    profile_info = reg_config.read([CURRENT_PROFILE])
    profile_name = profile_info.get(CURRENT_PROFILE, '')

    # Return None if there is no current profile
    if not profile_name:
        return None

    profiles = StdmConfiguration.instance().profiles

    return profiles.get(str(profile_name), None)


def save_current_profile(name):
    """
    Save the profile with the given name as the current profile.
    :param name: Name of the current profile.
    :type name: unicode
    """
    if not name:
        return

    # Save profile in the registry/settings
    reg_config = RegistryConfig()
    reg_config.write({CURRENT_PROFILE: name})


def save_configuration():
    """
    A util method for saving the configuration instance to the default
    file location.
    """
    config_path = QDesktopServices.storageLocation(QDesktopServices.HomeLocation) \
                  + '/.stdm/configuration.stc'
    conf_serializer = ConfigurationFileSerializer(config_path)
    conf_serializer.save()


def get_entity_browser_record_limit():
    reg_config = RegistryConfig()
    rec_info = reg_config.read([ENTITY_BROWSER_RECORD_LIMIT])
    rec_limit = rec_info.get(ENTITY_BROWSER_RECORD_LIMIT, 10)
    return rec_limit


def save_entity_browser_record_limit(limit):
    """
    type limit:int
    """
    reg_config = RegistryConfig()
    reg_config.write({ENTITY_BROWSER_RECORD_LIMIT: limit})


def get_entity_sort_order():
    reg_config = RegistryConfig()
    rec_info = reg_config.read([ENTITY_SORT_ORDER])
    sort_order = rec_info.get(ENTITY_SORT_ORDER, None)
    return sort_order


def save_entity_sort_order(sort_order):
    """
    :type sort_order: str
    """
    reg_config = RegistryConfig()
    reg_config.write({ENTITY_SORT_ORDER: sort_order})
