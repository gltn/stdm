"""
Name                 : ProjectionSelector
Description          : Load generic projections selector dialog for user to
                      select the srs id
Date                 : 17/Oct/13
copyright            : (C) 2014 by UN-Habitat and implementing partners.
                       See the accompanying file CONTRIBUTORS.txt in the root
email                : stdm@unhabitat.org
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/

"""
from PyQt4.QtGui import QDialog
from qgis.gui import QgsGenericProjectionSelector


class ProjectionSelector(QDialog):

    def __init__(self, parent):
        super(ProjectionSelector, self).__init__(parent)
        self._parent = parent

    def load_available_systems(self):
        """
        :return:
        """
        coord_sys = ""
        crs_dlg = QgsGenericProjectionSelector(self._parent)
        if crs_dlg.exec_() == QDialog.Accepted:
            coord_sys = str(crs_dlg.selectedAuthId())
        return coord_sys
