# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_gps_tool.ui'
#
# Created: Sun May 10 06:17:05 2015
#      by: PyQt4 UI code generator 4.10.4
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

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(597, 202)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.groupBox = QtGui.QGroupBox(Dialog)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_4 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.bn_gpx_select_file = QtGui.QPushButton(self.groupBox)
        self.bn_gpx_select_file.setObjectName(_fromUtf8("bn_gpx_select_file"))
        self.gridLayout_2.addWidget(self.bn_gpx_select_file, 0, 2, 1, 1)
        self.lblGPXFile = QtGui.QLabel(self.groupBox)
        self.lblGPXFile.setObjectName(_fromUtf8("lblGPXFile"))
        self.gridLayout_2.addWidget(self.lblGPXFile, 0, 0, 1, 1)
        self.tx_fl_edit_gpx = gui.QgsFileDropEdit(self.groupBox)
        self.tx_fl_edit_gpx.setObjectName(_fromUtf8("tx_fl_edit_gpx"))
        self.gridLayout_2.addWidget(self.tx_fl_edit_gpx, 0, 1, 1, 1)
        self.gridLayout_4.addLayout(self.gridLayout_2, 0, 0, 1, 1)
        self.gridLayout_3 = QtGui.QGridLayout()
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.rd_gpx_waypoints = QtGui.QRadioButton(self.groupBox)
        self.rd_gpx_waypoints.setEnabled(True)
        self.rd_gpx_waypoints.setChecked(True)
        self.rd_gpx_waypoints.setObjectName(_fromUtf8("rd_gpx_waypoints"))
        self.gridLayout_3.addWidget(self.rd_gpx_waypoints, 0, 1, 1, 1)
        self.rd_gpx_tracks = QtGui.QRadioButton(self.groupBox)
        self.rd_gpx_tracks.setEnabled(True)
        self.rd_gpx_tracks.setObjectName(_fromUtf8("rd_gpx_tracks"))
        self.gridLayout_3.addWidget(self.rd_gpx_tracks, 1, 1, 1, 1)
        self.lblGPXFeatureTypes = QtGui.QLabel(self.groupBox)
        self.lblGPXFeatureTypes.setObjectName(_fromUtf8("lblGPXFeatureTypes"))
        self.gridLayout_3.addWidget(self.lblGPXFeatureTypes, 0, 0, 1, 1)
        self.rd_gpx_routes = QtGui.QRadioButton(self.groupBox)
        self.rd_gpx_routes.setObjectName(_fromUtf8("rd_gpx_routes"))
        self.gridLayout_3.addWidget(self.rd_gpx_routes, 2, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem, 1, 2, 1, 1)
        self.gridLayout_4.addLayout(self.gridLayout_3, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 1)
        self.lblGPXFile.setBuddy(self.bn_gpx_select_file)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.groupBox.setTitle(_translate("Dialog", "Import GPS Points", None))
        self.bn_gpx_select_file.setText(_translate("Dialog", "Browse...", None))
        self.lblGPXFile.setText(_translate("Dialog", "File", None))
        self.rd_gpx_waypoints.setText(_translate("Dialog", "Waypoint", None))
        self.rd_gpx_tracks.setText(_translate("Dialog", "Track", None))
        self.lblGPXFeatureTypes.setText(_translate("Dialog", "Feature types", None))
        self.rd_gpx_routes.setText(_translate("Dialog", "Route", None))

from qgis import gui

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

