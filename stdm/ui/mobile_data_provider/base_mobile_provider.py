"""
/***************************************************************************
Name                 : wizard
Description          : Mobile provider export and import wizard
Date                 : 25/March/2023
copyright            : (C) 2015 by UN-Habitat and implementing partners.
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

from qgis.PyQt import uic
from qgis.PyQt.QtCore import (
    Qt,
    QDir,
    pyqtSignal,
    QDate,
    QFile,
    QThread,
    QCoreApplication,
    QEvent,
    QIODevice,
    QPointF,
    QSizeF,
    QItemSelectionModel,
    QModelIndex,
    QSortFilterProxyModel
)
from qgis.PyQt.QtGui import (
    QStandardItemModel,
    QStandardItem,
    QColor,
    QFont
)
from qgis.PyQt.QtWidgets import (
    QWizard,
    QMessageBox,
    QAbstractItemView,
    QDialog,
    QApplication,
    QMenu,
    QFileDialog,
    QTableView
)
from qgis._core import QgsMessageLog

from stdm.data.configuration.db_items import DbItem
from stdm.data.configuration.profile import Profile
from stdm.settings import current_profile
from stdm.ui.gui_utils import GuiUtils
from .column_editor import AppearanceColumnEditor
from .custom_item_model import (
    EntitiesModel,
    ColumnEntitiesModel,
)
from stdm.utils.util import enable_drag_sort
from .mobile_provider_export import ProviderWriter
from ...data.pg_utils import pg_table_exists, pg_table_record_count, table_column_names
from ...exceptions import DummyException

WIDGET, BASE = uic.loadUiType(
    GuiUtils.get_ui_file_path('mobile_data_provider/ui_mobile_provider_wizard.ui'))

HOME = QDir.home().path()
PROVIDER_HOME = HOME + '/.stdm/ui/mobile_data_provider'


class BaseMobileProvider(WIDGET, BASE):
    """
    STDM mobile provider export and import wizard
    """
    wizardFinished = pyqtSignal(object, bool)

    def __init__(self, parent, provider=None):
        QWizard.__init__(self, parent)
        self.setupUi(self)

        # Add maximize buttons
        self.setWindowFlags(
            self.windowFlags() |
            Qt.WindowSystemMenuHint |
            Qt.WindowMaximizeButtonHint
        )

        self.register_fields()
        # self.txtMobileProviderIntroduction.setText(self.current_profile().name)
        self.entity_model = EntitiesModel()
        self.set_views_entity_model(self.entity_model)
        self.init_entity_item_model()
        self.col_view_model = ColumnEntitiesModel()
        self.providerEntityColumns.setModel(self.col_view_model)
        self.init_ui_ctrls()
        self.providerEntityColumns.installEventFilter(self)
        self.load_profiles()

    def register_fields(self):
        self.setOption(self.HaveHelpButton, True)
        page_count = self.page(1)

    def current_profile(self) -> Profile:
        """
        :return:profile object
        :rtype: Object
        """
        return current_profile()

    def init_entity_item_model(self):
        """
        Attach a selection change event handler for the custom
        QStandardItemModel - entity_item_model
        """
        self.entity_item_model = self.providerEntities.selectionModel()
        self.entity_item_model.selectionChanged.connect(self.entity_changed)

    def set_views_entity_model(self, entity_model):
        """
        Attach custom item model to hold data for the view controls
        :param entity_model: Custom QStardardItemModel
        :type entity_model: EntitiesModel
        """
        self.providerEntities.setModel(entity_model)

    def init_ui_ctrls(self):
        """
        Set default state for UI controls
        """
        self.providerEntityColumns.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.providerEntityColumns.doubleClicked.connect(self.edit_column)

        self.columns_proxy_model = QSortFilterProxyModel(self.col_view_model)
        self.columns_proxy_model.setSourceModel(self.col_view_model)
        self.columns_proxy_model.setFilterKeyColumn(0)
        self.providerEntityColumns.setModel(self.columns_proxy_model)
        self.providerEntityColumns.setSortingEnabled(True)
        self.providerEntities.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.providerEntities.clicked.connect(self.entity_clicked)
        enable_drag_sort(self.providerEntityColumns)

    def size_columns_viewer(self):
        NAME = 0
        TYPE = 1
        DESC = 2

        self.providerEntityColumns.setColumnWidth(NAME, 200)
        self.providerEntityColumns.setColumnWidth(TYPE, 180)
        self.providerEntityColumns.setColumnWidth(DESC, 200)

    def edit_column(self):
        """
        Event handler for editing a column.
        """
        if len(self.providerEntityColumns.selectedIndexes()) == 0:
            self.show_message(self.tr("Please select a column to edit"))
            return

        rid, column, model_item = self.get_selected_item_data(self.providerEntityColumns)
        if rid == -1:
            return
        if column and column.action == DbItem.CREATE:
            _, entity = self._get_entity(self.providerEntities)

            profile = self.current_profile()
            params = {}
            params['parent'] = self
            params['column'] = column
            params['entity'] = entity
            params['profile'] = profile
            params['in_db'] = self.column_exist_in_entity(entity, column)
            params['entity_has_records'] = self.entity_has_records(entity)

            params['is_new'] = False

            original_column = column  # model_item.entity(column.name)

            editor = AppearanceColumnEditor(**params)
            result = editor.exec_()

            if result == 1:

                model_index_name = model_item.index(rid, 0)
                model_index_dtype = model_item.index(rid, 1)
                model_index_desc = model_item.index(rid, 2)

                model_item.setData(model_index_name, editor.column.name)
                model_item.setData(model_index_dtype, editor.column.display_name())
                model_item.setData(model_index_desc, editor.column.description)

                model_item.edit_entity(original_column, editor.column)

                entity.columns[original_column.name] = editor.column
                entity.rename_column(original_column.name, editor.column.name)

        else:
            self.show_message(QApplication.translate("Configuration Wizard", \
                                                     "No column selected for edit!"))

    def entity_changed(self):
        """
        triggered when you select an entity, clears an existing column entity
        model and create a new one.
        Get the columns of the selected entity, add them to the newly created
        column entity model
        """
        self.trigger_entity_change()

    def trigger_entity_change(self):
        row_id = self.entity_item_model.currentIndex().row()
        view_model = self.entity_item_model.currentIndex().model()
        self.col_view_model.clear()
        self.col_view_model = ColumnEntitiesModel()

        if row_id > -1:
            # columns = view_model.entity_byId(row_id).columns.values()
            ent_name = view_model.data(view_model.index(row_id, 0))

            entity = view_model.entity(ent_name)
            if entity is None:
                return
            columns = list(view_model.entity(ent_name).columns.values())
            self.add_columns(self.col_view_model, columns)

            self.providerEntityColumns.setModel(self.col_view_model)
        self.size_columns_viewer()

    def add_columns(self, v_model, columns):
        """
        Add columns to a view model
        param v_model: Instance of EntitiesModel
        type v_model: EntitiesModel
        param columns: List of column names to insert in v_model
        type columns: list
        """
        for column in columns:
            if column.user_editable():
                v_model.add_entity(column)

    def entity_clicked(self):
        _, entity, _ = self.get_selected_item_data(self.providerEntities)
        if entity is None:
            return
        profile = current_profile()
        if profile is None:
            return

    def get_selected_item_data(self, view):
        if len(view.selectedIndexes()) == 0:
            return -1, None, None
        model_item = view.model()
        row_id = view.selectedIndexes()[0].row()
        col_name = view.model().data(
            view.model().index(row_id, 0))
        column = model_item.entities()[str(col_name)]
        return row_id, column, model_item

    def load_profiles(self):
        """
        Read and load profiles from StdmConfiguration instance
        """
        self.populate_view_models(current_profile())

    def populate_view_models(self, profile):
        for entity in profile.entities.values():
            if entity.action == DbItem.DROP:
                continue

            if hasattr(entity, 'user_editable') and entity.TYPE_INFO != 'VALUE_LIST':
                if entity.user_editable == False:
                    continue

            if entity.TYPE_INFO not in ['SUPPORTING_DOCUMENT',
                                        'SOCIAL_TENURE', 'ADMINISTRATIVE_SPATIAL_UNIT',
                                        'ENTITY_SUPPORTING_DOCUMENT', 'ASSOCIATION_ENTITY', 'AUTO_GENERATE_CODE']:

                if entity.TYPE_INFO == 'VALUE_LIST':
                    pass
                else:
                    self.entity_model.add_entity(entity)
        self.set_model_items_selectable()

    def set_model_items_selectable(self):
        """
        Ensure that the entities  are checkable
        :return:
        """
        if self.entity_model.rowCount() > 0:
            for row in range(self.entity_model.rowCount()):
                index = self.entity_model.index(row, 0)
                item_index = self.entity_model.itemFromIndex(index)
                #item_index.setCheckable(True)

    def _get_entity(self, view):
        model_item, entity, row_id = self.get_model_entity(view)
        if entity:
            return row_id, entity

    def get_model_entity(self, view):
        """
        Extracts and returns an entitymodel, entity and the
        current selected item ID from QAbstractItemView of a
        given view widget
        param view: Widget that inherits QAbstractItemView
        type view: QAbstractitemView
        rtype: tuple - (QStandardItemModel, Entity, int)
        """
        sel_id = -1
        entity = None
        model_indexes = view.selectedIndexes()
        if len(model_indexes) == 0:
            return (None, None, None)
        model_index = model_indexes[0]
        model_item = model_index.model()
        name = model_item.data(model_index)
        entity = model_item.entity(name)
        row = model_index.row()

        return (model_item, entity, row)

    def entity_has_records(self, entity):
        """
        Returns True if entity has records in the database else False.
        :param entity: Entity instance
        :type entity: Entity
        :rtype: boolean
        """
        if not pg_table_exists(entity.name):
            return False

        record_count = pg_table_record_count(entity.name)
        return True if record_count > 0 else False

    def column_exist_in_entity(self, entity, column):
        """
        Returns True if a column exists in a given entity in DB
        :param entity: Entity instance to check if column exist
        :type entity: Entity
        :param column: Column instance to check its existance
        :type entity: BaseColumn
        :rtype: boolean
        """
        cols = table_column_names(entity.name)
        return True if column.name in cols else False

    def validateCurrentPage(self):
        validPage = True

        if self.nextId() == 1:
            return validPage

        if self.currentId() == 1:
            QgsMessageLog.logMessage("Page 1", "STDM dev")
            validPage = True

        elif self.currentId() == 2:
            QgsMessageLog.logMessage("Page 2", "STDM dev")

            entities = self.selected_entities_from_model()
            QgsMessageLog.logMessage("Entities {entities}".format(entities=str(entities)), "STDM dev")
            if len(entities) == 0:
                QgsMessageLog.logMessage("No entity selected. Please select at least one entity...", "STDM dev")
                self._notif_bar_str.insertErrorNotification(
                    'No entity selected. Please select at least one entity...'
                )
                return

            else:
                QgsMessageLog.logMessage("Created", "STDM dev")
                self.generate_mobile_form(entities)

            validPage = False

        return validPage

    def generate_provider_output(self, profile):
        pass

    def selected_entities_from_model(self) ->list[str]:
        """
        Get selected entities for conversion to Xform.
        """
        entity_list = []
        if self.entity_model.rowCount() > 0:
            for row in range(self.entity_model.rowCount()):
                item = self.entity_model.item(row)
                entity_list.append(item.text())
        return entity_list

    def generate_mobile_form(self, profile_entities: list[str]):
        """
        Generate mobile form for entities of the current profile.
        """
        try:

            profile = self.current_profile()

            provider_writer = ProviderWriter(profile, profile_entities)

            created, create_msg = provider_writer.create_xsl_file()
            if not created:
                QgsMessageLog.logMessage("Message {msg}".format(msg=create_msg), "STDM dev")
                return

            data_written, write_msg = provider_writer.write_data_to_xlsform()
            if not data_written:
                QgsMessageLog.logMessage("Message {msg}".format(msg=write_msg), "STDM dev")
                return
            else:
                QgsMessageLog.logMessage("Message {msg}".format(msg=write_msg), "STDM dev")

        except DummyException as ex:
            QgsMessageLog.logMessage("Message {msg}".format(msg=ex.message +
                                                        ': Unable to generate Mobile Form'), "STDM dev")

