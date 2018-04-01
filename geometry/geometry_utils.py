# split polygon by area
# 0. Run this file.
# 1. Select one polygon
# 2. move_line_with_area(selected_line1, 400) # line 1
# 2. move_line_with_area(selected_line2, 400) # line 2
# 2. move_line_with_area(selected_line3, 400) # line 3
# 2. move_line_with_area(selected_line4, 400) # line 4

# add points of a line then get another point by distance along the line.
#1. add_line_points_to_map(layer_point, selected_line2)
#2. point_by_distance(layer_point, selected_line2, 30)

# rotate line from a point with a given distance from line point end, with an angle
#1. add_layers(1)
#2. Select one point
#3. rotate_line_with_area(selected_line2, 300, 30, -1)
import json
import math
from collections import OrderedDict

from PyQt4.QtCore import QVariant
from PyQt4.QtGui import QColor, QApplication
from qgis.gui import QgsHighlight, QgsLayerPropertiesWidget, QgsGenericProjectionSelector
from qgis.core import QgsPoint, QgsGeometry, QgsVectorLayer, QgsFeature, \
    QgsMapLayerRegistry, QgsLineStringV2, QgsPointV2, edit, QgsDistanceArea, \
    QgsCoordinateReferenceSystem, QgsField, QgsPalLayerSettings, \
    QgsRenderContext, QGis, QgsFeatureRequest
from qgis.utils import iface
from stdm.settings.registryconfig import (
    selection_color
)
line_start = QgsPoint(50, 125)
line_m2 = QgsPoint(70, 70)
line_m3 = QgsPoint(100, 100)
line_end = QgsPoint(120, 150)
selected_line1 = QgsGeometry.fromPolyline([line_start, line_end])
selected_line2 = QgsGeometry.fromPolyline([line_end, line_m3])
selected_line3 = QgsGeometry.fromPolyline([line_m3, line_m2])
selected_line4 = QgsGeometry.fromPolyline([line_m2, line_start])


def calculate_area(polygon_geom):
    area = polygon_geom.area()
    return area


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


def create_temporary_layer(source_layer, type, name, show_legend=True):

    # create a new memory layer
    crs = source_layer.crs()
    crs_id = crs.srsid()
    auth_id = crs.authid()
    wkt = crs.toWkt()
    print auth_id
    print crs_id
    vl_geom_config = u"{0}?crs={1}&field=name:string(20)&" \
                     u"index=yes".format(type, wkt)


    iface.mainWindow().blockSignals(True)

    v_layer = QgsVectorLayer(vl_geom_config, name, "memory")


    iface.mainWindow().blockSignals(False)

    target_crs = QgsCoordinateReferenceSystem(
        crs_id, QgsCoordinateReferenceSystem.InternalCrsId
    )
    v_layer.setCrs(target_crs)
    iface.mapCanvas().mapSettings().setDestinationCrs(target_crs)
    print 'dest ', iface.mapCanvas().mapSettings().destinationCrs().authid()
    # iface.mapCanvas().setDestinationCrs(target_crs)
    iface.mapCanvas().refresh()
    if type == 'LineString':

        symbols = v_layer.rendererV2().symbols()
        symbol = symbols[0]
        symbol.setWidth(2)









    # show the line
    QgsMapLayerRegistry.instance().addMapLayer(
        v_layer, show_legend
    )
    v_layer.updateExtents()
    return v_layer

def create_memory_layer(type, name, line=1):
    srid = 4326
    line_start = QgsPoint(50, 125)

    line_m2 = QgsPoint(70, 70)
    line_m3 = QgsPoint(100, 100)
    line_end = QgsPoint(120, 150)
    # line = QgsGeometry.fromPolyline([line_start, line_end])

    # create a new memory layer
    vl_geom_config = u"{0}?crs=epsg:{1:d}&field=name:string(20)&" \
                     u"index=yes".format(type, srid)
    v_layer = QgsVectorLayer(vl_geom_config, name, "memory")
    pr = v_layer.dataProvider()
    # create a new feature
    feature = QgsFeature()

    # add the geometry to the feature,
    if type == 'LineString':
        if line == 1:
            feature.setGeometry(selected_line1)
        if line == 2:
            feature.setGeometry(selected_line2)
        if line == 3:
            feature.setGeometry(selected_line3)
        if line == 4:
            feature.setGeometry(selected_line4)

        pr.addFeatures([feature])
    elif type == 'Polygon':
        feature.setGeometry(
            QgsGeometry.fromPolygon([[line_start, line_m2, line_m3, line_end]])
        )
        pr.addFeatures([feature])

    # update extent of the layer (not necessary)
    v_layer.updateExtents()
    # show the line  
    QgsMapLayerRegistry.instance().addMapLayers([v_layer])
    return v_layer
layer = None
layer_poly = None
layer_point = None
def add_layers(line):
    global layer
    global layer_poly
    global layer_point

    layer = create_memory_layer('LineString', 'Line1', line)
    layer_poly = create_memory_layer('Polygon', 'Poly1')
    layer_point = create_memory_layer('Point', 'Point1')
    if line == 1:
        add_line_points_to_map(layer_point, selected_line1)
    if line == 2:
        add_line_points_to_map(layer_point, selected_line2)
    if line == 3:
        add_line_points_to_map(layer_point, selected_line3)
    if line == 4:
        add_line_points_to_map(layer_point, selected_line4)


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
        add_geom_to_layer(layer, extended_geom)
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
    geom = add_geom_to_layer(point_layer, point)
    return geom

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
    # x_max = polygon_extent.xMaximum()
    # x_min = polygon_extent.xMinimum()
    # #TODO take this method outside this function and put all output as inputs
    # line, slope, start_x, start_y, end_x, end_y = line_slope(line_geom)
    #
    # # x1 = x_max
    # # x = x_min
    #
    # # y1 = start_y + slope * (x_max - start_x)
    # y1 = start_y + slope * (start_x - x_min)
    # y = end_y = slope * (end_x - x_max)
    #
    # p4 = QgsPoint(x_max, y)
    # p3 = QgsPoint(end_x, end_y)
    # p2 = QgsPoint(start_x, start_y)
    # p1 = QgsPoint(x_min, y1)
    #
    # poly_line = [p1, p2, p3, p4]
    # print poly_line
    # return poly_line

    x_max = polygon_extent.xMaximum()
    x_min = polygon_extent.xMinimum()
    # TODO fix extending vertical line.
    line, slope, start_x, start_y, end_x, end_y = line_slope(line_geom)
    if slope is None:
        y_max = polygon_extent.yMaximum()
        y_min = polygon_extent.yMinimum()
        ext_end_y = y_max
        ent_start_y = y_min
    else:
        ext_end_y = end_y + slope * (x_max - end_x)
        ent_start_y = start_y + slope * (x_min - start_x)

    p1 = QgsPoint(x_min, ent_start_y)
    p2 = QgsPoint(start_x, start_y)
    p3 = QgsPoint(x_max, ext_end_y)
    poly_line = [p1, p2, p3]
    return poly_line


def move_line_with_area(
        polygon_layer, line_layer, preview_layer,
        selected_line_ft, area, feature_ids=None
):
    # Get selected line geometry
    selected_line_geom = selected_line_ft.geometry()

    decimal_place_new = 0

    height = 1
    split_area1 = 0
    height_change = 1
    loop_index = 0
    multi_split_case = 0

    # Continuous loop until condition of split area and split polygon area is equal
    while split_area1 >= 0:
        QApplication.processEvents()
        # the height/ distance from selected line
        height = height + height_change / math.pow(10, decimal_place_new)

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

        nearest_line_geom2 = QgsGeometry.fromPolyline(added_points)

        if nearest_line_geom2.intersects(geom1):
            (res, split_geom0, topolist) = geom1.splitGeometry(
                added_points, False
            )

            if len(split_geom0) > 0:

                if loop_index == 0:
                    first_intersection = selected_line_ft.geometry()

                if loop_index >= 1:

                    if first_intersection.distance(geom1) < \
                            first_intersection.distance(split_geom0[0]):

                        split_area1 = geom1.area()
                        split_geom = geom1
                        main_geom = split_geom0[0]
                    elif first_intersection.distance(geom1) > \
                            first_intersection.distance(split_geom0[0]):

                        if len(split_geom0) > 1:
                            continue
                            # if multi_split_case > 3:
                            #     continue
                            #     # raise Exception(u'The area is too small.')
                            # multi_split_case = multi_split_case + 1

                        else:
                            split_area1 = split_geom0[0].area()
                            split_geom = split_geom0[0]
                            main_geom = geom1
                    else:
                        continue
                loop_index = loop_index + 1
            else:
                print 'continue'
                continue

            if area > split_area1:
                # helps in changing height in small steps after switching from
                if height_change == -1 and math.modf(split_area1)[1] + 5 > area:
                    decimal_place_new = 4
                else:
                    decimal_place_new = 2

                height_change = 1
                # print '2 {} {}'.format(split_area1, area)
                if math.modf(split_area1)[1] + 3 > area:
                    decimal_place_new = 4
                    if (round(split_area1, 2)) == area:

                        print '2 {} {}'.format(split_area1, area)
                        add_geom_to_layer(
                            polygon_layer, split_geom, main_geom, feature_ids
                        )
                        break
            if area < split_area1:
                # helps in changing height in small steps after switching from
                if height_change == 1 and math.modf(split_area1)[1] < area + 5:
                    decimal_place_new = 4
                else:
                    decimal_place_new = 2
                height_change = -1
                # print '3 {} {}'.format(split_area1, area)
                if math.modf(split_area1)[1] < area + 3:
                    decimal_place_new = 4
                    if (round(split_area1, 2)) == area:
                        # add_geom_to_layer(line_layer, nearest_line_geom2)
                        print '3 {} {}'.format(split_area1, area)
                        add_geom_to_layer(
                            polygon_layer, split_geom, main_geom, feature_ids
                        )
                        break
        else:
            print 'Failed'
            break


def add_geom_to_layer(layer, geom, main_geom=None, feature_ids=None):
    if isinstance(geom, QgsPoint):
        geom = QgsGeometry.fromPoint(geom)
    iface.setActiveLayer(layer)
    # refresh map canvas to see the result
    # with edit(layer):
    layer.startEditing()
    if feature_ids is not None:
        if len(feature_ids) > 0:
            features = feature_id_to_feature(layer, feature_ids)

            # TODO consider change for merge before split
            features[0].setGeometry(main_geom)
            layer.updateFeature(features[0])

        feature = QgsFeature()
        attr = layer.fields().toList()
        feature.setAttributes(attr)
        feature.setGeometry(geom)
        layer.addFeatures([feature])
        layer.updateExtents()

    else:

        feature = QgsFeature()
        feature.setGeometry(geom)
        layer.addFeatures([feature])
        layer.updateExtents()
        zoom_refresh_to_geom(geom)

    # return geom

def add_geom_to_layer_with_measurement(layer, geom):
    provider = layer.dataProvider()
    feature = QgsFeature()
    if isinstance(geom, QgsPoint):
        geom = QgsGeometry.fromPoint(geom)
    layer.startEditing()
    feature.setGeometry(geom)

    if geom.type() == 1:

        feature.setAttributes(['measurement', round(geom.length(), 2)])

    if geom.type() == 2:

        feature.setAttributes(['measurement', round(geom.area(), 2)])
    layer.updateFeature(feature)

    provider.addFeatures([feature])

    layer.commitChanges()

    # layer.selectByIds([feature.id()])
    # zoom_refresh_to_geom(geom)
    return geom

def zoom_refresh_to_geom(geom):
    extent = geom.boundingBox()
    iface.mapCanvas().setExtent(extent)
    iface.mapCanvas().refresh()


def identify_selected_point_location(point_layer, line_geom):
    """

    :param line_geom:
    :type line_geom: QgsGeometry
    :param point_geom:
    :type point_geom: QgsPoint
    :return:
    :rtype:
    """
    points = line_geom.asPolyline()
    sel_feats = point_layer.selectedFeatures()
    point_geom = sel_feats[0].geometry()
    line = create_V2_line(points)
    start_point = line.startPoint()
    end_point = line.endPoint()

    if point_geom.exportToGeoJSON() == start_point.asJSON():
        return 'start'
    elif point_geom.exportToGeoJSON() == end_point.asJSON():
        return 'end'
    else:
        return 'middle'


def add_line_points_to_map(point_layer, line_geom):
    # TODO create a radio button list to select point
    # TODO reset line before starting
    clear_points(point_layer)
    poly_lines = line_geom.asPolyline()
    for point in poly_lines:
        add_geom_to_layer(point_layer, point)
    return poly_lines

def clear_points(point_layer):
    features = point_layer.getFeatures()
    ids = [f.id() for f in features]
    with edit(point_layer):
        point_layer.deleteFeatures(ids)

def point_by_distance(point_layer, selected_line, distance):

    location = identify_selected_point_location(point_layer, selected_line)

    if location == 'start':
        added_point_geom = get_point_by_distance(point_layer, selected_line, distance)
        return added_point_geom
    elif location == 'end':
        line_length = selected_line.length()
        distance_from_end = line_length - distance
        # print distance_from_end, distance, line_length
        added_point_geom = get_point_by_distance(
            point_layer, selected_line, distance_from_end)
        return added_point_geom
    else:
        return None

def test_rotate():
    point_geom = point_by_distance(layer_point, selected_line2, 30)

    ext_line_geom = rotate_from_distance_point(
        layer_poly, point_geom,
        selected_line2, 90, False
    )

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
        # print res, split_geom
        # break

#(selected_line1, 400, -1, False
def rotate_line_with_area(selected_line_geom, area, distance, clockwise):
    line_v2 = create_V2_line(selected_line_geom.asPolyline())

    for poly_ft in layer_poly.getFeatures():
        layer_poly.selectByIds([poly_ft.id()])
        break
    sel_feats = layer_poly.selectedFeatures()
    geom0 = sel_feats[0].geometry()
    orig_geom = QgsGeometry(geom0)
    poly_bbox = geom0.boundingBox()

    # extent = geom0.boundingBox()
    # poly_line = geom0.exportToGeoJSON()
    # poly_json = json.loads(poly_line)

    # print poly_json
    # points_in_poly = len(poly_json['coordinates'][0]) - 1

    # nearest_angle = ((points_in_poly - 2) * 180)/ points_in_poly

    point_geom = point_by_distance(layer_point, selected_line_geom, distance)

    # added_points = extend_line_points(selected_line_geom, poly_bbox)

    # ext_line_geom = QgsGeometry.fromPolyline(added_points)
    # result = ext_line_geom.rotate(nearest_angle, point_geom.asPoint())
    # ext_line_geom = selected_line_geom
    # added_points = extend_line_points(ext_line_geom, poly_bbox)

    # points = ext_line_geom.asPolyline()
    #
    # (res, split_geom, topolist) = geom0.splitGeometry(added_points, False)
    # print 'first split ', split_geom
    # if len(split_geom) < 1:
    #     (res, split_geom, topolist) = geom0.splitGeometry(points, False)
    # if len(split_geom) < 1:
    #     return
    # if direction == -1:
    # if split_geom[0].intersects(ext_line_geom):
    #     split_area = split_geom[0].area()
    #
    # else:
    #
    #     split_area = geom0.area()

    handle_area_split_area2(orig_geom, line_v2, point_geom, poly_bbox,
        area, clockwise)


def highlight_geom(map, layer, geom):
    sel_highlight = QgsHighlight(map, geom, layer)

    sel_highlight.setFillColor(selection_color())
    sel_highlight.setWidth(4)
    sel_highlight.setColor(QColor(212, 95, 0, 255))
    sel_highlight.show()


def handle_area_split_area2(ori_poly_geom, selected_line, point_geom, poly_bbox, area,
                            clockwise):
    decimal_place_new = 0
    increment = 4

    if clockwise == -1:
        angle_change = -1
    else:
        angle_change = 1
    angle = 0

    size_calculator = QgsDistanceArea()

    crs = iface.activeLayer().crs()
    size_calculator.setSourceCrs(crs)
    size_calculator.setEllipsoid(crs.description())
    size_calculator.setEllipsoidalMode(True)

    split_area1 = 0
    loop_index = 0
    # Use this intersection point to find the first touched
    # geometry to find the split geom
    intersecting_point_pt = None

    while split_area1 <= area + 140:

        decimal_place = decimal_place_new

        if angle_change == -1:
            angle = angle - increment / math.pow(10, decimal_place)

        elif angle_change == 1:
            angle = angle + increment / math.pow(10, decimal_place)

        if angle > 180:
            angle = 0
        if angle < -180:
            angle = 0

        line_geom = QgsGeometry.fromWkt(selected_line.asWkt())
        result = line_geom.rotate(angle, point_geom.asPoint())
        # print 'result ', result
        added_points = extend_line_points(line_geom, poly_bbox)
        sel_feats = layer_poly.selectedFeatures()
        geom1 = sel_feats[0].geometry()
        ext_line_geom = QgsGeometry.fromPolyline(added_points)

        if ext_line_geom.intersects(ori_poly_geom):
            # split with the rotated line
            (res, split_geom, topolist) = geom1.splitGeometry(
                added_points, False
            )
            if len(split_geom) > 0:
                # print 'geom1 ', geom1.area(), 'split_geom[0] ', split_geom[0].area()
                if clockwise == -1:
                    angle_change = -1

                else:
                    angle_change = 1
                # Get first intersection coordinate

                if loop_index == 0:
                    intersection = ext_line_geom.intersection(ori_poly_geom)
                    inter_point = intersection.asPolyline()

                    for point in inter_point:
                        distance = point_geom.distance(
                            QgsGeometry.fromPoint(point)
                        )
                        if round(distance, 0) == 0:
                            inter_point.remove(point)

                    if len(inter_point) > 0:
                        intersecting_point = inter_point[0]
                        intersecting_point_pt = QgsGeometry.fromPoint(
                            intersecting_point
                        )

                    else:
                        continue

                if loop_index >= 1:
                    if intersecting_point_pt is None:
                        continue

                    if intersecting_point_pt.distance(geom1) < \
                            intersecting_point_pt.distance(split_geom[0]):
                        split_area1 = geom1.area()
                        split_geom1 = geom1
                    else:
                        split_area1 = split_geom[0].area()
                        split_geom1 = split_geom[0]

                loop_index = loop_index + 1
            else:
                continue

            if area > split_area1:
                # helps in changing height in small steps after switching from
                # print 'area large ', angle_change, area, split_area1
                # print 'area large ', decimal_place_new, increment, angle
                if area - math.modf(split_area1)[1] > 50:
                    decimal_place_new = 0
                    increment = 2
                elif area - math.modf(split_area1)[1] > 100:
                    decimal_place_new = 0
                    increment = 4
                elif area - math.modf(split_area1)[1] <= 50:
                    decimal_place_new = 2
                    increment = 1
                # print angle_change, increase
                if angle_change == -1:
                    if math.modf(split_area1)[1] + 1 > area:
                        decimal_place_new = 4
                    if math.modf(split_area1)[1] + 7 > area:
                        decimal_place_new = 3
                    elif math.modf(split_area1)[1] + 50 > area:
                        decimal_place_new = 2
                    elif math.modf(split_area1)[1] + 100 > area:
                        decimal_place_new = 1
                # if bearing >= 0:
                if clockwise == -1:
                    angle_change = -1
                else:
                    angle_change = 1

                if math.modf(split_area1)[1] + 1 > area:
                    decimal_place_new = 4
                    increment = 1
                    if (round(split_area1, 2)) == area:
                        add_geom_to_layer(layer_poly, split_geom1)
                        break

            if area < split_area1:
                # helps in changing height in small steps after switching from
                # print 'area small ', angle_change, area, split_area1
                # print 'area small ', decimal_place_new, increment, angle
                if math.modf(split_area1)[1] - area > 50:
                    decimal_place_new = 0
                    increment = 2
                elif math.modf(split_area1)[1] - area > 100:
                    decimal_place_new = 0
                    increment = 4
                elif math.modf(split_area1)[1] - area <= 50:
                    decimal_place_new = 2
                    increment = 1
                if angle_change == 1:
                    if math.modf(split_area1)[1] < area + 1:
                        decimal_place_new = 4
                    elif math.modf(split_area1)[1] < area + 7:
                        decimal_place_new = 3
                    elif math.modf(split_area1)[1] < area + 50:
                        decimal_place_new = 2
                    elif math.modf(split_area1)[1] < area + 100:
                        decimal_place_new = 1

                if clockwise == -1:
                    angle_change = 1
                else:
                    angle_change = -1

                if math.modf(split_area1)[1] < area + 1:
                    decimal_place_new = 4
                    increment = 1

                    if (round(split_area1, 2)) == area:
                        add_geom_to_layer(layer_poly, split_geom1)
                        break

            if area == split_area1:
                add_geom_to_layer(layer_poly, split_geom1)
                break

        else:
            print 'failed'
            continue

def show_polygon_area(layer):
    sel_feats = layer_poly.selectedFeatures()

    polygon_geom = sel_feats[0].geometry() #TODO make this parameter
    add_geom_to_layer_with_measurement(layer, polygon_geom)

    add_layer_double_field(layer)
    label_layer_by_field(layer, 'measurement')

def polygon_to_lines(layer, measurement=True):
    if layer.name() == 'Polygon Lines':
        return None
    line_geoms = []
    line_layers = QgsMapLayerRegistry.instance().mapLayersByName('Polygon Lines')
    sel_feats = layer.selectedFeatures()

    if len(line_layers) == 0:
        line_layer = create_temporary_layer(layer, 'LineString', 'Polygon Lines')
    else:
        line_layer = line_layers[0]
        clear_layer_features(line_layer)
        iface.setActiveLayer(line_layer)

    type = layer_type(layer)

    for feature in sel_feats:
        if measurement:
            add_layer_double_field(line_layer)
        polygon_geom = feature.geometry()
        if polygon_geom is None:
            return None
        if type == 'Polygon':
            list_of_lines = polygon_geom.asPolygon()
            for lines in list_of_lines:
                line_geom_list = add_line_features(line_layer, lines, measurement)
                line_geoms.extend(line_geom_list)
        if type == 'MultiPolygon':
            list_of_lines_1 = polygon_geom.asMultiPolygon()
            for list_of_lines in list_of_lines_1:
                for lines in list_of_lines:
                    line_geom_list = add_line_features(line_layer, lines, measurement)
                    line_geoms.extend(line_geom_list)
    # line_layer.blockSignals(False)
    return line_layer


def add_line_features(line_layer, lines, measurement):
    line_geom_list = []
    for i, line in enumerate(lines):
        if i != len(lines) - 1:
            line_list = [line, lines[i + 1]]
            line_geom = QgsGeometry.fromPolyline(line_list)
            line_geom_list.append(line_geom)
            if measurement:
                add_geom_to_layer_with_measurement(line_layer, line_geom)
                label_layer_by_field(line_layer, 'measurement')

            else:
                add_geom_to_layer(line_layer, line_geom)
    return line_geom_list

def add_layer_double_field(layer):
    layer.startEditing()
    layer.addAttribute(QgsField('measurement', QVariant.Double))
    layer.updateFields()
    layer.commitChanges()


def label_layer_by_field(layer, field_name):
    layer.setCustomProperty("labeling", "pal")
    layer.setCustomProperty(
        "labeling/fieldName", field_name)
    if layer.wkbType() != QGis.WKBPolygon:
        layer.setCustomProperty(
            "labeling/placement", QgsPalLayerSettings.AboveLine
        )
    layer.setCustomProperty("labeling/placementFlags",
                                 QgsPalLayerSettings.AboveLine)
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

        for f_id in features:

            request = QgsFeatureRequest()
            request.setFilterFid(f_id)
            feature_itr = layer.getFeatures(request)
            for feat in feature_itr:
                mem_layer_data.addFeatures([feat])

    mem_layer.commitChanges()
    QgsMapLayerRegistry.instance().addMapLayer(mem_layer, addToLegend=add_to_legend)

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
    with edit(layer):
        feat_ids = [feat.id() for feat in layer.getFeatures()]
        layer.deleteFeatures(feat_ids)

def add_features_to_layer(layer, features):

    provider = layer.dataProvider()
    layer.startEditing()
    for feat in features:
        provider.addFeatures([feat])

    layer.commitChanges()

def feature_id_to_feature(layer, feature_ids):
    features = []
    for f_id in feature_ids:
        # print f_id
        request = QgsFeatureRequest()
        request.setFilterFid(f_id)
        feature_itr = layer.getFeatures(request)
        for feat in feature_itr:
            features.append(feat)

    return features


