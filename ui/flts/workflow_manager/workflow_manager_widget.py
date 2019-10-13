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
    SchemeMessageBox,
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
from stdm.ui.flts.workflow_manager.message_box_widget import MessageBoxWidget
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
        self._message_box = {}
        self._tab_name = self._detail_table = self._msg_box_button = None
        self.notif_bar = NotificationBar(self.vlNotification)
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
        self.commentsButton.setObjectName(self._comments_title)
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
        self.commentsButton.clicked.connect(self._load_scheme_detail)
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
            self._load_comments(row, scheme_id, scheme_number)

    def _load_comments(self, row, scheme_id, scheme_number):
        """
        On click a scheme record, open Scheme comments tab
        :param scheme_id: Scheme record ID/primary key
        :type scheme_id: Integer
        :param scheme_number: Scheme number
        :type scheme_number: String
        """
        widget_id = self._create_key(
            scheme_id, scheme_number, self._comments_title
        )
        widget_prop = self._get_widget_properties(self._comments_title)
        widget_prop["scheme_items"] = {row: (
            self._model.results[row].get("data"), scheme_number
        )}
        self._load_details(widget_prop, widget_id, scheme_id)

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
                self._load_scheme_detail()
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

    def _on_check_enable_widgets(self):
        """
        Enable Workflow Manager widgets on check
        """
        status = self._get_stored_status()
        self._enable_widget([
            self.holdersButton, self.documentsButton,
            self.commentsButton
        ])
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

    def _load_scheme_detail(self, scheme_items=None):
        """
        On unchecking a record or clicking the 'Holders', 'Documents',
        'Comments' or 'Comment & Approve' buttons, open scheme detail tab
        :param scheme_items: Scheme items
        :type scheme_items: Dictionary
        """
        if not self._checked_ids:
            return
        last_id = self._checked_ids.keys()[-1]
        row, status, scheme_number = self._checked_ids[last_id]
        if self._msg_box_button:
            widget_id = self._create_key(
                last_id, scheme_number, self._comments_title
            )
            widget_prop = self._get_widget_properties(self._msg_box_button)
            self._msg_box_button = None
        else:
            widget_id = self._create_key(last_id, scheme_number)
            widget_prop = self._get_widget_properties()
        widget_prop["scheme_items"] = self._checked_scheme_items() \
            if not scheme_items else scheme_items
        self._load_details(widget_prop, widget_id, last_id)

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

    def _checked_scheme_items(self):
        """
        Returns checked scheme items; query object, scheme numbers
        :return: Scheme items of approval rows
        :rtype: Dictionary
        """
        return {
            row: (self._model.results[row].get("data"), scheme_number)
            for scheme_id, (row, status, scheme_number) in
            self._checked_ids.iteritems()
        }

    def _get_widget_properties(self, key=None):
        """
        Returns Scheme widgets properties
        :param key: Properties key
        :type key: String
        :return: Scheme widgets properties
        :rtype: Dictionary
        """
        key = key if key else self._get_label()
        return self._widget_properties[key]

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

    @property
    def _widget_properties(self):
        """
        Scheme widgets properties
        :return: Scheme widgets properties
        :rtype: Dictionary
        """
        widget_prop = {
            self.documentsButton.objectName(): {
                'data_service': DocumentDataService,
                'widget': SchemeDetailTableView,
                'load_collections': False
            },
            self.holdersButton.objectName(): {
                'data_service': HolderDataService,
                'widget': SchemeDetailTableView,
                'load_collections': True
            },
            self._comments_title: {
                'data_service': CommentDataService,
                'widget': CommentManagerWidget,
                'load_collections': True
            },
            self._msg_box_button: {
                'data_service': CommentDataService,
                'widget': CommentManagerWidget,
                'load_collections': True
            }
        }
        return widget_prop

    def _load_details(self, widget_prop, widget_id, scheme_id):
        """
        Add Scheme details tab
        :param widget_prop: Scheme details service items
        :type widget_prop: Scheme widgets properties
        :param widget_id: Dictionary
        :type widget_id: Widget key and label
        :param scheme_id: Scheme record ID/primary key
        :type scheme_id: Integer
        """
        self.notif_bar.clear()
        key, label = widget_id
        if None not in (key, label):
            details_widget = widget_prop['widget']
            self._detail_table = details_widget(
                widget_prop, self._profile, scheme_id, self
            )
            self._replace_tab(1, self._detail_table, label)
            self._enable_search() if self._detail_table.model.results \
                else self._disable_search()

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
        tab = self.tabWidget.widget(index)
        self.tabWidget.removeTab(index)
        if tab is not None:
            tab.deleteLater()
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
        if scheme_numbers["invalid"]:
            self._invalid_approval_msg(scheme_numbers)
        scheme_numbers = (num_records, scheme_numbers["valid"])
        self._approval_comment(items, title, scheme_numbers)

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
        self._approval_comment(items, title, scheme_numbers)

    def _invalid_approval_msg(self, scheme_numbers):
        """
        Return Scheme message for invalid approval
        :param scheme_numbers: Scheme number
        :type scheme_numbers: String
        :return: Formatted scheme numbers
        :return: Dictionary
        """
        msg = []
        column = "id"
        invalid_schemes = scheme_numbers["invalid"]
        numbers, workflow_ids, approval_ids = zip(*invalid_schemes)
        workflow_query = self._filter_in(
            self._lookup.WORKFLOW, {column: set(workflow_ids)}
        )
        approval_query = self._filter_in(
            self._lookup.APPROVAL_STATUS, {column: set(approval_ids)}
        )
        for scheme_number, workflow_id, approval_id in invalid_schemes:
            approval = self._get_valid_query(approval_query, column, approval_id)
            workflow = self._get_valid_query(workflow_query, column, workflow_id)
            msg.append("\n{0} - {1} in {2}".format(
                scheme_number, approval.value, workflow.value
            ))
        return scheme_numbers["valid"].extend(msg)

    def _filter_in(self, entity_name, filters):
        """
        Return query objects as a collection of filter using in_ operator
        :param entity_name: Name of entity to be queried
        :type entity_name: String
        :param filters: Query filter columns and values
        :type filters: Dictionary
        :return: Query object results
        :rtype: InstrumentedList
        """
        return self.data_service.filter_in(entity_name, filters).all()

    @staticmethod
    def _get_valid_query(query_objs, column, value):
        """
        Returns valid query object form a List
        :param query_objs: InstrumentedList of query objects
        :type query_objs: InstrumentedList
        :param column: Column name to be filtered against
        :type column: String
        :param value: Value to identify valid query object
        :type value: Multiple
        :return: Entity query object
        :rtype: Entity
        """
        for query_obj in query_objs:
            if getattr(query_obj, column, None) == value:
                return query_obj

    def _approval_comment(self, items, title, scheme_numbers):
        """
        Comment and approve or disapprove a Scheme
        :param items: Update items
        :type items: Tuple, Dictionary
        :param title: Approve title text
        :type title: String
        :param scheme_numbers: Scheme numbers and rows
        :type scheme_numbers: Tuple
        """
        num_records, scheme_numbers = scheme_numbers
        msg = self._approval_message(
            title.capitalize(), num_records, scheme_numbers
        )
        rows = self._approval_rows(items)
        scheme_items = self._approval_scheme_items(rows)
        result, self._msg_box_button = self._show_approval_message(
            msg, scheme_items
        )
        if result == 0:
            self._update_scheme(items, title)
        elif result == 1:
            self._load_scheme_detail(scheme_items)
            self._lambda_args = (items, title)  # Ensures lambda gets current value
            self._detail_table.submitted.connect(
                lambda: self._update_scheme(*self._lambda_args)
            )

    @staticmethod
    def _approval_rows(items):
        """
        Returns row indexes of valid checked approval table view items
        :param items: Update items
        :type items: Tuple, Dictionary
        :return: Table view rows to be updated
        :rtype: List
        """
        if isinstance(items, tuple):
            items, next_items, save_items = items
        return items.keys()

    def _approval_scheme_items(self, approval_rows):
        """
        Returns valid checked approval scheme items; query object, scheme numbers
        :param approval_rows: Approval table view rows
        :type approval_rows: List
        :return: Scheme items of approval rows
        :rtype: Dictionary
        """
        return {
            row: (self._model.results[row].get("data"), scheme_number)
            for scheme_id, (row, status, scheme_number) in self._checked_ids.items()
            if row in approval_rows
        }

    def _update_scheme(self, items, title):
        """
        On approve or disapprove update scheme record
        :param items: Update items
        :type items: Tuple, Dictionary
        :param title: Message title
        :type title: String
        """
        try:
            self.notif_bar.clear()
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
            self.refresh()
            msg = self._approval_message(
                "Successfully {}".format(title), updated_rows
            )
            self.notif_bar.insertInformationNotification(msg)

    def _update_on_approve(self, items, next_items, save_items):
        """
        Update approval status on approve
        :param items: Current workflow approval items
        :type items: Dictionary
        :Param next_items: Next workflow update values, columns and filters
        :type next_items: Dictionary
        :return save_items: Save items; columns, values and entity
        :rtype save_items: Dictionary
        :return updated_rows: Number of updated rows
        :rtype updated_rows: Integer
        """
        # TODO: Refactor each save/update into a function. The succeeding
        #  function in the execution chain should only be triggered if
        #  preceding save/update function returns successfully. The chained
        #  execution should stop on an error
        updated_rows = 0
        try:
            if next_items and save_items:
                self._model.update(next_items)  # Update succeeding workflow
                self._model.save(save_items)  # Save succeeding workflow
            elif next_items:
                self._model.update(next_items)
            elif save_items:
                self._model.save(save_items)
            if items:
                updated_rows = self._model.update(items)
        except (AttributeError, exc.SQLAlchemyError, Exception) as e:
            raise e
        finally:
            return updated_rows

    @staticmethod
    def _approval_message(prefix, num_records, scheme_numbers=None):
        """
        Returns approve or disapprove message
        :param prefix: Prefix text
        :type prefix: String
        :param num_records: Number of rows
        :type num_records: Integer
        :param scheme_numbers: Scheme numbers
        :type scheme_numbers: List
        :return: Approval message
        :rtype: String
        """
        msg = 'schemes' if num_records > 1 else 'scheme'
        if scheme_numbers:
            return "{0} {1} {2}\n{3}".format(
                prefix, num_records, msg, ', '.join(scheme_numbers)
            )
        return "{0} {1} {2}".format(prefix, num_records, msg)

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

    def _show_approval_message(self, msg, items):
        """
        Custom Message box
        :param msg: Message to be communicated
        :type msg: String
        :param items: Approval items
        :type items: Dictionary
        """
        button = self._button_clicked()
        button = button.objectName()
        msg_box = self._message_box.get(button)
        if msg_box:
            msg_box.setWindowTitle(self.tr('Workflow Manager'))
            msg_box.setText(self.tr(msg))
            return self._message_box_result(msg_box, items)
        options = SchemeMessageBox(self).message_box[button]
        msg_box = MessageBoxWidget(
            options,
            self.tr('Workflow Manager'),
            self.tr(msg),
            self
        )
        self._message_box[button] = msg_box
        return self._message_box_result(msg_box, items)

    def _message_box_result(self, message_box, items):
        """
        Returns custom message box results
        :param message_box: Custom QMessageBox
        :type message_box: QMessageBox
        :param items: Approval items
        :type items: Dictionary
        :return: Clicked button index or None
        :rtype: Integer, NoneType
        """
        if not items:
            buttons = [button for button in message_box.buttons() if button.text() != "Cancel"]
            self._disable_widget(buttons)
        result = message_box.exec_()
        if result in (0, 1):
            clicked_button = message_box.clickedButton()
            return result, clicked_button.objectName()
        return None, None

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

    def refresh(self):
        """
        Refresh checked items store and model
        """
        self._checked_ids = OrderedDict()
        self._model.refresh()
        self._on_uncheck_disable_widgets()

    def _on_uncheck_disable_widgets(self):
        """
        Disable Workflow Manager widgets on uncheck
        """
        status = self._get_stored_status()
        if not self._checked_ids:
            self._close_tab(1)
            self._disable_widget([
                self.approveButton, self.disapproveButton,
                self.holdersButton, self.documentsButton,
                self.commentsButton
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
