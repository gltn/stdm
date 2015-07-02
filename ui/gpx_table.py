from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from collections import OrderedDict

from ..data import (non_spatial_table_columns,
                    vector_layer)

from ui_gpx_table_widget import Ui_Dialog

from gpx_add_attribute_info import GPXAttributeInfoDialog


class GpxTableWidgetDialog(QDialog, Ui_Dialog):
    def __init__(self, iface, curr_layer, gpx_file, active_layer, active_layer_geom, sp_table, sp_col):
        QDialog.__init__(self, iface.mainWindow())
        self.setupUi(self)
        self.iface = iface
        self.curr_layer = curr_layer
        self.sp_table = sp_table
        self.sp_col = sp_col
        self.table_widget = self.tableWidget
        self.map_canvas = self.iface.mapCanvas()
        self.layer_gpx = gpx_file
        self.active_layer = active_layer
        self.green = QColor(0, 255, 0)
        self.red = QColor(255, 0, 0)
        self.black = QColor(0, 0, 0)
        self.vertex_color = QColor(0, 0, 0)
        self.active_layer_geometry_typ = active_layer_geom
        self.vertex_dict = {}
        self.reset_vertex_dict = {}
        self.gpx_tw_item_initial_state = Qt.Checked
        self.prv_chkbx_itm_placeholder_dict = {}
        self.table_widget.itemPressed.connect(self.gpx_table_widget_item_pressed)
        self.table_widget.itemClicked.connect(self.gpx_table_widget_item_clicked)
        self.table_widget.itemSelectionChanged.connect(self.gpx_table_widget_item_selection_changed)
        self.table_pressed_status = False
        self.table_select_status = False
        self.check_box_clicked_state = False
        self.list_of_selected_rows = []
        self.pressed_item_list = []
        self.gpx_add_attribute_info = None
        self.label = None
        self.vl = None

    def populate_qtable_widget(self):
        check_box_state = Qt.Checked

        # Populate QTableWidget
        self.table_widget.setRowCount(self.layer_gpx.GetFeatureCount())
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(["",
                                                     "Point Name",
                                                     "Latitude",
                                                     "Longitude",
                                                     # "Lat-Offset",
                                                     # "Long-offset"
                                                     ])
        self.table_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.table_widget.setFocusPolicy(Qt.NoFocus)

        row_counter = 0
        layer_list = []

        if self.active_layer_geometry_typ == 0:
            temp_layer_type = "Point"
        elif self.active_layer_geometry_typ == 1:
            temp_layer_type = "LineString"
        elif self.active_layer_geometry_typ == 2:
            temp_layer_type = "Polygon"

        # create memory layer
        self.vl = QgsVectorLayer("%s?crs=epsg:4326&field=id:integer&index=yes".format(temp_layer_type),
                            "tmp_layer",
                            "memory")
        pr = self.vl.dataProvider()
        self.vl.startEditing()
        fet = QgsFeature()

        for i, row in enumerate(self.layer_gpx):
            # Get point lon lat from GPX file
            lat, lon, ele = row.GetGeometryRef().GetPoint()
            item_lat = QTableWidgetItem(str(lat))
            item_lon = QTableWidgetItem(str(lon))
            self.label = QTableWidgetItem(row.GetFieldAsString(4))

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
            chk_bx_tb_widget_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsSelectable )
            chk_bx_tb_widget_item.setCheckState(check_box_state)

            # Spinbox for lat and lon offset
            x_offset_spin_bx = QSpinBox()
            y_offset_spin_bx = QSpinBox()

            # Add items to QTable widget
            # self.gpx_table.tableWidget.setCellWidget(i, 0, chk_bx_widget)  # Column 1
            self.table_widget.setItem(i, 0, chk_bx_tb_widget_item)  # Column 1
            self.table_widget.setItem(i, 1, self.label)
            self.table_widget.setItem(i, 2, item_lat)  # Column 2
            self.table_widget.setItem(i, 3, item_lon)  # Column 3
            # self.table_widget.setCellWidget(i, 3, x_offset_spin_bx)  # Column 4
            # self.table_widget.setCellWidget(i, 4, y_offset_spin_bx)  # Column 5

            # QgsVertex
            vertex_marker = QgsVertexMarker(self.map_canvas)
            vertex_marker.setCenter(QgsPoint(lat, lon))
            if check_box_state is Qt.Checked:
                vertex_marker.setColor(self.green)
                self.vertex_color = self.green
            elif check_box_state is Qt.Unchecked:
                vertex_marker.setColor(self.red)
                self.vertex_color = self.red

            # Add vertex to dictionary
            self.vertex_dict[row_counter] = [vertex_marker, lon, lat, check_box_state]

            # Add vertex to reset dictionary
            self.reset_vertex_dict[row_counter] = [vertex_marker,
                                                   self.vertex_color,
                                                   chk_bx_tb_widget_item,
                                                   check_box_state]

            if chk_bx_tb_widget_item.checkState() == Qt.Checked:
                self.prv_chkbx_itm_placeholder_dict[i] = chk_bx_tb_widget_item
            else:
                pass

            row_counter += 1

            if self.active_layer_geometry_typ == 0:
                check_box_state = Qt.Unchecked
            elif self.active_layer_geometry_typ == 1:
                check_box_state = Qt.Checked
            elif self.active_layer_geometry_typ == 2:
                check_box_state = Qt.Checked



        if self.active_layer_geometry_typ == 0:
            for feat in layer_list:
                fet.setGeometry(QgsGeometry.fromPoint(feat))
                pr.addFeatures([fet])

        elif self.active_layer_geometry_typ == 1:
            fet.setGeometry(QgsGeometry.fromPolyline(layer_list))
            pr.addFeatures([fet])

        elif self.active_layer_geometry_typ == 2:
            layer_list.append(layer_list[0])
            fet.setGeometry(QgsGeometry.fromPolygon([layer_list]))
            pr.addFeatures([fet])

        self.vl.commitChanges()
        self.vl.updateExtents()

        QgsMapLayerRegistry.instance().addMapLayer(self.vl)

        # Align table widget content to fit to header size
        self.table_widget.resizeColumnsToContents()

        # Enable selection if entire row
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)

        #
        # self.table_widget.setFixedSize(self.table_widget.horizontalHeader().length() + 60, )
        self.table_widget.setMaximumWidth(self.table_widget.horizontalHeader().length() + 60)

        # Update Extent to new QgsVertext position
        x_min, x_max, y_min, y_max = self.layer_gpx.GetExtent()
        # self.map_canvas.clearExtentHistory()
        extent = QgsRectangle(x_min, y_min, x_max, y_max)
        extent.scale(1.1)
        self.map_canvas.setExtent(extent)
        self.map_canvas.refresh()

        # Show GPX table
        self.table_widget.show()

    @pyqtSlot('QTableWidgetItem')
    def gpx_table_widget_item_pressed(self, item):
        """
        Run when table row is selected
        """
        self.table_pressed_status = True
        # QMessageBox.information(None, "STDM", "{0} {1}".format("Row pressed", self.table_pressed_status))

    @pyqtSlot('QTableWidgetItem')
    def gpx_table_widget_item_selection_changed(self):
        """
        Signal run when table item selection changes
        """
        self.table_select_status = True

        # # QMessageBox.information(None, "STDM", "{0} {1}".format("Selection has changed", self.table_pressed_status))
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
        # # QMessageBox.information(None, "STDM", "{0} {1}".format("Items state", self.vertex_dict))
        #
        # for row, vertex in self.vertex_dict.iteritems():
        #
        #     if row in unique_rows:
        #         vertex[0].setColor(self.black)
        #         vertex[0].setIconType(3)
        #         self.map_canvas.refresh()
        #
        #     elif row not in unique_rows and self.active_layer_geometry_typ == 0:
        #         vertex[0].setColor(self.red)
        #         vertex[0].setIconType(2)
        #         self.map_canvas.refresh()
        #
        #     elif row not in unique_rows and self.active_layer_geometry_typ in (1,2):
        #         vertex[0].setColor(self.green)
        #         vertex[0].setIconType(2)
        #         self.map_canvas.refresh()
        #
        #     if self.active_layer_geometry_typ == 0:
        #         for item_row, chkbx_item in self.prv_chkbx_itm_placeholder_dict.iteritems():
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
        #     #     for item_row, chkbx_item in self.prv_chkbx_itm_placeholder_dict.iteritems():
        #     #         if item_row == row:
        #     #             vertex[0].setColor(self.green)
        #     #             vertex[0].setIconType(2)
        #     #             self.map_canvas.refresh()

    @pyqtSlot('QTableWidgetItem')
    def gpx_table_widget_item_clicked(self, item):
        """
        Run when table checkbox column is clicked
        """
        # QMessageBox.information(None, "STDM", "{0} table status {1}".format("Checkbox clicked", self.table_pressed_status))

        # First check if row is pressed to avoid running twice pressed and clicked actions
        if self.table_pressed_status:
            pass

        elif not self.table_pressed_status or self.table_select_status:
            # QMessageBox.information(None, "STDM", "{0} {1}".format("Items state", self.vertex_dict))
            # If table row is not pressed maintain presses status at False

            # Check if import layer is a point
            if self.active_layer_geometry_typ == 0:

                # Do not allow deselection of checkbox item if non exists
                for item_row, chkbx_item in self.prv_chkbx_itm_placeholder_dict.iteritems():
                    if chkbx_item.checkState() == Qt.Unchecked:
                        QMessageBox.information(None,"STDM","{0}".format("You must select atleast one point"))
                        chkbx_item.setCheckState(Qt.Checked)


            if item.checkState() == Qt.Checked:
                for row, vertex in self.vertex_dict.iteritems():
                    if row == item.row():

                        # Set vertex marker green then refresh the map
                        vertex[0].setColor(self.green)
                        vertex[0].setIconType(2)
                        vertex[3] = Qt.Checked
                        self.map_canvas.refresh()

                        if self.active_layer_geometry_typ == 0:
                            for item_row, chkbx_item in self.prv_chkbx_itm_placeholder_dict.iteritems():
                                self.vertex_dict[item_row][0].setColor(self.red)
                                self.vertex_dict[item_row][0].setIconType(2)
                                self.vertex_dict[item_row][3] = Qt.Unchecked
                                chkbx_item.setCheckState(Qt.Unchecked)
                                self.map_canvas.refresh()

                        else:
                            pass

            elif item.checkState() == Qt.Unchecked:
                for row, vertex_lon_lat_state in self.vertex_dict.iteritems():
                    if row == item.row():
                        vertex_lon_lat_state[0].setColor(self.red)
                        self.map_canvas.refresh()


            if self.active_layer_geometry_typ == 0:
                # Empty previous checkbox item place holder
                self.prv_chkbx_itm_placeholder_dict = {}

                # Add current checked checkbox item
                self.prv_chkbx_itm_placeholder_dict[item.row()] = item

            else:
                pass
        self.table_pressed_status = False
        self.table_select_status = False

    @pyqtSlot()
    def on_bt_reset_clicked(self):
        """
        Run when reset button is clicked
            """
        for key, vertex in self.reset_vertex_dict.iteritems():
            vertex[0].setColor(vertex[1])
            vertex[0].setIconType(2)
            vertex[2].setCheckState(vertex[3])
        self.map_canvas.refresh()


    @pyqtSlot(bool)
    def on_bt_save_clicked(self):
        """
        Run when Qtablewidget button save is clicked
        """
        geom_list = []

        for key, vertex in self.vertex_dict.iteritems():
            if vertex[3] == Qt.Checked:
                geom_list.append(QgsPoint(vertex[1], vertex[2]))

        if self.active_layer_geometry_typ == 0:
            geom = QgsGeometry.fromPoint(geom_list[0])
        elif self.active_layer_geometry_typ == 1:
            geom = QgsGeometry.fromPolyline(geom_list)
        elif self.active_layer_geometry_typ == 2:
            geom = QgsGeometry.fromPolygon([geom_list])

        geom_wkb = geom.exportToWkt()

        non_sp_colms = non_spatial_table_columns(self.sp_table)

        for key, vertex in self.vertex_dict.iteritems():
            self.map_canvas.scene().removeItem(vertex[0])
        # id = self.vl.id()
        # QgsMapLayerRegistry.instance().removeMapLayer(id)
        self.close()

        self.curr_layer = vector_layer(self.sp_table, geom_column=self.sp_col)

        self.iface.mapCanvas().setExtent(self.curr_layer.extent())

        self.iface.mapCanvas().refresh()

        self.gpx_add_attribute_info = GPXAttributeInfoDialog(self.iface,
                                                             self.curr_layer,
                                                             non_sp_colms,
                                                             self.sp_table,
                                                             self.sp_col,
                                                             geom_wkb)
        self.gpx_add_attribute_info.create_attribute_info_gui()
        self.gpx_add_attribute_info.show()
        # self.active_layer.setEditForm()

    def closeEvent(self, QCloseEvent):
        id = self.vl.id()
        for key, vertex in self.vertex_dict.iteritems():
            self.map_canvas.scene().removeItem(vertex[0])
        QgsMapLayerRegistry.instance().removeMapLayer(id)
        self.map_canvas.refresh()
        self.close()