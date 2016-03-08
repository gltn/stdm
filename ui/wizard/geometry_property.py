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

geom_types = ['POINT', 'LINE', 'POLYGON', 'MULTIPOINT', 'MULTILINE',
'MULTIPOLYGON']

class GeometryProperty(QDialog, Ui_GeometryProperty):
    """
    Geometry type property editor
    """
    def __init__(self, parent, form_fields):
        """
        :param parent: Owner of this dialog window
        :type parent: QWidget
        :param form_fields: Dictionary for form fields
        :type form_fields: dictionary
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self._geom_type = form_fields['geom_type']
        self._srid = form_fields['srid']

        self.init_gui()

    def init_gui(self):
        """
        Initializes form fields
        """
        self.load_geometry_types()
        self.btnCoord.clicked.connect(self.projection_selector)
        self.cboGeoType.setCurrentIndex(self._geom_type)
        self.btnCoord.setText(self._srid)

    def load_geometry_types(self):
        """
        Initializes geometry combobox with geometry types
        """
        self.cboGeoType.clear()
        self.cboGeoType.addItems(geom_types)
        self.cboGeoType.setCurrentIndex(0)

    def projection_selector_TEST(self):
        self._srid = '4236'  #projection_selector.selectedAuthId()[5:]
        self.btnCoord.setText('EPSG: 4236')

    def projection_selector(self):
        """
        Opens the QGIS projection selector
        """
        projection_selector = QgsGenericProjectionSelector(self)

        if projection_selector.exec_() == QDialog.Accepted:
            #Remove 'EPSG:' part
            self._srid = projection_selector.selectedAuthId()[5:]
            self.btnCoord.setText(projection_selector.selectedAuthId())

    def add_values(self):
        self._geom_type = self.cboGeoType.currentIndex()

    def geom_type(self):
        return self._geom_type
	    
    def coord_sys(self):
        return self._srid
	    
    def accept(self):
        if not self._srid:
            self.error_message(QApplication.translate("GeometryPropetyEditor",
                "Please set geometry coordinate system"))

            return

        self.add_values()
        self.done(1)

    def reject(self):
        self.done(0)
    
    def error_message(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("STDM")
        msg.setText(message)
        msg.exec_()  

