from PyQt4.QtGui import QDesktopServices

from stdm.settings.registryconfig import (
    CURRENT_PROFILE,
    RegistryConfig,
    ENTITY_BROWSER_RECORD_LIMIT,
    IMPORT_MAPFILE,
    TRANS_PATH,
    MEDIA_URL,
    KOBO_USER,
    KOBO_PASS,

    FAMILY_PHOTO,
    SIGN_PHOTO,
    HOUSE_PHOTO,
    HOUSE_PICTURE,
    ID_PICTURE,
    
    PER_SIGNATURE,
    HHOLD_SIGNATURE,
    FINGER_PRINT,
    HHOLD_PHOTO,
    HHOLD_FAMILY_PHOTO,

    PROPERTY_DOC,
    ID_DOC,

    SCANNED_DOC,
    SCANNED_HSE_MAP,
    SCANNED_HSE_PIC,
    SCANNED_ID_DOC,
    SCANNED_FAMILY_PHOTO,
    SCANNED_SIGNATURE
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

def get_import_mapfile():
    reg_config = RegistryConfig()
    mapfile = reg_config.read([IMPORT_MAPFILE])
    import_mapfile = mapfile.get(IMPORT_MAPFILE, '')
    return import_mapfile

def save_import_mapfile(mapfile):
    reg_config = RegistryConfig()
    reg_config.write({IMPORT_MAPFILE:mapfile})

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

# ********* IRAQ *******************
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

# ************************************

# ----- YEMEN -------------------------

def get_person_signature():
    return get_key_value(PER_SIGNATURE)

def get_hhold_signature():
    return get_key_value(HHOLD_SIGNATURE)

def get_finger_print():
    return get_key_value(FINGER_PRINT)

def get_hhold_photo():
    return get_key_value(HHOLD_PHOTO)

def get_hhold_family_photo():
    return get_key_value(HHOLD_FAMILY_PHOTO)

def get_property_doc():
    return get_key_value(PROPERTY_DOC)

def get_id_doc():
    return get_key_value(ID_DOC)

# -----------------------------------------

def get_scanned_doc():
    return get_key_value(SCANNED_DOC)

def get_scanned_hse_map():
    return get_key_value(SCANNED_HSE_MAP)

def get_scanned_hse_pic():
    return get_key_value(SCANNED_HSE_PIC)

def get_scanned_id_doc():
    return get_key_value(SCANNED_ID_DOC)

def get_scanned_family_photo():
    return get_key_value(SCANNED_FAMILY_PHOTO)

def get_scanned_signature():
    return get_key_value(SCANNED_SIGNATURE)

def save_media_url(value):
    save_key_value(MEDIA_URL, value)

def save_kobo_user(value):
    save_key_value(KOBO_USER, value)

def save_kobo_pass(value):
    save_key_value(KOBO_PASS, value)

# ----- IRAQ ------------------------

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

# ---------------------------------

# -----  YEMEN -----------------------

def save_person_signature(value):
    save_key_value(PER_SIGNATURE, value)

def save_hhold_signature(value):
    save_key_value(HHOLD_SIGNATURE, value)

def save_finger_print(value):
    save_key_value(FINGER_PRINT, value)

def save_hhold_photo(value):
    save_key_value(HHOLD_PHOTO, value)

def save_hhold_family_photo(value):
    save_key_value(HHOLD_FAMILY_PHOTO, value)

def save_property_doc(value):
    save_key_value(PROPERTY_DOC, value)

def save_id_doc(value):
    save_key_value(ID_DOC, value)
    
# --------------------------------------


def save_scanned_doc(value):
    save_key_value(SCANNED_DOC, value)

def save_scanned_hse_map(value):
    save_key_value(SCANNED_HSE_MAP, value)

def save_scanned_hse_pic(value):
    save_key_value(SCANNED_HSE_PIC, value)

def save_scanned_id_doc(value):
    save_key_value(SCANNED_ID_DOC, value)

def save_scanned_family_photo(value):
    save_key_value(SCANNED_FAMILY_PHOTO, value)

def save_scanned_signature(value):
    save_key_value(SCANNED_SIGNATURE, value)

