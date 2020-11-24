"""
/***************************************************************************
Name                 : GPS Feature Import Data View Utility Module
Description          : Utility module that handles GPX file loading and
                        visualization.
                       in the Qtablewidget and QGIS map canvas
Date                 : 17/January/2017
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

from decimal import Decimal, DecimalException
from functools import partial

from qgis.PyQt.QtCore import (
    Qt,
    pyqtSignal
)
from qgis.PyQt.QtGui import (
    QColor
)
from qgis.PyQt.QtWidgets import (
    QAbstractItemView
)
from qgis.core import (
    edit,
    QgsGeometry,
    QgsProject,
    QgsPoint,
    QgsVectorLayer,
    QgsFeature,
    QgsRectangle,
    QgsPointXY
)
from qgis.gui import (
    QgsVertexMarker
)

VERTEX_COLOR = '#008000'


def enable_drag_drop(qt_widget, drag_enter_callback, item_drop_callback):
    """
    Enables internal drag and drop sorting in model/view widgets.
    :param qt_widget: QT widget for which drag and drop sort is enabled
    :return: None
    :rtype: None
    """
    qt_widget.setDragEnabled(True)
    qt_widget.setAcceptDrops(True)
    qt_widget.viewport().setAcceptDrops(True)
    qt_widget.setDragDropOverwriteMode(False)
    qt_widget.setDropIndicatorShown(True)
    qt_widget.setSelectionMode(QAbstractItemView.SingleSelection)
    qt_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
    qt_widget.setDragDropMode(QAbstractItemView.InternalMove)
    qt_widget.__class__.dropEvent = partial(_drop_event, callback=item_drop_callback)
    qt_widget.__class__.dragEnterEvent = partial(_drag_enter_event, callback=drag_enter_callback)


def _drop_event(qt_widget, event, callback):
    """
    A drop event function that prevents overwriting of destination
    rows if a row or cell is a destination target.
    :param qt_widget: QT widget for which drag and drop sort is enabled
    :param event: The drop event
    :return: None
    :rtype: None
    """
    if qt_widget is not None and (event.source() == qt_widget):
        rows = set([mi.row() for mi in qt_widget.selectedIndexes()])
        target_row = qt_widget.indexAt(event.pos()).row()
        rows.discard(target_row)
        rows = sorted(rows)
        if not rows:
            return
        if target_row == -1:
            target_row = qt_widget.rowCount()
        for _ in range(len(rows)):
            qt_widget.insertRow(target_row)
        row_mapping = dict()  # Src row to target row.
        for idx, row in enumerate(rows):
            if row < target_row:
                row_mapping[row] = target_row + idx
            else:
                row_mapping[row + len(rows)] = target_row + idx
        col_count = qt_widget.columnCount()
        for srcRow, tgtRow in sorted(row_mapping.items()):
            for col in range(0, col_count):
                qt_widget.setItem(tgtRow, col, qt_widget.takeItem(srcRow, col))
        callback()
        event.accept()
        return
    event.ignore()


def _drag_enter_event(qt_widget, event, callback):
    """
    Drag and drop start event set item drag signal
    :param qt_widget: QT widget for which drag and drop sort is enabled
    :param event: The drop event
    :return: None
    :rtype: None
    """
    if qt_widget is not None:
        callback()
        event.accept()
        return
    event.ignore()


def get_feature_attributes(gpx_layer):
    """
    Yields feature attributes and row number
    :param gpx_layer: GPX layer object
    :return row: Feature count
    :return list: List of feature data i.e. point name, latitude and longitude
    :rtype row: Integer
    :rtype list: List object
    """
    for row, feature_geom in enumerate(gpx_layer):
        lon, lat, ele = feature_geom.GetGeometryRef().GetPoint()
        point_name = feature_geom.GetFieldAsString(4)
        yield [point_name, lon, lat], row


def set_feature_vertex_marker(map_canvas, lon, lat, color=VERTEX_COLOR):
    """
    Sets single feature vertex
    :param map_canvas: Map canvas object
    :param lat: Vertex latitude value
    :param lon: Vertex longitude value
    :param color: Vertex color
    :return marker: Vertex object
    :rtype marker: Object
    """
    marker = QgsVertexMarker(map_canvas)
    marker.setCenter(QgsPointXY(lon, lat))
    marker.setColor(QColor(color))
    marker.setIconType(QgsVertexMarker.ICON_CIRCLE)
    marker.setPenWidth(4)
    return marker


def set_feature_vertices_marker(map_canvas, point_attr, color=None):
    """
    :param map_canvas: Map canvas object
    :param point_attr: GPS data attributes
    :param color: Vertex color
    :return point_attr: List of dictionary with GPS data attributes
    :rtype point_attr: List object with dictionary object
    """
    for point in point_attr:
        if point['qgs_point'] and (point['check_state'] == 2):
            lon = point['qgs_point'].x()
            lat = point['qgs_point'].y()
            if color:
                point['marker'] = set_feature_vertex_marker(
                    map_canvas, lon, lat, color
                )
            else:
                point['marker'] = set_feature_vertex_marker(
                    map_canvas, lon, lat
                )
    return point_attr


def create_feature(active_layer, geom_type, point_list, temp_layer_name):
    """
    Creates a vector feature based on the geometry
    :param active_layer: Current active layer
    :param geom_type: Feature geometry type
    :param point_list: Point objects to be created
    :param temp_layer_name: Temporary layer name
    :return temp_mem_layer: Temporary memory layer
    :rtype: Layer object
    """
    temp_mem_layer, data_provider = _create_temp_vector_layer(
        active_layer, geom_type, temp_layer_name
    )
    new_geometry = create_geometry(geom_type, point_list)
    add_feature(data_provider, new_geometry)
    return temp_mem_layer


def create_geometry(geom_type, point_list):
    """
    Creates a new geometry from a point list object
    :param geom_type: Feature geometry type
    :param point_list: Point objects to be created
    :return: Geometry
    :rtype: Geometry object
    """
    new_geometry = None
    if geom_type == 'Point':
        for point in point_list:
            new_geometry = QgsGeometry.fromPointXY(point)

    elif geom_type == 'LineString':
        new_geometry = QgsGeometry.fromPolylineXY(point_list)
    else:
        new_geometry = QgsGeometry.fromPolygonXY([point_list])

    return new_geometry


def _create_temp_vector_layer(active_layer, geom_type, temp_layer_name):
    """
    Creates a temporary vector layer in memory
    :param active_layer: Current active layer
    :param geom_type: Current active layer geometry type
    :param temp_layer_name: Temporary layer name
    :return temp_mem_layer: Temporary vector layer in memory
    :return data_provider: Layer data provider
    :rtype temp_mem_layer: Layer object
    :rtype data_provider: Data provider object
    """
    active_layer_crs = str(active_layer.crs().authid())
    uri = '{0}?crs={1}&field=id:integer&index=yes'.format(geom_type, active_layer_crs)
    temp_mem_layer = QgsVectorLayer(uri, temp_layer_name, 'memory')
    data_provider = temp_mem_layer.dataProvider()
    temp_mem_layer.startEditing()
    return temp_mem_layer, data_provider,


def add_feature(data_provider, geom_container):
    """
    Adds a vector feature based on the geometry and point object
    :param data_provider:
    :param geom_container:
    :return: None
    :rtype: None
    """
    new_feature = QgsFeature()
    new_feature.setGeometry(geom_container)
    data_provider.addFeatures([new_feature])


def add_map_layer(temp_mem_layer):
    """
    Adds temporary memory layer to map
    :param temp_mem_layer: Temporary vector layer in memory
    :return: None
    :rtype: None
    """
    commit_feature_edits(temp_mem_layer)
    QgsProject.instance().addMapLayer(temp_mem_layer)


def commit_feature_edits(temp_mem_layer):
    """
    Commits features edits and updates extends
    :param temp_mem_layer: Input layer
    :return: None
    :rtype: None
    """
    temp_mem_layer.commitChanges()
    temp_mem_layer.updateExtents()


def set_layer_extent(map_canvas, gpx_layer):
    """
    Sets the layer extent and zooms in to 1:1 scale
    :param gpx_layer: GPX layer object
    :param map_canvas: Map canvas object
    :return: None
    :rtype: None
    """
    x_min, x_max, y_min, y_max = gpx_layer.GetExtent()
    extent = QgsRectangle(x_min, y_min, x_max, y_max)
    extent.scale(1.1)
    map_canvas.setExtent(extent)
    map_canvas.refresh()


def check_uncheck_item(
        point_row_attr,
        map_canvas,
        item=None,
        check_transform=None,
        color=VERTEX_COLOR
):
    """
    Checks or unchecks item and sets vertex color on the layer feature
    :param point_row_attr: Point attribute
    :param map_canvas: QGIS map canvas
    :param item: Clicked item or checkbox widget
    :param check_transform: Flag indicating expected checkbox state change
    :param color: Color to be set for vertex
    :return checkbox_flag: A flag to indicate a checkbox click
    :rtype checkbox_flag: Boolean
    :return qgs_point: A list of spatial points
    :rtype qgs_point: List object
    """
    qgs_points = []
    for row, point_attr in enumerate(point_row_attr):
        if item:
            # On individual checkbox click
            if row == item.row() and item.column() == 0:
                _change_item_vertex_state(point_attr, color)
                qgs_points.append(point_attr['qgs_point'])
        else:
            # On select all or clear all button click
            if point_attr['checkbox'].checkState() == Qt.Unchecked and check_transform == 'check':
                _change_item_vertex_state(point_attr, color, Qt.Checked)
                qgs_points.append(point_attr['qgs_point'])
            elif point_attr['checkbox'].checkState() == Qt.Checked and check_transform == 'uncheck':
                _change_item_vertex_state(point_attr, color, Qt.Unchecked)
                qgs_points.append(point_attr['qgs_point'])
    map_canvas.refresh()
    return qgs_points


def row_selection_change(
        map_canvas, point_row_attr, selected_rows, color=VERTEX_COLOR
):
    """
    Set vertex color on row selection change
    :param map_canvas: QGIS map canvas
    :param point_row_attr: Point attribute
    :param selected_rows: Table widget selected rows
    :param color: Color to be set for vertex
    :return: None
    :rtype: None
    """
    if selected_rows:
        for selected_row in selected_rows:
            for row, point_attr in enumerate(point_row_attr):
                if row == selected_row:
                    _change_item_vertex_state(point_attr, color)
        map_canvas.refresh()


def _change_item_vertex_state(attr, color, check_state=None):
    """
    Change item checkbox state and vertex color
    :param attr: Dictionary identifier or key
    :param color: Hexadecimal color code
    :param check_state: State for checking and unchecking a combobox
    :return: None
    :rtype: None
    """
    if check_state == 0 or check_state == 2:
        attr['checkbox'].setCheckState(check_state)
    if attr['marker']:
        attr['marker'].setColor(QColor(color))


def remove_from_list(item_list, item):
    """
    Removes an element from a list
    :param item_list: Element/item list
    :param item: List element
    :return: Element list
    :rtype: List object
    """

    if item in set(item_list):
        item_list = [point for point in item_list if point != item]
        return item_list

    return []


def add_to_list(item_list, item):
    """
    Adds an element to a list
    :param item_list: Element/item list
    :param item: List element
    :return: Element
    :rtype: List element
    :rtype: Object type
    """
    if item:
        if item not in set(item_list):
            return item


def remove_vertex(map_canvas, point_row_attr):
    """
    Removes vertex from the map scene
    :param map_canvas: QGIS map canvas object
    :param point_row_attr: Point attribute list
    :return: None
    :rtype: None
    """
    for row, point_attr in enumerate(point_row_attr):
        if point_attr['marker'].scene():
            map_canvas.scene().removeItem(point_attr['marker'])
    map_canvas.refresh()


def remove_map_layer(map_canvas, temp_mem_layer):
    """
    Removes a map layer from the canvas
    :param map_canvas: QGIS map canvas object
    :param temp_mem_layer: Temporary map layer
    :return: None
    :rtype: None
    """
    layer_id = temp_mem_layer.id()
    QgsProject.instance().removeMapLayer(layer_id)
    map_canvas.refresh()


def get_layer_by_name(layer_name):
    """
    Retrieve layer by name
    :param layer_name: Name of the layer
    :return layers: List of layers matching the layer name
    :rtype: List object
    """
    layer_list = QgsProject.instance().mapLayersByName(layer_name)
    return layer_list


def get_qgs_points(qt_widget, checkbox_col='', lon_col='Longitude', lat_col='Latitude', ):
    """
    Gets new coordinates on drag and drop event or on text edit
    :param qt_widget: QT widget - table widget
    :param checkbox_col: Checkbox column name
    :param lon_col: Longitude column name
    :param lat_col: Latitude column name
    :return point_list: List of coordinates
    :rtype point_list: List object
    :return new_point_row_attr: List of dictionary with points and
                                table row
    :rtype new_point_row_attr: List object with dictionary object
    """
    point_list = []
    new_point_row_attr = []
    checkbox_state = lon_value = lat_value = None
    row_count = qt_widget.rowCount()
    column_count = qt_widget.columnCount()
    row = 0
    for row_index in range(row_count):
        for column_index in range(column_count):
            column_name = qt_widget.horizontalHeaderItem(column_index).text()
            cell_item = qt_widget.item(row_index, column_index)
            if cell_item:
                if str(column_name) == checkbox_col:
                    checkbox_state = cell_item.checkState()
                elif str(column_name) == lon_col:
                    lon_value = cell_item.text().strip()
                elif str(column_name) == lat_col:
                    lat_value = cell_item.text().strip()
        lon_value = _valid_number(lon_value)
        lat_value = _valid_number(lat_value)
        if lon_value and lat_value:
            point = QgsPointXY(lon_value, lat_value)
            new_point_row_attr.append({'row': row, 'qgs_point': point, 'check_state': checkbox_state})
            if checkbox_state == 2:
                point_list.append(point)
        else:
            if checkbox_state is not None:
                new_point_row_attr.append({'row': row, 'qgs_point': None, 'check_state': checkbox_state})
        if checkbox_state is not None:
            row += 1
        checkbox_state = lon_value = lat_value = None
    return point_list, new_point_row_attr


def _valid_number(value):
    """
    Validates if number is a decimal
    :param value: Input value
    :return: Decimal value if decimal else None
    :rtype: Decimal or None
    """
    try:
        if value:
            return Decimal(value)
    except (ValueError, DecimalException):
        return None


def update_point_row_attr(map_canvas, point_row_attr, new_point_row_attr):
    """
    Update QPS point and vertex marker objects based on
    end of drag and drop or text edit event
    :param map_canvas: QGIS map canvas object
    :param point_row_attr: Initial GPS data attributes
    :param new_point_row_attr: New GPS data attributes based on
                               edits in the table widget
    :return point_row_attr: List of dictionary with GPS data attributes
    :rtype point_row_attr: List object with dictionary object
    """
    vertex_markers = []
    for i, dict_one in enumerate(point_row_attr):
        dict_two = new_point_row_attr[i]
        if dict_one['row'] == dict_two['row']:
            if dict_one['qgs_point'] != dict_two['qgs_point']:
                old_marker = dict_one['marker']
                dict_one['qgs_point'] = dict_two['qgs_point']
                if dict_one['qgs_point']:
                    lon = dict_one['qgs_point'].x()
                    lat = dict_one['qgs_point'].y()
                    dict_one['marker'] = set_feature_vertex_marker(map_canvas, lon, lat)
                    vertex_markers.append({'marker': dict_one['marker']})
                    vertex_markers.append({'marker': old_marker})
                else:
                    dict_one['marker'] = None
            if dict_one['check_state'] != dict_two['check_state']:
                dict_one['check_state'] = dict_two['check_state']
                vertex_markers.append({'marker': dict_one['marker']})
    remove_vertex(map_canvas, vertex_markers)
    map_canvas.refresh()
    return point_row_attr


def delete_feature(map_canvas, temp_mem_layer):
    """
    Deletes feature from a layer
    :param map_canvas: QGIS map canvas object
    :param temp_mem_layer: Input layer
    :return: None
    :rtype: None
    """
    with edit(temp_mem_layer):
        feature_ids = [feature.id() for feature in temp_mem_layer.getFeatures()]
        temp_mem_layer.deleteFeatures(feature_ids)
    map_canvas.refresh()
