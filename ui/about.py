"""
/***************************************************************************
Name                 : About STDM Dialog
Description          : Provides a brief narrative of STDM
Date                 : 11/April/11
copyright            : (C) 2011 by John Gitau
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
import sys,os

from PyQt4.QtGui import (
    QDialog,
    QMessageBox,
    QApplication,
    QDesktopServices,
    QTextCharFormat,
    QTextCursor
)
from PyQt4.QtCore import (
    QFile,
    QTextStream,
    QIODevice,
    QUrl
)
from stdm.utils.util import PLUGIN_DIR, version_from_metadata
from ui_about_flts import Ui_frmAbout


class AboutSTDMDialog(QDialog,Ui_frmAbout):
    def __init__(self,parent=None, metadata=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self._metadata = metadata

        #Connect signals
        self.btnContactUs.clicked.connect(self.onContactUs)
        self.btnSTDMHome.clicked.connect(self.onSTDMHome)

        self._insert_metadata_info()

    def _insert_metadata_info(self):
        #Insert version and build numbers respectively.
        if not self._metadata is None:
            installed_version = self._metadata.get('version_installed', None)
        else:
            installed_version = version_from_metadata()

        if installed_version is None:
            return

        cursor = self.txtAbout.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertBlock()
        cursor.insertBlock()

        #Insert installed version text
        version_msg = QApplication.translate(
            'AboutSTDMDialog',
            'FLTS version'
        )
        version_text = u'{0} {1}'.format(version_msg, installed_version)
        char_format = cursor.blockCharFormat()
        text_format = QTextCharFormat(char_format)
        text_format.setFontWeight(75)
        cursor.insertText(version_text, text_format)
            
    def onSTDMHome(self):
        """
        Load STDM home page using the system's default browser.
        """
        fltsURL = "http://www.mlr.gov.na/"
        QDesktopServices.openUrl(QUrl(fltsURL))

    def onContactUs(self):
        """
        Load STDM contact page.
        """
        contactURL = "http://www.gov.na"
        QDesktopServices.openUrl(QUrl(contactURL))
    
