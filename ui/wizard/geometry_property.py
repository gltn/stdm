# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : geometry_property
Description          : Set properties for Geometry data type
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
    Geometry column property editor
    """
    def __init__(self, parent, form_fields):
        """
        :param parent: Owner of this dialog window
        :type parent: QWidget
        :param form_fields: Dictionary used to pass parameters from
         column editor
        :type form_fields: dictionary
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self._geom_type = form_fields['geom_type']
        self._srid = form_fields['srid']

        self.init_gui()

    def srid(self):
        if self._srid=="":
            return "Select..."
        else:
            return self._srid

    def init_gui(self):
        """
        Initializes form fields
        """
        self.load_geometry_types()
        self.btnCoord.clicked.connect(self.projection_selector)
        self.cboGeoType.setCurrentIndex(self._geom_type)
        self.btnCoord.setText(unicode(self.srid()))

    def load_geometry_types(self):
        """
        Initializes geometry combobox with geometry types
        """
        self.cboGeoType.clear()
        self.cboGeoType.addItems(geom_types)
        self.cboGeoType.setCurrentIndex(0)

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
        """
        Sets geom type properties with values from form widgets
        """
        self._geom_type = self.cboGeoType.currentIndex()

    def geom_type(self):
        """
        Returns geometry type property
        :rtype: str
        """
        return self._geom_type
	    
    def coord_sys(self):
        """
        Returns projection type
        :rtype: str
        """
        return self._srid
	    
    def accept(self):
        if self._srid =="":
            self.show_message(QApplication.translate("GeometryPropetyEditor",
                "Please set geometry coordinate system"))
            return

        self.add_values()
        self.done(1)

    def reject(self):
        self.done(0)

    def show_message(self, message, msg_icon=QMessageBox.Critical):
        msg = QMessageBox(self)
        msg.setIcon(msg_icon)
        msg.setWindowTitle(QApplication.translate("STDM Configuration Wizard","STDM"))
        msg.setText(QApplication.translate("STDM Configuration Wizard",message))
        msg.exec_()
