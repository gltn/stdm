from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from ui_gps_tool import Ui_Dialog
from osgeo import ogr
from ..utils import util

class GPSToolDialog(QDialog, Ui_Dialog):

    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.button_ok = self.buttonBox.button(QDialogButtonBox.Ok)
        self.button_cancel = self.buttonBox.button(QDialogButtonBox.Close)
        self.rd_button_group = QButtonGroup()
        self.rd_button_group.addButton(self.rd_gpx_waypoints)
        self.rd_button_group.addButton(self.rd_gpx_tracks)
        self.rd_button_group.addButton(self.rd_gpx_routes)
        self.rd_list = [self.rd_gpx_waypoints, self.rd_gpx_tracks, self.rd_gpx_routes]
        self.button_ok.setEnabled(False)
        self.iface = parent

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
        Overrides Qdialog accept and run when okay button is pressesd
        """
        if self.tx_fl_edit_gpx.text() == "":
            QMessageBox.information(None,"STDM","Enter or select valid GPX file")

        else:
            gpx_file = self.tx_fl_edit_gpx.text()
            for radio in self.rd_list:
                if radio.isChecked():
                    selected_rd_btn = str(radio.objectName())
                    break
                else:
                    continue

            # Open GPX file
            data_source = ogr.Open(gpx_file)

            if selected_rd_btn.endswith("waypoints"):
                layer_gpx = data_source.GetLayerByName('waypoints')
            elif selected_rd_btn.endswith("tracks"):
                layer_gpx = data_source.GetLayerByName('track_points')
            elif selected_rd_btn.endswith("routes"):
                layer_gpx = data_source.GetLayerByName('route_points')

            # Check if gpx layer has points
            if layer_gpx.GetFeatureCount() == 0:
                QMessageBox.information(None,"STDM","Selected layer has no features")

            else:
                active_layer = self.iface.activeLayer()
                if not active_layer.isEditable():
                    QMessageBox.warning(None,"STDM",
                                        "Current layer is not in edit mode, toogle start editing, to be able to import")
                else:
                    pass

    def get_gpx_file(self):
        return self.tx_fl_edit_gpx.text()