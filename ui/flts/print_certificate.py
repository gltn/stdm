"""
/***************************************************************************
Name                 : Print Certificate Dialog
Description          : Dialog printing certificates.
Date                 : 03/July/2019
copyright            : (C) 2019 by Joseph Kariuki
email                : joehene@gmail.com
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
from PyQt4 import Qt
from PyQt4.QtGui import (
    QDialog
)

from ui_print_certificate import Ui_PrintCert_dialog


class PrintCertificateDialog(QDialog, Ui_PrintCert_dialog):
    """
    Dialog that displays the printing shortcut menus
    """

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)


if __name__ == '__main__':
    import sys

    app = QDialog.QApplication(sys.argv)
    print_dialog = PrintCertificateDialog()
    print_dialog.show()
    sys.exit(app.exec_())
