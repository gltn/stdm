# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Licence Agreement
Description          : Handles the display of license agreements.
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
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QDialog,
    QApplication
)

from stdm.data.license_doc import LicenseDocument
from stdm.settings.registryconfig import (
    RegistryConfig,
    SHOW_LICENSE
)
from stdm.ui.gui_utils import GuiUtils
from stdm.ui.notification import NotificationBar, ERROR

WIDGET, BASE = uic.loadUiType(
    GuiUtils.get_ui_file_path('ui_license_agreement.ui'))


class LicenseAgreement(WIDGET, BASE):
    def __init__(self, parent=None):
        """
        This class checks if the user has accepted the
        license terms and conditions or not . It shows the
        terms and conditions if not.
        :param parent: The container of the dialog
        :type parent: QMainWindow or None
        :return: None
        :rtype: NoneType
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.reg_config = RegistryConfig()
        self.notice_bar = NotificationBar(self.notifBar)
        self.accepted = False
        self.btnAccept.clicked.connect(self.accept_action)
        self.btnDecline.clicked.connect(self.decline_action)
        self.label.setStyleSheet(
            '''
            QLabel {
                font: bold;
            }
            '''
        )

    def check_show_license(self):
        """
        Checks if you need to show the license page.
        Checks if the flag in the registry has been set.
        Returns True to show license. If registry key
        is not yet set, show the license page.
        :rtype: boolean
        """
        show_lic = 1
        license_key = self.reg_config.read(
            [SHOW_LICENSE]
        )

        if len(license_key) > 0:
            show_lic = license_key[SHOW_LICENSE]

        if show_lic == 1 or show_lic == str(1):
            return True
        elif show_lic == 0 or show_lic == str(0):
            self.accepted = True
            return False

    def show_license(self):
        """
        Show STDM license window if the user have never
        accepted the license terms and conditions.
        :return: None
        :rtype: NoneType
        """
        # validate if to show license
        show_lic = self.check_show_license()
        # THe user didn't accept license
        if show_lic:
            license = LicenseDocument()

            self.termsCondArea.setText(
                license.read_license_info()
            )

            self.exec_()

    def accept_action(self):
        """
        A slot raised when the user clicks on the Accept button.
        :return: None
        :rtype: NoneType
        """
        if not self.checkBoxAgree.isChecked():
            msg = QApplication.translate(
                'LicenseAgreement',
                'To use STDM, please accept the terms '
                'and conditions by selecting'
                ' the checkbox "I have read and agree ..."'
            )

            self.notice_bar.clear()
            self.notice_bar.insertNotification(msg, ERROR)
            return

        else:
            self.reg_config.write({SHOW_LICENSE: 0})
            self.accepted = True
            self.close()

    def decline_action(self):
        """
        A slot raised when the user clicks on
        the decline button.
        :return: None
        :rtype: NoneType
        """
        self.accepted = False
        self.close()
