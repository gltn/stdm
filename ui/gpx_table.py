from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

from ui_gpx_table_widget import Ui_Dialog


class GpxTableWidgetDialog(QDialog, Ui_Dialog):
    def __init__(self, iface, gpx_file, active_layer):
        QDialog.__init__(self, iface.mainWindow())
        self.setupUi(self)
        self.iface = iface
        self.table_widget = self.tableWidget
        self.map_canvas = self.iface.mapCanvas()
        self.layer_gpx = gpx_file
        self.active_layer_geometry_typ = active_layer
        self.vertex_dict = {}
        self.gpx_tw_item_initial_state = Qt.Checked
        self.prv_chkbx_itm_placeholder_dict = {}
        self.table_widget.itemPressed.connect(self.gpx_table_widget_item_pressed)
        self.table_widget.itemClicked.connect(self.gpx_table_widget_item_clicked)

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

            # Radio button
            rd_tb_widget_itm = QTableWidgetItem()

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
                vertex_marker.setColor(QColor(0, 255, 0))
            elif check_box_state is Qt.Unchecked:
                vertex_marker.setColor(QColor(255, 0, 0))
            self.vertex_dict[row_counter] = vertex_marker

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
        QMessageBox.information(None,"STDM","{0}".format("item pressed"))

    @pyqtSlot('QTableWidgetItem')
    def gpx_table_widget_item_clicked(self, item):
        """
        Slot run when table item is clicked
        """
        # Check if import layer is a point
        if self.active_layer_geometry_typ == 0:
            for item_row, chkbx_item in self.prv_chkbx_itm_placeholder_dict.iteritems():
                if chkbx_item.checkState() == Qt.Unchecked:
                    QMessageBox.information(None,"STDM","{0}".format("You must select atleast one point"))

        if item.checkState() == Qt.Checked:
            for row, vertex in self.vertex_dict.iteritems():
                if row == item.row():
                    vertex.setColor(QColor(0, 255, 0))
                    self.map_canvas.refresh()

                    if self.active_layer_geometry_typ == 0:
                        for item_row, chkbx_item in self.prv_chkbx_itm_placeholder_dict.iteritems():

                            # Uncheck previous checkbox item
                            chkbx_item.setCheckState(Qt.Unchecked)
                            self.vertex_dict[item_row].setColor(QColor(255, 0, 0))

                    else:
                        pass

        elif item.checkState() == Qt.Unchecked:
            for row, vertex_layertyp_state in self.vertex_dict.iteritems():
                if row == item.row():
                    vertex_layertyp_state[0].setColor(QColor(255, 0, 0))
                    self.map_canvas.refresh()


        if self.active_layer_geometry_typ == 0:
            # Empty previous checkbox item place holder
            self.prv_chkbx_itm_placeholder_dict = {}

            # Add current checked checkbox item
            self.prv_chkbx_itm_placeholder_dict[item.row()] = item

        else:
            pass

    # @pyqtSlot()
    # def on_button_reset_clicked(self):
    #     """
    #     Run when reset button is clicked
    #     """
    #     self.table_widget.close()

    @pyqtSlot(bool)
    def on_bt_save_clicked(self):
        for key, vertex in self.vertex_dict.iteritems():
            self.map_canvas.scene().removeItem(vertex)
            self.close()