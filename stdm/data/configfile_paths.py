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
import filecmp
import os
import platform
import shutil
from typing import Optional

from qgis.PyQt.QtWidgets import (
    QApplication,
    QMessageBox
)

from stdm.data.reports.sys_fonts import SysFonts
from stdm.settings.registryconfig import RegistryConfig
from stdm.utils.util import PLUGIN_DIR

DEFAULT_CONFIG = "stdmConfig.xml"
LICENSE = "LICENSE.txt"
HTML = "stdm_schema.html"
BASIC_SQL = "stdmConfig.sql"
CONFIG = "Config"
HELP = "stdm.chm"


class FilePaths:
    def __init__(self, path=None):
        self._file = PLUGIN_DIR
        self.baseDir = None
        self._html = ''
        self._sql = ''
        self.userPath = None
        self.cachePath = None
        self.config = RegistryConfig()
        # self.checkPreviousSetting()

    def checkPreviousSetting(self):
        self.defaultConfigPath()
        try:
            pathSettings = self.config.read([CONFIG])
            if pathSettings:
                self.setUserConfigPath(pathSettings[CONFIG])
            else:
                self.setUserConfigPath()
        except Exception as ex:
            raise ex

    def XMLFile(self):
        # this function returns the default xml file with configuration
        # self.setConfigPath()
        return self._file

    def cacheFile(self):
        # To implemented a backup file for comparing edits everytime the user
        #  makes changes
        path = self.userPath + '/temp/%s' % DEFAULT_CONFIG
        return path

    def cacheDir(self):
        return self.cachePath

    def setCacheDir(self, path=None):
        if path:
            self.cachePath = self.userPath + "/%s" % path
        else:
            self.cachePath = self.userPath + "/temp"
        self.createDir(self.cachePath)

    def STDMSettingsPath(self):
        # To be implemented to write new file with user edits
        return self.userPath

    def HtmlFile(self):
        # Read the html representation of the schema
        self._html = self.userPath + '/%s' % HTML
        return self._html

    def SQLFile(self):
        # Read the html representation of the schema
        self._sql = self.userPath + '/%s' % BASIC_SQL
        return self._sql

    def baseSQLPath(self):
        path = self.baseDir + '/%s' % DEFAULT_CONFIG
        # path=self.userPath+'/temp/%s'%FILE
        return path

    def HelpContents(self):
        """Method to load help contents file"""
        return self._file + '/%s' % HELP

    def defaultConfigPath(self):
        """
        returns the path with base configuration file
        """
        self.baseDir = self._file + "/templates/"
        return self.baseDir

    def setUserConfigPath(self, path: Optional[str] = None):
        """
        set new path with user configuration
        """
        if path is not None:
            self.userPath = path
        else:
            self.userPath = self.localPath()
        self.createDir(self.userPath)
        self.cachePath = self.userPath + '/temp'
        self.createDir(self.cachePath)
        self.userConfigPath(self.userPath)

    def userConfigPath(self, path=None):
        # Copy template files to the user directory
        try:
            # self.compare_config_version(FILE)
            for fileN in [BASIC_SQL]:
                if not os.path.isfile(path + '/%s' % fileN):
                    baseFile = self.baseDir + '/%s' % fileN
                    shutil.copy(baseFile, self.userPath)
                if not os.path.isfile(self.cacheFile()):
                    self.createBackup()
            self.localFontPath(path)
        except IOError as io:
            raise io

    def compare_config_version(self, path=None):
        """
        Method to check the version of the two files being copied and return the latest one
        """
        if not path:
            path = self.userPath
        else:
            path = path
        base_file = self.baseSQLPath()
        user_file = path + '/%s' % DEFAULT_CONFIG
        if os.path.isfile(user_file):
            if QMessageBox.warning(None, QApplication.translate("FilePaths",
                                                                "Previous user configuration found"),
                                   QApplication.translate("FilePaths",
                                                          "Wizard detected previous configuration exists in the current directory."
                                                          "\nDo you want to overwrite the existing config?"),
                                   QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                if filecmp.cmp(base_file, user_file, shallow=False):
                    pass
                else:
                    try:
                        os.remove(user_file)
                        shutil.copy(base_file, self.userPath)
                    except:
                        pass
            else:
                QMessageBox.information(None,
                                        QApplication.translate("FilePaths",
                                                               "Configuration Exist"),
                                        QApplication.translate("FilePaths",
                                                               "Previous configuration retained"))
        else:
            shutil.copy(base_file, user_file)
        self.createBackup()

    def localFontPath(self, path):
        """ Create a path where fonts will be stored"""
        if path is None:
            if platform.system() == "Windows":
                path = os.environ["USERPROFILE"]
            else:
                path = os.getenv("HOME")
            fontPath = path + "/.stdm/font.cache"
        else:
            fontPath = str(path).replace("\\", "/") + "/font.cache"
        SysFonts.register(fontPath)

    def setUserXMLFile(self):
        """
        Default path to the config file
        """
        xml = self.userPath + '/%s' % DEFAULT_CONFIG
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
            profPath = str(os.getenv('HOME')) + "/.stdm"
        return str(profPath).replace("\\", "/")

    def setLocalPath(self, path=None):
        if path:
            self.userPath = path
        if not path:
            self.userPath = self.localPath()

    def createDir(self, dirPath):
        if not os.access(dirPath, os.F_OK):
            os.makedirs(dirPath)
        else:
            return dirPath

    def STDMLicenseDoc(self):
        """
        load STDM license file for viewing
        """
        return self._file + '/%s' % LICENSE

    def createBackup(self):
        """
        In case the user want to keep track of the old file when current file changes
        :return:
        """
        if os.path.isfile(self.cacheFile()):
            os.remove(self.cacheFile())
        shutil.copy(self.setUserXMLFile(), self.cacheDir())

    def change_config(self):
        """
        Method to update the config file the detected one is old
        :return:
        """
        base_file = self.baseSQLPath()
        cur_file = self.setUserXMLFile()
        try:
            if os.path.isfile(cur_file):
                os.remove(cur_file)
            shutil.copy(base_file, self.userPath)
        except:
            pass

    def get_configuration_file(self):
        """ Default path to the config file """
        xml = self.userPath + '/%s' % DEFAULT_CONFIG
        return xml
