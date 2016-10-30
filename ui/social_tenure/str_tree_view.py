from collections import OrderedDict

from PyQt4.QtCore import (
    pyqtSignal,
    QTimer,
    Qt
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
    QComboBox,
    QHBoxLayout,
    QMessageBox,
    QDialogButtonBox,
    QItemSelectionModel,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout
)
from PyQt4.QtGui import QLabel
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
    SupportingDocuments
)
from stdm.utils.util import (
    format_name
)
from str_data import STRDataStore, STRDBHandler

class STRTreeView(QDialog, Ui_STREditor):

    partyInit = pyqtSignal()
    spatialUnitInit = pyqtSignal()
    docsInit = pyqtSignal()
    strTypeUpdated = pyqtSignal()

    def __init__(self, plugin):

        # TODO add multi-party entity support to db
        QDialog.__init__(self, plugin.iface.mainWindow())
        self.setupUi(self)
        self.iface = plugin.iface
        self.str_number = 0
        self.data_store = OrderedDict()
        self.party_item_index = None
        self.init_tree_view()
        self.supporting_doc_component = None
        self.str_items = {}
        self.add_str_tree_node()

        self.current_profile = current_profile()
        self.social_tenure = self.current_profile.social_tenure
        self.party = self.social_tenure.party
        self.spatial_unit = self.social_tenure.spatial_unit
        self.party_component = None
        self.str_model = None
        self.str_doc_model = None
        self.spatial_unit_component = None

        self.str_type_combo_connected = []
        # TODO Get list of party entities from the configuration
        self.party_group = [self.party, self.spatial_unit]

        self.str_type_component = None
        # TODO use the first party entity among many, if many or the only one
        QTimer.singleShot(22, self.init_party_component)

        self.copied_party_row = OrderedDict()
        self.init_str_editor()

    def init_str_editor(self):
        self.init_party_entity_combo()
        self.init_notification()
        self.splitter.isCollapsible(False)
        self.splitter.setSizes([220, 550])
        self.splitter.setChildrenCollapsible(False)

        self.buttonBox.button(
            QDialogButtonBox.Save
        ).setEnabled(False)
        self.str_editor_signals()

    def str_editor_signals(self):
        self.add_str_btn.clicked.connect(self.add_str_tree_node)
        self.remove_str_btn.clicked.connect(
            self.remove_str_tree_node
        )
        self.buttonBox.accepted.connect(self.test_save_str)
        self.buttonBox.accepted.connect(self.save_str)

    def init_notification(self):
        self.notice = NotificationBar(
            self.str_notification
        )
        self.notice.userClosed.connect(
            lambda: self.top_description_visibility(True)
        )
        self.notice.timer.timeout.connect(
            lambda: self.top_description_visibility(True)
        )
        self.notice.onShow.connect(
            lambda: self.top_description_visibility(False)
        )

    def party_entity_combo_signal(self):

        self.entity_combo.currentIndexChanged.connect(
            self.switch_entity
        )

    def init_party_entity_combo(self):
        self.entity_combo_label = QLabel()
        combo_text = QApplication.translate(
            'STRTreeView', 'Select a Party Entity: '
        )
        self.entity_combo_label.setText(combo_text)
        self.entity_combo_label.setParent(self)
        self.entity_combo_label.resize(130, 26)
        self.entity_combo_label.move(680, 70)

        self.entity_combo = QComboBox()
        self.entity_combo.setParent(self)
        self.entity_combo.resize(100, 26)
        self.entity_combo.move(813, 70)

        self.entity_combo_label.setHidden(True)
        self.entity_combo.setHidden(True)

        for entity in self.party_group:
            self.entity_combo.addItem(
                entity.short_name, entity.name
            )
        self.party_layout.setAlignment(Qt.AlignRight)

    def top_description_visibility(self, visible):

        if visible:
            self.top_description.show()
        else:
            self.top_description.hide()

    def resizeEvent(self, QResizeEvent):
        new_size = QResizeEvent.size()
        width = new_size.width()
        self.entity_combo.move(width - 127, 70)
        self.entity_combo_label.move(width - 260, 70)

    def init_party_component(self, party=None):
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
        self.party_signals()
        self.party_entity_combo_signal()

        self.partyInit.emit()

    def init_str_type_component(self, party=None):
        # Init STR Type
        if self.str_type_component is not None:
            return
        self.str_type_component = STRType(
            self.str_type_widget,
            self.str_type_box,
            self.notice,
            party
        )

    def init_spatial_unit_component(self):

        if self.spatial_unit_component is not None:
            return
        self.spatial_unit_component = SpatialUnit(
            self.spatial_unit_box,
            self.mirror_map,
            self.notice
        )
        self.spatial_unit_signals()
        self.spatialUnitInit.emit()

    def init_supporting_documents(self):
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
        self.docsInit.emit()

    def party_signals(self):
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

    def spatial_unit_signals(self):
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
        models = self.supporting_doc_component.str_doc_models()
        self.str_model = models[0]
        self.str_doc_model = models[1]

    def init_tree_view(self):
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

        self.tree_view_signals()

    def tree_view_signals(self):
        self.view_selection.currentChanged.connect(
            self.validate_page
        )
        self.view_selection.currentChanged.connect(
            self.bind_component_to_tree_view
        )
        self.view_selection.currentChanged.connect(self.sync_data)
        self.tree_view.clicked.connect(self.validation_error)

    def str_node(self):
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
        self.str_text = QApplication.translate(
            'STRTreeView', 'Social Tenure Relationship'
        )
        self.party_text = QApplication.translate(
            'STRTreeView', 'Party'
        )
        self.spatial_unit_text = QApplication.translate(
            'STRTreeView', 'Spatial Unit'
        )
        self.tenure_type_text = QApplication.translate(
            'STRTreeView', 'Tenure Type'
        )
        self.supporting_doc_text = QApplication.translate(
            'STRTreeView', 'Supporting Documents'
        )

    def str_children(self, str_root):
        self.translate_str_items()
        children = OrderedDict()
        children[self.party_text] = 'user.png'
        children[self.spatial_unit_text] = 'property.png'
        children[self.tenure_type_text] = 'social_tenure.png'
        children[self.supporting_doc_text] = 'document.png'
        for name, icon in children.iteritems():
            item = self.child_item(str_root, name, icon)
            self.str_items[
                '%s%s'%(name, self.str_number)
            ] = item

        self.str_items[
            '%s%s'%(self.str_text, self.str_number)
        ] = str_root
        party_item = self.str_items[
            '%s%s'%(self.party_text, self.str_number)
        ]
        party_item.setEnabled(True)

    def str_item(self, text, str_number):
        item = self.str_items['%s%s'%(text, str_number)]
        return item

    def current_item(self):
        index = self.tree_view.currentIndex()
        item = self.tree_view_model.itemFromIndex(index)
        return item

    def current_str_number(self):
        item = self.current_item()
        str_number = item.data()
        return str_number

    def child_item(self, str_root, name, icon):
        q_icon = QIcon(
            ':/plugins/stdm/images/icons/{}'.format(icon)
        )
        name_text = QApplication.translate(
            'STRTreeView', name
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
        self.str_number = self.str_number + 1
        self.str_node()
        self.buttonBox.button(
            QDialogButtonBox.Save
        ).setEnabled(False)

    def validate_str_delete(self, selected_str):
        if len(selected_str) < 1:
            warning = 'Please first select on STR tree node or ' \
                      'children you would like to delete.'
            warning_message = QApplication.translate(
                'STRTreeView', warning
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
                'STRTreeView', text
            )
            title = QApplication.translate(
                'STRTreeView', text2
            )
            result = self.message(
                title, question, 'warning', True
            )
            if result == QMessageBox.No:
                return False
            else:
                return True

    def remove_str_tree_node(self):
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
        del self.data_store[str_number]

    def remove_party_str_row_model(self, row_numbers):
        current_store = self.current_data_store()

        for row_number in row_numbers:
            party_keys = current_store.party.keys()

            try:
                removed_key = party_keys[row_number]
                del current_store.party[removed_key]
                del current_store.str_type[removed_key]
            except IndexError:
                pass

        self.str_type_component.remove_str_type_row(row_numbers)

    def remove_spatial_unit_model(self):
        current_store = self.current_data_store()
        current_store.spatial_unit.clear()


    def switch_entity(self, index):
        table = self.entity_combo.itemData(index)
        new_entity = self.current_profile.entity_by_name(table)
        self.party_component.party_fk_mapper.setParent(None)
        self.party_component = None

        self.init_party_component(new_entity)
        self.party_layout.addWidget(
            self.party_component.party_fk_mapper
        )
        self.party_component.party_fk_mapper.show()
        self.clear_store_on_switch()

        self.str_type_component.str_type_table.setParent(None)
        self.str_type_component = None

        self.init_str_type_component(new_entity)
        self.party_signals()


    def clear_store_on_switch(self):
        current_store = self.current_data_store()
        current_store.party.clear()
        current_store.str_type.clear()

    def bind_component_to_tree_view(self, current, previous):
        selected_item = self.tree_view_model.itemFromIndex(current)
        if selected_item is None:
            return
        str_number = selected_item.data()

        if selected_item.text() == '{} {}'\
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

    def bind_str(self):
        self.component_container.setCurrentIndex(0)
        self.top_description.setCurrentIndex(0)
        self.entity_combo.setHidden(True)
        self.entity_combo_label.setHidden(True)

    def bind_party(self):
        QTimer.singleShot(50, self.init_str_type_component)
        QTimer.singleShot(50, self.init_spatial_unit_component)
        self.component_container.setCurrentIndex(1)
        self.top_description.setCurrentIndex(1)
        self.entity_combo.setHidden(True)
        self.entity_combo_label.setHidden(True)

    def bind_spatial_unit(self):
        self.component_container.setCurrentIndex(2)
        self.mirror_map.set_iface(self.iface)
        self.mirror_map.refresh_canvas_layers()
        self.mirror_map.load_web_map()
        self.top_description.setCurrentIndex(2)
        self.entity_combo.setHidden(True)
        self.entity_combo_label.setHidden(True)

    def bind_tenure_type(self):
        self.component_container.setCurrentIndex(3)
        QTimer.singleShot(50, self.init_supporting_documents)
        self.top_description.setCurrentIndex(3)
        self.entity_combo.setHidden(True)
        self.entity_combo_label.setHidden(True)

    def bind_supporting_documents(self, str_number):
        self.component_container.setCurrentIndex(4)
        self.top_description.setCurrentIndex(4)
        self.supporting_doc_signals(str_number)
        self.entity_combo.setHidden(True)
        self.entity_combo_label.setHidden(True)

    def supporting_doc_signals(self, str_number):
        self.doc_type_cbo.currentIndexChanged.connect(
            lambda: self.supporting_doc_component.
                update_container(str_number)
        )
        self.supporting_doc_component.onUploadDocument.connect(
            lambda model_objs: self.set_supporting_documents(
                model_objs
            )
        )

    def sync_data(self, current, previous):
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
            self.toggle_str_type_models(data_store)

        if selected_item.text() == self.supporting_doc_text:
            self.toggle_supporting_doc(
                data_store, str_number
            )

    def validate_page(self, current, previous):
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
        self.spatial_unit_component.spatial_unit_fk_mapper.\
            beforeEntityAdded.connect(
            self.validate_party_count
        )
        self.spatial_unit_component.spatial_unit_fk_mapper.\
            afterEntityAdded.connect(
            self.validate_non_multi_party
        )

    def validate_str_type(self, data_store, selected_item):
        self.strTypeUpdated.connect(
            lambda: self.validate_str_type_length(
                data_store, selected_item
            )
        )

    def enable_next(self, selected_item, child_row, enable=True):
        str_root = selected_item.parent()
        if str_root is None:
            return
        next_item = str_root.child(child_row, 0)
        next_item.setEnabled(enable)

        self.enable_save_button()

    def enable_save_button(self):
        result = self.str_validity_status()

        self.buttonBox.button(
            QDialogButtonBox.Save
        ).setEnabled(result)

    def str_validity_status(self):
        for row in range(self.tree_view_model.rowCount()):
            root = self.tree_view_model.item(row)
            for child_row in range(root.rowCount()):
                child = root.child(child_row, 0)
                if not child.isEnabled():
                    return False
        return True
    def validate_party_length(self, store, item):

        if len(store.party) < 1:
            self.enable_next(item, 1, False)
            self.enable_next(item, 2, False)
            self.enable_next(item, 3, False)
        else:
            self.enable_next(item, 1)
            if len(store.spatial_unit) > 0:
                self.enable_next(item, 2)
            self.enable_next(item, 3, False)
            self.enable_save_button()

    def validate_spatial_unit_length(self, store, item):
        if len(store.spatial_unit) < 1:
            self.enable_next(item, 2, False)
        else:
            self.enable_next(item, 2)
            self.enable_save_button()

    def validate_str_type_length(self, store, selected_item):
        if 0 in store.str_type.values() or \
                None in store.str_type.values():
            self.enable_next(selected_item, 3, False)
        else:

            self.enable_next(selected_item, 3, True)
            self.enable_save_button()

    def validation_error(self, index):
        item = self.tree_view_model.itemFromIndex(index)
        if not item.isEnabled():
            warning = 'You should first select a ' \
                      'record in the enabled items to open the ' \
                      '%s component.'%item.text()
            warning_message = QApplication.translate(
                'STRTreeView', warning
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
                self.allowed_multi_party_info(
                    browser_notif, usage_count
                )
                return True
            else:
                QTimer.singleShot(
                    40, lambda: self.remove_browser_notice(fk_mapper)
                )
                QTimer.singleShot(
                        100, lambda:self.disallow_multi_party_error(
                        browser_notif, fk_mapper
                    )
                )
                return False
        else:
            return True

    def disallow_multi_party_error(self, browser_notif, fk_mapper):
        QTimer.singleShot(
            10100, lambda: self.remove_browser_notice(fk_mapper)
        )
        spatial_unit = format_name(
            self.spatial_unit.short_name
        )
        party = format_name(
            self.party.short_name
        )
        msg = QApplication.translate(
            'STRTreeView',
            'Unfortunately, this {} has already been '
            'assigned to a {}.'.format(spatial_unit, party)
        )
        self.notice.insertErrorNotification(msg)
        if isinstance(fk_mapper, ForeignKeyMapper):
            if browser_notif is not None:
                browser_notif.insertErrorNotification(msg)

    def allowed_multi_party_info(self, browser_notif, usage_count):

        occupant = '%s(s)' % format_name(self.party.short_name)
        msg = QApplication.translate(
            'STRTreeView',
            'This {} has already been assigned to {} {}.'.format(
                format_name(self.spatial_unit.short_name),
                str(usage_count),
                occupant
            )
        )
        self.notice.insertInformationNotification(msg)
        browser_notif.insertInformationNotification(msg)

    def remove_browser_notice(self, fk_mapper):
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
        :return: None
        :rtype: NoneType
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
                self.validate_spatial_unit_length(
                    store, item
                )

    def spatial_unit_usage_count(self, model_obj):
        """
        Gets the count of spatial unit usage in the database.
        :param model_obj: Spatial unit model object
        :type model_obj: SQLAlchemy model Object
        :return:
        :rtype:
        """
        # returns the number of entries for a specific parcel.
        str_obj = self.str_model()
        usage_count = str_obj.queryObject(
            [func.count().label('spatial_unit_count')]
        ).filter(
            self.str_model.spatial_unit_id == model_obj.id
        ).first()

        return usage_count.spatial_unit_count

    def init_str_type_signal(self, data_store, party_id):

        if self.str_type_component is None:
            return
        # gets all the comboboxes including the ones in other pages.
        str_type_combos = self.str_type_component.str_type_combobox()

        for str_type_combo in str_type_combos:
            # connect comboboxes that are only newly added
            if str_type_combo not in self.str_type_combo_connected:
                str_type_combo.currentIndexChanged.connect(
                    lambda index: self.update_str_type_data(
                        index, data_store, party_id
                    )
                )
                self.str_type_combo_connected.append(str_type_combo)

    def update_str_type_data(self, index, data_store, party_id):
        str_combo = self.sender()

        str_type_id = str_combo.itemData(index)

        data_store.str_type[party_id] = str_type_id

        self.strTypeUpdated.emit()


    def get_table_data(self, table_view):
        model = table_view.model()
        table_data = []
        spatial_unit_idx = model.index(0, 0)
        table_data.append(model.data(
            spatial_unit_idx, Qt.DisplayRole
        ))

    def toggle_party_models(self, fk_mapper, data_store):
        fk_mapper.remove_rows()
        for i, model_obj in enumerate(data_store.party.values()):
            fk_mapper.insert_model_to_table(
                model_obj
            )

    def toggle_spatial_unit_models(self, fk_mapper, data_store):
        fk_mapper.remove_rows()

        for i, model_obj in enumerate(
                data_store.spatial_unit.values()
        ):
            fk_mapper.insert_model_to_table(
                model_obj
            )

    def toggle_str_type_models(self, data_store):
        #self.set_str_type_combo_data(data_store)
        party_count = len(data_store.party)

        self.str_type_component.remove_table_data(
            self.str_type_component.str_type_table,
            party_count
        )

        for i, (party_id, str_type_id) in \
                enumerate(data_store.str_type.iteritems()):

            self.str_type_component.add_str_type_data(
                self.copied_party_row[party_id],
                str_type_id,
                i
            )

            self.init_str_type_signal(
                data_store, party_id
            )


    def toggle_supporting_doc(self, data_store, str_number):
        party_count = len(data_store.party)
        # update party count
        self.supporting_doc_component.party_count(party_count)
        # update the current widget container widget to be used.
        self.supporting_doc_component.update_container(str_number)

    def set_party_data(self, model):
        current_data_store = self.current_data_store()
        current_data_store.party[model.id] = model
        item = self.str_item(self.party_text, self.str_number)
        # validate party length to enable the next item
        self.validate_party_length(current_data_store, item)

    def set_spatial_unit_data(self, model):
        current_store = self.current_data_store()
        current_store.spatial_unit.clear()
        current_store.spatial_unit[model.id] = model

    def set_str_type_data(
            self, str_type_id, party_id, row_number
    ):
        """
        Adds STR type rows using party records selected.
        :param store:
        :type store:
        :param str_type_id:
        :type str_type_id:
        :param party_id:
        :type party_id:
        :param row_number:
        :type row_number:
        :return:
        :rtype:
        """
        current_store = self.current_data_store()
        current_store.str_type[party_id] = str_type_id
        row_data = self.str_type_component.copy_party_table(
            self.party_component.party_fk_mapper._tbFKEntity,
            row_number
        )

        self.copied_party_row[party_id] = row_data
        ##TODO check if this has no effect. Added to fix miss aligned frozen tableview.
        self.str_type_component.add_str_type_data(
            row_data, str_type_id, row_number
        )

    def set_supporting_documents(self, model_objs):
        current_store = self.current_data_store()

        current_store.supporting_document = model_objs

    def current_data_store(self):
        index = self.tree_view.currentIndex()
        selected_item = self.tree_view_model.itemFromIndex(index)
        data_store_obj = self.data_store[selected_item.data()]
        return data_store_obj


    def enable_component_items(self):
        for row in range(self.tree_view_model.rowCount()):
            root = self.tree_view_model.item(row)
            for child_row in range(root.rowCount()):
                child = root.child(child_row, 0)
                child.setEnabled(True)

    def save_str(self):
        db_handler = STRDBHandler(self.data_store, self.str_model)
        db_handler.commit_str()


    def test_save_str(self):
        print self.data_store
        for key, value in self.data_store.iteritems():
            print key, value.party
            print key, value.spatial_unit
            print key, value.str_type
            print key, value.supporting_document

    def message(self, title, message, type='information', yes_no=False):
        header = QApplication.translate('STRTreeView', title)
        body = QApplication.translate('STRTreeView', message)
        buttons = None
        result = None
        if yes_no:
            buttons = QMessageBox.Yes | QMessageBox.No

        if type=='information':
            result = QMessageBox.information(
                self.iface.mainWindow(), header, body, buttons
            )

        elif type=='warning' and yes_no:
            result = QMessageBox.warning(
                self.iface.mainWindow(), header, body, buttons
            )

        return result

    def translate(self, message):
        msg = QApplication.translate('STRTreeView', message)
        return msg


class EditSTRTreeView(STRTreeView, QTreeView):

    def __init__(self, plugin, str_edit_node):
        STRTreeView.__init__(self, plugin)

        self.str_edit_node = str_edit_node
        try:
            self.str_edit_obj = str_edit_node.model()
            self.str_doc_edit_obj = str_edit_node.documents()
        except AttributeError:
            self.str_edit_obj = str_edit_node[0]
            self.str_doc_edit_obj = str_edit_node[1]

        self.updated_str_obj = None

        title = QApplication.translate(
            'newSTRWiz',
            'Edit Social Tenure Relationship'
        )
        self.setWindowTitle(title)

        self.add_str_btn.setDisabled(True)
        self.remove_str_btn.setDisabled(True)

        QTimer.singleShot(33, self.init_str_type_component)
        QTimer.singleShot(55, self.init_spatial_unit_component)
        QTimer.singleShot(77, self.init_supporting_documents)

        self.partyInit.connect(self.populate_party_str_store)
        self.spatialUnitInit.connect(self.populate_spatial_unit_store)
        self.docsInit.connect(self.populate_supporting_doc_store)

    def populate_party_str_store(self):
        party_model_obj = getattr(
            self.str_edit_obj, self.party.name
        )

        self.data_store[1].party[
            self.str_edit_obj.party_id
        ] = party_model_obj
        str_type_id = self.str_edit_obj.tenure_type
        self.data_store[1].str_type[
            self.str_edit_obj.party_id
        ] = str_type_id

        QTimer.singleShot(
            40, lambda :self.populate_str_type(str_type_id)
        )
        self.party_component.party_fk_mapper.setSupportsList(False)
        self.set_party_active()

    def populate_str_type(self, str_type_id):
        self.init_str_type_component()
        # populate str type column
        self.set_str_type_data(
            str_type_id,
            self.str_edit_obj.party_id,
            0
        )
        self.str_type_component.add_str_type_data(
            self.copied_party_row[self.str_edit_obj.party_id],
            str_type_id,
            0
        )
        self.init_str_type_signal(
            self.data_store[1], self.str_edit_obj.party_id
        )
        doc_item = self.str_item(self.tenure_type_text, self.str_number)

        doc_item.setEnabled(True)

    def set_party_active(self):
        self.component_container.setCurrentIndex(1)
        self.top_description.setCurrentIndex(1)
        # Select the party item
        self.tree_view.selectionModel().setCurrentIndex(
            self.party_item_index, QItemSelectionModel.Select
        )
        # Click on party item
        self.tree_view.clicked.emit(self.party_item_index)

        self.enable_save_button()

    def populate_spatial_unit_store(self):
        spatial_unit_model_obj = getattr(
            self.str_edit_obj, self.spatial_unit.name
        )

        self.data_store[1].spatial_unit[
            self.str_edit_obj.spatial_unit_id
        ] = spatial_unit_model_obj

        doc_item = self.str_item(self.spatial_unit_text, self.str_number)

        doc_item.setEnabled(True)

    def populate_supporting_doc_store(self):
        """
        Initializes the supporting document page.
        :return: None
        :rtype: NoneType
        """
        doc_item = self.str_item(self.supporting_doc_text, self.str_number)

        if len(self.str_doc_edit_obj) < 1:
            doc_item.setEnabled(True)
            return

        for doc_id, doc_objs in self.str_doc_edit_obj.iteritems():

            index = self.doc_type_cbo.findData(
                doc_id
            )
            doc_text = self.doc_type_cbo.itemText(index)

            layout = self.supporting_doc_component.docs_tab.findChild(
                QVBoxLayout, 'layout_{}_{}'.format(
                    doc_text, self.str_number
                )
            )

            self.supporting_doc_component.supporting_doc_manager.\
                registerContainer(
                layout, doc_id
            )
            for doc_obj in doc_objs:
                self.supporting_doc_component.supporting_doc_manager.\
                    insertDocFromModel(
                    doc_obj, doc_id
                )

        doc_item.setEnabled(True)

    def set_party_data(self, model):
        store = self.current_data_store()
        store.party.clear()
        store.party[model.id] = model

    def set_str_type_data(
            self, str_type_id, party_id, row_number
    ):
        """
        Adds STR type rows using party records selected.
        :param store:
        :type store:
        :param str_type_id:
        :type str_type_id:
        :param party_id:
        :type party_id:
        :param row_number:
        :type row_number:
        :return:
        :rtype:
        """
        store = self.current_data_store()
        store.str_type.clear()
        store.str_type[party_id] = str_type_id
        row_data = self.str_type_component.copy_party_table(
            self.party_component.party_fk_mapper._tbFKEntity,
            row_number
        )
        self.copied_party_row.clear()
        self.copied_party_row[party_id] = row_data

    def save_str(self):
        db_handler = STRDBHandler(
            self.data_store, self.str_model, self.str_edit_node
        )

        self.updated_str_obj = db_handler.commit_str()


    def test_save_str(self):
        print self.data_store
        for key, value in self.data_store.iteritems():
            print key, value.party
            print key, value.spatial_unit
            print key, value.str_type
            print key, value.supporting_document

