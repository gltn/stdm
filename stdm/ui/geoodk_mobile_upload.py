
import os

from PyQt4 import uic
from PyQt4.QtGui import (
    QDialog,
    QFileSystemModel,
    QMessageBox

)
from PyQt4.QtCore import *



FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui_mobile_upload_form.ui'))


class FormUploader(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Class Constructor."""
        super(FormUploader, self).__init__(parent)

        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-aut o-connect
        self.connect_action = pyqtSignal(str)
        self.setupUi(self)
        self.enumerate_current_drives()

    def enumerate_current_drives(self):
        """
        Enumerate all the current drives in my computer
        :return: drive list
        """
        model = QFSFileEngine()
        for drive in model.drives():
            self.cbo_path.insertItem(0,str(drive.absolutePath()))
        # self.dirs = QFileSystemModel()
        # self.dirs.setFilter(QDir.Drives)
        # self.dirs.setRootPath(self.dirs.myComputer())
        # self.cbo_path.setModel(self.dirs)

    def feedback_message(self, msg):
        """
        Create a dialog box to capture and display errrors related to db
        while importing data
        :param: msg
        :type: string
        :return:Qdialog
        """
        msgbox = QMessageBox()
        msgbox.setStandardButtons(QMessageBox.Ok | QMessageBox.No)
        msgbox.setWindowTitle("Data Import")
        msgbox.setText(msg)
        msgbox.exec_()
        msgbox.show()
        return msgbox
