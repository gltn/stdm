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
from gps_tool_GUI import GPSToolDialog
from ..data import (
    spatial_tables,
    table_column_names,
    vector_layer,
    geometryType,
    write_display_name,
    check_if_display_name_exits,
    get_xml_display_name,
    write_changed_display_name
)

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui_edit_stdm_layer.ui'))

class SpatialUnitManagerDockWidget(QDockWidget, Ui_SpatialUnitManagerWidget):
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
        self.gps_tool_dialog = GPSToolDialog(self.iface)

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
                else:
                    self.icon = QIcon(":/plugins/stdm/images/icons/table.png")

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
            QMessageBox.warning(None,"No Layers")

        sp_col_info= self.stdm_layers_combo.itemData(self.stdm_layers_combo.currentIndex())
        if sp_col_info is None:
            #Message: Spatial column information could not be found
            QMessageBox.warning(None,"Spatial Column Layer Could not be found")

        table_name,spatial_column = sp_col_info["table_name"],sp_col_info["col_name"]

        curr_layer = vector_layer(table_name,geom_column=spatial_column)

        if curr_layer.isValid():
            QgsMapLayerRegistry.instance().addMapLayer(curr_layer)

            # Append column name to spatial table
            _current_display_name = str(table_name) + "." + str(spatial_column)

            # Get configuration file display name if it exists
            if check_if_display_name_exits(_current_display_name):
                xml_display_name = get_xml_display_name(_current_display_name)
                curr_layer.setLayerName(xml_display_name)

            # Write initial display name as original name of the layer
            elif not check_if_display_name_exits(_current_display_name):
                write_display_name(_current_display_name, _current_display_name)
                curr_layer.setLayerName(_current_display_name)

    @pyqtSignature("")
    def on_set_display_name_button_clicked(self):
        '''
        Method to change display name
        '''
        layer_map = QgsMapLayerRegistry.instance().mapLayers()
        for name, layer in layer_map.iteritems():
            if layer == self.iface.activeLayer():
                _name = layer.name()
                display_name, ok = QInputDialog.getText(None,"Change Display Name",
                                                        "Current Name is {0}".format(layer.originalName()))
                if ok and display_name != "":
                    layer.setLayerName(display_name)
                    write_changed_display_name(_name, display_name)
                elif not ok and display_name == "":
                    layer.originalName()
            else:
                continue

    @pyqtSignature("")
    def on_import_gpx_file_button_clicked(self):
        """
        Method to load GPS dialog
        """
        layer_map = QgsMapLayerRegistry.instance().mapLayers()
        if not bool(layer_map):
            QMessageBox.warning(None,"STDM","You must add a layer first, from Spatial Unit Manager to import GPX to")
        elif bool(layer_map):
            self.gps_tool_dialog.show()