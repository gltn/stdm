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
from PyQt4 import QtCore
from PyQt4.QtGui import (
    QDialog,
    QPlainTextEdit,
    QPainter
)

from ui_scheme_establishment import Ui_scheme_establish_dialog


class EstablishmentDialog(QDialog, Ui_scheme_establish_dialog):
    """
    Dialog that provides shortcut actions upon loading the establishment dialog.
    """

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.checkbox_color()

    def checkbox_color(self):
        """
        Give the checkbox labels color to distinguish
        between the functions.
        """
        self.chk_approve.setStyleSheet("QWidget { color: green}")
        self.chk_disapprove.setStyleSheet("QWidget { color: red}")

    @property
    def placeholder_text(self):
        if not hasattr(self, "_placeholder"):
            self.textEdit_approval = ""
            return self.textEdit_approval

    @placeholder_text.setter
    def place_holder_text(self, text):
        self.textEdit_approval = text
        self.update()

    def paint_event(self, event):
        super(EstablishmentDialog, self).paintEvent(event)

        if (
                self.placeholderText
                and self.document().isEmpty()
                and not self.isPreediting()
        ):
            painter = QPainter(self.viewport())
            col = self.palette().text().color()
            col.setAlpha(128)
            painter.setPen(col)
            margin = int(self.document().documentMargin())
            painter.drawText(
                self.viewport().rect().adjusted(margin, margin, -margin, -margin),
                QtCore.Qt.AlignTop | QtCore.Qt.TextWordWrap,
                self.placeholderText,
            )

    def click_action(self):
        """
        clear placeholder text on user selection
        """
        pass

    def approve_action(self):
        """
        When the user approves
        """
        pass

    def disapprove_action(self):
        """
        When the user disapproves
        """
        pass


if __name__ == '__main__':
    import sys

    app = QDialog.QApplication(sys.argv)
    te = QPlainTextEdit()
    te.placeholder_text = "Please insert comments here..."
    establish_dialog = EstablishmentDialog()
    establish_dialog.show()
    sys.exit(app.exec_())
