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

from qgis.PyQt import uic

from qgis.PyQt.QtCore import (
    pyqtSignal,
    QTimer,
    Qt,
    QItemSelectionModel,
    QModelIndex,
    QDate
)

from qgis.PyQt.QtGui import (
    QStandardItemModel,
    QStandardItem,
)
from qgis.PyQt.QtWidgets import (
    QTreeView,
    QApplication,
    QDialog,
    QAbstractItemView,
    QWidget,
    QMessageBox,
    QDialogButtonBox,
    QVBoxLayout,
    QDoubleSpinBox
)
from qgis.utils import (
    iface
)
from sqlalchemy import (
    func
)

from stdm.data.configuration.entity import Entity
from stdm.data.pg_utils import pg_table_record_count
from stdm.settings import current_profile
from stdm.ui.foreign_key_mapper import ForeignKeyMapper
from stdm.ui.gui_utils import GuiUtils
from stdm.ui.notification import NotificationBar
from stdm.ui.social_tenure.str_components import (
    Party,
    SpatialUnit,
    STRType,
    SupportingDocuments,
    ValidityPeriod,
    CustomTenureInfo
)
from stdm.ui.social_tenure.str_data import (
    STRDataStore,
    STRDBHandler
)
from stdm.utils.util import (
    format_name,
    entity_attr_to_model
)


class BindSTREditor(object):
    """
    Binds the STR components tree items with the stack widgets
    containing the component widgets.
    """

    def __init__(self, editor):
        """
        Initializes the class and the super class.
        """
        self.editor = editor
        editor.view_selection.currentChanged.connect(
            self.bind_component_to_tree_view
        )

    def bind_component_to_tree_view(self, current, previous):
        """
        Bind all components to the tree view component items.
        :param current: The current item index.
        :type current: QModelIndex
        :param previous: The previous  item index.
        :type previous: QModelIndex
        """
        selected_item = self.editor.tree_view_model.itemFromIndex(current)

        if selected_item is None:
            return
        str_number = selected_item.data()

        if selected_item.text() == '{} {}'.format(
                self.editor.str_text, str_number):
            self.bind_str()

        if selected_item.text() == self.editor.party_text:
            self.bind_party()

        if selected_item.text() == self.editor.spatial_unit_text:
            self.bind_spatial_unit()

        if selected_item.text() == self.editor.tenure_type_text:
            self.bind_tenure_type()

        if selected_item.text() == self.editor.custom_tenure_info_text:
            self.bind_custom_tenure_info()

        if selected_item.text() == self.editor.supporting_doc_text:
            self.bind_supporting_documents(
                str_number
            )
        if selected_item.text() == self.editor.validity_period_text:
            self.bind_validity_period()

    def bind_str(self):
        """
        Binds the STR introduction page to the STR root node item.
        """
        self.editor.component_container.setCurrentIndex(0)
        header = QApplication.translate(
            'BindSTREditor',
            'The Social Tenure Relationship'
        )
        self.editor.description_lbl.setText(header)

    def bind_party(self):
        """
        Binds the party item to the party component widget and description.
        """
        QTimer.singleShot(50, self.editor.init_str_type_component)
        QTimer.singleShot(50, self.editor.init_spatial_unit_component)
        self.editor.component_container.setCurrentIndex(1)
        header = QApplication.translate(
            'BindSTREditor',
            'Select the party by searching through the existing record.'
        )
        self.editor.description_lbl.setText(header)

    def bind_spatial_unit(self):
        """
        Binds the party item to the party component widget and description.
        """
        self.editor.notice.clear()
        self.editor.component_container.setCurrentIndex(2)
        self.editor.mirror_map.set_iface(self.editor.iface)
        self.editor.mirror_map.refresh_canvas_layers()
        self.editor.mirror_map.load_web_map()
        header = QApplication.translate(
            'BindSTREditor',
            'Select the spatial unit that could be parcel, '
            'land or building, structure and so on.'
        )
        self.editor.description_lbl.setText(header)

    def bind_tenure_type(self):
        """
        Binds the tenure type item to the tenure type component widget
        and description.
        """
        self.editor.notice.clear()
        self.editor.component_container.setCurrentIndex(3)
        QTimer.singleShot(50, self.editor.init_supporting_documents)
        QTimer.singleShot(50, self.editor.init_validity_period_component)

        header = QApplication.translate(
            'BindSTREditor',
            'Select the type of relationship that the specified party '
            'has with the selected spatial unit. Optionally you can '
            'specify the tenure share. '
        )
        self.editor.description_lbl.setText(header)

    def bind_custom_tenure_info(self):
        """
        Binds related tenure info item to the related tenure info component
        widget and description.
        """
        self.editor.notice.clear()
        self.editor.component_container.setCurrentIndex(4)

        header = QApplication.translate(
            'BindSTREditor',
            'Fill out the custom tenure information form for each party record.'
            'You need to select a party record to enable the form.'
        )
        self.editor.description_lbl.setText(header)

    def bind_supporting_documents(self, str_number):
        """
        Binds the supporting document item to the party component
        widget and description.
        :param str_number: The current STR record number
        :type str_number: Integer
        """
        self.editor.notice.clear()
        self.editor.component_container.setCurrentIndex(5)

        self.editor.supporting_doc_signals(str_number)
        header = QApplication.translate(
            'BindSTREditor',
            'Upload one or more supporting documents under '
            'each document types.'
        )
        if len(self.editor.data_store[str_number].party) > 1:
            explanation = QApplication.translate(
                'BindSTREditor',
                'The uploaded document will be copied '
                'for each party record selected.'

            )
            self.editor.description_lbl.setText('{} {}'.format(
                header, explanation
            ))
        else:
            self.editor.description_lbl.setText(header)

    def bind_validity_period(self):
        """
        Binds the validity period item to the party component widget
        and description.
        """
        self.editor.notice.clear()
        self.editor.component_container.setCurrentIndex(6)

        header = QApplication.translate(
            'BindSTREditor',
            'Specify the validity range of dates. The year and month option '
            'is used to quickly set the date ranges. '
        )
        self.editor.description_lbl.setText(header)


class SyncSTREditorData(object):
    """
    Synchronizes data in the data store to each components
    when the tree items are clicked.
    """

    def __init__(self, editor):
        """
        Initializes SyncSTREditorData and BindSTREditor.
        """
        self.editor = editor
        editor.view_selection.currentChanged.connect(
            self.sync_data
        )

    def sync_data(self, current: QModelIndex, previous: QModelIndex):
        """
        Synchronizes all components data store to the tree
        view component items.
        :param current: The current item index.
        :type current: QModelIndex
        :param previous: The previous  item index.
        :type previous: QModelIndex
        """
        selected_item = self.editor.tree_view_model.itemFromIndex(current)
        previous_item = self.editor.tree_view_model.itemFromIndex(previous)

        if selected_item is None:
            return

        if previous_item is not None:
            prev_str_number = previous_item.data()

            print(f'Previous Number: {prev_str_number}')

            prev_data_store = self.editor.data_store[prev_str_number]
            if previous_item.text() == self.editor.custom_tenure_info_text:
                self.save_custom_tenure_info(prev_data_store, prev_str_number)

        str_number = selected_item.data()

        data_store = self.editor.data_store[str_number]

        if selected_item.text() == self.editor.party_text:
            self.toggle_party_models(
                self.editor.party_component.party_fk_mapper, data_store
            )
        if selected_item.text() == self.editor.spatial_unit_text:
            self.toggle_spatial_unit_models(
                self.editor.spatial_unit_component.spatial_unit_fk_mapper,
                data_store
            )
        if selected_item.text() == self.editor.tenure_type_text:
            self.toggle_str_type_models(data_store, str_number)

        if selected_item.text() == self.editor.supporting_doc_text:
            self.toggle_supporting_doc(
                data_store, str_number
            )
        if selected_item.text() == self.editor.validity_period_text:
            self.toggle_validity_period(data_store, str_number)

        # save the tab forms of custom tenure info when a user unselects the node.
        # Load current custom tenure info tabs with data.
        if selected_item.text() == self.editor.custom_tenure_info_text:
            self.load_custom_tenure_data(data_store, str_number)

    def load_custom_tenure_data(self, data_store: STRDataStore, str_number: int):
        """
        Loads custom tenure data by adding tabs and associated editor with model.
        :param data_store: The current data store object
        :param str_number: The STR number
        :type str_number: Integer
        """
        self.editor.custom_tenure_tab.clear()

        if len(data_store.custom_tenure) > 0:
            for i, (party_id, model) in \
                    enumerate(data_store.custom_tenure.items()):
                if party_id in data_store.party.keys():
                    self.editor.add_custom_tenure_info_data(
                        data_store.party[party_id], i, model
                    )
        else:

            for i, (party_id, model) in enumerate(data_store.party.items()):
                # if party_id in data_store.party.keys():
                self.editor.add_custom_tenure_info_data(
                    data_store.party[party_id], i
                )

    def save_custom_tenure_info(self, prev_data_store: STRDataStore, prev_str_number: int):
        """
        When a custom tenure node is unselected, saves the changes in the tab
        forms.
        :param prev_data_store: The data store object of the unselected custom
        tenure nodes.
        :param prev_str_number: The STR number of the unselected custom tenure
        node.
        :type prev_str_number: Integer
        """
        print('----')
        print(self.editor.custom_tenure_info_component.entity_editors)
        print('----')

        for i, party_id in enumerate(prev_data_store.custom_tenure.keys()):
            self.editor.custom_tenure_info_component.entity_editors[
                (prev_str_number, i)].on_model_added()
            custom_model = \
                self.editor.custom_tenure_info_component.entity_editors[
                    (prev_str_number, i)
                ].model()
            prev_data_store.custom_tenure[party_id] = custom_model

    def toggle_party_models(self, fk_mapper: ForeignKeyMapper, data_store: STRDataStore):
        """
        Toggles party data store and insert it to foreign key mapper
        of party entity.
        :param fk_mapper: The foreign key mapper object
        :param data_store: The current STR data store object
        """
        fk_mapper.remove_rows()
        for i, model_obj in enumerate(data_store.party.values()):
            fk_mapper.insert_model_to_table(
                model_obj
            )

    def toggle_spatial_unit_models(self, fk_mapper: ForeignKeyMapper, data_store: STRDataStore):
        """
        Toggles spatial  data store and insert it to foreign key mapper
        of party entity.
        :param fk_mapper: The foreign key mapper object
        :param data_store: The current STR data store
        """
        if fk_mapper is None:
            return
        fk_mapper.remove_rows()

        for i, model_obj in enumerate(data_store.spatial_unit.values()):
            fk_mapper.insert_model_to_table(
                model_obj
            )

    def toggle_str_type_models(self, data_store: STRDataStore, str_number: int):
        """
        Toggles the STR type component data store when the tenure information
        treeview item is clicked.
        :param data_store: The current data store.
        :param str_number: The current STR root number.
        :type str_number: Integer
        """
        party_count = len(data_store.party)
        # If new party row is added after spinboxes values are set,
        # reset spinbox values into equal values based on the new count
        if str_number in self.editor.party_count.keys():
            if len(self.editor.party_count) > 0 and \
                    party_count > \
                    self.editor.party_count[str_number]:
                self.editor.reset_share_spinboxes(data_store)

        self.editor.party_count[str_number] = party_count
        # Remove previous item data
        self.editor.str_type_component.remove_table_data(
            self.editor.str_type_component.str_type_table, party_count
        )
        # Select the first column (STR Type)
        self.editor.str_type_component.str_type_table.selectColumn(0)

        for i, (party_id, str_type_id) in \
                enumerate(data_store.str_type.items()):
            if party_id in data_store.party.keys():
                self.editor.str_type_component.add_str_type_data(
                    self.editor.spatial_unit,
                    self.editor.copied_party_row[party_id], i
                )
                self.editor.init_tenure_data(
                    data_store, party_id, str_type_id, str_number
                )

    def toggle_supporting_doc(self, data_store: STRDataStore, str_number: int):
        """
        Toggles the supporting document component data store
        when the supporting documents treeview item is clicked.
        :param data_store: The current data store.
        :param str_number: The current STR root number.
        :type str_number: Integer
        """
        party_count = len(data_store.party)
        # update party count
        self.editor.supporting_doc_component.party_count(party_count)
        # update the current widget container to be used.
        self.editor.supporting_doc_component.update_container(str_number)

    def toggle_validity_period(self, data_store: STRDataStore, str_number: int):
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
                self.editor.validity_from_date.date()
            to_date = data_store.validity_period['to_date'] = \
                self.editor.validity_to_date.date()

        self.editor.validity_from_date.setDate(from_date)
        self.editor.validity_to_date.setDate(to_date)


class ValidateSTREditor(object):
    """
    Validates the STR editor. Validates user inputs and the
    enabling of buttons and treeview items.
    """

    def __init__(self, editor):
        """
        Initializes ValidateSTREditor and SyncSTREditorData.
        """
        self.editor = editor
        editor.view_selection.currentChanged.connect(
            self.validate_page
        )
        editor.tree_view.clicked.connect(
            self.validation_error
        )
        self._warning_message = QApplication.translate(
            'ValidateSTREditor', 'You should first select a '
                                 'record in the enabled items to open the '
                                 'this component.'
        )

    def validate_page(self, current: QModelIndex, previous: QModelIndex):
        """
        Validates str components pages when tree item is clicked.
        :param current: The newly clicked item index
        :type current: QModelIndex
        :param previous: The previous item index
        :type previous: QModelIndex
        """
        selected_item = self.editor.tree_view_model.itemFromIndex(current)
        if selected_item is None:
            return
        str_number = selected_item.data()
        data_store = self.editor.data_store[str_number]

        if selected_item.text() == self.editor.party_text:
            self.validate_party(data_store, selected_item)

        if selected_item.text() == self.editor.spatial_unit_text:
            self.validate_spatial_unit(data_store, selected_item)

        if selected_item.text() == self.editor.tenure_type_text:
            self.validate_str_type(data_store, selected_item)

        if selected_item.text() == self.editor.custom_tenure_info_text:
            pass

        if selected_item.text() == self.editor.supporting_doc_text:
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
        self.editor.party_component.party_fk_mapper.afterEntityAdded.connect(
            lambda: self.validate_party_length(data_store, selected_item)
        )
        self.editor.party_component.party_fk_mapper.deletedRows.connect(
            lambda: self.validate_party_length(data_store, selected_item)
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
        if self.editor.spatial_unit_component.spatial_unit_fk_mapper is None:
            return
        self.editor.spatial_unit_component.spatial_unit_fk_mapper. \
            afterEntityAdded.connect(
            lambda: self.enable_next(selected_item, 2)
        )
        self.editor.spatial_unit_component.spatial_unit_fk_mapper. \
            deletedRows.connect(
            lambda: self.validate_spatial_unit_length(
                data_store, selected_item
            )
        )
        self.editor.spatial_unit_component.spatial_unit_fk_mapper. \
            beforeEntityAdded.connect(
            self.validate_party_count
        )
        self.editor.spatial_unit_component.spatial_unit_fk_mapper. \
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
        self.editor.str_type_updated.connect(
            lambda: self.validate_str_type_length(data_store, selected_item)
        )

    def enable_next(self, selected_item, child_row, enable=True, handle_child=False):
        """
        Enables or disables the next treeview item.
        :param selected_item: The currently selected item.
        :type selected_item: QStandardItem
        :param child_row: The row number of an item to be enabled or disabled.
        :type child_row: Integer
        :param enable: A boolean to enable and disable the next treeview item.
        :type enable: Boolean
        """
        str_root = selected_item.parent()

        if str_root is None:
            return
        next_item = str_root.child(child_row, 0)
        if next_item is None:
            return

        next_item.setEnabled(enable)
        # if handle_child:
        #     next_item.child().setEnabled(enable)

        self.enable_save_button()

    def enable_save_button(self):
        """
        Enables or disables the Save button of the STR editor based on the
        validity status of the editor.
        """
        result = self.str_validity_status()
        self.editor.buttonBox.button(QDialogButtonBox.Save).setEnabled(result)

    def str_validity_status(self):
        """
        Determines the validity status of the editor by checking the whether
        the treeview items are enabled or not.
        """
        if self.editor.tree_view_model.rowCount() < 1:
            return False
        for row in range(self.editor.tree_view_model.rowCount()):
            root = self.editor.tree_view_model.item(row)
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
        :param selected_item: The current item
        :type selected_item: QStandardItem
        """
        # TODO fix validation issue when str type is 0 or None
        if 0 in store.str_type.values() or None in store.str_type.values():
            # TODO fix editing issue where supporting document is disabled
            if len(store.str_type) == len(store.party):

                self.enable_next(selected_item, 3, False)
                # Disable custom tenure information item
                if selected_item.child(0, 0) is not None:
                    selected_item.child(0, 0).setEnabled(False)
                self.enable_next(selected_item, 4, False)
                self.enable_next(selected_item, 5, False)

        else:
            self.enable_next(selected_item, 3)
            # Enable custom tenure information item

            if selected_item.child(0, 0) is not None:
                selected_item.child(0, 0).setEnabled(True)
            self.enable_next(selected_item, 4)
            self.enable_next(selected_item, 5)
            self.enable_save_button()

    def validation_error(self, index):
        """
        Validates the length of party component data.
        """
        item = self.editor.tree_view_model.itemFromIndex(index)
        if item is None:
            return
        if not item.isEnabled():
            # warning = 'You should first select a ' \
            #           'record in the enabled items to open the ' \
            #           '%s component.' % item.text()

            self.editor.notice.clear()
            self.editor.notice.insertWarningNotification(
                self._warning_message
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
        fk_mapper = self.editor.sender()
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
            self.editor.notice.clear()
            if self.editor.social_tenure.multi_party:
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
            self.editor.spatial_unit.short_name
        )
        if self.editor.party is not None:
            party = format_name(
                self.editor.party.short_name
            )
        else:
            party = 'party'

        msg = QApplication.translate(
            'ValidateSTREditor',
            'Unfortunately, this {} has already been '
            'assigned to a {}.'.format(spatial_unit, party)
        )
        self.editor.notice.insertErrorNotification(msg)
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
        if self.editor.party is not None:
            party = format_name(self.editor.party.short_name)
        else:
            party = 'party'
        occupant = '%s(s)' % format_name(party)

        msg = QApplication.translate(
            'ValidateSTREditor',
            'This {} has already been assigned to {} {}.'.format(
                format_name(self.editor.spatial_unit.short_name),
                str(usage_count),
                occupant
            )
        )
        self.editor.notice.insertInformationNotification(msg)
        browser_notif.insertInformationNotification(msg)

    def remove_browser_notice(self, fk_mapper):
        """
        Removes the foreign key mapper entity browser notification bar.
        :param fk_mapper: ForeignKeyMapper object of spatial unit entity.
        :type fk_mapper: Object
        """
        layout = fk_mapper._entitySelector.vlNotification

        for i in reversed(list(range(layout.count()))):
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
        if not self.editor.social_tenure.multi_party:
            usage_count = self.spatial_unit_usage_count(
                spatial_unit_obj
            )

            if usage_count > 0:
                fk_mapper = self.editor.sender()
                self.editor.spatial_unit_component.remove_table_data(
                    fk_mapper._tbFKEntity, 1
                )
                store = self.editor.current_data_store()
                store.spatial_unit.clear()

                item = self.editor.current_item()
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
        for data_store in self.editor.data_store.values():
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
        str_obj = self.editor.str_model()
        spatial_unit_id = getattr(self.editor.str_model, '{}_id'.format(
            self.editor.spatial_unit.short_name.replace(
                ' ', '_'
            ).lower()))
        usage_count = str_obj.queryObject(
            [func.count().label('spatial_unit_count')]
        ).filter(spatial_unit_id == model_obj.id).first()
        # TODO add a session rollback here and show error.
        current = self.spatial_unit_current_usage_count(model_obj.id)
        return current + usage_count.spatial_unit_count

    def validate_custom_tenure_form(self):
        """
        Validates custom tenure form validity.
        :return:
        :rtype:
        """
        stores = self.editor.data_store
        errors = []
        for str_number, store in stores.items():
            spatial_unit = store.current_spatial_unit
            custom_attr_entity = self.editor.social_tenure.spu_custom_attribute_entity(
                spatial_unit
            )
            if custom_attr_entity is None:
                continue

            if len(custom_attr_entity.columns) < 4:
                continue
            for i, (party_id, custom_model) in enumerate(store.custom_tenure.items()):
                if custom_model is not None:
                    if (str_number, i) in \
                            self.editor.custom_tenure_info_component. \
                                    entity_editors.keys():
                        editor = self.editor.custom_tenure_info_component.entity_editors[
                            (str_number, i)]

                        errors = editor.validate_all()

                else:
                    for col in custom_attr_entity.columns.values():
                        if col.mandatory:
                            msg = QApplication.translate("ValidateSTREditor",
                                                         "is a required field.")
                            error = '{} {}'.format(col.name, msg)
                            errors.append('{}:{} {}'.format(str_number, i, error))

        if len(errors) > 0:
            self.editor.notice.clear()
            for error in errors:
                self.editor.notice.insertWarningNotification(
                    error
                )
            return False
        return True


WIDGET, BASE = uic.loadUiType(
    GuiUtils.get_ui_file_path('social_tenure/ui_str_editor.ui'))


class STREditor(WIDGET, BASE):
    """
    Wrapper class for STR Editor for new STR record editor user interface.
    """
    party_init = pyqtSignal()
    spatial_unit_init = pyqtSignal()
    custom_tenure_info_init = pyqtSignal()
    validity_init = pyqtSignal()
    docs_init = pyqtSignal()
    str_type_updated = pyqtSignal()
    shareUpdated = pyqtSignal(list, QDoubleSpinBox)
    shareUpdatedOnZero = pyqtSignal(float)
    customTenureSaved = pyqtSignal(object, object)

    def __init__(self):
        """
        Initializes the STR editor.
        """
        QDialog.__init__(self, iface.mainWindow())
        self.setupUi(self)

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
        self.custom_tenure_info_text = QApplication.translate(
            'InitSTREditor', 'Custom Tenure Information'
        )
        self.supporting_doc_text = QApplication.translate(
            'InitSTREditor', 'Supporting Documents'
        )

        self.validity_period_text = QApplication.translate(
            'InitSTREditor', 'Validity Period'
        )

        self.add_str_btn.setIcon(GuiUtils.get_icon('add.png'))
        self.remove_str_btn.setIcon(GuiUtils.get_icon('remove.png'))
        self.add_documents_btn.setIcon(GuiUtils.get_icon('document.png'))

        self._init_tree_view()

        self.iface = iface
        self.str_number = 0
        self.data_store = OrderedDict()
        self.party_item_index = None

        self.supporting_doc_component = None
        self.str_items = {}
        self.current_profile = current_profile()

        self.social_tenure = self.current_profile.social_tenure

        count = pg_table_record_count(self.social_tenure.name)

        self.setWindowTitle(self.tr('{}{}'.format(self.windowTitle(), '- ' + str(count) + ' rows')))

        self.party_count = OrderedDict()

        self.parties = self.social_tenure.parties
        self.spatial_units = self.social_tenure.spatial_units
        if len(self.parties) > 0:
            self.party = self.parties[0]
        else:
            self.party = None
        if len(self.spatial_units) > 0:
            self.spatial_unit = self.spatial_units[0]
        else:
            self.spatial_unit = None

        self.add_str_tree_node()

        self.party_component = None
        self.str_model = None
        self.str_doc_model = None
        self.spatial_unit_component = None
        self.validity_period_component = None
        self.custom_tenure_info_component = None
        self.str_type_combo_connected = []
        self.share_spinbox_connected = []
        self.parties = self.social_tenure.parties

        self.str_type_component = None
        self._init_str_editor()
        self.init_party_component()
        self.init_custom_tenure_info_component()
        self._party_signals()
        self.copied_party_row = OrderedDict()

        self.str_editor_signals()
        self.bind = BindSTREditor(self)
        self.sync = SyncSTREditorData(self)
        self.validate = ValidateSTREditor(self)

    def _init_str_editor(self):
        """
        Initializes the GUI of the STR editor.
        """
        self._init_notification()
        self.splitter.isCollapsible(False)
        self.splitter.setSizes([220, 550])
        self.splitter.setChildrenCollapsible(False)

        self.buttonBox.button(QDialogButtonBox.Save).setEnabled(False)

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

    def create_new_str_node(self):
        """
        Creates the STR node with its children.
        """
        str_icon = GuiUtils.get_icon('new_str.png')

        str_label = QApplication.translate(
            'STRTreeView', 'Social Tenure Relationship')

        str_root = QStandardItem(
            str_icon, '{} {}'.format(str_label, self.str_number))

        self.str_number = self.str_number + 1

        str_root.setData(self.str_number)
        self.tree_view_model.appendRow(str_root)
        self.populate_children_for_str_node(str_root)
        self.tree_view.expandAll()
        store = STRDataStore()
        self.data_store[self.str_number] = store
        store.current_spatial_unit = self.spatial_unit
        store.current_party = self.party

    def populate_children_for_str_node(self, str_root: QStandardItem):
        """
        Creates STR children and
        populates self.str_items dictionary.
        :param str_root: The STR root item.
        :type str_root: QStandardItem
        """
        children = OrderedDict()
        children[self.party_text] = 'user.png'
        children[self.spatial_unit_text] = 'property.png'
        children[self.tenure_type_text] = 'social_tenure.png'
        children[self.supporting_doc_text] = 'document.png'
        children[self.validity_period_text] = 'period.png'
        children[self.custom_tenure_info_text] = 'custom_tenure.png'
        for name, icon in children.items():
            item = self.create_str_child_item(str_root, name, icon)
            self.str_items['%s%s' % (name, self.str_number)] = item

        self.str_items['%s%s' % (self.str_text, self.str_number)] = str_root

        party_item = self.str_item(self.party_text, self.str_number)
        party_item.setEnabled(True)

    def create_str_child_item(self, str_root: QStandardItem, name: str, icon: str):
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
        q_icon = GuiUtils.get_icon(icon)

        item = QStandardItem(q_icon, name)

        item.setData(self.str_number)

        # Add related tenure info under tenure information
        if name == self.custom_tenure_info_text:

            custom_attr = self.social_tenure.spu_custom_attribute_entity(
                self.spatial_unit
            )

            if custom_attr is not None:
                if len(custom_attr.columns) > 2:  # check if user columns are added
                    tenure_type_item = self.str_item(
                        self.tenure_type_text, self.str_number)
                    item.setEnabled(False)
                    tenure_type_item.appendRow([item])

        else:
            item.setEnabled(False)
            str_root.appendRow([item])

        if name == self.party_text:
            self.party_item_index = item.index()

        return item

    def add_str_tree_node(self):
        """
        Adds the first STR tree node.
        """
        self.create_new_str_node()
        self.buttonBox.button(QDialogButtonBox.Save).setEnabled(False)

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

    def current_item(self) -> QStandardItem:
        """
        Gets the currently selected tree_view item.
        :return: The currently selected item
        :rtype: QStandardItem
        """
        index = self.tree_view.currentIndex()
        item = self.tree_view_model.itemFromIndex(index)
        return item

    def current_str_number(self) -> int:
        """
        Gets the currently selected str_number.
        :return: The currently selected str_number
        :rtype: Integer
        """
        item = self.current_item()
        str_number = item.data()
        return str_number

    def top_description_visibility(self, is_visible: bool):
        """
        Sets the visibility of top description.
        :param is_visible: A boolean that shows or
        hides top description.
        """
        if is_visible:
            self.top_description.show()
        else:
            self.top_description.hide()

    def init_party_component(self, party: Entity=None):
        """
        Initializes the party component.
        :param party: Party entity object.
        If party is none, the default party loads.
        :type party: Entity
        """
        if party is not None:
            self.party_init.emit()

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

    def init_str_type_component(self, party: Entity=None):
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
            self.notice,
            party
        )

    def init_custom_tenure_info_component(self):
        """
        Initializes the str type component.
        """
        if self.custom_tenure_info_component is not None:
            return

        self.custom_tenure_info_component = CustomTenureInfo(self, self.notice)

        self.custom_tenure_info_init.emit()

    def init_spatial_unit_component(self, spatial_unit: Entity=None):
        """
        Initializes the spatial unit component.
        :param spatial_unit: The current spatial_unit entity.
        :type spatial_unit: Object
        """
        if spatial_unit is not None:
            self.spatial_unit_init.emit()

        if self.spatial_unit_component is not None:
            return
        self.spatial_unit_component = SpatialUnit(
            spatial_unit,
            self.spatial_unit_box,
            self.notice
        )
        self.spatial_unit_signals()

        self.spatial_unit_component.spatial_unit_fk_mapper.entity_combo. \
            currentIndexChanged.connect(
            self.switch_spatial_unit_entity
        )

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
            self.notice,
            parent=self
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

    def init_tenure_data(self, data_store: STRDataStore, party_id, str_type_id, str_number):
        """
        Connects str type combobox signals to a slot.
        :param data_store: Current data store
        :type data_store: Dictionary
        :param party_id: The added party model id.
        :type party_id: String
        :param str_type_id: Tenure type id
        :type str_type_id: Integer
        :param str_number: The str entry number.
        :type str_number: Integer
        """
        if self.str_type_component is None:
            return
        self.init_tenure_share_data(data_store, party_id, str_number)
        self.init_str_type_data(data_store, party_id, str_type_id, str_number)

    def init_tenure_share_data(self, data_store, party_id, str_number):
        """
        Initialize tenure share data by setting existing already set data.
        :param data_store: Current data store
        :type data_store: Dictionary
        :param party_id: The added party model id.
        :type party_id: String
        :param str_number: The str entry number.
        :type str_number: Integer
        """
        spinboxes = self.str_type_component.ownership_share()
        for spinbox in spinboxes:
            if spinbox not in self.share_spinbox_connected:
                row_number = spinbox.objectName()
                spinbox.setObjectName(
                    '{}_{}_{}'.format(str_number, party_id, row_number)
                )

                spinbox.valueChanged.connect(self.update_spinbox)
                self.share_spinbox_connected.append(spinbox)
        self.shareUpdated.connect(self.update_ownership_share_data)
        self.shareUpdated.connect(self.update_spinbox_when_zero)
        self.shareUpdatedOnZero.connect(self.update_ownership_share_data)
        self.init_share_spinboxes(data_store, str_number)

    def init_str_type_data(self, data_store, party_id, str_type_id,
                           str_number):
        """
        Initialize str type data by setting existing already set data.
        :param data_store: Current data store
        :type data_store: Dictionary
        :param party_id: The added party model id.
        :type party_id: String
        :param str_type_id: Tenure type id
        :type str_type_id: Integer
        :param str_number: The str entry number.
        :type str_number: Integer
        """
        # gets all the comboboxes including the ones in other pages.
        str_type_combos = self.str_type_component.str_type_combobox()
        for str_type_combo in str_type_combos:
            # connect comboboxes that are only newly added
            if str_type_combo not in self.str_type_combo_connected:
                row_number = str_type_combo.objectName()
                str_type_combo.setObjectName(
                    '{}_{}_{}'.format(str_number, party_id, row_number)
                )

                str_type_combo.currentIndexChanged.connect(
                    lambda index: self.update_str_type_data(
                        index, data_store, party_id
                    ))
                self.str_type_combo_connected.append(str_type_combo)
        self.init_tenure_type_combo(data_store, str_number)

    def init_tenure_type_combo(self, data_store, str_no):
        """
        Initialize the tenure type data by setting equal
        value to all spinboxes or by picking values
        from the data store.
        :param data_store: The current data store.
        :type data_store: Object
        """
        # gets all the comboboxes including the ones in other pages.
        str_type_combos = self.str_type_component.str_type_combobox()
        for str_type_combo in str_type_combos:
            if str_type_combo in self.str_type_combo_connected:
                str_number, party_id, current_row = \
                    self._extract_from_object_name(str_type_combo)
                # Exclude other str_type from another str entry
                if str_number != str_no:
                    continue

                if party_id in data_store.str_type.keys():
                    self.blockSignals(True)
                    if data_store.str_type[party_id] is None:
                        str_type_combo.setCurrentIndex(0)
                        data_store.str_type[party_id] = 0
                    else:
                        sel_index = str_type_combo.findData(
                            data_store.str_type[party_id],
                            Qt.UserRole, Qt.MatchExactly
                        )
                        str_type_combo.setCurrentIndex(sel_index)

                    self.blockSignals(False)

                else:
                    self.blockSignals(True)
                    str_type_combo.setCurrentIndex(0)
                    data_store.str_type[party_id] = 0

    def _party_signals(self):
        """
        Connects party and str_type
        related slots and signals.
        """
        QApplication.processEvents()
        self.party_component.party_fk_mapper.beforeEntityAdded.connect(
            lambda model: self.set_party_data(model)
        )
        self.party_component.party_fk_mapper.afterEntityAdded.connect(
            lambda model, row_number: self.set_str_type_data(
                0, model.id, row_number
            )
        )

        self.party_component.party_fk_mapper.afterEntityAdded.connect(
            lambda model, row_number: self.add_custom_tenure_info_data(
                model, row_number
            )
        )

        self.party_component.party_fk_mapper.deletedRows.connect(
            self.remove_party_str_row_model
        )

        self.party_component.party_fk_mapper.entity_combo. \
            currentIndexChanged.connect(
            self.switch_party_entity
        )

    def add_custom_tenure_info_data(self, party_model, row_number,
                                    custom_model=None):
        """
        Adds custom tenure info tab with editor form. It could load data if
        the custom_model is not none.
        :param party_model: The party model associated with custom tenure info
        record.
        :type party_model: Object
        :param row_number: The row number of the party entry
        :type row_number: Integer
        :param custom_model: The custom tenure model that populates the tab
        forms.
        :type custom_model: Integer
        """
        custom_attr_entity = self.social_tenure.spu_custom_attribute_entity(
            self.spatial_unit
        )

        if custom_attr_entity is None:
            return
        store = self.current_data_store()
        QApplication.processEvents()

        str_number = self.current_item().data()

        create_result = self.custom_tenure_info_component.add_entity_editor(
            self.party, self.spatial_unit, party_model,
            str_number, row_number, custom_model
        )

        if create_result:
            store.custom_tenure[party_model.id] = custom_model

    def reset_share_spinboxes(self, data_store):
        """
        Resets the share spinboxes value to have equal value.
        This method is used when a row is deleted,
        and new row is added.
        :param data_store: The current data store
        :type data_store: Object
        """
        row_count = len(data_store.party)
        if row_count == 0:
            return
        spinboxes = self.str_type_component.ownership_share()
        for spinbox in spinboxes:
            if spinbox in self.share_spinbox_connected:
                str_number, party_id, current_row = \
                    self._extract_from_object_name(spinbox)

                self.blockSignals(True)
                spinbox.setValue(100.00 / row_count)
                self.blockSignals(False)
                data_store.share[party_id] = 100.00 / row_count

    def init_share_spinboxes(self, data_store: STRDataStore, str_no):
        """
        Initialize the share spinboxes by setting equal
        value to all spinboxes or by picking values
        from the data store.
        :param data_store: The current data store.
        """
        row_count = len(data_store.party)
        spinboxes = self.str_type_component.ownership_share()
        for spinbox in spinboxes:

            if spinbox in self.share_spinbox_connected:
                str_number, party_id, current_row = \
                    self._extract_from_object_name(spinbox)
                # Exclude other spinboxes from another str entry
                if str_number != str_no:
                    continue
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

    def switch_party_entity(self, index):
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
        store = self.current_data_store()
        store.current_party = self.party
        self.clear_store_on_switch()

        self.str_type_components = None

        self.init_str_type_component(new_entity)

        self._party_signals()
        self.buttonBox.button(QDialogButtonBox.Save).setEnabled(False)

    def switch_spatial_unit_entity(self, index):
        """
        Switches the ForeignKeyMapper of a selected spatial unit entity.
        :param index: The Combobox current index.
        :type index: QModelIndex
        """
        store = self.current_data_store()
        self.spatial_entity_combo = self.sender()
        table = self.spatial_entity_combo.itemData(index)
        new_entity = self.current_profile.entity_by_name(table)
        self.spatial_unit = new_entity
        store.current_spatial_unit = self.spatial_unit
        self.spatial_unit_component.spatial_unit_fk_mapper.set_entity(
            self.spatial_unit)

        store.spatial_unit.clear()

        # store.str_type.clear()
        store.custom_tenure.clear()
        self.str_type_components = None
        self.init_custom_tenure_info_component()
        self.spatial_unit_signals()
        self.update_str_type_lookup()
        self.buttonBox.button(QDialogButtonBox.Save).setEnabled(False)

    def clear_store_on_switch(self):
        """
        Clear party and STR type store
        on switch of the party entity.
        """
        current_store = self.current_data_store()
        current_store.party.clear()
        current_store.str_type.clear()
        current_store.share.clear()

    def update_str_type_lookup(self):
        """
        Removes str_type row from the data store.
        """
        current_store = self.current_data_store()

        for row_number, party_id in enumerate(current_store.party.keys()):
            self.set_str_type_data(
                0, party_id, row_number
            )
        self.reset_share_spinboxes(current_store)
        self.validate.validate_str_type_length(
            current_store, self.current_item()
        )

    def update_str_type_data(self, index: QModelIndex, data_store: STRDataStore, party_id: int):
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

    def current_data_store(self) -> STRDataStore:
        """
        Gets the current data_store object for the selected STR tree.
        :return: The current data store object
        :rtype: Object
        """
        index = self.tree_view.currentIndex()
        selected_item = self.tree_view_model.itemFromIndex(index)
        data_store_obj = self.data_store[selected_item.data()]
        return data_store_obj

    def str_editor_signals(self):
        """
        The STR editor signals used to add new STR entry node and
        save the data.
        """
        self.add_str_btn.clicked.connect(self.add_str_tree_node)
        self.remove_str_btn.clicked.connect(self.remove_str_tree_node)
        # self.buttonBox.accepted.connect(self.save_str)

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

        self.spatial_unit_component.spatial_unit_fk_mapper. \
            afterEntityAdded.connect(
            lambda model: self.mirror_map.draw_spatial_unit(
                self.spatial_unit, model
            )
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

        str_number = self.current_item().data()

        item = self.str_item(self.party_text, str_number)

        # validate party length to enable the next item
        self.validate.validate_party_length(current_data_store, item)
        current_data_store.current_party = self.party

    def set_spatial_unit_data(self, model):
        """
        Sets spatial unit date to the data store spatial unit dictionary.
        :param model: The model of the selected spatial unit record.
        :type model: SQLAlchemy Model
        """
        current_store = self.current_data_store()
        current_store.spatial_unit.clear()
        current_store.spatial_unit[model.id] = model
        current_store.current_spatial_unit = self.spatial_unit

    def set_str_type_data(self, str_type_id: int, party_id: int, row_number: int):
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
            self.party_component.party_fk_mapper._tbFKEntity, row_number
        )
        self.copied_party_row[party_id] = row_data

        self.str_type_component.add_str_type_data(
            current_store.current_spatial_unit, row_data, row_number
        )

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

    def set_validity_period_data(self, date: QDate):
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

    def supporting_doc_signals(self, str_number: int):
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

    def set_supporting_documents(self, model_objs: list):
        """
        Sets the supporting document model object list into the current store
        supporting document object.
        :param model_objs: The supporting document model object list.
        :type model_objs: List
        """
        current_store = self.current_data_store()
        current_store.supporting_document = model_objs

    def validate_str_delete(self, selected_str: list[QModelIndex]) -> bool:
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

            return False if result == QMessageBox.No else True

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

        self.validate.enable_save_button()

    def remove_str_node_models(self, str_number):
        """
        Removes the STR node data store from the data store dictionary.
        :param str_number: The STR node number
        :type str_number: Integer
        """
        del self.data_store[str_number]

    def remove_party_str_row_model(self, row_numbers):
        """
        Removes party and str_type row from the data store.
        :param row_numbers: The row numbers of removed row.
        :type row_numbers: List
        """
        current_store = self.current_data_store()

        for row_number in row_numbers:
            party_keys = list(current_store.party.keys())

            try:
                removed_key = party_keys[row_number]
                if len(current_store.custom_tenure) == len(current_store.party):
                    del current_store.custom_tenure[removed_key]
                del current_store.party[removed_key]
                del current_store.str_type[removed_key]

            except IndexError:
                pass

        self.str_type_component.remove_str_type_row(row_numbers)
        self.custom_tenure_info_component.remove_entity_editor(
            self.spatial_unit, row_numbers
        )

        self.reset_share_spinboxes(current_store)
        self.validate.validate_str_type_length(
            current_store, self.current_item()
        )

    def remove_spatial_unit_model(self):
        """
        Clears the spatial unit dictionary.
        """
        current_store = self.current_data_store()
        current_store.spatial_unit.clear()

    def accept(self):
        """
        Saves the data into the database.
        """
        current_store = self.current_data_store()
        result = self.validate.validate_custom_tenure_form()
        if not result:
            return
        if self.current_item().text() == self.custom_tenure_info_text:
            self.sync.save_custom_tenure_info(
                current_store, self.str_number
            )

        db_handler = STRDBHandler(self.data_store, self.str_model)
        db_handler.commit_str()
        self.done(1)

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
        self.updated_str_obj = None
        self.str_edit_node = str_edit_node
        self.str_edits = self.current_str_detail()
        title = QApplication.translate(
            'EditSTREditor',
            'Edit Social Tenure Relationship'
        )
        self.setWindowTitle(title)

        self.add_str_btn.setDisabled(True)
        self.remove_str_btn.setDisabled(True)
        self.party_init.connect(self.populate_party_str_type_store)
        self.spatial_unit_init.connect(self.populate_spatial_unit_store)
        for rec in self.str_edits:
            self.init_party_component(rec['party'])
            self.init_spatial_unit_component(rec['sp_unit'])

        QTimer.singleShot(33, self._party_signals)

        QTimer.singleShot(33, self.init_str_type_component)
        # QTimer.singleShot(55, lambda: self.init_spatial_unit_component(
        #         self.spatial_unit
        #     )
        # )
        QTimer.singleShot(77, self.init_supporting_documents)
        QTimer.singleShot(80, self.init_validity_period_component)
        # QTimer.singleShot(90, self.init_custom_tenure_info_component)
        self.init_custom_tenure_info_component()

        self.docs_init.connect(self.populate_supporting_doc_store)
        self.validity_init.connect(self.populate_validity_store)
        # self.custom_tenure_info_init.connect(self.populate_custom_tenure_store)
        self.populate_custom_tenure_store()

    def clear_store(self, *args):
        """
        Remove all items from a dictionary object
        :param args: Data store attributes
        :type args: Tuple
        :return: None
        :rtype: None
        """
        for store in self.data_store.values():
            for attr in args:
                getattr(store, attr).clear()

    def current_str_detail(self) -> list:
        """
        Gets the current STR party and spatial unit entity details
        :return str_edits: A list of current party and spatial unit STR details
        :rtype str_edits: List
        """
        str_edits = []
        for rec in self.str_edit_node:
            details = dict(list(zip(('str_rec', 'str_doc'), rec)))
            rec = rec[0].__dict__
            current_party_detail = self.current_party(rec)
            if current_party_detail is not None:
                details['party'], details['party_col'] = current_party_detail
            current_spatial_unit_detail = self.current_spatial_unit(rec)
            if current_spatial_unit_detail is not None:
                details['sp_unit'], details['sp_unit_col'] = current_spatial_unit_detail
            str_edits.append(details)
        return str_edits

    def init_spatial_unit_component(self, spatial_unit=None):
        """
        Initializes the spatial unit component.
        :param spatial_unit: The current spatial_unit entity.
        :type spatial_unit: Object
        """

        if spatial_unit is None:
            return
        self.spatial_unit_init.emit()

        if self.spatial_unit_component is not None:
            return
        self.spatial_unit_component = SpatialUnit(
            spatial_unit,
            self.spatial_unit_box,
            self.notice
        )
        self.spatial_unit_signals()

        self.spatial_unit_component.spatial_unit_fk_mapper.entity_combo. \
            currentIndexChanged.connect(self.switch_spatial_unit_entity)

    def populate_party_str_type_store(self):
        """
        Populates the party and STR Type store into the data store.
        """
        self.clear_store('party', 'str_type', 'share', 'custom_tenure')
        self.copied_party_row.clear()
        for idx, rec in enumerate(self.str_edits):
            str_rec = rec['str_rec']
            str_rec_dict = str_rec.__dict__
            party_id = str_rec_dict[rec['party_col']]
            party_model_obj = getattr(str_rec, rec['party'].name)
            self.data_store[1].party[party_id] = party_model_obj
            tenure_type_col = self.social_tenure.spatial_unit_tenure_column(
                rec['sp_unit'].short_name
            )
            tenure_type_name = tenure_type_col.name
            tenure_type = getattr(str_rec, tenure_type_name, None)
            self.data_store[1].str_type[party_id] = tenure_type
            self.data_store[1].current_party = rec['party']
            rec['str_type'] = tenure_type
            self.populate_str_type(rec, idx)
        doc_item = self.str_item(self.tenure_type_text, self.str_number)
        doc_item.setEnabled(True)
        self.party_component.party_fk_mapper.setSupportsList(False)
        self.set_party_active()
        self.buttonBox.button(QDialogButtonBox.Save).setEnabled(True)

    def populate_str_type(self, rec, index):
        """
        Populate the STR type combobox and the tenure share spinbox.
        :param rec: The STR record to be edited
        :type rec: Dict
        :param index: The STR record index
        :type index: Integer
        """
        str_rec, tenure_type = rec['str_rec'], rec['str_type']
        str_rec_dict = str_rec.__dict__
        party_id = str_rec_dict[rec['party_col']]
        self.init_str_type_component()
        # populate str type column
        self.set_str_type_data(tenure_type, party_id, index)
        self.str_type_component.add_str_type_data(
            rec['sp_unit'], self.copied_party_row[party_id], 0
        )
        self.init_tenure_data(self.data_store[1], party_id, tenure_type, 1)
        self.data_store[1].share[party_id] = str_rec.tenure_share

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

        self.validate.enable_save_button()

    def populate_spatial_unit_store(self):
        """
        Populates the spatial unit data store.
        """
        self.clear_store('spatial_unit')
        for rec in self.str_edits:
            spatial_unit_model_obj = getattr(rec['str_rec'], rec['sp_unit'].name)
            self.data_store[1].spatial_unit[
                spatial_unit_model_obj.id
            ] = spatial_unit_model_obj
            self.data_store[1].current_spatial_unit = rec['sp_unit']
        doc_item = self.str_item(self.spatial_unit_text, self.str_number)
        doc_item.setEnabled(True)

    def populate_custom_tenure_store(self):
        """
        Populates the custom tenure info data store.
        """
        self.clear_store('custom_tenure')
        for rec in self.str_edits:
            party_model_obj = getattr(rec['str_rec'], rec['party'].name)
            custom_entity = self.social_tenure.spu_custom_attribute_entity(
                rec['sp_unit']
            )
            if custom_entity is None:
                return
            if len(custom_entity.columns) < 3:
                return
            custom_model = entity_attr_to_model(
                custom_entity, 'social_tenure_relationship_id', rec['str_rec'].id
            )
            self.data_store[1].custom_tenure[party_model_obj.id] = custom_model
        doc_item = self.str_item(self.custom_tenure_info_text, self.str_number)
        doc_item.setEnabled(True)

    def populate_validity_store(self):
        """
        Populates the spatial unit data store.
        """
        self.clear_store('validity_period')
        for rec in self.str_edits:
            start_date = rec['str_rec'].validity_start
            end_date = rec['str_rec'].validity_end
            self.data_store[1].validity_period['from_date'] = start_date
            self.data_store[1].validity_period['to_date'] = end_date
        doc_item = self.str_item(self.validity_period_text, self.str_number)
        doc_item.setEnabled(True)

    def populate_supporting_doc_store(self):
        """
        Initializes the supporting document page.
        """
        doc_item = self.str_item(
            self.supporting_doc_text, self.str_number
        )
        for rec in self.str_edits:
            doc = rec['str_doc']
            if len(doc) < 1:
                doc_item.setEnabled(True)
                return
            for doc_id, doc_objs in doc.items():

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

    def current_party(self, record):
        """
        Gets the current party column name in STR
        table by finding party column with value other than None.
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
            party_name = party_name.replace(' ', '_')
            party_id = '{}_id'.format(party_name)
            if party_id not in record.keys():
                return
            if record[party_id] is not None:
                return party, party_id

    def current_spatial_unit(self, record):
        """
        Gets the current spatial_units column name in STR
        table by finding spatial_unit column with value other than None.
        :param record: The STR record or result.
        :type record: Dictionary
        :return: The spatial_unit column name with value.
        :rtype: String
        """
        spatial_units = self.social_tenure.spatial_units
        if record is None:
            return
        for spatial_unit in spatial_units:
            spatial_unit_name = spatial_unit.short_name.lower()
            spatial_unit_name = spatial_unit_name.replace(' ', '_')
            spatial_units_id = '{}_id'.format(spatial_unit_name)
            if spatial_units_id not in record.keys():
                return
            if record[spatial_units_id] is not None:
                return spatial_unit, spatial_units_id

    def set_party_data(self, model):
        """
        Sets the party data from the ForeignKeyMapper model to the data store.
        :param model: The party model
        :type model: SQLAlchemy Model
        """
        store = self.current_data_store()
        store.party.clear()
        store.party[model.id] = model

    def set_str_type_data(self, str_type_id, party_id, index=0):
        """
        Sets the STR type data to the STR type data store dictionary.
        :param str_type_id: The STR type id
        :type str_type_id: Integer
        :param party_id: The party id
        :type party_id: Integer
        :param index: The STR record index
        :type index: Integer
        """
        self.data_store[1].str_type[party_id] = str_type_id
        row_data = self.str_type_component.copy_party_table(
            self.party_component.party_fk_mapper._tbFKEntity, index
        )
        self.copied_party_row[party_id] = row_data

    def accept(self):
        """
        Saves the edited data into the database.
        """
        current_store = self.current_data_store()

        result = self.validate.validate_custom_tenure_form()
        if not result:
            return
        if self.current_item().text() == self.custom_tenure_info_text:
            self.sync.save_custom_tenure_info(current_store, self.str_number)

        db_handler = STRDBHandler(
            self.data_store, self.str_model, self.str_edit_node
        )
        self.updated_str_obj = db_handler.commit_str()
        self.done(1)
