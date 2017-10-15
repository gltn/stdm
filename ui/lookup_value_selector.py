# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : lookup value selector
Description          : Enables the selection of lookup values from a
                        lookup entity.
Date                 : 09/February/2017
copyright            : (C) 2017 by UN-Habitat and implementing partners.
                       See the accompanying file CONTRIBUTORS.txt in the root
email                : stdm@unhabitat.org
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
from PyQt4.QtGui import (
    QApplication,
    QDialog,
    QStandardItem,
    QStandardItemModel
)
from PyQt4.QtCore import Qt
from stdm.ui.notification import NotificationBar
from ui_lookup_value_selector import Ui_LookupValueSelector
from stdm.settings import current_profile


class LookupValueSelector(QDialog, Ui_LookupValueSelector):
    """
    A dialog that enables to select a value and code from a lookup.
    .. versionadded:: 1.5
    """

    def __init__(self, parent, lookup_entity_name, profile=None):
        """

        """
        QDialog.__init__(self, parent, Qt.WindowTitleHint|Qt.WindowCloseButtonHint)
        self.setupUi(self)
        self.value_and_code = None
        if profile is None:
            self._profile = current_profile()
        else:
            self._profile = profile

        self.lookup_entity = self._profile.entity_by_name(
            '{}_{}'.format(self._profile.prefix, lookup_entity_name)
        )

        self.notice = NotificationBar(self.notice_bar)
        self._view_model = QStandardItemModel()
        self.value_list_box.setModel(self._view_model)
        header_item = QStandardItem(lookup_entity_name)
        self._view_model.setHorizontalHeaderItem(0, header_item)
        self.populate_value_list_view()

        self.selected_code = None
        self.selected_value_code = None

        self.value_list_box.clicked.connect(self.validate_selected_code)


    def populate_value_list_view(self):
        self.value_and_code = self.lookup_entity.values
        for value, code in self.value_and_code.iteritems():
            value_code = QStandardItem('{} ({})'.format(value, code.code))
            value_code.setData(code.code)
            self._view_model.appendRow(value_code)

    def validate_selected_code(self):
        self.notice.clear()
        self.selected_code_value()
        if self.selected_code == '':
            notice = QApplication.tr(self, 'The selected value has no code.')
            self.notice.insertWarningNotification(notice)

    def selected_code_value(self):
        index = self.value_list_box.currentIndex()
        item = self._view_model.itemFromIndex(index)
        self.selected_code = item.data()
        self.selected_value_code = item.text()

    def accept(self):
        self.selected_code_value()
        self.done(1)

    def reject(self):
        self.selected_code = None
        self.selected_value_code = None
        self.done(0)