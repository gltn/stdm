"""
/***************************************************************************
Name                 : GeometryProvider
Description          : A class to read and enumerate collected data from mobile phones
                       as points to transform to respective geometry

Date                 : 20/June/2017
copyright            : (C) 2017 by UN-Habitat and implementing partners.
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

from qgis.core import (
    QgsGeometry,
    QgsPoint,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform
)

class GeometryProvider:
    """
    Class constructor
    """
    def __init__(self, string_list):
        """
        Initialize variables for the class
        The points are a list of X and Y for a particular entry in the file
        :param points_list:
        :rtype list
        """
        self.point_list = string_list
        self._local_list = []
        self._X = 0
        self._Y = 0
        area = float
        perimeter = float

    def point_to_list(self):
        """

        :return:
        """
        self._local_list = self.point_list.split(";")
        return self._local_list

    def points(self):
        """

        :return:
        """
        self.point_to_list()
        if len(self.point_list) > 0:
            self._local_list = self.point_list.split(";")
        return self._local_list

    def point(self):
        """
        We expect that if point array belong to a single point ,
        our list is not longer than one
        :return:
        """
        self.point_to_list()
        if len(self._local_list) < 2:
            return self._local_list[0].replace('0.0 0.0','').strip()
        else:
            return self._local_list[0]

    def x(self):
        """

        :return:
        """
        return self.point().split()[0]

    def y(self):
        """

        :return:
        """
        return self.point().split()[1]

    def set_point(self,x):
        """

        :param x:
        :return:
        """
        return round(float(x), 6)

    def default_coordinate_system(self):
        """
        Create the default google projection
        returns a projection
        :return:Projection
        """
        spRef = QgsCoordinateReferenceSystem()
        return spRef.createFromId(4326)

    def destination_coordinate_system(self):
        """

        :return:
        """
        spRef = QgsCoordinateReferenceSystem()
        return spRef.createFromId(22033)

    def create_linear_line(self):
        """

        :return:
        """
        self.point_to_list()
        line_array = []
        for point in self._local_list:
            if point != '':
                var = point.replace('0.0 0.0', '').strip().split(' ')
                line_array.append(QgsPoint(self.set_point(var[1]),
                                           self.set_point(var[0])))
        return QgsGeometry.fromPolyline([line_array])

    def create_point(self):
        """

        :return:
        """
        qPoint = QgsGeometry.fromPoint(QgsPoint(self.set_point(self.X()),
                                                self.set_point(self.Y())))
        return qPoint

    def create_polygon(self):
        """

        :return:
        """
        self.point_to_list()

        line_array = []
        for point in self._local_list:
            if point != '':
                var = point.replace('0.0 0.0', '').strip().split(' ')
                line_array.append(QgsPoint(self.set_point(var[1]),
                                           self.set_point(var[0])))

        geom_poly = QgsGeometry.fromPolygon([line_array])

        return geom_poly

    def geometry_from_wkt(self, wkt):
        """

        :return:
        """
        geom = QgsGeometry.fromWkt(wkt)
        return geom

class GeomPolgyon(GeometryProvider):
    """
    Class constructor
    """
    def __init__(self, geomlist):
        """
        Initialize variables
        """
        GeometryProvider.__init__(self, geomlist)

    def polygon_to_Wkt(self):
        """

        :return:
        """
        poly = self.create_polygon()

        poly_as_text = poly.exportToWkt()
        #raise NameError(str(poly_as_text))
        # crsTransform = QgsCoordinateTransform(
        #     self.default_coordinate_system(),
        #     self.destination_coordinate_system())
        # poly_as_text.transform(crsTransform)

        return 'SRID={};{}'.format(32733, poly_as_text)



