from PyQt4.QtGui import QDesktopServices

from stdm.settings.registryconfig import (
    CURRENT_PROFILE,
    RegistryConfig,
    ENTITY_BROWSER_RECORD_LIMIT,
    IMPORT_MAPFILE,
    #Edited By strabzounly 03-may-2022 >- Deleted cbCountry >- ENUM_COUNTRY,
    TRANS_PATH,
    MEDIA_URL,
    KOBO_USER,
    KOBO_PASS,
    SAVE_CREDIT_OPTION,
    FAMILY_PHOTO,
    SIGN_PHOTO,
    HOUSE_PHOTO,
    HOUSE_PICTURE,
    ID_PICTURE,
    SCANNED_DOC,
    SCANNED_HSE_MAP,
    SCANNED_HSE_PIC,
    SCANNED_ID_DOC,
    ENTITY_SORT_ORDER
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
    reg_config.write({ENTITY_BROWSER_RECORD_LIMIT:limit})

def get_primary_mapfile():
    reg_config = RegistryConfig()
    mapfile = reg_config.read([IMPORT_MAPFILE])
    import_mapfile = mapfile.get(IMPORT_MAPFILE, '')
    return import_mapfile

def get_entity_sort_order():
    reg_config = RegistryConfig()
    rec_info = reg_config.read([ENTITY_SORT_ORDER])
    sort_order = rec_info.get(ENTITY_SORT_ORDER, None)
    return sort_order

def save_entity_sort_order(sort_order):
    reg_config = RegistryConfig()
    reg_config.write({ENTITY_SORT_ORDER:sort_order})

def save_import_mapfile(mapfile):
    reg_config = RegistryConfig()
    reg_config.write({IMPORT_MAPFILE:mapfile})

"""Edited By strabzounly 03-may-2022 >- Deleted cbCountry >- Edit Start
def save_enum_country(country):
    reg_config = RegistryConfig()
    reg_config.write({ENUM_COUNTRY:country})

def get_enum_country():
    reg_config = RegistryConfig()
    enum_country_key = reg_config.read([ENUM_COUNTRY])
    enum_country = enum_country_key.get(ENUM_COUNTRY, '')
    return enum_country
Edit End """

def get_trans_path():
    reg_config = RegistryConfig()
    trans_path_key = reg_config.read([TRANS_PATH])
    trans_path = trans_path_key.get(TRANS_PATH, '')
    return trans_path

def save_trans_path(trans_path):
    reg_config = RegistryConfig()
    reg_config.write({TRANS_PATH: trans_path})


def get_key_value(regkey):
    reg_config = RegistryConfig()
    key = reg_config.read([regkey])
    key_value = key.get(regkey, '')
    return key_value

def save_key_value(key, key_value):
    reg_config = RegistryConfig()
    reg_config.write({key: key_value})

def get_media_url():
    return get_key_value(MEDIA_URL)

def get_kobo_user():
    return get_key_value(KOBO_USER)

def get_kobo_pass():
    return get_key_value(KOBO_PASS)

def get_save_credit_option():
    return get_key_value(SAVE_CREDIT_OPTION)

def get_family_photo():
    return get_key_value(FAMILY_PHOTO)

def get_sign_photo():
    return get_key_value(SIGN_PHOTO)

def get_house_photo():
    return get_key_value(HOUSE_PHOTO)

def get_house_pic():
    return get_key_value(HOUSE_PICTURE)

def get_id_pic():
    return get_key_value(ID_PICTURE)

def get_scanned_doc():
    return get_key_value(SCANNED_DOC)

def get_scanned_hse_map():
    return get_key_value(SCANNED_HSE_MAP)

def get_scanned_hse_pic():
    return get_key_value(SCANNED_HSE_PIC)

def get_scanned_id_doc():
    return get_key_value(SCANNED_ID_DOC)

def save_media_url(value):
    save_key_value(MEDIA_URL, value)

def save_kobo_user(value):
    save_key_value(KOBO_USER, value)

def save_kobo_pass(value):
    save_key_value(KOBO_PASS, value)

def save_credit_option(value):
    save_key_value(SAVE_CREDIT_OPTION, value)

def save_family_photo(value):
    save_key_value(FAMILY_PHOTO, value)

def save_sign_photo(value):
    save_key_value(SIGN_PHOTO, value)

def save_house_photo(value):
    save_key_value(HOUSE_PHOTO, value)

def save_house_pic(value):
    save_key_value(HOUSE_PICTURE, value)

def save_id_pic(value):
    save_key_value(ID_PICTURE, value)

def save_scanned_doc(value):
    save_key_value(SCANNED_DOC, value)

def save_scanned_hse_map(value):
    save_key_value(SCANNED_HSE_MAP, value)

def save_scanned_hse_pic(value):
    save_key_value(SCANNED_HSE_PIC, value)

def save_scanned_id_doc(value):
    save_key_value(SCANNED_ID_DOC, value)

