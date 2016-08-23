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
from PyQt4.QtGui import QApplication, QProgressDialog, QLabel

class STDMProgressDialog:
    def __init__(self):
        """
        Initializes the progress dialog of
        the template updater with the option
        of updating the label of the dialog.
        :return:
        :rtype:
        """
        self.title = None
        self.prog = None

    def overall_progress(self, title, parent=None):
        """
        Initializes the progress dialog.
        :param parent: The parent of the dialog.
        :type parent: QWidget
        :return: The progress dialog initialized.
        :rtype: QProgressDialog
        """

        self.prog = QProgressDialog(
            parent
        )
        self.prog.setFixedWidth(380)
        self.prog.setFixedHeight(100)
        self.prog.setWindowTitle(
            QApplication.translate(
                "STDMProgressDialog",
                title
            )
        )

        label = QLabel()
        self.prog.setLabel(label)

        self.prog.setCancelButton(None)
        self.prog.show()

        return self.prog

    def progress_message(self, message, val):
        """
        Shows progress message in the progress bar.
        :param val: The template name
        :type val: String
        :param skip: Shows Skipping text if True.
        :type skip: Boolean
        """

        text = '{0} {1}...'.format(val, message)
        self.prog.setLabelText(
            QApplication.translate(
                'STDMProgressDialog',
                text
            )

        )

