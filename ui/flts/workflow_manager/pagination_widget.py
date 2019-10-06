from PyQt4.QtCore import *
from PyQt4.QtGui import *
from stdm.ui.flts.workflow_manager.config import ButtonIcons


class PaginationWidget:
    """
    Scheme workflow pagination widget
    """
    def __init__(self):
        self.first_button = QPushButton("First")
        self.previous_button = QPushButton("Previous")
        self.next_button = QPushButton("Next")
        self.last_button = QPushButton("Last")
        self.pagination_edit = QLineEdit("No Records")
        self.pagination_edit.setAlignment(Qt.AlignCenter)
        self.pagination_layout = QHBoxLayout()
        self.pagination_layout.addWidget(self.first_button)
        self.pagination_layout.addWidget(self.previous_button)
        self.pagination_layout.addWidget(self.pagination_edit)
        self.pagination_layout.addWidget(self.next_button)
        self.pagination_layout.addWidget(self.last_button)
        self.pagination_layout.setMargin(0)
        self._set_button_icons()

    def _set_button_icons(self):
        """
        Sets QPushButton icons
        """
        icons = ButtonIcons(self)
        pagination_buttons = icons.pagination_buttons
        for button, options in pagination_buttons.iteritems():
            button.setIcon(options.icon)
            button.setIconSize(options.size)
