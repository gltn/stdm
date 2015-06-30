from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from collections import OrderedDict

from ..data import (non_spatial_table_columns)

from ui_gpx_table_widget import Ui_Dialog

from gpx_add_attribute_info import GPXAttributeInfoDialog


class GpxTableWidgetDialog(QDialog, Ui_Dialog):
    def __init__(self, iface, gpx_file, active_layer, active_layer_geom, sp_table, sp_col):
        QDialog.__init__(self, iface.mainWindow())
        self.setupUi(self)
        self.iface = iface
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
        self.table_clicked_status = False
        self.table_select_status = False
        self.check_box_clicked_state = False
        self.list_of_selected_rows = []
        self.pressed_item_list = []
        self.gpx_add_attribute_info = None

    def populate_qtable_widget(self):
        check_box_state = Qt.Checked

        # Populate QTableWidget
        self.table_widget.setRowCount(self.layer_gpx.GetFeatureCount())
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(["", "Latitude", "Longitude", "Lat-Offset", "Long-offset"])
        self.table_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.table_widget.setFocusPolicy(Qt.NoFocus)

        row_counter = 0

        for i, row in enumerate(self.layer_gpx):
            # Get point lon lat from GPX file
            lat, lon, ele = row.GetGeometryRef().GetPoint()
            item_lat = QTableWidgetItem(str(lat))
            item_lon = QTableWidgetItem(str(lon))

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
            chk_bx_tb_widget_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            chk_bx_tb_widget_item.setCheckState(check_box_state)

            # Spinbox for lat and lon offset
            x_offset_spin_bx = QSpinBox()
            y_offset_spin_bx = QSpinBox()

            # Add items to QTable widget
            # self.gpx_table.tableWidget.setCellWidget(i, 0, chk_bx_widget)  # Column 1
            self.table_widget.setItem(i, 0, chk_bx_tb_widget_item)  # Column 1
            self.table_widget.setItem(i, 1, item_lat)  # Column 2
            self.table_widget.setItem(i, 2, item_lon)  # Column 3
            self.table_widget.setCellWidget(i, 3, x_offset_spin_bx)  # Column 4
            self.table_widget.setCellWidget(i, 4, y_offset_spin_bx)  # Column 5

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
        QMessageBox.information(None, "STDM", "{0} \n"
                                              "Clicked status {1} \n"
                                              "Pressed status {2} \n"
                                              "Select status {3}".format("I have been pressed ",
                                                                         self.table_clicked_status,
                                                                         self.table_pressed_status,
                                                                         self.table_select_status))
        self.table_pressed_status = False

    @pyqtSlot('QTableWidgetItem')
    def gpx_table_widget_item_selection_changed(self):
        """
        Signal run when table item selection changes
        """
        self.table_select_status = True
        QMessageBox.information(None, "STDM", "{0} \n"
                                              "Clicked status {1} \n"
                                              "Pressed status {2} \n"
                                              "Select status {3}".format("Selection has changed",
                                                                         self.table_clicked_status,
                                                                         self.table_pressed_status,
                                                                         self.table_select_status))

        self.table_select_status = False


    @pyqtSlot('QTableWidgetItem')
    def gpx_table_widget_item_clicked(self, item):
        """
        Run when table checkbox column is clicked
        """
        self.table_clicked_status = True
        QMessageBox.information(None, "STDM", "{0} \n"
                                              "Clicked status {1} \n"
                                              "Pressed status {2} \n"
                                              "Select status {3}".format("I have been clicked",
                                                                         self.table_clicked_status,
                                                                         self.table_pressed_status,
                                                                         self.table_select_status))
        if self.active_layer_geometry_typ == 0:

            for item_row, chkbx_item in self.prv_chkbx_itm_placeholder_dict.iteritems():

                if item.row() == item_row and item.checkState() != chkbx_item.checkState():
                    QMessageBox.information(None,"STDM","{0}".format("You must select atleast one point"))
                    chkbx_item.setCheckState(Qt.Checked)

                elif item.row() != item_row:

                    chkbx_item.setCheckState(Qt.Unchecked)
                    self.vertex_dict[item_row][0].setColor(self.red)
                    self.map_canvas.refresh()




        elif self.active_layer_geometry_typ in (1,2):
            for row, vertex in self.vertex_dict.iteritems():
                if row == item.row():
                    vertex[0].setColor(self.green)
                    self.map_canvas.refresh()

        self.table_clicked_status = False

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
        self.close()

        self.gpx_add_attribute_info = GPXAttributeInfoDialog(self.iface, non_sp_colms, self.sp_table, self.sp_col,
                                                                 geom_wkb)
        self.gpx_add_attribute_info.create_attribute_info_gui()
        self.gpx_add_attribute_info.show()
        # self.active_layer.setEditForm()

    def closeEvent(self, QCloseEvent):
        for key, vertex in self.vertex_dict.iteritems():
            self.map_canvas.scene().removeItem(vertex[0])
        self.map_canvas.refresh()
        self.close()
