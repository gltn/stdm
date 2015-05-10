# -*- coding: utf-8 -*-
"""
/***************************************************************************
 stdm
                                 A QGIS plugin
 Securing land and property rights for all
                              -------------------
        begin                : 2014-03-04
        copyright            : (C) 2014 by GLTN
        email                : njoroge.solomon@yahoo.com
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
import os
import shutil
import platform
import filecmp
from stdm.utils import PLUGIN_DIR
from PyQt4.QtGui import QApplication, QMessageBox
FILE="stdmConfig.xml"
LICENSE="LICENSE.txt"
HTML="stdm_schema.html"
SQL="stdmConfig.sql"
CONFIG="Config"
HELP="stdm.chm"

xmldoc=os.path.dirname(os.path.abspath(__file__))
#from stdm.config import activeProfile
from stdm.settings import RegistryConfig
from .reports import SysFonts

class FilePaths(object):
    def __init__(self, path=None):
        self._file=PLUGIN_DIR
        self.baseDir=None
        self._html=''
        self._sql=''
        self.userPath=None
        self.cachePath=None
        self.config = RegistryConfig()
        self.checkPreviousSetting()

    def checkPreviousSetting(self):    
        self.defaultConfigPath()
        try:
            pathSettings = self.config.read([CONFIG])
            if pathSettings:
                self.setUserConfigPath(pathSettings[CONFIG])
            else:
                self.setUserConfigPath()
        except Exception as ex:
            pass
                        
    def XMLFile(self):
        #this function returns the default xml file with configuration
        #self.setConfigPath()
        return self._file

    def cacheFile(self):
        #To implemented a backup file for comparing edits everytime the user makes changes
        path = self.userPath+'/temp/%s'%FILE
        return path
    
    def cacheDir(self):
        return self.cachePath
    
    def setCacheDir(self,path=None):
        if path:
            self.cachePath = self.userPath+"/%s"%path
        else:
            self.cachePath = self.userPath+"/temp"
        self.createDir(self.cachePath)

    def STDMSettingsPath(self):
        #To be implemented to write new file with user edits
        return self.userPath
    
    def HtmlFile(self):
        #Read the html representation of the schema
        self._html = self.userPath+'/%s'%HTML
        return self._html
    
    def SQLFile(self):
        #Read the html representation of the schema
        self._sql = self.userPath+'/%s'%SQL
        return self._sql
    
    def baseSQLPath(self):
        path= self.baseDir+'/%s'%FILE
        #path=self.userPath+'/temp/%s'%FILE
        return path
    
    def HelpContents(self):
        """Method to load help contents file"""
        return self._file+'/%s'%HELP
        
    def defaultConfigPath(self):
        """
        returns the path with base configuration file
        """
        self.baseDir = self._file+"/template/"       
    
    def setUserConfigPath(self,path=None):
        ''' set new path with user configuration'''
        if path is not None:
            self.userPath= path
        else:
            self.userPath = self.localPath()
        self.createDir(self.userPath)
        self.cachePath = self.userPath+'/temp'
        self.createDir(self.cachePath)
        self.userConfigPath(self.userPath)
    
    def userConfigPath(self,path=None):
        #Copy template files to the user directory
        try:
            #self.compare_config_version(FILE)
            for fileN in [FILE, HTML, SQL]:
                if not os.path.isfile(path+'/%s'%fileN):
                    baseFile = self.baseDir +'/%s'%fileN
                    shutil.copy(baseFile,self.userPath)
                if not os.path.isfile(self.cacheFile()):
                    self.createBackup()
            self.localFontPath(path)
        except IOError as io:
            raise io

    def compare_config_version(self, path = None):
        """
        Method to check the version of the two files being copied and return the latest one
        :param newfile: QFile
        :return: QFile
        """
        if not path:
            path = self.userPath
        else:
            path = path
        base_file = self.baseSQLPath()
        user_file = path +'/%s'%FILE
        if os.path.isfile(user_file):
            if QMessageBox.warning(None, QApplication.translate("FilePaths","User configuration found"),
                                   QApplication.translate("FilePaths",
                                                "Wizard detected configuration exist in the current directory."
                                                "\nDo you want to overwrite the existing config?"),
                                   QMessageBox.Yes| QMessageBox.No) == QMessageBox.Yes:
                if filecmp.cmp(base_file, user_file, shallow=False):
                    pass
                else:
                    os.remove(user_file)
                    shutil.copy(base_file, self.userPath)
            else:
                QMessageBox.information(None, QApplication.translate("FilePaths","Configuration Exist"),
                                        QApplication.translate("FilePaths","Existing configuration retained"))
        else:
            shutil.copy(base_file,user_file)
        self.createBackup()

    def localFontPath(self, path):
        """ Create a path where fonts will be stored"""
        fontPath=None
        if path == None:
            if platform.system() == "Windows":
                path = os.environ["USERPROFILE"]
            else:
                path = os.getenv("HOME")
            fontPath = path + "/.stdm/font.cache"
        else:
            fontPath=str(path).replace("\\", "/")+"/font.cache"
        SysFonts.register(fontPath)
    
    def setUserXMLFile(self):
        """
        Default path to the config file
        """
        xml = self.userPath +'/%s'%FILE
        return xml
    
    def localPath(self):
        """
        Look for users path based on platform, need to implement for unix systems
        :return:
        """
        profPath = None
        if platform.system() == "Windows":
            userPath = os.environ["USERPROFILE"]
            profPath = userPath + "/.stdm"
        else:
            profPath = str(os.getenv('HOME'))+"/.stdm"
        return str(profPath).replace("\\", "/")
    
    def setLocalPath(self,path=None):
        if path:
            self.userPath = path
        if not path:
            self.userPath = self.localPath()
            
    def createDir(self,dirPath):
        if os.access(dirPath, os.F_OK) == False:
            os.makedirs(dirPath)
        else:
            return dirPath
    
    def STDMLicenseDoc(self):
        """
        load STDM license file for viewing
        """
        return self._file+'/%s'%LICENSE
        
    def createBackup(self):
        """
        Incase the user want to keep track of the old file when current file changes
        :return:
        """
        if os.path.isfile(self.cacheFile()):
            os.remove(self.cacheFile())
        shutil.copy(self.setUserXMLFile(), self.cacheDir())
