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

from PyQt4.QtCore import (
    pyqtSignal,
    QObject
)

from stdm.data.database import Singleton

from .profile import Profile

LOGGER = logging.getLogger('stdm')

@Singleton
class StdmConfiguration(QObject):
    """
    The main class containing all the configuration information. This
    information is grouped into profiles, where only one profile instance can
    be active in the system.
    """
    VERSION = 1.2
    profile_added = pyqtSignal(Profile)
    profile_removed = pyqtSignal(str)

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self.profiles = OrderedDict()
        self.is_null = True

        LOGGER.debug("STDM Configuration created.")

    def add_profile(self, profile):
        """
        Add a new profile to the collection. The name of the profile is
        checked to ensure that it is unique.
        :param profile: Profile object.
        :type profile: Profile
        """
        if not profile.name in self.profiles:
            self.profiles[profile.name] = profile

            LOGGER.debug('%s profile added', profile.name)

            #Raise profile_added signal
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
        if not name in self.profiles:
            LOGGER.debug('Profile named %s not found.', name)

            return False

        del self.profiles[name]

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

