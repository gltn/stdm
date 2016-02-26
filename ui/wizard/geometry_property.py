# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : geometry_property
Description          : Set properties for Date data type
Date                 : 02/January/2016
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
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtCore import *
from PyQt4.QtGui import (
    QDialog,
    QApplication,
    QMessageBox
)

from qgis.gui import QgsGenericProjectionSelector

from ui_geom_property import Ui_GeometryProperty

class GeometryProperty(QDialog, Ui_GeometryProperty):
    def __init__(self, parent, geom_type=None, coord_sys=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self._geom_type = geom_type
        self._coord_sys = coord_sys 

        self.initGui()

    def initGui(self):
        self.load_geometry_types()
        self.btnCoord.clicked.connect(self.projection_selector)

    def load_geometry_types(self):
        self.cboGeoType.clear()
        self.cboGeoType.addItems(['POINT', 'LINE', 'POLYGON',
                                        'MULTIPOINT', 'MULTILINE',
                                        'MULTIPOLYGON'])
        self.cboGeoType.setCurrentIndex(0)

    def projection_selector(self):
        # open QGIS projection selector
        projection_selector = QgsGenericProjectionSelector(self)

        if projection_selector.exec_() == QDialog.Accepted:
            #Remove 'EPSG:' part
            self._coord_sys = projection_selector.selectedAuthId()[5:]
            self.btnCoord.setText(projection_selector.selectedAuthId())

    def add_values(self):
        self._geom_type = self.cboGeoType.currentIndex()

    def geom_type(self):
        return self._geom_type
	    
    def coord_sys(self):
        return self._coord_sys
	    
    def accept(self):
        if not self._coord_sys:
            self.error_message(QApplication.translate("GeometryPropetyEditor","Geometry coordinate system not given!"))

            return

        self.add_values()
        self.done(1)

    def reject(self):
        self.done(0)
    
    def error_message(self, Message):
        # Error Message Box
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("STDM")
        msg.setText(Message)
        msg.exec_()  

