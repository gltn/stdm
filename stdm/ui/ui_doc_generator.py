# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_doc_generator.ui'
#
# Created: Fri Jun 21 06:32:09 2019
#      by: PyQt4 UI code generator 4.11.3
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

class Ui_DocumentGeneratorDialog(object):
    def setupUi(self, DocumentGeneratorDialog):
        DocumentGeneratorDialog.setObjectName(_fromUtf8("DocumentGeneratorDialog"))
        DocumentGeneratorDialog.resize(531, 684)
        self.gridLayout = QtGui.QGridLayout(DocumentGeneratorDialog)
        self.gridLayout.setVerticalSpacing(9)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.groupBox_2 = QtGui.QGroupBox(DocumentGeneratorDialog)
        self.groupBox_2.setMinimumSize(QtCore.QSize(0, 80))
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.gridLayout_4 = QtGui.QGridLayout()
        self.gridLayout_4.setContentsMargins(-1, -1, -1, 0)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.cboImageType = QtGui.QComboBox(self.groupBox_2)
        self.cboImageType.setMinimumSize(QtCore.QSize(0, 25))
        self.cboImageType.setObjectName(_fromUtf8("cboImageType"))
        self.gridLayout_4.addWidget(self.cboImageType, 1, 1, 1, 1)
        self.rbExpImage = QtGui.QRadioButton(self.groupBox_2)
        self.rbExpImage.setChecked(False)
        self.rbExpImage.setObjectName(_fromUtf8("rbExpImage"))
        self.gridLayout_4.addWidget(self.rbExpImage, 1, 0, 1, 1)
        self.rbExpPDF = QtGui.QRadioButton(self.groupBox_2)
        self.rbExpPDF.setChecked(True)
        self.rbExpPDF.setObjectName(_fromUtf8("rbExpPDF"))
        self.gridLayout_4.addWidget(self.rbExpPDF, 0, 0, 1, 1)
        self.horizontalLayout_2.addLayout(self.gridLayout_4)
        self.gridLayout.addWidget(self.groupBox_2, 5, 0, 1, 1)
        self.gbDocNaming = QtGui.QGroupBox(DocumentGeneratorDialog)
        self.gbDocNaming.setEnabled(False)
        self.gbDocNaming.setMaximumSize(QtCore.QSize(16777215, 180))
        self.gbDocNaming.setObjectName(_fromUtf8("gbDocNaming"))
        self.gridLayout_3 = QtGui.QGridLayout(self.gbDocNaming)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.lstDocNaming = ModelAtrributesView(self.gbDocNaming)
        self.lstDocNaming.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.lstDocNaming.setObjectName(_fromUtf8("lstDocNaming"))
        self.gridLayout_3.addWidget(self.lstDocNaming, 1, 0, 1, 1)
        self.label_2 = QtGui.QLabel(self.gbDocNaming)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_3.addWidget(self.label_2, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.gbDocNaming, 8, 0, 1, 1)
        self.tabWidget = QtGui.QTabWidget(DocumentGeneratorDialog)
        self.tabWidget.setMinimumSize(QtCore.QSize(0, 140))
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.gridLayout.addWidget(self.tabWidget, 2, 0, 1, 1)
        self.chk_template_datasource = QtGui.QCheckBox(DocumentGeneratorDialog)
        self.chk_template_datasource.setObjectName(_fromUtf8("chk_template_datasource"))
        self.gridLayout.addWidget(self.chk_template_datasource, 3, 0, 1, 1)
        self.vlNotification = QtGui.QVBoxLayout()
        self.vlNotification.setObjectName(_fromUtf8("vlNotification"))
        self.gridLayout.addLayout(self.vlNotification, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(DocumentGeneratorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 10, 0, 1, 1)
        self.label = QtGui.QLabel(DocumentGeneratorDialog)
        self.label.setMaximumSize(QtCore.QSize(16777215, 25))
        self.label.setWordWrap(True)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.groupBox = QtGui.QGroupBox(DocumentGeneratorDialog)
        self.groupBox.setMinimumSize(QtCore.QSize(0, 0))
        self.groupBox.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.btnSelectTemplate = QtGui.QPushButton(self.groupBox)
        self.btnSelectTemplate.setMinimumSize(QtCore.QSize(0, 30))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/stdm/images/icons/document.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnSelectTemplate.setIcon(icon)
        self.btnSelectTemplate.setObjectName(_fromUtf8("btnSelectTemplate"))
        self.gridLayout_2.addWidget(self.btnSelectTemplate, 0, 0, 1, 2)
        self.lblTemplateName = QtGui.QLabel(self.groupBox)
        self.lblTemplateName.setMinimumSize(QtCore.QSize(0, 25))
        self.lblTemplateName.setFrameShape(QtGui.QFrame.WinPanel)
        self.lblTemplateName.setFrameShadow(QtGui.QFrame.Sunken)
        self.lblTemplateName.setText(_fromUtf8(""))
        self.lblTemplateName.setTextFormat(QtCore.Qt.PlainText)
        self.lblTemplateName.setObjectName(_fromUtf8("lblTemplateName"))
        self.gridLayout_2.addWidget(self.lblTemplateName, 0, 2, 1, 2)
        self.gridLayout.addWidget(self.groupBox, 4, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.chkUseOutputFolder = QtGui.QCheckBox(DocumentGeneratorDialog)
        self.chkUseOutputFolder.setObjectName(_fromUtf8("chkUseOutputFolder"))
        self.horizontalLayout.addWidget(self.chkUseOutputFolder)
        spacerItem = QtGui.QSpacerItem(150, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.btnShowOutputFolder = QtGui.QPushButton(DocumentGeneratorDialog)
        self.btnShowOutputFolder.setObjectName(_fromUtf8("btnShowOutputFolder"))
        self.horizontalLayout.addWidget(self.btnShowOutputFolder)
        self.gridLayout.addLayout(self.horizontalLayout, 6, 0, 1, 1)

        self.retranslateUi(DocumentGeneratorDialog)
        self.tabWidget.setCurrentIndex(-1)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), DocumentGeneratorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(DocumentGeneratorDialog)

    def retranslateUi(self, DocumentGeneratorDialog):
        DocumentGeneratorDialog.setWindowTitle(_translate("DocumentGeneratorDialog", "Document Generator", None))
        self.groupBox_2.setTitle(_translate("DocumentGeneratorDialog", "Output Type:", None))
        self.rbExpImage.setText(_translate("DocumentGeneratorDialog", "Export as Image", None))
        self.rbExpPDF.setText(_translate("DocumentGeneratorDialog", "Export as PDF", None))
        self.gbDocNaming.setTitle(_translate("DocumentGeneratorDialog", "Output Document Naming:", None))
        self.label_2.setText(_translate("DocumentGeneratorDialog", "Select the fields whose values will be used to name the output document files.", None))
        self.chk_template_datasource.setText(_translate("DocumentGeneratorDialog", "Disable record selection", None))
        self.label.setText(_translate("DocumentGeneratorDialog", "<html><head/><body><p>Click on the plus button below to add a record from the database.</p></body></html>", None))
        self.groupBox.setTitle(_translate("DocumentGeneratorDialog", "Template:", None))
        self.btnSelectTemplate.setText(_translate("DocumentGeneratorDialog", "Select document template", None))
        self.chkUseOutputFolder.setText(_translate("DocumentGeneratorDialog", "Save to output folder", None))
        self.btnShowOutputFolder.setText(_translate("DocumentGeneratorDialog", "Open output folder...", None))

from customcontrols import ModelAtrributesView
