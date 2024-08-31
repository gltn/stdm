# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : STR Components
Description          : GUI logic classes for Social tenure module components
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
import calendar
from collections import OrderedDict
from datetime import (
    date
)

from dateutil.relativedelta import relativedelta
from qgis.PyQt.QtCore import (
    pyqtSignal,
    QObject,
    Qt,
    QFileInfo,
    QRegExp
)
from qgis.PyQt.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QGridLayout,
    QAbstractItemView,
    QApplication,
    QTabWidget,
    QScrollArea,
    QFrame,
    QFileDialog,
    QComboBox,
    QLabel,
    QMessageBox,
    QSizePolicy,
    QSpacerItem,
    QDoubleSpinBox
)
from qgis.core import QgsProject
from qgis.utils import iface

from stdm.exceptions import DummyException
from stdm.data.configuration import entity_model
from stdm.data.configuration.entity import Entity
from stdm.settings import current_profile
from stdm.settings.registryconfig import (
    last_document_path,
    set_last_document_path
)
from stdm.ui.doc_generator_dlg import (
    EntityConfig
)
from stdm.ui.foreign_key_mapper import ForeignKeyMapper
from stdm.ui.forms.editor_dialog import EntityEditorDialog
from stdm.ui.social_tenure.str_helpers import FreezeTableWidget
from stdm.ui.sourcedocument import SourceDocumentManager
from stdm.utils.util import (
    format_name,
    entity_display_columns
)
from stdm.data.configuration.columns import  GeometryColumn


class ComponentUtility(QObject):
    """
    A utility class for STR components.
    """

    def __init__(self):
        """
        Initialize the STR component class.
        """
        super(ComponentUtility, self).__init__()
        self.current_profile = current_profile()
        self.social_tenure = self.current_profile.social_tenure
        self.parties = self.social_tenure.parties
        self.spatial_units = self.social_tenure.spatial_units

        self.str_model = None
        self.str_doc_model = None
        if len(self.parties) > 0:
            self.party_1 = self.parties[0]

        if len(self.spatial_units) > 0:
            self.spatial_unit_1 = self.spatial_units[0]

        try:
            self.str_model, self.str_doc_model = entity_model(
                self.social_tenure, False, True
            )
        except DummyException as ex:
            QMessageBox.critical(
                iface.mainWindow(),
                QApplication.translate('ComponentUtility', 'Database Error'),
                str(ex)
            )

    def str_doc_models(self):
        """
        A getter method for entity model of STR model and
        supporting document model.
        :return: STR and supporting document models
        :rtype: Tuple
        """
        return self.str_model, self.str_doc_model

    def _create_fk_mapper(
            self, config: EntityConfig, parent: QWidget, notif_bar: 'NotificationBar', multi_row: bool = True,
            is_party=False, is_spatial_unit=False
    ) -> ForeignKeyMapper:
        """
        Creates the foreign key mapper object.
        :param config: Entity configuration
        :type config: Object
        :param parent: Container of the mapper
        :type parent: QWidget
        :param notif_bar: The notification bar
        :type notif_bar: QVBLayout
        :param multi_row: Boolean allowing multi-rows
        in the tableview.
        :type multi_row: Boolean
        """
        fk_mapper_cls = ForeignKeyMapper
        if is_party:
            fk_mapper_cls = PartyForeignKeyMapper
        if is_spatial_unit:
            fk_mapper_cls = SpatialUnitForeignKeyMapper
        if config is None:
            return None
        fk_mapper = fk_mapper_cls(
            config.ds_entity, parent, notif_bar
        )
        fk_mapper.setDatabaseModel(config.model())
        fk_mapper.setSupportsList(multi_row)
        fk_mapper.setDeleteonRemove(False)
        fk_mapper.setNotificationBar(notif_bar)

        return fk_mapper

    def _load_entity_config(self, entity: Entity):
        """
        Creates an EntityConfig object from entity.
        :param entity: The entity object
        :type entity: Entity
        """
        table_display_name = format_name(entity.short_name)

        table_name = entity.name
        try:
            model = entity_model(entity)
        except DummyException:
            return None

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

    def update_table_view(self, table_view, str_type):
        """
        Updates a QTableView by resizing row and headers
        to content size and by hiding id columns
        :param table_view: The table view to be updated.
        :type table_view: QTableView
        :param str_type: A boolean that sets if it is
        for str type table or not.
        :type str_type: Boolean
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
            table_view.hideColumn(2)
        else:
            table_view.hideColumn(0)

    def remove_table_data(self, table_view, row_count):
        """
        Clears table rows for a table view.
        :param table_view: The table view
        to remove rows from.
        :type table_view: QTableView
        """
        row_count = table_view.model().rowCount()

        table_view.model().removeRows(0, row_count)


class PartyForeignKeyMapper(ForeignKeyMapper):
    """
    ForeignKeyMapper wrapper class for party entity.
    """

    def __init__(self, *args, **kwargs):
        """
        Initializes PartyForeignKeyMapper.
        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        """
        super(PartyForeignKeyMapper, self).__init__(*args, **kwargs)
        self.init_party_entity_combo()

    def init_party_entity_combo(self):
        """
        Creates the party entity combobox.
        """
        self.entity_combo_label = QLabel()
        combo_text = QApplication.translate(
            'PartyForeignKeyMapper', 'Select a party entity'
        )
        self.entity_combo_label.setText(combo_text)

        self.entity_combo = QComboBox()
        self.spacer_item = QSpacerItem(
            288,
            20,
            QSizePolicy.Expanding,
            QSizePolicy.Minimum
        )
        self.grid_layout.addItem(self.spacer_item, 0, 4, 1, 1)

        self.grid_layout.addWidget(self.entity_combo_label, 0, 5, 1, 1)
        self.grid_layout.addWidget(self.entity_combo, 0, 6, 1, 1)

        self.populate_parties()

    def populate_parties(self):
        """
        Populates the party entities in the entities combobox.
        """
        self.parties = current_profile().social_tenure.parties

        for entity in self.parties:
            self.entity_combo.addItem(
                entity.short_name, entity.name
            )


class SpatialUnitForeignKeyMapper(ForeignKeyMapper):
    """
    ForeignKeyMapper wrapper class for party entity.
    """

    def __init__(self, *args, **kwargs):
        """
        Initializes SpatialUnitForeignKeyMapper.
        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        """
        super(SpatialUnitForeignKeyMapper, self).__init__(*args, **kwargs)
        self.init_spatial_unit_entity_combo()

    def init_spatial_unit_entity_combo(self):
        """
        Creates the party entity combobox.
        """
        self.entity_combo_label = QLabel()
        combo_text = QApplication.translate(
            'SpatialUnitForeignKeyMapper', 'Select a spatial unit entity'
        )
        self.entity_combo_label.setText(combo_text)

        self.entity_combo = QComboBox()
        self.spacer_item = QSpacerItem(
            288, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )
        self.grid_layout.addItem(self.spacer_item, 0, 4, 1, 1)

        self.grid_layout.addWidget(self.entity_combo_label, 0, 5, 1, 1)
        self.grid_layout.addWidget(self.entity_combo, 0, 6, 1, 1)

        self.populate_spatial_units()

    def populate_spatial_units(self):
        """
        Populates the spatial unit entities in the entities combobox.
        """
        self.spatial_units = current_profile().social_tenure.spatial_units

        for entity in self.spatial_units:
            self.entity_combo.addItem(
                entity.short_name, entity.name
            )


class Party(ComponentUtility):
    def __init__(self, selected_party: Entity, box, party_layout, notification_bar):
        """
        Handles the loading of party ForeignKeyMapper.
        :param selected_party: The currently selected party entity.
        :type selected_party: Entity
        :param box: The container widget of the component.
        :type box: QWidget
        :param party_layout: The layout containing the widget.
        :type party_layout: QVBoxLayout
        :param notification_bar: The NotificationBar object that
        displays notification.
        :type notification_bar: Object
        """
        ComponentUtility.__init__(self)
        self.container_box = box
        self.party_layout = party_layout
        self.notification_bar = notification_bar
        self.selected_party = selected_party

        self.init_party()

    def init_party(self):
        """
        Initialize the party page
        """
        QApplication.processEvents()
        if self.selected_party is None:
            entity_config = self._load_entity_config(self.party_1)
        else:
            entity_config = self._load_entity_config(self.selected_party)

        QApplication.processEvents()
        if entity_config is None:
            return

        self.party_fk_mapper = self._create_fk_mapper(
            entity_config,
            self.container_box,
            self.notification_bar,
            self.social_tenure.multi_party,
            True
        )
        if self.party_fk_mapper is None:
            return

        self.party_layout.addWidget(self.party_fk_mapper)


class SpatialUnit(ComponentUtility):
    def __init__(self, selected_spatial_unit, box, notification_bar):
        """
        Handles the loading of spatial ForeignKeyMapper and the preview map.
        :param box: The container widget of the component.
        :type box: QWidget
        :param notification_bar: The NotificationBar object that
        displays notification.
        :type notification_bar: Object
        """
        ComponentUtility.__init__(self)
        self.container_box = box
        self.notification_bar = notification_bar
        self.selected_spatial_unit = selected_spatial_unit
        self.init_spatial_unit()

    def init_spatial_unit(self):
        """
        Initialize the spatial_unit page
        """
        QApplication.processEvents()
        if self.selected_spatial_unit is None:
            entity_config = self._load_entity_config(self.spatial_unit_1)
        else:
            entity_config = self._load_entity_config(
                self.selected_spatial_unit
            )

        QApplication.processEvents()
        if entity_config is None:
            return

        self.spatial_unit_fk_mapper = self._create_fk_mapper(
            entity_config,
            self.container_box,
            self.notification_bar,
            False, False, True
        )

        if self.spatial_unit_fk_mapper is None:
            return

        vertical_layout = QVBoxLayout()

        vertical_layout.addWidget(self.spatial_unit_fk_mapper)
        self.container_box.setLayout(vertical_layout)


    def notify_no_base_layers(self):
        """
        Checks if there are any base layers that will be used when
        visualizing the spatial units. If there are no base layers
        then insert warning message.
        """
        num_layers = len(QgsProject.instance().mapLayers())
        if num_layers == 0:
            msg = QApplication.translate(
                'SpatialUnit',
                'No basemap layers are loaded in the '
                'current project. Basemap layers '
                'enhance the visualization of spatial units.'
            )
            self.notification_bar.insertWarningNotification(msg)


class STRType(ComponentUtility):
    def __init__(self, container_widget, notification_bar, party=None):
        """
        Handles the STR type component for loading tenure type and share
        widgets in a QTableView.
        :param container_widget: The container widget for the component.
        :type container_widget: QWidget
        :param notification_bar: The NotificationBar object that
        displays notification.
        :type notification_bar: Object
        :param party: The party entity from with STR type component rows are
        populated. By default, if None, the first party component is used.
        :type party: Object
        """
        ComponentUtility.__init__(self)
        self.container_widget = container_widget
        self.notification_bar = notification_bar
        self.str_type_data = []
        self.selected_party = party
        self.create_str_type_table()

    def add_str_type_data(self, spatial_unit, row_data, insert_row):
        """
        Adds str type date into STR Type table view.
        :param row_data: The table data
        :type row_data: List
        :param insert_row: The row in which the STR type row is is added.
        :type insert_row: Integer
        """
        data = [None, None] + row_data
        self.str_type_data.append(data)
        self.str_type_table.add_widgets(spatial_unit, insert_row)

        self.update_table_view(self.str_type_table, True)

        self.str_type_table.model().layoutChanged.emit()
        # select the first column (STR Type)
        self.str_type_table.frozen_table_view.selectColumn(0)

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
            party_row_data.append(model.data(party_id_idx, Qt.DisplayRole))

        return party_row_data

    def add_str_type_headers(self):
        """
        Adds headers data for QTableView columns. The
        headers comes from the selected entity.
        :param entity: The entity for which the table
        header is created for.
        :return: List of Table headers
        :rtype: List
        """
        if not self.selected_party is None:
            self.party_1 = self.selected_party
        db_model = entity_model(self.party_1, True)
        headers = []
        # Load headers
        if db_model is not None:

            # Append str type if the method
            # is used for str_type
            str_type_header = QApplication.translate(
                'STRType', 'Social Tenure Type'
            )
            share_header = QApplication.translate(
                'STRType', 'Share         '
            )
            # First (ID) column will always be hidden
            headers.append(str_type_header)
            headers.append(share_header)
            display_columns = entity_display_columns(self.party_1, True)

            for col in display_columns.values():
                headers.append(col)

            return headers

    def create_str_type_table(self):
        """
        Creates social tenure type table that is composed
        of each selected party rows with a combobox for
        social tenure type.
        """
        headers = self.add_str_type_headers()
        self.str_type_table = FreezeTableWidget(
            self.str_type_data, headers, self.container_widget
        )
        self.str_type_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        grid_layout = QGridLayout(self.container_widget)
        grid_layout.setHorizontalSpacing(5)
        #grid_layout.setColumnStretch(4, 5)
        grid_layout.setColumnStretch(0, 5)
        grid_layout.setMargin(5)

        grid_layout.addWidget(self.str_type_table)

    def enable_str_type_widgets(self, row):
        """
        Makes the STR Type combobox editable.
        :param row: The row of STR Type combobox
        :type row: Integer
        """
        frozen_table = self.str_type_table.frozen_table_view
        model = frozen_table.model()
        for i in range(0, 1):
            frozen_table.openPersistentEditor(
                model.index(row, i)
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
        Gets str type QComboBox.
        :return: A list containing a STR type QComboBox
        :rtype: List
        """
        frozen_table = self.str_type_table.frozen_table_view
        combo_boxes = frozen_table.findChildren(QComboBox)
        return combo_boxes

    def ownership_share(self):
        """
        Gets ownership_share double spin box widgets.
        :return: A list containing a list double spin boxes
        :rtype: List
        """
        frozen_table = self.str_type_table.frozen_table_view
        spinboxes = frozen_table.findChildren(QDoubleSpinBox)
        return spinboxes

    def remove_str_type_row(self, rows=[0]):
        """
        Removes corresponding social tenure type
        row when a party row is removed.
        :param rows: List of party row position that is removed.
        :type rows: List
        """
        for row in rows:
            self.str_type_table.model().removeRow(row)


class CustomTenureInfo(object):
    def __init__(self, parent, notification_bar):

        self.notification = notification_bar
        self.social_tenure = current_profile().social_tenure
        self.parties = current_profile().social_tenure.parties
        self.parent = parent
        self.entity_editors = OrderedDict()

    def textual_display_columns(self, party_entity):
        """
        Returns the only textual columns.
        :param party_entity: The entity object
        :type party_entity: Object
        :return: Textual columns
        :rtype: List
        """
        return entity_display_columns(party_entity, False, [
            'SERIAL',
            'INT',
            'DOUBLE',
            'DATE',
            'DATETIME',
            'BOOL',
            'LOOKUP',
            'FOREIGN_KEY',
            'ADMIN_SPATIAL_UNIT',
            'MULTIPLE_SELECT',
            'PERCENT'
        ])

    def add_entity_editor(
            self, party_entity, spatial_unit_entity, party_model, str_number, row_number,
            custom_model=None):
        """
        Adds custom tenure info tab with editor form. It could load data if
        the custom_model is not none.
        :param party_entity: The associated party entity
        :type party_entity: Object
        :param spatial_unit_entity: The associated spatial unit entity
        :type spatial_unit_entity: Object
        :param party_model: The party model associated with custom tenure info
        record.
        :type party_model: Object
        :param str_number: The STR record number
        :type str_number: Integer
        :param row_number: The row number of the party entry
        :type row_number: Integer
        :param custom_model: The custom tenure model that populates the tab
        forms.
        :type custom_model: Integer
        :return: True if the editor is created and false if not created.
        :rtype: Boolean
        """
        # Get the custom attribute entity
        custom_attr_entity = self.social_tenure.spu_custom_attribute_entity(
            spatial_unit_entity
        )
        if custom_attr_entity is None:
            return False

        if len(custom_attr_entity.columns) < 3:
            return False

        # If None then create
        if custom_model is None:
            self.entity_editors[(str_number, row_number)] = EntityEditorDialog(
                custom_attr_entity, parent=self.parent.custom_tenure_tab,
                manage_documents=False, parent_entity=self.social_tenure,
                exclude_columns=['social_tenure_relationship_id',
                                 self.social_tenure.CUSTOM_TENURE_DUMMY_COLUMN]
            )
        else:
            self.entity_editors[(str_number, row_number)] = EntityEditorDialog(
                custom_attr_entity, parent=self.parent.custom_tenure_tab,
                manage_documents=False, model=custom_model,
                parent_entity=self.social_tenure,
                exclude_columns=['social_tenure_relationship_id',
                                 self.social_tenure.CUSTOM_TENURE_DUMMY_COLUMN]
            )

        display_columns = self.textual_display_columns(party_entity)
        if len(display_columns) > 0:
            party_title = getattr(party_model, display_columns[0], None)
        else:
            party_title = str(row_number)
        self.parent.custom_tenure_tab.insertTab(
            row_number,
            self.entity_editors[(str_number, row_number)].
                entity_tab_widget.widget(0),
            party_title
        )
        return True

    def remove_entity_editor(self, spatial_unit, row_numbers):
        """
        Instantiates entity editor and remove its widgets as tabs.
        :param spatial_unit: The spatial unit entity
        :type spatial_unit: Object
        :param row_numbers: Number of party rows
        :type row_numbers: Integer
        :return:
        :rtype:
        """
        # Get the custom attribute entity
        custom_attr_entity = self.social_tenure.spu_custom_attribute_entity(
            spatial_unit
        )
        # If None then create
        if custom_attr_entity is not None:
            for row_number in row_numbers:
                self.parent.custom_tenure_tab.removeTab(row_number)


class SupportingDocuments(ComponentUtility):
    onUploadDocument = pyqtSignal(list)

    def __init__(self, box, combobox, add_documents_btn, notification_bar, parent=None):
        """
        Handles the supporting documents component loading.
        :param box: The layout holding the container widget.
        :type box: QVBoxLayout
        :param combobox: The combobox loading supporting document types.
        :type combobox: QComboBox
        :param add_documents_btn: The add supporting document button
        :type add_documents_btn: QPushButton
        :param notification_bar: The NotificationBar object that displays
        notification.
        :type notification_bar: Object
        :param parent: The container of the widget
        :type parent: QDialog or None
        """
        ComponentUtility.__init__(self)
        self._parent = parent
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
        """
        self.supporting_doc_manager = SourceDocumentManager(
            self.social_tenure.supporting_doc,
            self.str_doc_model,
            self._parent
        )

        self.create_doc_tab_populate_combobox()

        self.doc_type_cbo.currentIndexChanged.connect(
            self.match_doc_combo_to_tab
        )
        self.docs_tab.currentChanged.connect(
            self.match_doc_tab_to_combo
        )

    def party_count(self, count):
        """
        A setter for current_party_count that is used to determined
        the number of copies for each supporting document.
        :param count: The number of currently added party records.
        :type count: Integer
        """
        self.current_party_count = count

    def create_doc_tab_populate_combobox(self):
        """
        Creates the supporting document component widget.
        """
        self.doc_tab_data()
        self.docs_tab = QTabWidget()
        self.docs_tab_index = OrderedDict()
        for i, (id, doc) in enumerate(self.doc_types.items()):
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
        """
        Sets the document types in the social tenure entity.
        """
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
        """
        combo_text = self.doc_type_cbo.currentText()
        if combo_text is not None and len(combo_text) > 0:
            index = self.docs_tab_index[combo_text]
            self.docs_tab.setCurrentIndex(index)

    def match_doc_tab_to_combo(self):
        """
        Changes the document type combobox value based on the
        selected tab.
        """
        doc_tab_index = self.docs_tab.currentIndex()
        self.doc_type_cbo.setCurrentIndex(doc_tab_index)

    @staticmethod
    def hide_doc_widgets(widget, visibility):
        """
        Hides or shows the visibility of the supporting document
        container widgets.
        :param widget: The widget to which the visibility is set.
        :type widget: QWidget
        :param visibility: A boolean to show or hide visibility.
        True hides widget and False shows it.
        :type visibility: Boolean
        """
        widget.setHidden(visibility)

    def update_container(self, str_number: int):
        """
        Update the current supporting document widget container to be used.
        :param str_number: The STR node number
        :type str_number: Integer
        """
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
            doc_widget_layout = scroll_area.findChild(
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
        """
        Hides all other supporting document widget except the current
        STR node widget.
        :param doc_text: The current document type selected.
        :type doc_text: String
        :param str_number: The STR node number
        :type str_number: Integer
        """
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
            "SupportingDocuments",
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
        """
        Displays a file dialog for a user to specify a source document
        :param title: The title of the file dialog
        :type title: String
        """
        # Get last path for supporting documents
        last_path = last_document_path()
        if last_path is None:
            last_path = '/home'

        files, _ = QFileDialog.getOpenFileNames(
            iface.mainWindow(),
            title,
            last_path,
            "Source Documents (*.jpg *.jpeg *.png *.bmp *.tiff *.svg)"
        )
        return files


class ValidityPeriod():
    def __init__(self, str_editor):
        """
        Handles the validity period component logic.
        :param str_editor: The STREditor object.
        :type str_editor: Object
        """
        self.str_editor = str_editor
        self.from_date = self.str_editor.validity_from_date
        self.to_date = self.str_editor.validity_to_date
        self.current_profile = current_profile()
        self.social_tenure = self.current_profile.social_tenure
        self.init_dates()

        str_editor.tenure_duration.valueChanged.connect(
            self.bind_to_date_by_year_month
        )
        str_editor.in_years.clicked.connect(
            self.adjust_to_year
        )
        str_editor.in_months.clicked.connect(
            self.adjust_to_month
        )
        self.to_date.dateChanged.connect(
            self.bind_year_month_by_dates_range
        )
        self.from_date.dateChanged.connect(
            self.bind_year_month_by_dates_range
        )
        self.from_date.dateChanged.connect(
            self.set_minimum_to_date
        )
        self.set_minimum_to_date()
        self.set_range_from_date()
        self.set_range_to_date()

    def init_dates(self):
        """
        Initialize the dates by setting the current date.
        """
        self.from_date.setDate(
            date.today()
        )
        self.to_date.setDate(
            date.today()
        )

    def adjust_to_year(self):
        """
        Adjusts the date range based on years using the numbers
        specified in the tenure duration spinbox.
        """
        duration = self.str_editor.tenure_duration.value()
        before_date = self.to_date.date().currentDate()

        after_date = date(
            before_date.year() + duration,
            self.to_date.date().month(),
            self.to_date.date().day()
        )
        self.to_date.setDate(after_date)

    def adjust_to_month(self):
        """
        Adjusts the date range based on month using the numbers
        specified in the tenure duration spinbox.
        """
        duration = self.str_editor.tenure_duration.value()
        before_date = self.from_date.date()
        after_date = self.add_months(
            before_date, duration
        )
        self.to_date.setDate(after_date)

    @staticmethod
    def add_months(source_date, months):
        """
        Adds months on a date.
        :param source_date: The date on which the months are
        going to be added
        :type source_date: date
        :param months: The number of months to be added
        :type months: Integer
        :return: The new date with the added months
        :rtype: date
        """
        month = source_date.month() - 1 + months
        year = int(source_date.year() + month / 12)
        month = month % 12 + 1
        day = min(
            source_date.day,
            calendar.monthrange(year, month)[1]
        )
        return date(year, month, day)

    def bind_to_date_by_year_month(self, increment):
        """
        A slot raised when validity year is specified.
        It changes the end date of the validity.
        :param increment: The new value of year spinbox.
        :type increment: Integer
        """
        if self.str_editor.in_years.isChecked():
            current_year = self.from_date.date().toPyDate().year
            after_date = date(
                current_year + increment,
                self.to_date.date().month(),
                self.to_date.date().day()
            )
        else:
            current_date = self.from_date.date()
            after_date = self.add_months(
                current_date, increment
            )

        self.to_date.setDate(after_date)

    def bind_year_month_by_dates_range(self):
        """
        A slot raised when from or to dates are changed.
        It updates the year spinbox. Note that,
        there is no rounding.
        """
        to_date = self.to_date.date().toPyDate()
        from_date = self.from_date.date().toPyDate()

        if self.str_editor.in_years.isChecked():
            period = relativedelta(to_date, from_date).years
        else:
            year_diff = to_date.year - from_date.year

            period = to_date.month - from_date.month + (12 * year_diff)
        # Fixes the value freeze when editing STR
        # period = period + 1
        self.str_editor.tenure_duration.setValue(period)

    def set_minimum_to_date(self):
        """
        Set the minimum to date based on the
        change in value of from date.
        """
        self.to_date.setMinimumDate(self.from_date.date())

    def set_range_from_date(self):
        """
        Sets the date rage on start date of the validity period as
        specified in the configuration.
        """
        minimum_date = self.social_tenure.validity_start_column.minimum
        maximum_date = self.social_tenure.validity_start_column.maximum

        self.from_date.setDateRange(
            minimum_date, maximum_date
        )

    def set_range_to_date(self):
        """
        Sets the date rage on end date of the validity period date as
        specified in the configuration.
        """
        minimum_date = self.social_tenure.validity_end_column.minimum
        maximum_date = self.social_tenure.validity_end_column.maximum

        self.to_date.setDateRange(
            minimum_date, maximum_date
        )
