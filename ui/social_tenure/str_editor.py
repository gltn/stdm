from collections import OrderedDict

from PyQt4.QtCore import QRegExp
from PyQt4.QtCore import (
    pyqtSignal,
    QTimer,
    Qt
)
from PyQt4.QtGui import QDoubleSpinBox

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
    SupportingDocuments,
    ValidityPeriod
)
from stdm.utils.util import (
    format_name
)
from str_data import STRDataStore, STRDBHandler

class InitSTREditor(QDialog, Ui_STREditor):

    partyInit = pyqtSignal()
    spatialUnitInit = pyqtSignal()
    validity_init = pyqtSignal()
    docsInit = pyqtSignal()
    strTypeUpdated = pyqtSignal()
    shareUpdated = pyqtSignal(list, QDoubleSpinBox)
    shareUpdatedOnZero = pyqtSignal(float)

    def __init__(self, plugin):
        """
        Initializes the STR editor.
        :param plugin: The plugin object
        :type plugin: Object
        """
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
        # TODO Get list of party entities from the configuration
        self.parties = self.social_tenure.parties

        self.str_type_component = None
        # TODO use the first party entity among many, if many or the only one
        QTimer.singleShot(22, self.init_party_component)

        self.copied_party_row = OrderedDict()
        self.init_str_editor()

    def init_str_editor(self):
        """
        Initializes the GUI of the STR editor.
        :return:
        :rtype:
        """
        self.init_party_entity_combo()
        self.init_notification()
        self.splitter.isCollapsible(False)
        self.splitter.setSizes([220, 550])
        self.splitter.setChildrenCollapsible(False)

        self.buttonBox.button(
            QDialogButtonBox.Save
        ).setEnabled(False)
        # self.str_editor_signals()

    def init_notification(self):
        """
        Initializes the notification object and
        connects signals and slot that toggles
        top description and the notification bar.
        :return:
        :rtype:
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

    def init_tree_view(self):
        """
        Initializes the tree view and model
        and adds it into the left scrollArea.
        :return:
        :rtype:
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

    def party_signals(self):
        """
        Connects party and str_type
        related slots and signals.
        :return:
        :rtype:
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
        :return:
        :rtype:
        """
        current_store = self.current_data_store()

        for row_number in row_numbers:
            party_keys = current_store.party.keys()

            try:
                removed_key = party_keys[row_number]
                ### apply this if incrementing the
                # next spinbox is preferred over resetting.
                # spinboxes = self.str_type_component.ownership_share()
                # for spinbox in spinboxes:
                #     if spinbox in self.share_spinbox_connected:
                #         name = spinbox.objectName()
                #         split_name = name.split('_')
                #         if int(split_name[1]) == removed_key:
                #             spinbox.setValue(0.00)

                del current_store.party[removed_key]
                del current_store.str_type[removed_key]


            except IndexError:
                pass

        self.str_type_component.remove_str_type_row(row_numbers)

        self.reset_share_spinboxes(current_store)

    def party_entity_combo_signal(self):
        """
        Connects the signal or entity_combo with
        switch_entity method that toggles
        ForeignKeyMapper for each selected party entity.
        :return:
        :rtype:
        """
        self.entity_combo.currentIndexChanged.connect(
            self.switch_entity
        )

    def init_party_entity_combo(self):
        """
        Creates the party entity combobox.
        :return:
        :rtype:
        """
        self.entity_combo_label = QLabel()
        combo_text = QApplication.translate(
            'InitSTREditor', 'Select a Party Entity: '
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

        for entity in self.parties:
            self.entity_combo.addItem(
                entity.short_name, entity.name
            )
        self.party_layout.setAlignment(Qt.AlignRight)

    def top_description_visibility(self, visible):
        """
        Sets the visibility of top description.
        :param visible: A boolean that shows or
        hides top description.
        :type visible:
        :return:
        :rtype:
        """
        if visible:
            self.top_description.show()
        else:
            self.top_description.hide()

    def resizeEvent(self, QResizeEvent):
        """
        Adjusts the position of the entity
        combo based on the dialog resize.
        :param QResizeEvent:
        :type QResizeEvent:
        :return:
        :rtype:
        """
        new_size = QResizeEvent.size()
        width = new_size.width()
        self.entity_combo.move(width - 127, 70)
        self.entity_combo_label.move(width - 260, 70)

    def init_party_component(self, party=None):
        """
        Initializes the party component.
        :param party: Party entity object.
        If party is none, the default party loads.
        :type party: Object
        :return:
        :rtype:
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
        self.party_signals()
        self.party_entity_combo_signal()

        self.partyInit.emit()

    def init_str_type_component(self, party=None):
        """
        Initializes the str type component.
        :param party: Party entity object.
        If party is none, the default party loads.
        :param party:
        :type party:
        :return:
        :rtype:
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
        :return:
        :rtype:
        """
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
        """
        Initialize the supporting documents component.
        :return:
        :rtype:
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
        self.docsInit.emit()

    def init_validity_period_component(self):
        if self.validity_period_component is not None:
            return
        self.validity_period_component = ValidityPeriod(self)
        self.validity_period_signals()
        self.validity_init.emit()

    def init_str_type_signal(self, data_store, party_id, str_number):
        """
        Connects str type combobox signals to a slot.
        :param data_store: Current datastore
        :type data_store: Dictionary
        :param party_id: The added party model id.
        :type party_id: String
        :return:
        :rtype:
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
        row_count = len(data_store.party)
        spinboxes = self.str_type_component.ownership_share()
        for spinbox in spinboxes:
            if spinbox in self.share_spinbox_connected:
                str_number, party_id, current_row = \
                    self.extract_from_object_name(spinbox)

                self.blockSignals(True)
                spinbox.setValue(100.00 / row_count)
                self.blockSignals(False)
                data_store.share[party_id] = 100.00 / row_count

    def init_share_spinboxes(self, data_store, row_count):
        spinboxes = self.str_type_component.ownership_share()
        for spinbox in spinboxes:
            if spinbox in self.share_spinbox_connected:
                str_number, party_id, current_row = \
                    self.extract_from_object_name(spinbox)
                if party_id in data_store.share.keys():

                    self.blockSignals(True)
                    if data_store.share[party_id] is None:
                        spinbox.setValue(100.00)
                    else:
                        spinbox.setValue(data_store.share[party_id])
                    self.blockSignals(False)

                else:
                    self.blockSignals(True)
                    spinbox.setValue(100.00/row_count)
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
            self.extract_from_object_name(current_spinbox)
        # print str_number, party_id, current_row
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

        #self.blockSignals(True)
        next_spinbox.setValue(next_value)
        #self.blockSignals(False)
        return next_spinbox

    def update_spinbox(self, increment):
        current_spinbox = self.sender()
        spinboxes = self.str_type_component.ownership_share()

        next_spinbox = self.execute_spinbox_update(
            spinboxes, current_spinbox
        )
        # if next_spinbox is None:
        #     return
        #
        self.shareUpdated.emit(spinboxes, next_spinbox)

    def update_spinbox_when_zero(self, spinboxes, next_spinbox):
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
        spinboxes = self.str_type_component.ownership_share()
        data_store = self.current_data_store()
        for spinbox in spinboxes:
            if spinbox in self.share_spinbox_connected:
                str_number_ext, party_id, current_row = \
                    self.extract_from_object_name(spinbox)
                data_store.share[party_id] = spinbox.value()

    def extract_from_object_name(self, current_spinbox):
        current_name = current_spinbox.objectName()
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
        :return:
        :rtype:
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
        :return:
        :rtype:
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
        :return:
        :rtype:
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
                '%s%s'%(name, self.str_number)
            ] = item

        self.str_items[
            '%s%s'%(self.str_text, self.str_number)
        ] = str_root
        party_item = self.str_items[
            '%s%s'%(self.party_text, self.str_number)
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
        :return:
        :rtype:
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
        :return:
        :rtype:
        """
        item = self.str_items['%s%s'%(text, str_number)]
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
        :return:
        :rtype:
        """
        table = self.entity_combo.itemData(index)
        new_entity = self.current_profile.entity_by_name(table)
        self.party = new_entity
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
        """
        Clear party and STR type store
        on switch of the party entity.
        :return:
        :rtype:
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
        :return:
        :rtype:
        """
        str_combo = self.sender()
        str_type_id = str_combo.itemData(index)
        data_store.str_type[party_id] = str_type_id
        self.strTypeUpdated.emit()

    def current_data_store(self):
        index = self.tree_view.currentIndex()
        selected_item = self.tree_view_model.itemFromIndex(index)
        data_store_obj = self.data_store[selected_item.data()]
        return data_store_obj

class BindSTREditor(InitSTREditor):
    def __init__(self, plugin):
        InitSTREditor.__init__(self, plugin)

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
        if selected_item.text() == self.validity_period_text:
            self.bind_validity_period()

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
        self.entity_combo.setHidden(False)
        self.entity_combo_label.setHidden(False)

    def bind_spatial_unit(self):
        self.notice.clear()
        self.component_container.setCurrentIndex(2)
        self.mirror_map.set_iface(self.iface)
        self.mirror_map.refresh_canvas_layers()
        self.mirror_map.load_web_map()
        self.top_description.setCurrentIndex(2)
        self.entity_combo.setHidden(True)
        self.entity_combo_label.setHidden(True)

    def bind_tenure_type(self):
        self.notice.clear()
        self.component_container.setCurrentIndex(3)
        QTimer.singleShot(50, self.init_supporting_documents)
        QTimer.singleShot(50, self.init_validity_period_component)
        self.top_description.setCurrentIndex(3)

        self.entity_combo.setHidden(True)
        self.entity_combo_label.setHidden(True)

    def bind_supporting_documents(self, str_number):
        self.notice.clear()
        self.component_container.setCurrentIndex(4)
        self.top_description.setCurrentIndex(4)
        self.supporting_doc_signals(str_number)
        self.entity_combo.setHidden(True)
        self.entity_combo_label.setHidden(True)

    def bind_validity_period(self):
        self.notice.clear()
        self.component_container.setCurrentIndex(5)
        self.top_description.setCurrentIndex(5)
        #self.supporting_doc_signals(str_number)
        self.entity_combo.setHidden(True)
        self.entity_combo_label.setHidden(True)

class SyncSTREditorData(BindSTREditor):
    def __init__(self, plugin):
        BindSTREditor.__init__(self, plugin)

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
            self.toggle_str_type_models(data_store, str_number)

        if selected_item.text() == self.supporting_doc_text:
            self.toggle_supporting_doc(
                data_store, str_number
            )
        if selected_item.text() == self.validity_period_text:
            self.toggle_validity_period(data_store, str_number)

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

    def toggle_str_type_models(self, data_store, str_number):

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
        # self.str_type_component.str_type_table.selectColumn(0)

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
        self.init_share_spinboxes(data_store, party_count)

    def toggle_supporting_doc(self, data_store, str_number):
        party_count = len(data_store.party)
        # update party count
        self.supporting_doc_component.party_count(party_count)
        # update the current widget container widget to be used.
        self.supporting_doc_component.update_container(str_number)

    def toggle_validity_period(self, data_store, str_number):
        from_date = data_store.validity_period['from_date']
        to_date = data_store.validity_period['to_date']
        if from_date is None or to_date is None:
            data_store.validity_period['from_date'] = \
                self.validity_from_date.date()
            data_store.validity_period['to_date'] = \
                self.validity_to_date.date()
        else:
            self.validity_from_date.setDate(from_date)
            self.validity_to_date.setDate(to_date)

class ValidateSTREditor(SyncSTREditorData):
    def __init__(self, plugin):
        SyncSTREditorData.__init__(self, plugin)

    def validate_page(self, current, previous):
        """
        Validates str components pages when tree item is clicked.
        :param current: The newly clicked item index
        :type current: QModelIndex
        :param previous: The previous item index
        :type previous: QModelIndex
        :return:
        :rtype:
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
            self.enable_next(selected_item, 4, True)
            self.enable_save_button()

    def validation_error(self, index):
        item = self.tree_view_model.itemFromIndex(index)
        if item is None:
            return
        if not item.isEnabled():
            warning = 'You should first select a ' \
                      'record in the enabled items to open the ' \
                      '%s component.'%item.text()
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
        #TODO add a session rollback here and show error.
        current = self.spatial_unit_current_usage_count(model_obj.id)
        return current + usage_count.spatial_unit_count


class STREditor(ValidateSTREditor):
    def __init__(self, plugin):
        InitSTREditor.__init__(self, plugin)
        self._plugin = plugin

        self.str_editor_signals()
        # self.validator = ValidateSTREditor(plugin)
        # self.sync = SyncSTREditorData(plugin)
        # self.bind = BindSTREditor(plugin)
        self.tree_view_signals()

    def str_editor_signals(self):
        self.add_str_btn.clicked.connect(
            self.add_str_tree_node
        )
        self.remove_str_btn.clicked.connect(
            self.remove_str_tree_node
        )
        self.buttonBox.accepted.connect(self.test_save_str)
        self.buttonBox.accepted.connect(self.save_str)

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

        self.str_type_component.add_str_type_data(
            row_data, str_type_id, row_number
        )
    def validity_period_signals(self):
        self.validity_from_date.dateChanged.connect(
            self.set_validity_period_data
        )
        self.validity_to_date.dateChanged.connect(
            self.set_validity_period_data
        )

    def set_validity_period_data(self, date):
        store = self.current_data_store()
        if self.sender().objectName() == 'validity_from_date':
            store.validity_period['from_date'] = date
        else:
            store.validity_period['to_date'] = date

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

    def set_supporting_documents(self, model_objs):
        current_store = self.current_data_store()

        current_store.supporting_document = model_objs

    def tree_view_signals(self):

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

    def remove_spatial_unit_model(self):
        current_store = self.current_data_store()
        current_store.spatial_unit.clear()

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
            print key, value.validity_period
            print key, value.share

    def message(self, title, message, type='information', yes_no=False):
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

    def __init__(self, plugin, str_edit_node):
        STREditor.__init__(self, plugin)

        self.str_edit_node = str_edit_node
        try:
            self.str_edit_obj = str_edit_node.model()
            self.str_doc_edit_obj = str_edit_node.documents()
        except AttributeError:
            self.str_edit_obj = str_edit_node[0]
            self.str_doc_edit_obj = str_edit_node[1]

        self.updated_str_obj = None
        self.str_edit_dict = self.str_edit_obj.__dict__
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

        self.partyInit.connect(self.populate_party_str_store)
        self.spatialUnitInit.connect(self.populate_spatial_unit_store)
        self.docsInit.connect(self.populate_supporting_doc_store)
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

        for party in parties:
            party_name = party.short_name.lower()
            party_id = '{}_id'.format(party_name)
            if record[party_id] != None:
                return party, party_id

    def populate_party_str_store(self):

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
        tenure_share =  self.str_edit_obj.tenure_share
        self.data_store[1].share[
            party_model_obj.id
        ] = tenure_share
        QTimer.singleShot(
            40, lambda: self.populate_str_type(str_type_id)
        )
        self.party_component.party_fk_mapper.setSupportsList(False)
        self.set_party_active()

    def populate_str_type(self, str_type_id):

        self.init_str_type_component()
        party_id = self.str_edit_dict[self.party_column]
        # populate str type column
        self.set_str_type_data(
            str_type_id,
            party_id,
            0
        )
        self.str_type_component.add_str_type_data(
            self.copied_party_row[party_id],
            str_type_id,
            0
        )
        self.init_str_type_signal(
            self.data_store[1], party_id, 1
        )
        doc_item = self.str_item(
            self.tenure_type_text, self.str_number
        )

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
        self.data_store[1].spatial_unit.clear()

        self.data_store[1].spatial_unit[
            self.str_edit_obj.spatial_unit_id
        ] = spatial_unit_model_obj

        doc_item = self.str_item(
            self.spatial_unit_text, self.str_number
        )

        doc_item.setEnabled(True)

    def populate_validity_store(self):
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
        :return: None
        :rtype: NoneType
        """
        doc_item = self.str_item(
            self.supporting_doc_text, self.str_number
        )

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
        store.share.clear()

        store.str_type[party_id] = str_type_id
        # store.share[party_id] =
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
            print key, value.validity_period
            print key, value.share

