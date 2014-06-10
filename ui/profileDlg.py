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
    def __init__(self,parent):
        QDialog.__init__(self,parent)
        
        self.setupUi(self)
        self.initControls()
        
    def initControls(self):
        self.txtProfile.clear()
        self.txtDesc.clear()
        
    def profileFormater(self):
        ''''remove training spaces in the name and replace them'''
        profileName=self.txtProfile.text()
        formattedName=str(profileName).strip()
        formattedName=formattedName.replace(' ', "_")
        return formattedName.lower()
    
    def writeProfile(self):
        '''add new profile to teh configuration file'''
        if self.profileFormater()== checkProfile(self.profileFormater()):
            self.ErrorInfoMessage(QApplication.translate("TableEditor","Profile already exist"))
            return
        if self.profileFormater()!= checkProfile(self.profileFormater()):
            profileData={}
            profileData['name']=str(self.profileFormater())
            profileData['fullname']=str(self.txtDesc.text())
            writeProfile(profileData)
        
    def accept(self):
        '''listen to user action on the dialog'''
        if self.txtProfile.text()=='':
            self.ErrorInfoMessage(QApplication.translate("TableEditor","Profile name is not given"))
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

        
        
        
        