from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import qgis
from ui_gps_tool import Ui_Dialog
from osgeo import ogr
from ..utils import util
from gpx_table import GpxTableWidgetDialog


class GPSToolDialog(QDialog, Ui_Dialog):

    def __init__(self, iface, curr_layer, sp_table, sp_col):
        QDialog.__init__(self, iface.mainWindow())
        self.setupUi(self)
        self.iface = iface
        self.curr_layer = curr_layer
        self.sp_table = sp_table
        self.sp_col = sp_col
        self.button_ok = self.buttonBox.button(QDialogButtonBox.Ok)
        self.button_cancel = self.buttonBox.button(QDialogButtonBox.Close)
        self.rd_button_group = QButtonGroup()
        self.rd_button_group.addButton(self.rd_gpx_waypoints)
        self.rd_button_group.addButton(self.rd_gpx_tracks)
        self.rd_button_group.addButton(self.rd_gpx_routes)
        self.rd_list = [self.rd_gpx_waypoints, self.rd_gpx_tracks, self.rd_gpx_routes]
        self.button_ok.setEnabled(False)
        self.layer_gpx = None
        self.selected_rd_btn = None
        self.gpx_table = None
        self.gpx_tw_item_chg_st_dict = {}
        self.map_canvas = self.iface.mapCanvas()

    @pyqtSlot()
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
            QMessageBox.information(None,"STDM", "Enter or select valid GPX file")

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
                QMessageBox.information(None,"STDM", "The selected feature type has no layer")

            else:
                active_layer = self.iface.activeLayer()
                active_layer_geometry_typ = int(active_layer.geometryType())

                if not active_layer.isEditable():
                    QMessageBox.warning(None,"STDM",
                                        "Current layer is not in edit mode, toogle start editing, to be able to import")
                else:

                    # Close import dialog to show table
                    self.close_gpx_select_file_gui()

                    # QTableWidget dialog
                    self.gpx_table = GpxTableWidgetDialog(self.iface,
                                                          self.curr_layer,
                                                          self.layer_gpx,
                                                          active_layer,
                                                          active_layer_geometry_typ,
                                                          self.sp_table,
                                                          self.sp_col
                                                          )
                    self.gpx_table.populate_qtable_widget()
                    self.gpx_table.show()

    def get_gpx_file(self):
        return self.tx_fl_edit_gpx.text()

    def close_gpx_select_file_gui(self):
        self.close()
