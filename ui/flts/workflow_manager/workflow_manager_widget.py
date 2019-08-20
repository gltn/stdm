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
from sqlalchemy import exc
from sqlalchemy.orm import joinedload
from stdm.data.configuration import entity_model
from stdm.settings import current_profile
from stdm.ui.flts.workflow_manager.scheme_model import SchemeModel
from stdm.ui.flts.workflow_manager.ui_workflow_manager import Ui_WorkflowManagerWidget


class WorkflowManagerWidget(QWidget, Ui_WorkflowManagerWidget):
    """
    Manages workflow and notification in Scheme Establishment and
    First, Second and Third Examination FLTS modules
    """
    setStyleSheet = "QHeaderView::section{" \
                    "border-top:0px solid #D8D8D8;" \
                    "border-left:0px solid #D8D8D8;" \
                    "border-right: 1px solid #D8D8D8;" \
                    "border-bottom: 1px solid #D8D8D8;" \
                    "padding:4px;" \
                    "}" \
                    "QTableCornerButton::section{" \
                    "border-top:0px solid #D8D8D8;" \
                    "border-left:0px solid #D8D8D8;" \
                    "border-right:1px solid #D8D8D8;" \
                    "border-bottom: 1px solid #D8D8D8;" \
                    "background-color:white;" \
                    "}"

    def __init__(self, title, object_name, parent=None):
        super(QWidget, self).__init__(parent)
        self.setupUi(self)
        self._profile = current_profile()
        self.setWindowTitle(title)
        self.setObjectName(object_name)
        self.data_service = SchemeDataService(self._profile)
        self.model = SchemeModel(self.data_service)
        self.table_view = QTableView()
        self.table_view.setModel(self.model)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setShowGrid(False)
        self.table_view.horizontalHeader().setStyleSheet(WorkflowManagerWidget.setStyleSheet)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.tabWidget.insertTab(0, self.table_view, 'Scheme')
        self.initial_load()

    def initial_load(self):
        """
        Initial table view data load
        """
        try:
            self.model.load()
        except (exc.SQLAlchemyError, Exception) as e:
            QMessageBox.critical(  # To be made dynamic
                self,
                self.tr('{} Entity Model'.format(self.model.entity_name)),
                self.tr("{0} failed to load: {1}".format(self.model.entity_name, e))
            )
        else:
            self.table_view.horizontalHeader().setStretchLastSection(True)
            self.table_view.resizeColumnsToContents()


class SchemeDataService:
    """
    Scheme data model services
    """
    config = [
            {'List of Holders': 'view'},
            {'Supporting Document': 'view'},
            {'Number of Scheme': 'scheme_number'},
            {'Name of Scheme': 'scheme_name'},
            {'Date of Approval': 'date_of_approval'},
            {'Date of Establishment': 'date_of_establishment'},
            {'Type of Relevant Authority': {'cb_check_lht_relevant_authority': 'value'}},
            {'Land Rights Office': {'cb_check_lht_land_rights_office': 'value'}},
            {'Region': {'cb_check_lht_region': 'value'}},
            {'Township': 'township_name'},
            {'Registration Division': 'registration_division'},
            {'Block Area': 'area'}
        ]

    def __init__(self, current_profile):
        self._profile = current_profile
        self.entity_name = "Scheme"

    def _entity_model(self):
        """
`       Scheme entity model
        :return model: Scheme entity model;
        :rtype model: DeclarativeMeta
        """
        try:
            self._entity = self._profile.entity(self.entity_name)
            model = entity_model(self._entity)
            return model
        except AttributeError as e:
            raise e

    def related_entity_name(self):
        """
        Related entity name
        :return entity_name: Related entity name
        :rtype entity_name: List
        """
        entity_name = []
        for fk in self._entity_model().__table__.foreign_keys:
            entity_name.append(fk.column.table.name)
        return entity_name

    def run_query(self):
        """
        Run query on an entity
        :return query_object: Query results
        :rtype query_object: Query
        """
        model = self._entity_model()
        entity_object = model()
        try:
            query_object = entity_object.queryObject(). \
                options(joinedload(model.cb_check_lht_land_rights_office)). \
                options(joinedload(model.cb_check_lht_region)). \
                options(joinedload(model.cb_check_lht_relevant_authority)). \
                options(joinedload(model.cb_cdrs_title_deed)).order_by(model.date_of_approval)
            return query_object
        except (exc.SQLAlchemyError, Exception) as e:
            raise e
