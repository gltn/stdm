# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : column_depend
Description          : show column dependecies
Date                 : 01/May/2016
copyright            : (C) 2015 by UN-Habitat and implementing partners.
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
from qgis.PyQt.QtGui import (
    QFont
)
from qgis.PyQt.QtWidgets import (
    QDialog,
    QTreeWidgetItem,
    QApplication,
)

from stdm.ui.gui_utils import GuiUtils

WIDGET, BASE = uic.loadUiType(
    GuiUtils.get_ui_file_path('wizard/ui_column_depend.ui'))


class ColumnDepend(WIDGET, BASE):
    def __init__(self, parent, column=None, dependencies=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.label.setPixmap(GuiUtils.get_icon_pixmap('warning_large.png'))

        self.column = column
        self.dependencies = dependencies

        self.init_gui()

    def init_gui(self):
        self.btnCancel.clicked.connect(self.cancel_dlg)
        self.btnDelete.clicked.connect(self.delete_entity)
        msg = "The following items depend on the '{}' column;\n "\
              " deleting it might affect the data stored in these dependent\n "\
              " objects and in some cases, might also lead to their deletion.\n "\
              " Click 'Delete column' to proceed.\n".format(self.column.name)                               
        self.qryLabel.setText(msg);
        self.btnDelete.setStyleSheet('QPushButton {font-weight: bold; color: red;}')
        self.show_dependencies()

    def show_dependencies(self):
        nodes = []
        entities = self.create_entities_node(self.twEntityDepend, self.dependencies['entities'])
        views = self.create_views_node(self.twEntityDepend, self.dependencies['views'])
        nodes.append(entities)
        nodes.append(views)
        # self.twEntityDepend.insertTopLevelItems(0, views)
        self.twEntityDepend.expandAll()

    def create_root_node(self, name):
        root = QTreeWidgetItem(self.twEntityDepend, 0)
        root.setText(0, name)
        return root

    def title_font(self):
        font = QFont('Seqoe UI', 8, QFont.Bold)
        return font

    def create_entities_node(self, root_node, entities):
        children = []
        title_node = QTreeWidgetItem(root_node, 0)
        title_node.setText(0, QApplication.translate("EntityDependencies", "Entities"))
        title_node.setFont(0, self.title_font())
        for entity in entities:
            node = QTreeWidgetItem(title_node, 0)
            node.setText(0, entity)
            children.append(node)
        return children

    def create_views_node(self, root_node, views):
        children = []
        title_node = QTreeWidgetItem(root_node, 0)
        title_node.setText(0, QApplication.translate("EntityDependencies", "Views"))
        title_node.setFont(0, self.title_font())
        for view in views:
            node = QTreeWidgetItem(title_node, 0)
            node.setText(0, view)
            children.append(node)
        return children

    def cancel_dlg(self):
        self.done(0)

    def delete_entity(self):
        self.done(1)
