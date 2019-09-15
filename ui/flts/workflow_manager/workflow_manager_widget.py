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
from ...notification import NotificationBar
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
        self._object_name = object_name
        self._checked_ids = OrderedDict()
        self._detail_store = {}
        self._tab_name = None
        self._notif_bar = NotificationBar(self.vlNotification)
        self._profile = current_profile()
        self.data_service = SchemeDataService(
            self._profile, self._object_name, self
        )
        self._lookup = self.data_service.lookups
        self._scheme_update_column = self.data_service.update_columns
        _header_style = StyleSheet().header_style
        self.setWindowTitle(title)
        self.setObjectName(self._object_name)
        self.holdersButton.setObjectName("Holders")
        self.documentsButton.setObjectName("Documents")
        self.table_view = QTableView()
        self._model = WorkflowManagerModel(self.data_service)
        self.table_view.setModel(self._model)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setShowGrid(False)
        self.table_view.horizontalHeader().\
            setStyleSheet(_header_style)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabWidget.insertTab(0, self.table_view, 'Scheme')
        self.table_view.clicked.connect(self._on_check)
        self.table_view.clicked.connect(self._on_uncheck)
        self.tabWidget.tabCloseRequested.connect(self._close_tab)
        self.approveButton.clicked.connect(
            lambda: self._approval(self._lookup.APPROVED(), "approve")
        )
        self.disapproveButton.clicked.connect(
            lambda: self._approval(self._lookup.DISAPPROVED(), "disapprove")
        )
        self.documentsButton.clicked.connect(
            lambda: self._load_scheme_detail(self._detail_store)
        )
        self._initial_load()

    def _initial_load(self):
        """
        Initial table view data load
        """
        try:
            self._model.load(self._workflow_filter)
            self._enable_search() if self._model.results \
                else self._disable_search()
        except (AttributeError, exc.SQLAlchemyError, Exception) as e:
            msg = "Failed to load: {}".format(e)
            self._show_critical_message(msg)
        else:
            self.table_view.horizontalHeader().setStretchLastSection(True)
            self.table_view.horizontalHeader().\
                setResizeMode(QHeaderView.ResizeToContents)

    @property
    def _workflow_filter(self):
        """
        Return workflow type data filter
        :return workflow_filter: Workflow type data filter
        :rtype workflow_filter: Dictionary
        """
        workflow_filter = ({
            self._lookup.WORKFLOW_COLUMN:
                self.data_service.get_workflow_id(self._object_name)
        })
        return workflow_filter

    def _on_check(self, index):
        """
        Handle checkbox check event
        :param index: Table view item identifier
        :type index: QModelIndex
        """
        row, check_state, record_id = self._check_state(index)
        if check_state == 1:
            status = self._get_approval_status(index)
            scheme_number = self._get_scheme_number(index)
            self._checked_ids[record_id] = (row, status, scheme_number)
            self._on_check_enable_widgets()

    def _on_uncheck(self, index):
        """
        Handle checkbox uncheck event
        :param index: Table view item identifier
        :type index: QModelIndex
        """
        row, check_state, record_id = self._check_state(index)
        if check_state == 0:
            self._remove_checked_id(record_id)
            scheme_number = self._get_scheme_number(index)
            key, label = self._create_key(record_id, scheme_number)
            self._remove_stored_widget(key)
            self._on_check_disable_widgets()

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
        row, column = self._model.get_column_index(
            index, self._lookup.CHECK
        )
        if None in (row, column):
            return None, None, None
        state = self._model.results[row].get(column)
        record_id = self._model.get_record_id(row)
        return row, int(state), int(record_id)

    def _get_approval_status(self, index):
        """
        Return scheme approval status
        :param index: Table view item identifier
        :type index: QModelIndex
        :return: Scheme approval status
        :rtype: Integer
        """
        return self._model.model_item(
            index.row(),
            self._lookup.STATUS
        )

    def _get_scheme_number(self, index):
        """
        Return scheme unique number
        :param index: Table view item identifier
        :type index: QModelIndex
        :return: Scheme unique number
        :rtype: String
        """
        return self._model.model_item(
            index.row(),
            self._lookup.SCHEME_NUMBER
        )

    def _remove_checked_id(self, record_id):
        """
        Remove table view checked ids from checked tracker
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

    def _on_check_enable_widgets(self):
        """
        Enable Workflow Manager widgets on check
        """
        status = self._get_stored_status()
        self._enable_widget([self.holdersButton, self.documentsButton])
        if self._lookup.PENDING() in status or \
                self._lookup.DISAPPROVED() in status:
            self._enable_widget(self.approveButton)
        if self._lookup.APPROVED() in status:
            self._enable_widget(self.disapproveButton)
        self._on_check_disable_widgets()

    def _on_check_disable_widgets(self):
        """
        Disable Workflow Manager widgets on uncheck
        """
        status = self._get_stored_status()
        if not self._checked_ids:
            self._close_tab(1)
            self._disable_widget([
                self.holdersButton, self.documentsButton,
                self.approveButton, self.disapproveButton
            ])
        elif self._lookup.APPROVED() not in status:
            self._disable_widget(self.disapproveButton)
        elif self._lookup.PENDING() not in status and \
                self._lookup.DISAPPROVED() not in status:
            self._disable_widget(self.approveButton)

    def _get_stored_status(self):
        """
        Return stored scheme approval status
        :return status: Scheme approval status
        :rtype status: List
        """
        status = [tup[1] for tup in self._checked_ids.values()]
        return status

    def _load_scheme_detail(self, store):
        """
        On unchecking a record or clicking the 'Holders'
        or'Documents' buttons, open scheme detail tab
        :param store: Archived QWidget
        :type store: Dictionary
        """
        if not self._checked_ids:
            return
        self._notif_bar.clear()
        last_id = self._checked_ids.keys()[-1]
        row, status, scheme_number = self._checked_ids[last_id]
        key, label = self._create_key(last_id, scheme_number)
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

    def _create_key(self, id_, scheme_number):
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
        label = "{0} - {1}".format(label, scheme_number)
        return key, label

    def _get_label(self):
        """
        Return label depending on the type of scheme
        details (holders or documents)
        :return: Sender object name
        :rtype: String
        """
        object_name = None
        button = self._button_clicked()
        if button:
            return button.objectName()
        elif self._tab_name:
            object_name, scheme_number = self._tab_name.split(" - ")
        return object_name

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

    @staticmethod
    def _is_alive(widget):
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

    def _approval(self, status, title):
        """
        Approve or disapprove a Scheme
        :param status: Approve or disapprove status
        :type status: Integer
        :param title: Approve or disapprove title text
        :type title: String
        """
        items, scheme_numbers, rows = self._approval_items(status)
        updated_rows = None
        try:
            self._notif_bar.clear()
            msg = self._approval_message(title.capitalize(), rows, scheme_numbers)
            reply = self._show_question_message(msg)
            if reply:
                updated_rows = self._model.update(items)
        except (AttributeError, exc.SQLAlchemyError, Exception) as e:
            msg = "Failed to update: {}".format(e)
            self._show_critical_message(msg)
        else:
            if reply:
                self._update_checked_id()
                msg = self._approval_message(
                    "Successfully {}".format(title), updated_rows
                )
                self._notif_bar.insertInformationNotification(msg)

    def _approval_items(self, status_option):
        """
        Returns approve or disapprove columns and
        accompanying configurations for update
        :param status_option: Approve or disapprove status
        :type status_option: Integer
        :return items: Approval/disapproval values and
                        accompanying configurations
        :rtype items: Dictionary
        """
        items = {}
        scheme_numbers = []
        count = 0
        for id_, (row, status, scheme_number) in self._checked_ids.iteritems():
            if status != status_option:
                update_items = []
                for updates in self._get_update_item(self._scheme_update_column):
                    if updates[1] == 4:
                        updates = updates + (1,)
                    else:
                        updates = updates + (status_option,)
                    update_items.append(updates)
                items[row] = update_items
                scheme_numbers.append(scheme_number)
                count += 1
        return items, scheme_numbers, count

    @ staticmethod
    def _get_update_item(updates):
        """
        Returns the necessary configuration
        update items per column
        :rtype updates: Update column values
        :param updates: List
        :return column: Column name as returned by SQLAlchemy query
                        Table and column name in cases of relationship
        :rtype column: String or Dictionary
        :return index: Position of the column in the table view
        :rtype index: Integer
        """
        for update in updates:
            yield update.column, update.index

    @staticmethod
    def _approval_message(prefix, rows, scheme_numbers=None):
        """
        Returns approve or disapprove message
        :param prefix: Prefix text
        :type prefix: String
        :param rows: Number of rows
        :type rows: Integer
        :param scheme_numbers: Scheme numbers
        :param scheme_numbers: List
        :return: Approval message
        :rtype: String
        """
        msg = 'schemes' if rows != 1 else 'scheme'
        if scheme_numbers:
            return "{0} {1} {2}?\n({3})".format(
                prefix, rows, msg, ', '.join(scheme_numbers)
            )
        return "{0} {1} {2}?".format(prefix, rows, msg)

    def _show_question_message(self, msg):
        """
        Message box to communicate a question
        :param msg: Message to be communicated
        :type msg: String
        """
        if QMessageBox.question(
            self,
            self.tr('Workflow Manager'),
            self.tr(msg),
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.No:
            return False
        return True

    def _show_critical_message(self, msg):
        """
        Message box to communicate critical message
        :param msg: Message to be communicated
        :type msg: String
        """
        QMessageBox.critical(
            self,
            self.tr('Workflow Manager'),
            self.tr(msg)
        )

    def _update_checked_id(self):
        """
        Update table view checked ids in the checked tracker
        """
        checked_ids = self._checked_ids.copy()
        for id_, (row, status, scheme_number) in checked_ids.iteritems():
            index = self._model.create_index(row, self._lookup.CHECK)
            if index:
                self._on_check(index)
