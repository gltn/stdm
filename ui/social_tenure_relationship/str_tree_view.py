from collections import OrderedDict

from PyQt4.QtCore import QRect
from PyQt4.QtCore import Qt
from PyQt4.QtCore import (
    pyqtSignal,
    QTimer
)
from PyQt4.QtGui import QComboBox
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import (
    QIcon,
    QStandardItemModel,
    QStandardItem,
    QTreeView,
    QApplication,
    QDialog,
    QAbstractItemView,
    QWidget
)
from PyQt4.QtGui import QSizePolicy
from PyQt4.QtGui import QSpacerItem
from PyQt4.QtGui import QVBoxLayout
from stdm.settings import current_profile
from stdm.ui.sourcedocument import SourceDocumentManager
from ui_str_editor import Ui_STREditor
from str_components import (
    Party,
    SpatialUnit,
    STRType,
    SupportingDocuments
)
from str_data import STRDataStore, STRDBHandler

class STRTreeView(QDialog, Ui_STREditor):
    PartyClicked = pyqtSignal()
    SpatialUnitClicked = pyqtSignal()

    def __init__(self, iface):
        QDialog.__init__(self, iface.mainWindow())
        self.setupUi(self)
        self.iface = iface
        self.str_number = 0
        self.data_store = OrderedDict()
        self.init_tree_view()
        self.supporting_doc_component = None

        self.add_str_tree_node()
        self.add_str_btn.clicked.connect(self.add_str_tree_node)
        self.remove_str_btn.clicked.connect(self.remove_str_tree_node)
        self.current_profile = current_profile()
        self.social_tenure = self.current_profile.social_tenure
        self.party_component = None
        self.str_model = None
        self.str_doc_model = None
        self.spatial_unit_component = None
        self.str_type_combo_connected = []

        self.party_group = [self.social_tenure.party, self.social_tenure.spatial_unit]
        self.entity_combo = QComboBox()

        self.str_type_component = None
        # TODO use the first party entity among many, if many or the only one
        QTimer.singleShot(22, self.init_party_component)
        self.tree_view.clicked.connect(self.bind_component_to_tree_view)
        self.tree_view.clicked.connect(self.sync_data)
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
        self.tree_view.setRootIsDecorated(True)
        self.splitter.isCollapsible(False)
        self.splitter.setSizes([220, 550])
        self.splitter.setChildrenCollapsible(False)
        self.buttonBox.accepted.connect(self.test_save_str)
        #self.buttonBox.accepted.connect(self.save_str)
        self.copied_party_row = OrderedDict()
        self.init_party_entity_combo()

    def party_entity_combo_signal(self):

        self.entity_combo.currentIndexChanged.connect(
            self.switch_entity
        )

    def init_party_entity_combo(self):
        self.entity_combo = QComboBox()

        spacer_item = QSpacerItem(
            400, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)
        horizontal = QHBoxLayout()
        horizontal.addItem(spacer_item)
        horizontal.addWidget(self.entity_combo)

        self.party_layout.addLayout(horizontal)
        self.entity_combo.setMaximumWidth(200)
        self.entity_combo.setMinimumWidth(100)

        # self.entity_combo.move(200, 20)
        self.entity_combo.setVisible(True)
        for entity in self.party_group:
            self.entity_combo.addItem(
                entity.short_name, entity.name
            )
        self.party_layout.setAlignment(Qt.AlignRight)



    def init_party_component(self, party=None):
        if self.party_component is not None:
            return

        self.party_component = Party(
            party, self.componentPage2, self.party_layout, self.str_notification
        )
        # self.horizontalLayout.addWidget(self.entity_combo)


        self.str_model, self.str_doc_model = \
            self.party_component.str_doc_models()
        self.party_entity_combo_signal()


    def init_str_type_component(self, party=None):
        # Init STR Type
        if self.str_type_component is not None:
            return
        self.str_type_component = STRType(
            self.str_type_widget,
            self.str_type_box,
            self.str_notification,
            party
        )

        # self.str_type_component.str_type_add_signals(
        #     self.party_component.party_fk_mapper,
        # )

    def init_spatial_unit_component(self):

        if self.spatial_unit_component is not None:
            return
        self.spatial_unit_component = SpatialUnit(
            self.spatial_unit_box,
            self.mirror_map,
            self.str_notification
        )

    def init_supporting_documents(self):
        if self.supporting_doc_component is not None:
            return
        self.supporting_doc_component = SupportingDocuments(
            self.supporting_doc_box,
            self.doc_type_cbo,
            self.add_documents_btn,
            self.str_notification
        )
        self.supporting_doc_component.add_documents_btn.clicked.connect(
            lambda :self.supporting_doc_component.on_upload_document()
        )
        self.set_str_doc_models()

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

    def str_children(self, str_root):
        children = OrderedDict()
        children['Party'] = 'user.png'
        children['Spatial Unit'] = 'property.png'
        children['Tenure Type'] = 'social_tenure.png'
        children['Supporting Documents'] = 'document.png'
        for name, icon in children.iteritems():
            self.child_item(str_root, name, icon)

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
        str_root.appendRow([item])

    def add_str_tree_node(self):
        self.str_number = self.str_number + 1
        self.str_node()

        print self.tree_view_model.rowCount()

    def remove_str_tree_node(self):
        index = self.tree_view.selectedIndexes()[0]
        selected_item = self.tree_view_model.itemFromIndex(index)
        str_number = selected_item.data()
        self.tree_view_model.removeRows(index.row(), 1)
        self.remove_str_node_models(str_number)
        # TODO fix deletion error for a tree view without selection of a row


    def remove_str_node_models(self, str_number):
        del self.data_store[str_number]

    def remove_party_str_row_model(self, store, row_numbers):
        #TODO fix index error
        #TODO fix deletion error for a record without selection of a row
        party_store = self.current_data_store(self.data_store)
        party_keys = party_store.party.keys()
        for row_number in row_numbers:
            removed_key = party_keys[row_number]
            print removed_key, row_number
            del party_store.party[removed_key]

        self.str_type_component.remove_str_type_row(row_numbers)

    def bind_component_to_tree_view(self, index):
        selected_item = self.tree_view_model.itemFromIndex(index)
        str_number = selected_item.data()
        data_store = self.data_store[str_number]

        if selected_item.text() == 'Social Tenure Relationship {}'\
                .format(str_number):
            self.bind_str()

        if selected_item.text() == 'Party':
            self.bind_party(data_store)


        if selected_item.text() == 'Spatial Unit':
            self.bind_spatial_unit(data_store)

        if selected_item.text() == 'Tenure Type':
            self.bind_tenure_type()


        if selected_item.text() == 'Supporting Documents':
            self.bind_supporting_documents(data_store, str_number)

    def bind_str(self):
        self.component_container.setCurrentIndex(0)
        self.top_description.setCurrentIndex(0)

    def switch_entity(self, index):
        table = self.entity_combo.itemData(index)
        new_entity = self.current_profile.entity_by_name(table)
       # layout = self.componentPage2.findChild(QVBoxLayout)
       #  print layout

        self.party_component.party_fk_mapper.setParent(None)

        self.party_component = None

        self.init_party_component(new_entity)


        # vertical_layout = QVBoxLayout()
        self.party_layout.addWidget(self.party_component.party_fk_mapper)
        self.party_component.party_fk_mapper.show()

        self.str_type_component.str_type_table.setParent(None)

        self.str_type_component = None

        self.init_str_type_component(new_entity)


        # self.componentPage2.setLayout(vertical_layout)
        # for item in self.componentPage2.findChildren(QWidget):
        #     print item, item.objectName()
        #self.party_component.party_fk_mapper.show()

    def bind_party(self, data_store):

        QTimer.singleShot(50, self.init_str_type_component)
        QTimer.singleShot(50, self.init_spatial_unit_component)
        self.component_container.setCurrentIndex(1)
        self.top_description.setCurrentIndex(1)
        self.party_component.party_fk_mapper.beforeEntityAdded.connect(
            lambda model: self.set_party_data(model, data_store)
        )
        self.party_component.party_fk_mapper.afterEntityAdded.connect(
            lambda model, row_number: self.set_str_type_data(
                data_store, 0, model.id, row_number
            )
        )

        self.party_component.party_fk_mapper.deletedRows.connect(
            lambda removed_rows: self.remove_party_str_row_model(
                self.data_store, removed_rows
            )
        )



    def bind_spatial_unit(self, data_store):
        self.component_container.setCurrentIndex(2)
        self.mirror_map.set_iface(self.iface)
        self.mirror_map.load_web_map()
        self.spatial_unit_component.spatial_unit_fk_mapper. \
            beforeEntityAdded.connect(
            lambda model: self.set_spatial_unit_data(
                model, data_store
            )
        )
        self.top_description.setCurrentIndex(2)

    def bind_tenure_type(self):
        self.component_container.setCurrentIndex(3)
        QTimer.singleShot(50, self.init_supporting_documents)
        self.top_description.setCurrentIndex(3)

    def bind_supporting_documents(self, data_store, str_number):
        self.component_container.setCurrentIndex(4)
        self.top_description.setCurrentIndex(4)
        self.doc_type_cbo.currentIndexChanged.connect(
            lambda: self.supporting_doc_component.
                update_container(str_number)
        )
        self.supporting_doc_component.onUploadDocument.connect(
            lambda model_objs: self.set_supporting_documents(
                model_objs, data_store
            )
        )

    def sync_data(self, index):
        selected_item = self.tree_view_model.itemFromIndex(index)
        str_number = selected_item.data()
        data_store = self.data_store[str_number]


        if selected_item.text() == 'Party':
            self.toggle_party_models(
                self.party_component.party_fk_mapper, data_store
            )
        if selected_item.text() == 'Spatial Unit':
            self.toggle_spatial_unit_models(
                self.spatial_unit_component.spatial_unit_fk_mapper,
                data_store
            )
        if selected_item.text() == 'Tenure Type':
            self.toggle_str_type_models(data_store)

        if selected_item.text() == 'Supporting Documents':
            self.toggle_supporting_doc(
                data_store, str_number
            )

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

    def set_party_data(self, model, store):
        store.party[model.id] = model

    def set_spatial_unit_data(self, model, store):

        store.spatial_unit[model.id] = model

    def set_str_type_data(
            self, store, str_type_id, party_id, row_number
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

        store.str_type[party_id] = str_type_id
        row_data = self.str_type_component.copy_party_table(
            self.party_component.party_fk_mapper._tbFKEntity,
            row_number
        )
        #self.str_type_component.enable_str_type_combo(row_number)

        self.copied_party_row[party_id] = row_data


        #self.init_str_type_signal(data_store_obj, party_id, row_number)

        # QTimer.singleShot(
        #     1000, lambda:
        #     self.init_str_type_signal(data_store_obj, party_id, row_number)
        # )

    def set_supporting_documents(self, model_objs, store):

        store.supporting_document = model_objs

    def current_data_store(self, store):
        index = self.tree_view.currentIndex()
        selected_item = self.tree_view_model.itemFromIndex(index)
        data_store_obj = store[selected_item.data()]
        return data_store_obj

    def validate_page(self, index):
        selected_item = self.tree_view_model.itemFromIndex(index)
        if selected_item.text() == 'Social Tenure Relationship':
            pass
        if selected_item.text() == 'Party':
            pass
        if selected_item.text() == 'Spatial Unit':
            pass
        if selected_item.text() == 'Tenure Type':
            pass
        if selected_item.text() == 'Supporting Documents':
            pass

    def add_data(self, index):
        selected_item = self.tree_view_model.itemFromIndex(index)
        if selected_item.text() == 'Social Tenure Relationship':
            pass
        if selected_item.text() == 'Party':
            pass
        if selected_item.text() == 'Spatial Unit':
            pass
        if selected_item.text() == 'Tenure Type':
            pass
        if selected_item.text() == 'Supporting Documents':
            pass

    def remove_data(self, index):
        selected_item = self.tree_view_model.itemFromIndex(index)
        str_number = selected_item.data()

        self.str_root[str_number].removeRows(index.row(), 5)
        if selected_item.text() == 'Social Tenure Relationship':
            pass
        if selected_item.text() == 'Party':
            pass
        if selected_item.text() == 'Spatial Unit':
            pass
        if selected_item.text() == 'Tenure Type':
            pass
        if selected_item.text() == 'Supporting Documents':
            pass



    def save_str(self):
        db_handler = STRDBHandler(self.data_store, self.str_model)
        db_handler.save_str()


    def test_save_str(self):
        print self.data_store
        for key, value in self.data_store.iteritems():
            print key, value.party
            print key, value.spatial_unit
            print key, value.str_type
            print key, value.supporting_document

