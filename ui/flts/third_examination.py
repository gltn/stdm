"""
/***************************************************************************
Name                 : Third Examination Widget
Description          : A widget for performing third examination  on a scheme.
Date                 : 07/August/2019
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
from stdm.ui.flts.workflow_manager.ui_workflow_manager import Ui_WorkflowManagerWidget


class ThirdExaminationWidget(QWidget, Ui_WorkflowManagerWidget):
    """
    Manages Third Examination notifications and workflow
    """
    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)

        self.setupUi(self)

        self.setWindowTitle("Third Workflow Manager")
        self.setObjectName("thirdExamination")
        # self.model = SchemeModel(session, entityModels)  # table model
        # self.schemeTableView.setModel(self.model)

        # self.schemeTableView.setSelectionMode(QTableView.SingleSelection)
        # self.schemeTableView.setSelectionBehavior(QTableView.SelectRows)
        # self.schemeTableView.resizeColumnsToContents()
