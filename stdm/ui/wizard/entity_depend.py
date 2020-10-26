# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : entity_depend  
Description          : show entities dependecies
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
from ui_entity_depend import Ui_dlgEntityDepend

from PyQt4.QtGui import(
        QDialog,
        QTreeWidgetItem,
        QApplication,
        QFont,
        QPixmap
)

from PyQt4.QtCore import *

class EntityDepend(QDialog, Ui_dlgEntityDepend):
    def __init__(self, parent, entity=None, dependencies=None):
        QDialog.__init__(self, parent)
        self.setupUi(self) 
        self.entity = entity
        self.dependencies = dependencies

        self.init_gui()

    def init_gui(self):
        self.btnCancel.clicked.connect(self.cancel_dlg)
        self.btnDelete.clicked.connect(self.delete_entity)
        self.qryLabel.setText(self.qryLabel.text() % self.entity.short_name)
        self.btnDelete.setStyleSheet('QPushButton {font-weight: bold; color: red;}')
        self.show_dependencies()

    def show_dependencies(self):
        nodes = []
        entities = self.create_entities_node(self.twEntityDepend, self.dependencies['entities'])
        views = self.create_views_node(self.twEntityDepend, self.dependencies['views'])
        nodes.append(entities)
        nodes.append(views)
        #self.twEntityDepend.insertTopLevelItems(0, views)
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

