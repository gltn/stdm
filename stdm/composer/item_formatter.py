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
from qgis.PyQt.QtCore import QRegExp
from qgis.PyQt.QtWidgets import (
    QApplication,
    QComboBox,
    QGroupBox,
    QCheckBox,
    QWidget,
    QLineEdit,
    QScrollArea,
    QToolButton
)
from qgis.core import (
    Qgis,
    QgsLayoutFrame,
    QgsLayoutTableColumn
)

from stdm.ui.composer.table_data_source import ComposerTableDataSourceEditor


class BaseComposerItemFormatter:
    """
    Defines the abstract interface for implementation by subclasses.
    """

    def apply(self, composerItem, composerWrapper, fromTemplate=False):
        """
        Subclasses to implement this method for formatting composer items.
        """
        raise NotImplementedError


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
