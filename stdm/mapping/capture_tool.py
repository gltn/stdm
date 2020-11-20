"""
/***************************************************************************
Name                 : Stdm Map Tool Capture
Description          : Map tool for capturing points, lines and polygons.
                       Code has been ported from QGIS source.
Date                 : 1/April/2014
copyright            : (C) 2014 by UN-Habitat and implementing partners.
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

from qgis.PyQt.QtCore import (
    QSettings,
    Qt
)
from qgis.PyQt.QtGui import (
    QColor
)
from qgis.PyQt.QtWidgets import (
    QApplication
)
from qgis.core import (
    QgsVectorLayer,
    QgsCsException,
    QgsWkbTypes,
    QgsMessageLog
)
from qgis.gui import (
    QgsVertexMarker
)

from stdm.mapping.edit_tool import StdmMapToolEdit

# Enums for digitization mode
CAPTURE_NONE = 0
CAPTURE_POINT = 1
CAPTURE_LINE = 2
CAPTURE_POLYGON = 3
mode = CAPTURE_NONE


class StdmMapToolCapture(StdmMapToolEdit):
    """
    Map tool for capturing points, lines and polygons.
    """

    def __init__(self, iface, mode=mode):
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        StdmMapToolEdit.__init__(self, self.iface)

        # Connect signals
        self.iface.currentLayerChanged.connect(
            self.onCurrentLayerChanged)

        # Instance variables
        self._mode = mode

        # Flag to indicate a map canvas capture operation is taking place
        self._capturing = False

        # Rubber band for polylines and polygons
        self._rubberBand = None

        # Temporary rubber band for polylines and polygons. this connects the
        # last added point to the mouse cursor position
        self._tempRubberBand = None

        # List to store the points of digitized lines and polygons (in layer
        # coordinates)
        self._captureList = []

        self._snappingMarker = None

    def captureMode(self):
        """
        Returns the capture mode that the map tool is currently running in
        """
        return self._mode

    def deactivate(self):
        """
        Called when the map tool is deactivated.
        """
        self._snappingMarker = None

        StdmMapToolEdit.deactivate(self)

    def clearSnapperMarker(self):
        if self._snappingMarker is not None:
            self.canvas.scene().removeItem(self._snappingMarker)

            del self._snappingMarker
            self._snappingMarker = None

    def createVertexMarker(self):
        """
        Function creates vertex marker that is used for marking new point on
        map.
        """
        # get qgis settings
        settings = QSettings()
        qgsLineRed = settings.value("/Qgis/digitizing/line_color_red", 255)
        qgsLineGreen = settings.value("/Qgis/digitizing/line_color_green", 0)
        qgsLineBlue = settings.value("/Qgis/digitizing/line_color_blue", 0)
        qgsMarkerSize = settings.value("/Qgis/digitizing/marker_size", 5)

        verMarker = QgsVertexMarker(self.canvas)
        verMarker.setIconSize(13)
        verMarker.setIconType(QgsVertexMarker.ICON_CROSS)
        verMarker.setColor(QColor(qgsLineRed, qgsLineGreen, qgsLineBlue))
        verMarker.setPenWidth(2)

        return verMarker

    def setCaptureMode(self, layer):
        """
        Set the capture mode of the tool.
        """
        self._mode = CAPTURE_NONE

        if not isinstance(layer, QgsVectorLayer):
            return

        geomType = layer.geometryType()
        if geomType == QgsWkbTypes.PointGeometry:
            self._mode = CAPTURE_POINT
        elif geomType == QgsWkbTypes.LineGeometry:
            self._mode = CAPTURE_LINE
        elif geomType == QgsWkbTypes.PolygonGeometry:
            self._mode = CAPTURE_POLYGON
        else:
            self._mode = CAPTURE_NONE

    def canvasMoveEvent(self, e):
        """
        Mouse move event override.
        """
        self.clearSnapperMarker()

        snapResults = []
        opResult, snapResults = self._snapper.snapToBackgroundLayers(e.pos())
        mapPoint = self.snapPointFromResults(snapResults, e.pos())

        if len(snapResults) > 0:
            self._snappingMarker = self.createVertexMarker()
            self._snappingMarker.setCenter(mapPoint)

        if self._mode != CAPTURE_POINT and self._tempRubberBand is not None \
                and self._capturing:
            self._tempRubberBand.movePoint(mapPoint)

    def onCurrentLayerChanged(self, layer):
        """
        Slot raised when the map layer in the TOC changes.
        """
        self.setCaptureMode(layer)

    def nextPoint(self, point):
        layerPoint = None
        mapPoint = None

        currLayer = self.canvas.currentLayer()

        if not isinstance(currLayer, QgsVectorLayer):
            QgsMessageLog.logMessage(QApplication.translate(
                "StdmMapToolCapture", "No Vector Layer Found"),
                QgsMessageLog.CRITICAL)
            return 1, layerPoint, mapPoint

        try:
            mapPoint = self.toMapCoordinates(point)
        except QgsCsException:
            QgsMessageLog.logMessage(QApplication.translate(
                "StdmMapToolCapture", "Transformation to map coordinate "
                                      "failed"), QgsMessageLog.CRITICAL)
            return 2, layerPoint, mapPoint

        try:
            layerPoint = self.toLayerCoordinates(currLayer, point)
        except QgsCsException:
            QgsMessageLog.logMessage(QApplication.translate(
                "StdmMapToolCapture",
                "Transformation to layer coordinate failed"),
                QgsMessageLog.CRITICAL)
            return 2, layerPoint, mapPoint

        snapResults = []
        result, snapResults = self._snapper.snapToBackgroundLayers(
            point, snapResults)

        if len(snapResults) > 0:
            mapPoint = self.snapPointFromResults(snapResults, point)
            try:
                layerPoint = self.toLayerCoordinates(currLayer, mapPoint)
            except QgsCsException:
                QgsMessageLog.logMessage(QApplication.translate(
                    "StdmMapToolCapture", "Transformation to layer "
                                          "coordinate failed"),
                    QgsMessageLog.CRITICAL)
                return 2, layerPoint, mapPoint

        return 0, layerPoint, mapPoint

    def addVertex(self, point, isLayerPoint=False):
        """
        Adds a point to the rubber band (in map coordinates) and to the
        capture  list (in layer coordinates) return 0 in case of success,
        1 if current layer is not a vector layer, 2 if layer coordinate
        transformation failed, 3 if map coordinate transformation failed.
        """
        layerPoint = None
        mapPoint = None

        if self.captureMode() == CAPTURE_NONE:
            QgsMessageLog.logMessage(QApplication.translate(
                "StdmMapToolCapture", "Invalid capture mode"),
                QgsMessageLog.CRITICAL)
            return 2

        if not isLayerPoint:
            result, layerPoint, mapPoint = self.nextPoint(point)

            if result != 0:
                QgsMessageLog.logMessage(QApplication.translate(
                    "StdmMapToolCapture", "Next point failed"),
                    QgsMessageLog.CRITICAL)
                return result
        else:
            layerPoint = point
            # Convert layer point to map coordinates for use in the rubberband
            try:
                mapPoint = self.toMapCoordinates(
                    self.currentVectorLayer(), layerPoint)
            except QgsCsException:
                QgsMessageLog.logMessage(QApplication.translate(
                    "StdmMapToolCapture", "Transformation to map coordinate "
                                          "failed"),
                    QgsMessageLog.CRITICAL)
                return 3, layerPoint, mapPoint

        geomType = QgsWkbTypes.PolygonGeometry if self.captureMode() == CAPTURE_POLYGON \
            else QgsWkbTypes.LineGeometry

        if self._rubberBand is None:
            self._rubberBand = self.createRubberBand(geomType)
            self._rubberBand.show()

        self._rubberBand.addPoint(mapPoint)
        self._captureList.append(layerPoint)

        if self._tempRubberBand is None:
            self._tempRubberBand = self.createRubberBand(geomType, True)

        else:
            self._tempRubberBand.reset(geomType)

        if self.captureMode() == CAPTURE_LINE:
            self._tempRubberBand.addPoint(mapPoint)

        elif self.captureMode() == CAPTURE_POLYGON:
            firstPoint = self._rubberBand.getPoint(0, 0)
            self._tempRubberBand.addPoint(firstPoint)
            self._tempRubberBand.movePoint(mapPoint)
            self._tempRubberBand.addPoint(mapPoint)
            self._tempRubberBand.addPoint(mapPoint)

        # TODO: Validate geometry

        return 0

    def undo(self):
        """
        Removes the last vertex from mRubberBand and mCaptureList
        """
        if self._rubberBand is not None:
            if len(self._captureList) == 0 or \
                    self._rubberBand.numberOfVertices() == 0:
                return

            self._rubberBand.removePoint(-1)

            if self._rubberBand.numberOfVertices() > 1:
                if self._tempRubberBand.numberOfVertices() > 1:
                    self._tempRubberBand.removePoint(-1)
                    point = self._rubberBand.getPoint(
                        0, self._rubberBand.numberOfVertices() - 1)
                    self._tempRubberBand.movePoint(
                        self._tempRubberBand.numberOfVertices() - 2, point)

            else:
                self._tempRubberBand.reset(
                    True if self.captureMode() == CAPTURE_POLYGON else False)

            self._captureList.pop()

            # TODO:Validate geometry

    def keyPressEvent(self, e):
        """
        Remove the last point  if the user hits the Del or Backspace key
        """
        if e.key() == Qt.Key_Backspace or e.key() == Qt.Key_Delete:
            self.undo()

            # Prevent propagation to map canvas
            e.ignore()

    def startCapturing(self):
        self._capturing = True

    def stopCapturing(self):
        if self._rubberBand is not None:
            self.canvas.scene().removeItem(self._rubberBand)
            del self._rubberBand
            self._rubberBand = None

        if self._tempRubberBand is not None:
            self.canvas.scene().removeItem(self._tempRubberBand)
            del self._tempRubberBand
            self._tempRubberBand = None

        self._capturing = False
        self._captureList = []
        self.canvas.refresh()

    def closePolygon(self):
        """
        Util function for closing polygon by linking the last point to the
        first one.
        """
        self._captureList.append(self._captureList[0])
