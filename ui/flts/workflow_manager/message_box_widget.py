from PyQt4.QtGui import (
    QMessageBox,
    QPushButton,
)


class MessageBox(QMessageBox):
    """
    Scheme workflow message box widget
    """
    def __init__(self, title=None, text=None, parent=None):
        QMessageBox.__init__(self, parent)
        self.setWindowTitle(title)
        self.setText(text)

    def add_buttons(self, buttons):
        """
        Adds buttons to QMessageBox
        :param buttons: Button options
        :type buttons: List
        """
        for button, role in buttons:
            self.addButton(button, role)

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


class MessageBoxButtons:
    """
    QMessageBox QPushButton buttons
    """
    def __init__(self, options, parent):
        self._options = options
        self._parent = parent

    def create_buttons(self):
        """
        Dynamically creates buttons from the options
        :return buttons: QPushButton and roles
        :rtype buttons: List
        """
        buttons = []
        for option in self._options:
            button = QPushButton(option.label, self._parent)
            if option.name:
                button.setObjectName(option.name)
            if option.icon:
                button.setIcon(option.icon)
            buttons.append((button, option.role))
        return buttons


class ApproveMessageBoxWidget(MessageBox):
    """
    Approve message box widget
    """
    def __init__(self, title, text, parent):
        MessageBox.__init__(self, title, text, parent)


class DisapproveMessageBoxWidget(MessageBox):
    """
    Disapprove message box widget
    """
    def __init__(self, title, text, parent):
        MessageBox.__init__(self, title, text, parent)


class HoldMessageBoxWidget(MessageBox):
    """
    Hold message box widget
    """
    def __init__(self, title, text, parent):
        MessageBox.__init__(self, title, text, parent)


def get_message_box(name):
    """
    Returns a QMessageBox object
    :param name: Clicked toolbar button object name
    :type name: String
    :return: QMessageBox object
    :rtype: QMessageBox
    """

    message_box = {
        "approveButton": ApproveMessageBoxWidget,
        "disapproveButton": DisapproveMessageBoxWidget,
        "holdButton": HoldMessageBoxWidget
    }
    return message_box[name]
