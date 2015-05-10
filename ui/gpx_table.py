from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ui_gpx_table_widget import Ui_Dialog


class GPXTableDialog(QDialog, Ui_Dialog):

    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setupUi(self)