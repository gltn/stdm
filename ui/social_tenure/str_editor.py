# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : STR Editor
Description          : GUI classes for Social tenure editor.
Date                 : 10/November/2016
copyright            : (C) 2016 by UN-Habitat and implementing partners.
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

from qgis.utils import (
    iface
)
from PyQt4.QtCore import (
    pyqtSignal,
    QTimer
)

from PyQt4.QtGui import (
    QIcon,
    QStandardItemModel,
    QStandardItem,
    QTreeView,
    QApplication,
    QDialog,
    QAbstractItemView,
    QWidget,
    QMessageBox,
    QDialogButtonBox,
    QItemSelectionModel,
    QVBoxLayout,
    QDoubleSpinBox
)

from sqlalchemy import (
    func
)
from stdm.settings import current_profile
from stdm.ui.foreign_key_mapper import ForeignKeyMapper
from stdm.ui.notification import NotificationBar
from ui_str_editor import Ui_STREditor
from str_components import (
    Party,
    SpatialUnit,
    STRType,
    SupportingDocuments,
    ValidityPeriod
)
from stdm.utils.util import (
    format_name
)
from str_data import STRDataStore, STRDBHandler


class InitSTREditor(QDialog, Ui_STREditor):
    """
    Initializes the STR Editor by inheriting the UI of the STREditor. 
    """
    party_init = pyqtSignal()
    spatial_unit_init = pyqtSignal()
    validity_init = pyqtSignal()
    docs_init = pyqtSignal()
    str_type_updated = pyqtSignal()
    shareUpdated = pyqtSignal(list, QDoubleSpinBox)
    shareUpdatedOnZero = pyqtSignal(float)

    def __init__(self):
        """
        Initializes the STR editor.
        """
        QDialog.__init__(self, iface.mainWindow())
        self.setupUi(self)
        self.iface = iface
        self.str_number = 0
        self.data_store = OrderedDict()
        self.party_item_index = None
        self._init_tree_view()
        self.supporting_doc_component = None
        self.str_items = {}
        self.add_str_tree_node()
        self.party_count = OrderedDict()
        self.current_profile = current_profile()
        self.social_tenure = self.current_profile.social_tenure

        self.parties = self.social_tenure.parties

        if len(self.parties) > 0:
            self.party = self.parties[0]
        else:
            self.party = None

        self.spatial_unit = self.social_tenure.spatial_unit
        self.party_component = None
        self.str_model = None
        self.str_doc_model = None
        self.spatial_unit_component = None
        self.validity_period_component = None

        self.str_type_combo_connected = []
        self.share_spinbox_connected = []
        self.parties = self.social_tenure.parties

        self.str_type_component = None

        QTimer.singleShot(22, self.init_party_component)

        self.copied_party_row = OrderedDict()
        self._init_str_editor()

    def _init_str_editor(self):
        """
        Initializes the GUI of the STR editor.
        """
        self._init_notification()
        self.splitter.isCollapsible(False)
        self.splitter.setSizes([220, 550])
        self.splitter.setChildrenCollapsible(False)

        self.buttonBox.button(
            QDialogButtonBox.Save
        ).setEnabled(False)

    def _init_notification(self):
        """
        Initializes the notification object and
        connects signals and slot that toggles
        top description and the notification bar.
        """
        self.notice = NotificationBar(
            self.str_notification
        )
        self.notice.userClosed.connect(
            lambda: self.top_description_visibility(True)
        )
        self.notice.timer.timeout.connect(
            lambda: self.top_description_visibility(True)
        )
        self.notice.onClear.connect(
            lambda: self.top_description_visibility(True)
        )
        self.notice.onShow.connect(
            lambda: self.top_description_visibility(False)
        )

    def _init_tree_view(self):
        """
        Initializes the tree view and model
        and adds it into the left scrollArea.
        """
        self.tree_view = QTreeView()
        self.tree_view_model = QStandardItemModel()
        self.tree_view.setModel(self.tree_view_model)
        self.scrollArea.setWidget(self.tree_view)
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setAlternatingRowColors(True)

        self.tree_view.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )
        self.tree_view.setStyleSheet(
            '''
            QTreeView:!active {
                selection-background-color: #72a6d9;
            }
            '''
        )
        self.view_selection = self.tree_view.selectionModel()

    def _party_signals(self):
        """
        Connects party and str_type
        related slots and signals.
        """
        self.party_component.party_fk_mapper.beforeEntityAdded.connect(
            lambda model: self.set_party_data(model)
        )
        self.party_component.party_fk_mapper.afterEntityAdded.connect(
            lambda model, row_number: self.set_str_type_data(
                0, model.id, row_number
            )
        )
        self.party_component.party_fk_mapper.deletedRows.connect(
            self.remove_party_str_row_model
        )

    def remove_party_str_row_model(self, row_numbers):
        """
        Removes party and str_type row from the data store.
        :param row_numbers: The row numbers of removed row.
        :type row_numbers: List
        """
        current_store = self.current_data_store()
        for row_number in row_numbers:
            party_keys = current_store.party.keys()

            try:
                removed_key = party_keys[row_number]
                del current_store.party[removed_key]
                del current_store.str_type[removed_key]

            except IndexError:
                pass

        self.str_type_component.remove_str_type_row(
            row_numbers
        )

        self.reset_share_spinboxes(current_store)
        self.validate_str_type_length(current_store, self.current_item())

    def top_description_visibility(self, set_visible):
        """
        Sets the visibility of top description.
        :param set_visible: A boolean that shows or
        hides top description.
        :type set_visible:
        """
        if set_visible:
            self.top_description.show()
        else:
            self.top_description.hide()

    def init_party_component(self, party=None):
        """
        Initializes the party component.
        :param party: Party entity object.
        If party is none, the default party loads.
        :type party: Object
        """
        if self.party_component is not None:
            return

        self.party_component = Party(
            party,
            self.componentPage2,
            self.party_layout,
            self.notice
        )

        self.str_model, self.str_doc_model = \
            self.party_component.str_doc_models()
        self._party_signals()
        self.party_component.party_fk_mapper.entity_combo. \
            currentIndexChanged.connect(
            self.switch_entity
        )

        self.party_init.emit()

    def init_str_type_component(self, party=None):
        """
        Initializes the str type component.
        :param party: Party entity object.
        If party is none, the default party loads.
        :param party: The party entity
        :type party: Entity
        """
        if self.str_type_component is not None:
            return
        self.str_type_component = STRType(
            self.str_type_widget,
            self.str_type_box,
            self.notice,
            party
        )

    def init_spatial_unit_component(self):
        """
        Initializes the spatial unit component.
        """
        if self.spatial_unit_component is not None:
            return
        self.spatial_unit_component = SpatialUnit(
            self.spatial_unit_box,
            self.mirror_map,
            self.notice
        )
        self.spatial_unit_signals()
        self.spatial_unit_init.emit()

    def init_supporting_documents(self):
        """
        Initialize the supporting documents component.
        """
        if self.supporting_doc_component is not None:
            return
        self.supporting_doc_component = SupportingDocuments(
            self.supporting_doc_box,
            self.doc_type_cbo,
            self.add_documents_btn,
            self.notice
        )
        self.supporting_doc_component.add_documents_btn.clicked.connect(
            self.supporting_doc_component.on_upload_document
        )
        self.set_str_doc_models()
        self.docs_init.emit()

    def init_validity_period_component(self):
        """
        Initialize the validity period component.
        """
        if self.validity_period_component is not None:
            return
        self.validity_period_component = ValidityPeriod(self)
        self.validity_period_signals()
        self.validity_init.emit()

    def init_str_type_signal(self, data_store, party_id, str_number):
        """
        Connects str type combobox signals to a slot.
        :param data_store: Current data store
        :type data_store: Dictionary
        :param party_id: The added party model id.
        :type party_id: String
        """
        if self.str_type_component is None:
            return
        # gets all the comboboxes including the ones in other pages.
        str_type_combos = self.str_type_component.str_type_combobox()
        spinboxes = self.str_type_component.ownership_share()
        for spinbox in spinboxes:
            if spinbox not in self.share_spinbox_connected:
                first_name = spinbox.objectName()
                spinbox.setObjectName(
                    '{}_{}_{}'.format(str_number, party_id, first_name)
                )

                spinbox.valueChanged.connect(self.update_spinbox)
                self.share_spinbox_connected.append(spinbox)

        self.shareUpdated.connect(self.update_ownership_share_data)
        self.shareUpdated.connect(self.update_spinbox_when_zero)
        self.shareUpdatedOnZero.connect(self.update_ownership_share_data)
        for str_type_combo in str_type_combos:
            # connect comboboxes that are only newly added
            if str_type_combo not in self.str_type_combo_connected:
                str_type_combo.currentIndexChanged.connect(
                    lambda index: self.update_str_type_data(
                        index, data_store, party_id
                    )
                )
                self.str_type_combo_connected.append(str_type_combo)

    def reset_share_spinboxes(self, data_store):
        """
        Resets the share spinboxes value to have equal value.
        This method is used when a row is deleted,
        and new row is added.
        :param data_store: The current data store
        :type data_store: Object
        """
        row_count = len(data_store.party)
        spinboxes = self.str_type_component.ownership_share()
        for spinbox in spinboxes:
            if spinbox in self.share_spinbox_connected:
                str_number, party_id, current_row = \
                    self._extract_from_object_name(spinbox)

                self.blockSignals(True)
                spinbox.setValue(100.00 / row_count)
                self.blockSignals(False)
                data_store.share[party_id] = 100.00 / row_count

    def init_share_spinboxes(self, data_store):
        """
        Initialize the share spinboxes by setting equal
        value to all spinboxes or by picking values
        from the data store.
        :param data_store: The current data store.
        :type data_store: Object
        """
        row_count = len(data_store.party)
        spinboxes = self.str_type_component.ownership_share()
        for spinbox in spinboxes:
            if spinbox in self.share_spinbox_connected:
                str_number, party_id, current_row = \
                    self._extract_from_object_name(spinbox)

                if party_id in data_store.share.keys():
                    self.blockSignals(True)
                    if data_store.share[party_id] is None:
                        spinbox.setValue(100.00)
                    else:
                        spinbox.setValue(data_store.share[party_id])
                    self.blockSignals(False)

                else:
                    self.blockSignals(True)
                    spinbox.setValue(100.00 / row_count)
                    self.blockSignals(False)
                    data_store.share[party_id] = 100.00 / row_count

    def execute_spinbox_update(self, spinboxes, current_spinbox):
        """
        Update other spinbox values based on the current spinbox.
        :param spinboxes: All spinbox in the table.
        :type spinboxes: List
        :param current_spinbox: The current spinbox with value change.
        :type current_spinbox: QDoubleSpinBox
        :return: The next spinbox with value that will change
        :rtype: QDoubleSpinBox
        """
        str_number, party_id, current_row = \
            self._extract_from_object_name(current_spinbox)

        if current_row is None:
            return None
        if len(spinboxes) < 2:
            return None

        next_spinbox = self.find_next_spinbox(current_row, spinboxes)
        spinbox_value_sum = 0
        for spinbox in spinboxes:
            if spinbox.objectName().startswith('{}_'.format(str_number)):
                spinbox_value_sum = spinbox_value_sum + spinbox.value()
        value_change = spinbox_value_sum - 100
        next_value = next_spinbox.value() - value_change
        next_spinbox.setValue(next_value)
        return next_spinbox

    def update_spinbox(self):
        """
        Updates other spinboxes when the value of
        the current spinbox changes.
        """
        current_spinbox = self.sender()
        spinboxes = self.str_type_component.ownership_share()

        next_spinbox = self.execute_spinbox_update(
            spinboxes, current_spinbox
        )

        self.shareUpdated.emit(spinboxes, next_spinbox)

    def update_spinbox_when_zero(self, spinboxes, next_spinbox):
        """
        Updates the second spinbox when the value of the next spinbox is 0.
        :param spinboxes: List of spinboxes that are connected.
        :type spinboxes: List
        :param next_spinbox: The next spinbox
        :type next_spinbox: QDoubleSpinBox
        """
        if next_spinbox is None:
            return
        if next_spinbox.value() == 0:
            spinbox = self.execute_spinbox_update(
                spinboxes, next_spinbox
            )

            self.shareUpdatedOnZero.emit(spinbox.value())
            if spinbox.value() == 0:
                self.update_spinbox_when_zero(
                    spinboxes, spinbox
                )

    def find_next_spinbox(self, current_row, spinboxes):
        """
        Finds the next spinbox using the object name and row.
        :param current_row: The current spinbox row.
        :type current_row: Integer
        :param spinboxes: The list of spinboxes that are added.
        :type spinboxes: List
        :return: Next spinbox
        :rtype: QDoubleSpinBox
        """
        next_row = current_row + 1
        next_spinboxes = [spinbox for spinbox in spinboxes
                          if spinbox.objectName().
                              endswith('_{}'.format(next_row))]
        if len(next_spinboxes) > 0:
            next_spinbox = next_spinboxes[0]
        else:
            next_spinboxes = [spinbox for spinbox in spinboxes
                              if spinbox.objectName().endswith('_0')]
            next_spinbox = next_spinboxes[0]
        return next_spinbox

    def update_ownership_share_data(self):
        """
        Updates the ownership share data in the share dictionary.
        """
        spinboxes = self.str_type_component.ownership_share()
        data_store = self.current_data_store()
        for spinbox in spinboxes:
            if spinbox in self.share_spinbox_connected:
                str_number_ext, party_id, current_row = \
                    self._extract_from_object_name(spinbox)
                data_store.share[party_id] = spinbox.value()
        print vars(data_store)
        # print self.data_store

    @staticmethod
    def _extract_from_object_name(spinbox):
        """
        Extracts str_number, party id, and row of a spinbox
        from its object name.
        :param spinbox: The spinbox from which the values are extracted from.
        :type spinbox: QDoubleSpinBox
        :return: str_number, party id, and row of a spinbox
        :rtype: Tuple
        """
        current_name = spinbox.objectName()
        current_name_split = current_name.split('_')
        if len(current_name_split) == 3:
            current_row = current_name_split[2]
            current_party_id = current_name_split[1]
            str_number = current_name_split[0]
            return int(str_number), \
                   int(current_party_id), \
                   int(current_row)
        else:
            return None, None, None

    def str_node(self):
        """
        Creates the STR node with its children.
        """
        str_icon = QIcon(
            ':/plugins/stdm/images/icons/new_str.png'
        )
        str_label = QApplication.translate(
            'STRTreeView', 'Social Tenure Relationship'
        )
        str_root = QStandardItem(
            str_icon, '{} {}'.format(str_label, self.str_number)
        )
        str_root.setData(self.str_number)
        self.tree_view_model.appendRow(str_root)
        self.str_children(str_root)
        self.tree_view.expand(str_root.index())

        self.data_store[self.str_number] = STRDataStore()

    def translate_str_items(self):
        """
        Translates the texts of the STR items.
        """
        self.str_text = QApplication.translate(
            'InitSTREditor', 'Social Tenure Relationship'
        )
        self.party_text = QApplication.translate(
            'InitSTREditor', 'Party'
        )
        self.spatial_unit_text = QApplication.translate(
            'InitSTREditor', 'Spatial Unit'
        )
        self.tenure_type_text = QApplication.translate(
            'InitSTREditor', 'Tenure Information'
        )
        self.supporting_doc_text = QApplication.translate(
            'InitSTREditor', 'Supporting Documents'
        )

        self.validity_period_text = QApplication.translate(
            'InitSTREditor', 'Validity Period'
        )

    def str_children(self, str_root):
        """
        Creates STR children and
        populates self.str_items dictionary.
        :param str_root: The STR root item.
        :type str_root: QStandardItem
        """
        self.translate_str_items()
        children = OrderedDict()
        children[self.party_text] = 'user.png'
        children[self.spatial_unit_text] = 'property.png'
        children[self.tenure_type_text] = 'social_tenure.png'
        children[self.supporting_doc_text] = 'document.png'
        children[self.validity_period_text] = 'period.png'
        for name, icon in children.iteritems():
            item = self.child_item(str_root, name, icon)
            self.str_items[
                '%s%s' % (name, self.str_number)
                ] = item

        self.str_items[
            '%s%s' % (self.str_text, self.str_number)
            ] = str_root
        party_item = self.str_items[
            '%s%s' % (self.party_text, self.str_number)
            ]
        party_item.setEnabled(True)

    def child_item(self, str_root, name, icon):
        """
        Creates the child item of str_root.
        :param str_root:  The STR root item.
        :type str_root: QStandardItem
        :param name: The item name
        :type name: String
        :param icon: The icon image of the item.
        :type icon: String
        :return: The child item
        :rtype: QStandardItem
        """
        q_icon = QIcon(
            ':/plugins/stdm/images/icons/{}'.format(icon)
        )
        name_text = QApplication.translate(
            'InitSTREditor', name
        )
        item = QStandardItem(
            q_icon, name_text
        )

        item.setData(self.str_number)
        item.setEnabled(False)

        str_root.appendRow([item])

        if name == self.party_text:
            self.party_item_index = item.index()

        return item

    def add_str_tree_node(self):
        """
        Adds the first STR tree node.
        """
        self.str_number = self.str_number + 1
        self.str_node()
        self.buttonBox.button(
            QDialogButtonBox.Save
        ).setEnabled(False)

    def str_item(self, text, str_number):
        """
        Gets the str_item by text and str_number.
        :param text: The translated text of items.
        :type text: String
        :param str_number: The current STR number
        :type str_number: Integer
        """
        item = self.str_items['%s%s' % (text, str_number)]
        return item

    def current_item(self):
        """
        Gets the currently selected tree_view item.
        :return: The currently selected item
        :rtype: QStandardItem
        """
        index = self.tree_view.currentIndex()
        item = self.tree_view_model.itemFromIndex(index)
        return item

    def current_str_number(self):
        """
        Gets the currently selected str_number.
        :return: The currently selected str_number
        :rtype: Integer
        """
        item = self.current_item()
        str_number = item.data()
        return str_number

    def switch_entity(self, index):
        """
        Switches the ForeignKeyMapper of a selected party entity.
        :param index: The Combobox current index.
        :type index: QModelIndex
        """
        self.entity_combo = self.sender()
        table = self.entity_combo.itemData(index)
        new_entity = self.current_profile.entity_by_name(table)
        self.party = new_entity
        self.party_component.party_fk_mapper.set_entity(self.party)

        self.clear_store_on_switch()

        self.str_type_components = None

        self.init_str_type_component(new_entity)

        self._party_signals()

    def clear_store_on_switch(self):
        """
        Clear party and STR type store
        on switch of the party entity.
        """
        current_store = self.current_data_store()
        current_store.party.clear()
        current_store.str_type.clear()
        current_store.share.clear()

    def update_str_type_data(self, index, data_store, party_id):
        """
        Gets str_type date from the comboboxes and set it to
        the current data store.
        :param index: Index of the combobox
        :type index: QModelIndex
        :param data_store: The current data store
        :type data_store: OrderedDict
        :param party_id: The party id matching the combobox.
        :type party_id: Integer
        """
        str_combo = self.sender()
        str_type_id = str_combo.itemData(index)
        data_store.str_type[party_id] = str_type_id
        self.str_type_updated.emit()
        print vars(self.data_store[1])

    def current_data_store(self):
        """
        Gets the current data_store object for the selected STR tree.
        :return: The current data store object
        :rtype: Object
        """
        index = self.tree_view.currentIndex()
        selected_item = self.tree_view_model.itemFromIndex(index)
        data_store_obj = self.data_store[selected_item.data()]
        return data_store_obj


class BindSTREditor(InitSTREditor):
    """
    Binds the STR components tree items with the stack widgets
    containing the component widgets.
    """

    def __init__(self):
        """
        Initializes the class and the super class. 
        """
        InitSTREditor.__init__(self)

    def bind_component_to_tree_view(self, current, previous):
        """
        Bind all components to the tree view component items.
        :param current: The current item index.
        :type current: QModelIndex
        :param previous: The previous  item index.
        :type previous: QModelIndex
        """
        selected_item = self.tree_view_model.itemFromIndex(current)

        if selected_item is None:
            return
        str_number = selected_item.data()

        if selected_item.text() == '{} {}' \
                .format(self.str_text, str_number):
            self.bind_str()

        if selected_item.text() == self.party_text:
            self.bind_party()

        if selected_item.text() == self.spatial_unit_text:
            self.bind_spatial_unit()

        if selected_item.text() == self.tenure_type_text:
            self.bind_tenure_type()

        if selected_item.text() == self.supporting_doc_text:
            self.bind_supporting_documents(
                str_number
            )
        if selected_item.text() == self.validity_period_text:
            self.bind_validity_period()

    def bind_str(self):
        """
        Binds the STR introduction page to the STR root node item.
        """
        self.component_container.setCurrentIndex(0)
        header = QApplication.translate(
            'BindSTREditor',
            'The Social Tenure Relationship'
        )
        self.description_lbl.setText(header)

    def bind_party(self):
        """
        Binds the party item to the party component widget and description.
        """
        QTimer.singleShot(50, self.init_str_type_component)
        QTimer.singleShot(50, self.init_spatial_unit_component)
        self.component_container.setCurrentIndex(1)
        header = QApplication.translate(
            'BindSTREditor',
            'Select the party by searching through the existing record.'
        )
        self.description_lbl.setText(header)

    def bind_spatial_unit(self):
        """
        Binds the party item to the party component widget and description.
        """
        self.notice.clear()
        self.component_container.setCurrentIndex(2)
        self.mirror_map.set_iface(self.iface)
        self.mirror_map.refresh_canvas_layers()
        self.mirror_map.load_web_map()
        header = QApplication.translate(
            'BindSTREditor',
            'Select the spatial unit that could be parcel, '
            'land or building, structure and so on.'
        )
        self.description_lbl.setText(header)

    def bind_tenure_type(self):
        """
        Binds the tenure type item to the party component widget
        and description.
        """
        self.notice.clear()
        self.component_container.setCurrentIndex(3)
        QTimer.singleShot(50, self.init_supporting_documents)
        QTimer.singleShot(50, self.init_validity_period_component)

        header = QApplication.translate(
            'BindSTREditor',
            'Select the type of relationship that the specified party '
            'has with the selected spatial unit. Optionally you can '
            'specify the tenure share. '
        )
        self.description_lbl.setText(header)

    def bind_supporting_documents(self, str_number):
        """
        Binds the supporting document item to the party component
        widget and description.
        :param str_number: The current STR record number
        :type str_number: Integer
        """
        self.notice.clear()
        self.component_container.setCurrentIndex(4)

        self.supporting_doc_signals(str_number)
        header = QApplication.translate(
            'BindSTREditor',
            'Upload one or more supporting documents under '
            'each document types.'
        )
        if len(self.data_store[str_number].party) > 1:
            explanation = QApplication.translate(
                'BindSTREditor',
                'The uploaded document will be copied '
                'for each party record selected.'

            )
            self.description_lbl.setText('{} {}'.format(header, explanation))
        else:
            self.description_lbl.setText(header)

    def bind_validity_period(self):
        """
        Binds the validity period item to the party component widget
        and description.
        """
        self.notice.clear()
        self.component_container.setCurrentIndex(5)

        header = QApplication.translate(
            'BindSTREditor',
            'Specify the validity range of dates. The year and month option '
            'is used to quickly set the date ranges. '
        )
        self.description_lbl.setText(header)


class SyncSTREditorData(BindSTREditor):
    """
    Synchronizes data in the data store to each components
    when the tree items are clicked.
    """

    def __init__(self):
        """
        Initializes SyncSTREditorData and BindSTREditor. 
        """
        BindSTREditor.__init__(self)

    def sync_data(self, current, previous):
        """
        Synchronizes all components data store to the tree
        view component items.
        :param current: The current item index.
        :type current: QModelIndex
        :param previous: The previous  item index.
        :type previous: QModelIndex
        """
        selected_item = self.tree_view_model.itemFromIndex(current)
        if selected_item is None:
            return
        str_number = selected_item.data()

        data_store = self.data_store[str_number]

        if selected_item.text() == self.party_text:
            self.toggle_party_models(
                self.party_component.party_fk_mapper, data_store
            )
        if selected_item.text() == self.spatial_unit_text:
            self.toggle_spatial_unit_models(
                self.spatial_unit_component.spatial_unit_fk_mapper,
                data_store
            )
        if selected_item.text() == self.tenure_type_text:
            self.toggle_str_type_models(data_store, str_number)

        if selected_item.text() == self.supporting_doc_text:
            self.toggle_supporting_doc(
                data_store, str_number
            )
        if selected_item.text() == self.validity_period_text:
            self.toggle_validity_period(data_store, str_number)

    def toggle_party_models(self, fk_mapper, data_store):
        """
        Toggles party data store and insert it to foreign key mapper
        of party entity.
        :param fk_mapper: The foreign key mapper object
        :type fk_mapper: Object
        :param data_store: The current STR data store
        :type data_store: Object
        """
        fk_mapper.remove_rows()
        for i, model_obj in enumerate(data_store.party.values()):
            fk_mapper.insert_model_to_table(
                model_obj
            )

    def toggle_spatial_unit_models(self, fk_mapper, data_store):
        """
        Toggles spatial  data store and insert it to foreign key mapper
        of party entity.
        :param fk_mapper: The foreign key mapper object
        :type fk_mapper: Object
        :param data_store: The current STR data store
        :type data_store: Object
        """
        if fk_mapper is None:
            return
        fk_mapper.remove_rows()

        for i, model_obj in enumerate(
                data_store.spatial_unit.values()
        ):
            fk_mapper.insert_model_to_table(
                model_obj
            )

    def toggle_str_type_models(self, data_store, str_number):
        """
        Toggles the STR type component data store when the tenure information
        treeview item is clicked.
        :param data_store: The current data store.
        :type data_store: Object
        :param str_number: The current STR root number.
        :type str_number: Integer
        """
        party_count = len(data_store.party)
        # If new party row is added after spinboxes values are set,
        # reset spinbox values into equal values based on the new count
        if str_number in self.party_count.keys():

            if len(self.party_count) > 0 and \
                            party_count > \
                            self.party_count[str_number]:
                self.reset_share_spinboxes(data_store)

        self.party_count[str_number] = party_count
        self.str_type_component.remove_table_data(
            self.str_type_component.str_type_table,
            party_count
        )
        # ## select the first column (STR Type)
        self.str_type_component.str_type_table.selectColumn(0)

        for i, (party_id, str_type_id) in \
                enumerate(data_store.str_type.iteritems()):
            self.str_type_component.add_str_type_data(
                self.copied_party_row[party_id],
                str_type_id,
                i
            )
            self.init_str_type_signal(
                data_store, party_id, str_number
            )

        self.init_share_spinboxes(data_store)

    def toggle_supporting_doc(self, data_store, str_number):
        """
        Toggles the supporting document component data store
        when the supporting documents treeview item is clicked.
        :param data_store: The current data store.
        :type data_store: Object
        :param str_number: The current STR root number.
        :type str_number: Integer
        """
        party_count = len(data_store.party)
        # update party count
        self.supporting_doc_component.party_count(party_count)
        # update the current widget container to be used.
        self.supporting_doc_component.update_container(str_number)

    def toggle_validity_period(self, data_store, str_number):
        """
        Toggles the validity period component data store
        when the validity period treeview item is clicked.
        :param data_store: The current data store
        :type data_store: STRDataStore
        :param str_number: The current STR root number.
        :type str_number: Integer
        """
        from_date = data_store.validity_period['from_date']
        to_date = data_store.validity_period['to_date']

        if from_date is None or to_date is None:
            from_date = data_store.validity_period['from_date'] = \
                self.validity_from_date.date()
            to_date = data_store.validity_period['to_date'] = \
                self.validity_to_date.date()

        self.validity_from_date.setDate(from_date)
        self.validity_to_date.setDate(to_date)


class ValidateSTREditor(SyncSTREditorData):
    """
    Validates the STR editor. Validates user inputs and the
    enabling of buttons and treeview items.
    """

    def __init__(self):
        """
        Initializes ValidateSTREditor and SyncSTREditorData. 
        """
        SyncSTREditorData.__init__(self)

    def validate_page(self, current, previous):
        """
        Validates str components pages when tree item is clicked.
        :param current: The newly clicked item index
        :type current: QModelIndex
        :param previous: The previous item index
        :type previous: QModelIndex
        """
        selected_item = self.tree_view_model.itemFromIndex(current)
        if selected_item is None:
            return
        str_number = selected_item.data()
        data_store = self.data_store[str_number]

        if selected_item.text() == self.party_text:
            self.validate_party(data_store, selected_item)

        if selected_item.text() == self.spatial_unit_text:
            self.validate_spatial_unit(data_store, selected_item)

        if selected_item.text() == self.tenure_type_text:
            self.validate_str_type(data_store, selected_item)

        if selected_item.text() == self.supporting_doc_text:
            self.enable_save_button()

    def validate_party(self, data_store, selected_item):
        """
        Validates the party length and enables and disables buttons and
        the next treeview items.
        :param data_store: The current data store object.
        :type data_store: Object
        :param selected_item: The currently selected treeview item/ party item.
        :type selected_item: QStandardItem
        """
        self.party_component.party_fk_mapper. \
            afterEntityAdded.connect(
            lambda: self.validate_party_length(
                data_store, selected_item
            )
        )
        self.party_component.party_fk_mapper. \
            deletedRows.connect(
            lambda: self.validate_party_length(
                data_store, selected_item
            )
        )

    def validate_spatial_unit(self, data_store, selected_item):
        """
        Validates the spatial unit length and enables and disables buttons and
        the next treeview items.
        :param data_store: The current data store object.
        :type data_store: Object
        :param selected_item: The currently selected treeview item/ spatial
        unit item.
        :type selected_item: QStandardItem
        """
        if self.spatial_unit_component.spatial_unit_fk_mapper is None:
            return
        self.spatial_unit_component.spatial_unit_fk_mapper. \
            afterEntityAdded.connect(
            lambda: self.enable_next(selected_item, 2)
        )
        self.spatial_unit_component.spatial_unit_fk_mapper. \
            deletedRows.connect(
            lambda: self.validate_spatial_unit_length(
                data_store, selected_item
            )
        )
        self.spatial_unit_component.spatial_unit_fk_mapper. \
            beforeEntityAdded.connect(
            self.validate_party_count
        )
        self.spatial_unit_component.spatial_unit_fk_mapper. \
            afterEntityAdded.connect(
            self.validate_non_multi_party
        )

    def validate_str_type(self, data_store, selected_item):
        """
        Validates the STR type entry and enables and disables buttons and
        the next treeview items.
        :param data_store: The current data store object.
        :type data_store: Object
        :param selected_item: The currently selected treeview item/ STR type
        item.
        :type selected_item: QStandardItem
        """
        self.str_type_updated.connect(
            lambda: self.validate_str_type_length(
                data_store, selected_item
            )
        )

    def enable_next(self, selected_item, child_row, enable=True):
        """
        Enables or disables the next treeview item.
        :param selected_item: The currently selected item.
        :type selected_item: QStandardItem
        :param child_row: The row number of an item to be enabled or disabled.
        :type child_row: Integer
        :param enable: A boolean to enable and disable the next treeview item.
        :type enable: Boolean
        """
        try:
            str_root = selected_item.parent()

            if str_root is None:
                return
            next_item = str_root.child(child_row, 0)
            next_item.setEnabled(enable)

            self.enable_save_button()
        except Exception:
            pass

    def enable_save_button(self):
        """
        Enables or disables the Save button of the STR editor based on the
        validity status of the editor.
        """
        result = self.str_validity_status()

        self.buttonBox.button(
            QDialogButtonBox.Save
        ).setEnabled(result)

    def str_validity_status(self):
        """
        Determines the validity status of the editor by checking the whether
        the treeview items are enabled or not.
        """
        for row in range(self.tree_view_model.rowCount()):
            root = self.tree_view_model.item(row)
            for child_row in range(root.rowCount()):
                child = root.child(child_row, 0)
                if not child.isEnabled():
                    return False
        return True

    def validate_party_length(self, store, item):
        """
        Validates the length of party component data.
        :param store: The current data store.
        :type store: Object
        :param item: The current item
        :type item: QStandardItem
        """
        if len(store.party) < 1:
            self.enable_next(item, 1, False)
            self.enable_next(item, 2, False)
            self.enable_next(item, 3, False)
        else:
            self.enable_next(item, 1)
            if len(store.spatial_unit) > 0:
                self.enable_next(item, 2)
            else:
                self.enable_next(item, 3, False)
            self.enable_save_button()

    def validate_spatial_unit_length(self, store, item):
        """
        Validates the length of party component data.
        :param store: The current data store.
        :type store: Object
        :param item: The current item
        :type item: QStandardItem
        """
        if len(store.spatial_unit) < 1:
            self.enable_next(item, 2, False)
        else:
            self.enable_next(item, 2)
            self.enable_save_button()

    def validate_str_type_length(self, store, selected_item):
        """
        Validates the length of party component data.
        :param store: The current data store.
        :type store: Object
        :param item: The current item
        :type item: QStandardItem
        """
        if 0 in store.str_type.values() or \
                        None in store.str_type.values():
            self.enable_next(selected_item, 3, False)
        else:

            self.enable_next(selected_item, 3)
            self.enable_next(selected_item, 4)
            self.enable_save_button()

    def validation_error(self, index):
        """
        Validates the length of party component data.
        :param store: The current data store.
        :type store: Object
        :param item: The current item
        :type item: QStandardItem
        """
        item = self.tree_view_model.itemFromIndex(index)
        if item is None:
            return
        if not item.isEnabled():
            warning = 'You should first select a ' \
                      'record in the enabled items to open the ' \
                      '%s component.' % item.text()
            warning_message = QApplication.translate(
                'ValidateSTREditor', warning
            )
            self.notice.clear()
            self.notice.insertWarningNotification(
                warning_message
            )

    def validate_party_count(self, spatial_unit_obj):
        """
        Validates the number of party assigned to a spatial unt.
        :param spatial_unit_obj: Spatial unit model object
        :type spatial_unit_obj: SQL Alchemy Model Object
        :return: True if the count is ok and false if not.
        :rtype: Boolean
        """
        # Get entity browser notification bar
        fk_mapper = self.sender()
        browser_notif = None
        if isinstance(fk_mapper, ForeignKeyMapper):
            # Insert error in entity browser too
            browser_notif = NotificationBar(
                fk_mapper._entitySelector.vlNotification
            )
            self.remove_browser_notice(fk_mapper)

        usage_count = self.spatial_unit_usage_count(
            spatial_unit_obj
        )
        # If entry is found, show info or error
        if usage_count > 0:
            self.notice.clear()
            if self.social_tenure.multi_party:
                QTimer.singleShot(
                    10100, lambda: self.remove_browser_notice(fk_mapper)
                )
                self.allow_multi_party_info(
                    browser_notif, usage_count
                )
                return True
            else:
                QTimer.singleShot(
                    40, lambda: self.remove_browser_notice(fk_mapper)
                )
                QTimer.singleShot(
                    100, lambda: self.disallow_multi_party_error(
                        browser_notif, fk_mapper
                    )
                )
                return False
        else:
            return True

    def disallow_multi_party_error(self, browser_notif, fk_mapper):
        """
        Prevents user from proceeding if multi-party is disabled and a
        spatial unit is used more than once.
        :param browser_notif: Foreign key mapper entity browser
        notification bar.
        :type browser_notif: NotificationBar
        :param fk_mapper: The ForeignKeyMapper object of spatial unit entity.
        :type fk_mapper: Object
        """
        QTimer.singleShot(
            10100, lambda: self.remove_browser_notice(fk_mapper)
        )
        spatial_unit = format_name(
            self.spatial_unit.short_name
        )
        if not self.party is None:
            party = format_name(
                self.party.short_name
            )
        else:
            party = 'party'

        msg = QApplication.translate(
            'ValidateSTREditor',
            'Unfortunately, this {} has already been '
            'assigned to a {}.'.format(spatial_unit, party)
        )
        self.notice.insertErrorNotification(msg)
        if isinstance(fk_mapper, ForeignKeyMapper):
            if browser_notif is not None:
                browser_notif.insertErrorNotification(msg)

    def allow_multi_party_info(self, browser_notif, usage_count):
        """
        When multi-party is allowed shows only information notification when
        a spatial unit is used by more than one party.
        :param browser_notif: Foreign key mapper entity browser
        notification bar.
        :type browser_notif: NotificationBar
        :param usage_count: The number of parties that are already assigned to
        a spatial unit.
        :type usage_count: Integer
        """
        if not self.party is None:
            party = format_name(self.party.short_name)
        else:
            party = 'party'
        occupant = '%s(s)' % format_name(party)
        msg = QApplication.translate(
            'ValidateSTREditor',
            'This {} has already been assigned to {} {}.'.format(
                format_name(self.spatial_unit.short_name),
                str(usage_count),
                occupant
            )
        )
        self.notice.insertInformationNotification(msg)
        browser_notif.insertInformationNotification(msg)

    def remove_browser_notice(self, fk_mapper):
        """
        Removes the foreign key mapper entity browser notification bar.
        :param fk_mapper: ForeignKeyMapper object of spatial unit entity.
        :type fk_mapper: Object
        """
        layout = fk_mapper._entitySelector.vlNotification

        for i in reversed(range(layout.count())):
            notif = layout.itemAt(i).widget()
            for lbl in notif.findChildren(QWidget):
                layout.removeWidget(lbl)
                lbl.setVisible(False)
                lbl.deleteLater()

            notif.setParent(None)

    def validate_non_multi_party(self, spatial_unit_obj):
        """
        Removes added row of spatial unit if the record
        is already linked to another party.
        :param spatial_unit_obj:The spatial unit model object
        :type spatial_unit_obj: SQLAlchemy model Object
        """
        if not self.social_tenure.multi_party:
            usage_count = self.spatial_unit_usage_count(
                spatial_unit_obj
            )

            if usage_count > 0:
                fk_mapper = self.sender()
                self.spatial_unit_component.remove_table_data(
                    fk_mapper._tbFKEntity, 1
                )
                store = self.current_data_store()
                store.spatial_unit.clear()

                item = self.current_item()
                self.enable_next(item, 2, False)
                self.validate_spatial_unit_length(
                    store, item
                )

    def spatial_unit_current_usage_count(self, current_id):
        """
        Gets the current usage count in this DataStore objects
        by looping through self.data_store.

        :return: usage count of spatial unit
        :rtype: Integer
        """
        spatial_unit_ids = []
        for data_store in self.data_store.values():
            for spatial_unit_obj in data_store.spatial_unit.values():
                spatial_unit_ids.append(spatial_unit_obj.id)

        if spatial_unit_ids.count(current_id) > 1:
            return spatial_unit_ids.count(current_id)
        elif spatial_unit_ids.count(current_id) <= 1:
            return 0

    def spatial_unit_usage_count(self, model_obj):
        """
        Gets the count of spatial unit usage in the database.
        :param model_obj: Spatial unit model object
        :type model_obj: SQLAlchemy model Object
        """
        # returns the number of entries for a specific parcel.
        str_obj = self.str_model()
        usage_count = str_obj.queryObject(
            [func.count().label('spatial_unit_count')]
        ).filter(
            self.str_model.spatial_unit_id == model_obj.id
        ).first()
        # TODO add a session rollback here and show error.
        current = self.spatial_unit_current_usage_count(model_obj.id)
        return current + usage_count.spatial_unit_count


class STREditor(ValidateSTREditor):
    def __init__(self):
        """
        Wrapper class for STR Editor for new STR record editor user interface.
        """
        InitSTREditor.__init__(self)

        self.str_editor_signals()

        self.tree_view_signals()

    def str_editor_signals(self):
        """
        The STR editor signals used to add new STR entry node and
        save the data.
        """
        self.add_str_btn.clicked.connect(
            self.add_str_tree_node
        )
        self.remove_str_btn.clicked.connect(
            self.remove_str_tree_node
        )

        self.buttonBox.accepted.connect(self.save_str)

    def spatial_unit_signals(self):
        """
        Spatial unit component signals.
        """
        if self.spatial_unit_component.spatial_unit_fk_mapper is None:
            return
        self.spatial_unit_component.spatial_unit_fk_mapper. \
            beforeEntityAdded.connect(
            lambda model: self.set_spatial_unit_data(
                model
            )
        )
        self.spatial_unit_component.spatial_unit_fk_mapper. \
            deletedRows.connect(
            self.remove_spatial_unit_model
        )

    def set_str_doc_models(self):
        """
        Sets STR model and supporting document model.
        """
        models = self.supporting_doc_component.str_doc_models()
        self.str_model = models[0]
        self.str_doc_model = models[1]

    def set_party_data(self, model):
        """
        Sets party date to the data store party dictionary.
        :param model: The model of the selected party record.
        :type model: SQLAlchemy Model
        """
        current_data_store = self.current_data_store()
        current_data_store.party[model.id] = model
        item = self.str_item(self.party_text, self.str_number)
        # validate party length to enable the next item
        self.validate_party_length(current_data_store, item)
        # print self.data_store

    def set_spatial_unit_data(self, model):
        """
        Sets spatial unit date to the data store spatial unit dictionary.
        :param model: The model of the selected spatial unit record.
        :type model: SQLAlchemy Model
        """
        current_store = self.current_data_store()
        current_store.spatial_unit.clear()
        current_store.spatial_unit[model.id] = model

    def set_str_type_data(self, str_type_id, party_id, row_number):
        """
        Adds STR type rows using party records selected.
        :param str_type_id: The STR type id
        :type str_type_id: Integer
        :param party_id: The party id
        :type party_id: Integer
        :param row_number: The STR row number
        :type row_number: Integer
        """
        current_store = self.current_data_store()
        current_store.str_type[party_id] = str_type_id
        row_data = self.str_type_component.copy_party_table(
            self.party_component.party_fk_mapper._tbFKEntity,
            row_number
        )

        self.copied_party_row[party_id] = row_data

        self.str_type_component.add_str_type_data(
            row_data, str_type_id, row_number
        )
        print vars(self.data_store[1])

    def validity_period_signals(self):
        """
        The validity period signals.
        """
        self.validity_from_date.dateChanged.connect(
            self.set_validity_period_data
        )
        self.validity_to_date.dateChanged.connect(
            self.set_validity_period_data
        )

    def set_validity_period_data(self, date):
        """
        Sets the validity period data to the data store validity
        period dictionary.
        :param date: Date set into the DateEdit
        :type date: QDate
        """
        store = self.current_data_store()
        if self.sender().objectName() == 'validity_from_date':
            store.validity_period['from_date'] = date
        else:
            store.validity_period['to_date'] = date

    def supporting_doc_signals(self, str_number):
        """
        Supporting document component signals.
        :param str_number: The STR node number
        :type str_number: Integer
        """
        self.doc_type_cbo.currentIndexChanged.connect(
            lambda: self.supporting_doc_component.
                update_container(str_number)
        )
        self.supporting_doc_component.onUploadDocument.connect(
            lambda model_objs: self.set_supporting_documents(
                model_objs
            )
        )

    def set_supporting_documents(self, model_objs):
        """
        Sets the supporting document model object list into the current store
        supporting document object.
        :param model_objs: The supporting document model object list.
        :type model_objs: List
        """
        current_store = self.current_data_store()
        current_store.supporting_document = model_objs

    def tree_view_signals(self):
        """
        Treeview signals that listens to three items.
        """
        self.view_selection.currentChanged.connect(
            self.validate_page
        )
        self.view_selection.currentChanged.connect(
            self.bind_component_to_tree_view
        )
        self.view_selection.currentChanged.connect(
            self.sync_data
        )
        self.tree_view.clicked.connect(
            self.validation_error
        )

    def validate_str_delete(self, selected_str):
        """
        Validates the deletion of the STR nodes.
        :param selected_str: Selected STR node index list.
        :type selected_str: List
        :return: Boolean of whether the deletion is valid or not valid. False
        means there is no selected STR node.
        :rtype: Boolean
        """
        if len(selected_str) < 1:
            warning = 'Please first select on STR tree node or ' \
                      'children you would like to delete.'
            warning_message = QApplication.translate(
                'STREditor', warning
            )
            self.notice.insertWarningNotification(
                warning_message
            )
            return False
        else:
            text = 'Are you sure you want to ' \
                   'delete the selected STR entry?'
            text2 = 'STR Delete Warning'
            question = QApplication.translate(
                'STREditor', text
            )
            title = QApplication.translate(
                'STREditor', text2
            )
            result = self.message(
                title, question, 'warning', True
            )
            if result == QMessageBox.No:
                return False
            else:
                return True

    def remove_str_tree_node(self):
        """
        Remove the STR node.
        """
        selected_indexes = self.tree_view.selectedIndexes()
        result = self.validate_str_delete(selected_indexes)
        if not result:
            return
        index = selected_indexes[0]
        selected_item = self.tree_view_model.itemFromIndex(index)
        str_number = selected_item.data()
        self.tree_view_model.removeRows(index.row(), 1)
        self.remove_str_node_models(str_number)
        self.enable_save_button()

    def remove_str_node_models(self, str_number):
        """
        Removes the STR node data store from the data store dictionary.
        :param str_number: The STR node number
        :type str_number: Integer
        """
        del self.data_store[str_number]

    def remove_spatial_unit_model(self):
        """
        Clears the spatial unit dictionary.
        """
        current_store = self.current_data_store()
        current_store.spatial_unit.clear()

    def save_str(self):
        """
        Saves the data into the database.
        """
        db_handler = STRDBHandler(self.data_store, self.str_model)
        db_handler.commit_str()

    def message(self, title, message, type='information', yes_no=False):
        """
        Shows popup message box.
        :param title: The title of the message.
        :type title: String
        :param message: The message of the message box.
        :type message: String
        :param type: Type of the message.
        :type type: String
        :param yes_no: Boolean for the presence of Yes/No button instead of
        the ok button.
        :type yes_no: Boolean
        :return: The message box result. Relevant when Yes/No button exists.
        :rtype: Integer
        """
        header = QApplication.translate('STREditor', title)
        body = QApplication.translate('STREditor', message)
        buttons = None
        result = None
        if yes_no:
            buttons = QMessageBox.Yes | QMessageBox.No

        if type == 'information':
            result = QMessageBox.information(
                self.iface.mainWindow(), header, body, buttons
            )

        elif type == 'warning' and yes_no:
            result = QMessageBox.warning(
                self.iface.mainWindow(), header, body, buttons
            )

        return result

    def translate(self, message):
        msg = QApplication.translate('STREditor', message)
        return msg


class EditSTREditor(STREditor):
    def __init__(self, str_edit_node):
        """
        The Edit user interface of the STR Editor.
        :param str_edit_node: The STR editable model containing
        the supporting document models.
        :type str_edit_node: List or STRNODE
        """
        STREditor.__init__(self)

        self.str_edit_node = str_edit_node
        try:
            self.str_edit_obj = str_edit_node.model()
            self.str_doc_edit_obj = str_edit_node.documents()
        except AttributeError:
            self.str_edit_obj = str_edit_node[0]
            self.str_doc_edit_obj = str_edit_node[1]

        self.updated_str_obj = None
        self.str_edit_dict = self.str_edit_obj.__dict__
        current_party_detail = self.current_party(
            self.str_edit_dict
        )
        if current_party_detail is not None:
            self.party, self.party_column = self.current_party(
                self.str_edit_dict
            )
        title = QApplication.translate(
            'EditSTREditor',
            'Edit Social Tenure Relationship'
        )
        self.setWindowTitle(title)

        self.add_str_btn.setDisabled(True)
        self.remove_str_btn.setDisabled(True)

        QTimer.singleShot(33, self.init_str_type_component)
        QTimer.singleShot(55, self.init_spatial_unit_component)
        QTimer.singleShot(77, self.init_supporting_documents)
        QTimer.singleShot(80, self.init_validity_period_component)

        self.party_init.connect(self.populate_party_str_type_store)
        self.spatial_unit_init.connect(self.populate_spatial_unit_store)
        self.docs_init.connect(self.populate_supporting_doc_store)
        self.validity_init.connect(self.populate_validity_store)

    def current_party(self, record):
        """
        Gets the current party column name in STR
        table by finding party column with value
        other than None.
        :param record: The STR record or result.
        :type record: Dictionary
        :return: The party column name with value.
        :rtype: String
        """
        parties = self.social_tenure.parties
        if record is None:
            return
        for party in parties:
            party_name = party.short_name.lower()
            party_id = '{}_id'.format(party_name)
            if party_id not in record.keys():
                return
            if record[party_id] != None:
                return party, party_id

    def populate_party_str_type_store(self):
        """
        Populates the party and STR Type store into the data store.
        """
        party_model_obj = getattr(
            self.str_edit_obj, self.party.name
        )
        self.data_store[1].party.clear()
        self.data_store[1].party[
            self.str_edit_dict[self.party_column]
        ] = party_model_obj

        str_type_id = self.str_edit_obj.tenure_type
        self.data_store[1].str_type[
            self.str_edit_dict[self.party_column]
        ] = str_type_id

        QTimer.singleShot(
            40, lambda: self.populate_str_type(str_type_id)
        )
        self.party_component.party_fk_mapper.setSupportsList(False)

        self.set_party_active()
        self.buttonBox.button(QDialogButtonBox.Save).setEnabled(True)

    def populate_str_type(self, str_type_id):
        """
        Populate the STR type combobox and the tenure share spinbox.
        :param str_type_id: The tenure type id
        :type str_type_id: Integer
        """
        self.init_str_type_component()
        party_id = self.str_edit_dict[self.party_column]
        # populate str type column
        self.set_str_type_data(str_type_id, party_id, 0)
        self.str_type_component.add_str_type_data(
            self.copied_party_row[party_id],
            str_type_id,
            0
        )
        self.init_str_type_signal(
            self.data_store[1], party_id, 1
        )

        tenure_share = self.str_edit_obj.tenure_share

        self.data_store[1].share[party_id] = tenure_share

        doc_item = self.str_item(
            self.tenure_type_text, self.str_number
        )

        doc_item.setEnabled(True)

    def set_party_active(self):
        """
        Select the party item active. Users doesn't need to see the
        description when editing an STR record.
        """
        self.component_container.setCurrentIndex(1)
        # Select the party item
        self.tree_view.selectionModel().setCurrentIndex(
            self.party_item_index, QItemSelectionModel.Select
        )
        # Click on party item
        self.tree_view.clicked.emit(self.party_item_index)

        self.enable_save_button()

    def populate_spatial_unit_store(self):
        """
        Populates the spatial unit data store.
        """
        spatial_unit_model_obj = getattr(
            self.str_edit_obj, self.spatial_unit.name
        )
        self.data_store[1].spatial_unit.clear()

        self.data_store[1].spatial_unit[
            self.str_edit_obj.spatial_unit_id
        ] = spatial_unit_model_obj

        doc_item = self.str_item(
            self.spatial_unit_text, self.str_number
        )

        doc_item.setEnabled(True)

    def populate_validity_store(self):
        """
        Populates the spatial unit data store.
        """
        start_date = self.str_edit_obj.validity_start
        end_date = self.str_edit_obj.validity_end
        self.data_store[1].validity_period.clear()

        self.data_store[1].validity_period['from_date'] = start_date
        self.data_store[1].validity_period['to_date'] = end_date

        doc_item = self.str_item(
            self.validity_period_text, self.str_number
        )

        doc_item.setEnabled(True)

    def populate_supporting_doc_store(self):
        """
        Initializes the supporting document page.
        """
        doc_item = self.str_item(
            self.supporting_doc_text, self.str_number
        )

        if len(self.str_doc_edit_obj) < 1:
            doc_item.setEnabled(True)
            return

        for doc_id, doc_objs in self.str_doc_edit_obj.iteritems():

            index = self.doc_type_cbo.findData(doc_id)
            doc_text = self.doc_type_cbo.itemText(index)

            layout = self.supporting_doc_component.docs_tab.findChild(
                QVBoxLayout, 'layout_{}_{}'.format(doc_text, self.str_number)
            )

            self.supporting_doc_component.supporting_doc_manager. \
                registerContainer(layout, doc_id)
            for doc_obj in doc_objs:
                self.supporting_doc_component.supporting_doc_manager. \
                    insertDocFromModel(doc_obj, doc_id)

        doc_item.setEnabled(True)

    def set_party_data(self, model):
        """
        Sets the party data from the ForeignKeyMapper model to the data store.
        :param model: The party model
        :type model: SQLAlchemy Model
        """
        store = self.current_data_store()
        store.party.clear()
        store.party[model.id] = model

    def set_str_type_data(self, str_type_id, party_id, row_number):
        """
        Sets the STR type data to the STR type data store dictionary.
        :param str_type_id: The STR type id
        :type str_type_id: Integer
        :param party_id: The party id
        :type party_id: Integer
        :param row_number: The STR row number
        :type row_number: Integer
        """
        store = self.current_data_store()
        store.str_type.clear()
        store.share.clear()

        store.str_type[party_id] = str_type_id

        row_data = self.str_type_component.copy_party_table(
            self.party_component.party_fk_mapper._tbFKEntity,
            row_number
        )
        self.copied_party_row.clear()
        self.copied_party_row[party_id] = row_data

    def save_str(self):
        """
        Saves the edited data into the database.
        """
        db_handler = STRDBHandler(
            self.data_store, self.str_model, self.str_edit_node
        )
        self.updated_str_obj = db_handler.commit_str()
