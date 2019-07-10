from PyQt4 import QtCore, QtGui


class TextEdit(QtGui.QTextEdit):
    @property
    def placeholderText(self):
        if not hasattr(self, "_placeholderText"):
            self._placeholderText = ""
        return self._placeholderText

    @placeholderText.setter
    def placeholderText(self, text):
        self._placeholderText = text
        self.update()

    def isPreediting(self):
        lay = self.textCursor().block().layout()
        if lay and lay.preeditAreaText():
            return True
        return False

    def paintEvent(self, event):
        super(TextEdit, self).paintEvent(event)

        if (
            self.placeholderText
            and self.document().isEmpty()
            and not self.isPreediting()
        ):
            painter = QtGui.QPainter(self.viewport())
            col = self.palette().text().color()
            col.setAlpha(128)
            painter.setPen(col)
            margin = int(self.document().documentMargin())
            painter.drawText(
                self.viewport().rect().adjusted(margin, margin, -margin, -margin),
                QtCore.Qt.AlignTop | QtCore.Qt.TextWordWrap,
                self.placeholderText,
            )


if __name__ == "__main__":
    import sys

    app = QtGui.QApplication(sys.argv)

    te = TextEdit()
    te.placeholderText = "Stack Overflow"

    w = QtGui.QWidget()
    lay = QtGui.QVBoxLayout(w)
    lay.addWidget(QtGui.QLineEdit())
    lay.addWidget(te)
    w.show()
    sys.exit(app.exec_())