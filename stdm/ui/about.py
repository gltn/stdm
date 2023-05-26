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

from qgis.PyQt import uic
from qgis.PyQt.QtCore import (
    QUrl
)
from qgis.PyQt.QtGui import (
    QDesktopServices,
    QTextCharFormat,
    QTextCursor
)
from qgis.PyQt.QtWidgets import (
    QDialog,
    QApplication
)

from stdm.ui.gui_utils import GuiUtils
from stdm.utils.util import value_from_metadata

WIDGET, BASE = uic.loadUiType(
    GuiUtils.get_ui_file_path('ui_about_stdm.ui'))


class AboutSTDMDialog(WIDGET, BASE):
    def __init__(self, parent=None, metadata=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.txtAbout.setHtml(self.txtAbout.toHtml().replace(':/plugins/stdm/images/icons/stdm_2.png',
                                                             GuiUtils.get_icon_svg('stdm_2.png')))

        self._metadata = metadata

        # Connect signals
        self.btnContactUs.clicked.connect(self.onContactUs)
        self.btnSTDMHome.clicked.connect(self.onSTDMHome)

        self._insert_metadata_info()

    def _insert_metadata_info(self):
        # Insert version and build numbers respectively.
        if not self._metadata is None:
            installed_version = self._metadata.get('version_installed', None)
            build_number = value_from_metadata('build_number')
        else:
            installed_version = value_from_metadata('version')
            build_number = value_from_metadata('build_number')

        if installed_version is None:
            return

        cursor = self.txtAbout.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertBlock()
        cursor.insertBlock()

        # Insert installed version text
        version_msg = QApplication.translate(
            'AboutSTDMDialog',
            'STDM Version:'
        )
        version_text = '{0} {1}'.format(version_msg, installed_version)
        char_format = cursor.blockCharFormat()
        text_format = QTextCharFormat(char_format)
        text_format.setFontWeight(75)
        cursor.insertText(version_text, text_format)

        # Build number
        build_msg = QApplication.translate('AboutSTDMDialog', 'Build Number:')
        build_text = f'{build_msg} {build_number}'

        cursor = self.txtAbout.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertBlock()

        char_format = cursor.blockCharFormat()
        text_format = QTextCharFormat(char_format)
        text_format.setFontWeight(75)
        cursor.insertText(build_text, text_format)

    def onSTDMHome(self):
        """
        Load STDM home page using the system's default browser.
        """
        stdmURL = "http://www.stdm.gltn.net"
        QDesktopServices.openUrl(QUrl(stdmURL))

    def onContactUs(self):
        """
        Load STDM contact page.
        """
        contactURL = "http://www.stdm.gltn.net/?page_id=291"
        QDesktopServices.openUrl(QUrl(contactURL))
