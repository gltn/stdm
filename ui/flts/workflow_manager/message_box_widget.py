from PyQt4.QtGui import QMessageBox


class MessageBoxWidget(QMessageBox):
    """
    Scheme workflow message box widget
    """
    def __init__(self, options, title=None, text=None, parent=None):
        QMessageBox.__init__(self, parent)
        self.setWindowTitle(title)
        self.setText(text)
        for option in options:
            button = option.pushButton
            if option.name:
                button.setObjectName(option.name)
            if option.icon:
                button.setIcon(option.icon)
            self.addButton(button, option.role)
