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
    QProgressDialog, QMenu, QMouseEvent

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
        self._iface = iface
        self._canvas = self._iface.mapCanvas()
        StdmMapToolCapture.__init__(self, self._iface)

        # Store the geometry of the sketch
        self._geometry = None

        # Container for pending entities from foreign key mappers
        self._pending_fk_entities = {}

    def activate(self):
        """
        Make STDM edit session active
        :rtype : None
        :return:
        """
        if self._canvas.isDrawing():
            return

        StdmMapToolEdit.activate(self)

    def mapContextMenuRequested(self, pnt, menu):
        """
        Method to add edit actions into the context menu.
        :rtype : None
        :param pnt:
        :param menu: QMenu
        """
        self.add_xy_action = QAction(QApplication.translate(
            "StdmMapToolCreateFeature", "Add X,Y Vertex..."),
            self._iface.mainWindow())
        self.cancel_sketch_action = QAction(QApplication.translate(
            "StdmMapToolCreateFeature", "Cancel Sketch"),
            self._iface.mainWindow())
        self.finish_sketch_action = QAction(QApplication.translate(
            "StdmMapToolCreateFeature", "Finish Sketch"),
            self._iface.mainWindow())

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
        :rtype : bool
        """
        return True

    def on_add_xy(self):
        """
        Slot raised to show the coordinates point editor for manually entering
        the X, Y coordinate values.
        :rtype : None
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
            QMessageBox.information(self._iface.mainWindow(),
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

        coords_editor = SpatialCoordinatesEditor(self._iface.mainWindow())
        ret = coords_editor.exec_()

        if ret == QDialog.Accepted:
            layer_point = coords_editor.qgsPoint()

            # Spatial unit point capture
            if self._mode == CAPTURE_POINT:
                if stdm_layer.geometry_type() != QGis.Point:
                    QMessageBox.information(self._iface.mainWindow(),
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
                    self._geometry = QgsGeometry.fromPoint(layer_point)
                elif layer_wkb_type == QGis.WKBMultiPoint or layer_wkb_type \
                        == QGis.WKBMultiPoint25D:
                    self._geometry = QgsGeometry.fromMultiPoint(layer_point)

            elif self._mode == CAPTURE_LINE or self._mode == CAPTURE_POLYGON:
                if self._mode == CAPTURE_LINE and stdm_layer.geometry_type() \
                        != QGis.Line:
                    QMessageBox.information(self._iface.mainWindow(),
                                            QApplication.translate(
                                                "StdmMapToolCreateFeature",
                                                "Wrong create tool"),
                                            QApplication.translate(
                                                "StdmMapToolCreateFeature",
                                                "Cannot apply the 'Create "
                                                "Line Feature' tool on this "
                                                "vector layer"))
                    return

                if self._mode == CAPTURE_POLYGON and stdm_layer.geometry_type(

                ) != QGis.Polygon:
                    QMessageBox.information(self._iface.mainWindow(),
                                            QApplication.translate(
                                                "StdmMapToolCreateFeature",
                                                "Wrong create tool"),
                                            QApplication.translate(
                                                "StdmMapToolCreateFeature",
                                                "Cannot apply the 'Create "
                                                "Polygon Feature' tool on "
                                                "this vector layer"))
                    return

                error = self.add_vertex(layer_point, True)

                if error == 2:
                    QMessageBox.critical(self._iface.mainWindow(),
                                         QApplication.translate(
                                             "StdmMapToolCreateFeature",
                                             "Coordinate transform error"),
                                         QApplication.translate(
                                             "StdmMapToolCreateFeature",
                                             "Cannot transform the point to "
                                             "the layer's coordinate system"))
                    return
                elif error == 3:
                    QMessageBox.critical(self._iface.mainWindow(),
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
        :rtype : None
        """
        stdm_layer = self.current_vector_layer()
        layer_wkb_type = stdm_layer.wkbType()

        feature = QgsFeature(stdm_layer.pendingFields())

        if self._mode == CAPTURE_POINT:
            feature.setGeometry(self._geometry)

        elif self._mode == CAPTURE_LINE or self._mode == CAPTURE_POLYGON:
            # Delete temporary rubber band
            if self._temp_rubber_band is not None:
                self._canvas.scene().removeItem(self._temp_rubber_band)
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
                    QMessageBox.critical(self._iface.mainWindow(),
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
                    QMessageBox.critical(self._iface.mainWindow(),
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
                    QMessageBox.critical(self._iface.mainWindow(),
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

                    QMessageBox.critical(self._iface.mainWindow(),
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

        self._canvas.refresh()

    def add_feature(self, stdm_layer, feat):
        """
        Add feature to the vector layer for pending commit.
        :rtype : bool
        :param stdm_layer: QgsVectorLayer
        :param feat: QgsFeature
        """
        # Try set the attribute editor
        self._configure_spatial_editor(stdm_layer)

        if self._editorWidget is None:
            QMessageBox.critical(self._iface.mainWindow(),
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
        stdm_layer.committedFeaturesAdded.connect(self.on_features_committed)

        sp_editor = self._editorWidget(self._iface.mainWindow(), stdm_layer,
                                       feat)

        if sp_editor.exec_() is QDialog.Accepted:
            # Check for pending entities and add to collection
            pending_layer_entities = sp_editor.pendingLayerEntities()

            if not pending_layer_entities.layerId() in \
                    self._pending_fk_entities:
                self._pending_fk_entities[
                    pending_layer_entities.layerId()] = pending_layer_entities

            else:
                self._pending_fk_entities[pending_layer_entities.layerId()].\
                    merge(pending_layer_entities)

            return True

        else:
            return False

    def on_features_committed(self, layer_id, features):
        """
        Update the related entities with the FK key from the primary spatial
        unit PK.
        :rtype : None
        :param layer_id: int
        :param features:
        """
        if layer_id in self._pending_fk_entities:
            pending_layer_entity = self._pending_fk_entities[layer_id]

            # Get map layer using layer_id
            ref_layer = QgsMapLayerRegistry.instance().mapLayer(layer_id)

            if ref_layer is not None:
                fid_x = ref_layer.fieldNameIndex(
                    pending_layer_entity.featureAttributeName())

                # Show progress dialog for updating the features.
                progress_label = QApplication.translate(
                    "StdmMapToolCreateFeature", "Updating related entities...")
                progress_dlg = QProgressDialog(
                    progress_label, "", 0, len(features),
                    self._iface.mainWindow())
                progress_dlg.setWindowModality(Qt.WindowModal)

                for i, feat in enumerate(features):
                    progress_dlg.setValue(i)
                    uniqueAttr_value = feat.attributes()[fid_x]
                    pending_layer_entity.setPrimaryKey(
                        uniqueAttr_value, int(feat.id()))

                progress_dlg.setValue(len(features))

    def canvasReleaseEvent(self, e):
        """
        Base class override.
        :rtype : None
        :param e: QMouseEvent
        """
        stdm_layer = self.current_vector_layer()

        # Try to set mode from layer type
        if self._mode is CAPTURE_NONE:
            self.set_capture_mode(stdm_layer)

        if not isinstance(stdm_layer, QgsVectorLayer):
            self.notify_not_vector_layer()
            return

        layer_wkb_type = stdm_layer.wkbType()
        provider = stdm_layer.dataProvider()

        if not (provider.capabilities() & QgsVectorDataProvider.AddFeatures):
            QMessageBox.information(self._iface.mainWindow(),
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

        # Spatial unit point capture
        if self._mode is CAPTURE_POINT:
            if stdm_layer.geometry_type() is not QGis.Point:
                QMessageBox.information(self._iface.mainWindow(),
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
            map_point = None
            snap_results = []
            # Point in layer coordinates
            layer_point = None

            op_result, snap_results = self._snapper.snapToBackgroundLayers(
                e.pos())

            if len(snap_results) > 0:
                map_point = self.snap_point_from_results(snap_results, e.pos())

            else:
                map_point = self.toMapCoordinates(e.pos())

            try:
                layer_point = self.toLayerCoordinates(stdm_layer, map_point)
            except QgsCsException:
                QMessageBox.information(self._iface.mainWindow(),
                                        QApplication.translate(
                                            "StdmMapToolCreateFeature",
                                            "Coordinate transform error"),
                                        QApplication.translate(
                                            "StdmMapToolCreateFeature",
                                            "Cannot transform the point to "
                                            "the layer's coordinate system"))
                self._capturing = False
                return

            if layer_wkb_type is QGis.WKBPoint or layer_wkb_type is \
                    QGis.WKBPoint25D:
                self._geometry = QgsGeometry.fromPoint(layer_point)
            elif layer_wkb_type is QGis.WKBMultiPoint or layer_wkb_type is \
                    QGis.WKBMultiPoint25D:
                self._geometry = QgsGeometry.fromMultiPoint(layer_point)

        # Line and polygon capturing
        elif self._mode is CAPTURE_LINE or self._mode is CAPTURE_POLYGON:
            if self._mode is CAPTURE_LINE and stdm_layer.geometry_type() is not \
                    QGis.Line:
                QMessageBox.information(self._iface.mainWindow(),
                                        QApplication.translate(
                                            "StdmMapToolCreateFeature",
                                            "Wrong create tool"),
                                        QApplication.translate(
                                            "StdmMapToolCreateFeature",
                                            "Cannot apply the 'Create Line "
                                            "Feature' tool on this vector "
                                            "layer"))
                return

            if self._mode is CAPTURE_POLYGON and stdm_layer.geometry_type() is\
                    not\
                    QGis.Polygon:
                QMessageBox.information(self._iface.mainWindow(),
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
                    QMessageBox.critical(self._iface.mainWindow(),
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
