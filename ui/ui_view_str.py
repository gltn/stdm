# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_view_str.ui'
#
# Created: Thu Jul 02 09:56:40 2015
#      by: PyQt4 UI code generator 4.11.1
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

class Ui_frmViewSTR(object):
    def setupUi(self, frmViewSTR):
        frmViewSTR.setObjectName(_fromUtf8("frmViewSTR"))
        frmViewSTR.resize(916, 600)
        self.gridLayout_3 = QtGui.QGridLayout(frmViewSTR)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.groupBox = QtGui.QGroupBox(frmViewSTR)
        self.groupBox.setMaximumSize(QtCore.QSize(400, 1000))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.vlSearchEntity = QtGui.QVBoxLayout()
        self.vlSearchEntity.setObjectName(_fromUtf8("vlSearchEntity"))
        self.gridLayout_2.addLayout(self.vlSearchEntity, 0, 0, 1, 2)
        self.tbSTREntity = QtGui.QTabWidget(self.groupBox)
        self.tbSTREntity.setMinimumSize(QtCore.QSize(0, 0))
        self.tbSTREntity.setObjectName(_fromUtf8("tbSTREntity"))
        self.gridLayout_2.addWidget(self.tbSTREntity, 1, 0, 1, 2)
        self.btnSearch = QtGui.QPushButton(self.groupBox)
        self.btnSearch.setMinimumSize(QtCore.QSize(0, 30))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/stdm/images/icons/search.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnSearch.setIcon(icon)
        self.btnSearch.setObjectName(_fromUtf8("btnSearch"))
        self.gridLayout_2.addWidget(self.btnSearch, 2, 0, 1, 1)
        self.btnClearSearch = QtGui.QPushButton(self.groupBox)
        self.btnClearSearch.setMinimumSize(QtCore.QSize(0, 30))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/stdm/images/icons/reset.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnClearSearch.setIcon(icon1)
        self.btnClearSearch.setObjectName(_fromUtf8("btnClearSearch"))
        self.gridLayout_2.addWidget(self.btnClearSearch, 2, 1, 1, 1)
        self.gridLayout_3.addWidget(self.groupBox, 0, 0, 1, 1)
        self.groupBox_3 = QtGui.QGroupBox(frmViewSTR)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_3.sizePolicy().hasHeightForWidth())
        self.groupBox_3.setSizePolicy(sizePolicy)
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox_3)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tbPropertyPreview = PropertyPreviewWidget(self.groupBox_3)
        self.tbPropertyPreview.setObjectName(_fromUtf8("tbPropertyPreview"))
        self.gridLayout.addWidget(self.tbPropertyPreview, 0, 0, 1, 1)
        self.gridLayout_3.addWidget(self.groupBox_3, 0, 1, 2, 1)
        self.groupBox_2 = QtGui.QGroupBox(frmViewSTR)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.groupBox_2.setMinimumSize(QtCore.QSize(300, 350))
        self.groupBox_2.setMaximumSize(QtCore.QSize(400, 16777215))
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox_2)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label_4 = QtGui.QLabel(self.groupBox_2)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.verticalLayout.addWidget(self.label_4)
        self.tvSTRResults = QtGui.QTreeView(self.groupBox_2)
        self.tvSTRResults.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.tvSTRResults.setAlternatingRowColors(True)
        self.tvSTRResults.setRootIsDecorated(True)
        self.tvSTRResults.setObjectName(_fromUtf8("tvSTRResults"))
        self.tvSTRResults.header().setCascadingSectionResizes(False)
        self.tvSTRResults.header().setDefaultSectionSize(0)
        self.verticalLayout.addWidget(self.tvSTRResults)
        self.gridLayout_3.addWidget(self.groupBox_2, 1, 0, 2, 1)
        self.groupBox_4 = QtGui.QGroupBox(frmViewSTR)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_4.sizePolicy().hasHeightForWidth())
        self.groupBox_4.setSizePolicy(sizePolicy)
        self.groupBox_4.setMinimumSize(QtCore.QSize(0, 100))
        self.groupBox_4.setMaximumSize(QtCore.QSize(16777215, 1677215))
        self.groupBox_4.setObjectName(_fromUtf8("groupBox_4"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox_4)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.tbSupportingDocs = QtGui.QTabWidget(self.groupBox_4)
        self.tbSupportingDocs.setMaximumSize(QtCore.QSize(16777215, 150))
        self.tbSupportingDocs.setObjectName(_fromUtf8("tbSupportingDocs"))
        self.verticalLayout_2.addWidget(self.tbSupportingDocs)
        self.gridLayout_3.addWidget(self.groupBox_4, 2, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(frmViewSTR)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_3.addWidget(self.buttonBox, 3, 0, 1, 2)

        self.retranslateUi(frmViewSTR)
        self.tbSTREntity.setCurrentIndex(-1)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), frmViewSTR.close)
        QtCore.QMetaObject.connectSlotsByName(frmViewSTR)

    def retranslateUi(self, frmViewSTR):
        frmViewSTR.setWindowTitle(_translate("frmViewSTR", "Social Tenure Relationship View", None))
        self.groupBox.setTitle(_translate("frmViewSTR", "Search By:", None))
        self.btnSearch.setText(_translate("frmViewSTR", "Search", None))
        self.btnClearSearch.setText(_translate("frmViewSTR", "Clear Results", None))
        self.groupBox_3.setTitle(_translate("frmViewSTR", "Spatial unit Preview:", None))
        self.groupBox_2.setTitle(_translate("frmViewSTR", "Search Results:", None))
        self.label_4.setText(_translate("frmViewSTR", "Right click on an item for more details", None))
        self.groupBox_4.setTitle(_translate("frmViewSTR", "Supporting Documents:", None))

from propertyPreview import PropertyPreviewWidget
import resources_rc
