# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Change Log
Description          : Handles the display of license agreements.
                       documents.
Date                 : 20/April/2016
copyright            : (C) 2016 by UN-Habitat and implementing partners.
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
from PyQt4.QtGui import (
    QDialog,
    QApplication
)
from PyQt4.QtCore import QUrl, Qt

# from stdm.settings.registryconfig import (
#     RegistryConfig,
#     SHOW_LICENSE
# )
# from stdm.data.license_doc import LicenseDocument
#
# from notification import NotificationBar, ERROR

from stdm.ui.ui_change_log import Ui_ChangeLog
from stdm.utils.util import file_text

class ChangeLog(QDialog, Ui_ChangeLog):
    def __init__(self, parent=None):
        """
        This class shows the change log.
        :param parent: The container of the dialog
        :type parent: QMainWindow or None
        :return: None
        :rtype: NoneType
        """
        QDialog.__init__(
            self, parent,
            Qt.WindowSystemMenuHint | Qt.WindowTitleHint
        )
        self.setupUi(self)
        self.buttonBox.accepted.connect(self.accept)
        # Add maximize buttons
        self.setWindowFlags(
            self.windowFlags() |
            Qt.WindowSystemMenuHint |
            Qt.WindowMaximizeButtonHint
        )

    def show_change_log(self, path):
        """
        Show STDM change log window if the user have never
        seen it before.
        :return: None
        :rtype: NoneType
        """
        change_log_path = '{}/html/change_log.htm'.format(path)
        change_log_url = QUrl()
        change_log_url.setPath(change_log_path)
        change_log_html = file_text(change_log_path)

        self.webView.setHtml(
            change_log_html, change_log_url
        )

        self.exec_()

