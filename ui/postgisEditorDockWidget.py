# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PostgisEditorDialog
                                 A QGIS plugin
 Plugin enables loading editing and saving layers back to PostGIS
                             -------------------
        begin                : 2015-04-08
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Erick Opiyo
        email                : e.omwandho@gmail.com
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

from PyQt4 import  uic
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from ui_edit_stdm_layer import Ui_PostgisEditorDialogBase
from ..data import (spatial_tables, vector_layer, geometryType)

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui_edit_stdm_layer.ui'))


class PostgisEditorDockWidgetDialog(QDockWidget, Ui_PostgisEditorDialogBase):
    def __init__(self, iface):
        """Constructor."""
        QDockWidget.__init__(self, iface.mainWindow())
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.populateLayers()

    def populateLayers(self):
        self.stdmLayersCombo.clear()
        self.model=QStandardItemModel(self.stdmLayersCombo)
        self.stdmTables = spatial_tables()
        self.spatial_layers = []
        for layer in self.stdmTables:
            self.spatial_layer = vector_layer(layer)
            self.layer_name = self.spatial_layer.name()
            self.geometry_type = geometryType(layer,"the_geom")[0]
            if self.geometry_type != '':
                self.layer_geometry_type = self.geometry_type
            elif self.geometry_type == '':
                self.layer_geometry_type = "None"
            self.loadLayer = self.layer_name + " | " + self.layer_geometry_type
            self.spatial_layers.append(self.loadLayer)
        self.stdmLayersCombo.addItems(self.spatial_layers)
        self.stdmLayersCombo.setCurrentIndex(0)

    def loadLayerToCanvas(self):
        self.addToCanvasButton.setEnabled(False)
        QMessageBox.information(self.iface.mainWindow(),QApplication.translate(""),"")
        self.addToCanvasButton.setEnabled(True)


    # def addLayers(self):
    #     self.comboBox.clear()
    #     self.layerList = self.populateLayers()
    #     self.comboBox.addItems(self.layerList)