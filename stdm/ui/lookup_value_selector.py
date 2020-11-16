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
from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import (
    QStandardItem,
    QStandardItemModel
)
from qgis.PyQt.QtWidgets import (
    QApplication,
    QDialog
)

from stdm.settings import current_profile
from stdm.ui.notification import NotificationBar
from stdm.ui.gui_utils import GuiUtils


WIDGET, BASE = uic.loadUiType(
    GuiUtils.get_ui_file_path('ui_lookup_value_selector.ui'))


class LookupValueSelector(WIDGET, BASE):
    """
    A dialog that enables to select a value and code from a lookup.
    .. versionadded:: 1.5
    """

    def __init__(self, parent, lookup_entity_name, profile=None):
        """
        Initializes LookupValueSelector.
        :param parent: The parent of the dialog.
        :type parent: QWidget
        :param lookup_entity_name: The lookup entity name
        :type lookup_entity_name: String
        :param profile: The current profile object
        :type profile: Object
        """
        QDialog.__init__(self, parent, Qt.WindowTitleHint |
                         Qt.WindowCloseButtonHint)
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
        """
        Populates the lookup values and codes.
        """
        self.value_and_code = self.lookup_entity.values

        for value, code in self.value_and_code.items():
            u_value = str(value)
            code_value = self.lookup_entity.values[u_value]

            value_code = QStandardItem('{} ({})'.format(
                code_value.value, code.code
            )
            )
            value_code.setData(code.code)
            self._view_model.appendRow(value_code)

    def validate_selected_code(self):
        """
        Validate the selected code for the presence of Code or not.
        """
        self.notice.clear()
        self.selected_code_value()
        if self.selected_code == '':
            notice = QApplication.tr(self, 'The selected value has no code.')
            self.notice.insertWarningNotification(notice)

    def selected_code_value(self):
        """
        Get the selected lookup value.
        """
        index = self.value_list_box.currentIndex()
        item = self._view_model.itemFromIndex(index)
        self.selected_code = item.data()
        self.selected_value_code = item.text()

    def accept(self):
        """
        Overridden QDialog accept method.
        """
        self.selected_code_value()
        self.done(1)

    def reject(self):
        """
        Overridden QDialog accept method.
        """
        self.selected_code = None
        self.selected_value_code = None
        self.done(0)
