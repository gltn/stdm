"""
/***************************************************************************
Name                 : ImageExportSettings
Description          : A dialog for providing edit options for exporting an
                        image.
Date                 : 9/October/2016
copyright            : (C) 2016 by UN-Habitat and implementing partners.
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
from qgis.PyQt import uic
from qgis.PyQt.QtCore import (
    Qt
)
from qgis.PyQt.QtGui import (
    QImageWriter
)
from qgis.PyQt.QtWidgets import (
    QFileDialog
)

from stdm.ui.gui_utils import GuiUtils
from stdm.ui.notification import NotificationBar

WIDGET, BASE = uic.loadUiType(
    GuiUtils.get_ui_file_path('ui_image_export_settings.ui'))


class ImageExportSettings(WIDGET, BASE):
    """A dialog for settings options for exporting an image."""

    def __init__(self, parent=None, **kwargs):
        super(ImageExportSettings, self).__init__(parent)
        self.setupUi(self)

        self.btn_path.setIcon(GuiUtils.get_icon('open_file.png'))

        self._image_tr = self.tr('Image')

        self.notif_bar = NotificationBar(self.vl_notification, 6000)

        # Connect signals
        self.btn_path.clicked.connect(self._on_choose_image_path)
        self.buttonBox.accepted.connect(self.on_accept)
        self.sb_resolution.valueChanged.connect(self._on_resolution_changed)

        # Set color button defaults
        self._default_color = Qt.white
        self.btn_color.setDefaultColor(self._default_color)
        self.btn_color.setColor(self._default_color)
        self.btn_color.setAllowOpacity(True)

        self.path = kwargs.get('image_path', '')
        self.resolution = kwargs.get('resolution', '96')
        self.background_color = kwargs.get('background', Qt.transparent)

        self._update_controls()

    def _update_controls(self):
        # Update input controls with export settings' values
        if self.background_color == Qt.transparent:
            self.rb_transparent.setChecked(True)
            self.btn_color.setVisible(False)

        else:
            self.rb_fill.setChecked(True)
            self.btn_color.setColor(self.background_color)

        self.sb_resolution.setValue(int(self.resolution))
        self.txt_path.setText(self.path)

        # Set image size just in case value does not change
        self._set_image_size()

    def _on_resolution_changed(self, value):
        # Slot raised when the resolution changes
        self._set_image_size()

    def _update_export_vars(self):
        # Update export variables based on user values.
        self.path = self.txt_path.text()
        self.resolution = self.sb_resolution.value()

        if self.rb_transparent.isChecked():
            self.background_color = Qt.transparent

        else:
            self.background_color = self.btn_color.color()

    def _set_image_size(self):
        # Set image size based on the resolution using A4 paper size
        res = self.sb_resolution.value()
        if res == 0:
            return

        # To mm
        res_mm = res / 25.4

        # A4 landscape size
        width = int(297 * res_mm)
        height = int(210 * res_mm)

        units = 'px'
        width_display = '{0} {1}'.format(width, units)
        height_display = '{0} {1}'.format(height, units)
        self.lbl_width.setText(width_display)
        self.lbl_height.setText(height_display)

    def _image_filters(self):
        # Return supported image formats for use in a QFileDialog filter
        formats = []

        for f in QImageWriter.supportedImageFormats():
            f_type = f.data().decode()
            filter_format = '{0} {1} (*.{2})'.format(
                f_type.upper(),
                self._image_tr,
                f_type
            )
            formats.append(filter_format)

        return ';;'.join(formats)

    def _on_choose_image_path(self):
        # Slot raised to choose image path
        img_path = self.txt_path.text()
        title = self.tr('Specify image location')
        sel_image_path, _ = QFileDialog.getSaveFileName(
            self,
            title,
            img_path,
            self._image_filters()
        )

        if sel_image_path:
            self.txt_path.setText(sel_image_path)

    def on_accept(self):
        """
        Slot raised to save the settings and close the dialog.
        """
        if not self.txt_path.text():
            msg = self.tr('Please specify the image path.')
            self.notif_bar.insertErrorNotification(msg)
            self.txt_path.setFocus()

            return

        self._update_export_vars()

        self.accept()
