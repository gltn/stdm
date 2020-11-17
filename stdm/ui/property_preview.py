"""
/***************************************************************************
Name                 : Property Preview Widget
Description          : Tab widget for previewing a single spatial unit overlaid
                       on either a local map or web sources (Google Maps or
                       OpenLayers).
Date                 : 10/October/2013
copyright            : (C) 2013 by John Gitau
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
import re

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QTabWidget,
    QApplication,
    QMessageBox
)
from qgis.core import (
    QgsFeature,
    QgsGeometry,
    QgsProject,
    QgsVectorLayer
)
from qgis.gui import (
    QgsHighlight
)

from stdm.data.database import STDMDb
from stdm.data.pg_utils import (
    pg_table_exists,
    qgsgeometry_from_wkbelement
)
from stdm.navigation.web_spatial_loader import (
    WebSpatialLoader,
    GMAP_SATELLITE,
    OSM
)
from stdm.settings.registryconfig import (
    selection_color
)
from stdm.ui.gui_utils import GuiUtils
from stdm.ui.notification import (
    ERROR
)
from stdm.ui.spatial_unit_manager import SpatialUnitManagerDockWidget

WIDGET, BASE = uic.loadUiType(
    GuiUtils.get_ui_file_path('ui_property_preview.ui'))


class SpatialPreview(WIDGET, BASE):
    """
    Widget for previewing spatial unit on either local map or web source.
    """

    def __init__(self, parent=None, iface=None):
        QTabWidget.__init__(self, parent)
        self.setupUi(self)

        self.local.setIcon(GuiUtils.get_icon('local.png'))
        self.web.setIcon(GuiUtils.get_icon('web.png'))

        self._notif_bar = None
        self._ol_loaded = False
        self._overlay_layer = None
        self.sel_highlight = None
        self.memory_layer = None
        self._db_session = STDMDb.instance().session

        self.set_iface(iface)

        # Web config
        self._web_spatial_loader = WebSpatialLoader(self.spatial_web_view, self)

        # Connect signals
        self._web_spatial_loader.loadError.connect(self.on_spatial_browser_error)
        self._web_spatial_loader.loadProgress.connect(self.on_spatial_browser_loading)
        self._web_spatial_loader.loadFinished.connect(self.on_spatial_browser_finished)
        self._web_spatial_loader.zoomChanged.connect(self.on_map_zoom_level_changed)
        self.rbGMaps.toggled.connect(self.on_load_GMaps)
        self.rbOSM.toggled.connect(self.on_load_OSM)
        self.zoomSlider.sliderReleased.connect(self.on_zoom_changed)
        self.btnResetMap.clicked.connect(self.on_reset_web_map)
        self.btnSync.clicked.connect(self.on_sync_extents)
        QgsProject.instance().layersWillBeRemoved.connect(self._on_overlay_to_be_removed)

    def set_iface(self, iface):
        self._iface = iface
        self.local_map.set_iface(iface)

    def set_notification_bar(self, notif_bar):
        """
        Set notification widget.
        :param notif_bar: Notification widget.
        """
        self._notif_bar = notif_bar

    def notification_bar(self):
        """
        :return: Currently configured notification bar.
        """
        return self._notif_bar

    def _insert_notification(self, msg, level, clear_first=True):
        if self._notif_bar is None:
            return

        if clear_first:
            self._notif_bar.clear()

        self._notif_bar.insertNotification(msg, level)

    def iface(self):
        return self._iface

    def _setDefaults(self):
        """
        Set default settings
        """
        self.set_canvas_background_color(self.canvasBgColor)

    def set_canvas_background_color(self, color):
        """
        Set the background color of the map canvas
        """
        self.localMap.setCanvasColor(color)
        self.canvasBgColor = color

    def refresh_canvas_layers(self, process_events=False):
        """
        Reload map layers in the viewer canvas.
        """
        self.local_map.refresh_layers()

    def load_web_map(self):
        """
        Loads the web map into the view using canvas extents if there
        are existing layers in the map canvas.
        """
        if not self._ol_loaded:
            self._web_spatial_loader.load()

    def _create_vector_layer(self, geom_type, prj_code):
        """
        Creates/resets the internal vector layer that will be used to draw
        the spatial unit overlays.
        :param geom_type: Geometry type
        :type geom_type: str
        :param prj_code: EPSG code
        :type prj_code: int
        """
        self._overlay_layer = QgsVectorLayer(
            "{0}?crs=epsg:{1!s}&field=lbname:string(20)&index=yes".format(geom_type,
                                                                          prj_code),
            "view_str_spatial_unit",
            "memory")

    def draw_spatial_unit(self, spatial_unit, model):
        """
        Draw geometry of the given model in the respective local and web views.
        :param model: Source model whose geometry will be drawn.
        :type model: object
        :param clear_existing: Clears any existing features prior to adding the
        new features.
        :type clear_existing: bool
        """
        if model is None:
            msg = QApplication.translate("SpatialPreview",
                                         "Data model is empty, the spatial "
                                         "unit cannot be rendered.")
            QMessageBox.critical(self,
                                 QApplication.translate(
                                     "SpatialPreview",
                                     "Spatial Unit Preview"),
                                 msg)

            return

        table_name = spatial_unit.name
        if not pg_table_exists(table_name):
            msg = QApplication.translate("SpatialPreview",
                                         "The spatial unit data source could "
                                         "not be retrieved, the feature cannot "
                                         "be rendered.")
            QMessageBox.critical(
                self,
                QApplication.translate(
                    "SpatialPreview",
                    "Spatial Unit Preview"),
                msg
            )

            return

        sp_unit_manager = SpatialUnitManagerDockWidget(self.iface())
        spatial_cols = sp_unit_manager.geom_columns(spatial_unit)

        geom, geom_col = None, ""
        sc_obj = None
        for sc in spatial_cols:

            db_geom = getattr(model, sc.name)
            # Use the first non-empty geometry
            # value in the collection
            if not db_geom is None:
                sc_obj = sc
                geom_col = sc.name
                geom = db_geom
        QApplication.processEvents()

        lyr = sp_unit_manager.geom_col_layer_name(
            table_name, sc_obj
        )

        sp_unit_manager.add_layer_by_name(lyr)

        if geom is not None:
            self.highlight_spatial_unit(
                spatial_unit, geom, self.local_map.canvas
            )
            self._web_spatial_loader.add_overlay(
                model, geom_col
            )

    def clear_sel_highlight(self):
        """
        Removes sel_highlight from the canvas.
        :return:
        """
        if self.sel_highlight is not None:
            self.sel_highlight = None

    def get_layer_source(self, layer):
        """
        Get the layer table name if the source is from the database.
        :param layer: The layer for which the source is checked
        :type QGIS vectorlayer
        :return: String or None
        """
        source = layer.source()
        vals = dict(re.findall('(\S+)="?(.*?)"? ', source))
        try:
            table = vals['table'].split('.')
            table_name = table[1].strip('"')
            return table_name
        except KeyError:
            return None

    def spatial_unit_layer(self, spatial_unit, active_layer):
        """
        Check whether the layer is parcel layer or not.
        :param active_layer: The layer to be checked
        :type QGIS vectorlayer
        :return: Boolean
        """
        if self.active_layer_check():
            layers = self.iface().legendInterface().layers()

            for layer in layers:
                layer_source = self.get_layer_source(layer)
                if layer_source == spatial_unit.name:
                    self.iface().setActiveLayer(layer)
                    return True

            not_sp_msg = QApplication.translate(
                'SpatialPreview',
                'You have selected a non-spatial_unit layer. '
                'Please select a spatial unit layer to preview.'
            )
            QMessageBox.information(
                self._iface.mainWindow(),
                "Error",
                not_sp_msg
            )

    def active_layer_check(self):
        """
        Check if there is active layer and if not, displays
        a message box to select a parcel layer.
        :return:
        """
        active_layer = self._iface.activeLayer()
        if active_layer is None:
            no_layer_msg = QApplication.translate(
                'SpatialPreview',
                'Please add a spatial unit layer '
                'to preview the spatial unit.'
            )
            QMessageBox.critical(
                self._iface.mainWindow(),
                "Error",
                no_layer_msg
            )
            return False
        else:
            return True

    def _add_geom_to_map(self, geom):

        if self._overlay_layer is None:
            return

        geom_func = geom.ST_AsText()
        geom_wkt = self._db_session.scalar(geom_func)

        dp = self._overlay_layer.dataProvider()

        feat = QgsFeature()
        qgis_geom = QgsGeometry.fromWkt(geom_wkt)
        feat.setGeometry(g)
        dp.addFeatures([feat])

        self._overlay_layer.updateExtents()

        return qgis_geom.boundingBox()

    def highlight_spatial_unit(
            self, spatial_unit, geom, map_canvas
    ):
        layer = self._iface.activeLayer()
        map_canvas.setExtent(layer.extent())
        map_canvas.refresh()

        if self.spatial_unit_layer(spatial_unit, layer):

            self.clear_sel_highlight()

            qgis_geom = qgsgeometry_from_wkbelement(geom)

            self.sel_highlight = QgsHighlight(
                map_canvas, qgis_geom, layer
            )
            rgba = selection_color()
            self.sel_highlight.setFillColor(rgba)

            self.sel_highlight.setWidth(3)
            self.sel_highlight.show()

            extent = qgis_geom.boundingBox()
            extent.scale(1.5)
            map_canvas.setExtent(extent)
            map_canvas.refresh()
        else:
            return

    def remove_preview_layer(self, layer, name):
        """
        Removes the preview layer from legend.
        :param layer: The preview polygon layer to be removed.
        :param name: The name of the layer to be removed.
        :return: None
        """
        if layer is not None:
            for lyr in QgsProject.instance().mapLayers().values():
                if lyr.name() == name:
                    id = lyr.id()
                    QgsProject.instance().removeMapLayer(id)

    def delete_local_features(self, feature_ids=[]):
        """
        Removes features in the local map overlay.
        """
        del_status = False

        if not self._overlay_layer is None:
            if len(feature_ids) == 0:
                feature_ids = self._overlay_layer.allFeatureIds()

            del_status = self._overlay_layer.dataProvider().deleteFeatures(feature_ids)

        return del_status

    def remove_layer(self):
        """
        Removes both the local and web layers.
        """
        if not self._overlay_layer is None:
            QgsProject.instance().layerTreeRoot().removeLayer(self._overlay_layer)

            # Clear web overlays
            self._web_spatial_loader.removeOverlay()

            self._overlay_layer = None

    def _on_overlay_to_be_removed(self, layers_ids):
        """
        Resets the local layer variable and removes the web overlay.
        """
        if not self._overlay_layer is None:
            if self._overlay_layer.id() in layers_ids:
                self.remove_layer()

    def on_spatial_browser_error(self, err):
        """
        Slot raised when an error occurs when loading items in the property browser
        """
        self._insert_notification(err, ERROR)

    def on_spatial_browser_loading(self, progress):
        """
        Slot raised when the property browser is loading.
        Displays the progress of the page loading as a percentage.
        """
        if progress <= 0 or progress >= 100:
            self.lblInfo.setText("")
            self.lblInfo.setVisible(False)

        else:
            self.lblInfo.setVisible(True)
            self.lblInfo.setText("Loading...%d%%)" % (progress))

    def on_spatial_browser_finished(self, status):
        """
        Slot raised when the property browser finishes loading the content
        """
        if status:
            if len(self.local_map.canvas_layers()) > 0:  # and not self._ol_loaded:
                self.on_sync_extents()

            self._ol_loaded = True
            # self._overlay_spatial_unit()

        else:
            msg = QApplication.translate("SpatialPreview",
                                         "Error: Spatial unit cannot be loaded.")
            self._insert_notification(msg, ERROR)

    def on_zoom_changed(self):
        """
        Slot raised when the zoom value in the slider changes.
        This is only raised once the user releases the slider with the mouse.
        """
        zoom = self.zoomSlider.value()
        self._web_spatial_loader.zoom_to_level(zoom)

    def on_load_GMaps(self, state):
        """
        Slot raised when a user clicks to set Google Maps Satellite
        as the base layer
        """
        if state:
            self._web_spatial_loader.setBaseLayer(GMAP_SATELLITE)

    def on_load_OSM(self, state):
        """
        Slot raised when a user clicks to set OSM as the base layer
        """
        if state:
            self._web_spatial_loader.setBaseLayer(OSM)

    def on_map_zoom_level_changed(self, level):
        """
        Slot which is raised when the zoom level of the map changes.
        """
        self.zoomSlider.setValue(level)

    def on_reset_web_map(self):
        """
        Slot raised when the user clicks to reset the property
        location in the map.
        """
        self._web_spatial_loader.zoom_to_extents()

    def on_sync_extents(self):
        """
        Slot raised to synchronize the webview extents with those of the
        local map canvas.
        """
        if len(self.local_map.canvas_layers()) > 0:  # and self._ol_loaded:
            curr_extent = self.map_extents()
            self._web_spatial_loader.zoom_to_map_extents(curr_extent)

    def map_extents(self):
        """
        :returns: Current extents of the local map.
        :rtype: QgsRectangle
        """
        return self.local_map.extent()

    def canvas_zoom_to_extent(self, extent):
        self.local_map.canvas.setExtent(extent)
