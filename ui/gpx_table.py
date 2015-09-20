# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Name               :Spatial Unit Manager Import GPX files table dialog
 Description        :An STDM module that enables loading editing and saving
                    layers back to database
                             -------------------
 Date                : 2015-04-08
 Copyright            : (C) 2014 by UN-Habitat and implementing partners.
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

from PyQt4.QtCore import Qt, pyqtSlot
from PyQt4.QtGui import QDialog, QColor, QTableWidgetItem, QSpinBox, \
    QMessageBox, QSizePolicy, QAbstractItemView
from qgis.core import QgsVectorLayer, QgsFeature, QgsPoint, QgsGeometry, \
    QgsMapLayerRegistry, QgsRectangle
from qgis.gui import QgsVertexMarker

from ..data import (non_spatial_table_columns,
                    vector_layer)

from ui_gpx_table_widget import Ui_Dialog

from gpx_add_attribute_info import GPXAttributeInfoDialog


class GpxTableWidgetDialog(QDialog, Ui_Dialog):

    def __init__(
            self, iface, curr_layer, gpx_file, active_layer,
            active_layer_geom, sp_table, sp_col):
        QDialog.__init__(self, iface.mainWindow())
        self.setupUi(self)
        self._iface = iface
        self._curr_layer = curr_layer
        self._sp_table = sp_table
        self._sp_col = sp_col
        self._table_widget = self.tableWidget
        self._map_canvas = self._iface.mapCanvas()
        self._layer_gpx = gpx_file
        self._active_layer = active_layer
        self._green = QColor(0, 255, 0)
        self._red = QColor(255, 0, 0)
        self._black = QColor(0, 0, 0)
        self._vertex_color = QColor(0, 0, 0)
        self._active_layer_geometry_typ = active_layer_geom
        self._vertex_dict = {}
        self._reset_vertex_dict = {}
        self._gpx_tw_item_initial_state = Qt.Checked
        self._prv_chkbx_itm_placeholder_dict = {}
        self._table_widget.itemPressed.connect(
            self.gpx_table_widget_item_pressed)
        self._table_widget.itemClicked.connect(
            self.gpx_table_widget_item_clicked)
        self._table_widget.itemSelectionChanged.connect(
            self.gpx_table_widget_item_selection_changed)
        self._table_pressed_status = False
        self._table_select_status = False
        self._check_box_clicked_state = False
        self._list_of_selected_rows = []
        self._pressed_item_list = []
        self._gpx_add_attribute_info = None
        self._label = None
        self._vl = None
        self._temp_layer_type = None

    def populate_qtable_widget(self):
        check_box_state = Qt.Checked

        # Populate QTableWidget
        self._table_widget.setRowCount(self._layer_gpx.GetFeatureCount())
        self._table_widget.setColumnCount(4)
        self._table_widget.setHorizontalHeaderLabels(["",
                                                     "Point Name",
                                                     "Latitude",
                                                     "Longitude",
                                                     # "Lat-Offset",
                                                     # "Long-offset"
                                                     ])

        # self.table_widget.setFocusPolicy(Qt.NoFocus)
        # self.table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        row_counter = 0
        layer_list = []

        if self._active_layer_geometry_typ == 0:
            self._temp_layer_type = "Point"
        elif self._active_layer_geometry_typ == 1:
            self._temp_layer_type = "LineString"
        elif self._active_layer_geometry_typ == 2:
            self._temp_layer_type = "Polygon"

        # create memory layer
        self._vl = QgsVectorLayer(
            "{0}?crs=epsg:4326&field=id:integer&index=yes".format(
                self._temp_layer_type), "tmp_layer", "memory")
        pr = self._vl.dataProvider()
        self._vl.startEditing()
        fet = QgsFeature()

        for i, row in enumerate(self._layer_gpx):
            # Get point lon lat from GPX file
            lat, lon, ele = row.GetGeometryRef().GetPoint()
            item_lat = QTableWidgetItem(str(lat))
            item_lon = QTableWidgetItem(str(lon))
            self._label = QTableWidgetItem(row.GetFieldAsString(4))

            gpx_layer_point = QgsPoint(lat, lon)

            layer_list.append(gpx_layer_point)

            # Center checkbox item
            # chk_bx_widget = QWidget()
            # chk_bx = QCheckBox()
            # chk_bx.setCheckState(Qt.Checked)
            # lay_out = QHBoxLayout(chk_bx_widget)
            # lay_out.addWidget(chk_bx)
            # lay_out.setAlignment(Qt.AlignCenter)
            # lay_out.setContentsMargins(0,0,0,0)
            # chk_bx_widget.setLayout(lay_out)

            # Normal checkbox item
            chk_bx_tb_widget_item = QTableWidgetItem()
            chk_bx_tb_widget_item.setFlags(
                Qt.ItemIsUserCheckable | Qt.ItemIsEnabled |
                Qt.ItemIsSelectable)
            chk_bx_tb_widget_item.setCheckState(check_box_state)

            # Spinbox for lat and lon offset
            x_offset_spin_bx = QSpinBox()
            y_offset_spin_bx = QSpinBox()

            # Add items to QTable widget
            # self.gpx_table.tableWidget.setCellWidget(i, 0, chk_bx_widget)
            #  Column 1
            self._table_widget.setItem(i, 0, chk_bx_tb_widget_item)  # Column 1
            self._table_widget.setItem(i, 1, self._label)
            self._table_widget.setItem(i, 2, item_lat)  # Column 2
            self._table_widget.setItem(i, 3, item_lon)  # Column 3
            # self.table_widget.setCellWidget(i, 3, x_offset_spin_bx)
            #  Column 4
            # self.table_widget.setCellWidget(i, 4, y_offset_spin_bx)
            #  Column 5

            # QgsVertex
            vertex_marker = QgsVertexMarker(self._map_canvas)
            vertex_marker.setCenter(QgsPoint(lat, lon))
            if check_box_state is Qt.Checked:
                vertex_marker.setColor(self._green)
                self._vertex_color = self._green
            elif check_box_state is Qt.Unchecked:
                vertex_marker.setColor(self._red)
                self._vertex_color = self._red

            # Add vertex to dictionary
            self._vertex_dict[row_counter] = [vertex_marker, lon, lat,
                                             check_box_state]

            # Add vertex to reset dictionary
            self._reset_vertex_dict[row_counter] = [vertex_marker,
                                                   self._vertex_color,
                                                   chk_bx_tb_widget_item,
                                                   check_box_state]

            if chk_bx_tb_widget_item.checkState() == Qt.Checked:
                self._prv_chkbx_itm_placeholder_dict[i] = chk_bx_tb_widget_item
            else:
                pass

            row_counter += 1

            if self._active_layer_geometry_typ == 0:
                check_box_state = Qt.Unchecked
            elif self._active_layer_geometry_typ == 1:
                check_box_state = Qt.Checked
            elif self._active_layer_geometry_typ == 2:
                check_box_state = Qt.Checked

        # QMessageBox.information(
        # None, "STDM", "{0} {1} {2}".format(layer_list,
        # self.active_layer_geometry_typ, self.temp_layer_type))

        if self._active_layer_geometry_typ == 0:
            for feat in layer_list:
                fet.setGeometry(QgsGeometry.fromPoint(feat))
                pr.addFeatures([fet])

        elif self._active_layer_geometry_typ == 1:
            fet.setGeometry(QgsGeometry.fromPolyline(layer_list))
            pr.addFeatures([fet])

        elif self._active_layer_geometry_typ == 2:
            layer_list.append(layer_list[0])
            fet.setGeometry(QgsGeometry.fromPolygon([layer_list]))
            pr.addFeatures([fet])

        self._vl.commitChanges()
        self._vl.updateExtents()

        QgsMapLayerRegistry.instance().addMapLayer(self._vl)

        # Align table widget content to fit to header size
        self._table_widget.resizeColumnsToContents()
        # self.table_widget.resizeRowsToContents()
        self._table_widget.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Enable selection if entire row
        self._table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)

        #
        # self.table_widget.setFixedSize(
        # self.table_widget.horizontalHeader().length() + 60, )
        # self.table_widget.setMaximumWidth(
        # self.table_widget.horizontalHeader().length() + 60)

        # Update Extent to new QgsVertext position
        x_min, x_max, y_min, y_max = self._layer_gpx.GetExtent()
        # self.map_canvas.clearExtentHistory()
        extent = QgsRectangle(x_min, y_min, x_max, y_max)
        extent.scale(1.1)
        self._map_canvas.setExtent(extent)
        self._map_canvas.refresh()

        # Show GPX table
        self._table_widget.show()

    @pyqtSlot('QTableWidgetItem')
    def gpx_table_widget_item_pressed(self, item):
        """
        Run when table row is selected
        """
        self._table_pressed_status = True
        # QMessageBox.information(
        # None, "STDM", "{0} {1}".format("Row pressed",
        # self.table_pressed_status))

    @pyqtSlot('QTableWidgetItem')
    def gpx_table_widget_item_selection_changed(self):
        """
        Signal run when table item selection changes
        """
        self._table_select_status = True

        # # QMessageBox.information(
        # None, "STDM", "{0} {1}".format(
        # "Selection has changed", self.table_pressed_status))
        # self.list_of_selected_rows = []  # Clear selected list row
        #
        # self.list_of_selected_items = self.table_widget.selectedItems()
        #
        # # Adding selected items to list_of_selected_rows
        # for itm in self.list_of_selected_items:
        #     selected_item_row = itm.row()
        #     self.list_of_selected_rows.append(selected_item_row)
        #
        # # Getting unique row of selected items rows
        # unique_rows = list(OrderedDict.fromkeys(self.list_of_selected_rows))
        #
        # # QMessageBox.information(
        # None, "STDM", "{0} {1}".format("Items state", self.vertex_dict))
        #
        # for row, vertex in self.vertex_dict.iteritems():
        #
        #     if row in unique_rows:
        #         vertex[0].setColor(self.black)
        #         vertex[0].setIconType(3)
        #         self.map_canvas.refresh()
        #
        #     elif row not in unique_rows and self.active_layer_geometry_typ
        #  == 0:
        #         vertex[0].setColor(self.red)
        #         vertex[0].setIconType(2)
        #         self.map_canvas.refresh()
        #
        #     elif row not in unique_rows and self.active_layer_geometry_typ
        #  in (1,2):
        #         vertex[0].setColor(self.green)
        #         vertex[0].setIconType(2)
        #         self.map_canvas.refresh()
        #
        #     if self.active_layer_geometry_typ == 0:
        #         for item_row, chkbx_item in
        # self.prv_chkbx_itm_placeholder_dict.iteritems():
        #             if item_row == row:
        #                 vertex[0].setColor(self.green)
        #                 vertex[0].setIconType(2)
        #                 self.map_canvas.refresh()
        #                 self.table_pressed_status = False
        #
        #     # if vertex[3] is Qt.Checked:
        #     #     vertex[0].setColor(self.green)
        #     #     vertex[0].setIconType(2)
        #     #     self.map_canvas.refresh()
        #     #
        #     # elif vertex[3] is Qt.Unchecked and row in unique_rows:
        #     #     vertex[0].setColor(self.black)
        #     #     vertex[0].setIconType(3)
        #     #     self.map_canvas.refresh()
        #
        #     # else:
        #     #     vertex[0].setColor(self.red)
        #     #     vertex[0].setIconType(2)
        #     #     self.map_canvas.refresh()
        #
        #     # vertex[0].setColor(self.red)
        #     # vertex[0].setIconType(2)
        #     #
        #     # if row in unique_rows:
        #     #     vertex[0].setColor(self.black)
        #     #     vertex[0].setIconType(3)
        #     #     self.map_canvas.refresh()
        #     #
        #     # if self.active_layer_geometry_typ == 0:
        #     #     for item_row, chkbx_item in
        # self.prv_chkbx_itm_placeholder_dict.iteritems():
        #     #         if item_row == row:
        #     #             vertex[0].setColor(self.green)
        #     #             vertex[0].setIconType(2)
        #     #             self.map_canvas.refresh()

    @pyqtSlot('QTableWidgetItem')
    def gpx_table_widget_item_clicked(self, item):
        """
        Run when table checkbox column is clicked
        """
        # QMessageBox.information(
        # None, "STDM", "{0} table status {1}".format(
        # "Checkbox clicked", self.table_pressed_status))

        # First check if row is pressed to avoid running twice pressed and
        # clicked actions
        if self._table_pressed_status:
            pass

        elif not self._table_pressed_status or self._table_select_status:
            # QMessageBox.information(
            # None, "STDM", "{0} {1}".format("Items state", self.vertex_dict))
            # If table row is not pressed maintain presses status at False

            # Check if import layer is a point
            if self._active_layer_geometry_typ == 0:

                # Do not allow deselection of checkbox item if non exists
                for item_row, chkbx_item in \
                        self._prv_chkbx_itm_placeholder_dict.iteritems():
                    if chkbx_item.checkState() == Qt.Unchecked:
                        QMessageBox.information(
                            None, "STDM", "{0}".format("You must select "
                                                       "atleast one point"))
                        chkbx_item.setCheckState(Qt.Checked)

            if item.checkState() == Qt.Checked:
                for row, vertex in self._vertex_dict.iteritems():
                    if row == item.row():

                        # Set vertex marker green then refresh the map
                        vertex[0].setColor(self._green)
                        vertex[0].setIconType(2)
                        vertex[3] = Qt.Checked
                        self._map_canvas.refresh()

                        if self._active_layer_geometry_typ == 0:
                            for item_row, chkbx_item in \
                                self._prv_chkbx_itm_placeholder_dict.\
                                    iteritems():
                                self._vertex_dict[item_row][0].setColor(
                                    self._red)
                                self._vertex_dict[item_row][0].setIconType(2)
                                self._vertex_dict[item_row][3] = Qt.Unchecked
                                chkbx_item.setCheckState(Qt.Unchecked)
                                self._map_canvas.refresh()

                        else:
                            pass

            elif item.checkState() == Qt.Unchecked:
                for row, vertex_lon_lat_state in self._vertex_dict.iteritems():
                    if row == item.row():
                        vertex_lon_lat_state[0].setColor(self._red)
                        self._map_canvas.refresh()

            if self._active_layer_geometry_typ == 0:
                # Empty previous checkbox item place holder
                self._prv_chkbx_itm_placeholder_dict = {}

                # Add current checked checkbox item
                self._prv_chkbx_itm_placeholder_dict[item.row()] = item

            else:
                pass
        self._table_pressed_status = False
        self._table_select_status = False

    @pyqtSlot()
    def on_bt_reset_clicked(self):
        """
        Run when reset button is clicked
            """
        for key, vertex in self._reset_vertex_dict.iteritems():
            vertex[0].setColor(vertex[1])
            vertex[0].setIconType(2)
            vertex[2].setCheckState(vertex[3])
        self._map_canvas.refresh()

    @pyqtSlot(bool)
    def on_bt_save_clicked(self):
        """
        Run when Qtablewidget button save is clicked
        """
        geom_list = []

        for key, vertex in self._vertex_dict.iteritems():
            if vertex[3] == Qt.Checked:
                geom_list.append(QgsPoint(vertex[2], vertex[1]))

        if self._active_layer_geometry_typ == 0:
            geom = QgsGeometry.fromPoint(geom_list[0])
        elif self._active_layer_geometry_typ == 1:
            geom = QgsGeometry.fromPolyline(geom_list)
        elif self._active_layer_geometry_typ == 2:
            geom = QgsGeometry.fromPolygon([geom_list])

        geom_wkb = geom.exportToWkt()

        non_sp_colms = non_spatial_table_columns(self._sp_table)

        for key, vertex in self._vertex_dict.iteritems():
            self._map_canvas.scene().removeItem(vertex[0])
        # id = self.vl.id()
        # QgsMapLayerRegistry.instance().removeMapLayer(id)
        self.close()

        self._curr_layer = vector_layer(
            self._sp_table, geom_column=self._sp_col)

        self._iface.mapCanvas().setExtent(self._curr_layer.extent())

        self._iface.mapCanvas().refresh()

        self._gpx_add_attribute_info = GPXAttributeInfoDialog(self._iface,
                                                             self._curr_layer,
                                                             non_sp_colms,
                                                             self._sp_table,
                                                             self._sp_col,
                                                             geom_wkb)
        self._gpx_add_attribute_info.create_attribute_info_gui()
        self._gpx_add_attribute_info.show()
        # self.active_layer.setEditForm()

    def closeEvent(self, QCloseEvent):
        id = self._vl.id()
        for key, vertex in self._vertex_dict.iteritems():
            self._map_canvas.scene().removeItem(vertex[0])
        QgsMapLayerRegistry.instance().removeMapLayer(id)
        self._map_canvas.refresh()
        self.close()
