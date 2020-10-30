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

from qgis.PyQt.QtGui import (
    QPixmap
)
from qgis.PyQt.QtWidgets import (
    QDialog
)

from stdm.ui.ui_about_stdm import Ui_frmAbout


class AboutDialog(QDialog):

    # Class constructor
    def __init__(self, photoArray=None):
        QDialog.__init__(self)
        # Inherit from base UI class
        self.ui = Ui_frmAbout()
        # Call the initialize component method
        self.ui.setupUi(self)
        # Resources have been embedded
        # self.initDialog()
        self.ui.buttonBox.clicked.connect(self.close)

    def initDialog(self):
        # Fetch references
        logoPixMap = QPixmap(":/plugins/stdm/images/un_habitat.jpg")
        self.ui.lblLogo.setPixmap(logoPixMap)
        dirP = os.path.dirname(__file__)
        normPath = str(dirP) + '\stdm\summary.txt'
        # absPath=os.path.join(str(dir),'\stdm\summary.txt')
        aboutStream = open(os.path.normpath(normPath))
        about = aboutStream.read()
        # self.ui.lblAbout.setText(about)
