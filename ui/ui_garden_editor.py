# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_garden_editor.ui'
#
# Created: Tue Apr 15 09:24:25 2014
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

class Ui_frmGardenEditor(object):
    def setupUi(self, frmGardenEditor):
        frmGardenEditor.setObjectName(_fromUtf8("frmGardenEditor"))
        frmGardenEditor.resize(370, 520)
        self.gridLayout = QtGui.QGridLayout(frmGardenEditor)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.vlNotification = QtGui.QVBoxLayout()
        self.vlNotification.setObjectName(_fromUtf8("vlNotification"))
        self.gridLayout.addLayout(self.vlNotification, 0, 0, 1, 2)
        self.btnSelectAdminUnit = QtGui.QPushButton(frmGardenEditor)
        self.btnSelectAdminUnit.setMinimumSize(QtCore.QSize(0, 30))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/stdm/images/icons/manage_admin_units.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnSelectAdminUnit.setIcon(icon)
        self.btnSelectAdminUnit.setObjectName(_fromUtf8("btnSelectAdminUnit"))
        self.gridLayout.addWidget(self.btnSelectAdminUnit, 1, 0, 1, 2)
        self.label = QtGui.QLabel(frmGardenEditor)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 2, 0, 1, 1)
        self.txtGardenIdentifier = QtGui.QLineEdit(frmGardenEditor)
        self.txtGardenIdentifier.setMinimumSize(QtCore.QSize(0, 30))
        self.txtGardenIdentifier.setMaxLength(30)
        self.txtGardenIdentifier.setReadOnly(True)
        self.txtGardenIdentifier.setObjectName(_fromUtf8("txtGardenIdentifier"))
        self.gridLayout.addWidget(self.txtGardenIdentifier, 2, 1, 1, 1)
        self.label_2 = QtGui.QLabel(frmGardenEditor)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 1)
        self.sbAcreage = QtGui.QDoubleSpinBox(frmGardenEditor)
        self.sbAcreage.setMinimumSize(QtCore.QSize(0, 30))
        self.sbAcreage.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.sbAcreage.setMaximum(100000.0)
        self.sbAcreage.setObjectName(_fromUtf8("sbAcreage"))
        self.gridLayout.addWidget(self.sbAcreage, 3, 1, 1, 1)
        self.label_3 = QtGui.QLabel(frmGardenEditor)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 4, 0, 1, 1)
        self.sbAverageHarvest = QtGui.QDoubleSpinBox(frmGardenEditor)
        self.sbAverageHarvest.setMinimumSize(QtCore.QSize(0, 30))
        self.sbAverageHarvest.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.sbAverageHarvest.setMaximum(1000000.0)
        self.sbAverageHarvest.setObjectName(_fromUtf8("sbAverageHarvest"))
        self.gridLayout.addWidget(self.sbAverageHarvest, 4, 1, 1, 1)
        self.label_4 = QtGui.QLabel(frmGardenEditor)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 5, 0, 1, 1)
        self.sbMonthlyEarning = QtGui.QSpinBox(frmGardenEditor)
        self.sbMonthlyEarning.setMinimumSize(QtCore.QSize(0, 30))
        self.sbMonthlyEarning.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.sbMonthlyEarning.setMaximum(100000000)
        self.sbMonthlyEarning.setObjectName(_fromUtf8("sbMonthlyEarning"))
        self.gridLayout.addWidget(self.sbMonthlyEarning, 5, 1, 1, 1)
        self.label_6 = QtGui.QLabel(frmGardenEditor)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout.addWidget(self.label_6, 6, 0, 1, 1)
        self.sbMonthlyLabor = QtGui.QSpinBox(frmGardenEditor)
        self.sbMonthlyLabor.setMinimumSize(QtCore.QSize(0, 30))
        self.sbMonthlyLabor.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.sbMonthlyLabor.setMaximum(100000000)
        self.sbMonthlyLabor.setObjectName(_fromUtf8("sbMonthlyLabor"))
        self.gridLayout.addWidget(self.sbMonthlyLabor, 6, 1, 1, 1)
        self.label_5 = QtGui.QLabel(frmGardenEditor)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout.addWidget(self.label_5, 7, 0, 1, 1)
        self.dtPlantingYear = QtGui.QDateEdit(frmGardenEditor)
        self.dtPlantingYear.setMinimumSize(QtCore.QSize(0, 30))
        self.dtPlantingYear.setObjectName(_fromUtf8("dtPlantingYear"))
        self.gridLayout.addWidget(self.dtPlantingYear, 7, 1, 1, 1)
        self.tbRelations = QtGui.QTabWidget(frmGardenEditor)
        self.tbRelations.setObjectName(_fromUtf8("tbRelations"))
        self.fkmFoodCrops = ForeignKeyMapper()
        self.fkmFoodCrops.setObjectName(_fromUtf8("fkmFoodCrops"))
        self.tbRelations.addTab(self.fkmFoodCrops, _fromUtf8(""))
        self.tab = ForeignKeyMapper()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.tbRelations.addTab(self.tab, _fromUtf8(""))
        self.gridLayout.addWidget(self.tbRelations, 8, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(frmGardenEditor)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 9, 0, 1, 2)

        self.retranslateUi(frmGardenEditor)
        self.tbRelations.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(frmGardenEditor)

    def retranslateUi(self, frmGardenEditor):
        frmGardenEditor.setWindowTitle(_translate("frmGardenEditor", "Garden Editor", None))
        self.btnSelectAdminUnit.setText(_translate("frmGardenEditor", "Select Administrative Unit", None))
        self.label.setText(_translate("frmGardenEditor", "Identifier (auto-generated)", None))
        self.label_2.setText(_translate("frmGardenEditor", "Acreage", None))
        self.label_3.setText(_translate("frmGardenEditor", "Average Harvest (kg)", None))
        self.sbAverageHarvest.setSuffix(_translate("frmGardenEditor", "kg", None))
        self.label_4.setText(_translate("frmGardenEditor", "Monthly Earning (UGX)", None))
        self.sbMonthlyEarning.setPrefix(_translate("frmGardenEditor", "UGX ", None))
        self.label_6.setText(_translate("frmGardenEditor", "Monthly Labour Cost (UGX)", None))
        self.sbMonthlyLabor.setPrefix(_translate("frmGardenEditor", "UGX ", None))
        self.label_5.setText(_translate("frmGardenEditor", "Planting Year", None))
        self.dtPlantingYear.setDisplayFormat(_translate("frmGardenEditor", "yyyy", None))
        self.tbRelations.setTabText(self.tbRelations.indexOf(self.fkmFoodCrops), _translate("frmGardenEditor", "Food Crops", None))
        self.tbRelations.setTabText(self.tbRelations.indexOf(self.tab), _translate("frmGardenEditor", "Survey Points", None))

from .foreign_key_mapper import ForeignKeyMapper
import resources_rc
