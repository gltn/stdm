# /***************************************************************************
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation; either version 2 of the License, or     *
# *   (at your option) any later version.                                   *
# *                                                                         *
# ***************************************************************************/

"""
Contains custom layout item types
"""
from qgis.PyQt.QtCore import (
    QCoreApplication,
    QPointF
)
from qgis.PyQt.QtGui import QPolygonF
from qgis.core import (
    QgsLayoutItemRegistry,
    QgsLayoutItemAbstractMetadata,
    QgsLayoutItemPolyline,
    QgsLayoutItemLabel,
    QgsLayoutItemMap,
    QgsLayoutItemPicture,
    QgsApplication
)

from stdm.ui.gui_utils import GuiUtils

BASE_ITEM_TYPE = QgsLayoutItemRegistry.PluginItem + 2337
STDM_LINE_ITEM_TYPE = BASE_ITEM_TYPE + 0
STDM_DATA_LABEL_ITEM_TYPE = BASE_ITEM_TYPE + 1
STDM_DATA_TABLE_ITEM_TYPE = BASE_ITEM_TYPE + 2
STDM_MAP_ITEM_TYPE = BASE_ITEM_TYPE + 3
STDM_PHOTO_ITEM_TYPE = BASE_ITEM_TYPE + 4
STDM_CHART_ITEM_TYPE = BASE_ITEM_TYPE + 5
STDM_QR_ITEM_TYPE = BASE_ITEM_TYPE + 6


class StdmLineLayoutItem(QgsLayoutItemPolyline):

    def __init__(self, layout):
        super().__init__(layout)
        self._size = None
        self._point = None

    def type(self):
        return STDM_LINE_ITEM_TYPE

    def icon(self):
        return GuiUtils.get_icon('line.png')

    def attemptResize(self, size, includesFrame):
        if not self.nodes():
            self._size = size
            self._set_initial_line()
        else:
            super().attemptResize(size, includesFrame)

    def attemptMove(self, point, useReferencePoint, includesFrame, page):
        if not self.nodes():
            self._point = point
            self._set_initial_line()
        else:
            super().attemptMove(point, useReferencePoint, includesFrame, page)

    def _set_initial_line(self):
        if self._point is not None and self._size is not None:
            self.setNodes(QPolygonF([QPointF(self._point.x(), self._point.y()),
                                     QPointF(self._point.x() + self._size.width(),
                                             self._point.y() + self._size.height())]))
            self._point = None
            self._size = None


class StdmLineLayoutItemMetadata(QgsLayoutItemAbstractMetadata):

    def __init__(self):
        super().__init__(STDM_LINE_ITEM_TYPE, QCoreApplication.translate('StdmItems', 'STDM Line'))

    def createItem(self, layout):
        return StdmLineLayoutItem(layout)


class StdmDataLabelLayoutItem(QgsLayoutItemLabel):

    def __init__(self, layout):
        super().__init__(layout)

    def type(self):
        return STDM_DATA_LABEL_ITEM_TYPE

    def icon(self):
        return GuiUtils.get_icon('db_field.png')


class StdmDataLabelLayoutItemMetadata(QgsLayoutItemAbstractMetadata):

    def __init__(self):
        super().__init__(STDM_DATA_LABEL_ITEM_TYPE, QCoreApplication.translate('StdmItems', 'STDM Data Label'))

    def createItem(self, layout):
        return StdmDataLabelLayoutItem(layout)


class StdmTableLayoutItem(QgsLayoutItemLabel):

    def __init__(self, layout):
        super().__init__(layout)

    def type(self):
        return STDM_DATA_TABLE_ITEM_TYPE

    def icon(self):
        return GuiUtils.get_icon('composer_table.png')


class StdmTableLayoutItemMetadata(QgsLayoutItemAbstractMetadata):

    def __init__(self):
        super().__init__(STDM_DATA_TABLE_ITEM_TYPE, QCoreApplication.translate('StdmItems', 'STDM Data Table'))

    def createItem(self, layout):
        return StdmTableLayoutItem(layout)


class StdmMapLayoutItem(QgsLayoutItemMap):

    def __init__(self, layout):
        super().__init__(layout)

    def type(self):
        return STDM_MAP_ITEM_TYPE

    def icon(self):
        return GuiUtils.get_icon('add_map.png')


class StdmMapLayoutItemMetadata(QgsLayoutItemAbstractMetadata):

    def __init__(self):
        super().__init__(STDM_MAP_ITEM_TYPE, QCoreApplication.translate('StdmItems', 'STDM Map'))

    def createItem(self, layout):
        return StdmMapLayoutItem(layout)


class StdmPhotoLayoutItem(QgsLayoutItemPicture):

    def __init__(self, layout):
        super().__init__(layout)

    def type(self):
        return STDM_PHOTO_ITEM_TYPE

    def icon(self):
        return GuiUtils.get_icon('photo_24.png')


class StdmPhotoLayoutItemMetadata(QgsLayoutItemAbstractMetadata):

    def __init__(self):
        super().__init__(STDM_PHOTO_ITEM_TYPE, QCoreApplication.translate('StdmItems', 'STDM Photo'))

    def createItem(self, layout):
        return StdmPhotoLayoutItem(layout)


class StdmChartLayoutItem(QgsLayoutItemPicture):

    def __init__(self, layout):
        super().__init__(layout)

    def type(self):
        return STDM_CHART_ITEM_TYPE

    def icon(self):
        return GuiUtils.get_icon('chart.png')


class StdmChartLayoutItemMetadata(QgsLayoutItemAbstractMetadata):

    def __init__(self):
        super().__init__(STDM_CHART_ITEM_TYPE, QCoreApplication.translate('StdmItems', 'STDM Chart'))

    def createItem(self, layout):
        return StdmChartLayoutItem(layout)


class StdmQrCodeLayoutItem(QgsLayoutItemPicture):

    def __init__(self, layout):
        super().__init__(layout)

    def type(self):
        return STDM_QR_ITEM_TYPE

    def icon(self):
        return GuiUtils.get_icon('qrcode.png')


class StdmQrCodeLayoutItemMetadata(QgsLayoutItemAbstractMetadata):

    def __init__(self):
        super().__init__(STDM_QR_ITEM_TYPE, QCoreApplication.translate('StdmItems', 'QR Code'))

    def createItem(self, layout):
        return StdmQrCodeLayoutItem(layout)


class StdmCustomLayoutItems:
    CUSTOM_CLASSES = [StdmLineLayoutItemMetadata,
                      StdmDataLabelLayoutItemMetadata,
                      StdmTableLayoutItemMetadata,
                      StdmMapLayoutItemMetadata,
                      StdmPhotoLayoutItemMetadata,
                      StdmChartLayoutItemMetadata,
                      StdmQrCodeLayoutItemMetadata]
    metadata = []

    @classmethod
    def add_custom_item_types(cls):
        for m in cls.CUSTOM_CLASSES:
            item_metadata = m()
            if item_metadata.type() in QgsApplication.layoutItemRegistry().itemTypes():
                continue  # already added

            cls.metadata.append(item_metadata)
            QgsApplication.layoutItemRegistry().addLayoutItemType(item_metadata)
