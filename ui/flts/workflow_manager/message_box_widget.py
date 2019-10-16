from PyQt4.QtGui import (
    QMessageBox,
    QPushButton,
)


class MessageBoxWidget(QMessageBox):
    """
    Scheme workflow message box widget
    """
    def __init__(self, parent=None):
        QMessageBox.__init__(self, parent)
        self._button = QPushButton()

    def create_buttons(self, options):
        """
        Dynamically creates buttons from the options
        :param options: QMessageBox configuration options
        :type options: Dictionary
        """
        for option in options:
            self._button = option.pushButton
            if option.name:
                self._button.setObjectName(option.name)
            if option.icon:
                self._button.setIcon(option.icon)
            self.addButton(self._button, option.role)

    def remove_buttons(self):
        """
        Removes and deletes buttons
        """
        buttons = self.buttons()
        for button in buttons:
            self.removeButton(button)
            button.deleteLater

    def enable_buttons(self, items):
        """
        Changes button active state
        :param items: Approval items
        :type items: Dictionary
        """
        buttons = self.buttons()
        for button in buttons:
            if not items and button.text() != "Cancel":
                button.setEnabled(False)
                continue
            button.setEnabled(True)
