# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_upgrade_paths.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
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

class Ui_UpgradePaths(object):
    def setupUi(self, UpgradePaths):
        UpgradePaths.setObjectName(_fromUtf8("UpgradePaths"))
        UpgradePaths.resize(484, 324)
        self.verticalLayout = QtGui.QVBoxLayout(UpgradePaths)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.notification_bar = QtGui.QVBoxLayout()
        self.notification_bar.setObjectName(_fromUtf8("notification_bar"))
        self.verticalLayout.addLayout(self.notification_bar)
        self.label = QtGui.QLabel(UpgradePaths)
        self.label.setWordWrap(True)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.gridLayout_3 = QtGui.QGridLayout()
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.label_6 = QtGui.QLabel(UpgradePaths)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout_3.addWidget(self.label_6, 0, 0, 1, 1)
        self.text_document = QtGui.QLineEdit(UpgradePaths)
        self.text_document.setMinimumSize(QtCore.QSize(0, 30))
        self.text_document.setMaxLength(500)
        self.text_document.setReadOnly(True)
        self.text_document.setObjectName(_fromUtf8("text_document"))
        self.gridLayout_3.addWidget(self.text_document, 0, 1, 1, 1)
        self.btn_supporting_docs = QtGui.QToolButton(UpgradePaths)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/stdm/images/icons/open_file.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_supporting_docs.setIcon(icon)
        self.btn_supporting_docs.setIconSize(QtCore.QSize(24, 24))
        self.btn_supporting_docs.setObjectName(_fromUtf8("btn_supporting_docs"))
        self.gridLayout_3.addWidget(self.btn_supporting_docs, 0, 2, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_3)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.text_template = QtGui.QLineEdit(UpgradePaths)
        self.text_template.setMinimumSize(QtCore.QSize(0, 30))
        self.text_template.setMaxLength(500)
        self.text_template.setReadOnly(True)
        self.text_template.setObjectName(_fromUtf8("text_template"))
        self.gridLayout.addWidget(self.text_template, 0, 1, 1, 1)
        self.btn_template = QtGui.QToolButton(UpgradePaths)
        self.btn_template.setIcon(icon)
        self.btn_template.setIconSize(QtCore.QSize(24, 24))
        self.btn_template.setObjectName(_fromUtf8("btn_template"))
        self.gridLayout.addWidget(self.btn_template, 0, 2, 1, 1)
        self.label_9 = QtGui.QLabel(UpgradePaths)
        self.label_9.setMinimumSize(QtCore.QSize(165, 0))
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.gridLayout.addWidget(self.label_9, 0, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label_10 = QtGui.QLabel(UpgradePaths)
        self.label_10.setMinimumSize(QtCore.QSize(165, 0))
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.gridLayout_2.addWidget(self.label_10, 0, 0, 1, 1)
        self.text_output = QtGui.QLineEdit(UpgradePaths)
        self.text_output.setMinimumSize(QtCore.QSize(0, 30))
        self.text_output.setMaxLength(500)
        self.text_output.setReadOnly(True)
        self.text_output.setObjectName(_fromUtf8("text_output"))
        self.gridLayout_2.addWidget(self.text_output, 0, 1, 1, 1)
        self.btn_output = QtGui.QToolButton(UpgradePaths)
        self.btn_output.setIcon(icon)
        self.btn_output.setIconSize(QtCore.QSize(24, 24))
        self.btn_output.setObjectName(_fromUtf8("btn_output"))
        self.gridLayout_2.addWidget(self.btn_output, 0, 2, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_2)
        self.buttonBox = QtGui.QDialogButtonBox(UpgradePaths)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Apply)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(UpgradePaths)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), UpgradePaths.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), UpgradePaths.reject)
        QtCore.QMetaObject.connectSlotsByName(UpgradePaths)

    def retranslateUi(self, UpgradePaths):
        UpgradePaths.setWindowTitle(_translate("UpgradePaths", "Directory Settings", None))
        self.label.setText(_translate("UpgradePaths", "We couldn\'t find the required STDM folder setting in the system. <br>Please, select the template and supporting document folders below. <br><br>The supporting documents folder is the folder that contains the 2020 folder.  <br>The template folder is the folder that contains your document templates.  <br>The output folder is the folder where you save the generated documents. ", None))
        self.label_6.setText(_translate("UpgradePaths", "Supporting documents folder", None))
        self.btn_supporting_docs.setToolTip(_translate("UpgradePaths", "Choose supporting documents directory", None))
        self.btn_supporting_docs.setText(_translate("UpgradePaths", "...", None))
        self.btn_template.setToolTip(_translate("UpgradePaths", "Choose templates directory", None))
        self.btn_template.setText(_translate("UpgradePaths", "...", None))
        self.label_9.setText(_translate("UpgradePaths", "Template folder", None))
        self.label_10.setText(_translate("UpgradePaths", "Output folder", None))
        self.btn_output.setToolTip(_translate("UpgradePaths", "Choose output directory", None))
        self.btn_output.setText(_translate("UpgradePaths", "...", None))

from stdm import resources_rc
