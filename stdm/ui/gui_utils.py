# -*- coding: utf-8 -*-
"""GUI Utilities

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

__author__ = '(C) 2018 by Nyall Dawson'
__date__ = '20/04/2018'
__copyright__ = 'Copyright 2018, North Road'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

import math
import os
from typing import Optional

from qgis.PyQt.QtCore import (
    QSize,
    QPointF
)
from qgis.PyQt.QtGui import (
    QIcon,
    QFont,
    QFontMetrics,
    QImage,
    QPainter,
    QPixmap
)
from qgis.PyQt.QtWidgets import QComboBox

from qgis.core import (
    Qgis,
    QgsExpressionContext,
    QgsRenderContext,
    QgsSymbol
)


class GuiUtils:
    """
    Utilities for GUI plugin components
    """

    @staticmethod
    def get_icon(icon: str) -> QIcon:
        """
        Returns a plugin icon
        :param icon: icon name (svg file name)
        :return: QIcon
        """
        path = GuiUtils.get_icon_svg(icon)
        if not path:
            return QIcon()

        return QIcon(path)

    @staticmethod
    def get_icon_svg(icon: str) -> str:
        """
        Returns a plugin icon's SVG file path
        :param icon: icon name (svg file name)
        :return: icon svg path
        """
        path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'images',
            'icons',
            icon)
        if not os.path.exists(path):
            return ''

        return path

    @staticmethod
    def get_icon_pixmap(icon: str) -> QPixmap:
        """
        Returns a plugin icon's PNG file path
        :param icon: icon name (png file name)
        :return: icon png path
        """
        path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'images',
            'icons',
            icon)
        if not os.path.exists(path):
            return QPixmap()

        im = QImage(path)
        return QPixmap.fromImage(im)

    @staticmethod
    def get_ui_file_path(file: str) -> str:
        """
        Returns a UI file's path
        :param file: file name (uifile name)
        :return: ui file path
        """
        path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'ui',
            file)
        if not os.path.exists(path):
            return ''

        return path

    @staticmethod
    def scale_icon_size(standard_size: int) -> int:
        """
        Scales an icon size accounting for device DPI
        """
        fm = QFontMetrics((QFont()))
        scale = 1.1 * standard_size / 24.0
        return int(math.floor(max(Qgis.UI_SCALE_FACTOR * fm.height() * scale,
                                  float(standard_size))))

    @staticmethod
    def big_marker_preview_image(symbol: QgsSymbol,
                                 expression_context: Optional[QgsExpressionContext] = None) -> QImage:
        """
        Generate a big symbol preview image for a marker
        """
        preview = QImage(QSize(100, 100), QImage.Format_ARGB32_Premultiplied)
        preview.fill(0)

        p = QPainter(preview)
        p.setRenderHint(QPainter.Antialiasing)
        p.translate(0.5, 0.5)

        context = QgsRenderContext.fromQPainter(p)
        try:
            context.setFlag(QgsRenderContext.RenderSymbolPreview)
        except AttributeError:
            pass

        if expression_context:
            context.setExpressionContext(expression_context)

        try:
            context.setIsGuiPreview(True)
        except AttributeError:
            pass

        symbol.startRender(context)
        symbol.renderPoint(QPointF(50, 50), None, context)
        symbol.stopRender(context)

        return preview

    @staticmethod
    def set_combo_index_by_data(combo: QComboBox, item_data, on_none_set_current_index: bool = True):
        """
        Convenience method for setting the current index of the combo item
        with the specified value of the item data.
        """
        if item_data is None and on_none_set_current_index:
            combo.setCurrentIndex(0)
        elif item_data is None and not on_none_set_current_index:
            return

        current_index = combo.findData(item_data)
        if current_index != -1:
            combo.setCurrentIndex(current_index)

    @staticmethod
    def set_combo_current_index_by_text(combo: QComboBox, text: str):
        """
        Convenience method for setting the current index of the combo item
        with the specified value of the corresponding display text.
        """
        txt_index = combo.findText(text)
        if txt_index != -1:
            combo.setCurrentIndex(txt_index)
