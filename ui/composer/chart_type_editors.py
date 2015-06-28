"""
/***************************************************************************
Name                 : Chart Type UI Editors
Description          : Implementation of chart type editors
Date                 : 17/April/2015
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
from collections import (
    OrderedDict
)

from PyQt4.QtGui import (
    QApplication,
    QColor,
    QGridLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QWidget
)

from qgis.gui import (
    QgsColorButtonV2
)

from stdm.data import (
    numeric_columns,
    table_column_names
)
from stdm.utils import (
    setComboCurrentIndexWithText
)

from .ui_chart_vertical_bar import Ui_VerticalBarGraphSettings

class DataSourceNotifier(object):
    """
    Base class that enables subclasses to receive changes when the data source
    changes.
    """
    def on_table_name_changed(self, table):
        raise NotImplementedError("Implement notifier in subclass")

class BarValueConfigWidget(QWidget):
    """
    Widget for editing y-value configurations.
    """
    def __init__(self, parent=None, value_field='', def_color='#2564e1',
                 legend_name=''):
        QWidget.__init__(self, parent)

        self._value_field = value_field

        #Insert controls for editing fill color and legend names
        self.lbl_fill_color = QLabel(self)
        self.lbl_fill_color.setText(QApplication.translate("ValueConfigWidget",
                                                      "Fill color"))
        self.fill_color_btn = QgsColorButtonV2(self,QApplication.translate("ValueConfigWidget",
                                                      "Select bar fill color"))
        self.fill_color_btn.setMaximumHeight(30)
        self.fill_color_btn.setMinimumHeight(30)
        self.fill_color_btn.setMinimumWidth(100)
        if QColor.isValidColor(def_color):
            default_color = QColor(def_color)
            self.fill_color_btn.setColor(default_color)

        self.lbl_legend_name = QLabel(self)
        self.lbl_legend_name.setText(QApplication.translate("ValueConfigWidget",
                                                      "Legend name"))
        self.txt_legend_name = QLineEdit(self)
        self.txt_legend_name.setMaxLength(50)
        self.txt_legend_name.setMinimumHeight(30)
        self.txt_legend_name.setText(legend_name)

        self.layout = QGridLayout(self)
        self.layout.addWidget(self.lbl_fill_color, 0, 0, 1, 1)
        self.layout.addWidget(self.fill_color_btn, 0, 1, 1, 1)
        self.layout.addWidget(self.lbl_legend_name, 1, 0, 1, 1)
        self.layout.addWidget(self.txt_legend_name, 1, 1, 1, 1)

    def value_field(self):
        """
        :return: Returns the value field used from the referenced table.
        :rtype: str
        """
        return self._value_field

    def set_value_field(self, value_field):
        """
        Set the value field used from the referenced table.
        :param value_field: Value field used from the referenced table.
        :type value_field: str
        """
        if value_field:
            self._value_field = value_field

    def configuration(self):
        """
        :return: BarValueConfiguration settings.
        :rtype: BarValueConfiguration
        """
        from stdm.composer import BarValueConfiguration

        bar_value_config = BarValueConfiguration()
        bar_value_config.set_value_field(self._value_field)
        bar_value_config.set_fill_color(self.fill_color_btn.color().name())
        bar_value_config.set_legend_name(self.txt_legend_name.text())

        return bar_value_config

    def set_configuration(self, config):
        pass

class VerticalBarGraphEditor(QWidget, DataSourceNotifier,
                             Ui_VerticalBarGraphSettings):
    def __init__(self, parent=None):
        QWidget.__init__(self,parent)

        self.setupUi(self)

        self._value_config_widgets = OrderedDict()

        #Connect signals
        self.btn_add_value_field.clicked.connect(self.on_add_value_config_widget)
        self.tb_value_config.tabCloseRequested.connect(self._on_tab_close_requested)
        self.btn_reset_value_fields.clicked.connect(self.clear)

    def on_table_name_changed(self, table):
        """
        Slot raised when table name changes so that the corresponding
        column names can be updated.
        :param table: Name of the current table
        :type table: str
        """
        self.cbo_value_field.clear()
        self.cbo_x_field.clear()

        numeric_cols = numeric_columns(table)
        x_cols = table_column_names(table)

        self.cbo_value_field.addItems(numeric_cols)
        self.cbo_x_field.addItems(x_cols)

    def configuration(self):
        """
        :return: VerticalBar configuration settings.
        :rtype: VerticalBarConfiguration
        """
        from stdm.composer import VerticalBarConfiguration

        vbar_config = VerticalBarConfiguration()
        vbar_config.set_x_label(self.txt_x_label.text())
        vbar_config.set_x_field(self.cbo_x_field.currentText())
        vbar_config.set_y_label(self.txt_y_label.text())

        #Set bar value configurations
        for cfg in self.bar_value_configurations():
            vbar_config.add_value_configuration(cfg)

        return vbar_config

    def set_configuration(self, configuration):
        setComboCurrentIndexWithText(self.cbo_x_field, configuration.x_field())
        self.txt_x_label.setText(configuration.x_label())
        self.txt_y_label.setText(configuration.y_label())

        #Set barvalue configurations
        for bar_cfg in configuration.value_configurations():
            self.add_value_configuration(bar_cfg)

    def bar_value_configurations(self):
        return [self.tb_value_config.widget(i).configuration()
                for i in range(self.tb_value_config.count())]

    def on_add_value_config_widget(self):
        """
        Slot raised to add a 'BarValueConfigWidget' widget for editing
        the configuration of a value field.
        """
        curr_value_field = self.cbo_value_field.currentText()

        self._add_value_config_widget(value_field=curr_value_field)

    def add_value_configuration(self, value_cfg):
        """
        Adds a value configuration widget and sets its attributes
        based on those of the 'BarValueConfiguration' object.
        """
        self._add_value_config_widget(value_field=value_cfg.value_field(),
                                      def_color=value_cfg.fill_color(),
                                      legend_name=value_cfg.legend_name())

    def _add_value_config_widget(self, **kwargs):
        curr_value_field = kwargs.get("value_field", "")

        if not curr_value_field:
            return

        if not curr_value_field in self._value_config_widgets:
            config_widget = BarValueConfigWidget(**kwargs)
            widg_idx = self.tb_value_config.addTab(config_widget, curr_value_field)
            self.tb_value_config.setCurrentIndex(widg_idx)

            self._value_config_widgets[curr_value_field] = config_widget

    def _on_tab_close_requested(self, idx):
        """
        Slot raised when the close button of the config tab widget has been
        clicked.
        :param idx: Index of the tab clicked.
        :type idx: int
        """
        status = self.remove_config_widget(idx)
        #QMessageBox.information(self,"Info",str(status))

    def remove_config_widget(self, idx):
        """
        Removes the configuration widget based on its position in the
        tab widget.
        :param idx: Position of configuration widget in tab widget
        :type idx: int
        :return: True if the configuration widget was successfully deleted.
        Otherwise False.
        """
        if idx <= self.tb_value_config.count() - 1:
            config_widget = self.tb_value_config.widget(idx)
            tab_title = self.tb_value_config.tabText(idx)
            del self._value_config_widgets[tab_title]
            self.tb_value_config.removeTab(idx)
            del config_widget

            return True

        return False

    def clear(self):
        """
        Removes all configuration widgets in the collection.
        """
        self.tb_value_config.clear()
        self._value_config_widgets = OrderedDict()