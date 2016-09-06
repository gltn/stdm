# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Progress Dialog
Description          : A tool used to show progress bar.
Date                 : 13/August/2016
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

from PyQt4.QtGui import QApplication, QProgressDialog, QLabel, QMessageBox
from qgis.utils import iface

class STDMProgressDialog(QProgressDialog):
    def __init__(self, parent):

        """
        Initializes the progress dialog of
        the template updater with the option
        of updating the label of the dialog.
        :return:
        :rtype:
        """

        QProgressDialog.__init__(self, parent)
        self.title = None
        self.prog = None

    def overall_progress(self, title):
        """
        Initializes the progress dialog.
        :param parent: The parent of the dialog.
        :type parent: QWidget
        :return: The progress dialog initialized.
        :rtype: QProgressDialog
        """
        self.setFixedWidth(380)
        self.setFixedHeight(100)
        self.setWindowTitle(
            QApplication.translate(
                "STDMProgressDialog",
                title
            )
        )

        label = QLabel()
        self.setLabel(label)

        self.setCancelButton(None)

    def progress_message(self, message, val):
        """
        Shows progress message in the progress bar.
        :param message: Add a text if needed.
        :type message: String
        :param val: The template name
        :type val: String

        """
        text = '{0} {1}...'.format(message, val)
        self.setLabelText(
            QApplication.translate(
                'STDMProgressDialog',
                text
            )

        )

    def closeEvent(self, event):
        title = self.tr('Upgrade Interruption Error')
        message = self.tr(
            'Interrupting the upgrading '
            'process could lead to data<br>'
            'corruption due to an incomplete '
            'migration of existing data.<br>'
            '<br>'
            'Are you sure you want to '
            'cancel the upgrading process?'
        )
        warning_result = QMessageBox.critical(
            iface.mainWindow(),
            title,
            message,
            QMessageBox.Yes,
            QMessageBox.No

        )

        if warning_result:
            event.accept()
        else:
            event.ignore()
