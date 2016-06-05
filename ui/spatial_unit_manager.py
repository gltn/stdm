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
from stdm.data.configuration import profile_foreign_keys
from stdm.data.pg_utils import (
    geometryType,
    spatial_tables,
    table_column_names,
    vector_layer
)
from stdm.mapping.utils import pg_layerNamesIDMapping
from stdm.data.xmlconfig_reader import (
    check_if_display_name_exits,
    get_xml_display_name
)
from stdm.data.xmlconfig_writer import (
    write_display_name,
    write_changed_display_name
)

from ui_spatial_unit_manager import Ui_SpatialUnitManagerWidget
from notification import NotificationBar,ERROR,INFO, WARNING

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
        self._curr_profile = None
        self._profile_spatial_layers = []
        self._populate_layers()
        self.curr_profile = current_profile()
        self.spatial_unit = None

    def _populate_layers(self):
        self.stdm_layers_combo.clear()

        self._curr_profile = current_profile()

        if self._curr_profile is None:

            return

        self.spatial_unit = self._curr_profile.social_tenure.spatial_unit

        #Get entities containing geometry columns based on the config info
        config_entities = self._curr_profile.entities
        geom_entities = [ge for ge in config_entities.values()
                         if ge.TYPE_INFO == 'ENTITY' and
                         ge.has_geometry_column()]

        self._profile_spatial_layers = []
        sp_tables = spatial_tables()

        #Check whether the geometry tables specified in the config exist
        missing_tables = [geom_entity.name for geom_entity in geom_entities
                          if not geom_entity.name in sp_tables]

        #Notify user of missing tables
        if len(missing_tables) > 0:
            msg = QApplication.translate(
                'Spatial Unit Manager',
                'The following '
                 'spatial tables '
                 'are missing in '
                 'the database:'
                 '\n {0}\nPlease '
                 're-run the '
                 'configuration '
                 'wizard to create '
                 'them.'.format('\n'.join(missing_tables)))
            QMessageBox.critical(
                self.iface.mainWindow(),
                'Spatial Unit Manager',
                msg
            )

        for e in geom_entities:
            table_name = e.name
            if table_name in sp_tables:
                for gc in e.geometry_columns():
                    column_name = gc.name
                    display_name = gc.layer_display()
                    self._add_geometry_column_to_combo(table_name,
                                                       column_name,
                                                       display_name,
                                                       gc)

                #Add geometry entity to the collection
                self._profile_spatial_layers.append(table_name)

        #Append the corresponding(profile) view to the list of entity names
        str_view = u'{0}_{1}'.format(self._curr_profile.prefix, BASE_STR_VIEW)
        if str_view in sp_tables:
            geom_columns = table_column_names(str_view, True)
            if len(geom_columns) > 0:
                #Pick the first column
                geom_col = geom_columns[0]
                view_layer_name = self._curr_profile.social_tenure.layer_display()
                self._add_geometry_column_to_combo(str_view, geom_col,
                                                   view_layer_name,
                                                   self._curr_profile.social_tenure)

                #Append view to the list of spatial layers
                self._profile_spatial_layers.append(str_view)

    def _format_layer_display_name(self, col, table):
        return u'{0}.{1}'.format(table,col)

    def _add_geometry_column_to_combo(self, table_name, column_name, display, item):
        icon = self._geom_icon(table_name, column_name)
        self.stdm_layers_combo.addItem(icon, display, {
            'table_name': table_name,
            'column_name': column_name,
            'item': item}
        )

        table = self.spatial_unit.name
        spatial_column = [c.name for c in self.spatial_unit.columns.values() if c.TYPE_INFO == 'GEOMETRY']
        spatial_unit_item = unicode(table + '.'+spatial_column[0])
        index = self.stdm_layers_combo.findText(spatial_unit_item, Qt.MatchFixedString)
        if index >= 0:
             self.stdm_layers_combo.setCurrentIndex(index)


    def _layer_info_from_table_column(self, table, column):
        #Returns the index and item data from the given table and column name
        idx, layer_info = -1, None

        for i in range(self.stdm_layers_combo.count()):
            layer_info = self.stdm_layers_combo.itemData(i)

            if layer_info['table_name'] == table and layer_info['column_name'] == column:
                idx, layer_info = i, layer_info

                break

        return idx, layer_info

    def _geom_icon(self, table, column):
        #Get column type and apply the appropriate icon
        geometry_typ = unicode(geometryType(table, column)[0])

        icon = None

        if geometry_typ == 'POLYGON':
            icon = QIcon(':/plugins/stdm/images/icons/layer_polygon.png')

        elif geometry_typ == 'LINESTRING':
            icon = QIcon(':/plugins/stdm/images/icons/layer_line.png')

        elif geometry_typ == 'POINT':
            icon = QIcon(':/plugins/stdm/images/icons/layer_point.png')

        else:
            icon = QIcon(':/plugins/stdm/images/icons/table.png')

        return icon

    @pyqtSignature("")
    def on_add_to_canvas_button_clicked(self):
        """
        Add STDM layer to map canvas.
        """
        if self.stdm_layers_combo.count() == 0:
            return

        sp_col_info = self.stdm_layers_combo.itemData(self.stdm_layers_combo.currentIndex())
        if sp_col_info is None:
            # Message: Spatial column information could not be found
            QMessageBox.warning(self.iface.mainWindow(), 'Spatial Unit Manager',
                                'Spatial Column Layer Could not be found')

        table_name, spatial_column = sp_col_info["table_name"], \
                                     sp_col_info["column_name"]


        #Check if the layer has already been added to the map layer registry
        tab_col = u'{0}.{1}'.format(table_name, spatial_column)
        if tab_col in self._map_registry_table_columns():
            return

        layer_item = sp_col_info.get('item', None)

        # Used in gpx_table.py
        self.curr_lyr_table = table_name
        self.curr_lyr_sp_col = spatial_column

        if not layer_item is None:
            curr_layer = vector_layer(table_name, geom_column=spatial_column,
                                      layer_name=layer_item.layer_display())
        else:
            curr_layer = vector_layer(table_name, geom_column=spatial_column)

        if curr_layer.isValid():
            QgsMapLayerRegistry.instance().addMapLayer(curr_layer)

            #Required in order for the layer name to be set
            QTimer.singleShot(100,
                              lambda: self._set_layer_display_name(curr_layer,
                                               layer_item.layer_display()))
            #curr_layer.setLayerName(layer_item.layer_display())

        else:
            msg = QApplication.translate("Spatial Unit Manager",
                                         "'{0}.{1}' layer is invalid, it cannot "
                                         "be added to the map view.".format(
                                             table_name,spatial_column))
            QMessageBox.critical(self.iface.mainWindow(), 'Spatial Unit Manager', msg)

    def _set_layer_display_name(self, layer, name):
        layer.setLayerName(name)

    def _layer_table_column(self, layer):
        #Returns the table and column name that a leyer belongs to.
        table, column = '', ''

        if hasattr(layer, 'dataProvider'):
            if layer.dataProvider().name() == 'postgres':
                layerConnStr = layer.dataProvider().dataSourceUri()
                dataSourceURI = QgsDataSourceURI(layerConnStr)
                table, column = dataSourceURI.table(), \
                                dataSourceURI.geometryColumn()

        return table, column

    def _map_registry_table_columns(self):
        """
        Returns a list of layers in form of table names concatenated with the
        column names separated by a full-stop.
        """
        tab_col_names = []
        layers = QgsMapLayerRegistry.instance().mapLayers()

        for layer in layers.values():
            table, column = self._layer_table_column(layer)
            if table and column:
                tab_col_names.append(u'{0}.{1}'.format(table, column))

        return tab_col_names

    @pyqtSignature("")
    def on_set_display_name_button_clicked(self):
        """
        Method to change display name
        """
        layer_names_ids = pg_layerNamesIDMapping().reverse
        layer = self.iface.activeLayer()

        if not layer is None:
            table_name = layer_names_ids.get(layer.id(), '')

            if table_name:
                #Check if the table name is in the current profile
                if table_name in self._profile_spatial_layers:
                    prompt = u"Set the display name for '{0}' layer".format(layer.name())
                    display_name, ok = QInputDialog.getText(self,
                                                            'Spatial Unit '
                                                            'Manager', prompt)

                    if ok and display_name:
                        #Get layer table and columns names
                        table, column = self._layer_table_column(layer)
                        if table and column:
                            idx, layer_info = \
                                self._layer_info_from_table_column(table,
                                                                   column)
                            #Get item in the combo corresponding to the layer
                            if idx != -1:
                                self.stdm_layers_combo.setItemText(idx,
                                                                   display_name)
                                layer.setLayerName(display_name)

                                #Update configuration item
                                config_item = layer_info.get('item', None)
                                if not config_item is None:
                                    config_item.layer_display_name = \
                                        display_name

                                    #Update configuration
                                    save_configuration()

                else:
                    msg = QApplication.translate("Spatial Unit Manager",
                                                 u"The layer does not "
                                                 u"belong in the '{0}' "
                                                 u"profile.\nThe display name "
                                                 u"will not be set."
                                                 u"".format(
                                                     self._curr_profile.name))
                    QMessageBox.critical(self.iface.mainWindow(),
                                'Spatial Unit Manager', msg)

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
