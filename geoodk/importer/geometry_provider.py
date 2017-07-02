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

from osgeo import (
    ogr,
    osr
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

    def X(self):
        """

        :return:
        """
        return self.point().split()[0]

    def Y(self):
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
        spRef = osr.SpatialReference()
        return spRef.ImportFromEPSG(4326)

    def destination_coordinate_system(self):
        """

        :return:
        """
        spsRef = osr.SpatialReference()
        return spsRef.ImportFromEPSG(32737)

    def create_linear_rings(self):
        """

        :return:
        """
        self.point_to_list()
        polyring = ogr.Geometry(ogr.wkbLinearRing)
        for point in self._local_list:
            if point != '':
                var = point.replace('0.0 0.0', '').strip().split(' ')
                polyring.AddPoint(self.set_point(var[1]), self.set_point(var[0]))
        return polyring

    def create_point(self):
        """

        :return:
        """
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(self.set_point(self.X()), self.set_point(self.Y()))
        return point.ExportToWkt()


    def create_line(self):
        """

        :return:
        """
        return self.create_linear_rings().ExportToIsoWkt()



    def create_polygon(self):
        """

        :return:
        """
        polyring = self.create_linear_rings()
        geompoly = ogr.Geometry(ogr.wkbPolygon)
        geompoly.AddGeometry(polyring)
        return geompoly

    def create_geometry_collection(self):
        """

        :return:
        """
        return ogr.Geometry(ogr.wkbGeometryCollection)

    def geometry_from_wkt(self, wkt):
        """

        :return:
        """
        geom = ogr.CreateGeometryFromWkt(wkt)
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

        transform = osr.CoordinateTransformation(self.default_coordinate_system(),
                                                 self.destination_coordinate_system())
        poly.Transform(transform)
        return poly.ExportToWkt()



