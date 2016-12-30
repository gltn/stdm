import PyQt4.QtCore as qc
import PyQt4.QtGui as qg
import qgis.core as q_core
import qgis.gui as q_gui


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
        lat, lon, ele = feature_geom.GetGeometryRef().GetPoint()
        point_name = feature_geom.GetFieldAsString(4)
        yield [point_name, lat, lon], row


def set_feature_vertex_marker(map_canvas, lat, lon, color='#008000'):
    """
    Sets features vertices
    :param map_canvas: Map canvas object
    :param lat: Vertex latitude value
    :param lon: Vertex longitude value
    :param color: Vertex color
    :return marker: Vertex objcet
    :rtype marker: Object
    """
    marker = q_gui.QgsVertexMarker(map_canvas)
    marker.setCenter(q_core.QgsPoint(lat, lon))
    marker.setColor(qg.QColor(color))
    marker.setIconType(q_gui.QgsVertexMarker.ICON_CIRCLE)
    marker.setPenWidth(4)
    return marker


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
    temp_mem_layer, data_provider = _create_temp_vector_layer(active_layer, geom_type, temp_layer_name)
    new_geometry = create_geometry(geom_type, point_list)
    _add_feature(data_provider, new_geometry)
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
            new_geometry = q_core.QgsGeometry.fromPoint(point)
    elif geom_type == 'LineString':
        new_geometry = q_core.QgsGeometry.fromPolyline(point_list)
    else:
        new_geometry = q_core.QgsGeometry.fromPolygon([point_list])
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
    temp_mem_layer = q_core.QgsVectorLayer(uri, temp_layer_name, 'memory')
    data_provider = temp_mem_layer.dataProvider()
    temp_mem_layer.startEditing()
    return temp_mem_layer, data_provider,


def _add_feature(data_provider, geom_container):
    """
    Adds a vector feature based on the geometry and point object
    :param data_provider:
    :param geom_container:
    :return: None
    :rtype: None
    """
    new_feature = q_core.QgsFeature()
    new_feature.setGeometry(geom_container)
    data_provider.addFeatures([new_feature])


def add_map_layer(temp_mem_layer):
    """
    Adds temporary memory layer to map
    :param temp_mem_layer: Temporary vector layer in memory
    :return: None
    :rtype: None
    """
    temp_mem_layer.commitChanges()
    temp_mem_layer.updateExtents()
    q_core.QgsMapLayerRegistry.instance().addMapLayer(temp_mem_layer)


def set_layer_extent(map_canvas, gpx_layer):
    """
    Sets the layer extent and zooms in to 1:1 scale
    :param gpx_layer: GPX layer object
    :param map_canvas: Map canvas object
    :return: None
    :rtype: None
    """
    x_min, x_max, y_min, y_max = gpx_layer.GetExtent()
    extent = q_core.QgsRectangle(x_min, y_min, x_max, y_max)
    extent.scale(1.1)
    map_canvas.setExtent(extent)
    map_canvas.refresh()


def select_unselect_item(point_row_attr, map_canvas, item=None, color='#008000'):
    """
    Select or unselects item and sets vertex color on the layer feature
    :param item: Clicked item or checkbox widget
    :param point_row_attr: Point attribute
    :param map_canvas: QGIS map canvas
    :param color: Color to be set for vertex
    :return: None
    :rtype: None
    """
    checkbox_flag = None
    qgs_point = None
    for row, point_attr in enumerate(point_row_attr):
        for attr in point_attr:
            if item:
                # On individual checkbox click
                if row == item.row() and item.column() == 0:
                    _change_item_vertex_state(attr, color)
                    qgs_point = attr['qgs_point']
                    checkbox_flag = True
            else:
                # On select all or clear all button click
                if attr['checkbox'].checkState() == qc.Qt.Unchecked and color == '#008000':
                    _change_item_vertex_state(attr, color, qc.Qt.Checked)
                    qgs_point = attr['qgs_point']
                elif attr['checkbox'].checkState() == qc.Qt.Checked and color == '#FF0000':
                    _change_item_vertex_state(attr, color, qc.Qt.Unchecked)
                    qgs_point = attr['qgs_point']
    map_canvas.refresh()
    return checkbox_flag, qgs_point


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
    attr['marker'].setColor(qg.QColor(color))


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


def add_to_list(item_list, item):
    """
    Adds an element to a list
    :param item_list: Element/item list
    :param item: List element
    :return: Element
    :rtype: List element
    :rtype: Object type
    """
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
        for attr in point_attr:
            map_canvas.scene().removeItem(attr['marker'])
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
    q_core.QgsMapLayerRegistry.instance().removeMapLayer(layer_id)
    map_canvas.refresh()


def get_layer_by_name(layer_name):
    """
    Retrieve layer by name
    :param layer_name: Name of the layer
    :return layers: List of layers matching the layer name
    :rtype: List object
    """
    layer_list = q_core.QgsMapLayerRegistry.instance().mapLayersByName(layer_name)
    return layer_list



