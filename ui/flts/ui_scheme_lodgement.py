# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_scheme_lodgement.ui'
#
# Created: Fri Aug 23 11:48:45 2019
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ldg_wzd(object):
    def setupUi(self, ldg_wzd):
        ldg_wzd.setObjectName(_fromUtf8("ldg_wzd"))
        ldg_wzd.setEnabled(True)
        ldg_wzd.resize(755, 657)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ldg_wzd.sizePolicy().hasHeightForWidth())
        ldg_wzd.setSizePolicy(sizePolicy)
        ldg_wzd.setMinimumSize(QtCore.QSize(255, 400))
        ldg_wzd.setMaximumSize(QtCore.QSize(1500, 900))
        ldg_wzd.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        ldg_wzd.setAcceptDrops(False)
        ldg_wzd.setWizardStyle(QtGui.QWizard.ModernStyle)
        ldg_wzd.setOptions(QtGui.QWizard.NoBackButtonOnStartPage)
        self.wizardPage1 = QtGui.QWizardPage()
        self.wizardPage1.setObjectName(_fromUtf8("wizardPage1"))
        self.gridLayout_2 = QtGui.QGridLayout(self.wizardPage1)
        self.gridLayout_2.setVerticalSpacing(10)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.vlNotification = QtGui.QVBoxLayout()
        self.vlNotification.setContentsMargins(-1, -1, -1, 10)
        self.vlNotification.setObjectName(_fromUtf8("vlNotification"))
        self.gridLayout_2.addLayout(self.vlNotification, 0, 0, 1, 2)
        self.cbx_region = QtGui.QComboBox(self.wizardPage1)
        self.cbx_region.setObjectName(_fromUtf8("cbx_region"))
        self.gridLayout_2.addWidget(self.cbx_region, 2, 1, 1, 1)
        self.label_desc = QtGui.QLabel(self.wizardPage1)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_desc.sizePolicy().hasHeightForWidth())
        self.label_desc.setSizePolicy(sizePolicy)
        self.label_desc.setObjectName(_fromUtf8("label_desc"))
        self.gridLayout_2.addWidget(self.label_desc, 1, 0, 1, 2)
        self.label_rel_auth_type = QtGui.QLabel(self.wizardPage1)
        self.label_rel_auth_type.setObjectName(_fromUtf8("label_rel_auth_type"))
        self.gridLayout_2.addWidget(self.label_rel_auth_type, 3, 0, 1, 1)
        self.label_region = QtGui.QLabel(self.wizardPage1)
        self.label_region.setObjectName(_fromUtf8("label_region"))
        self.gridLayout_2.addWidget(self.label_region, 2, 0, 1, 1)
        self.cbx_relv_auth = QtGui.QComboBox(self.wizardPage1)
        self.cbx_relv_auth.setObjectName(_fromUtf8("cbx_relv_auth"))
        self.gridLayout_2.addWidget(self.cbx_relv_auth, 3, 1, 1, 1)
        self.label_schm_name = QtGui.QLabel(self.wizardPage1)
        self.label_schm_name.setObjectName(_fromUtf8("label_schm_name"))
        self.gridLayout_2.addWidget(self.label_schm_name, 7, 0, 1, 1)
        self.date_apprv = QtGui.QDateEdit(self.wizardPage1)
        self.date_apprv.setMinimumDate(QtCore.QDate(2009, 9, 22))
        self.date_apprv.setCalendarPopup(True)
        self.date_apprv.setObjectName(_fromUtf8("date_apprv"))
        self.gridLayout_2.addWidget(self.date_apprv, 8, 1, 1, 1)
        self.label_rel_auth_name = QtGui.QLabel(self.wizardPage1)
        self.label_rel_auth_name.setObjectName(_fromUtf8("label_rel_auth_name"))
        self.gridLayout_2.addWidget(self.label_rel_auth_name, 4, 0, 1, 1)
        self.lnedit_twnshp = QtGui.QLineEdit(self.wizardPage1)
        self.lnedit_twnshp.setObjectName(_fromUtf8("lnedit_twnshp"))
        self.gridLayout_2.addWidget(self.lnedit_twnshp, 11, 1, 1, 1)
        self.cbx_reg_div = QtGui.QComboBox(self.wizardPage1)
        self.cbx_reg_div.setObjectName(_fromUtf8("cbx_reg_div"))
        self.gridLayout_2.addWidget(self.cbx_reg_div, 5, 1, 1, 1)
        self.label_twn_name = QtGui.QLabel(self.wizardPage1)
        self.label_twn_name.setObjectName(_fromUtf8("label_twn_name"))
        self.gridLayout_2.addWidget(self.label_twn_name, 11, 0, 1, 1)
        self.lnedit_schm_nam = QtGui.QLineEdit(self.wizardPage1)
        self.lnedit_schm_nam.setObjectName(_fromUtf8("lnedit_schm_nam"))
        self.gridLayout_2.addWidget(self.lnedit_schm_nam, 7, 1, 1, 1)
        self.label_reg_div = QtGui.QLabel(self.wizardPage1)
        self.label_reg_div.setObjectName(_fromUtf8("label_reg_div"))
        self.gridLayout_2.addWidget(self.label_reg_div, 5, 0, 1, 1)
        self.cbx_relv_auth_name = QtGui.QComboBox(self.wizardPage1)
        self.cbx_relv_auth_name.setObjectName(_fromUtf8("cbx_relv_auth_name"))
        self.gridLayout_2.addWidget(self.cbx_relv_auth_name, 4, 1, 1, 1)
        self.lnedit_schm_num = QtGui.QLineEdit(self.wizardPage1)
        self.lnedit_schm_num.setReadOnly(True)
        self.lnedit_schm_num.setObjectName(_fromUtf8("lnedit_schm_num"))
        self.gridLayout_2.addWidget(self.lnedit_schm_num, 6, 1, 1, 1)
        self.label_date_apprv = QtGui.QLabel(self.wizardPage1)
        self.label_date_apprv.setObjectName(_fromUtf8("label_date_apprv"))
        self.gridLayout_2.addWidget(self.label_date_apprv, 8, 0, 1, 1)
        self.label_schm_num = QtGui.QLabel(self.wizardPage1)
        self.label_schm_num.setObjectName(_fromUtf8("label_schm_num"))
        self.gridLayout_2.addWidget(self.label_schm_num, 6, 0, 1, 1)
        self.date_establish = QtGui.QDateEdit(self.wizardPage1)
        self.date_establish.setMinimumDate(QtCore.QDate(2019, 9, 14))
        self.date_establish.setCalendarPopup(True)
        self.date_establish.setObjectName(_fromUtf8("date_establish"))
        self.gridLayout_2.addWidget(self.date_establish, 9, 1, 1, 1)
        self.label_lro = QtGui.QLabel(self.wizardPage1)
        self.label_lro.setObjectName(_fromUtf8("label_lro"))
        self.gridLayout_2.addWidget(self.label_lro, 10, 0, 1, 1)
        self.label_blck_area = QtGui.QLabel(self.wizardPage1)
        self.label_blck_area.setObjectName(_fromUtf8("label_blck_area"))
        self.gridLayout_2.addWidget(self.label_blck_area, 12, 0, 1, 1)
        self.dbl_spinbx_block_area = QtGui.QDoubleSpinBox(self.wizardPage1)
        self.dbl_spinbx_block_area.setDecimals(4)
        self.dbl_spinbx_block_area.setMaximum(10000000.0)
        self.dbl_spinbx_block_area.setObjectName(_fromUtf8("dbl_spinbx_block_area"))
        self.gridLayout_2.addWidget(self.dbl_spinbx_block_area, 12, 1, 1, 1)
        self.label_date_establish = QtGui.QLabel(self.wizardPage1)
        self.label_date_establish.setObjectName(_fromUtf8("label_date_establish"))
        self.gridLayout_2.addWidget(self.label_date_establish, 9, 0, 1, 1)
        self.cbx_lro = QtGui.QComboBox(self.wizardPage1)
        self.cbx_lro.setObjectName(_fromUtf8("cbx_lro"))
        self.gridLayout_2.addWidget(self.cbx_lro, 10, 1, 1, 1)
        ldg_wzd.addPage(self.wizardPage1)
        self.wizardPage = QtGui.QWizardPage()
        self.wizardPage.setObjectName(_fromUtf8("wizardPage"))
        self.gridLayout = QtGui.QGridLayout(self.wizardPage)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_desc_3 = QtGui.QLabel(self.wizardPage)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_desc_3.sizePolicy().hasHeightForWidth())
        self.label_desc_3.setSizePolicy(sizePolicy)
        self.label_desc_3.setMinimumSize(QtCore.QSize(0, 15))
        self.label_desc_3.setMaximumSize(QtCore.QSize(16777215, 15))
        self.label_desc_3.setLineWidth(0)
        self.label_desc_3.setWordWrap(True)
        self.label_desc_3.setMargin(1)
        self.label_desc_3.setObjectName(_fromUtf8("label_desc_3"))
        self.gridLayout.addWidget(self.label_desc_3, 1, 0, 1, 2)
        self.btn_upload_dir = QtGui.QPushButton(self.wizardPage)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_upload_dir.sizePolicy().hasHeightForWidth())
        self.btn_upload_dir.setSizePolicy(sizePolicy)
        self.btn_upload_dir.setMinimumSize(QtCore.QSize(0, 0))
        self.btn_upload_dir.setMaximumSize(QtCore.QSize(5000, 16777215))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/stdm/images/icons/flts_scheme_docs_dir.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_upload_dir.setIcon(icon)
        self.btn_upload_dir.setIconSize(QtCore.QSize(16, 16))
        self.btn_upload_dir.setObjectName(_fromUtf8("btn_upload_dir"))
        self.gridLayout.addWidget(self.btn_upload_dir, 3, 1, 1, 1)
        self.label_upld_multi = QtGui.QLabel(self.wizardPage)
        self.label_upld_multi.setObjectName(_fromUtf8("label_upld_multi"))
        self.gridLayout.addWidget(self.label_upld_multi, 3, 0, 1, 1)
        self.vlNotification_docs = QtGui.QVBoxLayout()
        self.vlNotification_docs.setContentsMargins(-1, -1, -1, 10)
        self.vlNotification_docs.setObjectName(_fromUtf8("vlNotification_docs"))
        self.gridLayout.addLayout(self.vlNotification_docs, 0, 0, 1, 2)
        self.tbw_documents = DocumentTableWidget(self.wizardPage)
        self.tbw_documents.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.tbw_documents.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.tbw_documents.setObjectName(_fromUtf8("tbw_documents"))
        self.gridLayout.addWidget(self.tbw_documents, 2, 0, 1, 2)
        self.gp_preview_docs = QgsCollapsibleGroupBox(self.wizardPage)
        self.gp_preview_docs.setEnabled(False)
        self.gp_preview_docs.setObjectName(_fromUtf8("gp_preview_docs"))
        self.gridLayout.addWidget(self.gp_preview_docs, 4, 0, 1, 2)
        ldg_wzd.addPage(self.wizardPage)
        self.wizardPage2 = QtGui.QWizardPage()
        self.wizardPage2.setObjectName(_fromUtf8("wizardPage2"))
        self.gridLayout_3 = QtGui.QGridLayout(self.wizardPage2)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.tw_hld_prv = HoldersTableView(self.wizardPage2)
        self.tw_hld_prv.setObjectName(_fromUtf8("tw_hld_prv"))
        self.gridLayout_3.addWidget(self.tw_hld_prv, 4, 0, 1, 3)
        self.lnEdit_hld_path = QtGui.QLineEdit(self.wizardPage2)
        self.lnEdit_hld_path.setEnabled(True)
        self.lnEdit_hld_path.setObjectName(_fromUtf8("lnEdit_hld_path"))
        self.gridLayout_3.addWidget(self.lnEdit_hld_path, 2, 0, 1, 1)
        self.label_desc_2 = QtGui.QLabel(self.wizardPage2)
        self.label_desc_2.setObjectName(_fromUtf8("label_desc_2"))
        self.gridLayout_3.addWidget(self.label_desc_2, 1, 0, 1, 2)
        self.btn_brws_hld = QtGui.QPushButton(self.wizardPage2)
        self.btn_brws_hld.setText(_fromUtf8(""))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/stdm/images/icons/flts_open_file.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_brws_hld.setIcon(icon1)
        self.btn_brws_hld.setDefault(True)
        self.btn_brws_hld.setObjectName(_fromUtf8("btn_brws_hld"))
        self.gridLayout_3.addWidget(self.btn_brws_hld, 2, 1, 1, 1)
        self.vlNotification_holders = QtGui.QVBoxLayout()
        self.vlNotification_holders.setContentsMargins(-1, -1, -1, 10)
        self.vlNotification_holders.setObjectName(_fromUtf8("vlNotification_holders"))
        self.gridLayout_3.addLayout(self.vlNotification_holders, 0, 0, 1, 3)
        self.btn_reload_holders = QtGui.QPushButton(self.wizardPage2)
        self.btn_reload_holders.setText(_fromUtf8(""))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/stdm/images/icons/update.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_reload_holders.setIcon(icon2)
        self.btn_reload_holders.setObjectName(_fromUtf8("btn_reload_holders"))
        self.gridLayout_3.addWidget(self.btn_reload_holders, 2, 2, 1, 1)
        self.chk_holders_validate = QtGui.QCheckBox(self.wizardPage2)
        self.chk_holders_validate.setChecked(True)
        self.chk_holders_validate.setObjectName(_fromUtf8("chk_holders_validate"))
        self.gridLayout_3.addWidget(self.chk_holders_validate, 3, 0, 1, 1)
        ldg_wzd.addPage(self.wizardPage2)
        self.wizardPage_4 = QtGui.QWizardPage()
        self.wizardPage_4.setObjectName(_fromUtf8("wizardPage_4"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.wizardPage_4)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.label_desc_4 = QtGui.QLabel(self.wizardPage_4)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_desc_4.sizePolicy().hasHeightForWidth())
        self.label_desc_4.setSizePolicy(sizePolicy)
        self.label_desc_4.setObjectName(_fromUtf8("label_desc_4"))
        self.verticalLayout_2.addWidget(self.label_desc_4)
        self.tr_summary = SchemeSummaryWidget(self.wizardPage_4)
        self.tr_summary.setUniformRowHeights(True)
        self.tr_summary.setObjectName(_fromUtf8("tr_summary"))
        self.verticalLayout_2.addWidget(self.tr_summary)
        ldg_wzd.addPage(self.wizardPage_4)

        self.retranslateUi(ldg_wzd)
        QtCore.QMetaObject.connectSlotsByName(ldg_wzd)

    def retranslateUi(self, ldg_wzd):
        ldg_wzd.setWindowTitle(QtGui.QApplication.translate("ldg_wzd", "Lodgement of Scheme", None, QtGui.QApplication.UnicodeUTF8))
        self.label_desc.setText(QtGui.QApplication.translate("ldg_wzd", "<html><head/><body><p>Enter scheme information below. Please note the scheme number will be automatically generated</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_rel_auth_type.setText(QtGui.QApplication.translate("ldg_wzd", "Type of Relevant Authority", None, QtGui.QApplication.UnicodeUTF8))
        self.label_region.setText(QtGui.QApplication.translate("ldg_wzd", "Region", None, QtGui.QApplication.UnicodeUTF8))
        self.label_schm_name.setText(QtGui.QApplication.translate("ldg_wzd", "Scheme Name", None, QtGui.QApplication.UnicodeUTF8))
        self.label_rel_auth_name.setText(QtGui.QApplication.translate("ldg_wzd", "Name of Relevant Authority", None, QtGui.QApplication.UnicodeUTF8))
        self.label_twn_name.setText(QtGui.QApplication.translate("ldg_wzd", "Township Name", None, QtGui.QApplication.UnicodeUTF8))
        self.label_reg_div.setText(QtGui.QApplication.translate("ldg_wzd", "Registration Division", None, QtGui.QApplication.UnicodeUTF8))
        self.label_date_apprv.setText(QtGui.QApplication.translate("ldg_wzd", "Date of Approval", None, QtGui.QApplication.UnicodeUTF8))
        self.label_schm_num.setText(QtGui.QApplication.translate("ldg_wzd", "Scheme Number", None, QtGui.QApplication.UnicodeUTF8))
        self.label_lro.setText(QtGui.QApplication.translate("ldg_wzd", "Land Rights Office", None, QtGui.QApplication.UnicodeUTF8))
        self.label_blck_area.setText(QtGui.QApplication.translate("ldg_wzd", "Block Area", None, QtGui.QApplication.UnicodeUTF8))
        self.label_date_establish.setText(QtGui.QApplication.translate("ldg_wzd", "Date of Esablishment", None, QtGui.QApplication.UnicodeUTF8))
        self.wizardPage.setSubTitle(QtGui.QApplication.translate("ldg_wzd", "Upload the supporting documents for the scheme", None, QtGui.QApplication.UnicodeUTF8))
        self.label_desc_3.setText(QtGui.QApplication.translate("ldg_wzd", "<html><head/><body><p>Click the \'Browse\' link to add the individual supporting documents </p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_upload_dir.setText(QtGui.QApplication.translate("ldg_wzd", "Upload From Directory...", None, QtGui.QApplication.UnicodeUTF8))
        self.label_upld_multi.setText(QtGui.QApplication.translate("ldg_wzd", "Add multiple files from a source directory", None, QtGui.QApplication.UnicodeUTF8))
        self.gp_preview_docs.setTitle(QtGui.QApplication.translate("ldg_wzd", "Preview Documents", None, QtGui.QApplication.UnicodeUTF8))
        self.lnEdit_hld_path.setPlaceholderText(QtGui.QApplication.translate("ldg_wzd", "Path to the Holders Excel or CSV file...", None, QtGui.QApplication.UnicodeUTF8))
        self.label_desc_2.setText(QtGui.QApplication.translate("ldg_wzd", "Select the Excel or CSV file containing the holders information", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_brws_hld.setToolTip(QtGui.QApplication.translate("ldg_wzd", "Browse file", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_reload_holders.setToolTip(QtGui.QApplication.translate("ldg_wzd", "Reload file", None, QtGui.QApplication.UnicodeUTF8))
        self.chk_holders_validate.setText(QtGui.QApplication.translate("ldg_wzd", "Perform validation upon loading data", None, QtGui.QApplication.UnicodeUTF8))
        self.label_desc_4.setText(QtGui.QApplication.translate("ldg_wzd", "Confirm the scheme information.Click Back to edit the information or Finish to save.  ", None, QtGui.QApplication.UnicodeUTF8))

from stdm.ui.customcontrols.scheme_summary_widget import SchemeSummaryWidget
from stdm.ui.customcontrols.table_widget import HoldersTableView
from stdm.ui.customcontrols.documents_table_widget import DocumentTableWidget
from qgis.gui import QgsCollapsibleGroupBox
from stdm import resources_rc
