"""
/***************************************************************************
Name                 : GenericDelegate
Description          : A delegate class used in tables.

Date                 : 04/June/2018
copyright            : (C) 2018 by UN-Habitat and implementing partners.
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
from qgis.PyQt.QtCore import (
    Qt,
    QTimer
)

from qgis.PyQt.QtGui import QStandardItem

from qgis.PyQt.QtWidgets import (
    QItemDelegate,
    QComboBox,
    QDoubleSpinBox,
    QAbstractItemDelegate
)

class GenericDelegate(QItemDelegate):
    """
    It is a combobox delegate embedded in STR Type column.
    """
    def __init__(self, data, options, parent=None):
        """
        Initializes STRTypeDelegate and QItemDelegate.
        :param spatial_unit: The current spatial unit.
        :param type: Object
        :param parent: The parent of the item delegate.
        :type parent: QWidget
        """
        QItemDelegate.__init__(self, parent)
        self.data = data
        self.options = options

        self._view = parent


    def createEditor(self, parent, option, index):
        """
        Creates the combobox inside a parent.
        :param parent: The container of the combobox
        :type parent: QWidget
        :param option: QStyleOptionViewItem class is used to describe the
        parameters used to draw an item in a view widget.
        :type option: Object
        :param index: The index where the combobox
         will be added.
        :type index: QModelIndex
        :return: The combobox
        :rtype: QComboBox
        """
        widget = None
        if self.options['type'] == 'combobox':
            widget = self.create_combobox(parent, index)
        elif self.options['type'] == 'double_spinbox':
            widget = self.create_double_spinbox(parent, index)
        return widget

    def create_combobox(self, parent, index):
        """
        Creates combobox.
        :param parent: The parent widget.
        :type parent: QWidget
        :param index: The index.
        :type index: QModelIndex
        :return: The combobox
        :rtype: QComboBox
        """
        combo = QComboBox(parent)
        combo.setObjectName(str(index.row()))
        editor = combo
        editor.activated.connect(
            lambda index, editor=editor: self._view.commitData(editor))
        editor.activated.connect(
            lambda index, editor=editor: self._view.closeEditor(
                editor, QAbstractItemDelegate.NoHint)
        )
        QTimer.singleShot(10, editor.showPopup)
        return combo

    def create_double_spinbox(self, parent, index):
        """
        Creates double spinbox.
        :param parent: The parent widget.
        :type parent: QWidget
        :param index: The index.
        :type index: QModelIndex
        :return: The double spinbox
        :rtype: QDoubleSpinBox
        """
        spinbox = QDoubleSpinBox(parent)
        spinbox.setObjectName(str(index.row()))

        return spinbox

    def setEditorData(self, widget, index):
        """
        Set data to the Combobox.
        :param comboBox: The STR Type combobox
        :type comboBox: QCombobox
        :param index: The model index
        :type index: QModelIndex
        """
        if self.options['type'] == 'combobox':
            if widget.count() > 0:
                return
            widget.insertItem(0, " ")
                #, len(self.str_type_set_data())
            for id, text in self.data.iteritems():
                widget.addItem(text, id)

            list_item_index = None
            if not index.model() is None:
                list_item_index = index.model().data(index, Qt.DisplayRole)
            if list_item_index is not None and \
                    not isinstance(list_item_index, str):

                value = list_item_index.toInt()
                widget.blockSignals(True)
                widget.setCurrentIndex(value[0])
                widget.blockSignals(False)

    def setModelData(self, editor, model, index):
        """
        Gets data from the editor widget and stores
        it in the specified model at the item index.
        :param editor: combobox
        :type editor: QComboBox
        :param model: QModel
        :type model: QModel
        :param index: The index of the data
        to be inserted.
        :type index: QModelIndex
        """
        if self.options['type'] == 'combobox':
            value = editor.currentIndex()
            data = editor.itemData(editor.currentIndex())

            separator_item = QStandardItem(value)
            model.setItem(index.row(), index.column(), separator_item)
            separator_item.setData(data)
            model.setData(
                index,
                editor.itemData(value, Qt.DisplayRole)
            )

    def updateEditorGeometry(self, editor, option, index):
        """
        Updates the editor for the item specified
        by index according to the style option given.
        :param editor: STR Type combobox
        :type editor: QCombobox
        :param option: style options
        :type option: QStyle
        :param index: index of the combobox item
        :type index: QModelIndex
        """
        editor.setGeometry(option.rect)
