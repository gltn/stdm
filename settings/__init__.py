from PyQt4.QtGui import QDesktopServices

from stdm.settings.registryconfig import (
    CURRENT_PROFILE,
    RegistryConfig
)
from stdm.settings.config_serializer import ConfigurationFileSerializer


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

    #Return None if there is no current profile
    if not profile_name:
        return None

    profiles = StdmConfiguration.instance().profiles

    return profiles.get(unicode(profile_name), None)


def save_current_profile(name):
    """
    Save the profile with the given name as the current profile.
    :param name: Name of the current profile.
    :type name: unicode
    """
    if not name:
        return

    #Save profile in the registry/settings
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