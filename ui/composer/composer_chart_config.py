"""
/***************************************************************************
Name                 : ComposerGraphConfigEditor
Description          : Widget for specifying graph type and corresponding
                       properties, as well as the data source properties of
                       the linked tables.
Date                 : 15/April/2015
copyright            : (C) 2014 by UN-Habitat and implementing partners.
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
from PyQt4.QtGui import (
    QApplication,
    QWidget
)

from qgis.core import QgsComposerPicture

from stdm.utils import (
    setComboCurrentIndexWithItemData,
    setComboCurrentIndexWithText
)

from ..notification import (
    NotificationBar,
    ERROR
)

from .chart_type_register import ChartTypeUISettings
from .referenced_table_editor import LinkedTableProps
from .chart_type_editors import DataSourceNotifier
from .ui_composer_chart_config import Ui_ChartPropertiesEditor

class ComposerChartConfigEditor(QWidget, Ui_ChartPropertiesEditor):
    def __init__(self, composer_wrapper, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)

        self._composer_wrapper = composer_wrapper

        self._notif_bar = NotificationBar(self.vl_notification)

        self.cbo_chart_type.currentIndexChanged[int].connect(self._on_chart_type_changed)

        '''
        Register chartname to the positional index of the corresponding editor
        '''
        self._short_name_idx = {}

        #Add registered chart types
        self._load_chart_type_settings()

        #Load legend positions
        self._load_legend_positions()

        self.groupBox_2.setCollapsed(True)
        self.groupBox_2.collapsedStateChanged.connect(self._on_series_properties_collapsed)

        #Load fields if the data source has been specified
        ds_name = self._composer_wrapper.selectedDataSource()
        self.ref_table.load_data_source_fields(ds_name)

        #Load referenced table list
        self.ref_table.load_link_tables()

        #Connect signals
        self._composer_wrapper.dataSourceSelected.connect(self.ref_table.on_data_source_changed)
        self.ref_table.referenced_table_changed.connect(self.on_referenced_table_changed)

    def _load_legend_positions(self):
        from stdm.composer import legend_positions

        self.cbo_legend_pos.clear()
        for k,v in legend_positions.iteritems():
            self.cbo_legend_pos.addItem(k,v)

        #Select 'Automatic' option
        setComboCurrentIndexWithText(self.cbo_legend_pos,
            QApplication.translate("ChartConfiguration", "Automatic"))

    def _load_chart_type_settings(self):
        for cts in ChartTypeUISettings.registry:
            self.add_chart_type_setting(cts)

    def add_chart_type_setting(self, cts):
        """
        Adds a chart type and corresponding series properties editor to the
        collection.
        :param cts: Chart type setting containing a display name and
        corresponding editor.
        :type cts: ChartTypeUISettings
        """
        cts_obj = cts(self)

        widget_idx = self.series_type_container.addWidget(cts_obj.editor())
        self.cbo_chart_type.insertItem(widget_idx, cts_obj.icon(),
                                       cts_obj.title())

        #Register short_name index
        if cts_obj.short_name():
            self._short_name_idx[cts_obj.short_name()] = widget_idx

    def _on_series_properties_collapsed(self, state):
        """
        Slot to check whether the user has specified a chart type and collapse
         if none has been selected.
        :param state: True if group box is collapsed, false if not.
        :type state: bool
        """
        if not state and not self.cbo_chart_type.currentText():
            self._notif_bar.clear()
            msg = QApplication.translate("ComposerChartConfigEditor",
                                         "Please select a chart type from "
                                         "the drop down list below")
            self._notif_bar.insertWarningNotification(msg)

            self.groupBox_2.setCollapsed(True)

    def _on_chart_type_changed(self, index):
        """
        Slot raised when the chart type selection changes.
        :param index: Index of the chart type in the combobox
        :type index: int
        """
        if index >= 0:
            self.series_type_container.setCurrentIndex(index)

    def on_referenced_table_changed(self, table):
        """
        Slot raised when the referenced table name changes. This notifies
        series properties editors of the need to update the fields.
        :param table: Current table name.
        :type table: str
        """
        curr_editor = self.series_type_container.currentWidget()
        if not curr_editor is None:
            if isinstance(curr_editor, DataSourceNotifier):
                curr_editor.on_table_name_changed(table)

    def configuration(self):
        #Return chart configuration settings
        config = None

        curr_editor = self.series_type_container.currentWidget()
        if not curr_editor is None:
            try:
                config = curr_editor.configuration()
            except AttributeError:
                raise AttributeError(QApplication.translate("ComposerChartConfigEditor",
                                         "Series editor does not contain a method for "
                                         "returning a ChartConfigurationSettings object."))

        else:
            raise Exception(QApplication.translate("ComposerChartConfigEditor",
                                         "No series editor found."))

        if not config is None:
            ref_table_config = self.ref_table.properties()
            config.extract_from_linked_table_properties(ref_table_config)
            config.set_insert_legend(self.gb_legend.isChecked())
            config.set_title(self.txt_plot_title.text())
            config.set_legend_position(self.cbo_legend_pos.itemData
                                       (self.cbo_legend_pos.currentIndex()))

        return config

    def composer_item(self):
        return self._picture_item

    def _set_graph_properties(self, config):
        #Set the general graph properties from the config object
        self.txt_plot_title.setText(config.title())
        self.gb_legend.setChecked(config.insert_legend())
        setComboCurrentIndexWithItemData(self.cbo_legend_pos,
                                         config.legend_position())

    def set_configuration(self, configuration):
        #Load configuration settings
        short_name = configuration.plot_type

        if short_name:
            if short_name in self._short_name_idx:
                plot_type_idx = self._short_name_idx[short_name]
                self.cbo_chart_type.setCurrentIndex(plot_type_idx)

                #Set linked table properties
                self.ref_table.set_properties(configuration.linked_table_props())

                #Set series editor properties
                curr_editor = self.series_type_container.currentWidget()
                if not curr_editor is None:
                    try:
                        curr_editor.set_configuration(configuration)
                        self._set_graph_properties(configuration)

                    except AttributeError:
                        msg = QApplication.translate("ComposerChartConfigEditor",
                        "Configuration could not be set for series editor.")
                        self._notif_bar.clear()
                        self._notif_bar.insertErrorNotification(msg)

        else:
            msg = QApplication.translate("ComposerChartConfigEditor",
                        "Configuration failed to load. Plot type cannot be determined.")
            self._notif_bar.clear()
            self._notif_bar.insertErrorNotification(msg)
