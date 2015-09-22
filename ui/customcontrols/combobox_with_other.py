"""
/***************************************************************************
Name                 : ComboBox with other
Description          : Custom QComboBox which activates a QLineEdit control
                       for entering those items that are not in the list.
Date                 : 24/March/2014
copyright            : (C) 2015 by UN-Habitat and implementing partners.
                       See the accompanying file CONTRIBUTORS.txt in the root
email                : stdm@unhabitat.org
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
from PyQt4.QtCore import QSize, SIGNAL
from PyQt4.QtGui import QWidget, QSizePolicy, QApplication, QVBoxLayout, \
    QComboBox, QLineEdit


class ComboBoxWithOther(QWidget):
    """
    Custom QComboBox which activates a QLineEdit control
    for entering those items that are not in the list.
    """

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        self._v_box_layout = QVBoxLayout(self)
        self._v_box_layout.setMargin(0)

        self._combo_Item = QComboBox(self)
        self._combo_Item.setMinimumSize(QSize(0, 30))
        self._v_box_layout.addWidget(self._combo_Item)

        self._txt_other = QLineEdit(self)
        self._txt_other.setMinimumSize(QSize(0, 30))
        self._txt_other.setVisible(False)
        self._v_box_layout.addWidget(self._txt_other)

        # We are using random text here so that the custom line edit is not
        # shown on selecting a blank item in the list.
        self._activator_text = QApplication.translate(
            "ComboBoxWithOther", "Other")

        # Connect signals
        self.connect(
            self._combo_Item, SIGNAL("currentIndexChanged(const QString&)"),
            self.on_combo_index_changed)

    def sizeHint(self):
        """
        Size hint for the control.
        :rtype : QSize
        """
        return QSize(190, 80)

    def minimumHeight(self):
        """
        Minimum widget height.
        :rtype : int
        """
        return 70

    def combo_box(self):
        """
        Returns a reference to the combobox control.
        :rtype : QComboBox
        """
        return self._combo_Item

    def line_edit(self):
        """
        Returns a reference to the line edit control.
        :rtype : QLineEdit
        """
        return self._txt_other

    def activator_text(self):
        """
        Returns the text that is used to display the line edit control that
        enables the user to enter values that are not available in the
        combobox list.
        :rtype : QApplication
        """
        return self._activator_text

    def set_activator_text(self, activator_text):
        """
        Set the text that will be used to display the line edit control that
        enables the user to enter values that are not available in the
        combobox list.
        :param activator_text:
        """
        if not isinstance(activator_text, str):
            self._activator_text = str(activator_text)
        else:
            self._activator_text = activator_text

    def on_combo_index_changed(self, index_text):
        """
        Slot raised when the current index of the combobox changes. This
        searches for the activator text and loads the line edit for entering
        'Other' value.
        :param index_text:
        """
        self._txt_other.clear()

        if index_text == self._activator_text:
            self._txt_other.setVisible(True)
        else:
            self._txt_other.setVisible(False)

    def validate(self):
        """
        Validates the state of the control
        :rtype : bool, str
        """
        is_valid = True
        msg = ""

        if self._combo_Item.currentText() is self._activator_text \
                and self._txt_other.text() is "":
            msg = QApplication.translate(
                "ComboBoxWithOther", "'{0}' text cannot be empty.".format(
                    unicode(self._activator_text)))
            is_valid = False

        return is_valid, msg
