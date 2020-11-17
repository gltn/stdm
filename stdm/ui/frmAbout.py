"""
/***************************************************************************
Name                 : About STDM
Description          : About STDM Dialog
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
import os

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QDialog
)

from stdm.ui.gui_utils import GuiUtils

WIDGET, BASE = uic.loadUiType(
    GuiUtils.get_ui_file_path('ui_about_stdm.ui'))


class AboutDialog(WIDGET, BASE):

    # Class constructor
    def __init__(self, photoArray=None):
        QDialog.__init__(self)
        # Call the initialize component method
        self.setupUi(self)
        # Resources have been embedded
        # self.initDialog()
        self.buttonBox.clicked.connect(self.close)

    def initDialog(self):
        # Fetch references
        logoPixMap = GuiUtils.get_icon_pixmap("un_habitat.jpg")
        self.lblLogo.setPixmap(logoPixMap)
        dirP = os.path.dirname(__file__)
        normPath = str(dirP) + '\stdm\summary.txt'
        # absPath=os.path.join(str(dir),'\stdm\summary.txt')
        aboutStream = open(os.path.normpath(normPath))
        about = aboutStream.read()
        # self.ui.lblAbout.setText(about)
