"""
/***************************************************************************
Name                 : Composer item formatters
Description          : Classes for formatting QgsComposerItems.
Date                 : 10/May/2014
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
from qgis.PyQt.QtCore import QRegExp, QFile
from qgis.PyQt.QtWidgets import (
    QApplication,
    QComboBox,
    QGroupBox,
    QCheckBox,
    QWidget,
    QLineEdit,
    QDoubleSpinBox,
    QScrollArea,
    QToolButton
)
from qgis.core import (
    Qgis,
    QgsLayoutItemMap,
    QgsLayoutItemPicture,
    QgsLayoutFrame,
    QgsLayoutTableColumn
)
from qgis.gui import (
    QgsCollapsibleGroupBoxBasic
)

from stdm.ui.composer.composer_chart_config import ComposerChartConfigEditor
from stdm.ui.composer.composer_symbol_editor import ComposerSymbolEditor
from stdm.ui.composer.photo_data_source import ComposerPhotoDataSourceEditor
from stdm.ui.composer.qr_code import ComposerQREditor
from stdm.ui.composer.table_data_source import ComposerTableDataSourceEditor
from stdm.utils.util import PLUGIN_DIR


class BaseComposerItemFormatter:
    """
    Defines the abstract interface for implementation by subclasses.
    """

    def apply(self, composerItem, composerWrapper, fromTemplate=False):
        """
        Subclasses to implement this method for formatting composer items.
        """
        raise NotImplementedError


class MapFormatter(BaseComposerItemFormatter):
    """
    Add widget for formatting spatial data sources.
    """

    def apply(self, templateMap, composerWrapper, fromTemplate=False):
        if not isinstance(templateMap, QgsLayoutItemMap):
            return

        if not fromTemplate:
            # Enable outline in map composer item
            frameWidth = 0.3
            templateMap.setFrameEnabled(True)
            templateMap.setFrameOutlineWidth(frameWidth)

            templateMap.setKeepLayerSet(True)

            # Enable the properties for the corresponding widget for the frame
            # Get the editor widget for the label
            mapEditor = composerWrapper.itemDock().widget()

            if mapEditor is not None:
                frameGP = mapEditor.findChild(QgsCollapsibleGroupBoxBasic, "mGridFrameGroupBox")
                if frameGP is not None:
                    frameGP.setCollapse(True)

                thicknessSpinBox = mapEditor.findChild(QDoubleSpinBox, "mGridFramePenSizeSpinBox")
                if thicknessSpinBox is not None:
                    thicknessSpinBox.setValue(frameWidth)

            # Create styling editor and it to the dock widget
            composerSymbolEditor = ComposerSymbolEditor(composerWrapper)
            stdmDock = composerWrapper.stdmItemDock()
            stdmDock.setWidget(composerSymbolEditor)

            # Add widget to the composer wrapper widget mapping collection
            composerWrapper.addWidgetMapping(templateMap.uuid(), composerSymbolEditor)

        # Set ID to match UUID
        templateMap.setId(templateMap.uuid())


class PhotoFormatter(BaseComposerItemFormatter):
    """
    Add widget for formatting composer picture items.
    """

    def __init__(self):
        self.default_photo = PLUGIN_DIR + "/images/icons/photo_512.png"
        self.has_frame = True
        self._item_editor_cls = ComposerPhotoDataSourceEditor



class TableFormatter(BaseComposerItemFormatter):
    """
    Add widget for formatting an attribute table item.
    """

    def apply(self, frame_item, composerWrapper, fromTemplate=False):

        frame_item.blockSignals(True)

        if not isinstance(frame_item, QgsLayoutFrame):
            return

        table_item = frame_item.multiFrame()
        # Get the table editor widget and configure widgets
        table_editor = composerWrapper.itemDock().widget()

        if table_editor is not None:
            self._configure_table_editor_properties(table_editor)

        if not fromTemplate:
            table_item.setComposerMap(None)
            text = '     Choose the data source of the table and ' \
                   'the link columns in the STDM item properties.'
            table_text = QApplication.translate('TabelFormatter', text)
            default_column = QgsLayoutTableColumn(table_text)

            table_item.setColumns([default_column])

            # Create data properties editor and add it to the dock widget
            table_data_source_editor = ComposerTableDataSourceEditor(composerWrapper, table_item)

            ############################################################################################
            table_data_source_editor.ref_table.cbo_ref_table.currentIndexChanged[str].connect(
                table_data_source_editor.set_table_vector_layer)

            if composerWrapper.current_ref_table_index == -1:
                layer_name = self._current_layer_name(table_editor)
                idx = table_data_source_editor.ref_table.cbo_ref_table.findText(layer_name)
                table_data_source_editor.ref_table.cbo_ref_table.setCurrentIndex(idx)

            ############################################################################################

            stdmDock = composerWrapper.stdmItemDock()
            stdmDock.setWidget(table_data_source_editor)

            # Add widget to the composer wrapper widget mapping collection
            composerWrapper.addWidgetMapping(frame_item.uuid(), table_data_source_editor)

            # Set ID to match UUID
            frame_item.setId(frame_item.uuid())

    def _configure_table_editor_properties(self, base_table_editor):
        qgis_version = Qgis.QGIS_VERSION_INT
        # Get scroll area first
        scroll_area = base_table_editor.findChild(QScrollArea, "scrollArea")

        if scroll_area is not None:

            contents_widget = scroll_area.widget()
            object_names = ['^mRefreshPushButton$']  ##, '^mLayerLabel$', '^mLayerComboBox$', ]

            for object_name in object_names:
                name_regex = QRegExp(object_name)
                for widget in contents_widget.findChildren(QWidget, name_regex):
                    widget.setVisible(False)

                # main_properties_groupbox = contents_widget.findChild(QGroupBox, "groupBox")
                # #Version 2.4
                # if qgis_version >= 20400 and qgis_version <= 20600:
                #     self._hide_filter_controls(main_properties_groupbox)

            # if qgis_version >= 20600:
            #     feature_filter_groupbox = contents_widget.findChild(QGroupBox, "groupBox_5")
            # if not feature_filter_groupbox is None:
            #     self._hide_filter_controls(feature_filter_groupbox)
            appearance_groupbox = contents_widget.findChild(QGroupBox, "groupBox_6")
            appearance_groupbox.setVisible(True)

    def _current_layer_name(self, base_table_editor):
        curr_text = ''
        scroll_area = base_table_editor.findChild(QScrollArea, "scrollArea")
        if scroll_area is not None:
            contents_widget = scroll_area.widget()
            object_names = ['^mLayerComboBox$']
            for object_name in object_names:
                name_regex = QRegExp(object_name)
                for widget in contents_widget.findChildren(QWidget, name_regex):
                    if isinstance(widget, QComboBox):
                        curr_text = widget.currentText()
                        break
        return curr_text

    def _hide_filter_controls(self, groupbox):
        # Filter options
        filter_chk = groupbox.findChild(QCheckBox, "mFeatureFilterCheckBox")
        if filter_chk is not None:
            # Enable filter option if not enabled
            if not filter_chk.isChecked():
                filter_chk.setChecked(True)
            filter_chk.setVisible(False)

        txt_filter = groupbox.findChild(QLineEdit, "mFeatureFilterEdit")
        if txt_filter is not None:
            txt_filter.setVisible(False)

        filter_btn = groupbox.findChild(QToolButton, "mFeatureFilterButton")
        if filter_btn is not None:
            filter_btn.setVisible(False)


class ChartFormatter(PhotoFormatter):
    """
    Add widget for formatting composer picture items.
    """

    def apply(self, chart_item, composerWrapper, fromTemplate=False):
        if not isinstance(chart_item, QgsLayoutItemPicture):
            return

        # Get the main picture editor widget and configure widgets
        picture_editor = composerWrapper.itemDock().widget()

        if not fromTemplate:
            # Disable outline in map composer item
            chart_item.setFrameEnabled(False)

            # Create data properties editor and it to the dock widget
            graph_config_editor = ComposerChartConfigEditor(composerWrapper)
            stdmDock = composerWrapper.stdmItemDock()
            stdmDock.setWidget(graph_config_editor)

            # Add widget to the composer wrapper widget mapping collection
            composerWrapper.addWidgetMapping(chart_item.uuid(), graph_config_editor)

        # Set default photo properties
        default_chart_pic = PLUGIN_DIR + "/images/icons/chart-512.png"
        if QFile.exists(default_chart_pic):
            chart_item.setPicturePath(default_chart_pic)

        # Set ID to match UUID
        chart_item.setId(chart_item.uuid())


class QRCodeFormatter(PhotoFormatter):
    """Add composer widget for editing QRCode properties"""

    def __init__(self):
        self.default_photo = PLUGIN_DIR + "/images/icons/qrcode_512.png"
        self.has_frame = False
        self._item_editor_cls = ComposerQREditor
