# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Configfile_paths
Description          : Reads table configuration information in an XML config
                       file.
Date                 : 30/March/2014
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

import os
import shutil
import platform
import filecmp

from PyQt4.QtGui import QApplication, QMessageBox

from stdm.utils import PLUGIN_DIR
from stdm.settings import RegistryConfig
from .reports import SysFonts

DEFAULT_CONFIG="stdmConfig.xml"
LICENSE="LICENSE.txt"
HTML="stdm_schema.html"
BASIC_SQL="stdmConfig.sql"
CONFIG="Config"
HELP="stdm.chm"

xmldoc=os.path.dirname(os.path.abspath(__file__))

class FilePaths(object):
    def __init__(self, path=None):
        self._file = PLUGIN_DIR
        self.base_dir = None
        self._html = ''
        self._sql = ''
        self.user_path = None
        self.cache_path = None
        self.config = RegistryConfig()
        self.check_previous_setting()

    def check_previous_setting(self):    
        self.default_config_path()
        try:
            path_settings = self.config.read([CONFIG])
            if path_settings:
                self.set_user_config_path(path_settings[CONFIG])
            else:
                self.set_user_config_path()
        except Exception as ex:
            raise ex
                        
    def xml_file(self):
        ''' Function returns the default xml file with configuration '''
        #self.setConfigPath()
        return self._file

    def cache_file(self):
        ''' To implemented a backup file for comparing edits everytime the user makes changes '''
        path = self.user_path+'/temp/%s'%DEFAULT_CONFIG
        return path
    
    def cache_dir(self):
        return self.cache_path
    
    def set_cache_dir(self, path=None):
        if path:
            self.cache_path = self.user_path+"/%s"%path
        else:
            self.cache_path = self.user_path+"/temp"

        self.create_dir(self.cache_path)

    def stdm_settings_path(self):
        #To be implemented to write new file with user edits
        return self.user_path
    
    def html_file(self):
        #Read the html representation of the schema
        self._html = self.user_path+'/%s'%HTML
        return self._html
    
    def sql_file(self):
        #Read the html representation of the schema
        self._sql = self.user_path+'/%s'%BASIC_SQL
        return self._sql
    
    def base_sql_path(self):
        path= self.base_dir+'/%s'%DEFAULT_CONFIG
        #path=self.user_path+'/temp/%s'%FILE
        return path
    
    def HelpContents(self):
        """Method to load help contents file"""
        return self._file+'/%s'%HELP
        
    def default_config_path(self):
        """
        returns the path with base configuration file
        """
        self.base_dir = self._file+"/template/"       
    
    def set_user_config_path(self,path=None):
        ''' set new path with user configuration'''
        if path is not None:
            self.user_path= path
        else:
            self.user_path = self.localPath()
        self.create_dir(self.user_path)
        self.cache_path = self.user_path+'/temp'
        self.create_dir(self.cache_path)
        self.userConfigPath(self.user_path)
    
    def userConfigPath(self,path=None):
        #Copy template files to the user directory
        try:
            #self.compare_config_version(FILE)
            for fileN in [DEFAULT_CONFIG, BASIC_SQL]:
                if not os.path.isfile(path+'/%s'%fileN):
                    baseFile = self.base_dir +'/%s'%fileN
                    shutil.copy(baseFile,self.user_path)
                if not os.path.isfile(self.cache_file()):
                    self.create_backup()
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
            path = self.user_path
        else:
            path = path
        base_file = self.base_sql_path()
        user_file = path +'/%s'%DEFAULT_CONFIG
        if os.path.isfile(user_file):
            if QMessageBox.warning(None, QApplication.translate("FilePaths","Previous user configuration found"),
                                   QApplication.translate("FilePaths",
                                                "Wizard detected previous configuration exists in the current directory."
                                                "\nDo you want to overwrite the existing config?"),
                                   QMessageBox.Yes| QMessageBox.No) == QMessageBox.Yes:
                if filecmp.cmp(base_file, user_file, shallow=False):
                    pass
                else:
                    try:
                        os.remove(user_file)
                        shutil.copy(base_file, self.user_path)
                    except:
                        pass
            else:
                QMessageBox.information(None, QApplication.translate("FilePaths","Configuration Exist"),
                                        QApplication.translate("FilePaths","Previous configuration retained"))
        else:
            shutil.copy(base_file, user_file)
        self.create_backup()

    def localFontPath(self, path):
        """ Create a path where fonts will be stored"""
        if path == None:
            if platform.system() == "Windows":
                path = os.environ["USERPROFILE"]
            else:
                path = os.getenv("HOME")
            fontPath = path + "/.stdm/font.cache"
        else:
            fontPath = str(path).replace("\\", "/")+"/font.cache"
        SysFonts.register(fontPath)
    
    def set_user_xml_file(self):
        """
        Default path to the config file
        """
        xml = self.user_path +'/%s'%DEFAULT_CONFIG
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
    
    def setLocalPath(self, path=None):
        if path:
            self.user_path = path
        if not path:
            self.user_path = self.localPath()
            
    def create_dir(self, dir_path):
        if not os.access(dir_path, os.F_OK):
            os.makedirs(dir_path)
        else:
            return dir_path
    
    def stdm_license_doc(self):
        """
        load STDM license file for viewing
        """
        return self._file+'/%s'%LICENSE
        
    def create_backup(self):
        """
        Incase the user want to keep track of the old file when current file changes
        :return:
        """
        if os.path.isfile(self.cache_file()):
            os.remove(self.cache_file())
        shutil.copy(self.set_user_xml_file(), self.cache_dir())

    def change_config(self):
        """
        Method to update the config file the detected one is old
        :return:
        """
        base_file = self.base_sql_path()
        cur_file = self.set_user_xml_file()
        try:
            if os.path.isfile(cur_file):
                os.remove(cur_file)
            shutil.copy(base_file, self.user_path)
        except:
            pass

