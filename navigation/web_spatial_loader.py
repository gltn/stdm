"""
/***************************************************************************
Name                 : WebSpatialLoader
Description          : Class that provides functions for overlaying property
                       boundaries in either a Google Maps Satellite view or 
                       OpenStreetMaps.
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
import os.path

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from PyQt4.QtNetwork import *

from qgis.core import *

from stdm.settings import getProxy
from stdm.utils import PLUGIN_DIR
from stdm.data.database import STDMDb

from geoalchemy2 import WKBElement 

#Layer type enumeration
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
        """
        self.style = style

        settings = QSettings()
        
        #Use QGIS selection fill color
        qgs_sel_red = settings.value("/Qgis/default_selection_color_red", 255, type=int)
        qgs_sel_green = settings.value("/Qgis/default_selection_color_green", 255, type=int)
        qgs_sel_blue = settings.value("/Qgis/default_selection_color_blue", 0, type=int)
        qgs_sel_alpha = settings.value("/Qgis/default_selection_color_alpha", 255, type=int)

        sel_color = QColor(qgs_sel_red, qgs_sel_green, qgs_sel_blue,
                                         qgs_sel_alpha)

        #Set defaults
        self.style["fillColor"] = sel_color.name()
        self.style["fillOpacity"] = 0.5
        self.style["strokeColor"] = "#FE2E64"
        self.style["strokeOpacity"] = 1
        self.style["strokeWidth"] = 1

    def setFillColor(self,color):
        """
        'color' can be a string or QColor
        """
        if isinstance(color,QColor):
            color = str(color.name())

        self.style["fillColor"] = color
        
    def setFillOpacity(self, opacity):
        """
        Set opacity of the fill color.
        Ranges from 0-1.
        """
        if opacity < 0 or opacity > 1:
            return

        self.style["fillOpacity"] = opacity
        
    def setStrokeColor(self, color):
        """
        'color' can be a string or QColor.
        """
        if isinstance(color,QColor):
            color = color.name()

        self.style["strokeColor"] = color
        
    def setStrokeOpacity(self, opacity):
        """
        Set opacity of the the outline.
        Ranges from 0-1.
        """
        if opacity < 0 or opacity > 1:
            return

        self.style["strokeOpacity"] = opacity
        
    def setStrokeWidth(self, width):
        """
        Set the width of the outline.
        """
        self.style["strokeWidth"] = width
        
    def setLabelField(self, label_field):
        """
        Set the name of the attribute whose value should be 
        used for labeling the property.
        """
        self.style["label"] = "${%s}"%(label_field,)
        
    def toJson(self):
        """
        Returns the corresponding style object in JSON format
        """
        import json
        return json.dumps(self.style)

class WebSpatialLoader(QObject):
    """
    Overlays geometries in either on Google Maps Satellite view or
    OpenStreetMaps on the QWebView control specified.
    """
    loadError = pyqtSignal(str)
    loadStarted = pyqtSignal()
    loadFinished = pyqtSignal(bool)
    loadProgress = pyqtSignal(int)
    zoomChanged = pyqtSignal(int)

    def __init__(self, webview, parent=None, style=OLStyle()):
        QObject.__init__(self, parent)
        self._base_html = "spatial_unit_overlay.html"
        self.webview = webview
        self.dbSession = STDMDb.instance().session
        
        self.olPage = ProxyWebPage(self)
        
        #Property Style
        self._style = style            
        
        #Connect slots
        self.olPage.loadFinished.connect(self.onFinishLoading)
        self.olPage.loadProgress.connect(self.onLoadingProgress)
        self.olPage.loadStarted.connect(self.onStartLoading)
        
    def url(self):
        """
        Returns both the normal and URL paths of the base HTML file to load.
        The HTML file has to be located in the 'html' folder of the plugin.
        """
        abs_norm_path = PLUGIN_DIR + "/html/" + self._base_html
        browser_path = "file:///" + abs_norm_path
        
        return abs_norm_path, browser_path
    
    def load(self):
        """
        Loads the spatial overlay page into the QWebView.
        This method is only called once on initializing the view. Subsequent object calls
        are made to the 'addOverlay' method.
        """
        if not QFile.exists(self.url()[0]):
            errmsg = QApplication.translate("WebSpatialLoader",
                                            "The source HTML file could not be found.")
            self.loadError.emit(errmsg)

            return

        self.olPage.mainFrame().load(QUrl(self.url()[1]))
        self.webview.setPage(self.olPage)

        receivers = self.olPage.mainFrame().receivers(SIGNAL("javaScriptWindowObjectCleared()"))
        if receivers > 0:
            self.olPage.mainFrame().javaScriptWindowObjectCleared.disconnect()

        self.olPage.mainFrame().javaScriptWindowObjectCleared.connect(
            self._populate_js_window_object
        )

    @pyqtSlot()
    def onStartLoading(self):
        """
        Propagate the page loading events
        """
        self.loadStarted.emit()

    @pyqtSlot(bool)
    def onFinishLoading(self, status):
        """
        Propagate signal
        """
        self.loadFinished.emit(status)

    @pyqtSlot(int)
    def onLoadingProgress(self, prog):
        """
        Propagate signal
        """
        self.loadProgress.emit(prog)

    @pyqtSlot(int)
    def onZoomLevelChanged(self, level):
        """
        Signal raised when the zoom level of the map changes.
        This signal is only raised in certain circumstances.
        (Enumerate the levels)
        """
        self.zoomChanged.emit(level)
    
    def setBaseLayer(self,layertype):
        """
        Set the base layer to either Google Maps or OpenStreetMaps
        """
        changeBaseJS = "setBaseLayer(%s)" % (layertype)
        zoomLevel = self._setJS(changeBaseJS)
        
        #Raise map zoom changed event
        self.onZoomLevelChanged(zoomLevel)
        
    def setCenter(self, x, y, zoom=12):
        """
        Set the center of the map with an optional zoom level
        """
        setCenterJS = "setCenter(%s,%s,%s)" % (x,y,zoom)
        self._setJS(setCenterJS)
        
    def zoom_to_level(self,level):
        """
        Zoom to a specific level
        """
        zoomJS = "zoom(%s)"%(level)
        zoomLevel = self._setJS(zoomJS)

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

        zoom_to_extents_JS = "zoomToExtents([{0},{1},{2},{3}])".format(left,
                                            bottom, right, top)
        self._setJS(zoom_to_extents_JS)
        
    def zoom_to_extents(self):
        """
        Zoom to the boundary extents of the last loaded
        property.
        """
        zoomToExtentsJS = "zoomToSpatialUnitExtent()"
        zoomLevel = self._setJS(zoomToExtentsJS)
        
        #Raise map zoom changed event
        self.onZoomLevelChanged(zoomLevel)
    
    def add_overlay(self, sp_unit, geometry_col, labelfield=""):
        """
        Overlay a point/line/polygon onto the baselayer and set the label to use for the
        feature.
        The feature will be transported in GeoJSON format since it is the most
        efficient format for AJAX loading.
        """
        if sp_unit is None:
            return
        
        #Set the name of the field to use for labeling        
        #self._style.setLabelField(labelfield)
        
        #Update the style of the property on each overlay operation
        self._updateLayerStyle()
        
        #Set label object
        label_js_object = "null"
        if hasattr(sp_unit, labelfield):
            lbl_val = getattr(sp_unit, labelfield)
            label_js_object = "{'%s':'%s'}" % (labelfield, str(lbl_val))
        
        #Reproject to web mercator
        #TODO: Remove hardcode of geometry field name
        geom = getattr(sp_unit, geometry_col)
        sp_unit_wkb = self.dbSession.scalar(geom.ST_Transform(900913))

        web_geom = WKBElement(sp_unit_wkb)
        sp_unit_geo_json = self.dbSession.scalar(web_geom.ST_AsGeoJSON())
        
        overlay_js = "drawSpatialUnit('%s',%s);" % (sp_unit_geo_json, label_js_object)
        zoom_level = self._setJS(overlay_js)
        
        #Raise map zoom changed event
        self.onZoomLevelChanged(zoom_level)
    
    def removeOverlay(self):
        """
        Removes all spatial unit overlays.
        """
        overlayRemJS = "clearOverlays()"
        self._setJS(overlayRemJS)
    
    def setStyle(self, style):
        """
        Set the style of the property
        """
        self._style = style
        
    def _updateLayerStyle(self):
        """
        Updates the style of the property vector layer
        in the map.
        """
        olStyle = self._style.toJson()
        updateStyleJS = "setSpatialUnitStyle(%s)" % (olStyle,)
        self._setJS(updateStyleJS)
        
    def _setJS(self, javascript):
        """
        Set the JavaScript code to be executed.
        """
        frame = self.olPage.mainFrame()

        return frame.evaluateJavaScript(javascript)

    def _populate_js_window_object(self):
        self.olPage.mainFrame().addToJavaScriptWindowObject("sp_loader",
                                                            self)
        
class ProxyWebPage(QWebPage):
    """
    Custom web page implementation since we need to use
    the QGIS proxy settings if a proxy has been specified.
    """
    def __init__(self, parent=None):
        QWebPage.__init__(self, parent)
        self._manager = None
        
        #Set proxy in webpage
        proxy = getProxy()

        if not proxy is None:
            self._manager = QNetworkAccessManager()
            self._manager.setProxy(proxy)
            self.setNetworkAccessManager(self._manager)
            
    def javaScriptConsoleMessage(self, message, lineNumber, sourceID):
        #For debugging purposes
        logEntry = "%s[%d]: %s" % (sourceID, lineNumber, message)
        qDebug(logEntry)
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

        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
