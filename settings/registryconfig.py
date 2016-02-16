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
from PyQt4.QtCore import QSettings

#Names of registry keys
NETWORK_DOC_RESOURCE = 'NetDocumentResource'
PATHKEYS = ['Config','NetDocumentResource','ComposerOutputs','ComposerTemplates']
DATABASE_LOOKUP = 'LookupInit'
LOCAL_SOURCE_DOC = 'SourceDocuments'
COMPOSER_OUTPUT = 'ComposerOutputs'
COMPOSER_TEMPLATE = 'ComposerTemplates'

class RegistryConfig(object):
    """
    Utility class for reading and writing STDM user settings in Windows Registry
    """
    def __init__(self):
        self.groupPath = "STDM"
    
    def read(self,items):
        """
        Get the value of the user defined items from the STDM registry tree
        """
        userKeys = {}
        settings = QSettings()        
        settings.beginGroup("/")
        groups = settings.childGroups()
        for group in groups:
            #QMessageBox.information(None, "Info", group)
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

    def write(self, settings):
        """
        Write items in settings dictionary to the STDM registry
        """
        uSettings = QSettings()
        stdmGroup = "/" + self.groupPath
        uSettings.beginGroup(stdmGroup)

        for k,v in settings.iteritems():
            uSettings.setValue(k,v)

        uSettings.endGroup()
        uSettings.sync()
        
class QGISRegistryConfig(RegistryConfig):
    """
    Class for reading and writing QGIS-wide registry settings.
    The user has to specify the group path which contains the keys.
    """
    def __init__(self,path):
        RegistryConfig.__init__(self)

        #Insert forward slash if it does not exist in the path
        if len(path) > 0:
            slash = path[0]
            slash_char = "/"

            if slash != slash_char:
                path = slash_char + path

        self.groupPath = path