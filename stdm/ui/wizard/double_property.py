# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : double_property
Description          : Set properties for Double data type
Date                 : 02/January/2016
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
from decimal import (
    Decimal,
    InvalidOperation
)

import math

from qgis.PyQt.QtGui import QDoubleValidator
from qgis.PyQt.QtWidgets import (
    QDialog,
    QApplication,
    QMessageBox
)

from stdm.ui.wizard.ui_double_property import Ui_DoubleProperty

class DoubleProperty(QDialog, Ui_DoubleProperty):
    """
    Editor to create/edit Double column property
    """
    def __init__(self, parent, form_fields):
        """
        :param parent: Owner of the form
        :type parent: QWidget
        :param form_fields: Contains data from the column editor window
        :type form_field: dictionary
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self._min_val = form_fields['minimum']
        self._max_val = form_fields['maximum']
        self._precision = form_fields['precision']
        self._scale = form_fields['scale']
        self.in_db = form_fields['in_db']

        # Connect signals
        self.sbPrecision.valueChanged.connect(self._on_precision_changed)
        self.sbScale.valueChanged.connect(self._on_scale_changed)

        self.init_gui()

    def init_gui(self):
        """
        Initializes form widgets
        """
        validator = QDoubleValidator()
        self.edtMinVal.setValidator(validator)
        self.edtMaxVal.setValidator(validator)

        self.edtMinVal.setText(str(self._min_val))
        self.edtMaxVal.setText(str(self._max_val))

        self.edtMinVal.setEnabled(not self.in_db)
        self.edtMaxVal.setEnabled(not self.in_db)
        self.sbPrecision.setEnabled(not self.in_db)
        self.sbScale.setEnabled(not self.in_db)

        self.sbPrecision.setValue(self._precision)
        self.sbScale.setValue(self._scale)

    @property
    def precision(self):
        """
        :return: Returns the user defined precision value.
         :rtype: int
        """
        return self._precision

    @property
    def scale(self):
        """
        :return: Returns the user-defined scale value.
        :rtype: int
        """
        return self._scale

    def _scale_quantize_factor(self, scale):
        # Returns the quantization factor that will be used to compute the
        # minimum and maximum value.
        return round(math.pow(0.1, scale), scale)

    def _generate_quantized_value(self, value, scale):
        # Returns the quantized value based on the given scale.
        try:
            q_value = Decimal(value).quantize(
                Decimal(
                    str(self._scale_quantize_factor(scale))
                )
            )
        except InvalidOperation:
            q_value = value

        return q_value

    def _on_precision_changed(self, value):
        # Slot raised when the value of the precision in the spinbox changes
        pass

    def _on_scale_changed(self, value):
        # Slot raised when the value of the scale in the spinbox changes.
        # Update minimum and maximum values for illustration purposes.
        min_val = self.edtMinVal.text()
        max_val = self.edtMaxVal.text()

        # Update the scale of the specified values
        if min_val:
            min_val = str(self._generate_quantized_value(min_val, value))
            self.edtMinVal.setText(min_val)

        if max_val:
            max_val = str(self._generate_quantized_value(max_val, value))
            self.edtMaxVal.setText(max_val)

    def add_values(self):
        """
        Sets min/max properties with values from form widgets
        """
        self._min_val = float(self.edtMinVal.text())
        self._max_val = float(self.edtMaxVal.text())
        self._precision = int(self.sbPrecision.value())
        self._scale = int(self.sbScale.value())

    def min_val(self):
        """
        Returns minimum property
        :rtype: int
        """
        return self._min_val

    def max_val(self):
        """
        Returns maximum property
        :rtype: int
        """
        return self._max_val

    def accept(self):
        if self.edtMinVal.text()=='':
            self.show_message(QApplication.translate("DoublePropetyEditor",
                "Please set minimum value"))
            return

        if self.edtMaxVal.text()=='':
            self.show_message(QApplication.translate("DoublePropetyEditor",
                "Pleasei set maximum value."))
            return

        self.add_values()
        self.done(1)

    def reject(self):
        self.done(0)

    def show_message(self, message, msg_icon=QMessageBox.Critical):
        msg = QMessageBox(self)
        msg.setIcon(msg_icon)
        msg.setWindowTitle(QApplication.translate("STDM Configuration Wizard","STDM"))
        msg.setText(QApplication.translate("STDM Configuration Wizard",message))
        msg.exec_()
