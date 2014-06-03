"""
/***************************************************************************
Name                 : Property Browser
Description          : Class that provides functions for overlaying property
                       boundaries in either a Google Maps Satellite view or 
                       OpenStreetMaps.
Date                 : 8/July/2013 
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
import os.path

from stdm.settings import getProxy
from stdm.utils import PLUGIN_DIR
from stdm.data import STDMDb

from geoalchemy2 import WKBElement 

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from PyQt4.QtNetwork import *

#Layer type enumeration
GMAP_SATELLITE = 2010
OSM = 2011

class OLStyle(object):
    '''
    Wrapper for defining the style to be used for
    rendering the property overlay in OpenLayers.
    '''
    def __init__(self):
        '''
        Instantiate styling dictionary. This will be
        serialized to a JSON object and passed to
        OpenLayers.
        '''
        self.style = {}
        
        #Set defaults
        self.style["fillColor"] = "#00FF00"
        self.style["fillOpacity"] = 0.4
        self.style["strokeColor"] = "#FE2E64"
        self.style["strokeOpacity"] = 1
        self.style["strokeWidth"] = 1
        self.style["label"] = "${id}"
        self.style["labelOutlineColor"] = "#FFFFFF"
        self.style["labelOutlineWidth"] = 3

    def setFillColor(self,color):
        '''
        'color' can be a string or QColor
        '''
        if isinstance(color,QColor):
            color = str(color.name())
        self.style["fillColor"] = color
        
    def setFillOpacity(self,opacity):
        '''
        Set opacity of the fill color.
        Ranges from 0-1.
        '''
        self.style["fillOpacity"] = opacity
        
    def setStrokeColor(self,color):
        '''
        'color' can be a string or QColor.
        '''
        if isinstance(color,QColor):
            color = str(color.name())
        self.style["strokeColor"] = color
        
    def setStrokeOpacity(self,opacity):
        '''
        Set opacity of the the outline.
        Ranges from 0-1.
        '''
        self.style["strokeOpacity"] = opacity
        
    def setStrokeWidth(self,width):
        '''
        Set the width of the outline.
        '''
        self.style["strokeWidth"] = width
        
    def setLabelField(self,labelField):
        '''
        Set the name of the attribute whose value should be 
        used for labeling the property.
        '''
        self.style["label"] = "${%s}"%(labelField,)
        
    def toJson(self):
        '''
        Returns the corresponding style object in JSON format
        '''
        import json
        return json.dumps(self.style)

class PropertyBrowser(QObject):
    '''
    Overlays property bounds in either on Google Maps Satellite view or 
    OpenStreetMaps on the QWebView control specified.
    '''
    def __init__(self,webview,parent = None,style = OLStyle()):
        '''
        Initialize 
        '''
        QObject.__init__(self,parent)
        self.baseHTML = "property_overlay.html"
        self.webview = webview
        self.dbSession = STDMDb.instance().session
        
        self.olPage = OLWebPage(self)
        
        #Property Style
        self._style = style            
        
        #Connect slots
        QObject.connect(self.olPage, SIGNAL("loadFinished(bool)"),self.onFinishLoading)
        QObject.connect(self.olPage, SIGNAL("loadProgress(int)"),self.onLoadingProgress)
        QObject.connect(self.olPage, SIGNAL("loadStarted()"),self.onStartLoading)
        
    def url(self):
        '''
        Returns both the normal and URL paths of the base HTML file to load. 
        The HTML file has to be located in the 'html' folder of the plugin.       
        '''                
        absNormPath = PLUGIN_DIR + "/html/" + self.baseHTML
        browserPath = "file:///" + absNormPath
        
        return absNormPath, browserPath
    
    def load(self):
        '''
        Loads the property page into the QWebView.
        This method is only called once on initializing the view. Subsequent object calls
        are made to the addOverlay method.
        '''  
        if not QFile.exists(self.url()[0]):
            errmsg = QApplication.translate("PropertyBrowser", "The source HTML file could not be found.")            
            self.emit(SIGNAL("loadError(QString)"), errmsg)
            return 
                    
        self.olPage.mainFrame().load(QUrl(self.url()[1]))  
        self.webview.setPage(self.olPage)               
        
    def onStartLoading(self):
        '''
        Propagate the page loading events
        '''
        self.emit(SIGNAL("loadStarted()"))
        
    def onFinishLoading(self,status):
        '''
        Propagate event/signal
        '''
        self.emit(SIGNAL("loadFinished(bool)"),status)
        
    def onLoadingProgress(self,prog):
        '''
        Propagate event
        '''    
        self.emit(SIGNAL("loadProgress(int)"),prog)
        
    def onZoomLevelChanged(self,level):
        '''
        Signal raised when the zoom level of the map changes.
        This signal is only raised in certain circumstances.
        (Enumerate the levels)
        '''
        self.emit(SIGNAL("zoomChanged(int)"),level)
    
    def setBaseLayer(self,layertype):
        '''
        Set the base layer to either Google Maps or OpenStreetMaps
        '''        
        changeBaseJS = "setBaseLayer(%s)"%(layertype)
        zoomLevel,ok = self._setJS(changeBaseJS).toInt()
        
        #Raise map zoom changed event
        self.onZoomLevelChanged(zoomLevel)
        
    def setCenter(self,x,y,zoom=12):
        '''
        Set the center of the map with an optional zoom level
        '''
        setCenterJS = "setCenter(%s,%s,%s)"%(x,y,zoom)
        self._setJS(setCenterJS)
        
    def zoomTo(self,level):
        '''
        Zoom to a specific level
        '''
        zoomJS = "zoom(%s)"%(level)
        zoomLevel,ok = self._setJS(zoomJS).toInt()
        
    def zoomToPropertyExtents(self):
        '''
        Zoom to the boundary extents of the last loaded
        property.
        '''
        zoomToExtentsJS = "zoomToPropertyExtent()"
        zoomLevel,ok = self._setJS(zoomToExtentsJS).toInt()
        
        #Raise map zoom changed event
        self.onZoomLevelChanged(zoomLevel)
    
    def addOverlay(self,property,labelfield = ""):
        '''
        Overlay a polygon onto the baselayer and set the label to use for the
        polygon.
        The feature will be transported in GeoJSON format since it is the most 
        efficient format for AJAX loading.
        '''
        if property is None:return
        
        #Set the name of the field to use for labeling        
        self._style.setLabelField(labelfield)
        
        #Update the style of the property on each overlay operation
        self._updateLayerStyle()
        
        #Set label object
        labelJSObject = "null"
        if hasattr(property,labelfield):
            propVal = getattr(property,labelfield)
            labelJSObject = "{'%s':'%s'}"%(labelfield,str(propVal))
        
        #Reproject to web mercator
        prop_wkb = self.dbSession.scalar(property.geom.ST_Transform(900913))  
        web_geom = WKBElement(prop_wkb)
        prop_geo_json = self.dbSession.scalar(web_geom.ST_AsGeoJSON())
        
        overlayJS = "drawProperty('%s',%s);"%(prop_geo_json,labelJSObject)                
        zoomLevel,ok = self._setJS(overlayJS).toInt()
        
        #Raise map zoom changed event
        self.onZoomLevelChanged(zoomLevel)
    
    def removeOverlay(self):
        '''
        Removes all property overlays
        '''
        overlayRemJS = ""
        self._setJS(overlayRemJS)
    
    def setStyle(self,style):
        '''
        Set the style of the property
        '''
        self._style = style
        
    def _updateLayerStyle(self):
        '''
        Updates the style of the property vector layer
        in the map.
        '''
        olStyle = self._style.toJson()
        updateStyleJS = "setPropertyStyle(%s)"%(olStyle,)
        self._setJS(updateStyleJS)
        
    def _setJS(self,javascript):
        '''
        Set the JavaScript code to be executed.
        '''
        frame = self.olPage.mainFrame()
        return frame.evaluateJavaScript(javascript)
        
class OLWebPage(QWebPage):
    '''
    We define a custom web page implementation since we need to use
    the QGIS proxy settings if a proxy has been specified.
    '''
    def __init__(self,parent=None):
        QWebPage.__init__(self,parent)
        self._manager = None
        
        #Set proxy in webpage
        proxy = getProxy()
        
        if not proxy is None:
            self._manager = QNetworkAccessManager()
            self._manager.setProxy(proxy)
            self.setNetworkAccessManager(self._manager)
            
    def javaScriptConsoleMessage(self, message, lineNumber, sourceID):    
        logEntry = "%s[%d]: %s" % (sourceID, lineNumber, message)
        qDebug(logEntry)
        
        '''
        Log console messages to file.
        This is meant for debugging purposes only.
        '''
        file = "D:/Logs.txt"
        f = open(file,'w')
        f.write(logEntry)
        if logEntry[-1:] != "\n":
            f.write("\n")
        f.flush()

        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
