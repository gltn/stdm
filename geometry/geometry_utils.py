# split polygon by area
# 0. Run this file.
# 1. Select one polygon
# 2. move_line_with_area(selected_line1, 400, -1, False) # line 1
# 2. move_line_with_area(selected_line2, 400, -1, True) # line 2
# 2. move_line_with_area(selected_line3, 400, -1, True) # line 3
# 2. move_line_with_area(selected_line4, 400, -1, True) # line 4

# add points of a line then get another point by distance along the line.
#1. add_line_points_to_map(layer_point, selected_line2)
#2. point_by_distance(layer_point, selected_line2, 30)

# rotate line from a point with a given distance from line point end, with an angle
#1. add_line_points_to_map(layer_point, selected_line2)
#2. Select one point
#3. rotate_line_with_area(selected_line2, 300, 30, -1, True)
import json
import math

from qgis.core import QgsPoint, QgsGeometry, QgsVectorLayer, QgsFeature, \
    QgsMapLayerRegistry, QgsLineStringV2, QgsPointV2, edit
from qgis.utils import iface

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


layer = create_memory_layer('LineString', 'Line1', 1)
layer_poly = create_memory_layer('Polygon', 'Poly1')
layer_point = create_memory_layer('Point', 'Point1')


def rotate_line(point_geom, polygon_layer, line_geom, angle):
    # pr = layer.dataProvider()
    # line_start = QgsPoint(50, 50)
    # geom = None
    # for feature in layer.getFeatures():
    #     geom = feature.geometry()

    result = line_geom.rotate(angle, point_geom)
    print 'angle', angle
    print result
        # pr.addFeatures([feature])
        # # update extent of the layer (not necessary)
        # layer.updateExtents()
        # break
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
    # print angle
    return rotate_line(point_geom, polygon_layer, line_geom, angle)


def rotate_line_anti_clockwise(point_geom, polygon_layer, line_geom, angle):
    if angle > 0:
        angle = angle * -1
    # print angle
    return rotate_line(point_geom, polygon_layer, line_geom, angle)


def get_point_by_distance(point_layer, line_geom, distance):
    point = line_geom.interpolate(distance)
    geom = add_geom_to_layer(point_layer, point)
    return geom


def get_parallel_line(offset_distance):
    pr = layer.dataProvider()
    parallel_geom = None
    for feature in layer.getFeatures():
        geom = feature.geometry()
        parallel_geom = geom.offsetCurve(offset_distance, 1, 2, 0)
        break
    if parallel_geom is None:
        return None

    line_feature = QgsFeature()
    line_feature.setGeometry(parallel_geom)
    pr.addFeatures([line_feature])
    layer.updateExtents()
    return line_feature
    # return True


# def split_polygon(line_feature):
#     line_geom = line_feature.geometry()
#     points = line_geom.asPolyline()
#     selfeats = layer_poly.selectedFeatures()
#     pr = layer_poly.dataProvider()
#     geom0 = selfeats[0].geometry()
#     if line_geom.intersects(geom0):
#         (res, newlist, topolist) = geom0.splitGeometry(points, False)
#         if res == 0:
#             for geom in newlist:
#                 poly_feature = QgsFeature()
#                 poly_feature.setGeometry(geom)
#                 pr.addFeatures([poly_feature])
#                 layer.updateExtents()

#
# def split_by_area(line_feature, area):
#     line_geom = line_feature.geometry()
#     points = line_geom.asPolyline()
#     selfeats = layer_poly.selectedFeatures()
#     pr = layer_poly.dataProvider()
#     geom0 = selfeats[0].geometry()
#     if line_geom.intersects(geom0):
#         (res, newlist, topolist) = geom0.splitGeometry(points, False)
#         if newlist[0].area() == area:
#             # for geom in newlist:
#             poly_feature = QgsFeature()
#             poly_feature.setGeometry(newlist[0])
#             pr.addFeatures([poly_feature])
#             layer.updateExtents()
#

def check_segment_sign():
    pass


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
    x_max = polygon_extent.xMaximum()
    x_min = polygon_extent.xMinimum()
    line, slope, start_x, start_y, end_x, end_y = line_slope(line_geom)
    x1 = x_max
    x = x_min
    y = end_y + slope * (x - end_x)
    y1 = start_y + slope * (x1 - start_x)
    p1 = QgsPoint(x1, y1)
    p2 = QgsPoint(end_x, end_y)
    p3 = QgsPoint(x, y)
    # print p1.azimuth(p3)
    poly_line = [p1, p2, p3]
    print p1,
    return poly_line


def move_line_with_area(selected_line_geom, area):
    # original_line_geom = selected_line_geom
    original_line = selected_line_geom.exportToWkt()
    print original_line
    line_v2 = create_V2_line(selected_line_geom.asPolyline())

    height = area / selected_line_geom.length()
    nearest_line = get_parallel_line(height * -1)
    nearest_line_geom = nearest_line.geometry()
    sel_feats = layer_poly.selectedFeatures()
    geom0 = sel_feats[0].geometry()
    extent = geom0.boundingBox()
    # extend/elongate geometry
    added_points = extend_line_points(nearest_line_geom, extent)
    nearest_line_geom = QgsGeometry.fromPolyline(added_points)
    # add_geom_to_layer(layer, nearest_line_geom)

    if nearest_line_geom.intersects(geom0):
        (res, newlist, topolist) = geom0.splitGeometry(added_points, False)
        start_point = QgsGeometry.fromWkt(line_v2.startPoint().asWkt())
        print geom0.intersects(start_point)
        print newlist[0].intersects(start_point)

        if len(newlist) < 1:
            return
        # if direction == -1:
        if newlist[0].intersects(start_point):
            split_area = newlist[0].area()
            vertical = False
        else:
            vertical = True
            split_area = geom0.area()
        decimal_place = 1

        handle_area_split_area(
            area, decimal_place, height, split_area, vertical
        )
        handle_area_split_area(
            area, decimal_place, height, split_area, vertical, False
        )

def handle_area_split_area(area, ori_decimal_place, ori_height,
                           split_area, vertical=False, area_above=True):
    decimal_place_new = None
    height = None
    if area_above:
        condition = area > split_area
        height_change = 1
    else:
        condition = area < split_area
        height_change = -1
    while condition:
        if decimal_place_new is None:
            decimal_place = ori_decimal_place
        else:
            decimal_place = decimal_place_new
        if height is None:
            height = ori_height + height_change / math.pow(10, decimal_place)
        else:
            height = height + height_change / math.pow(10, decimal_place)

        nearest_line = get_parallel_line(height * -1)
        nearest_line_geom = nearest_line.geometry()
        selfeats = layer_poly.selectedFeatures()
        geom1 = selfeats[0].geometry()
        extent = geom1.boundingBox()
        # extend/elongate geometry
        added_points = extend_line_points(nearest_line_geom, extent)
        nearest_line_geom = QgsGeometry.fromPolyline(added_points)
        # add_geom_to_layer(layer, nearest_line_geom)
        print 'handler', nearest_line_geom.intersects(geom1)

        if nearest_line_geom.intersects(geom1):
            (res, newlist1, topolist) = geom1.splitGeometry(added_points,
                                                            False)

            if vertical:
                split_area1 = geom1.area()
                split_geom = geom1
            else:
                split_area1 = newlist1[0].area()
                split_geom = newlist1[0]
            if area > split_area1:
                # helps in changing height in small steps after switching from
                # area < split_area1
                if height_change == -1:
                    decimal_place_new = 2
                height_change = 1
                print height, decimal_place
                print '2 {} {}'.format(split_area1, area_above)
                if math.modf(split_area1)[1] + 3 > area:
                    decimal_place_new = 4
                    if (round(split_area1, 2)) == area:
                        add_geom_to_layer(layer_poly, split_geom)
                        break
            if area < split_area1:
                # helps in changing height in small steps after switching from
                # area > split_area1
                if height_change == 1:
                    decimal_place_new = 2
                height_change = -1
                print height, decimal_place
                print '3 {} {}'.format(split_area1, area_above)
                if math.modf(split_area1)[1] < area + 3:
                    decimal_place_new = 4
                    if (round(split_area1, 2)) == area:
                        add_geom_to_layer(layer_poly, split_geom)
                        break
        else:
            print 'Failed'
            break


def add_geom_to_layer(layer, geom):
    provider = layer.dataProvider()
    feature = QgsFeature()
    if isinstance(geom, QgsPoint):
        geom = QgsGeometry.fromPoint(geom)
    feature.setGeometry(geom)
    # print geom.exportToGeoJSON()
    provider.addFeatures([feature])
    layer.setSelectedFeatures([feature.id()])

    zoom_refresh_to_geom(geom)
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
    # point = point_geom.asPoint()
    line = create_V2_line(points)
    start_point = line.startPoint()
    end_point = line.endPoint()
    # print point_geom, start_point, end_point
    # print point_geom.exportToGeoJSON(), start_point.asJSON(), end_point.asJSON()
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
        get_point_by_distance(point_layer, selected_line, distance)

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
        polygon_layer, point_geom, line_geom, angle, clockwise=True):

    if clockwise:
        ext_line_geom = rotate_line_clockwise(
            point_geom.asPoint(), polygon_layer, line_geom, angle
        )
    else:
        ext_line_geom = rotate_line_anti_clockwise(
            point_geom.asPoint(), polygon_layer, line_geom, angle
        )
    return ext_line_geom
        # print res, split_geom
        # break

#(selected_line1, 400, -1, False
def rotate_line_with_area(selected_line_geom, area, distance, clockwise):

    for poly_ft in layer_poly.getFeatures():
        layer_poly.setSelectedFeatures([poly_ft.id()])
        break
    sel_feats = layer_poly.selectedFeatures()
    geom0 = sel_feats[0].geometry()
    # extent = geom0.boundingBox()
    poly_line = geom0.exportToGeoJSON()
    poly_json = json.loads(poly_line)
    # print poly_json
    points_in_poly = len(poly_json['coordinates'][0]) - 1

    nearest_angle = ((points_in_poly-2) * 180)/ points_in_poly

    point_geom = point_by_distance(layer_point, selected_line_geom, distance)

    ext_line_geom = rotate_from_distance_point(
        layer_poly, point_geom,
        selected_line_geom, nearest_angle, clockwise
    )

    points = ext_line_geom.asPolyline()

    (res, split_geom, topolist) = geom0.splitGeometry(points, False)

    # if not clockwise and len(split_geom) > 0:
    #     split_area = split_geom[0].area()
    # else:
    #     split_area = geom0.area()

    if len(split_geom) < 1:
        return
    # if direction == -1:
    if split_geom[0].intersects(ext_line_geom):
        split_area = split_geom[0].area()
        vertical = False
    else:
        vertical = True
        split_area = geom0.area()


    decimal_place = 1
    if area > split_area:
        handle_area_split_area2(geom0, selected_line_geom, point_geom,
            area, decimal_place, clockwise, nearest_angle, split_area, vertical
        )
    else:
        handle_area_split_area2(geom0, selected_line_geom, point_geom,
            area, decimal_place, clockwise, nearest_angle, split_area, vertical, False
        )


def handle_area_split_area2(poly_geom, selected_line_geom, point_geom, area,
                            ori_decimal_place, clockwise, ori_angle,
                           split_area, vertical=False, area_above=True):
    #TODO check if angle change is causing errors of two rotating lines
    decimal_place_new = None
    angle = None
    if area_above:
        condition = area > split_area
        angle_change = 1
    else:
        condition = area < split_area
        angle_change = -1
    while condition:
        if decimal_place_new is None:
            decimal_place = ori_decimal_place
        else:
            decimal_place = decimal_place_new
        print 'angle_change', angle_change
        if angle is None:
            angle = ori_angle + angle_change / math.pow(10, decimal_place)
        else:
            angle = angle + angle_change / math.pow(10, decimal_place)
        print 'angle', angle
        ext_line_geom = rotate_from_distance_point(
            layer_poly, point_geom, selected_line_geom, angle, clockwise
        )

        points = ext_line_geom.asPolyline()
        print 'points ', points
        if ext_line_geom.intersects(poly_geom):
            # split with the rotated line
            (res, split_geom, topolist) = poly_geom.splitGeometry(points, False)
            # add_geom_to_layer(polygon_layer, split_geom[0])

            # if vertical:
            if len(split_geom):
                split_area1 = split_geom[0].area()
                split_geom = split_geom[0]
            else:
                split_area1 = poly_geom.area()
                split_geom = poly_geom
            print 'compare ',  area, split_area1
            if area > split_area1:
                # helps in changing height in small steps after switching from
                # area < split_area1
                if angle_change == -1:
                    decimal_place_new = 10
                angle_change = 1

                print '22 {} {}'.format(split_area1, area_above)
                if math.modf(split_area1)[1] + 25 > area:
                    decimal_place_new = 10
                    print 'round ', int(round(split_area1))
                    if int(round(split_area1)) == area - 1:
                        add_geom_to_layer(layer_poly, split_geom)
                        break
            if area < split_area1:
                # helps in changing height in small steps after switching from
                # area > split_area1
                if angle_change == 1:
                    decimal_place_new = 10
                angle_change = -1

                print '32 {} {}'.format(split_area1, area_above)

                if math.modf(split_area1)[1] < area + 25:
                    decimal_place_new = 10
                    print 'round ', int(round(split_area1))
                    if int(round(split_area1)) == area + 1:
                        add_geom_to_layer(layer_poly, split_geom)
                        break
            if area == split_area1:

                print '42 {} {}'.format(split_area1, area_above)
                add_geom_to_layer(layer_poly, split_geom)
                break
        else:

            print 'Failed'
            # print '51 ', angle, decimal_place
            # print '52 {} {}'.format(split_area1, area_above)
            break

