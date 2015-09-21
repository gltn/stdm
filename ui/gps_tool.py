# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Name               :Spatial Unit Manager Import feature from GPX file
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

from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import QDialog, QDialogButtonBox, QButtonGroup, QMessageBox
from ui_gps_tool import Ui_Dialog
from osgeo import ogr
from ..utils import util
from gpx_table import GpxTableWidgetDialog


class GPSToolDialog(QDialog, Ui_Dialog):
    """
    Import GPX file main dialog, implements import from GPX button
    """

    def __init__(self, iface, curr_layer, sp_table, sp_col):
        """Constructor."""
        QDialog.__init__(self, iface.mainWindow())
        self.setupUi(self)
        self._iface = iface
        self._curr_layer = curr_layer
        self._sp_table = sp_table
        self._sp_col = sp_col
        self._button_ok = self.buttonBox.button(QDialogButtonBox.Ok)
        self._button_cancel = self.buttonBox.button(QDialogButtonBox.Close)
        self._rd_button_group = QButtonGroup()
        self._rd_button_group.addButton(self.rd_gpx_waypoints)
        self._rd_button_group.addButton(self.rd_gpx_tracks)
        self._rd_button_group.addButton(self.rd_gpx_routes)
        self._rd_list = [self.rd_gpx_waypoints, self.rd_gpx_tracks,
                        self.rd_gpx_routes]
        self._button_ok.setEnabled(False)
        self._layer_gpx = None
        self._selected_rd_btn = None
        self._gpx_table = None
        self._gpx_tw_item_chg_st_dict = {}
        self._map_canvas = self._iface.mapCanvas()

    @pyqtSlot()
    def on_bn_gpx_select_file_clicked(self):
        """
        Run when browse button is pressed
        """
        self.tx_fl_edit_gpx.clear()
        (gpx_file, encoding) = util.open_dialog(self)
        self.tx_fl_edit_gpx.setText(gpx_file)
        self._button_ok.setEnabled(True)

    def accept(self):
        """
        Executed when Ok button is pressed
        """
        if self.tx_fl_edit_gpx.text() == "":
            QMessageBox.information(
                None, "STDM", "Enter or select valid GPX file")

        else:
            gpx_file = self.tx_fl_edit_gpx.text()
            for radio in self._rd_list:
                if radio.isChecked():
                    self._selected_rd_btn = str(radio.objectName())
                    break
                else:
                    continue

            # Open GPX file
            data_source = ogr.Open(gpx_file)

            if self._selected_rd_btn.endswith("waypoints"):
                self._layer_gpx = data_source.GetLayerByName('waypoints')
            elif self._selected_rd_btn.endswith("tracks"):
                self._layer_gpx = data_source.GetLayerByName('track_points')
            elif self._selected_rd_btn.endswith("routes"):
                self._layer_gpx = data_source.GetLayerByName('route_points')

            # Check if gpx layer has points
            if self._layer_gpx.GetFeatureCount() == 0:
                QMessageBox.information(
                    None, "STDM", "The selected feature type has no layer")

            else:
                active_layer = self._iface.activeLayer()
                active_layer_geometry_typ = int(active_layer.geometryType())

                if not active_layer.isEditable():
                    QMessageBox.warning(
                        None, "STDM", "Current layer is not in edit mode, "
                                      "toogle start editing, to be able to "
                                      "import")
                else:

                    # Close import dialog to show table
                    self._close_gpx_select_file_gui()

                    # QTableWidget dialog
                    self._gpx_table = GpxTableWidgetDialog(
                        self._iface, self._curr_layer, self._layer_gpx,
                        active_layer, active_layer_geometry_typ,
                        self._sp_table, self._sp_col)
                    self._gpx_table.populate_qtable_widget()
                    self._gpx_table.show()

    def get_gpx_file(self):
        return self.tx_fl_edit_gpx.text()

    def _close_gpx_select_file_gui(self):
        """
        Closes GPX import dialog
        """
        self.close()
