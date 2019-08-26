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
from PyQt4.QtGui import *
from sqlalchemy import exc
from stdm.ui.flts.workflow_manager.config import StyleSheet
from stdm.settings import current_profile
from stdm.ui.flts.workflow_manager.data_service import SchemeDataService
from stdm.ui.flts.workflow_manager.model import WorkflowManagerModel
from stdm.ui.flts.workflow_manager.scheme_detail_widget import SchemeDetailTableView
from stdm.ui.flts.workflow_manager.ui_workflow_manager import Ui_WorkflowManagerWidget


class WorkflowManagerWidget(QWidget, Ui_WorkflowManagerWidget):
    """
    Manages workflow and notification in Scheme Establishment and
    First, Second and Third Examination FLTS modules
    """

    def __init__(self, title, object_name, parent=None):
        super(QWidget, self).__init__(parent)
        self.setupUi(self)
        self._profile = current_profile()
        self._checked_ids = []
        self._saved_detail_widget = {}
        self.setWindowTitle(title)
        self.setObjectName(object_name)
        self.data_service = SchemeDataService(self._profile)
        self.model = WorkflowManagerModel(self.data_service)
        self.table_view = QTableView()
        self.table_view.setModel(self.model)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setShowGrid(False)
        self.table_view.horizontalHeader().\
            setStyleSheet(StyleSheet().header_style)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabWidget.insertTab(0, self.table_view, 'Scheme')
        self.table_view.clicked.connect(self._on_check_uncheck)
        self.tabWidget.tabCloseRequested.connect(self._close_tab)
        self.holdersButton.setObjectName("Holders")
        self.documentsButton.setObjectName("Documents")
        self.documentsButton.clicked.connect(self._on_view_scheme_detail)
        self.initial_load()

    def initial_load(self):
        """
        Initial table view data load
        """
        try:
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
            self.table_view.horizontalHeader().setStretchLastSection(True)
            self.table_view.horizontalHeader().\
                setResizeMode(QHeaderView.ResizeToContents)

    def _on_check_uncheck(self, index):
        """
        Slot called on check/uncheck
        :param index: Table view item identifier/QModelIndex
        :type index: Integer
        """
        row = index.row()
        column = index.column()
        if column != 0:
            return
        value = self.model.results[row].get(column)
        record_id = self.model.get_record_id(row)
        if int(value) == 1:
            self._add_checked_id(int(record_id))
            self._enable_widget([self.holdersButton, self.documentsButton])
        else:
            self._remove_checked_id(record_id)
            if not self._checked_ids:
                self._disable_widget([self.holdersButton, self.documentsButton])

    def _remove_checked_id(self, record_id):
        """
        Remove table view record identifier
        from checked tracker
        :param record_id: Checked table view identifier
        :rtype record_id: Integer
        """
        if record_id in self._checked_ids:
            try:
                self._checked_ids.remove(record_id)
            except ValueError:
                pass

    def _add_checked_id(self, record_id):
        """
        Add table view record identifier
        from checked tracker
        :param record_id: Checked table view identifier
        :rtype record_id: Integer
        """
        if record_id not in self._checked_ids:
            self._checked_ids.append(record_id)

    def _on_view_scheme_detail(self):
        """
        On clicking the 'Holders' or 'Documents'
        buttons, open scheme detail table view
        """
        if not self._checked_ids:
            return
        label = self._get_button_name(self.sender())
        key = "{0}_{1}".format(str(self._checked_ids[-1]), label)
        if key in self._saved_detail_widget:
            saved_widget = self._saved_detail_widget[key]
            if self._is_alive(saved_widget):
                self._replace_tab(1, saved_widget, label)
        else:
            detail_table = SchemeDetailTableView(
                self._checked_ids[-1], self._profile, self
            )
            self._replace_tab(1, detail_table, label)
            self._saved_detail_widget[key] = detail_table

    def _get_button_name(self, sender):
        """
        Return button object name
        :param sender: Object invoking the signal
        :type sender: QPushButton
        :return: Sender button label text
        :rtype: String
        """
        sender = sender
        if sender is None or not isinstance(sender, QPushButton):
            return
        return sender.objectName()

    def _replace_tab(self, index, widget, label):
        """
        Replace existing tab with another
        :param index: Current tab index
        :type index: Integer
        :param widget: Tab widget
        :type widget: QTabWidget
        :param label: Tab label
        :type label: String
        """
        self.tabWidget.removeTab(index)
        self.tabWidget.insertTab(index, widget, label)
        self.tabWidget.setTabsClosable(True)
        tab_bar = self.tabWidget.tabBar()
        tab_bar.setTabButton(0, QTabBar.RightSide, None)
        self.tabWidget.setCurrentIndex(index)

    def _close_tab(self, index):
        """
        Cleanly closes the tab
        :param index: Index of the tab to be closed
        :type index: Integer
        """
        # tab = self.tabWidget.widget(index)
        self.tabWidget.removeTab(index)
        # if tab is not None:
        #     tab.deleteLater()

    @staticmethod
    def _enable_widget(widgets):
        """
        Enable a widget
        :param widgets: A widget/group of widgets to be enabled
        :rtype widgets: List or QWidget
        """
        if isinstance(widgets, list):
            for widget in widgets:
                widget.setEnabled(True)
        else:
            widgets.setEnabled(True)

    @staticmethod
    def _disable_widget(widgets):
        """
        Disable a widget
        :param widgets: A widget/group of widgets to be enabled
        :rtype widgets: List or QWidget
        """
        if isinstance(widgets, list):
            for widget in widgets:
                widget.setEnabled(False)
        else:
            widgets.setEnabled(False)

    def _is_alive(self, widget):
        """
        Checks widget/tab for aliveness
        :param widget: Qt widget
        :type widget: QtWidget
        :return: True if alive False otherwise
        :rtype: Boolean
        """
        import sip
        try:
            sip.unwrapinstance(widget)
        except RuntimeError:
            return False
        return True
