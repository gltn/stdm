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
from ui_profile import Ui_Profile
from PyQt4.QtCore import *
from PyQt4.QtGui import QDialog, QApplication, QMessageBox
from stdm.data import writeProfile, checkProfile

class ProfileEditor(QDialog, Ui_Profile):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        
        self.setupUi(self)
        self.initControls()
        
    def initControls(self):
        self.txtProfile.clear()
        self.txtDesc.clear()
        
    def profile_formater(self):
        ''''remove training spaces in the name and replace them'''
        profile_name = self.txtProfile.text()
        formatted_name = str(profile_name).strip().replace(' ', "_")
        return formatted_name.lower()
    
    def writeProfile(self):
        '''add new profile to the configuration file'''
        if self.txtProfile.text() == str(checkProfile(self.txtProfile.text())):
            self.ErrorInfoMessage(QApplication.translate("ProfileEditor","Profile already exist"))
            return
        if self.profile_formater() == str(checkProfile(self.profile_formater())):
            self.ErrorInfoMessage(QApplication.translate("ProfileEditor","Profile already exist"))
            return
        if self.profile_formater() != str(checkProfile(self.profile_formater())).lower():
            profileData = {}
            profileData['name'] = str(self.profile_formater())
            profileData['fullname'] = str(self.txtDesc.text())
            writeProfile(profileData)
        
    def accept(self):
        '''listen to user action on the dialog'''
        if self.txtProfile.text() == '':
            self.ErrorInfoMessage(QApplication.translate("ProfileEditor","Profile name is not given"))
            return
        self.writeProfile()
        self.close()
        
    def ErrorInfoMessage(self, Message):
        # Error Message Box
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("STDM")
        msg.setText(Message)
        msg.exec_()  

