# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Dockable MirrorMap
Description          : Creates a dockable map canvas
Date                 : February 1, 2011
copyright            : (C) 2011 by Giuseppe Sucameli (Faunalia)
email                : brush.tyler@gmail.com

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

from qgis.PyQt.QtWidgets import (
    QWidget,
    QGridLayout,
    QToolButton,
    QCheckBox,
    QDoubleSpinBox,
    QLabel
)
from qgis.PyQt.QtGui import (
    QColor,
    QIcon
)
from qgis.PyQt.QtCore import (
    QSettings,
    Qt
)

from qgis.core import (
    QgsProject
)
from qgis.gui import (
    QgsMapCanvas,
    QgsMapToolPan,
)

class MirrorMap(QWidget):
    def __init__(self, parent=None, iface=None):
        QWidget.__init__(self, parent)
        #self.setAttribute(Qt.WA_DeleteOnClose)

        self.iface = iface
        self.layerId2canvasLayer = {}
        self.canvasLayers = []

        self.setupUi()

    def closeEvent(self, event):
        self.scaleFactor.valueChanged.disconnect(self.onExtentsChanged)

        if not self.iface is None:
            self.iface.mapCanvas().extentsChanged.discconnect(self.onExtentsChanged)
            self.iface.mapCanvas().mapRenderer().destinationCrsChanged.disconnect(self.onCrsChanged)
            self.iface.mapCanvas().mapRenderer().mapUnitsChanged.disconnect(self.onCrsChanged)
            self.iface.mapCanvas().mapRenderer().hasCrsTransformEnabled.disconnect(self.onCrsTransformEnabled)
            QgsProject.instance().layerWillBeRemoved.disconnect(self.delLayer)
            self.iface.currentLayerChanged.disconnect(self.refreshLayerButtons)

        self.closed.emit()

        return QWidget.closeEvent(self, event)

    def setupUi(self):
        self.setObjectName("mirrormap")

        gridLayout = QGridLayout(self)
        gridLayout.setContentsMargins(0, 0, gridLayout.verticalSpacing(), gridLayout.verticalSpacing())

        self.canvas = QgsMapCanvas(self)
        self.canvas.setCanvasColor(QColor(255,255,255))
        settings = QSettings()
        self.canvas.enableAntiAliasing(settings.value("/qgis/enable_anti_aliasing", False, type=bool))
        self.canvas.useImageToRender(settings.value("/qgis/use_qimage_to_render", False, type=bool))
        action = settings.value( "/qgis/wheel_action", 0, type=int)
        zoomFactor = settings.value( "/qgis/zoom_factor", 2.0, type=float)
        self.canvas.setWheelAction(QgsMapCanvas.WheelAction(action), zoomFactor)
        gridLayout.addWidget(self.canvas, 0, 0, 1, 5)

        self.addLayerBtn = QToolButton(self)
        #self.addLayerBtn.setToolButtonStyle( Qt.ToolButtonTextBesideIcon )
        #self.addLayerBtn.setText("Add current layer")
        self.addLayerBtn.setIcon(QIcon(":/plugins/stdm/images/icons/add.png"))

        self.addLayerBtn.clicked.connect(self.tool_add_layer)
        gridLayout.addWidget(self.addLayerBtn, 1, 0, 1, 1)

        self.delLayerBtn = QToolButton(self)
        #self.delLayerBtn.setToolButtonStyle( Qt.ToolButtonTextBesideIcon )
        #self.delLayerBtn.setText("Remove current layer")
        self.delLayerBtn.setIcon(QIcon(":/plugins/stdm/images/icons/remove.png"))
        self.delLayerBtn.clicked.connect(self.tool_remove_layer)
        gridLayout.addWidget(self.delLayerBtn, 1, 1, 1, 1)

        self.renderCheck = QCheckBox("Render", self)
        self.renderCheck.toggled.connect(self.toggleRender)
        self.renderCheck.setChecked(True)
        gridLayout.addWidget(self.renderCheck, 1, 2, 1, 1)

        self.scaleFactorLabel = QLabel(self)
        self.scaleFactorLabel.setText("Scale factor:")
        self.scaleFactorLabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        gridLayout.addWidget(self.scaleFactorLabel, 1, 3, 1, 1)
        self.scaleFactor = QDoubleSpinBox(self)
        self.scaleFactor.setMinimum(0.0)
        self.scaleFactor.setMaximum(1000.0)
        self.scaleFactor.setDecimals(3)
        self.scaleFactor.setValue(1)
        self.scaleFactor.setObjectName("scaleFactor")
        self.scaleFactor.setSingleStep(.05)
        gridLayout.addWidget(self.scaleFactor, 1, 4, 1, 1)
        self.scaleFactor.valueChanged.connect(self.onExtentsChanged)

        # Add a default pan tool
        self.toolPan = QgsMapToolPan(self.canvas)
        self.canvas.setMapTool(self.toolPan)

        self.scaleFactor.valueChanged.connect(self.onExtentsChanged)
        self.set_iface(self.iface)

    def toggleRender(self, enabled):
        self.canvas.setRenderFlag(enabled)

    def extent(self):
        """
        :return: Current extents of the map canvas view.
        """
        return self.canvas.extent()

    def canvas_layers(self):
        """
        :return: Layers currently in the canvas.
        :rtype: list
        """
        return self.canvasLayers

    def on_canvas_refreshed(self):
        """
        """
        self.refresh_layers()

    def tool_add_layer(self):
        self.addLayer()

    def tool_remove_layer(self):
        self.delLayer()

    def set_iface(self, iface):
        if iface is None:
            return

        self.iface = iface
        self.iface.mapCanvas().extentsChanged.connect(self.onExtentsChanged)
        #self.iface.mapCanvas().mapCanvasRefreshed.connect(self.on_canvas_refreshed)
        self.iface.mapCanvas().mapRenderer().destinationSrsChanged.connect(self.onCrsChanged)
        self.iface.mapCanvas().mapRenderer().mapUnitsChanged.connect(self.onCrsChanged)
        self.iface.mapCanvas().mapRenderer().hasCrsTransformEnabled.connect(self.onCrsTransformEnabled)
        QgsProject.instance().layerWillBeRemoved.connect(self.delLayer)
        self.iface.currentLayerChanged.connect(self.refreshLayerButtons)

        self.refreshLayerButtons()

        self.onExtentsChanged()
        self.onCrsChanged()
        self.onCrsTransformEnabled(self.iface.mapCanvas().hasCrsTransformEnabled())

    def refresh_layers(self):
        """
        Checks if the layers in the canvas list have already been added.
        If not, then add to the property viewer canvas.
        """
        for ly in self.iface.legendInterface().layers():
            layer_id = self._layerId(ly)
            if not self.layerId2canvasLayer.has_key(layer_id):
                self.addLayer(layer_id)
        #QCoreApplication.processEvents(QEventLoop.ExcludeSocketNotifiers|QEventLoop.ExcludeUserInputEvents)

    def onExtentsChanged(self):
        prevFlag = self.canvas.renderFlag()
        self.canvas.setRenderFlag(False)

        self.canvas.setExtent(self.iface.mapCanvas().extent())
        self.canvas.zoomByFactor(self.scaleFactor.value())
        #self.canvas.refresh()

        self.canvas.setRenderFlag(prevFlag)

    def onCrsChanged(self):

        prevFlag = self.canvas.renderFlag()
        self.canvas.setRenderFlag(False)
        try:
            renderer = self.iface.mapCanvas().mapRenderer()
            self._setRendererCrs(
                self.canvas.mapRenderer(),
                self._rendererCrs(renderer)
            )
            self.canvas.mapRenderer().setMapUnits(renderer.mapUnits())

            self.canvas.setRenderFlag(prevFlag)
        except Exception:
            pass

    def onCrsTransformEnabled(self, enabled):
        prevFlag = self.canvas.renderFlag()
        self.canvas.setRenderFlag(False)

        self.canvas.mapRenderer().setProjectionsEnabled(enabled)

        self.canvas.setRenderFlag(prevFlag)

    def refreshLayerButtons(self):
        layer = self.iface.activeLayer()

        isLayerSelected = layer != None
        hasLayer = False
        for l in self.canvas.layers():
            if l == layer:
                hasLayer = True
                break

        self.addLayerBtn.setEnabled(isLayerSelected and not hasLayer)
        self.delLayerBtn.setEnabled(isLayerSelected and hasLayer)

    def getLayerSet(self):
        return map(lambda x: self._layerId(x.layer()), self.canvasLayers)

    def setLayerSet(self, layerIds=None):
        prevFlag = self.canvas.renderFlag()
        self.canvas.setRenderFlag(False)

        if layerIds == None:
            self.layerId2canvasLayer = {}
            self.canvasLayers = []
            self.canvas.setLayerSet([])

        else:
            for lid in layerIds:
                self.addLayer(lid)

        self.refreshLayerButtons()
        self.onExtentsChanged()
        self.canvas.setRenderFlag(prevFlag)

    def addLayer(self, layerId=None):
        if layerId == None:
            layer = self.iface.activeLayer()
        else:
            layer = QgsProject.instance().mapLayer(layerId)

        if layer == None:
            return

        prevFlag = self.canvas.renderFlag()
        self.canvas.setRenderFlag(False)

        # add the layer to the map canvas layer set
        self.canvasLayers = []
        id2cl_dict = {}
        for l in self.iface.legendInterface().layers():
            lid = self._layerId(l)
            if self.layerId2canvasLayer.has_key(lid):	#previously added
                cl = self.layerId2canvasLayer[lid]
            elif l == layer:	#Selected layer
                cl = QgsMapCanvasLayer(layer)
            else:
                continue

            id2cl_dict[lid] = cl
            self.canvasLayers.append(cl)

        self.layerId2canvasLayer = id2cl_dict
        self.canvas.setLayerSet(self.canvasLayers)

        self.refreshLayerButtons()
        self.onExtentsChanged()
        self.canvas.setRenderFlag(prevFlag)

    def delLayer(self, layerId=None):
        if layerId == None:
            layer = self.iface.activeLayer()
            if layer == None:
                return
            layerId = self._layerId(layer)

        # remove the layer from the map canvas layer set
        if not self.layerId2canvasLayer.has_key(layerId):
            return

        prevFlag = self.canvas.renderFlag()
        self.canvas.setRenderFlag( False )

        cl = self.layerId2canvasLayer[layerId]
        del self.layerId2canvasLayer[layerId]
        self.canvasLayers.remove(cl)
        self.canvas.setLayerSet(self.canvasLayers)
        del cl

        self.refreshLayerButtons()
        self.onExtentsChanged()
        self.canvas.setRenderFlag(prevFlag)

    def _layerId(self, layer):
        if hasattr(layer, 'id'):
            return layer.id()

        return layer.getLayerID()

    def _rendererCrs(self, renderer):
        if hasattr(renderer, 'destinationCrs'):
            return renderer.destinationCrs()
        return renderer.destinationSrs()

    def _setRendererCrs(self, renderer, crs):
        if hasattr(renderer, 'setDestinationCrs'):
            return renderer.setDestinationCrs(crs)

        return renderer.setDestinationSrs(crs)

