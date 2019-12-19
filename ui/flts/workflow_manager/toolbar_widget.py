from collections import OrderedDict
from PyQt4.QtGui import (
    QPushButton,
    QLineEdit,
    QComboBox,
    QHBoxLayout
)
from stdm.ui.flts.workflow_manager.config import ToolbarButtonsConfig


class ToolbarWidget:
    """
    Scheme workflow manager toolbar widget
    """
    def __init__(self):
        self.config = ToolbarButtonsConfig().buttons
        self.widgets = OrderedDict()

    def create_search_widget(self):
        """
        Creates toolbar search widget
        :return search: Search QWidgets
        :rtype search: OrderedDict
        """
        search = OrderedDict()
        search["searchEdit"] = self.create_line_editor()
        search["filterComboBox"] = self.create_combobox()
        search.update(self.create_buttons(self.config['searchButton']))
        return search

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
            button.setEnabled(False)
            if option.name:
                button.setObjectName(option.name)
            if option.icon:
                button.setIcon(option.icon)
                button.setIconSize(option.size)
            buttons[option.name] = button
        return buttons

    @staticmethod
    def create_line_editor():
        """
        Creates toolbar QLineEditor
        :return editor: Line text editor
        :rtype editor: QLineEdit
        """
        editor = QLineEdit()
        editor.setPlaceholderText("Type to search...")
        editor.setObjectName("searchEdit")
        return editor

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

    def get_widget(self, name):
        """
        Return Toolbar widget
        :param name: QWidget object name
        :type: String
        :return: Toolbar widget
        :rtype: QWidget
        """
        return self.widgets[name]

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
        for widget in widgets.values():
            layout.addWidget(widget)
        layout.setMargin(0)
        return layout


class SchemeExamination(ToolbarWidget):
    """
    Scheme Examination toolbar widget
    """
    def __init__(self):
        ToolbarWidget.__init__(self)
        self._create_widgets()
        self.layout = self.add_to_layout(self.widgets, QHBoxLayout)

    def _create_widgets(self):
        """
        Creates Scheme Examination toolbar widgets
        """
        options = self.config['schemeExamination'] + self.config["sharedButtons"]
        self.widgets.update(self.create_buttons(options))
        self.widgets.update(self.create_search_widget())


class SchemeLodgementToolbarWidget(ToolbarWidget):
    """
    Scheme Lodgement toolbar widget
    """
    def __init__(self):
        ToolbarWidget.__init__(self)
        self._create_widgets()
        self.layout = self.add_to_layout(self.widgets, QHBoxLayout)

    def _create_widgets(self):
        """
        Creates Scheme Lodgement toolbar widgets
        """
        options = self.config['schemeLodgement'] + self.config["sharedButtons"]
        self.widgets.update(self.create_buttons(options))
        self.widgets.update(self.create_search_widget())


class SchemeEstablishmentToolbarWidget(SchemeExamination):
    """
    Scheme Establishment toolbar widget
    """
    def __init__(self):
        SchemeExamination.__init__(self)


class FirstExaminationtToolbarWidget(SchemeExamination):
    """
    First Examination toolbar widget
    """
    def __init__(self):
        SchemeExamination.__init__(self)


class SecondExaminationToolbarWidget(SchemeExamination):
    """
    Second Examination toolbar widget
    """
    def __init__(self):
        SchemeExamination.__init__(self)


class ThirdExaminationToolbarWidget(ToolbarWidget):
    """
    Third Examination toolbar widget
    """

    def __init__(self):
        ToolbarWidget.__init__(self)
        self._create_widgets()
        self.layout = self.add_to_layout(self.widgets, QHBoxLayout)

    def _create_widgets(self):
        """
        Creates Third Examination toolbar widgets
        """
        options = self.config['schemeExamination'] + \
                  self.config["thirdExamination"] + \
                  self.config["sharedButtons"]
        self.widgets.update(self.create_buttons(options))
        self.widgets.update(self.create_search_widget())


class ImportPlotToolbarWidget(ToolbarWidget):
    """
    Import Plot toolbar widget
    """
    def __init__(self):
        ToolbarWidget.__init__(self)
        self._create_widgets()
        self.layout = self.add_to_layout(self.widgets, QHBoxLayout)

    def _create_widgets(self):
        """
        Creates Scheme Plot toolbar widgets
        """
        options = self.config['importPlot'] + self.config["sharedButtons"]
        self.widgets.update(self.create_buttons(options))
        self.widgets.update(self.create_search_widget())


def get_toolbar(name):
    """
    Returns toolbar widget object
    :param name: Workflow Manager object name
    :type name: String
    :return: ToolbarWidget object
    :rtype: ToolbarWidget
    """

    toolbar = {
        "schemeLodgement": SchemeLodgementToolbarWidget(),
        "schemeEstablishment": SchemeEstablishmentToolbarWidget(),
        "firstExamination": FirstExaminationtToolbarWidget(),
        "secondExamination": SecondExaminationToolbarWidget(),
        "thirdExamination": ThirdExaminationToolbarWidget(),
        "importPlot": ImportPlotToolbarWidget()

    }
    return toolbar[name]
