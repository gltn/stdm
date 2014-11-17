# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_foreign_key_mapper.ui'
#
# Created: Sat Mar 08 13:50:34 2014
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

class Ui_frmFKMapper(object):
    def setupUi(self, frmFKMapper):
        frmFKMapper.setObjectName(_fromUtf8("frmFKMapper"))
        frmFKMapper.resize(393, 320)
        frmFKMapper.setWindowTitle(_fromUtf8(""))
        self.tbFKEntity = QtGui.QTableView(frmFKMapper)
        self.tbFKEntity.setGeometry(QtCore.QRect(10, 60, 371, 251))
        self.tbFKEntity.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.tbFKEntity.setAlternatingRowColors(True)
        self.tbFKEntity.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tbFKEntity.setObjectName(_fromUtf8("tbFKEntity"))

        self.retranslateUi(frmFKMapper)
        QtCore.QMetaObject.connectSlotsByName(frmFKMapper)

    def retranslateUi(self, frmFKMapper):
        pass

