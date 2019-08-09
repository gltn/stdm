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
from ui_workflow_manager import Ui_WorkflowManagerWidget
# from scheme_model import SchemeModel


class WorkflowManagerDockWidget(QDockWidget):
    """
    Docks Workflow Manager in QGIS window
    """
    def __init__(self, parent=None):
        super(QDockWidget, self).__init__(parent)
        self.setWindowTitle("FLTS Workflow Manager")
        self.setObjectName("WorkflowManagerDockWidget")
        self.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.TopDockWidgetArea)
        workflowManagerObj = WorkflowManager(self)
        self.setWidget(workflowManagerObj)


class WorkflowManager(QWidget, Ui_WorkflowManagerWidget):
    """
    Manages FLTS workflow and notifications on;
    Scheme Establishment and First, Second and Third Examination
    """
    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)

        self.setupUi(self)

        # self.model = SchemeModel(session, entityModels)  # table model
        # self.schemeTableView.setModel(self.model)

        # self.schemeTableView.setSelectionMode(QTableView.SingleSelection)
        # self.schemeTableView.setSelectionBehavior(QTableView.SelectRows)
        # self.schemeTableView.resizeColumnsToContents()

