# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_coordinates_editor.ui'
#
# Created: Wed Apr 16 11:45:37 2014
#      by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_frmCoordinatesEditor(object):
    def setupUi(self, frmCoordinatesEditor):
        frmCoordinatesEditor.setObjectName(_fromUtf8("frmCoordinatesEditor"))
        frmCoordinatesEditor.resize(267, 151)
        self.gridLayout = QtGui.QGridLayout(frmCoordinatesEditor)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.vlNotification = QtGui.QVBoxLayout()
        self.vlNotification.setObjectName(_fromUtf8("vlNotification"))
        self.gridLayout.addLayout(self.vlNotification, 0, 0, 1, 1)
        self.coordWidget = CoordinatesWidget(frmCoordinatesEditor)
        self.coordWidget.setObjectName(_fromUtf8("coordWidget"))
        self.gridLayout.addWidget(self.coordWidget, 1, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(frmCoordinatesEditor)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 1)

        self.retranslateUi(frmCoordinatesEditor)
        QtCore.QMetaObject.connectSlotsByName(frmCoordinatesEditor)

    def retranslateUi(self, frmCoordinatesEditor):
        frmCoordinatesEditor.setWindowTitle(_translate("frmCoordinatesEditor", "Coordinates Pair Editor", None))

from customcontrols import CoordinatesWidget
