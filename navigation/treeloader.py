"""
/***************************************************************************
Name                 : Tree Widget Loader
Description          : Loads KVP information into a tree widget
Date                 : 4/July/2013
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
from PyQt4.QtGui import QTreeWidgetItem, QIcon, QHeaderView


class TreeSummaryLoader(object):
    """
    Load summary information in a dictionary into a tree widget.
    The class will iterate through the items and if the child items are of
    type 'dict' then a child node will be created.
    """

    def __init__(self, tree_widget, root_title="Summary Information"):
        self._tree = tree_widget
        self._items = []
        self._title = root_title
        self._separator = ": "
        self._root_resource = ":/plugins/stdm/images/icons/information.png"

    def set_root_resource(self, resource_path):
        """
        Set the path of the image file to be used in the root item
        :param resource_path:
        """
        self._root_resource = resource_path

    def set_items(self, tree_items):
        """
        Set the collection to use to load items into the tree widget
        :param tree_items:
        """
        self._items = tree_items

    def add_collection(self, collection, title, root_resource):
        """
        Add collection for inclusion into tree widget.
        Title and root resource are overridden from the ones specified in
        the constructor there is only one item in the collection.
        :param collection:
        :param title:
        :param root_resource:
        """
        if isinstance(collection, dict):
            pr_item = self.build_parent_item(collection, title, root_resource)
            self._items.append(pr_item)

    def set_separator(self, sep):
        """
        Specify a separator to use for column-value details
        :param sep:
        """
        self._separator = sep

    def display(self):
        """
        Initialize top-level items
        """
        if len(self._items) == 0:
            return

        self._tree.clear()

        # If there is only one item then set it as the root item
        if len(self._items) == 1:
            root_item = self._items[0]

            # Set root font
            rt_font = root_item.font(0)
            rt_font.setBold(True)
            root_item.setFont(0, rt_font)

            # Add the tree item to the tree widget
            self._tree.addTopLevelItem(root_item)
            root_item.setExpanded(True)

        else:
            root_item = QTreeWidgetItem(self._tree)
            root_item.setText(0, self._title)
            root_item.setIcon(0, QIcon(self._root_resource))

            # Set root font
            rt_font = root_item.font(0)
            rt_font.setBold(True)
            root_item.setFont(0, rt_font)

            root_item.addChildren(self._items)
            root_item.setExpanded(True)

        # Force the horizontal scrollbar to show
        self._tree.header().setResizeMode(QHeaderView.ResizeToContents)

    def _combine(self, column, value):
        """
        Combine column and value using the specified separator
        :rtype : str
        :param column:
        :param value:
        """
        return "%s%s%s" % (column, self._separator, value)

    def build_parent_item(self, d_collection, title, root_resource):
        """
        Builds tree widget items from a dictionary.
        :rtype : QTreeWidgetItem
        :param d_collection:
        :param title:
        :param root_resource:
        """
        rt_item = QTreeWidgetItem()
        rt_item.setText(0, title)
        rt_item.setIcon(0, QIcon(root_resource))

        top_level_items = []

        for k, v in d_collection.iteritems():
            parent_item = QTreeWidgetItem()

            if isinstance(v, dict):
                parent_item.setText(0, k)

                for kc, vc in v.iteritems():
                    child = QTreeWidgetItem()
                    child.setText(0, self._combine(kc, vc))
                    parent_item.addChild(child)

            else:
                parent_item.setText(0, self._combine(k, v))

            top_level_items.append(parent_item)

        rt_item.addChildren(top_level_items)
        rt_item.setExpanded(True)

        return rt_item
