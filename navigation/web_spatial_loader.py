"""
/***************************************************************************
Name                 : WebSpatialLoader
Description          : Class that provides functions for overlaying property
                       boundaries in either a Google Maps Satellite view or
                       OpenStreetMaps
Date                 : 8/July/2014
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
import json

from PyQt4.QtCore import pyqtSignal, QObject, QFile, QUrl, SIGNAL, pyqtSlot,\
    qDebug, QSettings
from PyQt4.QtGui import QColor, QApplication
from PyQt4.QtWebKit import QWebPage
from PyQt4.QtNetwork import QNetworkAccessManager

from settings import get_proxy
from utils import PLUGIN_DIR
from data import STDMDb

from geoalchemy2 import WKBElement

# Layer type enumeration
GMAP_SATELLITE = 2010
OSM = 2011


class OLStyle(object):
    """
    Wrapper for defining the style to be used for
    rendering the property overlay in OpenLayers.
    """

    def __init__(self, style={}):
        """
        Instantiate styling dictionary. This will be
        serialized to a JSON object and passed to
        OpenLayers.
        :param style:
        """
        self._style = style

        settings = QSettings()

        # Use QGIS selection fill color
        qgs_sel_red = settings.value(
            "/Qgis/default_selection_color_red", 255, type=int)
        qgs_sel_green = settings.value(
            "/Qgis/default_selection_color_green", 255, type=int)
        qgs_sel_blue = settings.value(
            "/Qgis/default_selection_color_blue", 0, type=int)
        qgs_sel_alpha = settings.value(
            "/Qgis/default_selection_color_alpha", 255, type=int)

        sel_color = QColor(qgs_sel_red, qgs_sel_green, qgs_sel_blue,
                           qgs_sel_alpha)

        # Set defaults
        self._style["fillColor"] = sel_color.name()
        self._style["fillOpacity"] = 0.5
        self._style["strokeColor"] = "#FE2E64"
        self._style["strokeOpacity"] = 1
        self._style["strokeWidth"] = 1

    def set_fill_color(self, color):
        """
        'color' can be a string or QColor
        :param color:
        """
        if isinstance(color, QColor):
            color = str(color.name())

        self._style["fillColor"] = color

    def set_fill_opacity(self, opacity):
        """
        Set opacity of the fill color.
        Ranges from 0-1.
        :param opacity:
        """
        if opacity < 0 or opacity > 1:
            return

        self._style["fillOpacity"] = opacity

    def set_stroke_color(self, color):
        """
        'color' can be a string or QColor.
        :param color:
        """
        if isinstance(color, QColor):
            color = color.name()

        self._style["strokeColor"] = color

    def set_stroke_opacity(self, opacity):
        """
        Set opacity of the the outline.
        Ranges from 0-1.
        """
        if opacity < 0 or opacity > 1:
            return

        self._style["strokeOpacity"] = opacity

    def set_stroke_width(self, width):
        """
        Set the width of the outline.
        :param width:
        """
        self._style["strokeWidth"] = width

    def set_label_field(self, label_field):
        """
        Set the name of the attribute whose value should be used for
        labeling the property.
        :rtype : str
        :param label_field:
        """
        self._style["label"] = "${%s}" % (label_field,)

    def to_json(self):
        """
        Returns the corresponding style object in JSON format
        :rtype : json
        """
        return json.dumps(self._style)


class WebSpatialLoader(QObject):
    """
    Overlays geometries in either on Google Maps Satellite view or
    OpenStreetMaps on the QWebView control specified.
    """
    _load_error = pyqtSignal(str)
    _load_started = pyqtSignal()
    _load_finished = pyqtSignal(bool)
    _load_progress = pyqtSignal(int)
    _zoom_changed = pyqtSignal(int)

    def __init__(self, web_view, parent=None, style=OLStyle()):
        QObject.__init__(self, parent)
        self._base_html = "spatial_unit_overlay.html"
        self._web_view = web_view
        self._db_session = STDMDb.instance().session

        self._ol_page = ProxyWebPage(self)

        # Property Style
        self._style = style

        # Connect slots
        self._ol_page.loadFinished.connect(self._on_finish_loading)
        self._ol_page.loadProgress.connect(self._on_loading_progress)
        self._ol_page.loadStarted.connect(self._on_start_loading)

    def url(self):
        """
        Returns both the normal and URL paths of the base HTML file to load.
        The HTML file has to be located in the 'html' folder of the plugin.
        :rtype : str
        """
        abs_norm_path = PLUGIN_DIR + "/html/" + self._base_html
        browser_path = "file:///" + abs_norm_path

        return abs_norm_path, browser_path

    def load(self):
        """
        Loads the spatial overlay page into the QWebView.
        This method is only called once on initializing the view. Subsequent
        object calls are made to the 'addOverlay' method.
        """
        if not QFile.exists(self.url()[0]):
            errmsg = QApplication.translate("WebSpatialLoader",
                                            "The source HTML file could not "
                                            "be found.")
            self._load_error.emit(errmsg)

            return

        self._ol_page.mainFrame().load(QUrl(self.url()[1]))
        self._web_view.setPage(self._ol_page)

        receivers = self._ol_page.mainFrame().receivers(
            SIGNAL("javaScriptWindowObjectCleared()"))
        if receivers > 0:
            self._ol_page.mainFrame().\
                javaScriptWindowObjectCleared.disconnect()

        self._ol_page.mainFrame().javaScriptWindowObjectCleared.connect(
            self._populate_js_window_object)

    @pyqtSlot()
    def _on_start_loading(self):
        """
        Propagate the page loading events
        """
        self._load_started.emit()

    @pyqtSlot(bool)
    def _on_finish_loading(self, status):
        """
        Propagate signal
        :rtype : pyqtSignal
        :param status:
        """
        self._load_finished.emit(status)

    @pyqtSlot(int)
    def _on_loading_progress(self, prog):
        """
        Propagate signal
        :param prog:
        :rtype : pyqtSignal
        """
        self._load_progress.emit(prog)

    @pyqtSlot(int)
    def _on_zoom_level_changed(self, level):
        """
        Signal raised when the zoom level of the map changes.
        This signal is only raised in certain circumstances.
        (Enumerate the levels)
        :param level:
        :rtype : pyqtSignal
        """
        self._zoom_changed.emit(level)

    def _set_base_layer(self, layer_type):
        """
        Set the base layer to either Google Maps or OpenStreetMaps
        :param layer_type:
         :rtype : pyqtSignal
        """
        change_base_js = "setBaseLayer(%s)" % (layer_type)
        zoom_level = self._set_js(change_base_js)

        # Raise map zoom changed event
        self._on_zoom_level_changed(zoom_level)

    def set_center(self, x, y, zoom=12):
        """
        Set the center of the map with an optional zoom level
        :param x:
        :param y:
        :param zoom:
        """
        set_center_js = "setCenter(%s,%s,%s)" % (x, y, zoom)
        self._set_js(set_center_js)

    def zoom_to_level(self, level):
        """
        Zoom to a specific level
        :param level:
        """
        zoom_js = "zoom(%s)" % (level)
        zoom_level = self._set_js(zoom_js)

    def zoom_to_map_extents(self, extents):
        """
        Zooms the view to given map extents.
        :param extents: Bounding box containing the extent coordinates.
        :type extents: QgsRectangle
        """
        left = extents.xMinimum()
        bottom = extents.yMinimum()
        right = extents.xMaximum()
        top = extents.yMaximum()

        zoom_to_extents_JS = "zoomToExtents([{0},{1},{2},{3}])".format(
            left, bottom, right, top)
        self._set_js(zoom_to_extents_JS)

    def zoom_to_extents(self):
        """
        Zoom to the boundary extents of the last loaded
        property.
        """
        zoom_to_extents_js = "zoomToSpatialUnitExtent()"
        zoom_level = self._set_js(zoom_to_extents_js)

        # Raise map zoom changed event
        self._on_zoom_level_changed(zoom_level)

    def add_overlay(self, sp_unit, geometry_col, label_field=""):
        """
        Overlay a point/line/polygon onto the baselayer and set the label to
        use for the feature.
        The feature will be transported in GeoJSON format since it is the most
        efficient format for AJAX loading.
        :param sp_unit:
        :param geometry_col:
        :param label_field:
        """
        if sp_unit is None:
            return

        # Set the name of the field to use for labeling
        # self._style.setLabelField(labelfield)

        # Update the style of the property on each overlay operation
        self._update_layer_style()

        # Set label object
        label_js_object = "null"
        if hasattr(sp_unit, label_field):
            lbl_val = getattr(sp_unit, label_field)
            label_js_object = "{'%s':'%s'}" % (label_field, str(lbl_val))

        # Reproject to web mercator
        # TODO: Remove hardcode of geometry field name
        geom = getattr(sp_unit, geometry_col)
        sp_unit_wkb = self._db_session.scalar(geom.ST_Transform(900913))

        web_geom = WKBElement(sp_unit_wkb)
        sp_unit_geo_json = self._db_session.scalar(web_geom.ST_AsGeoJSON())

        overlay_js = "drawSpatialUnit('%s',%s);" % (
            sp_unit_geo_json, label_js_object)
        zoom_level = self._set_js(overlay_js)

        # Raise map zoom changed event
        self._on_zoom_level_changed(zoom_level)

    def remove_overlay(self):
        """
        Removes all spatial unit overlays.
        """
        overlay_rem_js = "clearOverlays()"
        self._set_js(overlay_rem_js)

    def set_style(self, style):
        """
        Set the style of the property
        :param style:
        """
        self._style = style

    def _update_layer_style(self):
        """
        Updates the style of the property vector layer
        in the map.
        """
        ol_style = self._style.to_json()
        update_style_js = "setSpatialUnitStyle(%s)" % (ol_style,)
        self._set_js(update_style_js)

    def _set_js(self, javascript):
        """
        Set the JavaScript code to be executed.
        :rtype : object
        :param javascript:
        """
        frame = self._ol_page.mainFrame()

        return frame.evaluateJavaScript(javascript)

    def _populate_js_window_object(self):
        self._ol_page.mainFrame().addToJavaScriptWindowObject(
            "sp_loader", self)


class ProxyWebPage(QWebPage):
    """
    Custom web page implementation since we need to use
    the QGIS proxy settings if a proxy has been specified.
    """

    def __init__(self, parent=None):
        QWebPage.__init__(self, parent)
        self._manager = None

        # Set proxy in webpage
        proxy = get_proxy()

        if proxy is not None:
            self._manager = QNetworkAccessManager()
            self._manager.setProxy(proxy)
            self.setNetworkAccessManager(self._manager)

    def javaScriptConsoleMessage(self, message, line_number, source_id):
        # For debugging purposes
        """
        :param message:
        :param line_number:
        :param source_id:
        """
        log_entry = "%s[%d]: %s" % (source_id, line_number, message)
        qDebug(log_entry)
        '''
        Log console messages to file for debugging purposes.

        #TODO: Store path in registry
        file = "D:/Logs.txt"

        f = open(file, 'w')
        f.write(logEntry)
        if logEntry[-1:] != "\n":
            f.write("\n")
        f.flush()
        '''
