# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_options.ui'
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

class Ui_DlgOptions(object):
    def setupUi(self, DlgOptions):
        DlgOptions.setObjectName(_fromUtf8("DlgOptions"))
        DlgOptions.resize(626, 606)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(DlgOptions.sizePolicy().hasHeightForWidth())
        DlgOptions.setSizePolicy(sizePolicy)
        self.verticalLayout = QtGui.QVBoxLayout(DlgOptions)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.vlNotification = QtGui.QVBoxLayout()
        self.vlNotification.setObjectName(_fromUtf8("vlNotification"))
        self.verticalLayout.addLayout(self.vlNotification)
        self.scrollArea = QtGui.QScrollArea(DlgOptions)
        self.scrollArea.setFrameShape(QtGui.QFrame.NoFrame)
        self.scrollArea.setFrameShadow(QtGui.QFrame.Sunken)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 608, 551))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.gridLayout_5 = QtGui.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.chk_logging = QtGui.QCheckBox(self.scrollAreaWidgetContents)
        self.chk_logging.setObjectName(_fromUtf8("chk_logging"))
        self.gridLayout_5.addWidget(self.chk_logging, 8, 0, 1, 1)
        self.groupBox_3 = QtGui.QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_3.setMaximumSize(QtCore.QSize(16777215, 100))
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.gridLayout_4 = QtGui.QGridLayout(self.groupBox_3)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.btn_template_folder = QtGui.QToolButton(self.groupBox_3)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/stdm/images/icons/flts_scheme_docs_dir.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_template_folder.setIcon(icon)
        self.btn_template_folder.setIconSize(QtCore.QSize(24, 24))
        self.btn_template_folder.setObjectName(_fromUtf8("btn_template_folder"))
        self.gridLayout_4.addWidget(self.btn_template_folder, 0, 2, 1, 1)
        self.label_8 = QtGui.QLabel(self.groupBox_3)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.gridLayout_4.addWidget(self.label_8, 1, 0, 1, 1)
        self.txt_template_dir = QtGui.QLineEdit(self.groupBox_3)
        self.txt_template_dir.setMinimumSize(QtCore.QSize(0, 30))
        self.txt_template_dir.setMaxLength(500)
        self.txt_template_dir.setReadOnly(True)
        self.txt_template_dir.setObjectName(_fromUtf8("txt_template_dir"))
        self.gridLayout_4.addWidget(self.txt_template_dir, 0, 1, 1, 1)
        self.label_7 = QtGui.QLabel(self.groupBox_3)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout_4.addWidget(self.label_7, 0, 0, 1, 1)
        self.txt_output_dir = QtGui.QLineEdit(self.groupBox_3)
        self.txt_output_dir.setMinimumSize(QtCore.QSize(0, 30))
        self.txt_output_dir.setMaxLength(500)
        self.txt_output_dir.setReadOnly(True)
        self.txt_output_dir.setObjectName(_fromUtf8("txt_output_dir"))
        self.gridLayout_4.addWidget(self.txt_output_dir, 1, 1, 1, 1)
        self.btn_composer_out_folder = QtGui.QToolButton(self.groupBox_3)
        self.btn_composer_out_folder.setIcon(icon)
        self.btn_composer_out_folder.setIconSize(QtCore.QSize(24, 24))
        self.btn_composer_out_folder.setObjectName(_fromUtf8("btn_composer_out_folder"))
        self.gridLayout_4.addWidget(self.btn_composer_out_folder, 1, 2, 1, 1)
        self.gridLayout_5.addWidget(self.groupBox_3, 6, 0, 1, 3)
        self.gridLayout_7 = QtGui.QGridLayout()
        self.gridLayout_7.setObjectName(_fromUtf8("gridLayout_7"))
        self.label = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_7.addWidget(self.label, 0, 0, 1, 1)
        self.cbo_profiles = QtGui.QComboBox(self.scrollAreaWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbo_profiles.sizePolicy().hasHeightForWidth())
        self.cbo_profiles.setSizePolicy(sizePolicy)
        self.cbo_profiles.setMinimumSize(QtCore.QSize(0, 30))
        self.cbo_profiles.setObjectName(_fromUtf8("cbo_profiles"))
        self.gridLayout_7.addWidget(self.cbo_profiles, 0, 1, 1, 1)
        self.gridLayout_5.addLayout(self.gridLayout_7, 0, 0, 1, 2)
        self.groupBox = QtGui.QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_3 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.label_5 = QtGui.QLabel(self.groupBox)
        self.label_5.setWordWrap(True)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout_3.addWidget(self.label_5, 0, 0, 1, 3)
        self.frame = QtGui.QFrame(self.groupBox)
        self.frame.setFrameShape(QtGui.QFrame.NoFrame)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.gridLayout_2 = QtGui.QGridLayout(self.frame)
        self.gridLayout_2.setMargin(0)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setContentsMargins(-1, -1, 6, -1)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_3 = QtGui.QLabel(self.frame)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)
        self.txtHost = QtGui.QLineEdit(self.frame)
        self.txtHost.setMinimumSize(QtCore.QSize(0, 30))
        self.txtHost.setMaxLength(200)
        self.txtHost.setObjectName(_fromUtf8("txtHost"))
        self.gridLayout.addWidget(self.txtHost, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.frame)
        self.label_2.setMinimumSize(QtCore.QSize(70, 0))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.cbo_pg_connections = QtGui.QComboBox(self.frame)
        self.cbo_pg_connections.setEnabled(False)
        self.cbo_pg_connections.setMinimumSize(QtCore.QSize(0, 30))
        self.cbo_pg_connections.setObjectName(_fromUtf8("cbo_pg_connections"))
        self.gridLayout.addWidget(self.cbo_pg_connections, 3, 1, 1, 1)
        self.txtDatabase = QtGui.QLineEdit(self.frame)
        self.txtDatabase.setMinimumSize(QtCore.QSize(0, 30))
        self.txtDatabase.setMaxLength(100)
        self.txtDatabase.setObjectName(_fromUtf8("txtDatabase"))
        self.gridLayout.addWidget(self.txtDatabase, 2, 1, 1, 1)
        self.chk_pg_connections = QtGui.QCheckBox(self.frame)
        self.chk_pg_connections.setObjectName(_fromUtf8("chk_pg_connections"))
        self.gridLayout.addWidget(self.chk_pg_connections, 3, 0, 1, 1)
        self.label_4 = QtGui.QLabel(self.frame)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 1)
        self.txtPort = QtGui.QLineEdit(self.frame)
        self.txtPort.setMinimumSize(QtCore.QSize(0, 30))
        self.txtPort.setMaxLength(6)
        self.txtPort.setEchoMode(QtGui.QLineEdit.Normal)
        self.txtPort.setObjectName(_fromUtf8("txtPort"))
        self.gridLayout.addWidget(self.txtPort, 1, 1, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 4, 1)
        spacerItem = QtGui.QSpacerItem(20, 38, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 0, 1, 1, 1)
        self.btn_db_conn_clear = QtGui.QPushButton(self.frame)
        self.btn_db_conn_clear.setMinimumSize(QtCore.QSize(0, 30))
        self.btn_db_conn_clear.setObjectName(_fromUtf8("btn_db_conn_clear"))
        self.gridLayout_2.addWidget(self.btn_db_conn_clear, 1, 1, 1, 1)
        self.btn_test_db_connection = QtGui.QPushButton(self.frame)
        self.btn_test_db_connection.setMinimumSize(QtCore.QSize(0, 30))
        self.btn_test_db_connection.setObjectName(_fromUtf8("btn_test_db_connection"))
        self.gridLayout_2.addWidget(self.btn_test_db_connection, 2, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem1, 3, 1, 1, 1)
        self.gridLayout_3.addWidget(self.frame, 1, 0, 2, 3)
        self.gridLayout_5.addWidget(self.groupBox, 3, 0, 1, 3)
        self.groupBox_2 = QtGui.QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout_6 = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout_6.setObjectName(_fromUtf8("gridLayout_6"))
        self.label_6 = QtGui.QLabel(self.groupBox_2)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout_6.addWidget(self.label_6, 0, 0, 1, 1)
        self.txt_atom_pub_url = QtGui.QLineEdit(self.groupBox_2)
        self.txt_atom_pub_url.setMinimumSize(QtCore.QSize(0, 30))
        self.txt_atom_pub_url.setMaxLength(1000)
        self.txt_atom_pub_url.setObjectName(_fromUtf8("txt_atom_pub_url"))
        self.gridLayout_6.addWidget(self.txt_atom_pub_url, 0, 1, 1, 2)
        self.label_9 = QtGui.QLabel(self.groupBox_2)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.gridLayout_6.addWidget(self.label_9, 1, 0, 1, 1)
        self.cbo_auth_config_name = QtGui.QComboBox(self.groupBox_2)
        self.cbo_auth_config_name.setMinimumSize(QtCore.QSize(0, 30))
        self.cbo_auth_config_name.setObjectName(_fromUtf8("cbo_auth_config_name"))
        self.gridLayout_6.addWidget(self.cbo_auth_config_name, 1, 1, 1, 2)
        spacerItem2 = QtGui.QSpacerItem(398, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_6.addItem(spacerItem2, 2, 0, 1, 2)
        self.btn_test_docs_repo_conn = QtGui.QPushButton(self.groupBox_2)
        self.btn_test_docs_repo_conn.setMinimumSize(QtCore.QSize(0, 30))
        self.btn_test_docs_repo_conn.setObjectName(_fromUtf8("btn_test_docs_repo_conn"))
        self.gridLayout_6.addWidget(self.btn_test_docs_repo_conn, 2, 2, 1, 1)
        self.gridLayout_5.addWidget(self.groupBox_2, 4, 0, 1, 3)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)
        self.buttonBox = QtGui.QDialogButtonBox(DlgOptions)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Apply|QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(DlgOptions)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), DlgOptions.reject)
        QtCore.QMetaObject.connectSlotsByName(DlgOptions)

    def retranslateUi(self, DlgOptions):
        DlgOptions.setWindowTitle(_translate("DlgOptions", "Options", None))
        self.chk_logging.setText(_translate("DlgOptions", "Debug logging", None))
        self.groupBox_3.setTitle(_translate("DlgOptions", "Document Composer", None))
        self.btn_template_folder.setToolTip(_translate("DlgOptions", "Choose templates directory", None))
        self.btn_template_folder.setText(_translate("DlgOptions", "...", None))
        self.label_8.setText(_translate("DlgOptions", "Output folder", None))
        self.label_7.setText(_translate("DlgOptions", "Template folder", None))
        self.btn_composer_out_folder.setToolTip(_translate("DlgOptions", "Choose output directory", None))
        self.btn_composer_out_folder.setText(_translate("DlgOptions", "...", None))
        self.label.setText(_translate("DlgOptions", "Set current profile", None))
        self.groupBox.setTitle(_translate("DlgOptions", "Database Properties", None))
        self.label_5.setText(_translate("DlgOptions", "<html><head/><body><p><span style=\" font-weight:600;\">Note:</span> Changes to the database connection properties will only take effect upon the next login</p></body></html>", None))
        self.label_3.setText(_translate("DlgOptions", "Port", None))
        self.label_2.setText(_translate("DlgOptions", "Host", None))
        self.chk_pg_connections.setText(_translate("DlgOptions", "Extract from existing connection", None))
        self.label_4.setText(_translate("DlgOptions", "Database", None))
        self.btn_db_conn_clear.setToolTip(_translate("DlgOptions", "Clear database connection properties", None))
        self.btn_db_conn_clear.setText(_translate("DlgOptions", "Clear", None))
        self.btn_test_db_connection.setToolTip(_translate("DlgOptions", "Test database connection", None))
        self.btn_test_db_connection.setText(_translate("DlgOptions", "Test connection...", None))
        self.groupBox_2.setTitle(_translate("DlgOptions", "Document Repository", None))
        self.label_6.setText(_translate("DlgOptions", "Atom pub CMIS URL", None))
        self.label_9.setText(_translate("DlgOptions", "Authentication configuration name", None))
        self.btn_test_docs_repo_conn.setText(_translate("DlgOptions", "Test connection...", None))

from stdm import resources_rc
