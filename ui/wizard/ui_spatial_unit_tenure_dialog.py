# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_spatial_unit_tenure_dialog.ui'
#
# Created: Wed Jul 12 04:36:40 2017
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_SpatialUnitTenureDialog(object):
    def setupUi(self, SpatialUnitTenureDialog):
        SpatialUnitTenureDialog.setObjectName(_fromUtf8("SpatialUnitTenureDialog"))
        SpatialUnitTenureDialog.resize(318, 252)
        self.gridLayout = QtGui.QGridLayout(SpatialUnitTenureDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.buttonBox = QtGui.QDialogButtonBox(SpatialUnitTenureDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 1)
        self.sp_tenure_view = ListPairTableView(SpatialUnitTenureDialog)
        self.sp_tenure_view.setObjectName(_fromUtf8("sp_tenure_view"))
        self.gridLayout.addWidget(self.sp_tenure_view, 1, 0, 1, 1)
        self.label = QtGui.QLabel(SpatialUnitTenureDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.retranslateUi(SpatialUnitTenureDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), SpatialUnitTenureDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), SpatialUnitTenureDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(SpatialUnitTenureDialog)

    def retranslateUi(self, SpatialUnitTenureDialog):
        SpatialUnitTenureDialog.setWindowTitle(QtGui.QApplication.translate("SpatialUnitTenureDialog", "Spatial Unit Tenure Types", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("SpatialUnitTenureDialog", "<html><head/><body><p>Specify the tenure type corresponding to each spatial unit</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))

from ..customcontrols import ListPairTableView
