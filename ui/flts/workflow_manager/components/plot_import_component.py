"""
/***************************************************************************
Name                 : Plot Import Component
Description          : Plot import widget component for managing import of
                       a scheme plot.
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
from PyQt4.QtGui import QHBoxLayout
from stdm.ui.flts.workflow_manager.config import PlotImportButtonsConfig
from stdm.ui.flts.workflow_manager.components.widgets import Widgets


class PlotImportComponent:
    """
    Scheme workflow manager plot import component
    """
    def __init__(self):
        config = PlotImportButtonsConfig().buttons
        self._widgets = Widgets()
        self.components = OrderedDict()
        toolbar_buttons = self._create_buttons(config['toolbar'])
        self.components.update(toolbar_buttons)
        self.components.update({"stretcher": None})
        self.layout = self._add_to_layout(self.components, QHBoxLayout)

    def _create_buttons(self, options):
        """
        Dynamically creates QPushButton from options
        :param options: QPushButton configurations
        :type options: List
        :return: Dictionary of buttons - QPushButtons
        :rtype: OrderedDict
        """
        return self._widgets.create_buttons(options)

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