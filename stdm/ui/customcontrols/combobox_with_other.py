"""
/***************************************************************************
Name                 : ComboBox with other
Description          : Custom QComboBox which activates a QLineEdit control
                       for entering those items that are not in the list.
Date                 : 24/March/2014
copyright            : (C) 2014 by John Gitau
email                : gkahiu@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSize
from qgis.PyQt.QtWidgets import (
    QWidget,
    QSizePolicy,
    QVBoxLayout,
    QComboBox,
    QLineEdit,
    QApplication
)


class ComboBoxWithOther(QWidget):
    '''
    Custom QComboBox which activates a QLineEdit control
    for entering those items that are not in the list.
    '''

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        self._vboxLayout = QVBoxLayout(self)
        self._vboxLayout.setMargin(0)

        self._cboItem = QComboBox(self)
        self._cboItem.setMinimumSize(QSize(0, 30))
        self._vboxLayout.addWidget(self._cboItem)

        self._txtOther = QLineEdit(self)
        self._txtOther.setMinimumSize(QSize(0, 30))
        self._txtOther.setVisible(False)
        self._vboxLayout.addWidget(self._txtOther)

        # We are using random text here so that the custom line edit is not shown on selecting a blank item in the list.
        self._activatorText = QApplication.translate("ComboBoxWithOther", "Other")

        # Connect signals
        self._cboItem.currentIndexChanged[str].connect(self.onComboIndexChanged)

    def sizeHint(self):
        '''
        Size hint for the control.
        '''
        return QSize(190, 80)

    def minimumHeight(self):
        '''
        Minimum widget height.
        '''
        return 70

    def comboBox(self):
        '''
        Returns a reference to the combobox control.
        '''
        return self._cboItem

    def lineEdit(self):
        '''
        Returns a reference to the line edit control.
        '''
        return self._txtOther

    def activatorText(self):
        '''
        Returns the text that is used to display the line edit control that enables the user to
        enter values that are not available in the combobox list.
        '''
        return self._activatorText

    def setActivatorText(self, activatorText):
        '''
        Set the text that will be used to display the line edit control that enables the user to
        enter values that are not available in the combobox list.
        '''
        if not isinstance(activatorText, str):
            self._activatorText = str(activatorText)
        else:
            self._activatorText = activatorText

    def onComboIndexChanged(self, indexText):
        '''
        Slot raised when the current index of the combobox changes. This searches for the activator text
        and loads the line edit for entering 'Other' value.
        '''
        self._txtOther.clear()

        if indexText == self._activatorText:
            self._txtOther.setVisible(True)
        else:
            self._txtOther.setVisible(False)

    def validate(self):
        '''
        Validates the state of the control
        '''
        isValid = True
        msg = ""

        if self._cboItem.currentText() == self._activatorText and self._txtOther.text() == "":
            msg = QApplication.translate("ComboBoxWithOther", \
                                         "'{0}' text cannot be empty.".format(str(self._activatorText)))
            isValid = False

        return isValid, msg
