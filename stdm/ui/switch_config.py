"""
/***************************************************************************
Name                 : SwitchConfiguration
Description          : Dialog for switching configurations
Date                 : 07/07/2023
copyright            : (C) 2023 by UN-Habitat and implementing partners.
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
import os
import glob
import json

from qgis.PyQt import uic
from qgis.PyQt.QtCore import (
    QDir
)

from qgis.PyQt.QtWidgets import (
    QDialog,
    QTreeWidgetItem,
    QMessageBox
)

from stdm.ui.switch_config_handler import SwitchConfigHandler

from stdm.ui.gui_utils import GuiUtils

WIDGET, BASE = uic.loadUiType(
    GuiUtils.get_ui_file_path('ui_switch_config.ui')
)

class SwitchConfiguration(WIDGET, BASE):
    def __init__(self, iface):
        QDialog.__init__(self, iface.mainWindow())
        self.setupUi(self)
        self.setWindowTitle("Switch Configuration")
        self.iface = iface
        self._current_config_name = ''
        self._config_store = f'{QDir.homePath()}/.stdm/configurations'
        self.switch_handler = SwitchConfigHandler()

        self.btnSwitch.setEnabled(False)
        self.lblDBName.setText('')

        self.connect_signals()
        self.read_configs(self._config_store)

    def connect_signals(self):
        self.btnSwitch.clicked.connect(self.on_switch_config)
        self.btnClose.clicked.connect(self.close_window)
        self.cbConfigs.currentTextChanged.connect(self.on_config_changed)

    def on_switch_config(self):
        info = (
               f'Please note, after switching the configuration,'
               f'the system will log you off for the changes to take effect.'
        )
        self.show_message(info, QMessageBox.Information)
        if self.switch_handler.switch_config():
            self.done(1)
        else:
            msg = self.tr(f'Switch aborted.')
            self.show_message(msg, QMessageBox.Critical)

    def close_window(self):
        self.done(0)

    def on_config_changed(self, text: str):
        self._current_config_name = text
        config_store_filepath = f'{self._config_store}/{text}'
        if self.show_config_details(config_store_filepath):
            self.btnSwitch.setEnabled(True)

    def read_configs(self, config_store: str):
        dir = QDir(config_store)
        if not dir.exists():
            return

        # Get all configurations but not the active one.
        configs = [d for d in os.listdir(config_store) 
                   if os.path.isdir(os.path.join(config_store, d)) and d != self.switch_handler.active_config_name]
        self.cbConfigs.addItems(configs)

    def show_config_details(self, config_filepath: str) ->bool:
        store_folder = os.path.join(config_filepath, '*.json')
        json_files = glob.glob(store_folder)

        if len(json_files) == 0:
            msg = self.tr("Missing a valid backup log file.")
            return False

        self.config_log_file = json_files[0]

        if self.switch_handler.read_config_info_file(self.config_log_file):
            self._show_config_info()
            self.btnSwitch.setEnabled(True)
        else:
            msg = f'Error reading config file.'
            self.show_message(msg, QMessageBox.Critical)
    
    def _show_config_info(self):
        self.lblDBName.setText(self.switch_handler.db_name)
        self._display_profiles(self.switch_handler.profiles)

    def _display_profiles(self, profiles: list):
        self.twProfiles.clear()
        for profile in profiles:
            profile_item = QTreeWidgetItem()
            profile_item.setText(0, profile['name'])
            profile_item.setIcon(0, GuiUtils.get_icon("folder.png"))

            entity_node = QTreeWidgetItem()
            entity_node.setText(0, "Entities")
            profile_item.addChild(entity_node)
            entity_node.addChildren(self._make_tree_items(profile['entities'], "Table02.png"))
            
            templates = self._make_tree_items(profile['templates'], "record02.png")
            if len(templates) > 0:
                template_node = QTreeWidgetItem()
                template_node.setText(0, "Templates")
                profile_item.addChild(template_node)
                template_node.addChildren(templates)

            self.twProfiles.insertTopLevelItem(0, profile_item)

    def _make_tree_items(self, node_names: list[str], icon_filename: str) ->list[QTreeWidgetItem]:
        tree_items = []
        for node_name in node_names:
            tree_item = QTreeWidgetItem()
            tree_item.setText(0, node_name)
            tree_item.setIcon(0, GuiUtils.get_icon(icon_filename))
            tree_items.append(tree_item)
        return tree_items

    def show_message(self, msg: str, icon_type):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("STDM")
        msg_box.setText(msg)
        msg_box.setIcon(icon_type)
        msg_box.exec_()


