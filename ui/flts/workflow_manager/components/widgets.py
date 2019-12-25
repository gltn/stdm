"""
/***************************************************************************
Name                 : Workflow Manager Widget
Description          : Widget for managing workflow and notification in
                       Scheme Establishment and First, Second and
                       Third Examination FLTS modules.
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
from PyQt4.QtGui import QPushButton


class Widgets:
    """
    Widgets creator
    """
    @staticmethod
    def create_buttons(options):
        """
        Dynamically creates QPushButton from options
        :param options: QPushButton configurations
        :type options: List
        :return buttons: Dictionary of buttons - QPushButtons
        :rtype buttons: OrderedDict
        """
        buttons = OrderedDict()
        for option in options:
            button = QPushButton(option.label)
            button.setEnabled(option.enable)
            if option.name:
                button.setObjectName(option.name)
            if option.icon:
                button.setIcon(option.icon)
            if option.size:
                button.setIconSize(option.size)
            buttons[option.name] = button
        return buttons

    @staticmethod
    def add_to_layout(widgets, layout):
        """
        Adds QWidgets to QBoxLayout
        :param widgets: Widgets to be added to the layout
        :param widgets: QWidget
        :param layout: Widget layout
        :type layout: QBoxLayout
        :return layout: Layout of QPushButton(s)
        :rtype layout: QBoxLayout
        """
        layout = layout()
        for name, widget in widgets.items():
            if name != "stretcher":
                layout.addWidget(widget)
            else:
                layout.addStretch()
        layout.setMargin(0)
        return layout
