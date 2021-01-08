# /***************************************************************************
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation; either version 2 of the License, or     *
# *   (at your option) any later version.                                   *
# *                                                                         *
# ***************************************************************************/

"""
Contains GUI classes for STDM custom layout item types
"""
from qgis.PyQt.QtCore import (
    QCoreApplication,
    QFile
)
from qgis.PyQt.QtWidgets import (
    QVBoxLayout,
    QWidget
)
from qgis.core import (
    QgsLayoutItemRegistry,
    QgsLayoutItemPicture,
    QgsLayoutMeasurement,
    QgsUnitTypes
)
from qgis.gui import (
    QgsGui,
    QgsLayoutItemBaseWidget,
    QgsLayoutItemAbstractGuiMetadata
)

from stdm.composer.custom_layout_items import (
    STDM_LINE_ITEM_TYPE,
    STDM_DATA_LABEL_ITEM_TYPE,
    STDM_DATA_TABLE_ITEM_TYPE,
    STDM_MAP_ITEM_TYPE,
    STDM_PHOTO_ITEM_TYPE,
    STDM_CHART_ITEM_TYPE,
    STDM_QR_ITEM_TYPE
)
from stdm.ui.composer.composer_field_selector import ComposerFieldSelector
from stdm.ui.composer.layout_gui_utils import LayoutGuiUtils
from stdm.ui.composer.linear_rubber_band import LinearRubberBand
from stdm.ui.composer.photo_data_source import ComposerPhotoDataSourceEditor
from stdm.ui.composer.qr_code import ComposerQREditor
from stdm.ui.composer.composer_chart_config import ComposerChartConfigEditor
from stdm.ui.gui_utils import GuiUtils


class LineConfigWidget(QgsLayoutItemBaseWidget):

    def __init__(self, parent, layout_object):
        super().__init__(parent, layout_object)

        label = LayoutGuiUtils.create_heading_label(QCoreApplication.translate('StdmItems', 'STDM Item Properties'))

        vl = QVBoxLayout()
        vl.setContentsMargins(0, 0, 0, 0)
        vl.addWidget(label)

        self.base_widget = LayoutGuiUtils.create_standard_item_widget(layout_object,
                                                                      QgsLayoutItemRegistry.LayoutPolyline)

        arrow_group = self.base_widget.findChild(QWidget, 'mArrowMarkersGroupBox')
        if arrow_group is not None:
            arrow_group.setVisible(False)

        self.connectChildPanel(self.base_widget)
        vl.addWidget(self.base_widget)

        self.setLayout(vl)

    def setDockMode(self, dockMode):
        self.base_widget.setDockMode(dockMode)
        super().setDockMode(dockMode)


class StdmLineLayoutItemGuiMetadata(QgsLayoutItemAbstractGuiMetadata):

    def __init__(self):
        super().__init__(STDM_LINE_ITEM_TYPE, QCoreApplication.translate('StdmItems', 'STDM Line'))

    def creationIcon(self):  # pylint: disable=missing-docstring, no-self-use
        return GuiUtils.get_icon('line.png')

    def createItemWidget(self, item):  # pylint: disable=missing-docstring, no-self-use
        return LineConfigWidget(None, item)

    def createRubberBand(self, view):
        return LinearRubberBand(view)


class DataLabelConfigWidget(QgsLayoutItemBaseWidget):

    def __init__(self, parent, layout_object):
        super().__init__(parent, layout_object)

        label = LayoutGuiUtils.create_heading_label(QCoreApplication.translate('StdmItems', 'STDM Item Properties'))

        vl = QVBoxLayout()
        vl.setContentsMargins(0, 0, 0, 0)
        vl.addWidget(label)

        fieldSelector = ComposerFieldSelector(layout_object)
        vl.addWidget(fieldSelector)

        self.base_widget = LayoutGuiUtils.create_standard_item_widget(layout_object, QgsLayoutItemRegistry.LayoutLabel)
        expression_button = self.base_widget.findChild(QWidget, 'mInsertExpressionButton')
        if expression_button is not None:
            expression_button.setVisible(False)

        self.connectChildPanel(self.base_widget)
        vl.addWidget(self.base_widget)

        self.setLayout(vl)

    def setDockMode(self, dockMode):
        self.base_widget.setDockMode(dockMode)
        super().setDockMode(dockMode)


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


class StdmTableLayoutItemGuiMetadata(QgsLayoutItemAbstractGuiMetadata):

    def __init__(self):
        super().__init__(STDM_DATA_TABLE_ITEM_TYPE, QCoreApplication.translate('StdmItems', 'STDM Data Table'))

    def creationIcon(self):  # pylint: disable=missing-docstring, no-self-use
        return GuiUtils.get_icon('composer_table.png')

    def createItemWidget(self, item):  # pylint: disable=missing-docstring, no-self-use
        return None  # PlotLayoutItemWidget(None, item)


class MapConfigWidget(QgsLayoutItemBaseWidget):

    def __init__(self, parent, layout_object):
        super().__init__(parent, layout_object)

        label = LayoutGuiUtils.create_heading_label(QCoreApplication.translate('StdmItems', 'STDM Item Properties'))

        vl = QVBoxLayout()
        vl.setContentsMargins(0, 0, 0, 0)
        vl.addWidget(label)

        self.base_widget = LayoutGuiUtils.create_standard_item_widget(layout_object, QgsLayoutItemRegistry.LayoutMap)

        self.connectChildPanel(self.base_widget)
        vl.addWidget(self.base_widget)

        self.setLayout(vl)

    def setDockMode(self, dockMode):
        self.base_widget.setDockMode(dockMode)
        super().setDockMode(dockMode)


class StdmMapLayoutItemGuiMetadata(QgsLayoutItemAbstractGuiMetadata):

    def __init__(self):
        super().__init__(STDM_MAP_ITEM_TYPE, QCoreApplication.translate('StdmItems', 'STDM Map'))

    def creationIcon(self):  # pylint: disable=missing-docstring, no-self-use
        return GuiUtils.get_icon('add_map.png')

    def createItemWidget(self, item):  # pylint: disable=missing-docstring, no-self-use
        return MapConfigWidget(None, item)


class PhotoConfigWidget(QgsLayoutItemBaseWidget):

    def __init__(self, parent, layout_object):
        super().__init__(parent, layout_object)
        label = LayoutGuiUtils.create_heading_label(QCoreApplication.translate('StdmItems', 'STDM Item Properties'))

        vl = QVBoxLayout()
        vl.setContentsMargins(0, 0, 0, 0)
        vl.addWidget(label)

        data_source_editor = ComposerPhotoDataSourceEditor(layout_object)
        vl.addWidget(data_source_editor)

        self.base_widget = LayoutGuiUtils.create_standard_item_widget(layout_object,
                                                                      QgsLayoutItemRegistry.LayoutPicture)

        for name in (
                'mSVGFrame', 'mRotationGroupBox', 'mSVGParamsGroupBox', 'mRadioSVG', 'mRadioRaster', 'mRasterFrame',
                'mPreviewGroupBox'):
            widget = self.base_widget.findChild(QWidget, name)
            if widget is not None:
                widget.setVisible(False)

        self.connectChildPanel(self.base_widget)
        vl.addWidget(self.base_widget)

        self.setLayout(vl)

    def setDockMode(self, dockMode):
        self.base_widget.setDockMode(dockMode)
        super().setDockMode(dockMode)


class StdmPhotoLayoutItemGuiMetadata(QgsLayoutItemAbstractGuiMetadata):

    def __init__(self):
        super().__init__(STDM_PHOTO_ITEM_TYPE, QCoreApplication.translate('StdmItems', 'STDM Photo'))

        self.default_photo = GuiUtils.get_icon_svg("photo_512.png")

    def creationIcon(self):  # pylint: disable=missing-docstring, no-self-use
        return GuiUtils.get_icon('photo_24.png')

    def createItemWidget(self, item):  # pylint: disable=missing-docstring, no-self-use
        return PhotoConfigWidget(None, item)

    def newItemAddedToLayout(self, item):
        try:
            item.setMode(QgsLayoutItemPicture.FormatRaster)
        except AttributeError:
            pass

        item.setFrameEnabled(True)
        item.setFrameStrokeWidth(QgsLayoutMeasurement(0.5, QgsUnitTypes.LayoutMillimeters))

        item.setResizeMode(QgsLayoutItemPicture.ZoomResizeFrame)

        if QFile.exists(self.default_photo):
            item.setPicturePath(self.default_photo)

        item.setId(item.uuid())


class ChartConfigWidget(QgsLayoutItemBaseWidget):

    def __init__(self, parent, layout_object):
        super().__init__(parent, layout_object)
        label = LayoutGuiUtils.create_heading_label(QCoreApplication.translate('StdmItems', 'STDM Item Properties'))

        vl = QVBoxLayout()
        vl.setContentsMargins(0, 0, 0, 0)
        vl.addWidget(label)

        data_source_editor = ComposerChartConfigEditor(layout_object)
        vl.addWidget(data_source_editor)

        self.base_widget = LayoutGuiUtils.create_standard_item_widget(layout_object,
                                                                      QgsLayoutItemRegistry.LayoutPicture)

        for name in (
                'mSVGFrame', 'mRotationGroupBox', 'mSVGParamsGroupBox', 'mRadioSVG', 'mRadioRaster', 'mRasterFrame',
                'mPreviewGroupBox'):
            widget = self.base_widget.findChild(QWidget, name)
            if widget is not None:
                widget.setVisible(False)

        self.connectChildPanel(self.base_widget)
        vl.addWidget(self.base_widget)

        self.setLayout(vl)

    def setDockMode(self, dockMode):
        self.base_widget.setDockMode(dockMode)
        super().setDockMode(dockMode)


class StdmChartLayoutItemGuiMetadata(QgsLayoutItemAbstractGuiMetadata):

    def __init__(self):
        super().__init__(STDM_CHART_ITEM_TYPE, QCoreApplication.translate('StdmItems', 'STDM Chart'))
        self.default_photo = GuiUtils.get_icon_svg("chart-512.png")

    def creationIcon(self):  # pylint: disable=missing-docstring, no-self-use
        return GuiUtils.get_icon('chart.png')

    def createItemWidget(self, item):  # pylint: disable=missing-docstring, no-self-use
        return ChartConfigWidget(None, item)

    def newItemAddedToLayout(self, item):
        try:
            item.setMode(QgsLayoutItemPicture.FormatRaster)
        except AttributeError:
            pass

        item.setFrameEnabled(False)
        item.setResizeMode(QgsLayoutItemPicture.Zoom)

        if QFile.exists(self.default_photo):
            item.setPicturePath(self.default_photo)

        item.setId(item.uuid())


class QrConfigWidget(QgsLayoutItemBaseWidget):

    def __init__(self, parent, layout_object):
        super().__init__(parent, layout_object)
        label = LayoutGuiUtils.create_heading_label(QCoreApplication.translate('StdmItems', 'STDM Item Properties'))

        vl = QVBoxLayout()
        vl.setContentsMargins(0, 0, 0, 0)
        vl.addWidget(label)

        data_source_editor = ComposerQREditor(layout_object)
        vl.addWidget(data_source_editor)

        self.base_widget = LayoutGuiUtils.create_standard_item_widget(layout_object,
                                                                      QgsLayoutItemRegistry.LayoutPicture)

        for name in (
                'mSVGFrame', 'mRotationGroupBox', 'mSVGParamsGroupBox', 'mRadioSVG', 'mRadioRaster', 'mRasterFrame',
                'mPreviewGroupBox'):
            widget = self.base_widget.findChild(QWidget, name)
            if widget is not None:
                widget.setVisible(False)

        self.connectChildPanel(self.base_widget)
        vl.addWidget(self.base_widget)

        self.setLayout(vl)

    def setDockMode(self, dockMode):
        self.base_widget.setDockMode(dockMode)
        super().setDockMode(dockMode)


class StdmQrCodeLayoutItemGuiMetadata(QgsLayoutItemAbstractGuiMetadata):

    def __init__(self):
        super().__init__(STDM_QR_ITEM_TYPE, QCoreApplication.translate('StdmItems', 'QR Code'))
        self.default_photo = GuiUtils.get_icon_svg("qrcode_512.png")

    def creationIcon(self):  # pylint: disable=missing-docstring, no-self-use
        return GuiUtils.get_icon('qrcode.png')

    def createItemWidget(self, item):  # pylint: disable=missing-docstring, no-self-use
        return QrConfigWidget(None, item)

    def newItemAddedToLayout(self, item):
        try:
            item.setMode(QgsLayoutItemPicture.FormatRaster)
        except AttributeError:
            pass

        item.setFrameEnabled(False)
        item.setResizeMode(QgsLayoutItemPicture.ZoomResizeFrame)

        if QFile.exists(self.default_photo):
            item.setPicturePath(self.default_photo)

        item.setId(item.uuid())


class StdmCustomLayoutGuiItems:
    GUI_CLASSES = [StdmLineLayoutItemGuiMetadata,
                   StdmDataLabelLayoutItemGuiMetadata,
                   StdmTableLayoutItemGuiMetadata,
                   StdmMapLayoutItemGuiMetadata,
                   StdmPhotoLayoutItemGuiMetadata,
                   StdmChartLayoutItemGuiMetadata,
                   StdmQrCodeLayoutItemGuiMetadata]

    gui_metadata = []

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
