"""
/***************************************************************************
Name                 : user Shortcut Dialog
Description          : Dialog for selecting user actions after login.
Date                 : 01/July/2019
copyright            : (C) 2019 by Joseph Kariuki
email                : joehene@gmail.com
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
from PyQt4.QtCore import (
    Qt
)

from PyQt4.QtGui import (
    QDialog,
    QIcon,
    QListWidgetItem,
    QTreeWidgetItem,
    QMessageBox,
    QApplication
)

from .ui_user_shortcut import Ui_UserShortcutDialog
from ..notification import NotificationBar,ERROR


class UserShortcutDialog(QDialog, Ui_UserShortcutDialog):
    """
    Dialog that provides shortcut actions upon successful login.
    """
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.load_categories()

        # Connect signals
        # On tree item changed
        self.tr_title_category.itemSelectionChanged.connect(
            self.on_category_item_changed
        )
        self.lsw_category_action.itemDoubleClicked.connect(
            self.on_category_list_item_db_clicked
        )

        self.buttonBox.accepted.connect(
            self.accept_dlg
        )

        # Select scheme item in the tree widget
        self.tr_title_category.setCurrentItem(self.lht_scheme_item)

        # Configure notification bar
        self.notif_bar = NotificationBar(self.vlNotification)

        # User selected action code upon accept
        self._action_code = ''

    @property
    def action_code(self):
        """
        :return:Returns the code representing the user action
        :type: str
        """
        return self._action_code

    def module_icons(self):
        """
        Accessing the module icon file display.
        """
        # Container of list items based on category
        self._scheme_items = []
        self._certificate_items = []
        self._notification_items = []
        self._report_items = []
        self._search_items = []

        self.lsi_lodge_scheme = QListWidgetItem(
            QIcon(':/plugins/stdm/images/icons/flts_scheme_assessment.png'),
            self.tr('Lodgement')
        )
        self.lsi_establish_scheme = QListWidgetItem(
            QIcon(':/plugins/stdm/images/icons/flts_scheme_management.png'),
            self.tr('Establishment')
        )
        self.lsi_first_examination = QListWidgetItem(
            QIcon(':/plugins/stdm/images/icons/flts_scheme_management2.png'),
            self.tr('First Examination')
        )
        self.lsi_second_examination = QListWidgetItem(
            QIcon(':/plugins/stdm/images/icons/flts_scheme_management3.png'),
            self.tr('Second Examination')
        )
        self.lsi_third_examination = QListWidgetItem(
            QIcon(':/plugins/stdm/images/icons/flts_third_examination.png'),
            self.tr('Third Examination')
        )
        self.lsi_revision = QListWidgetItem(
            QIcon(':/plugins/stdm/images/icons/flts_revision.png'),
            self.tr('Revision')
        )
        self.lsi_import_plots = QListWidgetItem(
            QIcon(':/plugins/stdm/images/icons/flts_import_plot.png'),
            self.tr('Import Plots')
        )
        self.lsi_print_certificate = QListWidgetItem(
            QIcon(':/plugins/stdm/images/icons/flts_print.png'),
            self.tr('Print Certificate')
        )
        self.lsi_scan_certificate = QListWidgetItem(
            QIcon(':/plugins/stdm/images/icons/flts_scan.png'),
            self.tr('Scan Certificate')
        )
        self.lsi_search = QListWidgetItem(
            QIcon(':/plugins/stdm/images/icons/flts_search.png'),
            self.tr('Search')
        )
        self.lsi_report = QListWidgetItem(
            QIcon(':/plugins/stdm/images/icons/flts_report.png'),
            self.tr('Report')
        )
        self.lsi_notification = QListWidgetItem(
            QIcon(':/plugins/stdm/images/icons/flts_notification.png'),
            self.tr('Notification')
        )

        # Assign unique identifier to the list item
        self.lsi_lodge_scheme.setData(Qt.UserRole, 'LDG_SCM')
        self.lsi_establish_scheme.setData(Qt.UserRole, 'EST_SCM')
        self.lsi_first_examination.setData(Qt.UserRole, 'EXM_SCM')
        self.lsi_second_examination.setData(Qt.UserRole, 'EXM2_SCM')
        self.lsi_third_examination.setData(Qt.UserRole, 'EXM3_SCM')
        self.lsi_import_plots.setData(Qt.UserRole, 'PLT_SCM')
        self.lsi_print_certificate.setData(Qt.UserRole, 'P_CRT')
        self.lsi_scan_certificate.setData(Qt.UserRole, 'S_CRT')
        self.lsi_notification.setData(Qt.UserRole, 'NTF')
        self.lsi_search.setData(Qt.UserRole, 'SRC')
        self.lsi_report.setData(Qt.UserRole, 'RPT')

        # Assigning items to the scheme items
        self._scheme_items.append(self.lsi_lodge_scheme)
        self._scheme_items.append(self.lsi_establish_scheme)
        self._scheme_items.append(self.lsi_first_examination)
        self._scheme_items.append(self.lsi_second_examination)
        self._scheme_items.append(self.lsi_third_examination)
        self._scheme_items.append(self.lsi_import_plots)

        # Certificate items
        self._certificate_items.append(self.lsi_print_certificate)
        self._certificate_items.append(self.lsi_scan_certificate)

        # Notification items
        self._notification_items.append(self.lsi_notification)

        # Search items
        self._search_items.append(self.lsi_search)

        # Report items
        self._report_items.append(self.lsi_report)

    def load_categories(self):
        # Load items based on category selection
        self.lht_tr_item = QTreeWidgetItem(['Land Hold Title', 'LHT'])
        self.lht_scheme_item = QTreeWidgetItem(['Scheme', 'SCM'])
        self.lht_certificate_item = QTreeWidgetItem(['Certificate', 'CRT'])
        self.lht_notification_item = QTreeWidgetItem(['Notification', 'NTF'])
        self.lht_search_item = QTreeWidgetItem(['Search', 'SRC'])
        self.lht_report_item = QTreeWidgetItem(['Report', 'RPT'])

        self.tr_title_category.addTopLevelItem(self.lht_tr_item)
        # Hide code column
        self.tr_title_category.hideColumn(1)

        self.lht_tr_item.addChild(self.lht_scheme_item)
        self.lht_tr_item.addChild(self.lht_certificate_item)
        self.lht_tr_item.addChild(self.lht_notification_item)
        self.lht_tr_item.addChild(self.lht_search_item)
        self.lht_tr_item.addChild(self.lht_report_item)

        # Expand base categories
        self.tr_title_category.expandItem(self.lht_tr_item)

    def _clear_category_items(self):
        # Remove all items without deleting them
        print self.lsw_category_action.count()
        for i in range(self.lsw_category_action.count()):
            row_item = self.lsw_category_action.item(i)
            print row_item

            if row_item != 0:
                # print row_item.text()
                self.lsw_category_action.takeItem(i)

    def _load_category_items(self, lst_items):
        for it in lst_items:
            self.lsw_category_action.addItem(it)

    def on_category_item_changed(self):
        # Load list items based on selected category
        # Clear list first
        self.lsw_category_action.clear()

        sel_tr_items = self.tr_title_category.selectedItems()
        if len(sel_tr_items) == 0:
            return

        self.module_icons()

        # Get selected items
        tr_cat_item = sel_tr_items[0]
        cat_code = tr_cat_item.data(1, Qt.DisplayRole)
        if cat_code == 'SCM':
            self._load_category_items(self._scheme_items)
        elif cat_code == 'CRT':
            self._load_category_items(self._certificate_items)
        elif cat_code == 'RPT':
            self._load_category_items(self._report_items)
        elif cat_code == 'SRC':
            self._load_category_items(self._search_items)
        elif cat_code == 'NTF':
            self._load_category_items(self._notification_items)

    def on_category_list_item_db_clicked(self, item):
        # Load dialog based on specified action
        # get selected items
        data = item.data(Qt.UserRole)
        self._action_code = data
        self.accept()

    def accept_dlg(self):
        # Check if the user has selected an action from the list widget
        self.notif_bar.clear()

        selected_items = self.lsw_category_action.selectedItems()

        if len(selected_items) == 0:
            self.notif_bar.insertWarningNotification(
                self.tr("Please select an operation to perform"))
            return

        self._action_code = selected_items[0].data(Qt.UserRole)
        self.accept()

