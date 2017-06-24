# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : copy_editor
Description          : STDM copy editor
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

from ui_copy_profile import Ui_dlgCopyProfile 

class CopyProfileEditor(QDialog, Ui_dlgCopyProfile):
    def __init__(self, parent, orig_name, orig_desc, profile_names):
        QDialog.__init__(self, parent)

        self.orig_name = orig_name
        self.orig_desc = orig_desc
        self.copy_name = orig_name+'_copy'
        self.copy_desc = ''
        self.profile_names = profile_names
        
        self.setupUi(self)
        self.init_controls()
        
    def init_controls(self):
        self.edtFromProfile.setText(self.orig_name)
        self.edtDesc.setText(self.orig_desc)
        self.edtName.setText(self.copy_name)
        self.edtName.setFocus()
        name_regex = QRegExp('^[A-Za-z0-9_\s]*$')
        name_validator = QRegExpValidator(name_regex)
        self.edtName.setValidator(name_validator)
        
    def format_name(self, txt):
        ''''remove any trailing spaces in the name and replace them underscore'''
        formatted_name = txt.strip().replace(' ', "_")
        return formatted_name
    
    def add_profile(self):
        self.copy_name = self.format_name(unicode(self.edtName.text()))
        self.copy_desc = self.edtDesc.text()

    def accept(self):
        '''
        listen to user OK action
        '''
        if self.edtName.text() == '':
            self.error_info_message(
                QApplication.translate(
                    "CopyEditor", "Please enter a profile name.")
            )
            return

        # avoid existing profile names
        if self.edtName.text() in self.profile_names:
            self.error_info_message(
                QApplication.translate(
                    "CopyEditor",
                    "Entered name is already in use. "
                    "Please enter another profile name."
                )
            )
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

