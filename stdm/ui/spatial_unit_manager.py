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

import logging
import re
from collections import OrderedDict

from qgis.PyQt import uic
from qgis.PyQt.QtCore import (
    pyqtSignal,
    Qt,
    QTimer
)
from qgis.PyQt.QtGui import (
    QFontMetrics
)
from qgis.PyQt.QtWidgets import (
    QDockWidget,
    QApplication,
    QMessageBox,
    QInputDialog
)
from qgis.core import (
    QgsProject,
    QgsVectorLayerJoinInfo,
    QgsCoordinateReferenceSystem,
    QgsDataSourceUri
)

from stdm.data.configuration.social_tenure import SocialTenure
from stdm.data.pg_utils import (
    geometryType,
    spatial_tables,
    table_column_names,
    vector_layer,
    pg_views
)
from stdm.mapping.utils import pg_layerNamesIDMapping
from stdm.settings import (
    current_profile,
    save_configuration
)
from stdm.ui.forms.spatial_unit_form import (
    STDMFieldWidget
)
from stdm.ui.gps_tool import GPSToolDialog
from stdm.ui.gui_utils import GuiUtils
from stdm.utils.util import (
    profile_and_user_views
)
from stdm.utils.layer_utils import LayerUtils

LOGGER = logging.getLogger('stdm')

WIDGET, BASE = uic.loadUiType(
    GuiUtils.get_ui_file_path('ui_spatial_unit_manager.ui'))


class SpatialUnitManagerDockWidget(WIDGET, BASE):
    onLayerAdded = pyqtSignal(str, object)

    def __init__(self, iface, plugin=None):
        QDockWidget.__init__(self, iface.mainWindow())
        # Set up the user interface from Designer.
        self.setupUi(self)

        self.iface = iface
        self._plugin = plugin
        self.gps_tool_dialog = None
        # properties of last added layer
        self.curr_lyr_table = None
        self.curr_lyr_sp_col = None

        # properties of the active layer
        self.active_entity = None
        self.active_table = None
        self.active_sp_col = None
        self.style_updated = None
        self.setMaximumHeight(300)
        self._curr_profile = current_profile()
        self._profile_spatial_layers = []
        self.stdm_fields = STDMFieldWidget(plugin)
        self._populate_layers()
        self._adjust_layer_drop_down_width()
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

        self.set_display_name_button.clicked.connect(
            self.set_display_name_button_clicked
        )

        self.import_gpx_file_button.clicked.connect(
            self.import_gpx_file
        )

        self.iface.projectRead.connect(self.on_project_opened)

    def on_project_opened(self):
        for _, layer in QgsProject.instance().mapLayers().items():
            source = self.layer_source(layer)
            if source is not bool and source is not None:
                self.init_spatial_form(self.active_sp_col, layer)

    def get_column_config(self, config, name):
        """
        Gets joined column name config.
        :param config: The config object
        :type config: ColumnConfig
        :param name: The column name
        :type name:String
        :return:
        :rtype:
        """
        configs = [c for c in config.columns() if c.name == name]
        if len(configs) > 0:
            return configs[0]
        else:
            return None

    def sort_joined_columns(self, layer, fk_fields):
        """
        Sort joined columns using the order in the configuration
        :param layer: The layer containing joined layers
        :type layer: QgsVectorLayer
        :return:
        :rtype:
        """
        if not hasattr(layer, 'attributeTableConfig'):
            return
        entity = self._curr_profile.entity_by_name(self.curr_lyr_table)

        config = layer.attributeTableConfig()
        columns = config.columns()
        updated_columns = []
        for column in columns:
            if column.name not in entity.columns.keys():
                continue
            if column.name in fk_fields.keys():

                # hide the lookup id column
                column.hidden = True
                header = entity.columns[column.name].header()

                joined_column_name = '{} {}'.format(header, fk_fields[column.name])

                joined_column = self.get_column_config(config, joined_column_name)

                if joined_column is not None:
                    updated_columns.append(joined_column)

                    updated_columns.append(column)

            else:
                updated_columns.append(column)

        config.setColumns(updated_columns)
        layer.setAttributeTableConfig(config)

    @staticmethod
    def execute_layers_join(layer, layer_field, column_header, fk_layer, fk_field):
        """
        Joins two layers with specified field.
        :param layer: The destination layer of the merge.
        :type layer: QgsVectorLayer
        :param layer_field: The source layer of the merge.
        :type layer_field: String
        :param fk_layer: The foreign key layer object.
        :type fk_layer: QgsVectorLayer
        :param fk_field: The foreign key layer field name.
        :type fk_field: String
        :return:
        :rtype:
        """
        join = QgsVectorLayerJoinInfo()
        join.joinLayerId = fk_layer.id()
        join.joinFieldName = 'id'

        join.setJoinFieldNamesSubset([fk_field])
        join.targetFieldName = layer_field
        join.memoryCache = True
        join.prefix = '{} '.format(column_header)
        layer.addJoin(join)

    def column_to_fk_layer_join(self, column, layer, join_field):
        """
        Creates and executes the join by creating fk layer and running the join
        method using a column object.
        :param column: The column object
        :type column: Object
        :param layer: The layer to contain the joined fk layer
        :type layer: QgsVectorLayer
        :param join_field: The join field that is in the fk layer
        :type join_field: String
        """
        fk_entity = column.entity_relation.parent
        fk_layer = vector_layer(
            fk_entity.name,
            layer_name=fk_entity.name
        )
        QgsProject.instance().addMapLayer(
            fk_layer, False
        )
        # hide the fk id column
        column.hidden = True
        header = column.header()

        self.execute_layers_join(layer, column.name, header, fk_layer, join_field)

    def join_fk_layer(self, layer, entity):
        """
        Joins foreign key to the layer by creating and choosing join fields.
        :param layer: The layer to contain the joined fk layer
        :type layer: QgsVectorLayer
        :param entity: The layer entity object
        :type entity: Object
        :return: A dictionary containing fk_field and column object
        :rtype: OrderedDict
        """

        if entity is None:
            return

        fk_columns = OrderedDict()
        for column in entity.columns.values():
            if column.TYPE_INFO == 'LOOKUP':
                fk_column = 'value'

            elif column.TYPE_INFO == 'ADMIN_SPATIAL_UNIT':
                fk_column = 'name'

            elif column.TYPE_INFO == 'FOREIGN_KEY':
                display_cols = column.entity_relation.display_cols

                if len(display_cols) > 0:
                    fk_column = display_cols[0]
                else:
                    fk_column = 'id'
            else:
                fk_column = None

            if fk_column is not None:
                self.column_to_fk_layer_join(column, layer, fk_column)
                fk_columns[column.name] = fk_column

        return fk_columns

    def _adjust_layer_drop_down_width(self):
        """
        Adjusts the layers combobox drop down to expand based on the layer name.
        """
        if len(self._profile_spatial_layers) > 0:
            longest_item = max(self._profile_spatial_layers, key=len)
            font_meter = QFontMetrics(self.fontMetrics())
            item_width = font_meter.width(longest_item) + 80
            self.stdm_layers_combo.setStyleSheet(
                '''*
                    QComboBox QAbstractItemView{
                        min-width: 60px;
                        width: %s px;
                    }
                ''' % item_width
            )

    def _populate_layers(self):
        self.stdm_layers_combo.clear()

        if self._curr_profile is None:
            return

        self.spatial_units = self._curr_profile.social_tenure.spatial_units

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
                for i, gc in enumerate(e.geometry_columns()):
                    column_name = gc.name

                    display_name = gc.layer_display()
                    if i > 0:
                        display_name = '{}.{}'.format(display_name, gc.name)
                    self._add_geometry_column_to_combo(
                        table_name,
                        column_name,
                        display_name,
                        gc
                    )

                # Add geometry entity to the collection
                self._profile_spatial_layers.append(
                    table_name
                )

        # Append the corresponding(profile) view to the list of entity names
        str_views = list(self._curr_profile.social_tenure.views.keys())

        for str_view in str_views:
            if str_view in self.sp_tables:
                self.str_view_geom_columns = table_column_names(
                    str_view, True
                )

                if len(self.str_view_geom_columns) > 0:
                    # Pick the first column
                    for i, geom_col in enumerate(self.str_view_geom_columns):
                        view_layer_name = str_view
                        if i > 0:
                            view_layer_name = '{}.{}'.format(
                                view_layer_name, geom_col
                            )

                        self._add_geometry_column_to_combo(
                            str_view,
                            geom_col,
                            view_layer_name,
                            self._curr_profile.social_tenure
                        )
                        # Append view to the list of spatial layers
                        self._profile_spatial_layers.append(
                            str_view
                        )
        # add old config views and custom views.
        for sp_table in self.sp_tables:
            if sp_table in pg_views() and sp_table not in str_views and \
                    sp_table in profile_and_user_views(
                self._curr_profile):
                view_geom_columns = table_column_names(
                    sp_table, True
                )

                for geom_col in view_geom_columns:
                    view_layer_name = '{}.{}'.format(
                        sp_table, geom_col
                    )
                    self._add_geometry_column_to_combo(
                        sp_table,
                        geom_col,
                        view_layer_name,
                        geom_col
                    )

    def control_digitize_toolbar(self, curr_layer):
        if curr_layer is not None:
            table, column = self._layer_table_column(
                curr_layer
            )
            
            if curr_layer.isSpatial() and table not in pg_views():
                # Make sure digitizing toolbar is enabled
                self.iface.digitizeToolBar().setEnabled(True)
                self.set_canvas_crs(curr_layer)
            elif table in pg_views():
                self.iface.digitizeToolBar().setEnabled(False)

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

            self.iface.mapCanvas().mapSettings().setDestinationCrs(layer_crs)

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

        if table not in pg_views() and curr_layer is not None:
            self.stdm_fields.init_form(
                table, spatial_column, curr_layer
            )

    def _format_layer_display_name(self, col, table):
        return '{0}.{1}'.format(table, col)

    def _add_geometry_column_to_combo(
            self, table_name, column_name, display, item
    ):
        icon = self._geom_icon(table_name, column_name)

        self.stdm_layers_combo.addItem(icon, display, {
            'table_name': table_name,
            'column_name': column_name,
            'item': item
        }
                                       )
        for spatial_unit in self.spatial_units:
            table = spatial_unit.name
            spatial_column = [
                c.name
                for c in spatial_unit.columns.values()
                if c.TYPE_INFO == 'GEOMETRY'
            ]

            spatial_unit_item = str(
                table + '.' + spatial_column[0]
            )
            index = self.stdm_layers_combo.findText(
                spatial_unit_item, Qt.MatchFixedString
            )
            if index >= 0:
                self.stdm_layers_combo.setCurrentIndex(index)

    def _layer_info_from_table_column(
            self, table, column
    ):
        # Returns the index and item
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
        # Get column type and apply the appropriate icon
        geometry_typ = str(geometryType(table, column)[0])

        icon = None

        if geometry_typ == 'POLYGON':
            icon = GuiUtils.get_icon(
                'layer_polygon.png'
            )

        elif geometry_typ == 'LINESTRING':
            icon = GuiUtils.get_icon(
                'layer_line.png'
            )

        elif geometry_typ == 'POINT':
            icon = GuiUtils.get_icon(
                'layer_point.png'
            )
        elif geometry_typ == 'MULTIPOLYGON':
            icon = GuiUtils.get_icon(
                'layer_polygon.png'
            )
        elif geometry_typ == 'MULTILINESTRING':
            icon = GuiUtils.get_icon(
                'layer_line.png'
            )
        else:
            icon = GuiUtils.get_icon(
                'table.png'
            )

        return icon

    def add_layer_by_name(self, layer_name):
        """
        Add a layer when a name is supplied.
        :param layer_name: The stdm layer name
        :type layer_name: String

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

        if col is None: return

        if isinstance(col, str):

            spatial_layer_item = '{}.{}'.format(table, col)

        elif isinstance(col, SocialTenure):
            spatial_layer_item = col.view_name

        elif col.layer_display_name == '':
            spatial_layer_item = '{0}'.format(col.entity.short_name)
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
            QMessageBox.warning(self.iface.mainWindow(), title, msg)

        table_name, spatial_column = sp_col_info["table_name"], \
                                     sp_col_info["column_name"]

        # Check if the layer has already been
        layer_item = sp_col_info.get('item', None)

        layer_name = self.geom_col_layer_name(
            table_name, layer_item
        )

        if layer_name in self._map_registry_layer_names():
            layer = QgsProject.instance().mapLayersByName(layer_name)[0]
            self.iface.setActiveLayer(layer)
            return

        self.curr_lyr_table = table_name
        self.curr_lyr_sp_col = spatial_column

        if layer_item is not None:
            if isinstance(layer_item, str):
                layer_name = layer_item
            else:
                layer_name = layer_item.layer_display()

            entity = self._curr_profile.entity_by_name(table_name)
            if entity is not None:
                geom_col_obj = entity.columns[spatial_column]

                srid = None
                if int(geom_col_obj.srid) >= 100000:
                    srid = geom_col_obj.srid

                curr_layer = vector_layer(
                    table_name,
                    geom_column=spatial_column,
                    layer_name=layer_name,
                    proj_wkt=srid
                )
            else:

                curr_layer = vector_layer(
                    table_name,
                    geom_column=spatial_column,
                    layer_name=layer_name,
                    proj_wkt=None
                )
        # for lookup layer.
        else:
            curr_layer = vector_layer(
                table_name, geom_column=spatial_column
            )

        if curr_layer is not None and curr_layer.isValid():
            if curr_layer.name() in self._map_registry_layer_names():
                return

            QgsProject.instance().addMapLayer(
                curr_layer
            )
            LayerUtils.tag_layer_as_stdm_layer(curr_layer)
            self.zoom_to_layer()

            self.onLayerAdded.emit(spatial_column, curr_layer)

            self.toggle_entity_multi_layers(curr_layer)

            self.set_canvas_crs(curr_layer)
            # Required in order for the layer name to be set
            if layer_name is not None:
                QTimer.singleShot(
                    100,
                    lambda: self._set_layer_display_name(
                        curr_layer,
                        layer_name
                    )
                )

            entity = self._curr_profile.entity_by_name(self.curr_lyr_table)
            fk_fields = self.join_fk_layer(curr_layer, entity)
            if entity is not None:
                self.sort_joined_columns(curr_layer, fk_fields)
                self.set_field_alias(curr_layer, entity, fk_fields)

        elif curr_layer is not None:
            msg = QApplication.translate(
                "Spatial Unit Manager",
                "'{0}.{1}' layer is invalid, it cannot "
                "be added to the map view.".format(
                    table_name, spatial_column
                )
            )
            QMessageBox.critical(
                self.iface.mainWindow(),
                'Spatial Unit Manager',
                msg
            )

    def set_field_alias(self, layer, entity, fk_fields):
        """
        Set the field alia for fk joined fields so that they are
        same as the child columns.
        :param layer: The layer containing the join
        :type layer: QgsVectorLayer
        :param entity: The entity of the layer
        :type entity: Object
        :param fk_fields: The dictionary containing the parent and child fields
        :type fk_fields: OrderedDict
        :return:
        :rtype:
        """
        for column, fk_field in fk_fields.items():
            header = entity.columns[column].header()

            f_index = layer.fields().indexFromName(
                '{} {}'.format(header, fk_field)
            )
            alias = '{} Value'.format(header)

            layer.setFieldAlias(f_index, alias)

    def zoom_to_layer(self):
        """
        Zooms the map canvas to the extent
        the active layer.
        :return:
        :rtype:
        """
        layer = self.iface.activeLayer()
        if layer is not None:
            self.iface.mapCanvas().setExtent(
                layer.extent()
            )
            self.iface.mapCanvas().refresh()

    def geom_columns(self, entity):
        """
        Returns the geometry columns of an entity.
        :param entity: The entity object.
        :type entity: Object
        :return: List of Geometry column objects
        :rtype: List
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
            layer_lists = [geom_columns]

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

                layer_objects = QgsProject. \
                    instance().mapLayersByName(layer_name)

                if len(layer_objects) > 0:
                    for layer in layer_objects:
                        layer_id = layer.id()
                        QgsProject. \
                            instance().removeMapLayer(layer_id)
            # Change the crs of the canvas based on the new layer

            layer_list = QgsProject.instance(). \
                mapLayersByName(sel_lyr_name)
            if len(layer_list) > 0:
                self.set_canvas_crs(
                    layer_list[0]
                )

    def _set_layer_display_name(self, layer, name):
        try:
            layer.setName(name)
        except RuntimeError:
            pass

    def _layer_table_column(self, layer):
        # Returns the table and column name
        # that a layer belongs to.
        table, column = '', ''

        if hasattr(layer, 'dataProvider'):
            if layer.dataProvider().name() == 'postgres':
                layerConnStr = layer.dataProvider().dataSourceUri()
                dataSourceURI = QgsDataSourceUri(layerConnStr)
                table, column = dataSourceURI.table(), \
                                dataSourceURI.geometryColumn()

        return table, column

    def _map_registry_layer_names(self):
        """
        Returns a list of layers names.
        """
        layers = QgsProject.instance().mapLayers()
        layer_names = [lyr.name() for lyr in layers.values()]
        return layer_names

    def set_display_name_button_clicked(self):
        """
        Method to change display name
        """
        layer_names_ids = pg_layerNamesIDMapping().reverse
        layer = self.iface.activeLayer()

        if layer is not None:
            table_name = layer_names_ids.get(layer.id(), '')

            if table_name:
                # Check if the table name is in the current profile
                if table_name in self._profile_spatial_layers:
                    prompt = \
                        "Set the display name for '{0}' layer".format(
                            layer.name()
                        )
                    display_name, ok = QInputDialog.getText(
                        self,
                        'Spatial Unit '
                        'Manager', prompt
                    )

                    if ok and display_name:
                        # Get layer table and columns names
                        table, column = self._layer_table_column(layer)
                        if table and column:
                            idx, layer_info = \
                                self._layer_info_from_table_column(
                                    table,
                                    column
                                )
                            # Get item in the combo corresponding to the layer
                            if idx != -1:
                                self.stdm_layers_combo.setItemText(
                                    idx,
                                    display_name
                                )
                                layer.setName(display_name)

                                # Update configuration item
                                config_item = layer_info.get('item', None)
                                if config_item is not None:
                                    config_item.layer_display_name = \
                                        display_name

                                    # Update configuration
                                    save_configuration()

                else:
                    msg = QApplication.translate(
                        "Spatial Unit Manager",
                        "The layer does not "
                        "belong in the '{0}' "
                        "profile.\nThe display name "
                        "will not be set."
                        "".format(
                            self._curr_profile.name
                        )
                    )
                    QMessageBox.critical(
                        self.iface.mainWindow(),
                        'Spatial Unit Manager',
                        msg
                    )

    def active_layer_source(self):
        """
        Get the layer table name if the source is from the database.
        :return: The a Boolean True if a valid source is found or False if not.
        Alternatively, None if there is no active layer.
        :rtype: Boolean or NoneType
        """
        active_layer = self.iface.activeLayer()
        return self.layer_source(active_layer)

    def layer_source(self, layer):
        """
        Gets the layer source.
        :param layer: The layer
        :type layer: Any
        :return: Layer Source or None
        :rtype:
        """
        if layer is None:
            return None
        source = layer.source()
        if source is None:
            return False
        source_value = dict(re.findall('(\\S+)="?(.*?)"? ', source))
        try:
            table = source_value['table'].split('.')

            table_name = table[1].strip('"')
            if table_name in pg_views():
                return False

            entity = self._curr_profile.entity_by_name(table_name)
            if entity is None:
                return False
            else:
                self.active_entity = entity
                self.active_table = table_name
                # get all spatial columns of the entity.
                spatial_columns = [
                    c.name
                    for c in entity.columns.values()
                    if c.TYPE_INFO == 'GEOMETRY'
                ]
                # get all fields excluding the geometry.
                layer_fields = [
                    field.name()
                    for field in layer.fields()
                ]
                # get the currently being used geometry column
                active_sp_cols = [
                    col
                    for col in spatial_columns
                    if col not in layer_fields
                ]

                if len(active_sp_cols) == 1:
                    self.active_sp_col = active_sp_cols[0]

                return True

        except KeyError:
            return False

    def import_gpx_file(self):
        """
        Method to load GPS dialog
        """
        source_status = self.active_layer_source()
        layer_map = QgsProject.instance().mapLayers()
        error_title = QApplication.translate(
            'SpatialUnitManagerDockWidget',
            'GPS Feature Import Loading Error'
        )
        if len(layer_map) > 0:
            if source_status is None:
                QMessageBox.critical(
                    self,
                    error_title,
                    QApplication.translate(
                        'SpatialUnitManagerDockWidget',
                        'You have not selected a layer.\n '
                        'Please select a valid layer to import GPS features.'
                    )
                )
            elif source_status is False:
                QMessageBox.critical(
                    self,
                    error_title,
                    QApplication.translate(
                        'SpatialUnitManagerDockWidget',
                        'You have selected a non-STDM entity layer.\n '
                        'Please select a valid layer to import GPS features.'
                    )
                )
            elif source_status is True:
                self.gps_tool_dialog = GPSToolDialog(
                    self.iface,
                    self.active_entity,
                    self.active_table,
                    self.active_sp_col
                )
                self.gps_tool_dialog.show()
        else:
            QMessageBox.critical(
                self,
                error_title,
                QApplication.translate(
                    'SpatialUnitManagerDockWidget',
                    'You must add an entity layer from Spatial Unit Manager\n'
                    'and select it to import GPS Features.'
                )
            )

    def _valid_entity(self):
        """
        Checks if the current active layer in the layer panel
        represents a valid entity in the current profile
        :return: Error object
        :rtype: Object
        """
        entity_profile = current_profile()
        entity_obj = entity_profile.entity_by_name(self.curr_lyr_table)
        if entity_obj is None:
            return None
        return entity_obj

    def closeEvent(self, event):
        """
        On close of the dock window, this event is executed
        to run close_dock method
        :param event: The close event
        :type QCloseEvent
        :return: None
        """
        if self._plugin is None:
            return True

        self._plugin.spatialLayerManager.setChecked(False)
