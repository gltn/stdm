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
from collections import OrderedDict
from PyQt4.QtGui import *
from sqlalchemy import exc
from stdm.ui.flts.workflow_manager.config import (
    ColumnPosition,
    ApprovalStatus,
    StyleSheet,
)
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
        self._checked_ids = OrderedDict()
        self._detail_store = {}
        self._tab_name = None
        self._column = ColumnPosition().position
        self._status = ApprovalStatus().status
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
        self.table_view.clicked.connect(self._on_check)
        self.table_view.clicked.connect(self._on_uncheck)
        self.tabWidget.tabCloseRequested.connect(self._close_tab)
        self.holdersButton.setObjectName("Holders")
        self.documentsButton.setObjectName("Documents")
        self.documentsButton.clicked.connect(
            lambda: self._load_scheme_detail(self._detail_store)
        )
        self.initial_load()

    def initial_load(self):
        """
        Initial table view data load
        """
        try:
            self.model.load()
            self._enable_search() if self.model.results \
                else self._disable_search()
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

    def _on_check(self, index):
        """
        Handle checkbox check event
        :param index: Table view item identifier
        :type index: QModelIndex
        """
        check_state, record_id = self._check_state(index)
        if check_state == 1:
            status = self._get_approval_status(index)
            self._checked_ids[record_id] = status
            self._enable_widgets_on_check(status)

    def _on_uncheck(self, index):
        """
        Handle checkbox uncheck event
        :param index: Table view item identifier
        :type index: QModelIndex
        """
        check_state, record_id = self._check_state(index)
        if check_state == 0:
            self._remove_checked_id(record_id)
            key, label = self._create_key(record_id)
            self._remove_stored_widget(key)
            self._disable_widgets_on_uncheck()

    def _check_state(self, index):
        """
        Returns checkbox check state
        :param index: Table view item identifier
        :type index: QModelIndex
        :return state: Checkbox check or uncheck flag/value
        :rtype state: Integer
        :return record_id: Record/entity id (primary key)
        :rtype record_id: Integer
        """
        row, column = self.model.get_column_index(
            index, self._column.CHECK
        )
        if None in (row, column):
            return None, None
        state = self.model.results[row].get(column)
        record_id = self.model.get_record_id(row)
        return int(state), int(record_id)

    def _get_approval_status(self, index):
        """
        Return scheme approval status
        :param index: Table view item identifier
        :type index: QModelIndex
        :return status: Scheme approval status
        :rtype status: Integer
        """
        row = index.row()
        status = self.model.results[row].get(self._column.STATUS)
        return int(status)

    def _remove_checked_id(self, record_id):
        """
        Remove table view record identifier
        from checked tracker
        :param record_id: Checked table view identifier
        :rtype record_id: Integer
        """
        try:
            del self._checked_ids[record_id]
        except KeyError:
            return

    def _remove_stored_widget(self, key):
        """
        Removed archived table view widget
        :param key: Archived widget identifier
        :type key: String
        :return: True if widget is removed otherwise False
        :rtype: Boolean
        """
        try:
            del self._detail_store[key]
        except KeyError:
            return
        else:
            self._load_scheme_detail(self._detail_store)

    def _enable_widgets_on_check(self, status):
        """
        Enable Workflow Manager widgets on check
        """
        self._enable_widget([self.holdersButton, self.documentsButton])
        self._enable_widget(self.approveButton) if status != self._status.APPROVED \
            else self._enable_widget(self.disapproveButton)

    def _disable_widgets_on_uncheck(self):
        """
        Disable Workflow Manager widgets on uncheck
        """
        status = self._checked_ids.values()
        if not self._checked_ids:
            self._close_tab(1)
            self._disable_widget([
                self.holdersButton, self.documentsButton,
                self.approveButton, self.disapproveButton
            ])
        elif self._status.APPROVED not in status:
            self._disable_widget(self.disapproveButton)
        elif self._status.PENDING not in status and \
                self._status.UNAPPROVED not in status:
            self._disable_widget(self.approveButton)

    def _load_scheme_detail(self, store):
        """
        On unchecking a record or clicking the 'Holders'
        or'Documents' buttons, open scheme detail tab
        :param store: Archived QWidget
        :type store: Dictionary
        """
        if not self._checked_ids:
            return
        last_id = self._checked_ids.keys()[-1]
        key, label = self._create_key(last_id)
        if key in store:
            saved_widget = store[key]
            if self._is_alive(saved_widget):
                self._replace_tab(1, saved_widget, label)
        elif None not in (key, label):
            detail_table = SchemeDetailTableView(last_id, self._profile, self)
            self._replace_tab(1, detail_table, label)
            self._enable_search() if detail_table.model.results \
                else self._disable_search()
            store[key] = detail_table

    def _create_key(self, id_):
        """
        Create key to be used as widget store ID
        :param id_: Unique integer value
        :type id_: Integer
        :return key: Dictionary store ID
        :rtype key: String
        :return label: Label identify type of scheme
        details (holders or documents)
        :rtype label: String
        """
        label = self._get_label()
        if label is None:
            return None, None
        key = "{0}_{1}".format(str(id_), label)
        return key, label

    def _get_label(self):
        """
        Return label depending on the type of scheme
        details (holders or documents)
        :return: Sender object name or detail tab name
        :rtype: String
        """
        button = self._button_clicked()
        if button:
            return button.objectName()
        return self._tab_name

    def _enable_search(self):
        """
        Enables Workflow Manager search features
        """
        self._enable_widget([
            self.searchEdit, self.filterComboBox, self.searchButton
        ])

    def _disable_search(self):
        """
        Disables Workflow Manager search features
        """
        self._disable_widget([
            self.searchEdit, self.filterComboBox, self.searchButton
        ])

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
        if self._button_clicked():
            self.tabWidget.setCurrentIndex(index)
        self._tab_name = label

    def _button_clicked(self):
        """
        Returns button object when clicked
        :return button: Button object
        :rtype button: QPushButton
        """
        button = self.sender()
        if button is None or not isinstance(button, QPushButton):
            return
        return button

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
        self._tab_name = None

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
