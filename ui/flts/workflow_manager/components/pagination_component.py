"""
/***************************************************************************
Name                 : Pagination Component
Description          : Pagination widget component for navigating page records in
                       Scheme Establishment First, Second and Third Examination
                       and Scheme Revision FLTS modules.
Date                 : 24/December/2019
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
from PyQt4.QtCore import Qt
from PyQt4.QtGui import (
    QLineEdit,
    QHBoxLayout
)
from stdm.ui.flts.workflow_manager.config import PaginationButtonsConfig
from stdm.ui.flts.workflow_manager.components.widgets import Widgets


class PaginationComponent:
    """
    Scheme workflow manager pagination component
    """
    def __init__(self):
        config = PaginationButtonsConfig().buttons
        self._widgets = Widgets()
        components = OrderedDict()
        previous_buttons = self._create_buttons(config['previousButtons'])
        next_buttons = self._create_buttons(config['nextButtons'])
        line_editor = self._create_line_editor()
        components.update(previous_buttons)
        components[line_editor.objectName()] = line_editor
        components.update(next_buttons)
        self.layout = self._add_to_layout(components, QHBoxLayout)

    def _create_buttons(self, options):
        """
        Dynamically creates QPushButton from options
        :param options: QPushButton configurations
        :type options: List
        :return: Dictionary of buttons - QPushButtons
        :rtype: OrderedDict
        """
        return self._widgets.create_buttons(options)

    @staticmethod
    def _create_line_editor():
        """
        Creates pagination QLineEditor
        :return editor: Line text editor
        :rtype editor: QLineEdit
        """
        line_editor = QLineEdit("No Records")
        line_editor.setAlignment(Qt.AlignCenter)
        line_editor.setObjectName("paginationRecords")
        return line_editor

    def _add_to_layout(self, widgets, layout):
        """
        Adds QWidgets to QBoxLayout
        :param widgets: Widgets to be added to the layout
        :param widgets: QWidget
        :param layout: Widget layout
        :type layout: QBoxLayout
        :return: Layout of QPushButton(s)
        :rtype: QBoxLayout
        """
        return self._widgets.add_to_layout(widgets, layout)
