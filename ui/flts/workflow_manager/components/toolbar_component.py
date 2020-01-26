"""
/***************************************************************************
Name                 : Toolbar Component
Description          : Toolbar widget component for navigating page records in
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
from PyQt4.QtGui import (
    QLineEdit,
    QComboBox,
    QHBoxLayout
)
from stdm.ui.flts.workflow_manager.config import ToolbarButtonsConfig
from stdm.ui.flts.workflow_manager.components.widgets import Widgets


class SearchComponent:
    """
    Scheme workflow manager search component
    """
    def __init__(self):
        self.widgets = Widgets()

    def create_component(self, options):
        """
        Creates search component widget
        :param options: QPushButton configurations
        :type options: List
        :return components: Search widget components
        :rtype components: OrderedDict
        """
        search = OrderedDict()
        line_editor = self.create_line_editor()
        search[line_editor.objectName()] = line_editor
        combobox = self.create_combobox()
        search[combobox.objectName()] = combobox
        buttons = self.create_buttons(options)
        search.update(buttons)
        return search

    @staticmethod
    def create_line_editor():
        """
        Creates toolbar QLineEditor
        :return editor: Line text editor
        :rtype editor: QLineEdit
        """
        line_editor = QLineEdit()
        line_editor.setPlaceholderText("Type to search...")
        line_editor.setObjectName("searchEdit")
        return line_editor

    @staticmethod
    def create_combobox():
        """
        Creates toolbar QComboBox
        :return combobox: Combobox
        :rtype combobox: QComboBox
        """
        combobox = QComboBox()
        combobox.setObjectName("filterComboBox")
        combobox.addItems(["Apply Filter"])
        return combobox

    def create_buttons(self, options):
        """
        Dynamically creates QPushButton from options
        :param options: QPushButton configurations
        :type options: List
        :return: Dictionary of buttons - QPushButtons
        :rtype: OrderedDict
        """
        return self.widgets.create_buttons(options)


class ToolbarComponent:
    """
    Scheme workflow manager toolbar component
    """
    def __init__(self):
        self.config = ToolbarButtonsConfig().buttons
        self.widgets = Widgets()
        self.search = SearchComponent()
        self.components = OrderedDict()

    def create_component(self, options):
        """
        Dynamically creates component widget
        :param options: QPushButton configurations
        :type options: List
        :return components: Toolbar widget components
        :rtype components: OrderedDict
        """
        buttons = self.create_buttons(options)
        search_widget = self.create_search()
        self.components.update(buttons)
        self.components.update({"stretcher": None})
        self.components.update(search_widget)
        return self.components

    def create_buttons(self, options):
        """
        Dynamically creates QPushButton from options
        :param options: QPushButton configurations
        :type options: List
        :return: Dictionary of buttons - QPushButtons
        :rtype: OrderedDict
        """
        return self.widgets.create_buttons(options)

    def create_search(self):
        """
        Creates search component widget
        :return components: Search widget components
        :rtype components: OrderedDict
        """
        return self.search.create_component(self.config['searchButton'])

    def add_to_layout(self, widgets, layout):
        """
        Adds QWidgets to QBoxLayout
        :param widgets: Widgets to be added to the layout
        :param widgets: QWidget
        :param layout: Widget layout
        :type layout: QBoxLayout
        :return: Layout of QPushButton(s)
        :rtype: QBoxLayout
        """
        return self.widgets.add_to_layout(widgets, layout)


class SchemeExamination(ToolbarComponent):
    """
    Scheme Examination toolbar component
    """
    def __init__(self):
        ToolbarComponent.__init__(self)
        component = self._create_component()
        self.layout = self.add_to_layout(component, QHBoxLayout)

    def _create_component(self):
        """
        Creates Scheme Examination toolbar components from options list
        :return: Toolbar widget component
        :rtype: OrderedDict
        """
        options = self.config['schemeExamination'] + self.config["sharedButtons"]
        return self.create_component(options)


class SchemeLodgementToolbarComponent(ToolbarComponent):
    """
    Scheme Lodgement toolbar component
    """
    def __init__(self):
        ToolbarComponent.__init__(self)
        component = self._create_component()
        self.layout = self.add_to_layout(component, QHBoxLayout)

    def _create_component(self):
        """
        Creates Scheme Lodgement toolbar components from options list
        :return: Toolbar widget component
        :rtype: OrderedDict
        """
        options = self.config['schemeLodgement'] + self.config["sharedButtons"]
        return self.create_component(options)


class SchemeEstablishmentToolbarComponent(SchemeExamination):
    """
    Scheme Establishment toolbar component
    """
    def __init__(self):
        SchemeExamination.__init__(self)


class FirstExaminationtToolbarWidget(SchemeExamination):
    """
    First Examination toolbar component
    """
    def __init__(self):
        SchemeExamination.__init__(self)


class SecondExaminationToolbarWidget(SchemeExamination):
    """
    Second Examination toolbar component
    """
    def __init__(self):
        SchemeExamination.__init__(self)


class ThirdExaminationToolbarComponent(ToolbarComponent):
    """
    Third Examination toolbar component
    """

    def __init__(self):
        ToolbarComponent.__init__(self)
        component = self._create_component()
        self.layout = self.add_to_layout(component, QHBoxLayout)

    def _create_component(self):
        """
        Creates Third Examination toolbar components from options list
        :return: Toolbar widget component
        :rtype: OrderedDict
        """
        options = self.config['schemeExamination'] + \
                  self.config["thirdExamination"] + \
                  self.config["sharedButtons"]
        return self.create_component(options)


class ImportPlotToolbarComponent(ToolbarComponent):
    """
    Import Plot toolbar component
    """
    def __init__(self):
        ToolbarComponent.__init__(self)
        component = self._create_component()
        self.layout = self.add_to_layout(component, QHBoxLayout)

    def _create_component(self):
        """
        Creates Import Plot toolbar components from options list
        :return: Toolbar widget component
        :rtype: OrderedDict
        """
        options = self.config['importPlot'] + self.config["sharedButtons"]
        return self.create_component(options)


def get_toolbar(name):
    """
    Returns Scheme Workflow Manager toolbar component object
    :param name: Workflow Manager object name
    :type name: String
    :return: ToolbarComponent object
    :rtype: ToolbarComponent
    """

    toolbar = {
        "schemeLodgement": SchemeLodgementToolbarComponent(),
        "schemeEstablishment": SchemeEstablishmentToolbarComponent(),
        "firstExamination": FirstExaminationtToolbarWidget(),
        "secondExamination": SecondExaminationToolbarWidget(),
        "thirdExamination": ThirdExaminationToolbarComponent(),
        "importPlot": ImportPlotToolbarComponent()

    }
    return toolbar[name]
