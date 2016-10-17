from collections import OrderedDict

from PyQt4.QtCore import Qt
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
    QDialog
)
from stdm.settings import current_profile
from stdm.ui.sourcedocument import SourceDocumentManager
from ui_str_editor import Ui_STREditor
from str_components import (
    Party,
    SpatialUnit,
    STRType,
    SupportingDocuments
)
from str_data import STRDataStore

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

        self.str_type_component = None
        QTimer.singleShot(22, self.init_party_component)
        self.tree_view.clicked.connect(self.bind_component_to_tree_view)
        self.tree_view.clicked.connect(self.sync_data)
        self.splitter.isCollapsible(False)
        self.splitter.setSizes([220, 550])
        self.splitter.setChildrenCollapsible(False)
        self.buttonBox.accepted.connect(self.test_save_str)
        self.copied_party_row = OrderedDict()


    def init_party_component(self):
        if self.party_component is not None:
            return
        self.party_component = Party(
            self.componentPage2, self.str_notification
        )
        self.str_model, self.str_doc_model = \
            self.party_component.str_doc_models()

    def init_str_type_component(self):
        # Init STR Type
        if self.str_type_component is not None:
            return
        self.str_type_component = STRType(
            self.str_type_widget,
            self.str_type_box,
            self.str_notification
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
        # index = self.tree_view.currentIndex()
        # current_item = self.tree_view_model.itemFromIndex(index)
        # str_number = current_item.data()
        if self.supporting_doc_component is not None:
            return
        self.supporting_doc_component = SupportingDocuments(
            self.supporting_doc_box,
            self.doc_type_cbo,
            self.add_documents_btn,
            self.str_notification
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
        #self.str_node()

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
        #unique_data = '{}-{}'.format(name, self.str_number)
        item.setData(self.str_number)
        str_root.appendRow([item])

    def add_str_tree_node(self):
        self.str_number = self.str_number + 1
        self.str_node()
        if self.supporting_doc_component is not None:
            self.supporting_doc_component.update_str_number(self.str_number)
            self.supporting_doc_component.create_doc_tab()
            self.supporting_doc_component.init_document_add()

    def remove_str_tree_node(self):
        indexes = self.tree_view.selectedIndexes()
        for index in indexes:
            selected_item = self.tree_view_model.\
                itemFromIndex(index)
            selected_item.removeRow(
                index.row()
            )

    def bind_component_to_tree_view(self, index):
        selected_item = self.tree_view_model.itemFromIndex(index)
        str_number = selected_item.data()
        # data_store = self.data_store[str_number]

        if selected_item.text() == 'Social Tenure Relationship {}'\
                .format(str_number):
            self.component_container.setCurrentIndex(0)
            self.top_description.setCurrentIndex(0)

        if selected_item.text() == 'Party':
            QTimer.singleShot(50, self.init_str_type_component)
            QTimer.singleShot(50, self.init_spatial_unit_component)
            self.component_container.setCurrentIndex(1)
            self.top_description.setCurrentIndex(1)

            self.party_component.party_fk_mapper.beforeEntityAdded.connect(
                lambda model:self.set_party_data(model, self.data_store)
            )
            self.party_component.party_fk_mapper.afterEntityAdded.connect(
                lambda model: self.set_str_type_data(self.data_store, 0, model)
            )

        if selected_item.text() == 'Spatial Unit':
            self.component_container.setCurrentIndex(2)
            self.mirror_map.set_iface(self.iface)
            self.mirror_map.load_web_map()

            self.spatial_unit_component.spatial_unit_fk_mapper.\
                beforeEntityAdded.connect(
                lambda model: self.set_spatial_unit_data(
                    model, self.data_store
                )
            )
            self.top_description.setCurrentIndex(2)

        if selected_item.text() == 'Tenure Type':
            self.component_container.setCurrentIndex(3)
            QTimer.singleShot(50, self.init_supporting_documents)
            self.top_description.setCurrentIndex(3)

        if selected_item.text() == 'Supporting Documents':
            self.component_container.setCurrentIndex(4)
            self.top_description.setCurrentIndex(4)
            self.supporting_doc_component.onUploadDocument.connect(
                lambda model_objs: self.set_supporting_documents(
                    model_objs, self.data_store
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
            self.toggle_supporting_doc_models(data_store, str_number)
    def get_table_data(self, table_view):
        model = table_view.model()
        table_data = []
        spatial_unit_idx = model.index(0, 0)
        table_data.append(model.data(
            spatial_unit_idx, Qt.DisplayRole
        ))
        print table_data

    def toggle_party_models(self, fk_mapper, data_store):
        fk_mapper.remove_rows()

        for i, model_obj in enumerate(data_store.party.values()):
            fk_mapper.insert_model_to_table(
                model_obj
            )

    def toggle_spatial_unit_models(self, fk_mapper, data_store):
        fk_mapper.remove_rows()

        for i, model_obj in enumerate(data_store.spatial_unit.values()):
            fk_mapper.insert_model_to_table(
                model_obj
            )

    def toggle_str_type_models(self, data_store):
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

    def toggle_supporting_doc_models(self, data_store, str_number):
        self.supporting_doc_component.update_str_number(str_number)
        self.supporting_doc_component.init_document_add()

    def set_party_data(self, model, store):
        data_store_obj = self.current_data_store(store)
        data_store_obj.party[model.id] = model


    def set_spatial_unit_data(self, model, store):

        data_store_obj = self.current_data_store(store)
        data_store_obj.spatial_unit[model.id] = model

    def set_str_type_data(self, store, str_type_id, model):
        party_id = model.id
        data_store_obj = self.current_data_store(store)
        data_store_obj.str_type[party_id] = str_type_id
        row_data = self.str_type_component.copy_party_table(
            self.party_component.party_fk_mapper._tbFKEntity,
            len(data_store_obj.str_type) - 1
        )

        self.copied_party_row[party_id] = row_data

    def set_supporting_documents(self, model_objs, store):
        data_store_obj = self.current_data_store(store)

        data_store_obj.supporting_document.extend(
            model_objs
        )

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

    def test_save_str(self):
        print self.data_store
        for key, value in self.data_store.iteritems():
            print key, value.party
            print key, value.spatial_unit
            print key, value.str_type
            print key, value.supporting_document
