# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : profile_editor
Description          : STDM profile editor
Date                 : 20/January/2016
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
from PyQt4.QtCore import *
from PyQt4.QtGui import (
    QDialog,
    QApplication,
    QMessageBox,
    QRegExpValidator
)
from ui_profile import Ui_Profile

class ProfileEditor(QDialog, Ui_Profile):
    def __init__(self, parent):
        QDialog.__init__(self, parent)

        self.profile_name = ''
        self.desc = ''
        
        self.setupUi(self)
        self.init_controls()
        
    def init_controls(self):
        self.edtProfile.clear()
        self.edtDesc.clear()
        self.edtProfile.setFocus()
        name_regex = QRegExp('^[A-Za-z0-9_\s]*$')
        name_validator = QRegExpValidator(name_regex)
        self.edtProfile.setValidator(name_validator)
        
        
    def format_name(self, txt):
        ''''remove any trailing spaces in the name and replace them underscore'''
        formatted_name = txt.strip().replace(' ', "_")
        return formatted_name
    
    def add_profile(self):
        self.profile_name = self.format_name(unicode(self.edtProfile.text()))
        self.desc = unicode(self.edtDesc.text())

    def accept(self):
        '''listen to user action on the dialog'''
        if self.edtProfile.text() == '':
            self.error_info_message(QApplication.translate("ProfileEditor", "Profile name is not given"))
            return

        self.add_profile()
        self.done(1)

    def reject(self):
        self.done(0)
        
    def error_info_message(self, Message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("STDM")
        msg.setText(Message)
        msg.exec_()  

