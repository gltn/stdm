"""
/***************************************************************************
Name                 : Registry Configuration
Description          : Class for reading and writing generic KVP settings for
                        STDM stored in the registry
Date                 : 24/May/2013
copyright            : (C) 2014 by UN-Habitat and implementing partners.
                       See the accompanying file CONTRIBUTORS.txt in the root
email                : stdm@unhabitat.org
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
from PyQt4.QtCore import QSettings

# Names of registry keys
NETWORK_DOC_RESOURCE = "NetDocumentResource"
PATHKEYS = ['Config', 'NetDocumentResource',
            'ComposerOutputs', 'ComposerTemplates']
DATABASE_LOOKUP = "LookupInit"
LOCAL_SOURCE_DOC = "SourceDocuments"
COMPOSER_OUTPUT = 'ComposerOutputs'
COMPOSER_TEMPLATE = 'ComposerTemplates'


class RegistryConfig(object):
    """
    Utility class for reading and writing STDM user settings in Windows
    Registry
    """

    def __init__(self):
        self._group_path = "STDM"

    def read(self, items):
        """
        Get the value of the user defined items from the STDM registry tree
        :return : User Keys
        :rtype : dict
        :param items: list
        """
        user_keys = {}
        settings = QSettings()
        settings.beginGroup("/")
        groups = settings.childGroups()
        for group in groups:
            # QMessageBox.information(None, "Info", group)
            if str(group) == self._base_group():
                for t in items:
                    tKey = self._group_path + "/" + t
                    if settings.contains(tKey):
                        tValue = settings.value(tKey)
                        user_keys[t] = tValue
                break

        return user_keys

    def _base_group(self):
        """
        :return: Extract the name of the base group in the group path variable
        of the class.
        :rtype: str
        """
        if not self._group_path:
            return self._group_path

        slash_char = "/"

        group_path = self._group_path

        if self._group_path[0] == slash_char:
            group_path = self._group_path[1:]

        groups = group_path.split(slash_char)

        return groups[0]

    def group_children(self):
        """
        :return: Names of the child groups in the path specified in the
        constructor.
        :rtype: list
        """
        settings = QSettings()
        settings.beginGroup(self._group_path)

        group_children = settings.childGroups()

        settings.endGroup()

        return group_children

    def write(self, settings):
        """
        Write items in settings dictionary to the STDM registry
        """
        u_settings = QSettings()
        stdm_group = "/" + self._group_path
        u_settings.beginGroup(stdm_group)

        for k, v in settings.iteritems():
            u_settings.setValue(k, v)

        u_settings.endGroup()
        u_settings.sync()


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

        self._group_path = path
