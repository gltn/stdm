"""
/***************************************************************************
Name                 : Registry Configuration
Description          : Class for reading and writing generic KVP settings for
                        STDM stored in the registry
Date                 : 24/May/2013
copyright            : (C) 2013 by John Gitau
email                : gkahiu@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import typing 

from qgis.PyQt.QtCore import QSettings
from qgis.PyQt.QtGui import QColor

# Names of registry keys
NETWORK_DOC_RESOURCE = 'NetDocumentResource'
PATHKEYS = ['Config', 'NetDocumentResource', 'ComposerOutputs', 'ComposerTemplates']
DATABASE_LOOKUP = 'LookupInit'
# There was a mixup in these 2 keys. Consolidation required across the plugin.
LOCAL_SOURCE_DOC = NETWORK_DOC_RESOURCE
COMPOSER_OUTPUT = 'ComposerOutputs'
COMPOSER_TEMPLATE = 'ComposerTemplates'
CURRENT_PROFILE = 'CurrentProfile'
LAST_SUPPORTING_DOC_PATH = 'LastDocumentPath'
SHOW_LICENSE = 'ShowLicense'
WIZARD_RUN = 'wizardRun'
CONFIG_UPDATED = 'ConfigUpdated'
SUB_QGIS = '/Qgis'
QGIS_PYTHON_PLUGINS = '/PythonPlugins'
DEBUG_LOG = 'Debug'
HOST = 'Host'
FIRST_LOGIN = 'FirstLogin'
STDM_PLUGIN = 'stdm'
STDM_VERSION = 'STDMVersion'
ENTITY_BROWSER_RECORD_LIMIT = 'EntityBrowserRecordLimit'
ENTITY_SORT_ORDER = 'EntitySortOrder'
RUN_TEMPLATE_CONVERTER = 'RunTemplateConverter'
LOG_MODE = 'LogMode'

def registry_value(key_name: str):
    """
    Util method for reading the value for the given key.
    :param key_name: Name of the registry key.
    :type key_name: str
    :return: Value of the of the given registry key.
    :rtype: object
    """
    reg_config = RegistryConfig()

    key_value = reg_config.read([key_name])

    if len(key_value) == 0:
        return None
    else:
        return key_value[key_name]


def set_registry_value(key: str, value: typing.Any):
    """
    Sets the registry key with the specified value. A new key will be created
    if it does not exist.
    :param key: Registry key
    :type: str
    :param value: Value to be set for the given key.
    :type value: object
    """
    reg_config = RegistryConfig()

    reg_config.write({key: value})


def composer_output_path():
    """
    :return: Returns the directory path of composer outputs.
    :rtype: str
    """
    return registry_value(COMPOSER_OUTPUT)


def composer_template_path():
    """
    :return: Returns the directory path of composer templates.
    :rtype: str
    """
    return registry_value(COMPOSER_TEMPLATE)


def source_documents_path():
    """
    :return: Returns the root path of source documents.
    :rtype: str
    """
    return registry_value(NETWORK_DOC_RESOURCE)


def last_document_path():
    """
    :return: Returns the latest path used for uploading supporting documents.
    :rtype: str
    """
    return registry_value(LAST_SUPPORTING_DOC_PATH)


def debug_logging():
    """
    :return: Returns whether debug logging has been enabled.
    :rtype: bool
    """
    dbg = registry_value(DEBUG_LOG)
    if dbg is None or dbg == 0:
        return False

    return True

def logging_mode():
    log_mode = registry_value(LOG_MODE)
    if log_mode is None:
        return "STDOUT"
    return log_mode


def set_debug_logging(state: bool):
    """
    Enable or disable debug logging.
    :param state: True to enable, False to disable.
    :type state: bool
    """
    lvl = 0
    if state:
        lvl = 1

    set_registry_value(DEBUG_LOG, lvl)

def set_run_template_converter_on_startup(state: bool):
    value = 'True' if state else 'False'
    set_registry_value(RUN_TEMPLATE_CONVERTER, value) 

def run_template_converter_on_startup() -> bool:
    value = registry_value(RUN_TEMPLATE_CONVERTER)
    return True if value == 'True' else False

def set_last_document_path(path):
    """
    Sets the latest path used for uploading supporting documents.
    :param path: Supporting documents path
    :type path: str
    """
    set_registry_value(LAST_SUPPORTING_DOC_PATH, path)


def enable_stdm():
    """
    Enables the STDM plugin if it is disabled.
    """
    config_plugins = QGISRegistryConfig(QGIS_PYTHON_PLUGINS)
    stdm_status = config_plugins.read([STDM_PLUGIN])
    if stdm_status[STDM_PLUGIN] == 'false':
        config_plugins.write({STDM_PLUGIN: 'true'})


def selection_color():
    """
    Gets qgis default selection color.
    Returns:
        The default selection color.
        Tuple

    """
    color_config = QGISRegistryConfig(SUB_QGIS)

    red_dic = color_config.read(
        ['default_selection_color_red']
    )
    green_dic = color_config.read(
        ['default_selection_color_green']
    )
    blue_dic = color_config.read(
        ['default_selection_color_blue']
    )
    alpha_dic = color_config.read(
        ['default_selection_color_alpha']
    )
    if len(red_dic) < 1 or len(green_dic) < 1 or \
            len(blue_dic) < 1 or len(alpha_dic) < 1:
        rgba = QColor(255, 255, 0, 255)

        return rgba

    selection_red = int(
        red_dic['default_selection_color_red']
    )
    selection_green = int(
        green_dic['default_selection_color_green']
    )
    selection_blue = int(
        blue_dic['default_selection_color_blue']
    )
    selection_alpha = int(
        alpha_dic['default_selection_color_alpha']
    )
    rgba = QColor(
        selection_red,
        selection_green,
        selection_blue,
        selection_alpha
    )
    return rgba


class RegistryConfig:
    """
    Utility class for reading and writing STDM user settings in Windows Registry
    """
    def __init__(self):
        self.groupPath = "STDM"

    def read(self, items):
        """
        Get the value of the user defined items from the STDM registry tree
        param items: List of registry keys to fetch.
        type items: list
        """
        userKeys = {}
        settings = QSettings()
        settings.beginGroup("/")
        groups = settings.childGroups()
        for group in groups:
            if str(group) == self._base_group():
                for t in items:
                    tKey = self.groupPath + "/" + t
                    if settings.contains(tKey):
                        tValue = settings.value(tKey)
                        userKeys[t] = tValue
                break

        return userKeys

    def _base_group(self):
        """
        :return: Extract the name of the base group in the group path variable
        of the class.
        :rtype: str
        """
        if not self.groupPath:
            return self.groupPath

        slash_char = "/"

        group_path = self.groupPath

        if self.groupPath[0] == slash_char:
            group_path = self.groupPath[1:]

        groups = group_path.split(slash_char)

        return groups[0]

    def group_children(self):
        """
        :return: Names of the child groups in the path specified in the constructor.
        :rtype: list
        """
        settings = QSettings()
        settings.beginGroup(self.groupPath)

        group_children = settings.childGroups()

        settings.endGroup()

        return group_children

    def write(self, settings: dict):
        """
        Write items in settings dictionary to the STDM registry
        """
        uSettings = QSettings()
        stdmGroup = "/" + self.groupPath
        uSettings.beginGroup(stdmGroup)

        for k, v in settings.items():
            uSettings.setValue(k, v)

        uSettings.endGroup()
        uSettings.sync()

    def all_keys(self):
        settings = QSettings()
        settings.beginGroup(self.groupPath)
        return settings.allKeys()

    def group_keys(self, group_name):
        settings = QSettings()
        settings.beginGroup(self.groupPath+'/'+group_name)
        keys = settings.childKeys()
        settings.endGroup()
        return keys

    def add_value(self, group_name: str, vals: dict):
        """
        Writes values to registry.
        :param group_name: Name of the sorting group in the regristry.
        Format: `Sorting/profile_name`
        This is appended to the `groupPath` (STDM) defined in this class.
        :type group_name: str

        :param vals: Dictionary with entity name as key and a tuple of
         sorting column and order of sorting (Ascending or Descending) as the 
         value.
        :type vals: dict  {entity_name:(sort_column, sort_order)}
        """
        settings = QSettings()
        settings.beginGroup(self.groupPath+'/'+group_name)
        entity_name = list(vals.keys())[0]
        sort_column = list(vals.values())[0][0]
        sort_order  = list(vals.values())[0][1]
        value = sort_column+' '+sort_order
        settings.setValue(entity_name, value)
        settings.endGroup()

    def remove_key(self, group_name: str, key: typing.Any):
        settings = QSettings()
        settings.beginGroup(self.groupPath+'/'+group_name)
        settings.remove(key)
        settings.endGroup()

    def get_value(self, group_name: str, entity_name: str) ->str:
        """
        Finds and returns a value of a key from group `Sorting/profile_name`.
        :param group_name: Name of the sorting group under the main STDM group
          in the registry. The format of the group_name is `Sorting/profile_name`
        :type group_name: str
        :param entity_name:
        :type entity_name: str
        """
        settings = QSettings()
        settings.beginGroup(self.groupPath+'/'+group_name)
        value = settings.value(entity_name)
        settings.endGroup()
        return value

class QGISRegistryConfig(RegistryConfig):
    """
    Class for reading and writing QGIS-wide registry settings.
    The user has to specify the group path which contains the keys.
    """
    def __init__(self, path):
        RegistryConfig.__init__(self)

        # Insert forward slash if it does not exist in the path
        if len(path) > 0:
            slash = path[0]
            slash_char = "/"

            if slash != slash_char:
                path = slash_char + path

        self.groupPath = path
