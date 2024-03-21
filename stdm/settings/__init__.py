from qgis.PyQt.QtCore import QStandardPaths

from stdm.data.configuration.profile import Profile
from stdm.settings.config_serializer import ConfigurationFileSerializer
from stdm.settings.registryconfig import (
    CURRENT_PROFILE,
    RegistryConfig,
    ENTITY_BROWSER_RECORD_LIMIT,
    ENTITY_SORT_ORDER,
    LOG_MODE

)



def current_profile() -> Profile:
    """
    :returns current Profile object in the configuration currently being used.
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


def save_current_profile(name: str):
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
    config_path = QStandardPaths.standardLocations(QStandardPaths.HomeLocation)[0] \
                  + '/.stdm/configuration.stc'
    conf_serializer = ConfigurationFileSerializer(config_path)
    conf_serializer.save()


def get_entity_browser_record_limit() -> int:
    reg_config = RegistryConfig()
    rec_info = reg_config.read([ENTITY_BROWSER_RECORD_LIMIT])
    rec_limit = int(rec_info.get(ENTITY_BROWSER_RECORD_LIMIT, 10000))
    return rec_limit


def save_entity_browser_record_limit(limit: int):
    """
    type limit:int
    """
    reg_config = RegistryConfig()
    reg_config.write({ENTITY_BROWSER_RECORD_LIMIT: limit})

def save_log_mode(log_mode: str):
    reg_config = RegistryConfig()
    reg_config.write({LOG_MODE: log_mode})


def get_entity_sort_details(group_name: str, entity_name: str) -> str:
    reg_config = RegistryConfig()
    sort_details = reg_config.get_value(group_name, entity_name)
    return sort_details


def save_entity_sort_order(sort_order: str):
    """
    :type sort_order: str
    """
    reg_config = RegistryConfig()
    reg_config.write({ENTITY_SORT_ORDER: sort_order})
