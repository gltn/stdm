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
NETWORK_DOC_RESOURCE = "NetDocumentResource"
DATABASE_LOOKUP = "LookupInit"

class RegistryConfig(object):
    '''
    Utility class for reading and writing STDM user settings in Windows Registry
    '''
    def __init__(self):
        self.groupPath = "STDM"
    
    def read(self,items):
        '''
        Get the value of the user defined items from the STDM registry tree
        '''
        userKeys = {}
        settings = QSettings()        
        settings.beginGroup("/")
        groups = settings.childGroups()
        for group in groups:
            if str(group) == self.groupPath:
                for t in items:
                    tKey = self.groupPath + "/" + t
                    if settings.contains(tKey):                        
                        tValue = settings.value(tKey)
                        userKeys[t] = tValue
                break        
        return userKeys
    
    def write(self, settings):
        '''
        Write items in settings dictionary to the STDM registry
        '''
        uSettings = QSettings()
        stdmGroup = "/" + self.groupPath
        uSettings.beginGroup(stdmGroup)
        for k,v in settings.iteritems():
            uSettings.setValue(k,v)
        uSettings.endGroup()
        uSettings.sync()
            
        
        
        
        
        
        
        
        
        