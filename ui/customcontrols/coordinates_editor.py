"""
/***************************************************************************
Name                 : Coordinates Editor
Description          : Custom widget for entering an X,Y coordinate pair.
Date                 : 16/April/2014
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
from PyQt4.QtCore import QSize
from PyQt4.QtGui import QWidget, QGridLayout, QDoubleSpinBox, QLabel, \
    QApplication, QVBoxLayout

from qgis.core import QgsPoint

__all__ = ["CoordinatesWidget"]


class CoordinatesWidget(QWidget):
    """
    Custom widget for entering an X,Y coordinate pair.
    """

    def __init__(self, parent=None, x=0, y=0):
        QWidget.__init__(self, parent)
        self.resize(270, 130)

        self._grid_layout = QGridLayout(self)
        self._sb_ycoord = QDoubleSpinBox(self)
        self._sb_ycoord.setMinimumSize(QSize(0, 30))
        self._sb_ycoord.setDecimals(5)
        self._sb_ycoord.setMinimum(-180.0)
        self._sb_ycoord.setMaximum(180.0)
        self._grid_layout.addWidget(self._sb_ycoord, 2, 1, 1, 1)
        self._label_2 = QLabel(self)
        self._label_2.setText(QApplication.translate(
            "CoordinatesWidget", "Y-Coordinate"))
        self._grid_layout.addWidget(self._label_2, 2, 0, 1, 1)
        self._label = QLabel(self)
        self._label.setMaximumSize(QSize(80, 16777215))
        self._label.setText(QApplication.translate(
            "CoordinatesWidget", "X-Coordinate"))
        self._grid_layout.addWidget(self._label, 1, 0, 1, 1)
        self._sb_xcoord = QDoubleSpinBox(self)
        self._sb_xcoord.setMinimumSize(QSize(0, 30))
        self._sb_xcoord.setDecimals(5)
        self._sb_xcoord.setMinimum(-180.0)
        self._sb_xcoord.setMaximum(180.0)
        self._grid_layout.addWidget(self._sb_xcoord, 1, 1, 1, 1)
        self.vl_notification = QVBoxLayout()
        self._grid_layout.addLayout(self.vl_notification, 0, 0, 1, 2)

        # Set X and Y values
        self._sb_xcoord.setValue(float(x))
        self._sb_ycoord.setValue(float(y))

        self._geomPoint = QgsPoint(x, y)

        # Use default SRID
        self._srid = 4326

        # Connect signals
        self._sb_xcoord.valueChanged.connect(self.on_x_coord_value_changed)
        self._sb_ycoord.valueChanged.connect(self.on_y_coord_value_changed)

    def on_x_coord_value_changed(self, value):
        """
        Slot raised when the value of the X-Coordinate spinbox changes
        :param value:
        """
        self._geomPoint.setX(value)

    def on_y_coord_value_changed(self, value):
        """
        Slot raised when the value of the Y-Coordinate spinbox changes
        :param value:
        """
        self._geomPoint.setY(value)

    def x_coord(self):
        """
        :rtype : QgsPoint
        :return: Geometry Point
        """
        return self._geomPoint.x()

    def y_coord(self):
        """
        :rtype : QgsPoint
        :return: Geometry Point
        """
        return self._geomPoint.y()

    def x_y(self):
        """
        :rtype : Tuple
        :return: Geometry Points
        """
        return (self.x_coord(), self.y_coord())

    def set_x(self, x_coord):
        self._sb_xcoord.setValue(x_coord)

    def set_y(self, y_coord):
        self._sb_ycoord.setValue(y_coord)

    def set_x_y(self, x, y):
        """
        Set both X and Y coordinate values.
        """
        self.set_x(x)
        self.set_y(y)

    def geom_point(self):
        """
        Returns the coordinate representation as a QgsPoint.
        :rtype : QgsPoint
        """
        return self._geomPoint

    def set_srid(self, geo_model):
        """
        Set the SRID using the SRID by using that one specified in the
        geometry column of an sqlalchemy object.
        :param geo_model:
        """
        if hasattr(geo_model, "SRID"):
            self._srid = geo_model.SRID()

    def to_ewkt(self):
        """
        Returns the specified X,Y point as an extended well-known text
        representation. PostGIS 2.0 requires geometry to be in EWKT
        specification.
        :rtype : str
        """
        return "SRID={0};{1}".format(
            str(self._srid), self._geomPoint.wellKnownText())
