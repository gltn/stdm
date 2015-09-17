"""
/***************************************************************************
Name                 : StdmMapToolCreateFeature
Description          : Map tool for creating spatial units, represented either
                       as a point, line or polygon.
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
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QAction, QApplication, QDialog, QMessageBox, \
    QProgressDialog

from qgis.core import QgsVectorLayer, QGis, QgsVectorDataProvider, \
    QgsGeometry, QgsFeature, QgsMapLayerRegistry, QgsCsException

# from stdm.ui import SpatialCoordinatesEditor
from .capture_tool import StdmMapToolCapture, CAPTURE_LINE, CAPTURE_NONE, \
    CAPTURE_POINT, CAPTURE_POLYGON
from .edit_tool import StdmMapToolEdit

__all__ = ["StdmMapToolCreateFeature"]


class StdmMapToolCreateFeature(StdmMapToolCapture):
    """
    Map tool for creating spatial units.
    """

    def __init__(self, iface):
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        StdmMapToolCapture.__init__(self, self.iface)

        # Store the geometry of the sketch
        self._geometry = None

        # Container for pending entities from foreign key mappers
        self._pending_fk_entities = {}

    def activate(self):
        if self.canvas.isDrawing():
            return

        StdmMapToolEdit.activate(self)

    def mapContextMenuRequested(self, pnt, menu):
        """
        Add actions to the editing context menu.
        """
        self.add_xy_action = QAction(QApplication.translate(
            "StdmMapToolCreateFeature", "Add X,Y Vertex..."),
            self.iface.mainWindow())
        self.cancel_sketch_action = QAction(QApplication.translate(
            "StdmMapToolCreateFeature", "Cancel Sketch"),
            self.iface.mainWindow())
        self.finish_sketch_action = QAction(QApplication.translate(
            "StdmMapToolCreateFeature", "Finish Sketch"),
            self.iface.mainWindow())

        if not self._capturing:
            self.finish_sketch_action.setEnabled(False)
            self.cancel_sketch_action.setEnabled(False)

        # Connect signals
        self.add_xy_action.triggered.connect(self.on_add_xy)
        self.finish_sketch_action.triggered.connect(self.on_finish_sketch)
        self.cancel_sketch_action.triggered.connect(self.stop_capturing)

        menu.addAction(self.add_xy_action)
        menu.addSeparator()
        menu.addAction(self.finish_sketch_action)
        menu.addAction(self.cancel_sketch_action)

    def supportsContextMenu(self):
        """
        This map tool supports an editing context menu.
        """
        return True

    def on_add_xy(self):
        """
        Slot raised to show the coordinates point editor for manually entering
        the X, Y coordinate values.
        """
        stdm_layer = self.current_vector_layer()

        # Try to set mode from layer type
        if self._mode == CAPTURE_NONE:
            self.set_capture_mode(stdm_layer)

        if not isinstance(stdm_layer, QgsVectorLayer):
            self.notify_not_vector_layer()
            return

        layer_wkb_type = stdm_layer.wkbType()
        provider = stdm_layer.dataProvider()

        if not (provider.capabilities() & QgsVectorDataProvider.AddFeatures):
            QMessageBox.information(self.iface.mainWindow(),
                                    QApplication.translate(
                                        "StdmMapToolCreateFeature", "Cannot "
                                                                    "add to "
                                                                    "layer"),
                                    QApplication.translate(
                                        "StdmMapToolCreateFeature",
                                        "The data provider for this layer "
                                        "does not support the addition of "
                                        "features."))
            return

        if not stdm_layer.isEditable():
            self.notify_not_editable_layer()
            return

        coords_editor = SpatialCoordinatesEditor(self.iface.mainWindow())
        ret = coords_editor.exec_()

        if ret == QDialog.Accepted:
            layerPoint = coords_editor.qgsPoint()

            # Spatial unit point capture
            if self._mode == CAPTURE_POINT:
                if stdm_layer.geometryType() != QGis.Point:
                    QMessageBox.information(self.iface.mainWindow(),
                                            QApplication.translate(
                                                "StdmMapToolCreateFeature",
                                                "Wrong create tool"),
                                            QApplication.translate(
                                                "StdmMapToolCreateFeature",
                                                "Cannot apply the 'Create "
                                                "Point Feature' tool on this"
                                                "vector layer"))
                    return

                self.start_capturing()

                if layer_wkb_type == QGis.WKBPoint or layer_wkb_type == \
                        QGis.WKBPoint25D:
                    self._geometry = QgsGeometry.fromPoint(layerPoint)
                elif layer_wkb_type == QGis.WKBMultiPoint or layer_wkb_type == \
                        QGis.WKBMultiPoint25D:
                    self._geometry = QgsGeometry.fromMultiPoint(layerPoint)

            elif self._mode == CAPTURE_LINE or self._mode == CAPTURE_POLYGON:
                if self._mode == CAPTURE_LINE and stdm_layer.geometryType() \
                        != QGis.Line:
                    QMessageBox.information(self.iface.mainWindow(),
                                            QApplication.translate(
                                                "StdmMapToolCreateFeature",
                                                "Wrong create tool"),
                                            QApplication.translate(
                                                "StdmMapToolCreateFeature",
                                                "Cannot apply the 'Create "
                                                "Line Feature' tool on this "
                                                "vector layer"))
                    return

                if self._mode == CAPTURE_POLYGON and stdm_layer.geometryType(

                ) != QGis.Polygon:
                    QMessageBox.information(self.iface.mainWindow(),
                                            QApplication.translate(
                                                "StdmMapToolCreateFeature",
                                                "Wrong create tool"),
                                            QApplication.translate(
                                                "StdmMapToolCreateFeature",
                                                "Cannot apply the 'Create "
                                                "Polygon Feature' tool on "
                                                "this vector layer"))
                    return

                error = self.add_vertex(layerPoint, True)

                if error == 2:
                    QMessageBox.critical(self.iface.mainWindow(),
                                         QApplication.translate(
                                             "StdmMapToolCreateFeature",
                                             "Coordinate transform error"),
                                         QApplication.translate(
                                             "StdmMapToolCreateFeature",
                                             "Cannot transform the point to "
                                             "the layer's coordinate system"))
                    return
                elif error == 3:
                    QMessageBox.critical(self.iface.mainWindow(),
                                         QApplication.translate(
                                             "StdmMapToolCreateFeature",
                                             "Coordinate transform error"),
                                         QApplication.translate(
                                             "StdmMapToolCreateFeature",
                                             "Cannot transform the layer "
                                             "point to the map's coordinate "
                                             "system"))
                    return

                self.start_capturing()

    def on_finish_sketch(self):
        """
        Slot raised upon selecting to finish drawing the sketch spatial unit.
        """
        stdm_layer = self.current_vector_layer()
        layer_wkb_type = stdm_layer.wkbType()

        feature = QgsFeature(stdm_layer.pendingFields())

        if self._mode == CAPTURE_POINT:
            feature.setGeometry(self._geometry)

        elif self._mode == CAPTURE_LINE or self._mode == CAPTURE_POLYGON:
            # Delete temporary rubber band
            if self._temp_rubber_band is not None:
                self.canvas.scene().removeItem(self._temp_rubber_band)
                del self._temp_rubber_band
                self._temp_rubber_band = None

            # Validate geometries using number of points
            if self._mode == CAPTURE_LINE and len(self._capture_list) < 2:
                self.stop_capturing()
                return

            if self._mode == CAPTURE_POLYGON and len(self._capture_list) < 3:
                self.stop_capturing()
                return

            if self._mode == CAPTURE_LINE:
                if layer_wkb_type == QGis.WKBLineString or layer_wkb_type == \
                        QGis.WKBLineString25D:
                    self._geometry = QgsGeometry.fromPolyline(
                        self._capture_list)

                elif layer_wkb_type == QGis.WKBMultiLineString or layer_wkb_type\
                        == QGis.WKBMultiLineString25D:
                    self._geometry = QgsGeometry.fromMultiPolyline(
                        self._capture_list)

                else:
                    QMessageBox.critical(self.iface.mainWindow(),
                                         QApplication.translate(
                                             "StdmMapToolCreateFeature",
                                             "WKB Type Error"),
                                         QApplication.translate(
                                             "StdmMapToolCreateFeature",
                                             "Cannot add feature. Unknown "
                                             "WKB type"))
                    return

                feature.setGeometry(self._geometry)

            # Polygon
            else:
                if layer_wkb_type == QGis.WKBPolygon or layer_wkb_type == \
                        QGis.WKBPolygon25D:
                    self._geometry = QgsGeometry.fromPolygon(
                        [self._capture_list])

                elif layer_wkb_type == QGis.WKBMultiPolygon or \
                        layer_wkb_type == \
                        QGis.WKBMultiPolygon25D:
                    self._geometry = QgsGeometry.fromMultiPolygon(
                        [self._capture_list])

                else:
                    QMessageBox.critical(self.iface.mainWindow(),
                                         QApplication.translate(
                                             "StdmMapToolCreateFeature",
                                             "WKB Type Error"),
                                         QApplication.translate(
                                             "StdmMapToolCreateFeature",
                                             "Cannot add feature. Unknown "
                                             "WKB type"))
                    return

                feature.setGeometry(self._geometry)

                avoid_intersections_return = feature.geometry(
                ).avoidIntersections()

                if avoid_intersections_return == 3:
                    QMessageBox.critical(self.iface.mainWindow(),
                                         QApplication.translate(
                                             "StdmMapToolCreateFeature",
                                             "Error"),
                                         QApplication.translate(
                                             "StdmMapToolCreateFeature",
                                             "An error was reported during "
                                             "intersection removal"))

                poly_wkb = feature.geometry().asWkb()

                if poly_wkb is None:
                    reason = ""
                    if avoid_intersections_return is not 2:
                        reason = QApplication.translate(
                            "StdmMapToolCreateFeature", "The feature cannot "
                                                        "be added because "
                                                        "it's geometry is "
                                                        "empty")
                    else:
                        reason = QApplication.translate(
                            "StdmMapToolCreateFeature", "The feature cannot "
                                                        "be added because "
                                                        "it's geometry "
                                                        "collapsed due to "
                                                        "intersection "
                                                        "avoidance")

                    QMessageBox.critical(self.iface.mainWindow(),
                                         QApplication.translate(
                                             "StdmMapToolCreateFeature",
                                             "Error"),
                                         reason)

                    self.stop_capturing()
                    del feature
                    self._reset_geometry()
                    return

        stdm_layer.beginEditCommand(QApplication.translate(
            "StdmMapToolCreateFeature", "Feature Added"))

        if self.add_feature(stdm_layer, feature):
            stdm_layer.endEditCommand()

        else:
            del feature
            self._reset_geometry()
            stdm_layer.destroyEditCommand()

        self.stop_capturing()

        self.canvas.refresh()

    def add_feature(self, stdmlayer, feat):
        """
        Add feature to the vector layer for pending commit.
        :type feat: QgsFeature
        :type stdmlayer: QgsVectorLayer
        """
        # Try set the attribute editor
        self._configure_spatial_editor(stdmlayer)

        if self._editorWidget is None:
            QMessageBox.critical(self.iface.mainWindow(),
                                 QApplication.translate(
                                     "StdmMapToolCreateFeature", "Cannot "
                                                                 "open "
                                                                 "editor"),
                                 QApplication.translate(
                                     "StdmMapToolCreateFeature", "Attribute "
                                                                 "editor for "
                                                                 "the "
                                                                 "selected "
                                                                 "layer "
                                                                 "could not "
                                                                 "be found."))
            return False

        # Connect commitChanges signals so that the relation of foreign key
        # entities can be updated accordingly.
        stdmlayer.committedFeaturesAdded.connect(self.onFeaturesCommitted)

        spEditor = self._editorWidget(self.iface.mainWindow(), stdmlayer, feat)

        if spEditor.exec_() is QDialog.Accepted:
            # Check for pending entities and add to collection
            pendingLayerEntities = spEditor.pendingLayerEntities()

            if not pendingLayerEntities.layerId() in self._pending_fk_entities:
                self._pending_fk_entities[
                    pendingLayerEntities.layerId()] = pendingLayerEntities

            else:
                self._pending_fk_entities[pendingLayerEntities.layerId()].merge(
                    pendingLayerEntities)

            return True

        else:
            return False

    def onFeaturesCommitted(self, layerid, features):
        """
        Update the related entities with the FK key from the primary spatial
        unit PK.
        """
        if layerid in self._pending_fk_entities:
            pendingLayerEntity = self._pending_fk_entities[layerid]

            # Get map layer using layerid
            refLayer = QgsMapLayerRegistry.instance().mapLayer(layerid)

            if refLayer is not None:
                fidx = refLayer.fieldNameIndex(
                    pendingLayerEntity.featureAttributeName())

                # Show progress dialog for updating the features.
                progressLabel = QApplication.translate(
                    "StdmMapToolCreateFeature", "Updating related entities...")
                progressDlg = QProgressDialog(
                    progressLabel, "", 0, len(features),
                    self.iface.mainWindow())
                progressDlg.setWindowModality(Qt.WindowModal)

                for i, feat in enumerate(features):
                    progressDlg.setValue(i)
                    uniqueAttrValue = feat.attributes()[fidx]
                    pendingLayerEntity.setPrimaryKey(
                        uniqueAttrValue, int(feat.id()))

                progressDlg.setValue(len(features))

    def canvasReleaseEvent(self, e):
        """
        Base class override.
        """
        stdmLayer = self.current_vector_layer()

        # Try to set mode from layer type
        if self._mode is CAPTURE_NONE:
            self.set_capture_mode(stdmLayer)

        if not isinstance(stdmLayer, QgsVectorLayer):
            self.notify_not_vector_layer()
            return

        layerWKBType = stdmLayer.wkbType()
        provider = stdmLayer.dataProvider()

        if not (provider.capabilities() & QgsVectorDataProvider.AddFeatures):
            QMessageBox.information(self.iface.mainWindow(),
                                    QApplication.translate(
                                        "StdmMapToolCreateFeature", "Cannot "
                                                                    "add to "
                                                                    "layer"),
                                    QApplication.translate(
                                        "StdmMapToolCreateFeature",
                                        "The data provider for this layer "
                                        "does not support the addition of "
                                        "features."))
            return

        if not stdmLayer.isEditable():
            self.notify_not_editable_layer()
            return

        # Spatial unit point capture
        if self._mode is CAPTURE_POINT:
            if stdmLayer.geometryType() is not QGis.Point:
                QMessageBox.information(self.iface.mainWindow(),
                                        QApplication.translate(
                                            "StdmMapToolCreateFeature",
                                            "Wrong create tool"),
                                        QApplication.translate(
                                            "StdmMapToolCreateFeature",
                                            "Cannot apply the 'Create Point "
                                            "Feature' tool on this vector "
                                            "layer"))
                return

            self.start_capturing()

            # Point in map coordinates
            mapPoint = None
            snapResults = []
            # Point in layer coordinates
            layerPoint = None

            opResult, snapResults = self._snapper.snapToBackgroundLayers(
                e.pos())

            if len(snapResults) > 0:
                mapPoint = self.snap_point_from_results(snapResults, e.pos())

            else:
                mapPoint = self.toMapCoordinates(e.pos())

            try:
                layerPoint = self.toLayerCoordinates(stdmLayer, mapPoint)
            except QgsCsException:
                QMessageBox.information(self.iface.mainWindow(),
                                        QApplication.translate(
                                            "StdmMapToolCreateFeature",
                                            "Coordinate transform error"),
                                        QApplication.translate(
                                            "StdmMapToolCreateFeature",
                                            "Cannot transform the point to "
                                            "the layer's coordinate system"))
                self._capturing = False
                return

            if layerWKBType is QGis.WKBPoint or layerWKBType is \
                    QGis.WKBPoint25D:
                self._geometry = QgsGeometry.fromPoint(layerPoint)
            elif layerWKBType is QGis.WKBMultiPoint or layerWKBType is \
                    QGis.WKBMultiPoint25D:
                self._geometry = QgsGeometry.fromMultiPoint(layerPoint)

        # Line and polygon capturing
        elif self._mode is CAPTURE_LINE or self._mode is CAPTURE_POLYGON:
            if self._mode is CAPTURE_LINE and stdmLayer.geometryType() is not \
                    QGis.Line:
                QMessageBox.information(self.iface.mainWindow(),
                                        QApplication.translate(
                                            "StdmMapToolCreateFeature",
                                            "Wrong create tool"),
                                        QApplication.translate(
                                            "StdmMapToolCreateFeature",
                                            "Cannot apply the 'Create Line "
                                            "Feature' tool on this vector "
                                            "layer"))
                return

            if self._mode is CAPTURE_POLYGON and stdmLayer.geometryType() is\
                    not\
                    QGis.Polygon:
                QMessageBox.information(self.iface.mainWindow(),
                                        QApplication.translate(
                                            "StdmMapToolCreateFeature",
                                            "Wrong create tool"),
                                        QApplication.translate(
                                            "StdmMapToolCreateFeature",
                                            "Cannot apply the 'Create "
                                            "Polygon  Feature' tool on this "
                                            "vector layer"))
                return

            if e.button() is Qt.LeftButton:
                error = self.add_vertex(e.pos())

                if error is 2:
                    QMessageBox.critical(self.iface.mainWindow(),
                                         QApplication.translate(
                                             "StdmMapToolCreateFeature",
                                             "Coordinate transform error"),
                                         QApplication.translate(
                                             "StdmMapToolCreateFeature",
                                             "Cannot transform the point to "
                                             "the layer's coordinate system"))
                    return

                self.start_capturing()

    def _reset_geometry(self):
        del self._geometry
        self._geometry = None
