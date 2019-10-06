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
from stdm.ui.flts.workflow_manager.config import (
    SchemeButtonIcons,
    StyleSheet,
    TabIcons,
)
from stdm.settings import current_profile
from stdm.ui.flts.workflow_manager.data_service import (
    CommentDataService,
    DocumentDataService,
    HolderDataService,
    SchemeDataService
)
from stdm.ui.flts.workflow_manager.model import WorkflowManagerModel
from stdm.ui.flts.workflow_manager.scheme_approval import (
    Approve,
    Disapprove
)
from stdm.ui.flts.workflow_manager.comment_manager_widget import CommentManagerWidget
from stdm.ui.flts.workflow_manager.pagination_widget import PaginationWidget
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
        self._tab_name = self._detail_table = None
        self._notif_bar = NotificationBar(self.vlNotification)
        self._profile = current_profile()
        self.data_service = SchemeDataService(
            self._profile, self._object_name, self
        )
        self._approve = Approve(self.data_service, self._object_name)
        self._disapprove = Disapprove(self.data_service,)
        self._lookup = self.data_service.lookups
        _header_style = StyleSheet().header_style
        self._comments_title = "Comments"
        self.setWindowTitle(title)
        self.setObjectName(self._object_name)
        self.holdersButton.setObjectName("Holders")
        self.documentsButton.setObjectName("Documents")
        self._set_button_icons()
        self.table_view = QTableView()
        self._model = WorkflowManagerModel(
            self.data_service, self._workflow_load_filter
        )
        self.table_view.setModel(self._model)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setShowGrid(False)
        self.table_view.horizontalHeader().\
            setStyleSheet(_header_style)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabWidget.insertTab(0, self.table_view, "Scheme")
        self._tab_icons = TabIcons().icons
        self.tabWidget.setTabIcon(0, self._tab_icons["Scheme"])
        self.paginationFrame.setLayout(PaginationWidget().pagination_layout)
        self.tabWidget.currentChanged.connect(self._on_tab_change)
        self.table_view.clicked.connect(self._on_comment)
        self.table_view.clicked.connect(self._on_check)
        self.table_view.clicked.connect(self._on_uncheck)
        self.tabWidget.tabCloseRequested.connect(self._close_tab)
        self.approveButton.clicked.connect(
            lambda: self._on_approve(self._lookup.APPROVED(), "approve")
        )
        self.disapproveButton.clicked.connect(
            lambda: self._on_disapprove(
                self._lookup.DISAPPROVED(), "disapprove"
            )
        )
        self.documentsButton.clicked.connect(self._load_scheme_detail)
        self.holdersButton.clicked.connect(self._load_scheme_detail)
        self._initial_load()

    def _set_button_icons(self):
        """
        Sets QPushButton icons
        """
        icons = SchemeButtonIcons(self)
        buttons = icons.buttons
        for button, options in buttons.iteritems():
            button.setIcon(options.icon)
            button.setIconSize(options.size)

    @property
    def _workflow_load_filter(self):
        """
        On load, return workflow type data filter
        :return workflow_filter: Workflow type data filter
        :rtype workflow_filter: Dictionary
        """
        workflow_filter = {
            self._lookup.WORKFLOW_COLUMN:
                self.data_service.get_workflow_id(self._object_name)
        }
        return workflow_filter

    def _initial_load(self):
        """
        Initial table view data load
        """
        try:
            self._model.load()
            self._enable_search() if self._model.results \
                else self._disable_search()
        except (AttributeError, exc.SQLAlchemyError, Exception) as e:
            msg = "Failed to load: {}".format(e)
            self._show_critical_message(msg)
        else:
            self.table_view.horizontalHeader().setStretchLastSection(True)
            self.table_view.horizontalHeader().\
                setResizeMode(QHeaderView.ResizeToContents)

    def _on_comment(self, index):
        """
        Handles click on a scheme record to view scheme comments
        :param index: Table view item identifier
        :type index: QModelIndex
        """
        if index.column() != self._lookup.CHECK:
            row, value, scheme_id = self._get_model_item(index)
            scheme_number = self._get_scheme_number(index)
            self._load_comments(scheme_id, scheme_number)

    def _load_comments(self, scheme_id, scheme_number):
        """
        On click a scheme record, open scheme comments tab
        :param scheme_id: Scheme record ID/primary key
        :type scheme_id: Integer
        :param scheme_number: Scheme number
        :type scheme_number: String
        """
        # TODO: Refactor. Repetion refer to _load_scheme_detail
        self._notif_bar.clear()
        key, label = self._create_key(
            scheme_id, scheme_number, self._comments_title
        )
        if key in self._detail_store:
            saved_widget = self._detail_store[key]
            if self._is_alive(saved_widget):
                self._replace_tab(1, saved_widget, label)
        elif None not in (key, label):
            detail_service = self._get_detail_service(self._comments_title)
            comments = CommentManagerWidget(
                detail_service, self._profile, scheme_id, self
            )
            self._replace_tab(1, comments, label)
            self._disable_search()
            self._detail_store[key] = comments

    def _on_check(self, index):
        """
        Handle checkbox check event
        :param index: Table view item identifier
        :type index: QModelIndex
        """
        if index.column() == self._lookup.CHECK:
            row, check_state, record_id = self._get_model_item(index)
            if int(check_state) == 1:
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
        if index.column() == self._lookup.CHECK:
            row, check_state, record_id = self._get_model_item(index)
            if int(check_state) == 0:
                self._remove_checked_id(record_id)
                scheme_number = self._get_scheme_number(index)
                key, label = self._create_key(record_id, scheme_number)
                self._remove_stored_widget(key)
                self._on_uncheck_disable_widgets()

    def _get_model_item(self, index):
        """
        Returns model items
        :param index: Table view item identifier
        :type index: QModelIndex
        :return value: Model item value represented by a row and column
        :rtype value: Multiple types
        :return record_id: Record/entity id (primary key)
        :rtype record_id: Integer
        """
        row = index.row()
        column = index.column()
        value = self._model.results[row].get(column)
        record_id = self._model.get_record_id(row)
        return row, value, int(record_id)

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
            self._load_scheme_detail()

    def _on_check_enable_widgets(self):
        """
        Enable Workflow Manager widgets on check
        """
        status = self._get_stored_status()
        self._enable_widget([self.holdersButton, self.documentsButton])
        if self._lookup.PENDING() in status or \
                self._lookup.DISAPPROVED() in status:
            self._enable_widget(self.approveButton)
        if self._lookup.PENDING() in status or \
                self._lookup.APPROVED() in status:
            self._enable_widget(self.disapproveButton)
        self._on_uncheck_disable_widgets()

    def _get_stored_status(self):
        """
        Return stored scheme approval status
        :return status: Scheme approval status
        :rtype status: List
        """
        status = [tup[1] for tup in self._checked_ids.values()]
        return status

    def _load_scheme_detail(self):
        """
        On unchecking a record or clicking the 'Holders'
        or'Documents' buttons, open scheme detail tab
        """
        # TODO: Refactor. Repetion refer to _load_comment
        if not self._checked_ids:
            return
        self._notif_bar.clear()
        last_id = self._checked_ids.keys()[-1]
        row, status, scheme_number = self._checked_ids[last_id]
        key, label = self._create_key(last_id, scheme_number)
        if key in self._detail_store:
            saved_widget = self._detail_store[key]
            if self._is_alive(saved_widget):
                self._replace_tab(1, saved_widget, label)
        elif None not in (key, label):
            detail_service = self._get_detail_service()
            self._detail_table = SchemeDetailTableView(
                detail_service, self._profile, last_id, self
            )
            self._replace_tab(1, self._detail_table, label)
            self._enable_search() if self._detail_table.model.results \
                else self._disable_search()
            self._detail_store[key] = self._detail_table

    def _get_detail_service(self, comment=None):
        """
        Returns scheme details and comments data service
        :param comment: Comment label
        :type comment: String
        :return: Scheme details data service
        :rtype: DocumentDataService or HolderDataService
        """
        label = comment if comment else self._get_label()
        return self._detail_services[label]

    @property
    def _detail_services(self):
        """
        Scheme details data services
        :return: Scheme details data services
        :rtype: Dictionary
        """
        detail_service = {
            self.documentsButton.objectName(): {
                'data_service': DocumentDataService,
                'load_collections': False
            },
            self.holdersButton.objectName(): {
                'data_service': HolderDataService,
                'load_collections': True
            },
            self._comments_title: {
                'data_service': CommentDataService,
                'load_collections': True
            }
        }
        return detail_service

    def _create_key(self, scheme_id, scheme_number, comment=None):
        """
        Create key to be used as widget store ID
        :param scheme_id: Scheme record ID/primary key
        :type scheme_id: Integer
        :param scheme_number: Scheme number
        :type scheme_number: String
        :param comment: Comment label
        :type comment: String
        :return key: Dictionary store ID
        :rtype key: String
        :return label: Scheme details/comments identifier
        :rtype label: String
        """
        label = comment if comment else self._get_label()
        if label is None:
            return None, None
        key = "{0}_{1}".format(str(scheme_id), label)
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
        for key, icon in self._tab_icons.iteritems():
            if label.startswith(key):
                self.tabWidget.setTabIcon(index, icon)
        tab_bar = self.tabWidget.tabBar()
        tab_bar.setTabButton(0, QTabBar.RightSide, None)
        if self._button_clicked() or widget.objectName() \
                == self._comments_title:
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

    def _on_approve(self, status, title):
        """
        Approve a Scheme
        :param status: Approve status
        :type status: Integer
        :param title: Approve title text
        :type title: String
        """
        self._approve.set_check_ids(self._checked_ids)
        items, scheme_numbers = self._approve.approve_items(status)
        items = (items,) + self._approve.next_approval_items(items)
        num_records = len(scheme_numbers["valid"])
        self._format_scheme_number(scheme_numbers)
        scheme_numbers = (num_records, scheme_numbers["valid"])
        self._update_scheme(items, title, scheme_numbers)

    def _on_disapprove(self, status, title):
        """
        Disapprove a Scheme
        :param status: Disapprove status
        :type status: Integer
        :param title: Disapprove title text
        :type title: String
        """
        self._disapprove.set_check_ids(self._checked_ids)
        items, scheme_numbers = self._disapprove.disapprove_items(status)
        scheme_numbers = (len(scheme_numbers), scheme_numbers)
        self._update_scheme(items, title, scheme_numbers)

    def _format_scheme_number(self, scheme_numbers):
        """
        Formats the scheme message
        :param scheme_numbers: Scheme number
        :param scheme_numbers: String
        :return: Formatted scheme numbers
        :return: Dictionary
        """
        msg = []
        approval_entity = self._lookup.APPROVAL_STATUS
        workflow_entity = self._lookup.WORKFLOW
        for scheme_number, workflow_id, approval_id in scheme_numbers["invalid"]:
            approval = self._filter_query_by(
                approval_entity, {'id': approval_id}
            ).first()
            workflow = self._filter_query_by(
                workflow_entity, {'id': workflow_id}
            ).first()
            msg.append("\n{0} - {1} in {2}".format(
                scheme_number, approval.value, workflow.value
            ))
        return scheme_numbers["valid"].extend(msg)

    def _filter_query_by(self, entity_name, filters):
        """
        Filters query result by a column value
        :param entity_name: Entity name
        :type entity_name: String
        :param filters: Column filters - column name and value
        :type filters: Dictionary
        :return: Filter entity query object
        :rtype: Entity object
        """
        try:
            result = self.data_service.filter_query_by(entity_name, filters)
        except (AttributeError, exc.SQLAlchemyError, Exception) as e:
            raise e
            # TODO: Return critical message instead of raise
        else:
            return result

    def _update_scheme(self, items, title, scheme_numbers):
        """
        On approve or disapprove update scheme record
        :param items: Update items
        :param items: Dictionary
        :param title: Message title
        :param title: String
        :param scheme_numbers: Scheme numbers and rows
        :param scheme_numbers: Tuple
        """
        updated_rows = None
        rows, scheme_numbers = scheme_numbers
        try:
            self._notif_bar.clear()
            msg = self._approval_message(
                title.capitalize(), rows, scheme_numbers
            )
            reply = self._show_question_message(msg)
            if reply:
                if isinstance(items, tuple):
                    items, next_items, save_items = items
                    updated_rows = self._update_on_approve(
                        items, next_items, save_items
                    )
                else:
                    updated_rows = self._model.update(items)
        except (AttributeError, exc.SQLAlchemyError, Exception) as e:
            msg = "Failed to update: {}".format(e)
            self._show_critical_message(msg)
        else:
            if reply:
                self.refresh()
                msg = self._approval_message(
                    "Successfully {}".format(title), updated_rows
                )
                self._notif_bar.insertInformationNotification(msg)

    def _update_on_approve(self, items, next_items, save_items):
        """
        Update approval status on approve
        :param items: Current workflow approval items
        :type items: Dictionary
        :Param next_items: Next workflow update values, columns and filters
        :type next_items: Dictionary
        :Param save_items: Next workflow save values, columns and filters
        :type save_items: Dictionary
        :return updated_rows: Number of updated rows
        :rtype updated_rows: Integer
        """
        updated_rows = 0
        if next_items:
            updated_rows = self._model.update(items)  # Update current workflow
            self._model.update(next_items)  # Update preceding workflow
        elif save_items:
            updated_rows = self._model.update(items)
            # TODO: Call model's save method from here and pass save_items
        elif items:
            updated_rows = self._model.update(items)
        return updated_rows

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
            return "{0} {1} {2}?\n{3}".format(
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

    def _on_uncheck_disable_widgets(self):
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
        elif self._lookup.PENDING() not in status and \
                self._lookup.APPROVED() not in status:
            self._disable_widget(self.disapproveButton)
        elif self._lookup.PENDING() not in status and \
                self._lookup.DISAPPROVED() not in status:
            self._disable_widget(self.approveButton)

    def _on_tab_change(self, index):
        """
        Shows or hides widget on tab change
        :param index: Tab index
        :type index: Integer
        """
        active_tab_label = self.tabWidget.tabText(index)
        active_tab_label = active_tab_label.split(" - ")[0]
        tabs_label = (self.holdersButton.objectName())
        if index == 0 or active_tab_label in tabs_label:
            self._show_widget(self.paginationFrame)
            self._enable_search() if self._model.results or \
                self._detail_table.model.results else \
                self._disable_search()
        elif active_tab_label not in tabs_label:
            self._hide_widget(self.paginationFrame)
            if active_tab_label != self.documentsButton.objectName():
                self._disable_search()

    @staticmethod
    def _show_widget(widget):
        """
        Shows a widget
        :param widget:
        :type widget: QWidget
        """
        if not widget.isVisible():
            widget.show()

    @staticmethod
    def _hide_widget(widget):
        """
        Hides a widget
        :param widget:
        :type widget: QWidget
        """
        if widget.isVisible():
            widget.hide()

    def refresh(self):
        """
        Refresh checked items store and model
        """
        self._checked_ids = OrderedDict()
        self._model.refresh()
        self._on_uncheck_disable_widgets()
