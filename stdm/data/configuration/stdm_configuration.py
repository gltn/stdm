"""
/***************************************************************************
Name                 : Config
Description          : Configuration classes of STDM entities.
Date                 : 22/December/2015
copyright            : (C) 2015 by UN-Habitat and implementing partners.
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
import logging
from collections import OrderedDict

from qgis.PyQt.QtCore import (
    pyqtSignal,
    QObject
)

from stdm.data.configuration.profile import Profile
from stdm.data.database import Singleton

LOGGER = logging.getLogger('stdm')


@Singleton
class StdmConfiguration(QObject):
    """
    The main class containing all the configuration information. This
    information is grouped into profiles, where only one profile instance can
    be active in the system.
    """
    VERSION = 1.8
    profile_added = pyqtSignal(Profile)
    profile_removed = pyqtSignal(str)

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self.profiles = OrderedDict()
        self.is_null = True
        self._removed_profiles = []

        LOGGER.debug("STDM Configuration initialized.")

    def __len__(self):
        """
        Return a count of all assets in the configuration
        """
        count = 0
        for p in self.profiles.values():
            for e in p.entities.values():
                if e.TYPE_INFO == 'VALUE_LIST':
                    count += len(list(e.values.values()))
                count += len(e.columns)
            count += len(p.entities)
        count += len(self.profiles)
        return count

    @property
    def removed_profiles(self):
        """
        :return: Returns a list of removed profiles.
        :rtype: list(Profile)
        """
        return self._removed_profiles

    def reset_removed_profiles(self):
        """
        Clears the list of removed profiles.
        """
        self._removed_profiles = []

    def add_profile(self, profile):
        """
        Add a new profile to the collection. The name of the profile is
        checked to ensure that it is unique.
        :param profile: Profile object.
        :type profile: Profile
        """
        profile_name = str(profile.name)

        if profile_name not in self.profiles:
            self.profiles[profile_name] = profile

            LOGGER.debug('%s profile added', profile_name)

            if self.is_null:
                self.is_null = False

            # Raise profile_added signal
            self.profile_added.emit(profile)

    def create_profile(self, name):
        """
        Creates a new profile with the given name. This configuration becomes
        the parent.
        :param name: Name of the profile.
        :type name: str
        :returns: Profile object which is not yet added to the collection in
        the configuration.
        :rtype: Profile
        """
        return Profile(name, self)

    def remove_profile(self, name):
        """
        Remove a profile with the given name from the collection.
        :param name: Name of the profile to be removed.
        :type name: str
        :returns: True if the profile was successfully removed. False if the
        profile was not found.
        :rtype: bool
        """
        if name not in self.profiles:
            LOGGER.debug('Profile named %s not found.', name)

            return False

        del_profile = self.profiles.pop(name, None)

        if len(self.profiles) == 0:
            self.is_null = True

        # Remove all references for the profile using the clone object
        if del_profile is not None:
            del_profile.on_delete()

        # Add to the list of removed profiles
        self._removed_profiles.append(del_profile)

        LOGGER.debug('%s profile removed.', name)

        self.profile_removed.emit(name)

        return True

    def profile(self, name):
        """
        Get profile using its name.
        :param name: Name of the profile.
        :type name: str
        :returns: Return a profile with the given name if found, else None.
        :rtype: Profile
        """
        return self.profiles.get(name, None)

    def prefixes(self):
        """
        :returns: A list containing prefixes of the profiles contained in the
        collection.
        :rtype: list
        """
        return [p.prefix for p in self.profiles.values()]

    # Added in v1.7
    def prefix_from_profile_name(self, profile):
        """
        Creates profile prefix using a given profile name.
        :param profile: Profile name
        :type profile: String
        :return: Profile prefix
        :rtype: String
        """
        prefixes = self.prefixes()

        prefix = profile

        for i in range(2, len(profile)):
            curr_prefix = profile[0:i].lower()

            if curr_prefix not in prefixes:
                prefix = curr_prefix

                LOGGER.debug('Prefix determined %s for %s profile',
                             prefix.lower(), profile)

                break

        return prefix.lower()

    def _clear(self):
        """
        Resets the profile collection without syncing the operations in the
        database. Only used when loading the configuration from file. It
        should not be used in most circumstances.
        """
        self.profiles = OrderedDict()
        self.is_null = True


    def print_profile_entities_columns(self):
        print("-------------------------------------------")
        for profile in self.profiles.values():
            print(f'Profile: {profile.name}')
            for entity in profile.entities.values():
                if entity.short_name == 'Enumeration':
                    print(entity.short_name)
                    for column in entity.columns.values():
                        print(f'\t{column.name} : Action - {column.action}')