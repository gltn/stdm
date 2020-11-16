"""
/***************************************************************************
Name                 : SpatialUnitsTenureDialog
Description          : Dialog for matching tenure types to spatial units.
Date                 : 11/July/2017
copyright            : (C) 2017 by UN-Habitat and implementing partners.
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
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHeaderView
)

from stdm.ui.gui_utils import GuiUtils

WIDGET, BASE = uic.loadUiType(
    GuiUtils.get_ui_file_path('wizard/ui_spatial_unit_tenure_dialog.ui'))


class SpatialUnitTenureTypeDialog(WIDGET, BASE):
    """
    Dialog for defining configuration settings for the
    RelatedTableTranslator class implementation.
    """

    def __init__(self, parent=None, editable=True):
        """
        Class constructor.
        :param parent: Dialog parent.
        :type parent: QObject
        :param editable: Whether the spatial unit tenure mappings can be
        specified. Default is True.
        :type editable: bool
        """
        super(SpatialUnitTenureTypeDialog, self).__init__(parent)
        self.setupUi(self)

        hv = self.sp_tenure_view.horizontalHeader()
        hv.setResizeMode(QHeaderView.Interactive)
        hv.setStretchLastSection(True)

        self._add_headers()

        # Adjust first column width
        hv.resizeSection(0, 100)

        self.sp_tenure_view.clear_view()

        self.sp_tenure_view.add_empty_row = False

        # Disable changing the spatial unit
        # self.sp_tenure_view.disable_editing_column = 0

        self._sp_units, self._t_types = [], []

        if not editable:
            self._disable_editing()

    def _add_headers(self):
        # Configure the list table view
        sp_unit_header = self.tr('Spatial Unit')
        t_type_header = self.tr('Tenure Type')

        self.sp_tenure_view.set_header_labels(
            [sp_unit_header, t_type_header]
        )

    def init(self, spatial_units_tenures):
        """
        Adds the spatial units and corresponding tenure types to the
        respective combo boxes.
        :param spatial_units_tenures: Two-dimensional list containing the
        spatial unit names and tenure type names.
        :type spatial_units_tenures: list
        """
        self._sp_units = spatial_units_tenures[0]
        self._t_types = spatial_units_tenures[1]

        # Add spatial units and tenure types to the table view.
        self.sp_tenure_view.set_combo_selection(spatial_units_tenures, False)

    def set_spatial_unit_tenure_type(self, spatial_unit, tenure_type):
        """
        Set the tenure type for the given spatial unit. Both values need
        to exist in the collection of spatial units and tenure types
        respectively.
        :param spatial_unit: Name of the spatial unit.
        :type spatial_unit: str
        :param tenure_type: Name of the tenure type lookup.
        :type tenure_type: str
        """
        if spatial_unit in self._sp_units and tenure_type in self._t_types:
            self.sp_tenure_view.append_data_row(spatial_unit, tenure_type)

    def _disable_editing(self):
        """
        Disable editing of spatial unit tenure type mappings.
        """
        ok_btn = self.buttonBox.button(QDialogButtonBox.Ok)
        ok_btn.setEnabled(False)
        self.sp_tenure_view.setEnabled(False)

    def tenure_mapping(self):
        """
        :return: Returns a collection containing spatial unit names and
        their corresponding tenure types.
        :rtype: dict
        """
        return self.sp_tenure_view.column_pairings()
