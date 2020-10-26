"""
/***************************************************************************
Name                 : Coordinates Editor
Description          : Custom widget for entering an X,Y coordinate pair.
Date                 : 16/April/2014
copyright            : (C) 2014 by John Gitau
email                : gkahiu@gmail.com
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
from qgis.PyQt.QtCore import QSize
from qgis.PyQt.QtWidgets import (
    QWidget,
    QGridLayout,
    QDoubleSpinBox,
    QLabel,
    QApplication,
    QVBoxLayout
)
from qgis.core import QgsPoint

__all__ = ["CoordinatesWidget"]


class CoordinatesWidget(QWidget):
    """
    Custom widget for entering an X,Y coordinate pair.
    """

    def __init__(self, parent=None, x=0, y=0):
        QWidget.__init__(self, parent)
        self.resize(270, 130)

        self._gridLayout = QGridLayout(self)
        self._sbYCoord = QDoubleSpinBox(self)
        self._sbYCoord.setMinimumSize(QSize(0, 30))
        self._sbYCoord.setDecimals(5)
        self._sbYCoord.setMinimum(-180.0)
        self._sbYCoord.setMaximum(180.0)
        self._gridLayout.addWidget(self._sbYCoord, 2, 1, 1, 1)
        self._label_2 = QLabel(self)
        self._label_2.setText(QApplication.translate("CoordinatesWidget", "Y-Coordinate"))
        self._gridLayout.addWidget(self._label_2, 2, 0, 1, 1)
        self._label = QLabel(self)
        self._label.setMaximumSize(QSize(80, 16777215))
        self._label.setText(QApplication.translate("CoordinatesWidget", "X-Coordinate"))
        self._gridLayout.addWidget(self._label, 1, 0, 1, 1)
        self._sbXCoord = QDoubleSpinBox(self)
        self._sbXCoord.setMinimumSize(QSize(0, 30))
        self._sbXCoord.setDecimals(5)
        self._sbXCoord.setMinimum(-180.0)
        self._sbXCoord.setMaximum(180.0)
        self._gridLayout.addWidget(self._sbXCoord, 1, 1, 1, 1)
        self.vlNotification = QVBoxLayout()
        self._gridLayout.addLayout(self.vlNotification, 0, 0, 1, 2)

        # Set X and Y values
        self._sbXCoord.setValue(float(x))
        self._sbYCoord.setValue(float(y))

        self._geomPoint = QgsPoint(x, y)

        # Use default SRID
        self._srid = 4326

        # Connect signals
        self._sbXCoord.valueChanged.connect(self.onXCoordValueChanged)
        self._sbYCoord.valueChanged.connect(self.onYCoordValueChanged)

    def onXCoordValueChanged(self, value):
        """
        Slot raised when the value of the X-Coordinate spinbox changes
        """
        self._geomPoint.setX(value)

    def onYCoordValueChanged(self, value):
        """
        Slot raised when the value of the Y-Coordinate spinbox changes
        """
        self._geomPoint.setY(value)

    def xCoord(self):
        return self._geomPoint.x()

    def yCoord(self):
        return self._geomPoint.y()

    def XY(self):
        return (self.xCoord(), self.yCoord())

    def setX(self, xCoord):
        self._sbXCoord.setValue(xCoord)

    def setY(self, yCoord):
        self._sbYCoord.setValue(yCoord)

    def setXY(self, x, y):
        """
        Set both X and Y coordinate values.
        """
        self.setX(x)
        self.setY(y)

    def geomPoint(self):
        """
        Returns the coordinate representation as a QgsPoint.
        """
        return self._geomPoint

    def clear(self):
        """
        Clears the value from x and y coordinate spinbox.
        """
        self._sbXCoord.clear()
        self._sbYCoord.clear()

    def setSRID(self, geoModel):
        """
        Set the SRID using the SRID by using that one specified in the geometry column of
        an sqlalchemy object.
        """
        if hasattr(geoModel, "SRID"):
            self._srid = geoModel.SRID()

    def toEWKT(self):
        """
        Returns the specified X,Y point as an extended well-known text representation.
        PostGIS 2.0 requires geometry to be in EWKT specification.
        """
        return "SRID={0};{1}".format(str(self._srid), self._geomPoint.wellKnownText())
