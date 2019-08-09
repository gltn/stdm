"""
/***************************************************************************
Name                 : Scheme Lodgement Wizard
Description          : Dialog for lodging a new scheme.
Date                 : 01/July/2019
copyright            : (C) 2019
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
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ui_scheme_manager import Ui_SchemeManagerDlg
from scheme_model import SchemeModel


class SchemeManagerDlg(QDialog, Ui_SchemeManagerDlg):
    """
    Dialog that manages all scheme pipelines; establishment and, first and
    second examination
    """

    def __init__(self, iface_, parent=None):
        QDialog.__init__(self, parent)

        self.setupUi(self)

        # self.model = SchemeModel(session, entityModels)  # table model
        # self.schemeTableView.setModel(self.model)

        self.schemeTableView.setSelectionMode(QTableView.SingleSelection)
        self.schemeTableView.setSelectionBehavior(QTableView.SelectRows)
        self.schemeTableView.resizeColumnsToContents()
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 3)
