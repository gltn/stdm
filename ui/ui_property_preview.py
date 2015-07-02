# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_property_preview.ui'
#
# Created: Thu Oct 16 13:32:44 2014
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

class Ui_frmPropertyPreview(object):
    def setupUi(self, frmPropertyPreview):
        frmPropertyPreview.setObjectName(_fromUtf8("frmPropertyPreview"))
        frmPropertyPreview.resize(545, 486)
        frmPropertyPreview.setMaximumSize(QtCore.QSize(16777215, 16777215))
        frmPropertyPreview.setTabPosition(QtGui.QTabWidget.South)
        self.local = QtGui.QWidget()
        self.local.setObjectName(_fromUtf8("local"))
        self.gridLayout = QtGui.QGridLayout(self.local)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.local_map = MirrorMap(self.local)
        self.local_map.setObjectName(_fromUtf8("local_map"))
        self.gridLayout.addWidget(self.local_map, 0, 0, 1, 1)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/stdm/images/icons/local.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        frmPropertyPreview.addTab(self.local, icon, _fromUtf8(""))
        self.web = QtGui.QWidget()
        self.web.setObjectName(_fromUtf8("web"))
        self.gridLayout_3 = QtGui.QGridLayout(self.web)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.btnSync = QtGui.QPushButton(self.web)
        self.btnSync.setObjectName(_fromUtf8("btnSync"))
        self.gridLayout_3.addWidget(self.btnSync, 4, 2, 1, 1)
        self.btnResetMap = QtGui.QPushButton(self.web)
        self.btnResetMap.setMinimumSize(QtCore.QSize(0, 0))
        self.btnResetMap.setObjectName(_fromUtf8("btnResetMap"))
        self.gridLayout_3.addWidget(self.btnResetMap, 3, 2, 1, 1)
        self.lblInfo = QtGui.QLabel(self.web)
        self.lblInfo.setEnabled(True)
        self.lblInfo.setText(_fromUtf8(""))
        self.lblInfo.setObjectName(_fromUtf8("lblInfo"))
        self.gridLayout_3.addWidget(self.lblInfo, 1, 0, 1, 3)
        self.groupBox = QtGui.QGroupBox(self.web)
        self.groupBox.setTitle(_fromUtf8(""))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setMargin(1)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.spatial_web_view = QtWebKit.QWebView(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spatial_web_view.sizePolicy().hasHeightForWidth())
        self.spatial_web_view.setSizePolicy(sizePolicy)
        self.spatial_web_view.setUrl(QtCore.QUrl(_fromUtf8("about:blank")))
        self.spatial_web_view.setObjectName(_fromUtf8("spatial_web_view"))
        self.gridLayout_2.addWidget(self.spatial_web_view, 0, 0, 1, 1)
        self.gridLayout_3.addWidget(self.groupBox, 2, 0, 1, 3)
        self.frame = QtGui.QFrame(self.web)
        self.frame.setFrameShape(QtGui.QFrame.NoFrame)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.verticalLayout = QtGui.QVBoxLayout(self.frame)
        self.verticalLayout.setMargin(1)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.zoomSlider = QtGui.QSlider(self.frame)
        self.zoomSlider.setMinimum(2)
        self.zoomSlider.setMaximum(20)
        self.zoomSlider.setProperty("value", 12)
        self.zoomSlider.setOrientation(QtCore.Qt.Horizontal)
        self.zoomSlider.setTickPosition(QtGui.QSlider.TicksBelow)
        self.zoomSlider.setTickInterval(2)
        self.zoomSlider.setObjectName(_fromUtf8("zoomSlider"))
        self.verticalLayout.addWidget(self.zoomSlider)
        self.label = QtGui.QLabel(self.frame)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.gridLayout_3.addWidget(self.frame, 3, 1, 2, 1)
        self.groupBox_2 = QtGui.QGroupBox(self.web)
        self.groupBox_2.setMinimumSize(QtCore.QSize(0, 50))
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout_5 = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout_5.setHorizontalSpacing(20)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.rbGMaps = QtGui.QRadioButton(self.groupBox_2)
        self.rbGMaps.setChecked(True)
        self.rbGMaps.setObjectName(_fromUtf8("rbGMaps"))
        self.gridLayout_5.addWidget(self.rbGMaps, 0, 0, 1, 1)
        self.rbOSM = QtGui.QRadioButton(self.groupBox_2)
        self.rbOSM.setObjectName(_fromUtf8("rbOSM"))
        self.gridLayout_5.addWidget(self.rbOSM, 0, 1, 1, 1)
        self.gridLayout_3.addWidget(self.groupBox_2, 3, 0, 2, 1)
        self.label_2 = QtGui.QLabel(self.web)
        self.label_2.setStyleSheet(_fromUtf8("color: rgb(255, 0, 0);"))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_3.addWidget(self.label_2, 0, 0, 1, 3)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/stdm/images/icons/web.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        frmPropertyPreview.addTab(self.web, icon1, _fromUtf8(""))

        self.retranslateUi(frmPropertyPreview)
        frmPropertyPreview.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(frmPropertyPreview)

    def retranslateUi(self, frmPropertyPreview):
        frmPropertyPreview.setWindowTitle(_translate("frmPropertyPreview", "Spatial Preview", None))
        frmPropertyPreview.setTabText(frmPropertyPreview.indexOf(self.local), _translate("frmPropertyPreview", "Local", None))
        self.btnSync.setToolTip(_translate("frmPropertyPreview", "Sync extents of web view with local view", None))
        self.btnSync.setText(_translate("frmPropertyPreview", "Sync", None))
        self.btnResetMap.setToolTip(_translate("frmPropertyPreview", "Zoom to spatial unit extents", None))
        self.btnResetMap.setText(_translate("frmPropertyPreview", "Reset Map", None))
        self.label.setText(_translate("frmPropertyPreview", "Zoom level", None))
        self.groupBox_2.setTitle(_translate("frmPropertyPreview", "Choose Base Layer", None))
        self.rbGMaps.setText(_translate("frmPropertyPreview", "Google Maps", None))
        self.rbOSM.setText(_translate("frmPropertyPreview", "Open Street Maps", None))
        self.label_2.setText(_translate("frmPropertyPreview", "Web overlay may vary from actual representation in the local map.", None))
        frmPropertyPreview.setTabText(frmPropertyPreview.indexOf(self.web), _translate("frmPropertyPreview", "Web", None))

from PyQt4 import QtWebKit
from mirror_map import MirrorMap
import resources_rc
