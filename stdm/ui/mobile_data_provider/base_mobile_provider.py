"""
/***************************************************************************
Name                 : wizard
Description          : Mobile provider export and import wizard
Date                 : 25/March/2023
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

from qgis.PyQt import uic
from qgis.PyQt.QtCore import (
    pyqtSignal
)
from qgis.PyQt.QtWidgets import (
    QWizard,
    QMessageBox
)

from stdm.ui.gui_utils import GuiUtils

WIDGET, BASE = uic.loadUiType(
    GuiUtils.get_ui_file_path('mobile_data_provider/ui_mobile_provider_wizard.ui'))


class BaseMobileProvider(WIDGET, BASE):
    """
    STDM mobile provider export and import wizard
    """
    wizardFinished = pyqtSignal(object, bool)

    def __init__(self, parent, provider=None):
        QWizard.__init__(self, parent)
        self.msg = QMessageBox()
        self.msg.setWindowTitle("Base Mobile Provider")
        self.setupUi(self)
        self.provider = provider
        self.msg.setText("{provider}".format(provider=self.provider))
        self.msg.exec_()
