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
from typing import Optional

from qgis.PyQt.QtCore import (
    QCoreApplication
)
from qgis.PyQt.QtWidgets import (
    QVBoxLayout,
    QLabel,
    QSizePolicy
)
from qgis.core import (
    QgsLayoutItemRegistry,
    QgsLayoutItemAbstractMetadata,
    QgsLayoutItemPolyline,
    QgsLayoutItemLabel,
    QgsLayoutItemMap,
    QgsLayoutItemPicture,
    QgsApplication,
    QgsLayoutItem
)
from qgis.gui import (
    QgsGui,
    QgsLayoutItemAbstractGuiMetadata,
    QgsLayoutItemBaseWidget
)

from stdm.ui.gui_utils import GuiUtils
from stdm.ui.composer.composer_field_selector import ComposerFieldSelector


BASE_ITEM_TYPE = QgsLayoutItemRegistry.PluginItem + 2337
STDM_LINE_ITEM_TYPE = BASE_ITEM_TYPE + 0
STDM_DATA_LABEL_ITEM_TYPE = BASE_ITEM_TYPE + 1
STDM_DATA_TABLE_ITEM_TYPE = BASE_ITEM_TYPE + 2
STDM_MAP_ITEM_TYPE = BASE_ITEM_TYPE + 3
STDM_PHOTO_ITEM_TYPE = BASE_ITEM_TYPE + 4
STDM_CHART_ITEM_TYPE = BASE_ITEM_TYPE + 5
STDM_QR_ITEM_TYPE = BASE_ITEM_TYPE + 6


class LayoutGuiUtils:

    @staticmethod
    def get_gui_metadata_for_item_type(item_type: int) -> Optional[QgsLayoutItemAbstractGuiMetadata]:
        for item_gui_id in QgsGui.layoutItemGuiRegistry().itemMetadataIds():
            if QgsGui.layoutItemGuiRegistry().itemMetadata(item_gui_id).type() == item_type:
                return QgsGui.layoutItemGuiRegistry().itemMetadata(item_gui_id)
        return None

    @staticmethod
    def create_standard_item_widget(item: QgsLayoutItem, standard_item_type: int) -> Optional[QgsLayoutItemBaseWidget]:
        metadata = LayoutGuiUtils.get_gui_metadata_for_item_type(standard_item_type)
        if metadata is None:
            return None

        return metadata.createItemWidget(item)

    @staticmethod
    def create_heading_label(text: str) -> QLabel:
        label = QLabel(text)
        sp = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        sp.setHorizontalStretch(0)
        sp.setVerticalStretch(0)
        sp.setHeightForWidth(label.sizePolicy().hasHeightForWidth())
        label.setSizePolicy(sp)
        label.setStyleSheet("padding: 2px; font-weight: bold; background-color: rgb(200, 200, 200);")
        return label


class StdmLineLayoutItem(QgsLayoutItemPolyline):

    def __init__(self, layout):
        super().__init__(layout)

    def type(self):
        return STDM_LINE_ITEM_TYPE

    def icon(self):
        return GuiUtils.get_icon('line.png')


class StdmLineLayoutItemMetadata(QgsLayoutItemAbstractMetadata):

    def __init__(self):
        super().__init__(STDM_LINE_ITEM_TYPE, QCoreApplication.translate('StdmItems', 'STDM Line'))

    def createItem(self, layout):
        return StdmLineLayoutItem(layout)


class StdmLineLayoutItemGuiMetadata(QgsLayoutItemAbstractGuiMetadata):

    def __init__(self):
        super().__init__(STDM_LINE_ITEM_TYPE, QCoreApplication.translate('StdmItems', 'STDM Line'))

    def creationIcon(self):  # pylint: disable=missing-docstring, no-self-use
        return GuiUtils.get_icon('line.png')

    def createItemWidget(self, item):  # pylint: disable=missing-docstring, no-self-use
        return None  # PlotLayoutItemWidget(None, item)


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


class DataLabelConfigWidget(QgsLayoutItemBaseWidget):

    def __init__(self, parent, layout_object):
        super().__init__(parent, layout_object)

        label = LayoutGuiUtils.create_heading_label(QCoreApplication.translate('StdmItems', 'STDM Item Properties'))

        vl = QVBoxLayout()
        vl.setContentsMargins(0, 0, 0, 0)
        vl.addWidget(label)

        fieldSelector = ComposerFieldSelector(layout_object)
        vl.addWidget(fieldSelector)

        base_widget = LayoutGuiUtils.create_standard_item_widget(layout_object, QgsLayoutItemRegistry.LayoutLabel)
        vl.addWidget(base_widget)

        self.setLayout(vl)


class StdmDataLabelLayoutItemGuiMetadata(QgsLayoutItemAbstractGuiMetadata):

    def __init__(self):
        super().__init__(STDM_DATA_LABEL_ITEM_TYPE, QCoreApplication.translate('StdmItems', 'STDM Data Label'))

    def creationIcon(self):  # pylint: disable=missing-docstring, no-self-use
        return GuiUtils.get_icon('db_field.png')

    def createItemWidget(self, item):  # pylint: disable=missing-docstring, no-self-use
        return DataLabelConfigWidget(None, item)

    def newItemAddedToLayout(self, item):
        item.setText(QCoreApplication.translate("DataLabelFormatter", "[STDM Data Field]"))

        # Adjust width
        item.adjustSizeToText()

        # Set ID to match UUID
        item.setId(item.uuid())


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


class StdmTableLayoutItemGuiMetadata(QgsLayoutItemAbstractGuiMetadata):

    def __init__(self):
        super().__init__(STDM_DATA_TABLE_ITEM_TYPE, QCoreApplication.translate('StdmItems', 'STDM Data Table'))

    def creationIcon(self):  # pylint: disable=missing-docstring, no-self-use
        return GuiUtils.get_icon('composer_table.png')

    def createItemWidget(self, item):  # pylint: disable=missing-docstring, no-self-use
        return None  # PlotLayoutItemWidget(None, item)


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


class StdmMapLayoutItemGuiMetadata(QgsLayoutItemAbstractGuiMetadata):

    def __init__(self):
        super().__init__(STDM_MAP_ITEM_TYPE, QCoreApplication.translate('StdmItems', 'STDM Map'))

    def creationIcon(self):  # pylint: disable=missing-docstring, no-self-use
        return GuiUtils.get_icon('add_map.png')

    def createItemWidget(self, item):  # pylint: disable=missing-docstring, no-self-use
        return None  # PlotLayoutItemWidget(None, item)


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


class StdmPhotoLayoutItemGuiMetadata(QgsLayoutItemAbstractGuiMetadata):

    def __init__(self):
        super().__init__(STDM_PHOTO_ITEM_TYPE, QCoreApplication.translate('StdmItems', 'STDM Photo'))

    def creationIcon(self):  # pylint: disable=missing-docstring, no-self-use
        return GuiUtils.get_icon('photo_24.png')

    def createItemWidget(self, item):  # pylint: disable=missing-docstring, no-self-use
        return None  # PlotLayoutItemWidget(None, item)


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


class StdmChartLayoutItemGuiMetadata(QgsLayoutItemAbstractGuiMetadata):

    def __init__(self):
        super().__init__(STDM_CHART_ITEM_TYPE, QCoreApplication.translate('StdmItems', 'STDM Chart'))

    def creationIcon(self):  # pylint: disable=missing-docstring, no-self-use
        return GuiUtils.get_icon('chart.png')

    def createItemWidget(self, item):  # pylint: disable=missing-docstring, no-self-use
        return None  # PlotLayoutItemWidget(None, item)


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


class StdmQrCodeLayoutItemGuiMetadata(QgsLayoutItemAbstractGuiMetadata):

    def __init__(self):
        super().__init__(STDM_QR_ITEM_TYPE, QCoreApplication.translate('StdmItems', 'QR Code'))

    def creationIcon(self):  # pylint: disable=missing-docstring, no-self-use
        return GuiUtils.get_icon('qrcode.png')

    def createItemWidget(self, item):  # pylint: disable=missing-docstring, no-self-use
        return None  # PlotLayoutItemWidget(None, item)


class StdmCustomLayoutItems:
    CUSTOM_CLASSES = [StdmLineLayoutItemMetadata,
                      StdmDataLabelLayoutItemMetadata,
                      StdmTableLayoutItemMetadata,
                      StdmMapLayoutItemMetadata,
                      StdmPhotoLayoutItemMetadata,
                      StdmChartLayoutItemMetadata,
                      StdmQrCodeLayoutItemMetadata]
    GUI_CLASSES = [StdmLineLayoutItemGuiMetadata,
                   StdmDataLabelLayoutItemGuiMetadata,
                   StdmTableLayoutItemGuiMetadata,
                   StdmMapLayoutItemGuiMetadata,
                   StdmPhotoLayoutItemGuiMetadata,
                   StdmChartLayoutItemGuiMetadata,
                   StdmQrCodeLayoutItemGuiMetadata]

    metadata = []
    gui_metadata = []

    @classmethod
    def add_custom_item_types(cls):
        for m in cls.CUSTOM_CLASSES:
            item_metadata = m()
            if item_metadata.type() in QgsApplication.layoutItemRegistry().itemTypes():
                continue  # already added

            cls.metadata.append(item_metadata)
            QgsApplication.layoutItemRegistry().addLayoutItemType(item_metadata)

    @classmethod
    def register_gui(cls):
        existing_items_types = [QgsGui.layoutItemGuiRegistry().itemMetadata(_id).type() for _id in
                                QgsGui.layoutItemGuiRegistry().itemMetadataIds()]

        for m in cls.GUI_CLASSES:
            item_metadata = m()

            if item_metadata.type() in existing_items_types:
                continue  # already added

            cls.gui_metadata.append(item_metadata)
            QgsGui.layoutItemGuiRegistry().addLayoutItemGuiMetadata(item_metadata)

    @classmethod
    def stdm_action_text(cls):
        items = [m().visibleName() for m in cls.GUI_CLASSES]
        return [QCoreApplication.translate('StdmItems', 'Add {}'.format(t)) for t in items]
