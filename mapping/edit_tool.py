"""
/***************************************************************************
Name                 : StdmMapToolEdit
Description          : Base class for all STDM editing map tools.
                       Code has been ported from QGIS source.
Date                 : 1/April/2014
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
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.gui import *
from qgis.core import *

from .utils import pg_layerNamesIDMapping
from .editor_config import spatial_editor_widgets

class StdmMapToolEdit(QgsMapTool):
    '''
    Base class for all STDM editing map tools.
    '''
    def __init__(self,iface):
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        QgsMapTool.__init__(self,self.canvas)
        
        #Snapper object that reads the settings from project and applies to the map canvas
        self._snapper = QgsMapCanvasSnapper(self.canvas)
        
        #Dialog for setting textual attributes of the spatial unit being digitized. 
        self._editorWidget = None
        
        #Initial context menu state of the map canvas
        self._mpCanvasContentMenuPolicy = self.canvas.contextMenuPolicy()
        
    def isEditTool(self):
        return True
    
    def activate(self):
        QgsMapTool.activate(self)
        
        if self.supportsContextMenu():
            self.canvas.setContextMenuPolicy(Qt.CustomContextMenu)
            self.canvas.customContextMenuRequested.connect(self.onMapContextMenuRequested)
        
    def deactivate(self):
        if self.supportsContextMenu():
            self.canvas.setContextMenuPolicy(self._mpCanvasContentMenuPolicy)
            self.canvas.customContextMenuRequested.disconnect(self.onMapContextMenuRequested)
            
        QgsMapTool.deactivate(self)
        
    def onMapContextMenuRequested(self,pnt):
        '''
        Slot raised upon right-clicking the map canvas.
        '''
        editMenu = QMenu(self.iface.mainWindow())
        self.mapContextMenuRequested(pnt,editMenu)
        
        if not editMenu.isEmpty():
            editMenu.exec_(QCursor.pos())
        
    def mapContextMenuRequested(self,pnt,menu):
        '''
        Protected function to be implemented by subclasses for adding edit actions into the context menu.
        Default does nothing.
        '''
        pass
            
    def supportsContextMenu(self):
        '''
        Set whether the map tool supports a custom context menu for additional mapping functionality
        on edit mode.
        To be implemented by sub-classes.
        '''
        return False
    
    def snapPointFromResults(self,snapResults,screenCoords):
        '''
        Extracts a single snapping point from a set of snapping results.
        This is useful for snapping operations that just require a position to snap to and not all the
        snapping results. If the list is empty, the screen coordinates are transformed into map 
        coordinates and returned.
        '''
        if len(snapResults) == 0:
            return self.toMapCoordinates(screenCoords)
        
        else:
            return snapResults[0].snappedVertex
        
    def createRubberBand(self,geomType,alternativeBand=False):
        '''
        Creates a rubber band with the color/line width from the QGIS settings.
        '''
        settings = QSettings()
        rb = QgsRubberBand(self.canvas,geomType)
        rb.setWidth(settings.value("/Qgis/digitizing/line_width",1))
        color = QColor(settings.value("/Qgis/digitizing/line_color_red", 255),\
                       settings.value("/Qgis/digitizing/line_color_green",0), \
                       settings.value("/Qgis/digitizing/line_color_blue", 0))
        
        myAlpha = settings.value("/Qgis/digitizing/line_color_alpha", 200)/255.0
        
        if alternativeBand:
            myAlpha = myAlpha * 0.75
            rb.setLineStyle(Qt.DotLine)
        
        if geomType == QGis.Polygon:
            color.setAlphaF(myAlpha)
            
        rb.setColor(color)
        rb.show()
        
        return rb
    
    def currentVectorLayer(self):
        '''
        Returns the current vector layer of the map canvas or None
        '''
        return self.canvas.currentLayer()
    
    def notifyNotVectorLayer(self):
        '''
        Display a timed message bar noting the active layer is not vector.
        '''
        self.messageEmitted.emit(QApplication.translate("StdmMapToolEdit", "No active vector layer"))
        
    def notifyNotEditableLayer(self):
        '''
        Display a timed message bar noting the active vector layer is not editable.
        '''
        self.messageEmitted.emit(QApplication.translate("StdmMapToolEdit", "Layer not editable"))
        
    def setEditorWidget(self,editorWidget):
        '''
        Set the widget for editing attributing values
        '''
        self._editorWidget = editorWidget
        
    def _configureSpatialEditor(self,layer):
        '''
        Factory method that sets the spatial editor dialog using the configuration specified in the
        editor_config module.
        '''
        layerId = layer.id()
        if layerId in pg_layerNamesIDMapping().reverse:
            tableName = pg_layerNamesIDMapping().reverse[layerId]
            #Get corresponding editor widget from the config
            if tableName in spatial_editor_widgets:
                self._editorWidget = spatial_editor_widgets[tableName]
            
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    