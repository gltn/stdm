"""
/***************************************************************************
Name                 : StdmMapToolEdit
Description          : Base class for all STDM editing map tools.
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
from PyQt4.QtCore import Qt, QSettings
from PyQt4.QtGui import QMenu, QCursor, QColor, QApplication

from qgis.gui import QgsMapTool, QgsMapCanvasSnapper, QgsRubberBand, \
    QgsVertexMarker
from qgis.core import QGis, QgsGeometry, QgsVectorLayer

from .utils import pg_layer_names_id_mapping
# from .editor_config import spatial_editor_widgets


class StdmMapToolEdit(QgsMapTool):
    """
    Base class for all STDM editing map tools.
    """

    def __init__(self, iface):
        self._iface = iface
        self._canvas = self._iface.mapCanvas()
        QgsMapTool.__init__(self, self._canvas)

        # Snapper object that reads the settings from project and applies to
        # the map canvas
        self._snapper = QgsMapCanvasSnapper(self._canvas)

        # Dialog for setting textual attributes of the spatial unit being
        # digitized.
        self._editorWidget = None

        # Initial context menu state of the map canvas
        self._mpCanvasContentMenuPolicy = self._canvas.contextMenuPolicy()

    def isEditTool(self):
        """
        Check edit tool status
        :rtype : bool
        :return: True
        """
        return True

    def activate(self):
        """
        Activates Map tool
        :rtype : None
        """
        QgsMapTool.activate(self)

        if self.supportsContextMenu():
            self._canvas.setContextMenuPolicy(Qt.CustomContextMenu)
            self._canvas.customContextMenuRequested.connect(
                self.on_map_context_menu_requested)

    def deactivate(self):
        """
        Deactivates Map tool
        :rtype : None
        """
        if self.supportsContextMenu():
            self._canvas.setContextMenuPolicy(self._mpCanvasContentMenuPolicy)
            self._canvas.customContextMenuRequested.disconnect(
                self.on_map_context_menu_requested)

        QgsMapTool.deactivate(self)

    def on_map_context_menu_requested(self, pnt):
        """
        Slot raised upon right-clicking the map canvas.
        :param pnt:
        :rtype : None
        """
        editMenu = QMenu(self._iface.mainWindow())
        self.mapContextMenuRequested(pnt, editMenu)

        if not editMenu.isEmpty():
            editMenu.exec_(QCursor.pos())

    def mapContextMenuRequested(self, pnt, menu):
        """
        Protected function to be implemented by subclasses for adding edit
        actions into the context menu.
        Default does nothing.
        :rtype : None
        :param pnt:
        :param menu:
        """
        pass

    def supportsContextMenu(self):
        """
        Set whether the map tool supports a custom context menu for
        additional  mapping functionality
        on edit mode.
        To be implemented by sub-classes.
        :rtype : bool
        """
        return False

    def snap_point_from_results(self, snap_results, screen_coords):
        """
        Extracts a single snapping point from a set of snapping results.
        This is useful for snapping operations that just require a position
        to  snap to and not all the snapping results. If the list is empty,
        the screen coordinates are transformed into map coordinates and
        returned.
        :rtype : QgsVertexMarker
        :param snap_results: list
        :param screen_coords: QMouseEvent
        """
        if len(snap_results) == 0:
            return self.toMapCoordinates(screen_coords)

        else:
            return snap_results[0].snappedVertex

    def create_rubber_band(self, geom_type, alternative_band=False):
        """
        Creates a rubber band with the color/line width from the QGIS settings.
        :rtype : QgsRubberBand
        :param geom_type: QgsGeometry
        :param alternative_band: bool
        """
        settings = QSettings()
        rb = QgsRubberBand(self._canvas, geom_type)
        rb.setWidth(settings.value("/Qgis/digitizing/line_width", 1))
        color = QColor(settings.value("/Qgis/digitizing/line_color_red", 255),
                       settings.value("/Qgis/digitizing/line_color_green", 0),
                       settings.value("/Qgis/digitizing/line_color_blue", 0))

        my_alpha = settings.value(
            "/Qgis/digitizing/line_color_alpha", 200) / 255.0

        if alternative_band:
            my_alpha = my_alpha * 0.75
            rb.setLineStyle(Qt.DotLine)

        if geom_type == QGis.Polygon:
            color.setAlphaF(my_alpha)

        rb.setColor(color)
        rb.show()

        return rb

    def current_vector_layer(self):
        """
        Returns the current vector layer of the map canvas or None
        :rtype : QgsVectorLayer
        """
        return self._canvas.currentLayer()

    def notify_not_vector_layer(self):
        """
        Display a timed message bar noting the active layer is not vector.
        :rtype : None
        """
        self.messageEmitted.emit(QApplication.translate(
            "StdmMapToolEdit", "No active vector layer"))

    def notify_not_editable_layer(self):
        """
        Display a timed message bar noting the active vector layer is not
        editable.
        :rtype : None
        """
        self.messageEmitted.emit(QApplication.translate(
            "StdmMapToolEdit", "Layer not editable"))

    def set_editor_widget(self, editor_widget):
        """
        Set the widget for editing attributing values
        :rtype : None
        :param editor_widget:
        :type editor_widget: object
        """
        self._editorWidget = editor_widget

    def _configure_spatial_editor(self, layer):
        """
        Factory method that sets the spatial editor dialog using the
        configuration specified in the
        editor_config module.
        :rtype : None
        :param layer: QgsVectorLayer
        """
        layer_id = layer.id()
        if layer_id in pg_layer_names_id_mapping().reverse:
            table_name = pg_layer_names_id_mapping().reverse[layer_id]
            # Get corresponding editor widget from the config
            # if tableName in spatial_editor_widgets:
            #     self._editorWidget = spatial_editor_widgets[tableName]
