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
import logging
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
from stdm.data.pg_utils import (
    pg_views
)


from stdm.ui.forms.spatial_unit_form import (
    STDMFieldWidget
)

from stdm.mapping.utils import pg_layerNamesIDMapping

from ui_spatial_unit_manager import Ui_SpatialUnitManagerWidget

FORM_CLASS, _ = uic.loadUiType(
    os.path.join(
    os.path.dirname(__file__), 'ui_spatial_unit_manager.ui'))

LOGGER = logging.getLogger('stdm')

class SpatialUnitManagerDockWidget(
    QDockWidget, Ui_SpatialUnitManagerWidget
):
    onLayerAdded = pyqtSignal(str, object)
    def __init__(self, iface, plugin=None):
        """Constructor."""
        QDockWidget.__init__(self, iface.mainWindow())
        # Set up the user interface from Designer.
        self.setupUi(self)
        self.iface = iface
        self._plugin = plugin
        self.gps_tool_dialog = None
        self.curr_lyr_table = None
        self.curr_lyr_sp_col = None
        self.curr_layer = None
        self.setMaximumHeight(250)
        self._curr_profile = current_profile()
        self._profile_spatial_layers = []
        self.stdm_fields = STDMFieldWidget()
        self._populate_layers()

        self.spatial_unit = None
        
        self.iface.currentLayerChanged.connect(
            self.control_digitize_toolbar
        )
        self.onLayerAdded.connect(
            self.init_spatial_form
        )
        self.add_to_canvas_button.clicked.connect(
            self.on_add_to_canvas_button_clicked
        )

    def _populate_layers(self):
        self.stdm_layers_combo.clear()

        if self._curr_profile is None:

            return

        self.spatial_unit = self._curr_profile.\
            social_tenure.spatial_unit

        # Get entities containing geometry
        # columns based on the config info
        config_entities = self._curr_profile.entities
        self.geom_entities = [
            ge for ge in config_entities.values()
            if ge.TYPE_INFO == 'ENTITY' and
            ge.has_geometry_column()
        ]

        self._profile_spatial_layers = []
        self.sp_tables = spatial_tables()

        for e in self.geom_entities:
            table_name = e.name
            if table_name in self.sp_tables:
                for gc in e.geometry_columns():
                    column_name = gc.name
                    display_name = gc.layer_display()
                    self._add_geometry_column_to_combo(
                        table_name,
                        column_name,
                        display_name,
                        gc
                    )

                #Add geometry entity to the collection
                self._profile_spatial_layers.append(
                    table_name
                )

        # Append the corresponding(profile)
        # view to the list of entity names
        str_view = self._curr_profile.social_tenure.view_name
        if str_view in self.sp_tables:
            self.str_view_geom_columns = table_column_names(
                str_view, True
            )
            if len(self.str_view_geom_columns) > 0:
                #Pick the first column
                # geom_col = geom_columns[0]
                for i, geom_col in enumerate(self.str_view_geom_columns):
                    if i > 0:
                        view_layer_name = self._curr_profile. \
                            social_tenure.layer_display()
                        view_layer_name = '{}.{}'.format(
                            view_layer_name, geom_col
                        )
                    else:
                        view_layer_name = self._curr_profile. \
                            social_tenure.layer_display()

                    self._add_geometry_column_to_combo(
                        str_view,
                        geom_col,
                        view_layer_name,
                        self._curr_profile.social_tenure
                    )
                    #Append view to the list of spatial layers
                    self._profile_spatial_layers.append(
                        str_view
                    )

    def control_digitize_toolbar(self, curr_layer):
        if not curr_layer is None:
            try:
                table, column = self._layer_table_column(
                    curr_layer
                )
                if table not in pg_views():
                    # Make sure digitizing toolbar is enabled
                    self.iface.digitizeToolBar().setEnabled(True)
                    self.set_canvas_crs(curr_layer)
                elif table in pg_views():
                    self.iface.digitizeToolBar().setEnabled(False)
            except Exception:
                pass

    def set_canvas_crs(self, layer):
        # Sets canvas CRS
        # get srid with EPSG text
        if layer.isValid():
            full_srid = layer.crs().authid().split(':')
            srid = int(full_srid[1])
            layer_crs = QgsCoordinateReferenceSystem(
                srid,
                QgsCoordinateReferenceSystem.EpsgCrsId
            )

            self.iface.mapCanvas().mapRenderer().setDestinationCrs(layer_crs)


    def init_spatial_form(self, spatial_column, curr_layer):
        """
        Initializes the Layer form.
        :param curr_layer: The layer for which
        the widgets are set.
        :type curr_layer: QgsVectorLayer
        :return: None
        :rtype: NoneType
        """
        table, column = self._layer_table_column(curr_layer)
        if table not in pg_views() and not curr_layer is None:
            try:
                self.stdm_fields.init_form(
                    table, spatial_column, curr_layer
                )
            except Exception as ex:
                LOGGER.debug(unicode(ex))

    def _format_layer_display_name(self, col, table):
        return u'{0}.{1}'.format(table,col)

    def _add_geometry_column_to_combo(
            self, table_name, column_name, display, item
    ):
        icon = self._geom_icon(table_name, column_name)
        self.stdm_layers_combo.addItem(icon, display, {
            'table_name': table_name,
            'column_name': column_name,
            'item': item}
        )

        table = self.spatial_unit.name
        spatial_column = [
            c.name
            for c in self.spatial_unit.columns.values()
            if c.TYPE_INFO == 'GEOMETRY'
        ]

        spatial_unit_item = unicode(
            table + '.'+spatial_column[0]
        )
        index = self.stdm_layers_combo.findText(
            spatial_unit_item, Qt.MatchFixedString
        )
        if index >= 0:
             self.stdm_layers_combo.setCurrentIndex(index)


    def _layer_info_from_table_column(
            self, table, column
    ):
        #Returns the index and item
        # data from the given table and column name
        idx, layer_info = -1, None

        for i in range(self.stdm_layers_combo.count()):
            layer_info = self.stdm_layers_combo.itemData(i)

            if layer_info['table_name'] == table and \
                            layer_info['column_name'] == column:
                idx, layer_info = i, layer_info

                break

        return idx, layer_info

    def _geom_icon(self, table, column):
        #Get column type and apply the appropriate icon
        geometry_typ = unicode(geometryType(table, column)[0])

        icon = None

        if geometry_typ == 'POLYGON':
            icon = QIcon(
                ':/plugins/stdm/images/icons/layer_polygon.png'
            )

        elif geometry_typ == 'LINESTRING':
            icon = QIcon(
                ':/plugins/stdm/images/icons/layer_line.png'
            )

        elif geometry_typ == 'POINT':
            icon = QIcon(
                ':/plugins/stdm/images/icons/layer_point.png'
            )

        else:
            icon = QIcon(
                ':/plugins/stdm/images/icons/table.png'
            )

        return icon

    def add_layer_by_name(self, layer_name):
        """
        Add a layer when a name is supplied.
        :param layer_name: The stdm layer name
        :type layer_name: String
        :return: None
        :rtype: NoneType
        """
        index = self.stdm_layers_combo.findText(
            layer_name, Qt.MatchFixedString
        )
        if index >= 0:

            self.stdm_layers_combo.setCurrentIndex(index)
            # add spatial unit layer.
            self.on_add_to_canvas_button_clicked()

    def geom_col_layer_name(self, table, col):
        """
        Returns the layer name based on geom column object.
        :param col: Column Object
        :type col: Object
        :param table: Table name
        :type table: String
        :return: Layer name
        :rtype: String
        """
        # Check if the geom has display name, if not,
        # get layer name with default naming.

        if col.layer_display_name == '':
            spatial_layer_item = unicode(
                '{}.{}'.format(
                    table, col.name
                )
            )
        # use the layer_display_name
        else:
            spatial_layer_item = col.layer_display_name
        return spatial_layer_item

    def on_add_to_canvas_button_clicked(self):
        """
        Add STDM layer to map canvas.
        """
        if self.stdm_layers_combo.count() == 0:
            return

        sp_col_info = self.stdm_layers_combo.itemData(
            self.stdm_layers_combo.currentIndex()
        )
        if sp_col_info is None:
            title = QApplication.translate(
                'SpatialUnitManagerDockWidget',
                'Spatial Unit Manager'
            )
            msg = QApplication.translate(
                'SpatialUnitManagerDockWidget',
                'Spatial Column Layer Could not be found'
            )
            # Message: Spatial column information
            # could not be found
            QMessageBox.warning(
                self.iface.mainWindow(),
                title,
                msg
            )

        table_name, spatial_column = sp_col_info["table_name"], \
                                     sp_col_info["column_name"]


        #Check if the layer has already been
        layer_item = sp_col_info.get('item', None)

        layer_name = self.geom_col_layer_name(
            table_name, layer_item
        )

        if layer_name in self._map_registry_layer_names():
            return

        # Used in gpx_table.py
        self.curr_lyr_table = table_name
        self.curr_lyr_sp_col = spatial_column

        if not layer_item is None:
            curr_layer = vector_layer(
                table_name,
                geom_column=spatial_column,
                layer_name=layer_item.layer_display()
            )
        else:
            curr_layer = vector_layer(
                table_name, geom_column=spatial_column
            )

        if curr_layer.isValid():

            QgsMapLayerRegistry.instance().addMapLayer(
                curr_layer
            )

            self.toggle_entity_multi_layers(curr_layer)

            self.set_canvas_crs(curr_layer)
            #Required in order for the layer name to be set
            QTimer.singleShot(
                100,
                lambda: self._set_layer_display_name(
                    curr_layer,
                    layer_item.layer_display()
                )
            )
            self.zoom_to_layer()
            self.onLayerAdded.emit(spatial_column, curr_layer)
        else:
            msg = QApplication.translate(
                "Spatial Unit Manager",
                "'{0}.{1}' layer is invalid, it cannot "
                "be added to the map view.".format(
                    table_name,spatial_column
                )
            )
            QMessageBox.critical(
                self.iface.mainWindow(),
                'Spatial Unit Manager',
                msg
            )

    def zoom_to_layer(self):
        """
        Zooms the map canvas to the extent
        the active layer.
        :return:
        :rtype:
        """
        layer = self.iface.activeLayer()
        if not layer is None:
            self.iface.mapCanvas().setExtent(
                layer.extent()
            )
            self.iface.mapCanvas().refresh()

    def geom_columns(self, entity):
        """
        Get the geometry column
        :return:
        :rtype:
        """
        geom_column = [
            column
            for column in entity.columns.values()
            if column.TYPE_INFO == 'GEOMETRY'
        ]
        return geom_column

    def same_entity_layers(self):
        """
        Returns layer names of an entity if they are
        more than one in one entity.
        :return: List in a list
        :rtype: List
        """
        entity_layers = []
        for entity in self.geom_entities:
            layer_list = self.entity_layer_names(entity)
            entity_layers.append(layer_list)
        return entity_layers

    def entity_layer_names(self, entity):
        """
        Returns layer names of an entity if
        they are more than one in one entity.
        :param entity: The Entity object
        :param type: Object
        :return: List in a list
        :rtype: List
        """
        cols = self.geom_columns(entity)
        layer_list = []

        for col in cols:
            lyr_name = self.geom_col_layer_name(
                entity.name, col
            )
            layer_list.append(lyr_name)
        return layer_list

    def layer_entity_children(self, sel_lyr_name):

        layer_lists = [
            layer_list
            for layer_list in self.same_entity_layers()
            if sel_lyr_name in layer_list
        ]


        str_view = self._curr_profile.social_tenure.view_name

        if len(layer_lists) < 1:

            geom_columns = table_column_names(
                str_view, True
            )
            layer_lists =  [geom_columns]

        return layer_lists

    def toggle_entity_multi_layers(self, new_layer):
        """
        Removes other layers created from the entity
        of the new layer.
        :param new_layer: The new layer added
        :type new_layer: QgsVectorLayer
        :return: None
        :rtype: NoneType
        """
        sel_lyr_name = new_layer.name()

        layer_lists = self.layer_entity_children(
            sel_lyr_name
        )
        # Include layers for toggling whose entity
        # has more than one geometry

        if len(layer_lists) < 1:
            return
        # if the layer_list is the
        # parent of selected layer
        for layer_name in layer_lists[0]:
            # remove other layers
            # of the same entity
            if layer_name != sel_lyr_name:

                layer_objects = QgsMapLayerRegistry.\
                    instance().mapLayersByName(layer_name)

                if len(layer_objects) > 0:
                    for layer in layer_objects:
                        layer_id = layer.id()
                        QgsMapLayerRegistry.\
                            instance().removeMapLayer(layer_id)
            # Change the crs of the canvas based on the new layer

            layer_list = QgsMapLayerRegistry.instance(). \
                mapLayersByName(sel_lyr_name)
            if len(layer_list) > 0:
                self.set_canvas_crs(
                    layer_list[0]
                )



    def _set_layer_display_name(self, layer, name):
        try:
            layer.setLayerName(name)
        except RuntimeError:
            pass

    def _layer_table_column(self, layer):
        #Returns the table and column name
        # that a layer belongs to.
        table, column = '', ''

        if hasattr(layer, 'dataProvider'):
            if layer.dataProvider().name() == 'postgres':
                layerConnStr = layer.dataProvider().dataSourceUri()
                dataSourceURI = QgsDataSourceURI(layerConnStr)
                table, column = dataSourceURI.table(), \
                                dataSourceURI.geometryColumn()

        return table, column

    def _map_registry_layer_names(self):
        """
        Returns a list of layers names.
        """
        layers = QgsMapLayerRegistry.instance().mapLayers()
        layer_names = [lyr.name() for lyr in layers.values()]
        return layer_names

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
                    prompt = \
                        u"Set the display name for '{0}' layer".format(
                            layer.name()
                        )
                    display_name, ok = QInputDialog.getText(
                        self,
                        'Spatial Unit '
                        'Manager', prompt
                    )

                    if ok and display_name:
                        #Get layer table and columns names
                        table, column = self._layer_table_column(layer)
                        if table and column:
                            idx, layer_info = \
                                self._layer_info_from_table_column(
                                    table,
                                    column
                                )
                            #Get item in the combo corresponding to the layer
                            if idx != -1:
                                self.stdm_layers_combo.setItemText(
                                    idx,
                                    display_name
                                )
                                layer.setLayerName(display_name)

                                #Update configuration item
                                config_item = layer_info.get('item', None)
                                if not config_item is None:
                                    config_item.layer_display_name = \
                                        display_name

                                    #Update configuration
                                    save_configuration()

                else:
                    msg = QApplication.translate(
                        "Spatial Unit Manager",
                        u"The layer does not "
                        u"belong in the '{0}' "
                        u"profile.\nThe display name "
                        u"will not be set."
                        u"".format(
                            self._curr_profile.name
                        )
                    )
                    QMessageBox.critical(
                        self.iface.mainWindow(),
                        'Spatial Unit Manager',
                        msg
                    )

    @pyqtSignature("")
    def on_import_gpx_file_button_clicked(self):
        """
        Method to load GPS dialog
        """
        layer_map = QgsMapLayerRegistry.instance().mapLayers()
        if not bool(layer_map):
            QMessageBox.warning(
                self,
                "STDM",
                "You must add a layer first from Spatial Unit "
                "Manager to import GPX to"
            )
        elif bool(layer_map):
            self.gps_tool_dialog = GPSToolDialog(
                self.iface,
                self.curr_layer,
                self.curr_lyr_table,
                self.curr_lyr_sp_col
            )
            self.gps_tool_dialog.show()


    def closeEvent(self, event):
        """
        On close of the dock window, this event is executed
        to run close_dock method
        :param event: The close event
        :type QCloseEvent
        :return: None
        """
        self._plugin.spatialLayerManager.setChecked(False)

