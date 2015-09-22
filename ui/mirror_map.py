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

from PyQt4.QtCore import SIGNAL, QSettings, Qt
from PyQt4.QtGui import QWidget, QGridLayout, QIcon, QToolButton, QColor, \
    QCheckBox, QLabel, QDoubleSpinBox

from qgis.core import QgsMapLayerRegistry
from qgis.gui import QgsMapCanvas, QgsMapToolPan, QgsMapCanvasLayer


class MirrorMap(QWidget):

    def __init__(self, parent=None, iface=None):
        QWidget.__init__(self, parent)
        # self.setAttribute(Qt.WA_DeleteOnClose)

        self._iface = iface
        self._layer_id_2_canvas_layer = {}
        self.canvas_layers = []

        self._set_up_ui()

    def closeEvent(self, event):
        """
        Closes Window
        :rtype : QWidget
        :param event:
        :return:
        """
        self.scale_factor.valueChanged.disconnect(self.on_extents_changed)

        if self._iface is not None:
            self._iface.mapCanvas().extentsChanged.discconnect(
                self.on_extents_changed)
            self._iface.mapCanvas().mapRenderer(). \
                destinationCrsChanged.disconnect(self.on_crs_changed)
            self._iface.mapCanvas().mapRenderer(). \
                mapUnitsChanged.disconnect(self.on_crs_changed)
            self._iface.mapCanvas().mapRenderer(). \
                hasCrsTransformEnabled.disconnect(
                self.on_crs_trans_form_enabled)
            QgsMapLayerRegistry.instance(). layerWillBeRemoved.disconnect(
                self.del_layer)
            self._iface.currentLayerChanged.disconnect(
                self.refresh_layer_buttons)

        self.emit(SIGNAL("closed(PyQt_PyObject)"), self)

        return QWidget.closeEvent(self, event)

    def _set_up_ui(self):
        """
        Sets up UI elements
        """
        self.setObjectName("mirrormap")

        grid_layout = QGridLayout(self)
        grid_layout.setContentsMargins(
            0, 0, grid_layout.verticalSpacing(), grid_layout.verticalSpacing())

        self.canvas = QgsMapCanvas(self)
        self.canvas.setCanvasColor(QColor(255, 255, 255))
        settings = QSettings()
        self.canvas.enableAntiAliasing(settings.value(
            "/qgis/enable_anti_aliasing", False, type=bool))
        self.canvas.useImageToRender(settings.value(
            "/qgis/use_qimage_to_render", False, type=bool))
        action = settings.value("/qgis/wheel_action", 0, type=int)
        zoom_factor = settings.value("/qgis/zoom_factor", 2.0, type=float)
        self.canvas.setWheelAction(
            QgsMapCanvas.WheelAction(action), zoom_factor)
        grid_layout.addWidget(self.canvas, 0, 0, 1, 5)

        self.add_layer_btn = QToolButton(self)
        # self.addLayerBtn.setToolButtonStyle( Qt.ToolButtonTextBesideIcon )
        # self.addLayerBtn.setText("Add current layer")
        self.add_layer_btn.setIcon(
            QIcon(":/plugins/stdm/images/icons/add.png"))
        self.add_layer_btn.clicked.connect(self.tool_add_layer)
        grid_layout.addWidget(self.add_layer_btn, 1, 0, 1, 1)

        self.del_layer_btn = QToolButton(self)
        # self.delLayerBtn.setToolButtonStyle( Qt.ToolButtonTextBesideIcon )
        # self.delLayerBtn.setText("Remove current layer")
        self.del_layer_btn.setIcon(
            QIcon(":/plugins/stdm/images/icons/remove.png"))
        self.del_layer_btn.clicked.connect(self.tool_remove_layer)
        grid_layout.addWidget(self.del_layer_btn, 1, 1, 1, 1)

        self.render_check = QCheckBox("Render", self)
        self.render_check.toggled.connect(self.toggle_render)
        self.render_check.setChecked(True)
        grid_layout.addWidget(self.render_check, 1, 2, 1, 1)

        self.scale_factor_label = QLabel(self)
        self.scale_factor_label.setText("Scale factor:")
        self.scale_factor_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid_layout.addWidget(self.scale_factor_label, 1, 3, 1, 1)
        self.scale_factor = QDoubleSpinBox(self)
        self.scale_factor.setMinimum(0.0)
        self.scale_factor.setMaximum(1000.0)
        self.scale_factor.setDecimals(3)
        self.scale_factor.setValue(1)
        self.scale_factor.setObjectName("scaleFactor")
        self.scale_factor.setSingleStep(.05)
        grid_layout.addWidget(self.scale_factor, 1, 4, 1, 1)
        self.scale_factor.valueChanged.connect(self.on_extents_changed)

        # Add a default pan tool
        self.toolPan = QgsMapToolPan(self.canvas)
        self.canvas.setMapTool(self.toolPan)

        self.scale_factor.valueChanged.connect(self.on_extents_changed)
        self.set_iface(self._iface)

    def toggle_render(self, enabled):
        """
        :param enabled:
        """
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
        return self.canvas_layers

    def on_canvas_refreshed(self):
        """
        """
        self.refresh_layers()

    def tool_add_layer(self):
        self.add_layer()

    def tool_remove_layer(self):
        self.del_layer()

    def set_iface(self, iface):
        if iface is None:
            return

        self._iface = iface
        self._iface.mapCanvas().extentsChanged.connect(self.on_extents_changed)
        # self.iface.mapCanvas().mapCanvasRefreshed.connect(
        # self.on_canvas_refreshed)
        self._iface.mapCanvas().mapRenderer().destinationSrsChanged.connect(
            self.on_crs_changed)
        self._iface.mapCanvas().mapRenderer().mapUnitsChanged.connect(
            self.on_crs_changed)
        self._iface.mapCanvas().mapRenderer().hasCrsTransformEnabled.connect(
            self.on_crs_trans_form_enabled)
        QgsMapLayerRegistry.instance().layerWillBeRemoved.connect(
            self.del_layer)
        self._iface.currentLayerChanged.connect(self.refresh_layer_buttons)

        self.refresh_layer_buttons()

        self.on_extents_changed()
        self.on_crs_changed()
        self.on_crs_trans_form_enabled(
            self._iface.mapCanvas().hasCrsTransformEnabled())

    def refresh_layers(self):
        """
        Checks if the layers in the canvas list have already been added.
        If not, then add to the property viewer canvas.
        """
        for ly in self._iface.legendInterface().layers():
            layer_id = self._layer_id(ly)
            if layer_id not in self._layer_id_2_canvas_layer:
                self.add_layer(layer_id)
        # QCoreApplication.processEvents(
        # QEventLoop.ExcludeSocketNotifiers|QEventLoop.ExcludeUserInputEvents)

    def on_extents_changed(self):
        """
        Implemented when extent changes
        """
        prev_flag = self.canvas.renderFlag()
        self.canvas.setRenderFlag(False)

        self.canvas.setExtent(self._iface.mapCanvas().extent())
        self.canvas.zoomByFactor(self.scale_factor.value())
        # self.canvas.refresh()

        self.canvas.setRenderFlag(prev_flag)

    def on_crs_changed(self):
        """
        Implemented when CRS changes
        """
        prev_flag = self.canvas.renderFlag()
        self.canvas.setRenderFlag(False)

        renderer = self._iface.mapCanvas().mapRenderer()
        self._set_renderer_crs(
            self.canvas.mapRenderer(), self._renderer_crs(renderer))
        self.canvas.mapRenderer().setMapUnits(renderer.mapUnits())

        self.canvas.setRenderFlag(prev_flag)

    def on_crs_trans_form_enabled(self, enabled):
        """
        :param enabled:
        """
        prev_flag = self.canvas.renderFlag()
        self.canvas.setRenderFlag(False)

        self.canvas.mapRenderer().setProjectionsEnabled(enabled)

        self.canvas.setRenderFlag(prev_flag)

    def refresh_layer_buttons(self):
        layer = self._iface.activeLayer()

        is_layer_selected = layer is not None
        has_layer = False
        for l in self.canvas.layers():
            if l is layer:
                has_layer = True
                break

        self.add_layer_btn.setEnabled(is_layer_selected and not has_layer)
        self.del_layer_btn.setEnabled(is_layer_selected and has_layer)

    def get_layer_set(self):
        """
        Gets Lay set
        :rtype : map
        :return:
        """
        return map(lambda x: self._layer_id(x.layer()), self.canvas_layers)

    def set_layer_set(self, layer_ids=None):
        """
        :param layer_ids:
        """
        prev_flag = self.canvas.renderFlag()
        self.canvas.setRenderFlag(False)

        if layer_ids is None:
            self._layer_id_2_canvas_layer = {}
            self.canvas_layers = []
            self.canvas.setLayerSet([])

        else:
            for lid in layer_ids:
                self.add_layer(lid)

        self.refresh_layer_buttons()
        self.on_extents_changed()
        self.canvas.setRenderFlag(prev_flag)

    def add_layer(self, layer_id=None):
        """
        Add layer
        :param layer_id:
        :return:
        """
        if layer_id is None:
            layer = self._iface.activeLayer()
        else:
            layer = QgsMapLayerRegistry.instance().mapLayer(layer_id)

        if layer is None:
            return

        prev_flag = self.canvas.renderFlag()
        self.canvas.setRenderFlag(False)

        # add the layer to the map canvas layer set
        self.canvas_layers = []
        id2cl_dict = {}
        for l in self._iface.legendInterface().layers():
            lid = self._layer_id(l)
            # previously added
            if lid in self._layer_id_2_canvas_layer:
                cl = self._layer_id_2_canvas_layer[lid]
            elif l == layer:  # Selected layer
                cl = QgsMapCanvasLayer(layer)
            else:
                continue

            id2cl_dict[lid] = cl
            self.canvas_layers.append(cl)

        self._layer_id_2_canvas_layer = id2cl_dict
        self.canvas.setLayerSet(self.canvas_layers)

        self.refresh_layer_buttons()
        self.on_extents_changed()
        self.canvas.setRenderFlag(prev_flag)

    def del_layer(self, layer_id=None):
        """
        :param layer_id:
        :return:
        """
        if layer_id is None:
            layer = self._iface.activeLayer()
            if layer is None:
                return
            layer_id = self._layer_id(layer)

        # remove the layer from the map canvas layer set
        if layer_id not in self._layer_id_2_canvas_layer:
            return

        prev_flag = self.canvas.renderFlag()
        self.canvas.setRenderFlag(False)

        cl = self._layer_id_2_canvas_layer[layer_id]
        del self._layer_id_2_canvas_layer[layer_id]
        self.canvas_layers.remove(cl)
        self.canvas.setLayerSet(self.canvas_layers)
        del cl

        self.refresh_layer_buttons()
        self.on_extents_changed()
        self.canvas.setRenderFlag(prev_flag)

    def _layer_id(self, layer):
        """
        :rtype : int
        :param layer:
        :return:
        """
        if hasattr(layer, 'id'):
            return layer.id()

        return layer.getLayerID()

    def _renderer_crs(self, renderer):
        """
        :param renderer:
        :return:
        """
        if hasattr(renderer, 'destinationCrs'):
            return renderer.destinationCrs()
        return renderer.destinationSrs()

    def _set_renderer_crs(self, renderer, crs):
        """
        :param renderer:
        :param crs:
        :return:
        """
        if hasattr(renderer, 'setDestinationCrs'):
            return renderer.setDestinationCrs(crs)

        return renderer.setDestinationSrs(crs)
