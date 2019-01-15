# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : vdc_selection  
Description          : Dialog to select VDC/Ward
Date                 : 01/May/2019
copyright            : (C) 2015 by UN-Habitat and implementing partners.
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
from ui_vdc_selection import Ui_VdcSelection

from PyQt4.QtGui import(
        QDialog,
        QApplication,
        QLabel,
        QPushButton
)

from stdm.ui.admin_unit_selector import AdminUnitSelector
from stdm.data.pg_utils import (
        pg_table_count,
        get_admin_unit_details
        )

class VdcSelector(QDialog, Ui_VdcSelection):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.admin_unit = None
        self.setupUi(self) 
        self.init_gui()

    def init_gui(self):
        self.btnBrowse.clicked.connect(self.open_admin_unit_selection)

    def open_admin_unit_selection(self):
        sel_admin_unit = AdminUnitSelector(self)
        sel_admin_unit.setManageMode(False)
        label = ''
        if sel_admin_unit.exec_() == QDialog.Accepted:
            self.admin_unit = sel_admin_unit.selectedAdminUnit
            if self.admin_unit.Parent is not None:
                label = self.admin_unit.Parent.Code+' '+\
                                self.admin_unit.Parent.Name+' / '+\
                                self.admin_unit.Code
        self.edtVdc.setText(label)

    def parcel_filter(self):
        """
        :param admin_unit: AdminSpatialUnitSet 
        :rtype: str
        """
        if self.admin_unit is None or self.admin_unit.Parent is None:
            return ''
        id = get_admin_unit_details(\
                self.admin_unit.Parent.id,
                self.admin_unit.Code)
        parcel_filter='vdc={} and ward_number={}'.format(self.admin_unit.Parent.id,id)
        return parcel_filter

    def accept(self):
        self.done(1)

    def cancel(self):
        self.done(0)


        
        
        

