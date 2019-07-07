"""
/***************************************************************************
Name                 : Scheme Establishment Dialog
Description          : Dialog for establishing a new scheme.
Date                 : 01/July/2019
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

from PyQt4.QtGui import (
    QDialog
)

from ui_scheme_establishment import Ui_scheme_establish_dialog


class EstablishmentDialog(QDialog, Ui_scheme_establish_dialog):
    """
    Dialog that provides shortcut actions upon loading the establishment dialog.
    """

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)


if __name__ == '__main__':
    import sys

    app = QDialog.QApplication(sys.argv)
    establish_dialog = EstablishmentDialog()
    establish_dialog.show()
    sys.exit(app.exec_())
