"""
/***************************************************************************
Name                 : Scheme Details View
Description          : Table view widget for viewing scheme holders and
                       supporting documents for workflow manager modules;
                       Scheme Establishment and First, Second and
                       Third Examination FLTS modules.
Date                 : 22/August/2019
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

from PyQt4.QtGui import *
from sqlalchemy import exc
from stdm.ui.flts.workflow_manager.config import StyleSheet
from stdm.ui.flts.workflow_manager.model import WorkflowManagerModel


class SchemeDetailTableView(QTableView):
    """
    Views scheme holders and supporting documents for workflow
    manager modules; Scheme Establishment and First, Second and
    Third Examination FLTS modules.
    """
    def __init__(self, widget_properties, profile, scheme_id, parent=None):
        super(QTableView, self).__init__(parent)
        self._load_collections = widget_properties['load_collections']
        data_service = widget_properties['data_service']
        data_service = data_service(profile, scheme_id)
        self.model = WorkflowManagerModel(data_service)
        self.setModel(self.model)
        self.setAlternatingRowColors(True)
        self.setShowGrid(False)
        self.horizontalHeader().setStyleSheet(StyleSheet().header_style)
        self.setSelectionBehavior(QTableView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        parent.paginationFrame.hide()
        self._initial_load()

    def _initial_load(self):
        """
        Initial table view data load
        """
        try:
            if self._load_collections:
                self.model.load_collection()
            else:
                self.model.load()
        except (exc.SQLAlchemyError, Exception) as e:
            QMessageBox.critical(
                self,
                self.tr('{} Entity Model'.format(self.model.entity_name)),
                self.tr("{0} failed to load: {1}".format(
                    self.model.entity_name, e
                ))
            )
        else:
            self.horizontalHeader().setStretchLastSection(True)
            self.horizontalHeader().setResizeMode(QHeaderView.ResizeToContents)
