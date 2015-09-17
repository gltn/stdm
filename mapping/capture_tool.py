"""
/***************************************************************************
Name                 : Stdm Map Tool Capture
Description          : Map tool for capturing points, lines and polygons.
                       Code has been ported from QGIS source.
Date                 : 1/April/2014
copyright            : (C) 2014 by UN-Habitat and implementing partners.
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
from PyQt4.QtCore import QSettings, Qt
from PyQt4.QtGui import QColor, QApplication

from qgis.gui import *
from qgis.core import *

from .edit_tool import StdmMapToolEdit

# Enums for digitization mode
CAPTURE_NONE = 0
CAPTURE_POINT = 1
CAPTURE_LINE = 2
CAPTURE_POLYGON = 3
mode = CAPTURE_NONE


class StdmMapToolCapture(StdmMapToolEdit):
    """
    Map tool for capturing points, lines and polygons.
    :type StdmMapToolEdit : Inherits from StdmMapToolEdit
    """

    def __init__(self, iface, mode=mode):
        """
        :type mode: object
        :type iface: int
        """
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        StdmMapToolEdit.__init__(self, self.iface)

        # Connect signals
        self.iface.legendInterface().currentLayerChanged.connect(
            self.on_current_layer_changed)

        # Instance variables
        self._mode = mode

        # Flag to indicate a map canvas capture operation is taking place
        self._capturing = False

        # Rubber band for polylines and polygons
        self._rubber_band = None

        # Temporary rubber band for polylines and polygons. this connects the
        # last added point to the mouse cursor position
        self._temp_rubber_band = None

        # List to store the points of digitized lines and polygons (in layer
        # coordinates)
        self._capture_list = []

        self._snapping_marker = None

    def capture_mode(self):
        """
        Returns the capture mode that the map tool is currently running in
        :return: Mode
        :rtype: int
        """
        return self._mode

    def deactivate(self):
        """
        Called when the map tool is deactivated.
        """
        self._snapping_marker = None

        StdmMapToolEdit.deactivate(self)

    def clear_snapper_marker(self):
        if self._snapping_marker is not None:
            self.canvas.scene().removeItem(self._snapping_marker)

            del self._snapping_marker
            self._snapping_marker = None

    def create_vertex_marker(self):
        """
        Function creates vertex marker that is used for marking new point on
        map.
        """
        # get qgis settings
        settings = QSettings()
        qgs_line_red = settings.value('/Qgis/digitizing/line_color_red', 255)
        qgs_line_green = settings.value('/Qgis/digitizing/line_color_green', 0)
        qgs_line_blue = settings.value('/Qgis/digitizing/line_color_blue', 0)
        qgs_marker_size = settings.value('/Qgis/digitizing/marker_size', 5)

        ver_marker = QgsVertexMarker(self.canvas)
        ver_marker.setIconSize(13)
        ver_marker.setIconType(QgsVertexMarker.ICON_CROSS)
        ver_marker.setColor(QColor(
            qgs_line_red, qgs_line_green, qgs_line_blue))
        ver_marker.setPenWidth(2)

        return ver_marker

    def set_capture_mode(self, layer):
        """
        Set the capture mode of the tool.
        """
        self._mode = CAPTURE_NONE

        if not isinstance(layer, QgsVectorLayer):
            return

        geom_type = layer.geometryType()
        if geom_type == QGis.Point:
            self._mode = CAPTURE_POINT
        elif geom_type == QGis.Line:
            self._mode = CAPTURE_LINE
        elif geom_type == QGis.Polygon:
            self._mode = CAPTURE_POLYGON
        else:
            self._mode = CAPTURE_NONE

    def canvasMoveEvent(self, e):
        """
        Mouse move event override.
        """
        self.clearSnapperMarker()

        snap_results = []
        op_result, snap_results = self._snapper.snapToBackgroundLayers(e.pos())
        map_point = self.snap_point_from_results(snap_results, e.pos())

        if len(snap_results) > 0:
            self._snapping_marker = self.createVertexMarker()
            self._snapping_marker.setCenter(map_point)

        if self._mode != CAPTURE_POINT and self._temp_rubber_band is not None \
                and self._capturing:
            self._temp_rubber_band.movePoint(map_point)

    def on_current_layer_changed(self, layer):
        """
        Slot raised when the map layer in the TOC changes.
        """
        self.set_capture_mode(layer)

    def next_point(self, point):
        layer_point = None
        map_point = None

        curr_layer = self.canvas.currentLayer()

        if not isinstance(curr_layer, QgsVectorLayer):
            QgsMessageLog.logMessage(QApplication.translate(
                "StdmMapToolCapture", "No Vector Layer Found"),
                QgsMessageLog.CRITICAL)
            return 1, layer_point, map_point

        try:
            map_point = self.toMapCoordinates(point)
        except QgsCsException:
            QgsMessageLog.logMessage(QApplication.translate(
                "StdmMapToolCapture", "Transformation to map coordinate "
                                      "failed"), QgsMessageLog.CRITICAL)
            return 2, layer_point, map_point

        try:
            layer_point = self.toLayerCoordinates(curr_layer, point)
        except QgsCsException:
            QgsMessageLog.logMessage(QApplication.translate(
                "StdmMapToolCapture",
                "Transformation to layer coordinate failed"),
                QgsMessageLog.CRITICAL)
            return 2, layer_point, map_point

        snap_results = []
        result, snap_results = self._snapper.snapToBackgroundLayers(
            point, snap_results)

        if len(snap_results) > 0:
            map_point = self.snap_point_from_results(snap_results, point)
            try:
                layer_point = self.toLayerCoordinates(curr_layer, map_point)
            except QgsCsException:
                QgsMessageLog.logMessage(QApplication.translate(
                    "StdmMapToolCapture", "Transformation to layer "
                                          "coordinate failed"),
                                         QgsMessageLog.CRITICAL)
                return 2, layer_point, map_point

        return 0, layer_point, map_point

    def add_vertex(self, point, is_layer_point=False):
        """
        Adds a point to the rubber band (in map coordinates) and to the
        capture  list (in layer coordinates) return 0 in case of success,
        1 if current layer is not a vector layer, 2 if layer coordinate
        transformation failed, 3 if map coordinate transformation failed.
        """
        layer_point = None
        map_point = None

        if self.captureMode() == CAPTURE_NONE:
            QgsMessageLog.logMessage(QApplication.translate(
                "StdmMapToolCapture", "Invalid capture mode"),
                QgsMessageLog.CRITICAL)
            return 2

        if not is_layer_point:
            result, layer_point, map_point = self.next_point(point)

            if result != 0:
                QgsMessageLog.logMessage(QApplication.translate(
                    "StdmMapToolCapture", "Next point failed"),
                    QgsMessageLog.CRITICAL)
                return result
        else:
            layer_point = point
            # Convert layer point to map coordinates for use in the rubberband
            try:
                map_point = self.toMapCoordinates(
                    self.current_vector_layer(), layer_point)
            except QgsCsException:
                QgsMessageLog.logMessage(QApplication.translate(
                    "StdmMapToolCapture", "Transformation to map coordinate "
                                          "failed"),
                                         QgsMessageLog.CRITICAL)
                return 3, layer_point, map_point

        geom_type = QGis.Polygon if self.captureMode() == CAPTURE_POLYGON \
            else QGis.Line

        if self._rubber_band is None:
            self._rubber_band = self.create_rubber_band(geom_type)
            self._rubber_band.show()

        self._rubber_band.addPoint(map_point)
        self._capture_list.append(layer_point)

        if self._temp_rubber_band is None:
            self._temp_rubber_band = self.create_rubber_band(geom_type, True)

        else:
            self._temp_rubber_band.reset(geom_type)

        if self.captureMode() == CAPTURE_LINE:
            self._temp_rubber_band.addPoint(map_point)

        elif self.captureMode() == CAPTURE_POLYGON:
            first_point = self._rubber_band.getPoint(0, 0)
            self._temp_rubber_band.addPoint(first_point)
            self._temp_rubber_band.movePoint(map_point)
            self._temp_rubber_band.addPoint(map_point)
            self._temp_rubber_band.addPoint(map_point)

        # TODO: Validate geometry

        return 0

    def undo(self):
        """
        Removes the last vertex from mRubberBand and mCaptureList
        """
        if self._rubber_band is not None:
            if len(self._capture_list) is 0 or \
                    self._rubber_band.numberOfVertices() is 0:
                return

            self._rubber_band.removePoint(-1)

            if self._rubber_band.numberOfVertices() > 1:
                if self._temp_rubber_band.numberOfVertices() > 1:
                    self._temp_rubber_band.removePoint(-1)
                    point = self._rubber_band.getPoint(
                        0, self._rubber_band.numberOfVertices() - 1)
                    self._temp_rubber_band.movePoint(
                        self._temp_rubber_band.numberOfVertices() - 2, point)

            else:
                self._temp_rubber_band.reset(
                    True if self.captureMode() == CAPTURE_POLYGON else False)

            self._capture_list.pop()

            # TODO:Validate geometry

    def keyPressEvent(self, e):
        """
        Remove the last point  if the user hits the Del or Backspace key
        """
        if e.key() == Qt.Key_Backspace or e.key() == Qt.Key_Delete:
            self.undo()

            # Prevent propagation to map canvas
            e.ignore()

    def start_capturing(self):
        self._capturing = True

    def stop_capturing(self):
        if self._rubber_band is not None:
            self.canvas.scene().removeItem(self._rubber_band)
            del self._rubber_band
            self._rubber_band = None

        if self._temp_rubber_band is not None:
            self.canvas.scene().removeItem(self._temp_rubber_band)
            del self._temp_rubber_band
            self._temp_rubber_band = None

        self._capturing = False
        self._capture_list = []
        self.canvas.refresh()

    def close_polygon(self):
        """
        Util function for closing polygon by linking the last point to the
        first one.
        """
        self._capture_list.append(self._capture_list[0])
