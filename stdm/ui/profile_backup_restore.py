
"""
/***************************************************************************
Name                 : ProfileBackupRestoreDialog
Description          : Dialog for doing restoring profile backup
Date                 : 01/05/2023
copyright            : (C) 2023 by UN-Habitat and implementing partners.
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

import os
import json
from zipfile import ZipFile

import subprocess
from subprocess import Popen

from qgis.PyQt import uic

from qgis.PyQt.QtWidgets import (
    QDialog,
    QFileDialog
)

from stdm.ui.gui_utils import GuiUtils
from stdm.data.config import DatabaseConfig
from stdm.data.configuration.stdm_configuration import StdmConfiguration
from stdm.data.connection import DatabaseConnection
from stdm.data.configuration.profile import Profile
from stdm.security.user import User

from stdm.utils.logging_handlers import (
    StreamHandler,
    FileHandler,
    StdOutHandler
)

WIDGET, BASE = uic.loadUiType(
    GuiUtils.get_ui_file_path('ui_profile_backup_restore.ui')
)

class ProfileBackupRestoreDialog(WIDGET, BASE):
    def __init__(self, iface):
        QDialog.__init__(self, iface.mainWindow())
        self.setupUi(self)
        self.iface = iface