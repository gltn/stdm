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

from qgis.PyQt.QtCore import (
    QSettings,
    Qt
)
from qgis.PyQt.QtGui import (
    QColor
)
from qgis.PyQt.QtWidgets import (
    QWidget,
    QGridLayout,
    QToolButton,
    QCheckBox,
    QDoubleSpinBox,
    QLabel
)
from qgis.core import (
    QgsProject
)
from qgis.gui import (
    QgsMapCanvas,
    QgsMapToolPan,
)
from stdm.ui.gui_utils import GuiUtils

class MirrorMap(QWidget):
    def __init__(self, parent=None, iface=None):
        QWidget.__init__(self, parent)
        # self.setAttribute(Qt.WA_DeleteOnClose)

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
        self.canvas.setCanvasColor(QColor(255, 255, 255))
        settings = QSettings()
        gridLayout.addWidget(self.canvas, 0, 0, 1, 5)

        self.addLayerBtn = QToolButton(self)
        # self.addLayerBtn.setToolButtonStyle( Qt.ToolButtonTextBesideIcon )
        # self.addLayerBtn.setText("Add current layer")
        self.addLayerBtn.setIcon(GuiUtils.get_icon("add.png"))

        self.addLayerBtn.clicked.connect(self.tool_add_layer)
        gridLayout.addWidget(self.addLayerBtn, 1, 0, 1, 1)

        self.delLayerBtn = QToolButton(self)
        # self.delLayerBtn.setToolButtonStyle( Qt.ToolButtonTextBesideIcon )
        # self.delLayerBtn.setText("Remove current layer")
        self.delLayerBtn.setIcon(GuiUtils.get_icon("remove.png"))
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
        # self.iface.mapCanvas().mapCanvasRefreshed.connect(self.on_canvas_refreshed)
        self.iface.mapCanvas().destinationCrsChanged.connect(self.onCrsChanged)
        QgsProject.instance().layerWillBeRemoved.connect(self.delLayer)
        self.iface.currentLayerChanged.connect(self.refreshLayerButtons)

        self.refreshLayerButtons()

        self.onExtentsChanged()
        self.onCrsChanged()

    def refresh_layers(self):
        """
        Checks if the layers in the canvas list have already been added.
        If not, then add to the property viewer canvas.
        """
        for ly in self.iface.mapCanvas().layers():
            layer_id = self._layerId(ly)
            if layer_id not in self.layerId2canvasLayer:
                self.addLayer(layer_id)
        # QCoreApplication.processEvents(QEventLoop.ExcludeSocketNotifiers|QEventLoop.ExcludeUserInputEvents)

    def onExtentsChanged(self):
        prevFlag = self.canvas.renderFlag()
        self.canvas.setRenderFlag(False)

        self.canvas.setExtent(self.iface.mapCanvas().extent())
        self.canvas.zoomByFactor(self.scaleFactor.value())
        # self.canvas.refresh()

        self.canvas.setRenderFlag(prevFlag)

    def onCrsChanged(self):
        self.canvas.setDestinationCrs(self.iface.mapCanvas().mapSettings().destinationCrs())

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
        return [self._layerId(x.layer()) for x in self.canvasLayers]

    def setLayerSet(self, layerIds=None):
        prevFlag = self.canvas.renderFlag()
        self.canvas.setRenderFlag(False)

        if layerIds == None:
            self.layerId2canvasLayer = {}
            self.canvasLayers = []
            self.canvas.setLayers([])

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
        for l in self.iface.mapCanvas().layers():
            lid = self._layerId(l)
            if lid in self.layerId2canvasLayer:  # previously added
                cl = self.layerId2canvasLayer[lid]
            elif l == layer:  # Selected layer
                cl = layer
            else:
                continue

            id2cl_dict[lid] = cl
            self.canvasLayers.append(cl)

        self.layerId2canvasLayer = id2cl_dict
        self.canvas.setLayers(self.canvasLayers)

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
        if layerId not in self.layerId2canvasLayer:
            return

        prevFlag = self.canvas.renderFlag()
        self.canvas.setRenderFlag(False)

        cl = self.layerId2canvasLayer[layerId]
        del self.layerId2canvasLayer[layerId]
        self.canvasLayers.remove(cl)
        self.canvas.setLayers(self.canvasLayers)

        self.refreshLayerButtons()
        self.onExtentsChanged()
        self.canvas.setRenderFlag(prevFlag)

    def _layerId(self, layer):
        if hasattr(layer, 'id'):
            return layer.id()

        return layer.getLayerID()
