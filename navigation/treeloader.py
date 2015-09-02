"""
/***************************************************************************
Name                 : Tree Widget Loader
Description          : Loads KVP information into a tree widget
Date                 : 4/July/2013 
copyright            : (C) 2013 by John Gitau
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
from PyQt4.QtGui import QTreeWidgetItem, QIcon, QHeaderView


class TreeSummaryLoader(object):
    '''
    Load summary information in a dictionary into a tree widget.
    The class will iterate through the items and if the child items are of 
    type 'dict' then a child node will be created.
    '''

    def __init__(self, treewidget, rootTitle="Summary Information"):
        self.tree = treewidget
        self.items = []
        self.title = rootTitle
        self.separator = ": "
        self.rootResource = ":/plugins/stdm/images/icons/information.png"

    def setRootResource(self, resourcepath):
        '''
        Set the path of the image file to be used in the root item
        '''
        self.rootResource = resourcepath

    def setItems(self, treeItems):
        '''
        Set the collection to use to load items into the tree widget
        '''
        self.items = treeItems

    def addCollection(self, collection, title, rootResource):
        '''
        Add collection for inclusion into tree widget.
        Title and root resource are overridden from the ones specified in the constructor 
        there is only one item in the collection.
        '''
        if isinstance(collection, dict):
            prItem = self.buildParentItem(collection, title, rootResource)
            self.items.append(prItem)

    def setSeparator(self, sep):
        '''
        Specify a separator to use for column-value details
        '''
        self.separator = sep

    def display(self):
        '''
        Initialize top-level items
        '''
        if len(self.items) == 0:
            return

        self.tree.clear()

        # If there is only one item then set it as the root item
        if len(self.items) == 1:
            rootItem = self.items[0]

            # Set root font
            rtFont = rootItem.font(0)
            rtFont.setBold(True)
            rootItem.setFont(0, rtFont)

            # Add the tree item to the tree widget
            self.tree.addTopLevelItem(rootItem)
            rootItem.setExpanded(True)

        else:
            rootItem = QTreeWidgetItem(self.tree)
            rootItem.setText(0, self.title)
            rootItem.setIcon(0, QIcon(self.rootResource))

            # Set root font
            rtFont = rootItem.font(0)
            rtFont.setBold(True)
            rootItem.setFont(0, rtFont)

            rootItem.addChildren(self.items)
            rootItem.setExpanded(True)

        # Force the horizontal scrollbar to show
        self.tree.header().setResizeMode(QHeaderView.ResizeToContents)

    def _combine(self, column, value):
        '''
        Combine column and value using the specified separator
        '''
        return ("%s%s%s" % (column, self.separator, value))

    def buildParentItem(self, dcollection, title, rootresource):
        '''
        Builds tree widget items from a dictionary.
        '''
        rtItem = QTreeWidgetItem()
        rtItem.setText(0, title)
        rtItem.setIcon(0, QIcon(rootresource))

        topLevelItems = []

        for k, v in dcollection.iteritems():
            parentItem = QTreeWidgetItem()

            if isinstance(v, dict):
                parentItem.setText(0, k)

                for kc, vc in v.iteritems():
                    child = QTreeWidgetItem()
                    child.setText(0, self._combine(kc, vc))
                    parentItem.addChild(child)

            else:
                parentItem.setText(0, self._combine(k, v))

            topLevelItems.append(parentItem)

        rtItem.addChildren(topLevelItems)
        rtItem.setExpanded(True)

        return rtItem
