
from __future__ import division
import json
import math
from collections import OrderedDict

from PyQt4.QtCore import QVariant
from PyQt4.QtGui import QColor, QApplication
from decimal import Decimal, getcontext, Context, ROUND_DOWN, ROUND_UP, \
    setcontext

from PyQt4.QtCore import QSizeF
from PyQt4.QtGui import QColor, QTextDocument

from qgis.gui import QgsTextAnnotationItem


from qgis.gui import QgsHighlight
from qgis.core import QgsPoint, QgsGeometry, QgsVectorLayer, QgsFeature, \
    QgsMapLayerRegistry, QgsLineStringV2, QgsPointV2, edit, QgsDistanceArea, \
    QgsCoordinateReferenceSystem, QgsField, QgsPalLayerSettings, \
    QgsRenderContext, QGis, QgsFeatureRequest, QgsFillSymbolV2, \
    QgsSingleSymbolRendererV2, QgsSymbolV2, QgsSymbolLayerV2Registry
from qgis.utils import iface
from stdm.settings.registryconfig import (
    selection_color
)


def calculate_area(polygon_features):
    areas = []
    for feature in polygon_features:
        area = feature.geometry().area()
        areas.append(area)

    total_area = sum(areas)
    return total_area


def calculate_parallel_line(line_geom, distance):
    return line_geom.offsetCurve(distance)


def calculate_line_length(line_geom):
    return line_geom.legth()


def get_line_point(line_geom, distance):
    return line_geom.interpolate(distance)


def merge_polygons(polygons_list):
    inc = 1
    merged = None
    if len(polygons_list) < 2:
        return
    for i, polygon in enumerate(polygons_list):
        if i == 0:
            merged = polygons_list[i].combine(polygons_list[i + 1])
        elif i + inc + 1 < len(polygons_list):
            merged = merged.combine(polygons_list[i + inc + 1])
            inc = inc + 1

    return merged


def create_temporary_layer(source_layer, type, name, show_legend=True, style=True):
    #TODO fix crash when used with feature details
    # create a new memory layer
    crs = source_layer.crs()
    crs_id = crs.srsid()
    wkt = crs.toWkt()
    vl_geom_config = u"{0}?crs={1}&field=name:string(20)&" \
                     u"index=yes".format(type, wkt)

    v_layer = QgsVectorLayer(vl_geom_config, name, "memory")

    target_crs = QgsCoordinateReferenceSystem(
        crs_id, QgsCoordinateReferenceSystem.InternalCrsId
    )

    v_layer.setCrs(target_crs)

    iface.mapCanvas().mapSettings().setDestinationCrs(target_crs)

    iface.mapCanvas().refresh()
    if style:
        if type == 'LineString':
            registry = QgsSymbolLayerV2Registry.instance()
            lineMeta = registry.symbolLayerMetadata("SimpleLine")
            markerMeta = registry.symbolLayerMetadata("MarkerLine")

            symbol = QgsSymbolV2.defaultSymbol(v_layer.geometryType())

            # Line layer
            lineLayer = lineMeta.createSymbolLayer(
                {'width': '0.26', 'color': '0,102,255', 'offset': '0',
                 'penstyle': 'solid', 'use_custom_dash': '0',
                 'joinstyle': 'bevel', 'capstyle': 'square'})

            # Marker layer
            markerLayer = markerMeta.createSymbolLayer(
                {'width': '0.26', 'color': '0,102,255', 'interval': '1',
                 'rotate': '1', 'placement': 'interval', 'offset': '0'})
            subSymbol = markerLayer.subSymbol()
            # Replace the default layer with our own SimpleMarker
            subSymbol.deleteSymbolLayer(0)
            triangle = registry.symbolLayerMetadata(
                "SimpleMarker").createSymbolLayer(
                {'name': 'square', 'color': '0,102,255',
                 'color_border': '0,0,0', 'offset': '0,0', 'size': '1.5',
                 'angle': '0'})
            subSymbol.appendSymbolLayer(triangle)

            # Replace the default layer with our two custom layers
            symbol.deleteSymbolLayer(0)
            symbol.appendSymbolLayer(lineLayer)
            symbol.appendSymbolLayer(markerLayer)

            # Replace the renderer of the current layer
            renderer = QgsSingleSymbolRendererV2(symbol)
            v_layer.setRendererV2(renderer)

            symbols = v_layer.rendererV2().symbols2(QgsRenderContext())
            symbol = symbols[0]
            symbol.setWidth(2)

        if type == 'Point':
            symbols = v_layer.rendererV2().symbols2(QgsRenderContext())
            symbol = symbols[0]
            symbol.setSize(2.5)
            color = QColor(7, 200, 139)
            symbol.setColor(color)
        if type == 'Polygon':
            symbols = v_layer.rendererV2().symbols2(QgsRenderContext())
            symbol = symbols[0]
            # symbol.setSize(2.5)
            color = QColor(198, 143, 67)
            symbol.setColor(color)
    # show the line
    QgsMapLayerRegistry.instance().addMapLayer(
        v_layer, show_legend
    )

    v_layer.updateExtents()

    return v_layer


def rotate_line(point_geom, polygon_layer, line, angle):
    if isinstance(line, QgsGeometry):
        line_geom = line
    else:
        line_geom = QgsGeometry.fromWkt(line.asWkt())
    result = line_geom.rotate(angle, point_geom)
    geom = None
    extended_geom = None
    sel_feats = polygon_layer.selectedFeatures()
    if len(sel_feats) > 0:
        geom = sel_feats[0].geometry()
    else:
        for feature in polygon_layer.getFeatures():
            geom = feature.geometry()
            break
    if geom is not None:

        added_points = extend_line_points(line_geom, geom.boundingBox())
        extended_geom = QgsGeometry.fromPolyline(added_points)
        # add_geom_to_layer(layer, extended_geom)
    return extended_geom


def rotate_line_clockwise(point_geom, polygon_layer, line_geom, angle):
    if angle < 0:
        angle = angle * -1
    return rotate_line(point_geom, polygon_layer, line_geom, angle)


def rotate_line_anti_clockwise(point_geom, polygon_layer, line, angle):
    if angle > 0:
        angle = angle * -1
    return rotate_line(point_geom, polygon_layer, line, angle)

def get_point_by_distance(point_layer, line_geom, distance):
    point = line_geom.interpolate(distance)
    feature = add_geom_to_layer(point_layer, point)
    return feature

def get_parallel_line(selected_line_geom, offset_distance):
    parallel_geom = selected_line_geom.offsetCurve(offset_distance, 1, 2, 0)
    if parallel_geom is None:
        return None

    return parallel_geom

def line_slope(line_geom):
    points = line_geom.asPolyline()
    line = create_V2_line(points)
    start_point = line.startPoint()
    end_point = line.endPoint()
    start_y = start_point.y()
    start_x = start_point.x()
    end_y = end_point.y()
    end_x = end_point.x()

    end_point = line.endPoint()
    denominator = end_point.x() - start_x
    numerator = end_point.y() - start_y
    if numerator == 0:
        slope = 0
    elif denominator == 0:
        slope = None
    else:
        slope = (end_point.y() - start_y) / (end_point.x() - start_x)
    return line, slope, start_x, start_y, end_x, end_y


def create_V2_line(points):
    line = QgsLineStringV2()
    for point in points:
        point_v2 = QgsPointV2(point.x(), point.y())
        line.addVertex(point_v2)
    return line
#
# def extend_line_points(line_geom, polygon_extent):
#     """
#
#     :param line_geom:
#     :type line_geom: QgsGeometry
#     :param x_step:
#     :type x_step: Integer
#     :param increase: To double or increase the x coordinate, increase should be
#     greater than x_step. If increase = 1, x will be halved or reduced.
#     :type increase: Integer
#     :return:
#     :rtype: Polyline
#     """
#     # x_max = polygon_extent.xMaximum()
#     # x_min = polygon_extent.xMinimum()
#     # #TODO take this method outside this function and put all output as inputs
#     # line, slope, start_x, start_y, end_x, end_y = line_slope(line_geom)
#     #
#     # # x1 = x_max
#     # # x = x_min
#     #
#     # # y1 = start_y + slope * (x_max - start_x)
#     # y1 = start_y + slope * (start_x - x_min)
#     # y = end_y = slope * (end_x - x_max)
#     #
#     # p4 = QgsPoint(x_max, y)
#     # p3 = QgsPoint(end_x, end_y)
#     # p2 = QgsPoint(start_x, start_y)
#     # p1 = QgsPoint(x_min, y1)
#     #
#     # poly_line = [p1, p2, p3, p4]
#     # print poly_line
#     # return poly_line
#
#     x_max = polygon_extent.xMaximum()
#     x_min = polygon_extent.xMinimum()
#     # TODO fix extending vertical line.
#     line, slope, start_x, start_y, end_x, end_y = line_slope(line_geom)
#     if slope is None:
#         y_max = polygon_extent.yMaximum()
#         y_min = polygon_extent.yMinimum()
#         ext_end_y = y_max
#         ent_start_y = y_min
#     else:
#         ext_end_y = end_y + slope * (x_max - end_x)
#         ent_start_y = start_y + slope * (x_min - start_x)
#
#     p1 = QgsPoint(x_min, ent_start_y)
#     p2 = QgsPoint(start_x, start_y)
#     p3 = QgsPoint(x_max, ext_end_y)
#     poly_line = [p1, p2, p3]
#     return poly_line
#


def extend_line_points(line_geom, polygon_extent):
    """

    :param line_geom:
    :type line_geom: QgsGeometry
    :param x_step:
    :type x_step: Integer
    :param increase: To double or increase the x coordinate, increase should be
    greater than x_step. If increase = 1, x will be halved or reduced.
    :type increase: Integer
    :return:
    :rtype: Polyline
    """
    x_max = polygon_extent.xMaximum()
    x_min = polygon_extent.xMinimum()
    # TODO fix extending vertical line.
    line, slope, start_x, start_y, end_x, end_y = line_slope(line_geom)
    if slope is None:
        y_box1 = polygon_extent.yMaximum()
        y_box2 = polygon_extent.yMinimum()

    else:
        y_box1 = end_y - slope * (end_x - x_max)
        y_box2 = start_y - slope * (start_x - x_min)

    p1 = QgsPoint(x_min, y_box2)
    p2 = QgsPoint(start_x, start_y)
    p3 = QgsPoint(end_x, end_y)
    p4 = QgsPoint(x_max, y_box1)
    poly_line = [p1, p2, p3, p4]
    return poly_line


def add_geom_to_layer(layer, geom, main_geom=None, feature_ids=None):
    if isinstance(geom, QgsPoint):
        geom = QgsGeometry.fromPoint(geom)
    try:
        iface.setActiveLayer(layer)
    except Exception:
        pass
    preview_layer = False
    feature = None
    # refresh map canvas to see the result
    if feature_ids is not None:
        layer.startEditing()
        if len(feature_ids) > 0:
            features = feature_id_to_feature(layer, feature_ids)
            if len(features) > 0:
                if main_geom is not None:
                    features[0].setGeometry(main_geom)
                    layer.updateFeature(features[0])
                feature = add_geom_to_feature(layer, geom, features[0])
            else: # for preview polygon
                preview_layer = True
                features = list(layer.getFeatures())
                if main_geom is not None:
                    features[0].setGeometry(main_geom)

                    layer.updateFeature(features[0])

                feature = add_geom_to_feature(
                    layer, geom, features[0], preview_layer=True)
                layer.selectByIds([features[0].id()])
            layer.updateFeature(features[0])
        layer.updateExtents()
    else:
        try:
            with edit(layer):
                feature = add_geom_to_feature(layer, geom)
            layer.updateExtents()
        except Exception as ex:
            print ex


    # if preview_layer:
    #     layer.commitChanges()
    # print 'added feat', feature

    return feature

def  add_geom_to_feature(layer, geom, original_feature=None, preview_layer=False):
    ft = QgsFeature()
    attr = layer.fields().toList()

    if original_feature is None:
        ft.setAttributes(attr)
    else:

        ft.setAttributes(original_feature.attributes())

    if isinstance(geom, QgsGeometry):
        ft.setGeometry(geom)
    else:
        ft.setGeometry(geom.geometry())
    if preview_layer:
        layer.dataProvider().addFeatures([ft])
        layer.commitChanges()
    else:
        layer.addFeatures([ft])
    #     if original_feature is not None:
    #         from stdm.ui.forms.spatial_unit_form import (
    #             STDMFieldWidget
    #         )
    #
    #         # layer.addFeatures([original_feature])
    # # layer.selectByIds([ft.id()])
    return ft

def add_geom_to_layer_with_measurement(layer, geom, prefix, suffix, unit=''):
    with edit(layer):
        feature = QgsFeature()
        if isinstance(geom, QgsPoint):
            geom = QgsGeometry.fromPoint(geom)

        feature.setGeometry(geom)

        if geom.type() == 1:
            length = "%.2f" % round(geom.length(), 2)
            attr = '{} {}{}'.format(prefix, length, suffix)

            feature.setAttributes(['measurement', attr])

        if geom.type() == 2:

            if unit == 'Hectares':
                area = geom.area() / 10000
            else:
                area = geom.area()
            area = "%.2f" % round(area, 2)
            attr = '{} {}{}'.format(prefix, area, suffix)

            feature.setAttributes(['measurement', attr])

        # layer.updateFeature(feature)
        layer.dataProvider().addFeatures([feature])
        # layer.addFeature(feature)

    # layer.commitChanges()

    # layer.selectByIds([feature.id()])
    # zoom_refresh_to_geom(geom)
    return geom

def zoom_refresh_to_geom(geom):
    extent = geom.boundingBox()
    iface.mapCanvas().setExtent(extent)
    iface.mapCanvas().refresh()

def zoom_to_selected(layer):
    box = layer.boundingBoxOfSelected()
    box.scale(1.2)
    canvas = iface.mapCanvas()
    canvas.setExtent(box)
    # canvas.zoomScale(1.3)
    canvas.refresh()

def identify_selected_point_location(selected_point_ft, line_geom):
    """

    :param line_geom:
    :type line_geom: QgsGeometry
    :param point_geom:
    :type point_geom: QgsPoint
    :return:
    :rtype:
    """
    points = line_geom.asPolyline()
    point_geom = selected_point_ft.geometry()
    line = create_V2_line(points)
    start_point = line.startPoint()
    end_point = line.endPoint()
    # print point_geom.exportToGeoJSON(), start_point.asJSON()
    # print point_geom.exportToGeoJSON(), end_point.asJSON()
    if point_geom.exportToGeoJSON() == start_point.asJSON():
        return 'start'
    elif point_geom.exportToGeoJSON() == end_point.asJSON():
        return 'end'
    else:
        return 'middle'


def add_line_points_to_map(point_layer, line_geom, clear=True):

    if clear:
        clear_points(point_layer)
    poly_lines = line_geom.asPolyline()
    point_features = []

    for point in poly_lines:
        feature = add_geom_to_layer(point_layer, point)
        point_features.append(feature)
    return point_features

def clear_points(point_layer):
    features = point_layer.getFeatures()
    ids = [f.id() for f in features]
    with edit(point_layer):
        point_layer.deleteFeatures(ids)

def point_by_distance(point_layer, selected_point_ft, selected_line, distance):
    # print selected_point_ft, selected_line, distance
    location = identify_selected_point_location(selected_point_ft, selected_line)

    if location == 'start':
        added_point_feature = get_point_by_distance(
            point_layer, selected_line, distance
        )

    elif location == 'end':
        line_length = selected_line.length()
        distance_from_end = line_length - distance

        added_point_feature = get_point_by_distance(
            point_layer, selected_line, distance_from_end
        )
    else:
        added_point_feature = get_point_by_distance(
            point_layer, selected_line, distance
        )
    # print 'added feature ', added_point_feature
    return added_point_feature

def rotate_from_distance_point(
        polygon_layer, point_geom, line, angle, clockwise=True
):
    if clockwise:
        ext_line_geom = rotate_line_clockwise(
            point_geom.asPoint(), polygon_layer, line, angle
        )
    else:
        ext_line_geom = rotate_line_anti_clockwise(
            point_geom.asPoint(), polygon_layer, line, angle
        )
    return ext_line_geom


def highlight_geom(map, layer, geom):
    sel_highlight = QgsHighlight(map, geom, layer)

    sel_highlight.setFillColor(selection_color())
    sel_highlight.setWidth(2.5)
    sel_highlight.setColor(QColor(212, 95, 0, 255))
    sel_highlight.show()

def make_layer_transparent(layer):
    myRenderer = layer.rendererV2()
    if layer.geometryType() == QGis.Polygon:
        mySymbol1 = QgsFillSymbolV2.createSimple({'color': '255,0,0,0',
                                                  'color_border': '#000000',
                                                  'width_border': '0.6'})

        myRenderer.setSymbol(mySymbol1)
        layer.triggerRepaint()
        iface.legendInterface().refreshLayerSymbology(layer)

def show_polygon_area(layer, temp_layer_name=None, prefix='', suffix='', all_features=False, unit='Meters', style=False):
    if not all_features:
        sel_feats = layer.selectedFeatures()
    else:
        sel_feats = layer.getFeatures()

    type = layer_type(layer)
    if temp_layer_name is not None:
        curr_layers = QgsMapLayerRegistry.instance().mapLayersByName(temp_layer_name)
        if len(curr_layers) == 0:
            curr_layer = create_temporary_layer(
                layer, type, temp_layer_name, show_legend=True, style=style
            )

        else:
            curr_layer = curr_layers[0]
            clear_layer_features(curr_layer)
            iface.setActiveLayer(curr_layer)
    else:
        curr_layer = layer

    add_measurement_field(curr_layer)

    for feature in sel_feats:

        polygon_geom = feature.geometry()
        if polygon_geom is not None:
            add_geom_to_layer_with_measurement(
                curr_layer, polygon_geom, prefix, suffix, unit
            )

    label_layer_by_field(curr_layer, 'measurement')

def add_area(layer, area_layer_name, all_features=False):
    show_polygon_area(
        layer,
        area_layer_name,
        all_features=all_features,
        suffix='m{}'.format(chr(0x00B2))
    )
    if area_layer_name is not None:
        area_layers = QgsMapLayerRegistry.instance().mapLayersByName(
            area_layer_name
        )
        if len(area_layers) > 0:
            make_layer_transparent(area_layers[0])

def polygon_to_lines(
        layer, layer_name, measurement=True, prefix='', suffix='',
        all_features=False, style=True):

    if layer.name() == layer_name:
        return None
    line_geoms = []

    if not all_features:
        sel_feats = layer.selectedFeatures()
    else:
        sel_feats = layer.getFeatures()

    line_layers = QgsMapLayerRegistry.instance().mapLayersByName(layer_name)

    if len(line_layers) == 0:
        line_layer = create_temporary_layer(
            layer, 'LineString', layer_name, style=style
        )

    else:
        line_layer = line_layers[0]
        # print QgsMapLayerRegistry.mapLayer(line_layer.id())
        clear_layer_features(line_layer)
        iface.setActiveLayer(line_layer)

    type = layer_type(layer)
    if measurement:
        add_measurement_field(line_layer)

    for feature in sel_feats:

        polygon_geom = feature.geometry()

        if polygon_geom is None:
            return None
        if type == 'Polygon':
            list_of_lines = polygon_geom.asPolygon()
            for lines in list_of_lines:
                line_geom_list = add_line_features(
                    line_layer, lines, prefix, suffix, measurement)
                line_geoms.extend(line_geom_list)

        if type == 'MultiPolygon':
            list_of_lines_1 = polygon_geom.asMultiPolygon()
            for list_of_lines in list_of_lines_1:
                for lines in list_of_lines:
                    line_geom_list = add_line_features(
                        line_layer, lines, prefix, suffix, measurement)
                    line_geoms.extend(line_geom_list)

    if measurement:
        label_layer_by_field(line_layer, 'measurement')
    iface.setActiveLayer(line_layer)
    return line_layer

def add_area_text(geometry):
    point = geometry.centroid().asPoint()

    area = geometry.area()
    canvas = iface.mapCanvas()
    text_annotation_item = QgsTextAnnotationItem(canvas)

    text_annotation_item.setMapPosition(point)
    text_annotation_item.setFrameSize(QSizeF(20, 20))
    text_annotation_item.setFrameColor(QColor(0, 255, 0))
    text_annotation_item.setFrameBackgroundColor(QColor(128, 128, 128))
    text_document = QTextDocument()
    html_content = "<b>{}M<sup>2</sup></b>".format(area)
    font_color, font_family, font_size = "#123456", "Times New Roman", 16
    text_document.setHtml('<font style="color:' + font_color +
                          "; font-family:" + font_family + "; font-size: " +
                          str(font_size) + 'px">' + html_content + "</font>")
    text_annotation_item.setDocument(text_document)
    canvas.refresh()

def polygon_to_points(polygon_layer, line_layer, point_layer,
                      line_layer_name, with_measurement=True):
    for feature in line_layer.getFeatures():

        add_line_points_to_map(point_layer, feature.geometry(), clear=False)

def add_line_features(line_layer, lines, prefix, suffix, measurement):
    line_geom_list = []
    for i, line in enumerate(lines):
        if i != len(lines) - 1:
            line_list = [line, lines[i + 1]]
            line_geom = QgsGeometry.fromPolyline(line_list)
            line_geom_list.append(line_geom)
            if measurement:
                add_geom_to_layer_with_measurement(
                    line_layer, line_geom, prefix, suffix
                )


            else:
                add_geom_to_layer(line_layer, line_geom)

    return line_geom_list

def add_measurement_field(layer):
    with edit(layer):
        layer.addAttribute(QgsField('measurement', QVariant.String))
        layer.updateFields()

def label_layer_by_field(layer, field_name):
    layer.setCustomProperty("labeling", "pal")
    layer.setCustomProperty(
        "labeling/fieldName", field_name)
    if layer.wkbType() != QGis.WKBPolygon and layer.wkbType() != QGis.WKBMultiPolygon:
        layer.setCustomProperty(
            "labeling/placement", QgsPalLayerSettings.AboveLine
        )
        layer.setCustomProperty("labeling/placementFlags",
                                 QgsPalLayerSettings.AboveLine)
    else:
        layer.setCustomProperty(
            "labeling/placement", QgsPalLayerSettings.AroundPoint
        )
    layer.setCustomProperty("labeling/fontSize", "10")
    layer.setCustomProperty("labeling/bufferDraw", True)
    layer.setCustomProperty("labeling/enabled", True)
    layer.setCustomProperty("labeling/drawLabels", True)


def copy_layer_to_memory(layer, name, features=None, add_to_legend=True):

    geom_type = layer_type(layer)

    crs = layer.crs().toWkt()
    vl_geom_config = u"{0}?crs={1}&field=name:string(20)&" \
                     u"index=yes".format(geom_type, crs)

    mem_layer = QgsVectorLayer(vl_geom_config, name, "memory")


    mem_layer_data = mem_layer.dataProvider()

    attr = layer.dataProvider().fields().toList()
    mem_layer_data.addAttributes(attr)
    mem_layer.startEditing()
    mem_layer.updateFields()
    if features is None:
        feats = [feat for feat in layer.getFeatures()]
        mem_layer_data.addFeatures(feats)
    else:
        feat = feature_id_to_feature(layer, features)
        # for f_id in features:
        #
        #     request = QgsFeatureRequest()
        #     request.setFilterFid(f_id)
        #     feature_itr = layer.getFeatures(request)
        #     for feat in feature_itr:
        mem_layer_data.addFeatures(feat)

    mem_layer.commitChanges()
    QgsMapLayerRegistry.instance().addMapLayer(
        mem_layer, addToLegend=add_to_legend
    )

    return mem_layer


def layer_type(layer):
    geom_type = None
    if layer.wkbType() == QGis.WKBPoint:
        geom_type = 'Point'
    if layer.wkbType() == QGis.WKBLineString:
        geom_type = 'LineString'
    if layer.wkbType() == QGis.WKBPolygon:
        geom_type = 'Polygon'
    if layer.wkbType() == QGis.WKBMultiPolygon:
        geom_type = 'MultiPolygon'
    return geom_type


def clear_layer_features(layer):
    feat_ids = [feat.id() for feat in layer.getFeatures()]
    with edit(layer):
        layer.deleteFeatures(feat_ids)
    if len(list(layer.getFeatures())) > 0:
        layer.startEditing()
        layer.dataProvider().deleteFeatures(feat_ids)
        layer.commitChanges()


def add_features_to_layer(layer, features):
    provider = layer.dataProvider()
    layer.startEditing()
    for feat in features:
        provider.addFeatures([feat])
    layer.commitChanges()

def feature_id_to_feature(layer, feature_ids):
    features = []
    try:
        for f_id in feature_ids:
            request = QgsFeatureRequest()
            request.setFilterFid(f_id)
            feature_itr = layer.getFeatures(request)
            for feat in feature_itr:
                features.append(feat)
    except Exception:
        pass
    return features

def merge_selected_lines_features(line_layer):
    features = line_layer.selectedFeatures()
    geoms = QgsGeometry.fromWkt('GEOMETRYCOLLECTION()')
    for feature in features:
        geoms = geoms.combine(feature.geometry())

    return geoms


def points_to_line(point_layer):
    poly_line = []
    for point_ft in point_layer.selectedFeatures():
        point = QgsGeometry.asPoint(point_ft.geometry())

        poly_line.append(point)

    line_geom = QgsGeometry.fromPolyline(poly_line)

    return line_geom

def add_geom_to_layer_bsc(layer, geom):
    # parallel_geom = get_parallel_line(
    #     geom, 3
    # )

    with edit(layer):
        # line_layer.startEditing()
        ft = QgsFeature()
        attr = layer.fields().toList()
        ft.setAttributes(attr)

        ft.setGeometry(geom)
        layer.addFeature(ft)

    layer.updateExtents()

def split_move_line_with_area(
        polygon_layer, line_layer, preview_layer,
        selected_line_ft, area, feature_ids=None
):
    # if previous_properties is None:
    decimal_place_new = 0
    height = 1
    height_change = 1
    # else:
    #     decimal_place_new = previous_properties['decimal_place_new']
    #     height = previous_properties['height']
    #     height_change = previous_properties['height_change']
    split_area1 = 0

    loop_index = 0
    failed_split = 0
    distance = 0
    # print list(preview_layer.getFeatures())[0].geometry().area()
    # multi_split_case = 0vb
    # first_height = 0
    area_toggle = 0
    # Continuous loop until condition of split area and split polygon area is equal
    while split_area1 >= 0:
        # the height/ distance from selected line
        # Get the parallel line from the selected line using the calculated height
        # print selected_line_ft, selected_line_ft.geometry()
        # if move_height is not None:
        #     parallel_line_geom = get_parallel_line(
        #         selected_line_ft.geometry(), move_height
        #     )
        # else:
        # if previous_properties is not None:
        #     decimal_place_new = previous_properties['decimal_place_new']
        #     height = previous_properties['height']
        #     height_change = previous_properties['height_change']

        height = Decimal(height) + Decimal(height_change) / \
                                   Decimal(math.pow(10, decimal_place_new))
        # print height, decimal_place_new, height_change
        parallel_line_geom = get_parallel_line(
            selected_line_ft.geometry(), height*-1
        )
        # print parallel_line_geom, height, height_change, decimal_place_new
        # print height*-1
        QApplication.processEvents()
        # print loop_index, parallel_line_geom,  height
        # if parallel_line_geom is None:
        #     if previous_properties is not None:
        #         decimal_place_new = previous_properties['decimal_place_new']
        #         height = previous_properties['height']
        #         height_change = previous_properties['height_change']

            # height = Decimal(height*-1) + Decimal(height_change) / \
            #                            Decimal(math.pow(10, decimal_place_new))
            # print selected_line_ft.geometry(), selected_line_ft.geometry().length()
            # parallel_line_geom = get_parallel_line(
            #     selected_line_ft.geometry(), height*-1
            # )
            # if parallel_line_geom is None:
            #     continue
            # return False, False, False
        # Get one feature selected on preview layer.
        # The preview layer has 1 feature
        # that copies and merges all selected feature from polygon.
        try:
            sel_features = list(preview_layer.getFeatures())
        except Exception:
            return False, False
        # if previous_geom is None:
            # Get the geometry
        geom1 = sel_features[0].geometry()
        # print geom1.area()
        # else:
        #     geom1 = previous_geom

        # This is needed for equal area split when the height needs to be positive
        # if parallel_line_geom is None:
        #     parallel_line_geom = get_parallel_line(
        #         selected_line_ft.geometry(), height*height*-1
        #     )
        # elif parallel_line_geom.distance(geom1) > distance:
        #     parallel_line_geom = get_parallel_line(
        #         selected_line_ft.geometry(), height
        #     )
        # print 2, parallel_line_geom
        # if parallel_line_geom is None:
        #     continue

        extent = geom1.boundingBox()

        # Using the extent, extend the parallel line to the selected
        # geometry bounding box to avoid failed split.
        added_points = extend_line_points(parallel_line_geom, extent)

        parallel_line_geom2 =  QgsGeometry.fromPolyline(added_points)

        # print parallel_line_geom2
        # parallel_line_geom3 = QgsGeometry.as
        #
            # line_layer.commitChanges()
        # If the line intersects the main geometry, split it
        if parallel_line_geom2.intersects(geom1):
            (res, split_geom0, topolist) = geom1.splitGeometry(
                added_points, False
            )

            if len(split_geom0) > 0:

                if loop_index == 0:
                    # Get the first line that intersects the geometry and use
                    # it as a reference using distance to the split feature.
                    if isinstance(selected_line_ft, QgsFeature):
                        first_intersection = selected_line_ft.geometry()
                    else:
                        first_intersection = selected_line_ft

                    # height = area/selected_line_ft.geometry().length()

                if loop_index >= 1:
                    # The closest geometry to fist intersection is the split geom
                    if first_intersection.distance(geom1) < \
                            first_intersection.distance(split_geom0[0]):

                        split_area1 = geom1.area()
                        split_geom = geom1
                        main_geom = split_geom0[0]
                    elif first_intersection.distance(geom1) > \
                            first_intersection.distance(split_geom0[0]):
                        # If split geom is over 1, continue
                        # TODO find a better solution than continue.
                        if len(split_geom0) > 1:
                            # print 'continue 0'
                            continue

                        else:
                            split_area1 = split_geom0[0].area()
                            split_geom = split_geom0[0]
                            main_geom = geom1
                    else:
                        # print 'continue 1'
                        continue
                loop_index = loop_index + 1
            else:

                continue

            # If provided area is greater than split area, increase height
            if area > split_area1:
                if area - math.modf(split_area1)[1] > 200:
                    if area_toggle == 0:
                        decimal_place_new = 0

                elif area - math.modf(split_area1)[1] in range(50, 200):
                    if area_toggle == 0:
                        decimal_place_new = 1

                elif area - math.modf(split_area1)[1] in range(10, 50):
                    if area_toggle == 0:
                        decimal_place_new = 2

                elif area - math.modf(split_area1)[1] in range(3, 10):
                    if area_toggle == 0:
                        decimal_place_new = 4

                # helps in changing height in small steps after switching from area < split_area1
                if height_change == -1:
                    # print 'changed ', loop_index > 0 and area_toggle < 300

                    # for large polygons

                    if loop_index > 0:
                        decimal_place_new = decimal_place_new + area_toggle

                    if loop_index > 0 and area_toggle < 300:
                        area_toggle = area_toggle + 1

                height_change = 1

                # print '2 {} {}'.format(split_area1, area), height_change, height, decimal_place_new
                if math.modf(split_area1)[1] + 3 > area:
                    # Set decimal place to small steps if area_toggle is 0,
                    # otherwise, use the area toggle value.
                    if (round(split_area1, 2)) == area:
                        # print '2 {} {}'.format(split_area1, area)
                        # line_layer.startEditing()
                        parallel_line_ft = add_geom_to_feature(
                            line_layer, parallel_line_geom2
                        )
                        feature = add_geom_to_layer(
                            polygon_layer, split_geom, main_geom, feature_ids
                        )
                        # print feature.geometry().area(), 1
                        # polygon_layer.selectByIds([feature.id()])
                        # print main_geom.area(), split_geom.area()
                        # polygon_layer.selectByIds([original_selected.id()])
                        # print 'aa', parallel_line_geom
                        # copy_layer_to_memory(line_layer, 'split line', [parallel_line_ft.id()])
                        # properties = {'height': height,
                        #               'decimal_place_new': decimal_place_new,
                        #               'height_change': height_change}

                        return feature, parallel_line_ft


            # If provided area is smaller than split area, decrease height
            if area < split_area1:
                if math.modf(split_area1)[1] - area > 200:
                    if area_toggle == 0:
                        decimal_place_new = 0

                elif math.modf(split_area1)[1] - area in range(50, 200):
                    if area_toggle == 0:
                        decimal_place_new = 1

                elif math.modf(split_area1)[1] - area in range(10, 50):
                    if area_toggle == 0:
                        decimal_place_new = 2

                elif math.modf(split_area1)[1] - area in range(3, 10):
                    if area_toggle == 0:
                        decimal_place_new = 4

                # helps in changing height in small steps after switching from area > split_area1
                if height_change == 1:

                    if loop_index > 0:
                        decimal_place_new = decimal_place_new + area_toggle

                    if loop_index > 0 and area_toggle < 300:
                        area_toggle = area_toggle + 1

                height_change = -1

                # print '3 {} {}'.format(split_area1, area), height_change, height, decimal_place_new
                if math.modf(split_area1)[1] < area + 3:

                    if (round(split_area1, 2)) == area:
                        # add_geom_to_layer(line_layer, parallel_line_geom2)
                        # print '3 {} {}'.format(split_area1, area)
                        # line_layer.startEditing()
                        parallel_line_ft = add_geom_to_feature(
                            line_layer, parallel_line_geom2
                        )

                        feature = add_geom_to_layer(
                            polygon_layer, split_geom, main_geom, feature_ids
                        )
                        # copy_layer_to_memory(line_layer, 'split line',
                        #                      [parallel_line_ft.id()])
                        # print feature.geometry().area(), 2
                        # polygon_layer.selectByIds([feature.id()])
                        # print main_geom.area(), split_geom.area()
                        # print 'bb', parallel_line_geom
                        # polygon_layer.selectByIds([original_selected.id()])
                        # properties = {'height': height,
                        #               'decimal_place_new': decimal_place_new,
                        #               'height_change': height_change}

                        return feature, parallel_line_ft
        else:

            # print loop_index, failed_split
            # add_geom_to_layer(line_layer, parallel_line_geom2)

            # return False, False
            if failed_split > 1000:

                return False, False
            else:
                failed_split = failed_split + 1


def split_offset_distance(
        polygon_layer, line_layer, preview_layer,
        selected_line_ft, offset_distance, feature_ids=None, validate=False
):
    # Get selected line geometry
    selected_line_geom = selected_line_ft.geometry()

    QApplication.processEvents()
    # the height/ distance from selected line
    height = offset_distance

    # Get the parallel line from the selected line using the calculated height
    parallel_line_geom = get_parallel_line(
        selected_line_geom, height*-1
    )
    # Get one feature selected on preview layer. The preview layer has 1 feature
    # that copies and merges all selected feature from polygon.
    sel_features = list(preview_layer.getFeatures())
    # Get the geometry
    geom1 = sel_features[0].geometry()

    extent = geom1.boundingBox()
    # Using the extent, extend the parallel line to the selected
    # geometry bounding box to avoid failed split.
    added_points = extend_line_points(parallel_line_geom, extent)

    parallel_line_geom2 = QgsGeometry.fromPolyline(added_points)
    # If the line intersects the main geometry, split it
    if parallel_line_geom2.intersects(geom1):
        if validate:
            return True
        (res, split_geom0, topolist) = geom1.splitGeometry(
            added_points, False
        )

        if len(split_geom0) > 0:
            # Get the first line that intersects the geometry and use
            # it as a reference using distance to the split feature.
            split_geom = None
            main_geom = None
            first_intersection = selected_line_ft.geometry()

            # The closest geometry to fist intersection is the split geom
            if first_intersection.distance(geom1) < \
                    first_intersection.distance(split_geom0[0]):

                split_geom = geom1
                main_geom = split_geom0[0]
            elif first_intersection.distance(geom1) > \
                    first_intersection.distance(split_geom0[0]):

                if not len(split_geom0) > 1:

                    split_geom = split_geom0[0]
                    main_geom = geom1
            if split_geom is not None and main_geom is not None:
                add_geom_to_layer(
                    polygon_layer, split_geom, main_geom, feature_ids
                )
            else:
                return False
        return True
    else:
        return False


def get_azimuth(selected_line_ft, rotation_point_ft):
    polyline = selected_line_ft.geometry().asPolyline()
    selected_point = rotation_point_ft.geometry().asPoint()
    distance_point = OrderedDict()
    for point in polyline:
        # Remove the rotation point and find another point
        distance = rotation_point_ft.geometry().distance(
            QgsGeometry.fromPoint(point)
        )
        distance_point[distance] = point

    if len(polyline) > 0:

        intersecting_point = distance_point[min(distance_point.keys())]
        polyline.remove(intersecting_point)
        # print polyline
    azimuth = selected_point.azimuth(polyline[0])
    # print azimuth
    return azimuth

def split_rotate_line_with_area(
        polygon_layer, preview_layer, selected_line_ft,
        rotation_point_ft, area, feature_ids, clockwise
):
    selected_line = create_V2_line(selected_line_ft.geometry().asPolyline())
    # print polygon_layer, preview_layer, selected_line_ft, rotation_point_ft, area, feature_ids, clockwise
    try:
        sel_features = list(preview_layer.getFeatures())
    except Exception:
        return 1
        # Get the geometry
    try:
        ori_poly_geom = sel_features[0].geometry()
    except Exception:
        return 2

    poly_bbox = ori_poly_geom.boundingBox()

    decimal_place_new = 0
    increment = 1
    area_toggle = 0
    excessive_toggle = 9
    if clockwise == -1:
        angle_change = -1
    else:
        angle_change = 1
    angle = clockwise * -1

    size_calculator = QgsDistanceArea()
    line_angle = round(get_azimuth(selected_line_ft, rotation_point_ft), 0)
    crs = iface.activeLayer().crs()
    size_calculator.setSourceCrs(crs)
    size_calculator.setEllipsoid(crs.description())
    size_calculator.setEllipsoidalMode(True)

    split_area1 = 0
    loop_index = 0
    failed_intersection = 0
    # Use this intersection point to find the first touched
    # geometry to find the split geom
    intersecting_point_pt = None
    digits = 0.0
    skip_angle_set = False
    prev_toggle_index = 0
    # print split_area1, loop_index, failed_intersection, angle, \
    #     area_toggle, excessive_toggle, decimal_place_new
    while split_area1 <= area + 10000040:
        QApplication.processEvents()
        # digits = Decimal(1) / (Decimal(math.pow(10, decimal_place_new)) * increment)
        # increment = digits + Decimal(math.pow(10, decimal_place_new))
        # digits = Decimal(round(digits, decimal_place_new))
        # print digits, decimal_place_new
        # getcontext().prec = decimal_place_new
        # if decimal_place_new > 0:
        # print float(digits), decimal_place_new
        # digits = Decimal(1)/Decimal(math.pow(10, decimal_place_new))
        # digits = digits * loop_index
        # digits = Decimal(digits)
        # inc = (Decimal(increment)/\
        #       Decimal(math.pow(10, decimal_place_new))) + \
        #        Decimal(round(1/(math.pow(10, decimal_place_new)+1), decimal_place_new))


        # inc = Decimal
        # print inc, 'test'
        # if not skip_angle_set:
        if angle_change == -1:
            context = Context(prec=decimal_place_new, rounding=ROUND_DOWN)
            # setcontext(context)
            increment = context.create_decimal(1/math.pow(10, decimal_place_new))
            # increment = round(increment, decimal_place_new)

            if decimal_place_new == 0:
                increment = 1

            angle = Decimal(angle) - increment
            # angle = Decimal(round(angle, decimal_place_new))

        elif angle_change == 1:
            context = Context(prec=decimal_place_new, rounding=ROUND_UP)
            # setcontext(context)
            increment = context.create_decimal(1/math.pow(10, decimal_place_new))
            # increment = round(increment, decimal_place_new)
            # print increment, ' add ', round(increment, decimal_place_new)
            if decimal_place_new == 0:
                increment = 1
            angle = Decimal(angle) + increment
                # angle = Decimal(round(angle, decimal_place_new))
        # print float(digits)
        # else:
        #     digits = Decimal(angle_change)
        # if angle_change == -1:
        #     angle = angle - digits
        #     # print 'angle change'
        # elif angle_change == 1:
        #     angle = angle + digits
        # print angle, decimal_place_new, area_toggle, split_area1
        if angle > 180:
            angle = 0
        if angle < -180:
            angle = 0

        line_geom = QgsGeometry.fromWkt(selected_line.asWkt())
        line_geom.rotate(angle, rotation_point_ft.geometry().asPoint())

        added_points = extend_line_points(line_geom, poly_bbox)

        try:
            sel_feats = list(preview_layer.getFeatures())
        except Exception:

            return 3

        geom1 = sel_feats[0].geometry()
        original_area = round(geom1.area(), 0)
        ext_line_geom = QgsGeometry.fromPolyline(added_points)
        # add_geom_to_layer(
        #     QgsMapLayerRegistry.instance().mapLayersByName('Polygon Lines')[0],
        #     ext_line_geom
        # )

        if ext_line_geom.intersects(ori_poly_geom):
            # split with the rotated line
            # if loop_index == 0:
            #     intersection = ext_line_geom.intersection(ori_poly_geom)
            #     print intersection, 1
            #     inter_point = intersection.asPolyline()
            #
            #     print inter_point
            (res, split_geom, topolist) = geom1.splitGeometry(
                added_points, False
            )
            if len(split_geom) > 0:
                # print geom1.area(), split_geom[0].area()
                # Get first intersection coordinate
                if loop_index == 0:
                    intersection = ext_line_geom.intersection(ori_poly_geom)

                    # print intersection
                    inter_point = intersection.asPolyline()

                    # print inter_point
                    distance_point = OrderedDict()
                    for point in inter_point:
                        # Use other than the rotation point
                        distance = rotation_point_ft.geometry().distance(
                            QgsGeometry.fromPoint(point)
                        )
                        distance_point[distance] = point
                        # if round(distance, 0) == 0:
                        #     inter_point.remove(point)

                    # print inter_point, distance_point
                    if len(inter_point) > 0:
                        # break
                        intersecting_point = distance_point[
                            max(distance_point.keys())
                        ]
                        intersecting_point_pt = QgsGeometry.fromPoint(
                            intersecting_point
                        )

                    else:
                        continue

                if loop_index >= 1:
                    if intersecting_point_pt is None:
                        continue
                    if round((geom1.area() + split_geom[0].area()), 0) != original_area:
                        continue
                    # print geom1.area() + split_geom[0].area(), original_area
                    #
                    # make the geom close to intersection point to be split geom
                    if intersecting_point_pt.distance(geom1) < \
                            intersecting_point_pt.distance(split_geom[0]):
                        split_area1 = geom1.area()
                        split_geom1 = geom1
                        main_geom = split_geom[0]

                    else:
                        split_area1 = split_geom[0].area()
                        split_geom1 = split_geom[0]
                        main_geom = geom1

                loop_index = loop_index + 1
            else:
                continue

            # print angle, angle_change, split_area1
            # if loop_index > 1:
            #     print split_area1,  intersecting_point_pt.distance(split_geom1), \
            #                intersecting_point_pt.distance(main_geom)
            # else:
            #     print geom1.area(), split_geom[0].area()
            if area > split_area1:
                # helps in changing height in small steps after switching from

                # print 'area large ', decimal_place_new, increment, angle

                if area - math.modf(split_area1)[1] > 200:

                    if area_toggle == 0:
                        decimal_place_new = 0

                elif area - math.modf(split_area1)[1] in range(50, 200):

                    if area_toggle == 0:
                        decimal_place_new = 0

                elif area - math.modf(split_area1)[1] in range(10, 50):

                    if area_toggle == 0:
                        decimal_place_new = 0

                elif area - math.modf(split_area1)[1] in range(5, 10):

                    if area_toggle == 0:
                        decimal_place_new = 0

                elif area - math.modf(split_area1)[1] in range(2, 5):

                    if area_toggle == 0:
                        decimal_place_new = 1

                if area - math.modf(split_area1)[1] in range(0, 1):
                    if area_toggle == 0:
                        decimal_place_new = 2

                if clockwise == 1:
                    if angle_change == -1 and loop_index > 0:
                        # if decimal_place_new < 5:

                        # increment = increment + 1
                        if area_toggle < 4:
                            # do not allow loop increase if
                            if prev_toggle_index + 2 != loop_index:
                                decimal_place_new = decimal_place_new + 1
                                area_toggle = area_toggle + 1
                                prev_toggle_index = loop_index
                        else:
                            excessive_toggle = excessive_toggle + 1
                            if excessive_toggle > 300:
                                # add_geom_to_layer(
                                #     QgsMapLayerRegistry.instance().mapLayersByName(
                                #         'Polygon Lines')[0],
                                #     ext_line_geom
                                # )
                                return
                else:
                    if angle_change == 1 and loop_index > 0:
                        # if decimal_place_new < 5:
                        #     increment = increment + 1

                        if area_toggle < 4:
                            if prev_toggle_index + 2 != loop_index:
                                decimal_place_new = decimal_place_new + 1

                                area_toggle = area_toggle + 1
                                prev_toggle_index = loop_index
                        else:
                            excessive_toggle = excessive_toggle + 1
                            if excessive_toggle > 300:
                                # add_geom_to_layer(
                                #     QgsMapLayerRegistry.instance().mapLayersByName(
                                #         'Polygon Lines')[0],
                                #     ext_line_geom
                                # )
                                return
                if clockwise == 1:
                    angle_change = 1
                else:
                    angle_change = -1

                if (round(split_area1, 2)) == area:
                    add_geom_to_layer(
                        polygon_layer, split_geom1, main_geom, feature_ids
                    )
                    # parallel_line_ft = add_geom_to_feature(
                    #     line_layer, split_geom1
                    # )
                    return True
                # print 'area large ', angle_change, decimal_place_new, area_toggle, \
                #     split_area1, area, area - math.modf(split_area1)[1]
            if split_area1 > area:
                # helps in changing height in small steps after switching from

                # print 'area small ', decimal_place_new, increment, angle
                if math.modf(split_area1)[1] - area > 200:

                    if area_toggle == 0:
                        decimal_place_new = 0

                elif math.modf(split_area1)[1] - area in range(50, 200):

                    if area_toggle == 0:
                        decimal_place_new = 0

                elif math.modf(split_area1)[1] - area in range(10, 50):

                    if area_toggle == 0:
                        decimal_place_new = 0

                elif math.modf(split_area1)[1] - area in range(5, 10):

                    if area_toggle == 0:
                        decimal_place_new = 0

                elif math.modf(split_area1)[1] - area in range(2, 5):

                    if area_toggle == 0:
                        decimal_place_new = 1
                if math.modf(split_area1)[1] - area in range(0, 1):
                    if area_toggle == 0:
                        decimal_place_new = 2
                if clockwise == 1:
                    if angle_change == 1 and loop_index > 0:
                        # if decimal_place_new < 5:
                        # increment = increment + 1
                        if area_toggle < 4:
                            if prev_toggle_index + 2 != loop_index:
                                decimal_place_new = decimal_place_new + 1
                                area_toggle = area_toggle + 1
                                prev_toggle_index = loop_index

                        else:
                            excessive_toggle = excessive_toggle + 1
                            if excessive_toggle > 300:
                                # add_geom_to_layer(
                                #     QgsMapLayerRegistry.instance().mapLayersByName(
                                #         'Polygon Lines')[0],
                                #     ext_line_geom
                                # )
                                return
                else:
                    if angle_change == -1 and loop_index > 0:
                        # if decimal_place_new < 5:
                        # increment = increment + 1
                        if area_toggle < 4:
                            if prev_toggle_index + 2 != loop_index:
                                decimal_place_new = decimal_place_new + 1
                                area_toggle = area_toggle + 1
                                prev_toggle_index = loop_index
                        else:
                            excessive_toggle = excessive_toggle + 1
                            if excessive_toggle > 300:
                                # add_geom_to_layer(
                                #     QgsMapLayerRegistry.instance().mapLayersByName(
                                #         'Polygon Lines')[0],
                                #     ext_line_geom
                                # )
                                return
                if clockwise == 1:
                    angle_change = -1
                else:
                    angle_change = 1

                if (round(split_area1, 2)) == area:
                    add_geom_to_layer(
                        polygon_layer, split_geom1, main_geom, feature_ids
                    )
                    # parallel_line_ft = add_geom_to_feature(
                    #     line_layer, split_geom1
                    # )
                    return True

                # print 'area small ', angle_change, decimal_place_new, area_toggle, \
                #     split_area1, area, math.modf(split_area1)[1] - area

            if area == split_area1:

                add_geom_to_layer(
                    polygon_layer, split_geom1, main_geom, feature_ids
                )
                # parallel_line_ft = add_geom_to_feature(
                #     line_layer, split_geom1
                # )
                return True

        else:

            failed_intersection = failed_intersection + 1
            # if clockwise == 1:
            #     angle = angle - Decimal(line_angle)
            # else:
            #     angle = angle + Decimal(line_angle)

            if angle_change == -1:
                angle = angle - Decimal(line_angle)
            else:
                angle = angle + Decimal(line_angle)
            # print 'failed intersection', failed_intersection
            QApplication.processEvents()
            if failed_intersection > 200:
                return False
            else:
                pass


def split_join_points(
        polygon_layer, preview_layer, point_layer, feature_ids=None, validate=False
):

    # Get one feature selected on preview layer. The preview layer has 1 feature
    # that copies and merges all selected feature from polygon.
    sel_features = list(preview_layer.getFeatures())
    # Get the geometry
    geom1 = sel_features[0].geometry()

    extent = geom1.boundingBox()
    # Using the extent, extend the parallel line to the selected
    # geometry bounding box to avoid failed split.

    line_geom = points_to_line(point_layer)
    line_points = extend_line_points(line_geom, extent)

    # If the line intersects the main geometry, split it
    if line_geom.intersects(geom1):
        if validate:
            return True
        (res, split_geom0, topolist) = geom1.splitGeometry(
            line_points, False
        )

        if len(split_geom0) > 0:
            # Get the first line that intersects the geometry and use
            # it as a reference using distance to the split feature.
            split_geom = split_geom0[0]
            main_geom = geom1

            add_geom_to_layer(
                polygon_layer, split_geom, main_geom, feature_ids
            )

            return True

        return False

    else:
        return False


def active_spatial_column(entity, layer):
    # get all spatial columns of the entity.
    spatial_columns = [
        c.name
        for c in entity.columns.values()
        if c.TYPE_INFO == 'GEOMETRY'
    ]
    # get all fields excluding the geometry.
    layer_fields = [
        field.name()
        for field in layer.pendingFields()
    ]
    # get the currently being used geometry column
    active_sp_cols = [
        col
        for col in spatial_columns
        if col not in layer_fields
    ]

    if len(active_sp_cols) > 0:
        return active_sp_cols[0]
    else:
        return None



def get_wkt(entity, layer, spatial_column, feature_id):
    """
    Gets feature geometry in Well-Known Text
    format and returns it.
    :param spatial_column: The spatial column name.
    :type spatial_column: String
    :param feature_id: Feature id
    :type feature_id: Integer
    :return: Well-Known Text format of a geometry
    :rtype: WKT
    """
    geom_wkt = None
    fid = feature_id
    request = QgsFeatureRequest()
    request.setFilterFid(fid)
    features = layer.getFeatures(request)

    geom_col_obj = entity.columns[spatial_column]
    geom_type = geom_col_obj.geometry_type()

    # get the wkt of the geometry
    for feature in features:
        geometry = feature.geometry()
        if geometry.isGeosValid():
            if geom_type in ['MULTIPOLYGON', 'MULTILINESTRING']:
                geometry.convertToMultiType()

            geom_wkt = geometry.exportToWkt()

    return geom_wkt