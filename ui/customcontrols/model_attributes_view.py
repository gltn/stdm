"""
/***************************************************************************
Name                 : Model Attributes ListView
Description          : Custom QListView implementation that displays checkable
                       model attributes.
Date                 : 22/May/2014
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
from collections import OrderedDict

from PyQt4.QtGui import (
    QListView,
    QStandardItemModel,
    QStandardItem
)
from PyQt4.QtCore import Qt

__all__ = ["ModelAtrributesView"]


class ModelAtrributesView(QListView):
    """
    Custom QListView implementation that displays checkable model attributes.
    """

    def __init__(self, parent=None, data_model=None):
        QListView.__init__(self, parent)

        self._data_model = data_model
        self._selected_display_mapping = OrderedDict()
        self._model_display_mapping = OrderedDict()
        self._attr_model = QStandardItemModel(self)

    def data_model(self):
        """
        Returns the data model instance.
        :rtype : data_model
        """
        return self._data_model

    def set_data_model(self, data_model):
        """
        Sets the data model. Should be a callable class rather than the class.
        instance.
        :param data_model:
        """
        if callable(data_model):
            self._data_model = data_model

        else:
            self._data_model = data_model.__class__

    def model_display_mapping(self):
        """
        Returns the column name and display name collection.
        :rtype : OrderedDict
        """
        return self._model_display_mapping

    def set_model_display_mapping(self, data_mapping):
        """
        Sets the mapping dictionary for the table object
        :param data_mapping:
        """
        if data_mapping is not None:
            self._model_display_mapping = data_mapping

    def load(self, sort=False):
        """
        Load the model's attributes into the list view.
        :param sort:
        """
        if self._data_model is None:
            return

        try:
            self._load_attrs(self._data_model.displayMapping(), sort)
        except AttributeError:
            # Ignore error if model does not contain the displayMapping static
            # method
            pass

    def load_mapping(self, mapping, sort=False):
        """
        Load collection containing column name and corresponding display name.
        :param mapping:
        :param sort:
        """
        self._model_display_mapping = mapping

        self._load_attrs(mapping, sort)

    def sort(self):
        """
        Sorts display name in ascending order.
        """
        self._attr_model.sort(0)

    def _load_attrs(self, attr_mapping, sort=False):
        """
        Loads display mapping into the list view.
        Specify to sort display names in ascending order once items have been
        added to the model.
        """
        self._attr_model.clear()
        self._attr_model.setColumnCount(2)

        for attr_name, display_name in attr_mapping.iteritems():
            # Exclude row ID in the list, other unique identifier attributes in
            # the model can be used
            if attr_name is not "id":
                display_name_item = QStandardItem(display_name)
                display_name_item.setCheckable(True)
                attr_name_item = QStandardItem(attr_name)

                self._attr_model.appendRow([display_name_item, attr_name_item])

        self.setModel(self._attr_model)

        if sort:
            self._attr_model.sort(0)

    def selected_mappings(self):
        """
        Return a dictionary of field names and their corresponding display
        values.
        """
        selected_attrs = {}

        for i in range(self._attr_model.rowCount()):
            display_name_item = self._attr_model.item(i, 0)

            if display_name_item.checkState() == Qt.Checked:
                attr_name_item = self._attr_model.item(i, 1)
                selected_attrs[attr_name_item.text()] \
                    = display_name_item.text()

        return selected_attrs
