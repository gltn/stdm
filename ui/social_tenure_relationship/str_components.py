from collections import OrderedDict
from PyQt4.QtCore import (
    pyqtSignal,
    QObject,
    Qt,
    QFileInfo,
    QRegExp
)

from PyQt4.QtGui import (
    QVBoxLayout,
    QWidget,
    QGridLayout,
    QAbstractItemView,
    QApplication,
    QTabWidget,
    QScrollArea,
    QFrame,
    QFileDialog,
    QComboBox
)

# from sqlalchemy import (
#     func
# )
from qgis.utils import iface
from stdm.ui.notification import NotificationBar, ERROR, INFORMATION
from stdm.ui.sourcedocument import SourceDocumentManager
from stdm.ui.foreign_key_mapper import ForeignKeyMapper
from stdm.settings import current_profile
from stdm.data.configuration import entity_model
from stdm.utils.util import (
    format_name,
    entity_display_columns
)
from stdm.settings.registryconfig import (
    last_document_path,
    set_last_document_path
)
from stdm.ui.social_tenure_relationship.str_helpers import (
    EntityConfig, FreezeTableWidget
)

class ComponentUtility(QObject):
    def __init__(self, box):
        super(ComponentUtility, self).__init__()
        self.container_box = box
        self.current_profile = current_profile()
        self.social_tenure = self.current_profile.social_tenure
        self.party = self.social_tenure.party
        self.spatial_unit = self.social_tenure.spatial_unit
        self.str_model, self.str_doc_model = entity_model(
            self.social_tenure, False, True
        )

    def str_doc_models(self):
        return self.str_model, self.str_doc_model


    def _create_fk_mapper(
            self, config, parent, notif_bar, multi_row=True
    ):
        """
        Creates the forign key mapper object.
        :param config: Entity configuration
        :type config: Object
        :param parent: Container of the mapper
        :type parent: QWidget
        :param notif_bar: The notification bar
        :type notif_bar: QVBLayout
        :param multi_row: Boolean allowing muti-rows
        in the tableview.
        :type multi_row: Boolean
        :return:
        :rtype:
        """
        fk_mapper = ForeignKeyMapper(
            config.ds_entity, parent, notif_bar
        )
        fk_mapper.setDatabaseModel(config.model())
        fk_mapper.setSupportsList(multi_row)
        fk_mapper.setDeleteonRemove(False)
        fk_mapper.setNotificationBar(notif_bar)

        return fk_mapper


    def _entity_groups(self, type='STR'):
        if type == 'STR':
            str_entities = [
                self.current_profile.social_tenure.party,
                self.current_profile.social_tenure.spatial_unit
            ]
            return str_entities



    def _load_entity_config(self, entity):
        """
        Creates an EntityConfig object from entity.
        :param entity: The entity object
        :type entity: Object
        """
        table_display_name = format_name(entity.short_name)
        table_name = entity.name
        model = entity_model(entity)

        if model is not None:
            return EntityConfig(
                title=table_display_name,
                data_source=table_name,
                model=model,
                expression_builder=False,
                entity_selector=None
            )
        else:
            return None

    def clear_component(self):
        for widget in self.container_box.findChildren(QWidget):
            if isinstance(widget, ForeignKeyMapper):
                widget.hide()

    def update_table_view(self, table_view, str_type):
        """
        Updates a tableview by resizing row and headers
        to content size and by hiding id columns
        :param table_view: The table view to be updated.
        :type table_view: QTableView
        :param str_type: A boolean that sets if it is
        for str type table or not.
        :type str_type: Boolean
        :return: None
        :rtype: NoneType
        """
        # show grid
        table_view.setShowGrid(True)
        # set column width to fit contents
        table_view.resizeColumnsToContents()
        # set row height
        table_view.resizeRowsToContents()
        # enable sorting
        table_view.setSortingEnabled(False)
        if str_type:
            table_view.hideColumn(1)
        else:
            table_view.hideColumn(0)

    def remove_table_data(self, table_view, row_count):
        """
        Clears table rows for a table view.
        :param table_view: The table view
        to remove rows from.
        :type table_view: QTableView
        :return: None
        :rtype: NoneType
        """
        row_count = table_view.model().rowCount()

        table_view.model().removeRows(0, row_count)


class Party(ComponentUtility):
    def __init__(self, selected_party, box, party_layout, notification_bar):
        ComponentUtility.__init__(self, box)
        self.container_box = box
        self.party_layout = party_layout
        self.notification_bar = notification_bar
        self.selected_party = selected_party

        # self.party_group = [self.party, self.spatial_unit]

        self.init_party()
        #self.party_entity_combo_signal()

    #
    # def party_entities(self):
    #
    #
    # def party_entity_combo_signal(self):
    #
    #     self.party_fk_mapper.entity_combo.currentIndexChanged.connect(
    #         self.switch_entity
    #     )
    #
    #
    # def switch_entity(self, index):
    #     table = self.party_fk_mapper.entity_combo.itemData(index)
    #     self.selected_party = self.current_profile.entity_by_name(table)
    #
    #     self.party_fk_mapper.setParent(None)
    #
    #     self.init_party()
    #
    #     #
    #     #
    #     # self.init_party_component(new_entity)
    #
    #
    #     # vertical_layout = QVBoxLayout()
    #     # self.party_layout.addWidget(self.party_component.party_fk_mapper)
    #     #self.party_fk_mapper.show()


    def init_party(self):
        """
        Initialize the party page
        :returns:None
        :rtype: NoneType
        """
        #if index is None:

        if self.selected_party is None:
            entity_config = self._load_entity_config(self.party)
        else:
            entity_config = self._load_entity_config(self.selected_party)

        self.party_fk_mapper = self._create_fk_mapper(
            entity_config,
            self.container_box,
            self.notification_bar,
            self.social_tenure.multi_party
        )
        # self.party_fk_mapper.show()
        # self.party_fk_mapper.populate_entities_combo(self.party_group)
        # vertical_layout = QVBoxLayout()
        self.party_layout.addWidget(self.party_fk_mapper)
        # self.party_fk_mapper.entity_combo.currentIndexChanged.connect(
        #     self.switch_entity
        # )

        # self.container_box.setLayout(vertical_layout)

        # self.party_signals(party_fk_mapper)
        #
        # if not self.social_tenure.multi_party:

        #     self.resize_to_single_row(
        #         party_fk_mapper, self.verticalLayout_2
        #     )
    #
    # def party_signals(self, party_table):
    #     """
    #     Initializes party signals.
    #     :param party_table: The party table view
    #     :type party_table: QTableView
    #     :return: None
    #     :rtype: NoneType
    #     """
    #     # party_table.beforeEntityAdded.connect(
    #     #     lambda model_obj: self.set_model_obj(
    #     #         model_obj, self.sel_party
    #     #     )
    #     # )
    #
    #     party_table.afterEntityAdded.connect(
    #         lambda model_obj, row: self.init_str_type(
    #             party_table, 0, row
    #         )
    #     )
        #
        # # Clear str type table data if multi-party is
        # #  not allowed or on editing mode
        # if not self.social_tenure.multi_party or \
        #     self.str_edit_obj is not None:
        #     party_table.beforeEntityAdded.connect(
        #         lambda : self.erase_table_data(
        #             party_table._tbFKEntity
        #         )
        #     )
        #
        # if self.str_edit_obj is not None:
        #     party_table.beforeEntityAdded.connect(
        #         lambda: self.erase_table_data(
        #             self.str_type_table
        #         )
        #     )
        #
        # party_table.deletedRows.connect(
        #     self.remove_str_type_row
        # )
        #
        # party_table.deletedRows.connect(
        #     lambda rows: self.remove_model(rows, self.sel_party)
        # )




class SpatialUnit(ComponentUtility):
    def __init__(self, box, mirror_map, notification_bar):
        ComponentUtility.__init__(self, box)
        self.container_box = box
        self.notification_bar = notification_bar
        self.mirror_map = mirror_map
        self.init_spatial_unit()
        self.spatial_unit_fk_mapper.afterEntityAdded.connect(
            self.draw_spatial_unit
        )


    def init_spatial_unit(self):
        """
        Initialize the spatial_unit page
        :returns:None
        :rtype: NoneType
        """
        entity_config = self._load_entity_config(self.spatial_unit)
        self.spatial_unit_fk_mapper = self._create_fk_mapper(
            entity_config, self.container_box, self.notification_bar, False
        )
        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.spatial_unit_fk_mapper)
        self.container_box.setLayout(vertical_layout)
        #
        # self.spatial_unit_signals(spatial_unit_fk_mapper)
        #
        # if not self.social_tenure.multi_spatial_unit:
        #     self.resize_to_single_row(
        #         spatial_unit_fk_mapper, self.verticalLayout_2
        #     )
    # def spatial_unit_init_signals(self, party_fk_mapper):
    #     party_fk_mapper.afterEntityAdded.connect(
    #         lambda model_obj, row: self.init_spatial_unit()
    #     )

    def draw_spatial_unit(self, model):
        """
        Render the geometry of the given spatial unit in the spatial view.
        :param row_id: Sqlalchemy object representing a feature.
        """
        self.mirror_map.draw_spatial_unit(model)


class STRType(ComponentUtility):
    def __init__(self, container_widget, box, notification_bar, party=None):
        #TODO capture str type data
        ComponentUtility.__init__(self, box)
        self.container_widget = container_widget
        self.container_box = box
        self.notification_bar = notification_bar
        self.str_type_data = []
        self.selected_party = party
        self.create_str_type_table()

    def add_str_type_data(
            self,
            row_data,
            str_type_id,
            insert_row
    ):
        """
        Adds str type date into STR Type table view.
        :param row_data: The table data
        :type row_data: List
        :param str_type_id: The str Type ID
        :type str_type_id: Integer
        :return:
        :rtype:
        """
        data = [None] + row_data
        self.str_type_data.append(data)
        self.str_type_table.add_combobox(str_type_id, insert_row)

        self.str_type_table.model().layoutChanged.emit()

        #self.enable_str_type_combo(insert_row)

    def copy_party_table(self, table_view, row):
        """
        Copy rows from party table view.
        :param row: The row to be copied
        :type row: Integer
        :param table_view: The party table view
        :type table_view: QTableView
        :return: List of row data
        :rtype: List
        """
        party_row_data = []
        model = table_view.model()
        for col in range(model.columnCount()):
            party_id_idx = model.index(row, col)

            party_row_data.append(model.data(
                party_id_idx, Qt.DisplayRole
            ))
        #self.enable_str_type_combo(row)
        return party_row_data


    def add_str_type_headers(self):
        """
        Adds headers data for tableview columns. The
        headers comes from the selected entity.
        :param entity: The entity for which the table
        header is created for.
        :return: List of Table headers
        :rtype: List
        """
        if not self.selected_party is None:
            self.party = self.selected_party
        db_model = entity_model(self.party, True)
        headers = []
        #Load headers
        if db_model is not None:
            entity_display_columns(self.party)
            # Append str type if the method
            # is used for str_type
            str_type_header = QApplication.translate(
                'STRType', 'Social Tenure Type'
            )
            #First (ID) column will always be hidden
            headers.append(str_type_header)

            for col in entity_display_columns(self.party):
                headers.append(format_name(col))

            return headers

    def create_str_type_table(self):
        """
        Creates social tenure type table that is composed
        of each selected party rows with a combobox for
        social tenure type.
        """
        self.str_type_notice = NotificationBar(
            self.notification_bar
        )
        headers = self.add_str_type_headers()

        self.str_type_table = FreezeTableWidget(
            self.str_type_data, headers, self.container_widget
        )
        self.str_type_table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )
        # Hide id from STR Type table
        self.update_table_view(
            self.str_type_table, True
        )
        self.container_box.setSpacing(4)
        self.container_box.setMargin(5)
        grid_layout = QGridLayout(self.container_widget)
        grid_layout.setHorizontalSpacing(5)
        grid_layout.setColumnStretch(4, 5)
        self.container_box.addLayout(grid_layout)
        self.container_box.addWidget(self.str_type_table)
        # if len(self.sel_party) < 1:
        #     self.container_box.addLayout(grid_layout)
        #     self.container_box.addWidget(self.str_type_table)

    def enable_str_type_combo(self, row):
        """
        Makes the STR Type combobox editable.
        :param row: The row of STR Type combobox
        :type row: Integer
        :return: None
        :rtype: NoneType
        """
        model = self.str_type_table.frozen_table_view.model()
        self.str_type_table.frozen_table_view. \
            openPersistentEditor(
            model.index(row, 0)
        )

    def str_type_data(self):
        """
        Gets party and str_type data from str_type
        page (page 3 of the wizard). It uses
        get_table_data() method.
        :return: A list containing a list of ids of
        the selected str related table or str_type value.
        :rtype: List
        """
        str_types = []
        frozen_table = self.str_type_table.frozen_table_view
        combo_boxes = frozen_table.findChildren(QComboBox)

        for combo in combo_boxes:
            index = combo.currentIndex()
            str_type = combo.itemData(index)
            str_types.append(str_type)


        return str_types


    def str_type_combobox(self):
        """
        Gets party and str_type data from str_type
        page (page 3 of the wizard). It uses
        get_table_data() method.
        :return: A list containing a list of ids of
        the selected str related table or str_type value.
        :rtype: List
        """
        frozen_table = self.str_type_table.frozen_table_view
        combo_boxes = frozen_table.findChildren(QComboBox)
        return combo_boxes

    def remove_str_type_row(self, rows=[0]):
        """
        Removes corresponding social tenure type
        row when a party row is removed.
        :param rows: Party row position that is removed.
        :type rows: integer
        :returns: None
        :rtype: NoneType
        """
        for row in rows:
            self.str_type_table.model().removeRow(row)

class SupportingDocuments(ComponentUtility):
    onUploadDocument = pyqtSignal(list)
    def __init__(self, box, combobox, add_documents_btn, notification_bar):
        ComponentUtility.__init__(self, box)
        self.container_box = box
        self.doc_type_cbo = combobox
        self.notification_bar = notification_bar
        self.str_number = 1
        self.add_documents_btn = add_documents_btn
        self.str_numbers = [1]
        self.current_party_count = None
        self.init_documents()

    def init_documents(self):
        """
        Initializes the document type combobox by
        populating data.
        :return: None
        :rtype: NoneType
        """
        self.supporting_doc_manager = SourceDocumentManager(
            self.social_tenure.supporting_doc,
            self.str_doc_model,
            iface.mainWindow()
        )
        self.doc_notice = NotificationBar(
            self.notification_bar
        )

        self.create_doc_tab_populate_combobox()

        self.doc_type_cbo.currentIndexChanged.connect(
            self.match_doc_combo_to_tab
        )
        self.docs_tab.currentChanged.connect(
            self.match_doc_tab_to_combo
        )

    def party_count(self, count):
        self.current_party_count = count

    def create_doc_tab_populate_combobox(self):

        self.doc_tab_data()
        self.docs_tab = QTabWidget()
        self.docs_tab_index = OrderedDict()
        for i, (id, doc) in enumerate(self.doc_types.iteritems()):
            self.docs_tab_index[doc] = i
            # the tab widget containing the document widget layout
            # and the child of the tab.
            tab_widget = QWidget()
            tab_widget.setObjectName(doc)
            # The layout of the tab widget
            cont_layout = QVBoxLayout(tab_widget)
            cont_layout.setObjectName(
                'widget_layout_{}'.format(doc)
            )
            # the scroll area widget inside the tab widget.
            scroll_area = QScrollArea(tab_widget)
            scroll_area.setFrameShape(QFrame.NoFrame)
            scroll_area.setObjectName(
                'tab_scroll_area_{}'.format(doc)
            )

            layout_widget = QWidget()
            # the widget the is under the scroll area content and
            # the widget containing the document widget layout
            # This widget is hidden and shown based on the STR number
            layout_widget.setObjectName(
                'widget_{}'.format(doc)
            )

            doc_widget_layout = QVBoxLayout(layout_widget)
            doc_widget_layout.setObjectName(
                'doc_widget_layout_{}'.format(
                    doc
                )
            )
            doc_widget = QWidget()
            doc_widget.setObjectName(
                'doc_widget_{}_{}'.format(doc, self.str_number)
            )

            doc_widget_layout.addWidget(doc_widget)

            # the layout containing document widget.
            ### This is the layout that is registered to add uploaded
            # supporting documents widgets into.
            tab_layout = QVBoxLayout(doc_widget)
            tab_layout.setObjectName(
                'layout_{}_{}'.format(doc, self.str_number)
            )

            scroll_area.setWidgetResizable(True)
            scroll_area.setWidget(layout_widget)

            cont_layout.addWidget(scroll_area)
            # Add the tab widget with the document
            # type name to create a tab.
            self.docs_tab.addTab(tab_widget, doc)

            self.container_box.addWidget(self.docs_tab, 1)
            if len(self.str_numbers) == 1:
                self.doc_type_cbo.addItem(doc, id)

    def doc_tab_data(self):
        doc_entity = self.social_tenure. \
            supporting_doc.document_type_entity
        doc_type_model = entity_model(doc_entity)
        docs = doc_type_model()
        doc_type_list = docs.queryObject().all()
        self.doc_types = [(doc.id, doc.value)
                          for doc in doc_type_list
                          ]
        self.doc_types = OrderedDict(self.doc_types)




    def match_doc_combo_to_tab(self):
        """
        Changes the active tab based on the
        selected value of document type combobox.
        :return: None
        :rtype: NoneType
        """
        combo_text = self.doc_type_cbo.currentText()
        if combo_text is not None and len(combo_text) > 0:
            index = self.docs_tab_index[combo_text]
            self.docs_tab.setCurrentIndex(index)

    def match_doc_tab_to_combo(self):
        """
        Changes the document type combobox value based on the
        selected tab.
        :return: None
        :rtype: NoneType
        """
        doc_tab_index = self.docs_tab.currentIndex()
        self.doc_type_cbo.setCurrentIndex(doc_tab_index)

    def hide_doc_widgets(self, widget, visibility):
        widget.setHidden(visibility)

    def update_container(self, str_number):
        ##TODO add a remove method or code block here
        doc_text = self.doc_type_cbo.currentText()
        cbo_index = self.doc_type_cbo.currentIndex()
        doc_id = self.doc_type_cbo.itemData(cbo_index)
        scroll_area = self.docs_tab.findChild(
            QScrollArea, 'tab_scroll_area_{}'.format(
                doc_text, str_number
            )
        )
        doc_widget = scroll_area.findChild(
            QWidget, 'doc_widget_{}_{}'.format(
                doc_text, str_number
            )
        )
        # If the doc widget doesn't exist create it for new STR instance
        if doc_widget is None:
            # find the doc_widget layout that contains
            # all STR doc widget layouts. Single
            # doc_widget_layout is created for each document type.
            # But all doc_widgets for each STR instance and
            # document types will be added here.
            doc_widget_layout =  scroll_area.findChild(
                QVBoxLayout, 'doc_widget_layout_{}'.format(doc_text)
            )

            doc_widget = QWidget()
            doc_widget.setObjectName(
                'doc_widget_{}_{}'.format(doc_text, str_number)
            )
            self.hide_all_other_widget(doc_text, str_number)
            doc_widget_layout.addWidget(doc_widget)
            # Create the layout so that layouts are registered in
            # which uploaded document widgets are added.
            layout = QVBoxLayout(doc_widget)
            layout.setObjectName('layout_{}_{}'.format(
                    doc_text, str_number
                )
            )
        # If the doc widget exists, get the lowest
        # layout so that it is registered.
        else:
            # hide all other widgets
            self.hide_all_other_widget(doc_text, str_number)
            # show the current doc widget to display
            # the document widgets for the current tab.
            self.hide_doc_widgets(doc_widget, False)
            layout = doc_widget.findChild(
                QVBoxLayout, 'layout_{}_{}'.format(
                    doc_text, str_number
                )
            )
        # register layout
        self.supporting_doc_manager.registerContainer(
            layout, doc_id
        )

    def hide_all_other_widget(self, doc_text, str_number):
        expression = QRegExp('doc_widget*')
        # hide all existing widgets in all layouts
        for widget in self.docs_tab.findChildren(QWidget, expression):
            if widget.objectName() != 'doc_widget_{}_{}'.format(
                    doc_text, str_number):
                self.hide_doc_widgets(widget, True)

    def on_upload_document(self):
        '''
        Slot raised when the user clicks
        to upload a supporting document.
        '''
        document_str = QApplication.translate(
            "newSTRWiz",
            "Specify the Document File Location"
        )
        documents = self.select_file_dialog(document_str)

        cbo_index = self.doc_type_cbo.currentIndex()
        doc_id = self.doc_type_cbo.itemData(cbo_index)

        for doc in documents:
            self.supporting_doc_manager.insertDocumentFromFile(
                doc,
                doc_id,
                self.social_tenure,
                self.current_party_count
            )

        # Set last path
        if len(documents) > 0:
            doc = documents[0]
            fi = QFileInfo(doc)
            dir_path = fi.absolutePath()
            set_last_document_path(dir_path)

            model_objs = self.supporting_doc_manager.model_objects()
            self.onUploadDocument.emit(model_objs)

    def select_file_dialog(self, title):
        '''
        Displays a file dialog for a user
        to specify a source document
        '''
        #Get last path for supporting documents
        last_path = last_document_path()
        if last_path is None:
            last_path = '/home'

        files = QFileDialog.getOpenFileNames(
            iface.mainWindow(),
            title,
            last_path,
            "Source Documents (*.jpg *.jpeg *.png *.bmp *.tiff *.svg)"
        )
        return files


