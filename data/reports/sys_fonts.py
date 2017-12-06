#begin:            11th September 2011
#copyright:        (c) 2011 by John Gitau
#email:            gkahiu@gmail.com
#about:            System Fonts Helper Class

import os

from PyQt4.QtCore import QFile

from stdm.third_party.ttfquery import ttffiles
from stdm.utils import *
from stdm.settings.registryconfig import RegistryConfig


class SysFonts:    
    '''
    Provides helper methods for querying the 
    installed system fonts.
    (Only supports True Type fonts)
    '''
    def __init__(self):
        self.reg = ttffiles.Registry()
        if fontCachePath()==None:
            return
        self.reg.load(fontCachePath())
    
    def fontFile(self,fontName):        
        #Get the system font filename from the specific font name                    
        fontFile=None
        mFont=self.matchingFontName(fontName) 
        if mFont!=None:         
            fontPath=self.reg.fontFile(fontName)
            #dir,fontFile=os.path.split(fontPath)
        return str(fontPath)  

    def fontMembers(self,fontName):
        #Get the matching font members for the selected font        
        fontMembers = []
        mFont = self.matchingFontName(fontName)
        if mFont != None:
            fontMembers = set(self.reg.fontMembers(mFont))
        return fontMembers  
    
    def matchingFontName(self,fontName):
        #Try to match the exact font based on the general name        
        matchingFont = None  
         
        try:
            fontList = self.reg.matchName(fontName) 
            if len(fontList) > 0:            
                fontIndex = getIndex(fontList,fontName)
                if fontIndex != -1:
                    matchingFont=fontName
                else:
                    matchingFont=fontList[0]
        except KeyError:
            pass
        
        return matchingFont 
    
    @staticmethod
    def register(fontPath=None): 
        """
        Write fonts into a cache file.
        """ 
        cache=None
        if fontPath!=None:
            cache=fontPath
        else:
            cache=fontCachePath()
        if not QFile.exists(cache):
            fontRegistry = ttffiles.Registry()
            new,failed = fontRegistry.scan()
            fontRegistry.save(cache)
            
            
def fontCachePath():
    regConfig = RegistryConfig()
    try:
        lookupReg = regConfig.read(['Config'])
        cachePath=lookupReg['Config']
        return cachePath+"/font.cache"
    except:
        return None
        
        