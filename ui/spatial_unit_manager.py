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

from PyQt4 import uic
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from qgis.core import *
from gps_tool import GPSToolDialog

from stdm.settings import (
    current_profile,
    save_configuration
)
from stdm.data.configuration.social_tenure_updater import BASE_STR_VIEW
from stdm.data.pg_utils import (
    geometryType,
    spatial_tables,
    table_column_names,
    vector_layer
)
from stdm.data.xmlconfig_reader import (
    check_if_display_name_exits,
    get_xml_display_name
)
from stdm.data.xmlconfig_writer import (
    write_display_name,
    write_changed_display_name
)

from ui_spatial_unit_manager import Ui_SpatialUnitManagerWidget

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui_spatial_unit_manager.ui'))

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
        self.iface = iface
        self.gps_tool_dialog = None
        self.curr_lyr_table = None
        self.curr_lyr_sp_col = None
        self.curr_layer = None
        self._populate_layers()

    def reload(self):
        """
        Repopulates the list of layers in the current profile.
        """
        self._populate_layers()

    def _populate_layers(self):
        self.stdm_layers_combo.clear()

        curr_profile = current_profile()
        if curr_profile is None:
            msg = QApplication.translate('Spatial Unit Manager', 'There is '
                                                                 'no current '
                                                                 'profile '
                                                                 'configured. '
                                                                 'Please '
                                                                 'create one '
                                                                 'by running '
                                                                 'the wizard '
                                                                 'or set an '
                                                                 'existing '
                                                                 'one in the '
                                                                 'settings.'
                                         )
            QMessageBox.warning(self.iface.mainWindow(), 'Spatial Unit Manager',
                                msg)

            return

        #Get entities containing geometry columns based on the config info
        config_entities = curr_profile.entities
        geom_entities = [ge for ge in config_entities.values()
                         if ge.TYPE_INFO == 'ENTITY' and
                         ge.has_geometry_column()]
        geom_entity_names = [ge.name for ge in geom_entities]

        self._stdm_tables = {}
        self.spatial_layers = []
        self.layers_info = []
        sp_tables = spatial_tables()

        #Check whether the geometry tables specified in the config exist
        missing_tables = [geom_entity.name for geom_entity in geom_entities
                          if not geom_entity.name in sp_tables]

        #Notify user of missing tables if they exist
        if len(missing_tables) > 0:
            msg = QApplication.translate('Spatial Unit Manager', 'The following '
                                                                 'spatial tables '
                                                                 'are missing in '
                                                                 'the database:'
                                                                 '\n- {0}\nPlease '
                                                                 're-run the '
                                                                 'configuration '
                                                                 'wizard to create '
                                                                 'them.'.format('\n'.join(missing_tables)))
            QMessageBox.warning(self.iface.mainWindow(),
                                'Spatial Unit Manager', msg)

        #Append the corresponding view to the list of entity names
        str_view = u'{0}_{1}'.format(curr_profile.prefix, BASE_STR_VIEW)
        geom_entity_names.append(str_view)

        for spt in sp_tables:
            #Only load those tables/views that are in the current profile
            if not spt in geom_entity_names:
                continue

            sp_columns = table_column_names(spt, True)
            self._stdm_tables[spt] = sp_columns

            #Add spatial columns to combo box
            for sp_col in sp_columns:
                #Get column type and apply the appropriate icon
                geometry_typ = unicode(geometryType(spt, sp_col)[0])

                if geometry_typ == "POLYGON":
                    self.icon = QIcon(":/plugins/stdm/images/icons/layer_polygon.png")
                elif geometry_typ == "LINESTRING":
                    self.icon = QIcon(":/plugins/stdm/images/icons/layer_line.png")
                elif geometry_typ == "POINT":
                    self.icon = QIcon(":/plugins/stdm/images/icons/layer_point.png")
                else:
                    self.icon = QIcon(":/plugins/stdm/images/icons/table.png")

                # QMessageBox.information(None,"Title",str(geometry_typ))
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
            return

        sp_col_info = self.stdm_layers_combo.itemData(self.stdm_layers_combo.currentIndex())
        if sp_col_info is None:
            # Message: Spatial column information could not be found
            QMessageBox.warning(self.iface.mainWindow(), 'Spatial Unit Manager',
                                'Spatial Column Layer Could not be found')

        table_name, spatial_column = sp_col_info["table_name"], sp_col_info["col_name"]

        # Used in gpx_table.py
        self.curr_lyr_table = table_name
        self.curr_lyr_sp_col = spatial_column

        self.curr_layer = vector_layer(table_name, geom_column=spatial_column)

        if self.curr_layer.isValid():
            QgsMapLayerRegistry.instance().addMapLayer(self.curr_layer)

            # Append column name to spatial table
            _current_display_name = str(table_name) + "." + str(spatial_column)

            # Get configuration file display name if it exists
            if check_if_display_name_exits(_current_display_name):
                xml_display_name = get_xml_display_name(_current_display_name)
                self.curr_layer.setLayerName(xml_display_name)

            # Write initial display name as original name of the layer
            elif not check_if_display_name_exits(_current_display_name):
                write_display_name(_current_display_name, _current_display_name)
                self.curr_layer.setLayerName(_current_display_name)

    @pyqtSignature("")
    def on_set_display_name_button_clicked(self):
        '''
        Method to change display name
        '''
        layer_map = QgsMapLayerRegistry.instance().mapLayers()
        for name, layer in layer_map.iteritems():
            if layer == self.iface.activeLayer():
                _name = layer.name()
                display_name, ok = QInputDialog.getText(self,"Change Display Name",
                                                        "Current Name is {0}".format(layer.originalName()))
                if ok and display_name != '':
                    layer.setLayerName(display_name)
                    write_changed_display_name(_name, display_name)
                elif not ok and display_name == "":
                    layer.originalName()
            else:
                continue

    def update_layer_display_name(self):
        """
        Update the configuration with the new layer display name.
        """
        pass

    @pyqtSignature("")
    def on_import_gpx_file_button_clicked(self):
        """
        Method to load GPS dialog
        """
        layer_map = QgsMapLayerRegistry.instance().mapLayers()
        if not bool(layer_map):
            QMessageBox.warning(self,
                                "STDM",
                                "You must add a layer first from Spatial Unit "
                                "Manager to import GPX to")
        elif bool(layer_map):
            self.gps_tool_dialog = GPSToolDialog(self.iface, self.curr_layer, self.curr_lyr_table, self.curr_lyr_sp_col)
            self.gps_tool_dialog.show()
