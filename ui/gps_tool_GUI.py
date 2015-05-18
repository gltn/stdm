from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from ui_gps_tool import Ui_Dialog
from osgeo import ogr
from ..utils import util
from gpx_table import GPXTableDialog

class GPSToolDialog(QDialog, Ui_Dialog):

    def __init__(self, iface):
        QDialog.__init__(self, iface.mainWindow())
        self.setupUi(self)
        self.iface = iface
        self.button_ok = self.buttonBox.button(QDialogButtonBox.Ok)
        self.button_cancel = self.buttonBox.button(QDialogButtonBox.Close)
        self.rd_button_group = QButtonGroup()
        self.rd_button_group.addButton(self.rd_gpx_waypoints)
        self.rd_button_group.addButton(self.rd_gpx_tracks)
        self.rd_button_group.addButton(self.rd_gpx_routes)
        self.rd_list = [self.rd_gpx_waypoints, self.rd_gpx_tracks, self.rd_gpx_routes]
        self.button_ok.setEnabled(False)
        self.gpx_table = GPXTableDialog(self.iface)
        self.layer_gpx = None
        self.selected_rd_btn = None

    @pyqtSignature("")
    def on_bn_gpx_select_file_clicked(self):
        """
        Run when browse button is pressed
        """
        self.tx_fl_edit_gpx.clear()
        (gpx_file, encoding) = util.openDialog(self)
        self.tx_fl_edit_gpx.setText(gpx_file)
        self.button_ok.setEnabled(True)

    def accept(self):
        """
        Executed when Ok button is pressed
        """
        if self.tx_fl_edit_gpx.text() == "":
            QMessageBox.information(None,"STDM","Enter or select valid GPX file")

        else:
            gpx_file = self.tx_fl_edit_gpx.text()
            for radio in self.rd_list:
                if radio.isChecked():
                    self.selected_rd_btn = str(radio.objectName())
                    break
                else:
                    continue

            # Open GPX file
            data_source = ogr.Open(gpx_file)

            if self.selected_rd_btn.endswith("waypoints"):
                self.layer_gpx = data_source.GetLayerByName('waypoints')
            elif self.selected_rd_btn.endswith("tracks"):
                self.layer_gpx = data_source.GetLayerByName('track_points')
            elif self.selected_rd_btn.endswith("routes"):
                self.layer_gpx = data_source.GetLayerByName('route_points')

            # Check if gpx layer has points
            if self.layer_gpx.GetFeatureCount() == 0:
                QMessageBox.information(None,"STDM","Selected layer has no features")

            else:
                active_layer = self.iface.activeLayer()
                if not active_layer.isEditable():
                    QMessageBox.warning(None,"STDM",
                                        "Current layer is not in edit mode, toogle start editing, to be able to import")
                else:
                    # Close import dialog to show table
                    self.close_gui()
                    # QtableWidget table population
                    self.gpx_table.tableWidget.setRowCount(self.layer_gpx.GetFeatureCount())
                    self.gpx_table.tableWidget.setColumnCount(5)
                    self.gpx_table.tableWidget.setHorizontalHeaderLabels(["Remove", "lat", "lon", "x-offset","y-offset"])
                    for i, row in enumerate(self.layer_gpx):
                        # Get point lon lat from GPX file
                        lat, lon, ele = row.GetGeometryRef().GetPoint()
                        item_lat = QTableWidgetItem(str(lat))
                        item_lon = QTableWidgetItem(str(lon))

                        vertex_marker = QgsVertexMarker(self.iface.mapCanvas())
                        vertex_marker.setCenter(QgsPoint(lat, lon))

                        # Center checkbox item
                        chk_bx_widget = QWidget()
                        chk_bx = QCheckBox()
                        chk_bx.setCheckState(Qt.Checked)
                        lay_out = QHBoxLayout(chk_bx_widget)
                        lay_out.addWidget(chk_bx)
                        lay_out.setAlignment(Qt.AlignCenter)
                        lay_out.setContentsMargins(0,0,0,0)
                        chk_bx_widget.setLayout(lay_out)

                        # Spinbox for lat and lon offset
                        x_offset_spin_bx = QSpinBox()

                        y_offset_spin_bx = QSpinBox()

                        # Add items to QTable widget
                        self.gpx_table.tableWidget.setCellWidget(i, 0, chk_bx_widget)
                        self.gpx_table.tableWidget.setItem(i, 1, item_lat)
                        self.gpx_table.tableWidget.setItem(i, 2, item_lon)
                        self.gpx_table.tableWidget.setCellWidget(i, 3, x_offset_spin_bx)
                        self.gpx_table.tableWidget.setCellWidget(i, 4, y_offset_spin_bx)

                    self.gpx_table.show()

    def get_gpx_file(self):
        return self.tx_fl_edit_gpx.text()

    def close_gui(self):
        self.close()