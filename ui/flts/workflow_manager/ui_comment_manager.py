# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:/Users/nkoec/.qgis2/python/plugins/stdm/ui/flts/workflow_manager/ui_comment_manager.ui'
#
# Created: Thu Sep 26 13:29:54 2019
#      by: PyQt4 UI code generator 4.10.2
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

class Ui_CommentManagerWidget(object):
    def setupUi(self, CommentManagerWidget):
        CommentManagerWidget.setObjectName(_fromUtf8("CommentManagerWidget"))
        CommentManagerWidget.resize(979, 596)
        self.horizontalLayout_3 = QtGui.QHBoxLayout(CommentManagerWidget)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.newCommetGroupBox = QtGui.QGroupBox(CommentManagerWidget)
        self.newCommetGroupBox.setFlat(False)
        self.newCommetGroupBox.setCheckable(False)
        self.newCommetGroupBox.setObjectName(_fromUtf8("newCommetGroupBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.newCommetGroupBox)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.newCommentTextEdit = QtGui.QTextEdit(self.newCommetGroupBox)
        self.newCommentTextEdit.setObjectName(_fromUtf8("newCommentTextEdit"))
        self.verticalLayout.addWidget(self.newCommentTextEdit)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.submitButton = QtGui.QPushButton(self.newCommetGroupBox)
        self.submitButton.setObjectName(_fromUtf8("submitButton"))
        self.horizontalLayout.addWidget(self.submitButton)
        spacerItem = QtGui.QSpacerItem(128, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2.addWidget(self.newCommetGroupBox)
        self.oldCommetGroupBox = QtGui.QGroupBox(CommentManagerWidget)
        self.oldCommetGroupBox.setObjectName(_fromUtf8("oldCommetGroupBox"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.oldCommetGroupBox)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.oldCommentTextEdit = QtGui.QTextEdit(self.oldCommetGroupBox)
        self.oldCommentTextEdit.setObjectName(_fromUtf8("oldCommentTextEdit"))
        self.verticalLayout_2.addWidget(self.oldCommentTextEdit)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_2.addWidget(self.oldCommetGroupBox)
        self.horizontalLayout_2.setStretch(0, 4)
        self.horizontalLayout_2.setStretch(1, 6)
        self.horizontalLayout_3.addLayout(self.horizontalLayout_2)

        self.retranslateUi(CommentManagerWidget)
        QtCore.QMetaObject.connectSlotsByName(CommentManagerWidget)

    def retranslateUi(self, CommentManagerWidget):
        CommentManagerWidget.setWindowTitle(_translate("CommentManagerWidget", "Form", None))
        self.newCommetGroupBox.setTitle(_translate("CommentManagerWidget", "Leave a Comment", None))
        self.submitButton.setText(_translate("CommentManagerWidget", "Submit Comment", None))
        self.oldCommetGroupBox.setTitle(_translate("CommentManagerWidget", "Review Comments", None))

