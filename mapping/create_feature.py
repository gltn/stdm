"""
/***************************************************************************
Name                 : StdmMapToolCreateFeature
Description          : Map tool for creating spatial units, represented either
                       as a point, line or polygon.
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

from stdm.ui import SpatialCoordinatesEditor
from .capture_tool import StdmMapToolCapture,CAPTURE_LINE,CAPTURE_NONE,CAPTURE_POINT, \
CAPTURE_POLYGON
from .edit_tool import StdmMapToolEdit

__all__ = ["StdmMapToolCreateFeature"]

class StdmMapToolCreateFeature(StdmMapToolCapture):
    '''
    Map tool for creating spatial units.
    '''
    def __init__(self,iface):
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        StdmMapToolCapture.__init__(self, self.iface)
        
        #Store the geometry of the sketch
        self._geometry = None
        
        #Container for pending entities from foreign key mappers
        self._pendingFKEntities = {}
        
    def activate(self):
        if self.canvas.isDrawing():
            return
        
        StdmMapToolEdit.activate(self)
        
    def mapContextMenuRequested(self,pnt,menu):
        '''
        Add actions to the editing context menu.
        '''
        self.addXYAction = QAction(QApplication.translate("StdmMapToolCreateFeature","Add X,Y Vertex..."), \
                                   self.iface.mainWindow())
        self.cancelSketchAction = QAction(QApplication.translate("StdmMapToolCreateFeature","Cancel Sketch"), \
                                   self.iface.mainWindow())
        self.finishSketchAction = QAction(QApplication.translate("StdmMapToolCreateFeature","Finish Sketch"), \
                                   self.iface.mainWindow())
        
        if not self._capturing:
            self.finishSketchAction.setEnabled(False)
            self.cancelSketchAction.setEnabled(False)
            
        #Connect signals
        self.addXYAction.triggered.connect(self.onAddXY)
        self.finishSketchAction.triggered.connect(self.onFinishSketch)
        self.cancelSketchAction.triggered.connect(self.stopCapturing)
        
        menu.addAction(self.addXYAction)
        menu.addSeparator()
        menu.addAction(self.finishSketchAction)
        menu.addAction(self.cancelSketchAction)
        
    def supportsContextMenu(self):
        '''
        This map tool supports an editing context menu.
        '''
        return True
    
    def onAddXY(self):
        '''
        Slot raised to show the coordinates point editor for manually entering
        the X, Y coordinate values. 
        '''
        stdmLayer = self.currentVectorLayer()
        
        #Try to set mode from layer type
        if self._mode == CAPTURE_NONE:
            self.setCaptureMode(stdmLayer)
        
        if not isinstance(stdmLayer,QgsVectorLayer):
            self.notifyNotVectorLayer()
            return
        
        layerWKBType = stdmLayer.wkbType()
        provider = stdmLayer.dataProvider()
        
        if not (provider.capabilities() & QgsVectorDataProvider.AddFeatures):
            QMessageBox.information(self.iface.mainWindow(), \
                                    QApplication.translate("StdmMapToolCreateFeature","Cannot add to layer"), \
                                    QApplication.translate("StdmMapToolCreateFeature",
                                                           "The data provider for this layer does not support the addition of features."))
            return
        
        if not stdmLayer.isEditable():
            self.notifyNotEditableLayer()
            return
        
        coordsEditor = SpatialCoordinatesEditor(self.iface.mainWindow())
        ret = coordsEditor.exec_()
        
        if ret == QDialog.Accepted:
            layerPoint = coordsEditor.qgsPoint()
            
            #Spatial unit point capture
            if self._mode == CAPTURE_POINT:        
                if stdmLayer.geometryType() != QGis.Point:
                    QMessageBox.information(self.iface.mainWindow(), \
                                        QApplication.translate("StdmMapToolCreateFeature","Wrong create tool"), \
                                        QApplication.translate("StdmMapToolCreateFeature",
                                                               "Cannot apply the 'Create Point Feature' tool on this vector layer"))
                    return
                
                self.startCapturing()
                
                if layerWKBType == QGis.WKBPoint or layerWKBType == QGis.WKBPoint25D:
                    self._geometry = QgsGeometry.fromPoint(layerPoint)
                elif layerWKBType == QGis.WKBMultiPoint or layerWKBType == QGis.WKBMultiPoint25D:
                    self._geometry = QgsGeometry.fromMultiPoint(layerPoint)
                    
            elif self._mode == CAPTURE_LINE or self._mode == CAPTURE_POLYGON:
                if self._mode == CAPTURE_LINE and stdmLayer.geometryType() != QGis.Line:
                    QMessageBox.information(self.iface.mainWindow(), \
                                        QApplication.translate("StdmMapToolCreateFeature","Wrong create tool"), \
                                        QApplication.translate("StdmMapToolCreateFeature",
                                                               "Cannot apply the 'Create Line Feature' tool on this vector layer"))
                    return
                
                if self._mode == CAPTURE_POLYGON and stdmLayer.geometryType() != QGis.Polygon:
                    QMessageBox.information(self.iface.mainWindow(), \
                                        QApplication.translate("StdmMapToolCreateFeature","Wrong create tool"), \
                                        QApplication.translate("StdmMapToolCreateFeature",
                                                               "Cannot apply the 'Create Polygon Feature' tool on this vector layer"))
                    return
                
                error = self.addVertex(layerPoint,True)
                    
                if error == 2:
                    QMessageBox.critical(self.iface.mainWindow(), \
                                        QApplication.translate("StdmMapToolCreateFeature","Coordinate transform error"), \
                                        QApplication.translate("StdmMapToolCreateFeature",
                                                               "Cannot transform the point to the layer's coordinate system"))
                    return
                elif error == 3:
                    QMessageBox.critical(self.iface.mainWindow(), \
                                        QApplication.translate("StdmMapToolCreateFeature","Coordinate transform error"), \
                                        QApplication.translate("StdmMapToolCreateFeature",
                                                               "Cannot transform the layer point to the map's coordinate system"))
                    return
                    
                self.startCapturing()
    
    def onFinishSketch(self):
        '''
        Slot raised upon selecting to finish drawing the sketch spatial unit.
        '''
        stdmLayer = self.currentVectorLayer()
        layerWKBType = stdmLayer.wkbType()
        
        feature = QgsFeature(stdmLayer.pendingFields())
        
        if self._mode == CAPTURE_POINT:
            feature.setGeometry(self._geometry)
        
        elif self._mode == CAPTURE_LINE or self._mode == CAPTURE_POLYGON:
            #Delete temporary rubber band
            if self._tempRubberBand != None:
                self.canvas.scene().removeItem(self._tempRubberBand)
                del self._tempRubberBand
                self._tempRubberBand = None
                
            #Validate geometries using number of points
            if self._mode == CAPTURE_LINE and len(self._captureList) < 2:
                self.stopCapturing()
                return
                
            if self._mode == CAPTURE_POLYGON and len(self._captureList) < 3:
                self.stopCapturing()
                return
                
            if self._mode == CAPTURE_LINE:
                if layerWKBType == QGis.WKBLineString or layerWKBType == QGis.WKBLineString25D:
                    self._geometry = QgsGeometry.fromPolyline(self._captureList)
                        
                elif layerWKBType == QGis.WKBMultiLineString or layerWKBType == QGis.WKBMultiLineString25D:
                    self._geometry = QgsGeometry.fromMultiPolyline(self._captureList)
                        
                else:
                    QMessageBox.critical(self.iface.mainWindow(), \
                                    QApplication.translate("StdmMapToolCreateFeature","WKB Type Error"), \
                                    QApplication.translate("StdmMapToolCreateFeature",
                                                           "Cannot add feature. Unknown WKB type"))
                    return
                    
                feature.setGeometry(self._geometry)
                
            #Polygon    
            else:
                if layerWKBType == QGis.WKBPolygon or layerWKBType == QGis.WKBPolygon25D:
                    self._geometry = QgsGeometry.fromPolygon([self._captureList])
                        
                elif layerWKBType == QGis.WKBMultiPolygon or layerWKBType == QGis.WKBMultiPolygon25D:
                    self._geometry = QgsGeometry.fromMultiPolygon([self._captureList])
                        
                else:
                    QMessageBox.critical(self.iface.mainWindow(), \
                                    QApplication.translate("StdmMapToolCreateFeature","WKB Type Error"), \
                                    QApplication.translate("StdmMapToolCreateFeature",
                                                           "Cannot add feature. Unknown WKB type"))
                    return
                
                feature.setGeometry(self._geometry)
                    
                avoidIntersectionsReturn = feature.geometry().avoidIntersections()
                    
                if avoidIntersectionsReturn == 3:
                    QMessageBox.critical(self.iface.mainWindow(), \
                                    QApplication.translate("StdmMapToolCreateFeature","Error"), \
                                    QApplication.translate("StdmMapToolCreateFeature",
                                                           "An error was reported during intersection removal"))
                        
                polyWkb = feature.geometry().asWkb()
                    
                if polyWkb == None:
                    reason = ""
                    if avoidIntersectionsReturn != 2:
                        reason = QApplication.translate("StdmMapToolCreateFeature",
                                                            "The feature cannot be added because it's geometry is empty")
                    else:
                        reason = QApplication.translate("StdmMapToolCreateFeature",
                                                            "The feature cannot be added because it's geometry collapsed due to intersection avoidance")
                            
                    QMessageBox.critical(self.iface.mainWindow(), \
                                    QApplication.translate("StdmMapToolCreateFeature","Error"), \
                                    reason)
                        
                    self.stopCapturing()
                    del feature
                    self._resetGeometry()
                    return
                           
        stdmLayer.beginEditCommand(QApplication.translate("StdmMapToolCreateFeature","Feature Added"))
                    
        if self.addFeature(stdmLayer, feature):
            stdmLayer.endEditCommand()
                        
        else:
            del feature
            self._resetGeometry()
            stdmLayer.destroyEditCommand()
            
        self.stopCapturing()
        
        self.canvas.refresh()
         
    def addFeature(self,stdmlayer,feat):
        '''
        Add feature to the vector layer for pending commit.
        '''
        #Try set the attribute editor
        self._configureSpatialEditor(stdmlayer)
        
        if self._editorWidget == None:
            QMessageBox.critical(self.iface.mainWindow(), \
                                    QApplication.translate("StdmMapToolCreateFeature","Cannot open editor"), \
                                    QApplication.translate("StdmMapToolCreateFeature",
                                                           "Attribute editor for the selected layer could not be found."))
            return False
        
        #Connect commitChanges signals so that the relation of foreign key entities can be updated accordingly. 
        stdmlayer.committedFeaturesAdded.connect(self.onFeaturesCommitted)

        spEditor = self._editorWidget(self.iface.mainWindow(),stdmlayer,feat)
        
        if spEditor.exec_() == QDialog.Accepted:
            #Check for pending entities and add to collection
            pendingLayerEntities = spEditor.pendingLayerEntities()
            
            if not pendingLayerEntities.layerId() in self._pendingFKEntities:
                self._pendingFKEntities[pendingLayerEntities.layerId()] = pendingLayerEntities
                
            else:
                self._pendingFKEntities[pendingLayerEntities.layerId()].merge(pendingLayerEntities)
            
            return True
        
        else:
            return False
        
    def onFeaturesCommitted(self,layerid,features):
        '''
        Update the related entities with the FK key from the primary spatial unit PK.
        '''
        if layerid in self._pendingFKEntities:
            pendingLayerEntity = self._pendingFKEntities[layerid]
            
            #Get map layer using layerid
            refLayer = QgsMapLayerRegistry.instance().mapLayer(layerid)
            
            if refLayer != None:   
                fidx = refLayer.fieldNameIndex(pendingLayerEntity.featureAttributeName())
                
                #Show progress dialog for updating the features.
                progressLabel = QApplication.translate("StdmMapToolCreateFeature", "Updating related entities...")
                progressDlg = QProgressDialog(progressLabel,"",0,len(features),self.iface.mainWindow())
                progressDlg.setWindowModality(Qt.WindowModal)
                
                for i,feat in enumerate(features):
                    progressDlg.setValue(i)
                    uniqueAttrValue = feat.attributes()[fidx]
                    pendingLayerEntity.setPrimaryKey(uniqueAttrValue,int(feat.id()))
                    
                progressDlg.setValue(len(features))
            
    def canvasReleaseEvent(self,e):
        '''
        Base class override.
        '''
        stdmLayer = self.currentVectorLayer()
        
        #Try to set mode from layer type
        if self._mode == CAPTURE_NONE:
            self.setCaptureMode(stdmLayer)
        
        if not isinstance(stdmLayer,QgsVectorLayer):
            self.notifyNotVectorLayer()
            return
        
        layerWKBType = stdmLayer.wkbType()
        provider = stdmLayer.dataProvider()
        
        if not (provider.capabilities() & QgsVectorDataProvider.AddFeatures):
            QMessageBox.information(self.iface.mainWindow(), \
                                    QApplication.translate("StdmMapToolCreateFeature","Cannot add to layer"), \
                                    QApplication.translate("StdmMapToolCreateFeature",
                                                           "The data provider for this layer does not support the addition of features."))
            return
        
        if not stdmLayer.isEditable():
            self.notifyNotEditableLayer()
            return
        
        #Spatial unit point capture
        if self._mode == CAPTURE_POINT:        
            if stdmLayer.geometryType() != QGis.Point:
                QMessageBox.information(self.iface.mainWindow(), \
                                    QApplication.translate("StdmMapToolCreateFeature","Wrong create tool"), \
                                    QApplication.translate("StdmMapToolCreateFeature",
                                                           "Cannot apply the 'Create Point Feature' tool on this vector layer"))
                return
            
            self.startCapturing()
            
            #Point in map coordinates
            mapPoint = None
            snapResults = []
            #Point in layer coordinates
            layerPoint = None
            
            opResult,snapResults = self._snapper.snapToBackgroundLayers(e.pos())
            
            if len(snapResults) > 0:
                mapPoint = self.snapPointFromResults(snapResults, e.pos())
                
            else:
                mapPoint = self.toMapCoordinates(e.pos())
                
            try:
                layerPoint = self.toLayerCoordinates(stdmLayer,mapPoint)
            except QgsCsException:
                QMessageBox.information(self.iface.mainWindow(), \
                                    QApplication.translate("StdmMapToolCreateFeature","Coordinate transform error"), \
                                    QApplication.translate("StdmMapToolCreateFeature",
                                                           "Cannot transform the point to the layer's coordinate system"))
                self._capturing = False
                return
            
            if layerWKBType == QGis.WKBPoint or layerWKBType == QGis.WKBPoint25D:
                self._geometry = QgsGeometry.fromPoint(layerPoint)
            elif layerWKBType == QGis.WKBMultiPoint or layerWKBType == QGis.WKBMultiPoint25D:
                self._geometry = QgsGeometry.fromMultiPoint(layerPoint)
            
        #Line and polygon capturing
        elif self._mode == CAPTURE_LINE or self._mode == CAPTURE_POLYGON:
            if self._mode == CAPTURE_LINE and stdmLayer.geometryType() != QGis.Line:
                QMessageBox.information(self.iface.mainWindow(), \
                                    QApplication.translate("StdmMapToolCreateFeature","Wrong create tool"), \
                                    QApplication.translate("StdmMapToolCreateFeature",
                                                           "Cannot apply the 'Create Line Feature' tool on this vector layer"))
                return
            
            if self._mode == CAPTURE_POLYGON and stdmLayer.geometryType() != QGis.Polygon:
                QMessageBox.information(self.iface.mainWindow(), \
                                    QApplication.translate("StdmMapToolCreateFeature","Wrong create tool"), \
                                    QApplication.translate("StdmMapToolCreateFeature",
                                                           "Cannot apply the 'Create Polygon Feature' tool on this vector layer"))
                return
            
            if e.button() == Qt.LeftButton:
                error = self.addVertex(e.pos())
                
                if error == 2:
                    QMessageBox.critical(self.iface.mainWindow(), \
                                    QApplication.translate("StdmMapToolCreateFeature","Coordinate transform error"), \
                                    QApplication.translate("StdmMapToolCreateFeature",
                                                           "Cannot transform the point to the layer's coordinate system"))
                    return
                
                self.startCapturing()
                
    def _resetGeometry(self):
        del self._geometry
        self._geometry = None
        
                
            
        
        
        
        