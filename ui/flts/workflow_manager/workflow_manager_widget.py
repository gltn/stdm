"""
/***************************************************************************
Name                 : Workflow Manager Widget
Description          : Widget for managing workflow and notification in
                       Scheme Establishment and First, Second and
                       Third Examination FLTS modules.
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
# from sqlalchemy import exc
# from stdm.data.configuration import entity_model
# from stdm.settings import current_profile
# from stdm.ui.flts.workflow_manager.workflow_manager_mvc import WorkflowManagerModel
from stdm.ui.flts.workflow_manager.ui_workflow_manager import Ui_WorkflowManagerWidget


class WorkflowManagerWidget(QWidget, Ui_WorkflowManagerWidget):
    """
    Manages workflow and notification in Scheme Establishment and
    First, Second and Third Examination FLTS modules
    """
    def __init__(self, title, object_name, parent=None):
        super(QWidget, self).__init__(parent)

        self.setupUi(self)
        self.setWindowTitle(title)
        self.setObjectName(object_name)
        # self._profile = current_profile()
        # self._entity = self._profile.entity("Scheme")
        # self._entity_model = entity_model(self._entity)
        #
        # if self._entity_model is None:
        #     QMessageBox.critical(
        #         self,
        #         self.tr('{} Entity Model'.format(self._entity.short_name)),
        #         self.tr("The {} entity model could not be generated.".format(self._entity.short_name))
        #     )
        #     self.reject()
        # self.model = WorkflowManagerModel(self._entity_model)
        # self.table_view = QTableView()
        # self.table_view.setModel(self.model)
        # self.table_view.setSelectionMode(QTableView.SingleSelection)
        # self.table_view.setSelectionBehavior(QTableView.SelectRows)

        # self.schemeTableView.resizeColumnsToContents()

    #     QTimer.singleShot(0, self.initial_load)
    #
    # def initial_load(self):
    #     try:
    #         self.model.load()
    #         print(0)
    #     except exc.SQLAlchemyError as sql_error:
    #         QMessageBox.critical(
    #             self,
    #             self.tr('{} Entity Model'.format(self._entity.short_name)),
    #             self.tr("{0}s failed to load: {1}".format(self._entity.short_name, sql_error))
    #         )
    #         self.reject()
    #     except Exception as e:
    #         QMessageBox.critical(
    #             self,
    #             self.tr('{} Entity Model'.format(self._entity.short_name)),
    #             self.tr("{0}s failed to load: {1}".format(self._entity.short_name, e))
    #         )
    #         self.reject()

        # self.model.sortByName()
        # self.resizeColumns()