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
from qgis.core import *
from ui_edit_stdm_layer import Ui_SpatialUnitManagerWidget
from ..data import (
    spatial_tables,
    table_column_names,
    vector_layer,
    geometryType
)

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui_edit_stdm_layer.ui'))

class PostgisEditorDockWidgetDialog(QDockWidget, Ui_SpatialUnitManagerWidget):
    def __init__(self, iface):
        """Constructor."""
        QDockWidget.__init__(self, iface.mainWindow())
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self._populate_layers()
        self.iface = iface


    def _populate_layers(self):
        self.stdm_layers_combo.clear()
        self._stdm_tables = {}
        self.spatial_layers = []
        self.layers_info = []
        for spt in spatial_tables():
            sp_columns = table_column_names(spt,True)
            self._stdm_tables[spt]=sp_columns
            #Add spatial columns to combo box
            for sp_col in sp_columns:
                #Get column type and apply the appropriate icon
                geometry_typ = str(geometryType(spt,sp_col)[0])

                if geometry_typ == "POLYGON":
                    self.icon = QIcon(":/plugins/stdm/images/icons/layer_polygon.png")
                elif geometry_typ == "LINESTRING":
                    self.icon = QIcon(":/plugins/stdm/images/icons/layer_line.png")
                elif geometry_typ == "POINT":
                    self.icon = QIcon(":/plugins/stdm/images/icons/layer_point.png")

                #QMessageBox.information(None,"Title",str(geometry_typ))
                self.stdm_layers_combo.addItem(self.icon, self._format_layer_display_name(sp_col, spt),
                                             {"table_name":spt,"col_name": sp_col})

    def _format_layer_display_name(self, col, table):
        return u"{0}.{1}".format(table,col)

    @pyqtSignature("")
    def on_add_to_canvas_button_clicked(self):
        '''
        Method used to add layers to canvas
        '''
        if self.stdm_layers_combo.count() == 0:
            #Return message that there are no layers
            QMessageBox.warning(None,"No Laers")

        sp_col_info= self.stdm_layers_combo.itemData(self.stdm_layers_combo.currentIndex())
        if sp_col_info is None:
            #Message: Spatial column information could not be found
            QMessageBox.warning(None,"Spatial Column Layer Could not be found")

        table_name,spatial_column = sp_col_info["table_name"],sp_col_info["col_name"]

        curr_layer = vector_layer(table_name,geom_column=spatial_column)
        #QMessageBox.information(None,"Title",str(geometry_typ))
        if curr_layer.isValid():
            QgsMapLayerRegistry.instance().addMapLayer(curr_layer)

    @pyqtSignature("")
    def on_set_display_name_button_clicked(self):
        '''
        Method to change display name
        '''
        layer_map = QgsMapLayerRegistry.instance().mapLayers()
        for name, layer in layer_map.iteritems():
            if layer == self.iface.activeLayer():
                display_name, ok = QInputDialog.getText(None,"Change Display Name")
                if ok and display_name != "":
                    layer.setLayerName(display_name)
                elif not ok and display_name == "":
                    layer.originalName()
