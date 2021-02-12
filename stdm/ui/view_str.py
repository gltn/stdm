"""
/***************************************************************************
Name                 : View STR Relationships
Description          : Main Window for searching and browsing the social tenure
                       relationship of the participating entities.
Date                 : 24/May/2014
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
import logging
from collections import OrderedDict
from datetime import date

from qgis.PyQt import uic
from qgis.PyQt.QtCore import (
    QTimer,
    Qt,
    QSize,
    QObject,
    pyqtSignal,
    QThread,
    QRegExp,
    QSortFilterProxyModel,
    pyqtSlot
)
from qgis.PyQt.QtWidgets import (
    QMainWindow,
    QDesktopWidget,
    QToolBar,
    QAction,
    QApplication,
    QProgressDialog,
    QProgressBar,
    QMessageBox,
    QVBoxLayout,
    QWidget,
    QScrollArea,
    QFrame,
    QCheckBox,
    QTabBar,
    QCompleter
)
from qgis.core import QgsProject
from qgis.utils import (
    iface
)
from sqlalchemy import exc
from sqlalchemy import (
    func,
    String
)

from stdm.data import globals
from stdm.data.configuration import entity_model
from stdm.data.database import Content
from stdm.data.pg_utils import pg_table_count
from stdm.data.qtmodels import (
    BaseSTDMTableModel
)
from stdm.exceptions import DummyException
from stdm.security.authorization import Authorizer
from stdm.settings import current_profile
from stdm.ui.feature_details import DetailsTreeView, SelectedItem
from stdm.ui.forms.widgets import ColumnWidgetRegistry
from stdm.ui.gui_utils import GuiUtils
from stdm.ui.notification import (
    NotificationBar
)
from stdm.ui.social_tenure.str_editor import STREditor
from stdm.ui.sourcedocument import (
    SourceDocumentManager,
    DocumentWidget
)
from stdm.ui.spatial_unit_manager import SpatialUnitManagerDockWidget
from stdm.utils.util import (
    entity_searchable_columns,
    entity_display_columns,
    format_name,
    lookup_parent_entity
)

LOGGER = logging.getLogger('stdm')

WIDGET, BASE = uic.loadUiType(
    GuiUtils.get_ui_file_path('ui_view_str.ui'))


class ViewSTRWidget(WIDGET, BASE):
    """
    Search and browse the social tenure relationship
    of all participating entities.
    """

    def __init__(self, plugin):
        QMainWindow.__init__(self, plugin.iface.mainWindow())
        self.setupUi(self)

        self.btnSearch.setIcon(GuiUtils.get_icon('search.png'))
        self.btnClearSearch.setIcon(GuiUtils.get_icon('reset.png'))

        self._plugin = plugin

        self.search_done = False
        # self.tbPropertyPreview.set_iface(self._plugin.iface)
        QTimer.singleShot(
            100, lambda: self.tbPropertyPreview.set_iface(self._plugin.iface))

        self.curr_profile = current_profile()

        self.spatial_units = self.curr_profile.social_tenure.spatial_units
        # Center me
        self.move(QDesktopWidget().availableGeometry().center() -
                  self.frameGeometry().center())
        self.sp_unit_manager = SpatialUnitManagerDockWidget(
            self._plugin.iface, self._plugin
        )
        self.geom_cols = []
        for spatial_unit in self.spatial_units:
            each_geom_col = self.sp_unit_manager.geom_columns(spatial_unit)
            self.geom_cols.extend(each_geom_col)

        # Configure notification bar
        self._notif_search_config = NotificationBar(
            self.vl_notification
        )

        # set whether currently logged in user has
        # permissions to edit existing STR records
        self._can_edit = self._plugin.STRCntGroup.canUpdate()
        self._can_delete = self._plugin.STRCntGroup.canDelete()
        self._can_create = self._plugin.STRCntGroup.canCreate()
        # Variable used to store a reference to the
        # currently selected social tenure relationship
        # when displaying documents in the supporting documents tab window.
        # This ensures that there are no duplicates
        # when the same item is selected over and over again.

        self._strID = None
        self.removed_docs = None
        # Used to store the root hash of the currently selected node.
        self._curr_rootnode_hash = ""

        self.str_model, self.str_doc_model = entity_model(
            self.curr_profile.social_tenure, False, True
        )

        self._source_doc_manager = SourceDocumentManager(
            self.curr_profile.social_tenure.supporting_doc,
            self.str_doc_model,
            self
        )

        self._source_doc_manager.documentRemoved.connect(
            self.onSourceDocumentRemoved
        )

        self._source_doc_manager.setEditPermissions(False)

        self.addSTR = None
        self.editSTR = None
        self.deleteSTR = None

        self.initGui()
        self.add_spatial_unit_layer()

        self.details_tree_view = DetailsTreeView(parent=self, plugin=self._plugin)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.details_tree_view)
        self.str_tree_container.setLayout(layout)

        # else:
        #     self.details_tree_view = self._plugin.details_tree_view
        self.details_tree_view.activate_feature_details(True)
        self.details_tree_view.model.clear()

        count = pg_table_count(self.curr_profile.social_tenure.name)
        self.setWindowTitle(
            self.tr('{}{}'.format(
                self.windowTitle(), '- ' + str(count) + ' rows'
            ))
        )

        self.active_spu_id = -1

        self.toolBox.setStyleSheet(
            '''
            QToolBox::tab {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #EDEDED, stop: 0.4 #EDEDED,
                    stop: 0.5 #EDEDED, stop: 1.0 #D3D3D3
                );
                border-radius: 2px;
                border-style: outset;
                border-width: 2px;
                height: 100px;
                border-color: #C3C3C3;
            }

            QToolBox::tab:selected {
                font: italic;
            }
            '''
        )

        self.details_tree_view.view.setStyleSheet(
            '''
            QTreeView:!active {
                selection-background-color: #72a6d9;
            }
            '''
        )

    def add_tool_buttons(self):
        """
        Add toolbar buttons of add, edit and delete buttons.
        :return: None
        :rtype: NoneType
        """
        tool_buttons = QToolBar()
        tool_buttons.setObjectName('form_toolbar')
        tool_buttons.setIconSize(QSize(16, 16))

        self.addSTR = QAction(GuiUtils.get_icon(
            'add.png'),
            QApplication.translate('ViewSTRWidget', 'Add'),
            self
        )

        self.editSTR = QAction(
            GuiUtils.get_icon('edit.png'),
            QApplication.translate('ViewSTRWidget', 'Edit'),
            self
        )

        self.deleteSTR = QAction(
            GuiUtils.get_icon('remove.png'),
            QApplication.translate('ViewSTRWidget', 'Remove'),
            self
        )

        tool_buttons.addAction(self.addSTR)
        tool_buttons.addAction(self.editSTR)
        tool_buttons.addAction(self.deleteSTR)

        self.toolbarVBox.addWidget(tool_buttons)

    def initGui(self):
        """
        Initialize widget
        """
        self.tb_actions.setVisible(False)
        self._load_entity_configurations()

        self.add_tool_buttons()

        # Connect signals
        self.tbSTREntity.currentChanged.connect(self.entityTabIndexChanged)
        self.btnSearch.clicked.connect(self.searchEntityRelations)
        self.btnClearSearch.clicked.connect(self.clearSearch)
        # self.tvSTRResults.expanded.connect(self.onTreeViewItemExpanded)

        # Set the results treeview to accept requests for context menus
        # self.tvSTRResults.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.tvSTRResults.customContextMenuRequested.connect(
        #     self.onResultsContextMenuRequested
        # )

        if not self._can_create:
            self.addSTR.hide()

        if not self._can_edit:
            self.editSTR.hide()
        else:
            self.editSTR.setDisabled(True)
        if not self._can_delete:
            self.deleteSTR.hide()
        else:
            self.deleteSTR.setDisabled(True)

        self.addSTR.triggered.connect(self.load_new_str_editor)

        self.deleteSTR.triggered.connect(self.delete_str)

        self.editSTR.triggered.connect(self.load_edit_str_editor)

        # Load async for the current widget
        self.entityTabIndexChanged(0)

    def init_progress_dialog(self):
        """
        Initializes the progress dialog.
        """
        self.progress = QProgressBar(self)
        self.progress.resize(self.width(), 10)
        self.progress.setTextVisible(False)

    def add_spatial_unit_layer(self):
        """
        Add the spatial unit layer into the map canvas for later use.
        """
        # Used for startup of view STR, just add the first geom layer.
        if len(self.geom_cols) > 0:
            for spatial_unit in self.spatial_units:
                layer_name_item = self.sp_unit_manager.geom_col_layer_name(
                    spatial_unit.name,
                    self.geom_cols[0]
                )
                self.sp_unit_manager.add_layer_by_name(layer_name_item)

    def _check_permissions(self):
        """
        Enable/disable actions based on the
        permissions defined in the content
        group.
        """
        if self._can_edit:
            self.tb_actions.addAction(self._new_str_action)
        else:
            self.tb_actions.removeAction(self._new_str_action)

        if len(self.tb_actions.actions()) == 0:
            self.tb_actions.setVisible(False)

        else:
            self.tb_actions.setVisible(True)

    def _load_entity_configurations(self):
        """
        Specify the entity configurations.
        """
        try:
            self.parties = self.curr_profile.social_tenure.parties
            tb_str_entities = self.parties + self.spatial_units

            for i, t in enumerate(tb_str_entities):
                QApplication.processEvents()
                entity_cfg = self._entity_config_from_profile(
                    str(t.name), t.short_name
                )

                if entity_cfg is not None:
                    entity_widget = self.add_entity_config(entity_cfg)

                    # entity_widget.setNodeFormatter(
                    #     EntityNodeFormatter(
                    #         entity_cfg, self.tvSTRResults, self
                    #     )
                    # )

        except DummyException as pe:
            self._notif_search_config.clear()
            self._notif_search_config.insertErrorNotification(str(pe))

    def _entity_config_from_profile(self, table_name, short_name):
        """
        Creates an EntityConfig object from the table name.
        :param table_name: Name of the database table.
        :type table_name: str
        :return: Entity configuration object.
        :rtype: EntityConfig
        """
        table_display_name = format_name(short_name)

        entity = self.curr_profile.entity_by_name(table_name)
        model = entity_model(entity)

        if model is not None:
            # Entity configuration
            entity_cfg = EntityConfiguration()
            entity_cfg.Title = table_display_name
            entity_cfg.STRModel = model
            entity_cfg.data_source_name = table_name
            for col, factory in self._get_widget_factory(entity):
                entity_cfg.LookupFormatters[col.name] = factory

            # Load filter and display columns
            # using only those which are of
            # numeric/varchar type
            searchable_columns = entity_searchable_columns(entity)
            display_columns = entity_display_columns(entity)
            for c in searchable_columns:
                if c != 'id':
                    entity_cfg.filterColumns[c] = format_name(c)
            for c in display_columns:
                if c != 'id':
                    entity_cfg.displayColumns[c] = format_name(c)
            return entity_cfg
        else:
            return None

    def _get_widget_factory(self, entity):
        """
        Get widget factory for specific column type
        :param entity: Current column entity object
        :type entity: Entity
        :return c: Column object corresponding to the widget factory
        :rtype c: BaseColumn
        :return col_factory: Widget factory corresponding to the column type
        :rtype col_factory: ColumnWidgetRegistry
        """
        for c in entity.columns.values():
            col_factory = ColumnWidgetRegistry.factory(c.TYPE_INFO)
            if col_factory is not None:
                yield c, col_factory(c)

    def add_entity_config(self, config):
        """
        Set an entity configuration option and
        add it to the 'Search Entity' tab.
        """
        entityWidg = STRViewEntityWidget(config)
        entityWidg.asyncStarted.connect(self._progressStart)
        entityWidg.asyncFinished.connect(self._progressFinish)

        tabIndex = self.tbSTREntity.addTab(entityWidg, config.Title)

        return entityWidg

    def entityTabIndexChanged(self, index):
        """
        Raised when the tab index of the entity search tab widget changes.
        """
        # Get the current widget in the tab container
        entityWidget = self.tbSTREntity.currentWidget()

        if isinstance(entityWidget, EntitySearchItem):
            entityWidget.loadAsync()

    def searchEntityRelations(self):
        """
        Slot that searches for matching items for
        the specified entity and corresponding STR entities.
        """

        entityWidget = self.tbSTREntity.currentWidget()

        entity_name = entityWidget.config.data_source_name

        self._reset_controls()

        if isinstance(entityWidget, EntitySearchItem):
            valid, msg = entityWidget.validate()

            if not valid:
                self._notif_search_config.clear()
                self._notif_search_config.insertErrorNotification(msg)

                return

            results, searchWord = entityWidget.executeSearch()

            # Show error message
            if len(results) == 0:
                noResultsMsg = QApplication.translate(
                    'ViewSTR',
                    'No results found for "{}"'.format(searchWord)
                )
                self._notif_search_config.clear()
                self._notif_search_config.insertErrorNotification(
                    noResultsMsg
                )

                return

            party_names = [e.name for e in self.curr_profile.social_tenure.parties]
            entity = self.curr_profile.entity_by_name(entity_name)

            result_ids = [r.id for r in results]

            if entity_name in party_names:

                self.active_spu_id = self.details_tree_view.search_party(
                    entity, result_ids
                )
            else:
                self.details_tree_view.search_spatial_unit(
                    entity, result_ids
                )

            # self.tbPropertyPreview._iface.activeLayer().selectByExpression("id={}".format(self.active_spu_id))
            # self.details_tree_view._selected_features = self.tbPropertyPreview._iface.activeLayer().selectedFeatures()
            # self._load_root_node(entity_name, formattedNode)

    def clearSearch(self):
        """
        Clear search input parameters (for current widget) and results.
        """
        entityWidget = self.tbSTREntity.currentWidget()
        if isinstance(entityWidget, EntitySearchItem):
            entityWidget.reset()
        self._reset_controls()

    def _reset_controls(self):
        # Clear tree view
        self._resetTreeView()

        # Clear document listings
        self._deleteSourceDocTabs()

        # Remove spatial unit memory layer
        self.tbPropertyPreview.remove_layer()

    def on_select_results(self):
        """
        Slot which is raised when the selection
        is changed in the tree view
        selection model.
        """
        if len(self.details_tree_view.view.selectedIndexes()) < 1:
            self.disable_buttons()
            return
        self.search_done = True

        index = self.details_tree_view.view.selectedIndexes()[0]
        item = self.details_tree_view.model.itemFromIndex(index)

        QApplication.processEvents()

        # STR node - edit social tenure relationship
        if item.text() == self.details_tree_view.str_text:
            entity = self.curr_profile.social_tenure
            str_model = self.details_tree_view.str_models[item.data()]

            self.details_tree_view.selected_model = str_model
            self.details_tree_view.selected_item = SelectedItem(item)

            documents = self.details_tree_view._supporting_doc_models(
                entity.name, str_model
            )

            self._load_source_documents(documents)
            # if there is supporting document,
            # expand supporting document tab
            if len(documents) > 0:
                self.toolBox.setCurrentIndex(1)
            self.disable_buttons(False)

        # party node - edit party
        elif item.data() in self.details_tree_view.spatial_unit_items.keys():
            self.toolBox.setCurrentIndex(0)
            entity = self.details_tree_view.spatial_unit_items[item.data()]

            model = self.details_tree_view.feature_model(entity, item.data())
            self.draw_spatial_unit(entity.name, model)
            self.disable_buttons()

            canvas = iface.mapCanvas()
            if canvas:
                canvas.zoomToFullExtent()

        else:
            self.disable_buttons()

    def disable_buttons(self, status=True):
        if self._can_edit:
            self.deleteSTR.setDisabled(status)
        if self._can_delete:
            self.editSTR.setDisabled(status)

    def str_party_column_obj(self, record):
        """
        Gets the current party column name in STR
        table by finding party column with value
        other than None.
        :param record: The STR record or result.
        :type record: Dictionary
        :return: The party column name with value.
        :rtype: String
        """
        for party in self.parties:
            party_name = party.short_name.lower()
            party_id = '{}_id'.format(party_name)
            if party_id not in record.__dict__:
                return None
            if record.__dict__[party_id] is not None:
                party_id_obj = getattr(self.str_model, party_id)
                return party_id_obj

    def load_edit_str_editor(self):
        self.details_tree_view.edit_selected_node(self.details_tree_view)
        self.btnSearch.click()
        self.disable_buttons()

    def load_new_str_editor(self):
        try:
            # Check type of node and perform corresponding action
            add_str = STREditor()
            add_str.exec_()

        except DummyException as ex:
            QMessageBox.critical(
                self._plugin.iface.mainWindow(),
                QApplication.translate(
                    "STDMPlugin",
                    "Loading Error"
                ),
                str(ex)
            )

    def delete_str(self):
        self.details_tree_view.delete_selected_item()
        self.btnSearch.click()
        self.disable_buttons()

    def onSourceDocumentRemoved(self, container_id, doc_uuid, removed_doc):
        """
        Slot raised when a source document is removed from the container.
        If there are no documents in the specified container then remove
        the tab.
        """
        curr_container = self.tbSupportingDocs.currentWidget()
        curr_doc_widget = curr_container.findChildren(DocumentWidget)

        for doc in curr_doc_widget:
            if doc.fileUUID == doc_uuid:
                doc.deleteLater()
        self.removed_docs = removed_doc

    def draw_spatial_unit(self, entity_name, model):
        """
        Render the geometry of the given spatial unit in the spatial view.
        :param row_id: Sqlalchemy object representing a feature.
        """
        entity = self.curr_profile.entity_by_name(entity_name)

        self.tbPropertyPreview.draw_spatial_unit(entity, model)

    def showEvent(self, event):
        """
        (Re)load map layers in the viewer and main canvas.
        :param event: Window event
        :type event: QShowEvent
        """
        self.setEnabled(True)
        if QTimer is not None:
            QTimer.singleShot(200, self.init_mirror_map)

        return QMainWindow.showEvent(self, event)

    def init_mirror_map(self):
        self._notify_no_base_layers()
        # Add spatial unit layer if it doesn't exist
        self.tbPropertyPreview.refresh_canvas_layers()
        self.tbPropertyPreview.load_web_map()

    def _notify_no_base_layers(self):
        """
        Checks if there are any base layers that will be used when
        visualizing the spatial units. If there are no base layers
        then insert warning message.
        """
        self._notif_search_config.clear()

        num_layers = len(QgsProject.instance().mapLayers())
        if num_layers == 0:
            msg = QApplication.translate(
                "ViewSTR",
                "No basemap layers are loaded in the "
                "current project. Basemap layers "
                "enhance the visualization of spatial units."
            )
            self._notif_search_config.insertWarningNotification(msg)

    def _deleteSourceDocTabs(self):
        """
        Removes all source document tabs and deletes their references.
        """
        tabCount = self.tbSupportingDocs.count()

        while tabCount != 0:
            srcDocWidget = self.tbSupportingDocs.widget(tabCount - 1)
            self.tbSupportingDocs.removeTab(tabCount - 1)
            del srcDocWidget
            tabCount -= 1

        self._strID = None
        self._source_doc_manager.reset()

    def _resetTreeView(self):
        """
        Clears the results tree view.
        """
        # Reset tree view
        strModel = self.details_tree_view.view.model()
        resultsSelModel = self.details_tree_view.view.selectionModel()

        if strModel:
            strModel.clear()

        if resultsSelModel:
            if self.search_done:
                resultsSelModel.selectionChanged.disconnect(self.on_select_results)
            resultsSelModel.selectionChanged.connect(self.on_select_results)

    def _load_source_documents(self, source_docs):
        """
        Load source documents into document listing widget.
        """
        # Configure progress dialog
        progress_msg = QApplication.translate(
            "ViewSTR", "Loading supporting documents..."
        )

        progress_dialog = QProgressDialog(self)
        if len(source_docs) > 0:
            progress_dialog.setWindowTitle(progress_msg)
            progress_dialog.setRange(0, len(source_docs))
            progress_dialog.setWindowModality(Qt.WindowModal)
            progress_dialog.setFixedWidth(380)
            progress_dialog.show()
            progress_dialog.setValue(0)
        self._notif_search_config.clear()

        self.tbSupportingDocs.clear()
        self._source_doc_manager.reset()

        if len(source_docs) < 1:
            empty_msg = QApplication.translate(
                'ViewSTR', 'No supporting document is uploaded '
                           'for this social tenure relationship.'
            )
            self._notif_search_config.clear()
            self._notif_search_config.insertWarningNotification(empty_msg)

        for i, (doc_type_id, doc_obj) in enumerate(source_docs.items()):

            # add tabs, and container and widget for each tab
            tab_title = self._source_doc_manager.doc_type_mapping[doc_type_id]

            tab_widget = QWidget()
            tab_widget.setObjectName(tab_title)

            cont_layout = QVBoxLayout(tab_widget)
            cont_layout.setObjectName('widget_layout_' + tab_title)

            scrollArea = QScrollArea(tab_widget)
            scrollArea.setFrameShape(QFrame.NoFrame)

            scrollArea_contents = QWidget()
            scrollArea_contents.setObjectName('tab_scroll_area_' + tab_title)

            tab_layout = QVBoxLayout(scrollArea_contents)
            tab_layout.setObjectName('layout_' + tab_title)

            scrollArea.setWidgetResizable(True)

            scrollArea.setWidget(scrollArea_contents)
            cont_layout.addWidget(scrollArea)

            self._source_doc_manager.registerContainer(
                tab_layout, doc_type_id
            )

            for doc in doc_obj:

                try:
                    # add doc widgets
                    self._source_doc_manager.insertDocFromModel(
                        doc, doc_type_id
                    )
                except DummyException as ex:
                    LOGGER.debug(str(ex))

            self.tbSupportingDocs.addTab(
                tab_widget, tab_title
            )
            progress_dialog.setValue(i + 1)

        progress_dialog.deleteLater()
        del progress_dialog

    # def _on_node_reference_changed(self, rootHash):
    #     """
    #     Method for resetting document listing and map preview
    #     if another root node and its children
    #     are selected then the documents are reset as
    #     well as the map preview control.
    #     """
    #     if rootHash != self._curr_rootnode_hash:
    #         self._deleteSourceDocTabs()
    #         self._curr_rootnode_hash = rootHash

    def _progressStart(self):
        """
        Load progress dialog window.
        For items whose durations is unknown,
        'isindefinite' = True by default.
        If 'isindefinite' is False, then
        'rangeitems' has to be specified.
        """
        pass

    def _progressFinish(self):
        """
        Hide progress dialog window.
        """
        pass

    def _edit_permissions(self):
        """
        Returns True/False whether the current logged in user
        has permissions to create new social tenure relationships.
        If true, then the system assumes that
        they can also edit STR records.
        """
        canEdit = False
        userName = globals.APP_DBCONN.User.UserName
        authorizer = Authorizer(userName)
        newSTRCode = "9576A88D-C434-40A6-A318-F830216CA15A"

        # Get the name of the content from the code
        cnt = Content()
        createSTRCnt = cnt.queryObject().filter(
            Content.code == newSTRCode
        ).first()
        if createSTRCnt:
            name = createSTRCnt.name
            canEdit = authorizer.CheckAccess(name)

        return canEdit


class EntitySearchItem(QObject):
    """
    Abstract class for implementation by widgets that
    enable users to search for entity records.
    """

    def __init__(self, formatter=None):
        super().__init__()
        # Specify the formatter that should be
        # applied on the result item. It should
        # inherit from 'stdm.navigation.STRNodeFormatter'
        self.formatter = formatter

    def setNodeFormatter(self, formatter):
        """
        Set the formatter that should be
        applied on the entity search results.
        """
        self.formatter = formatter

    def validate(self):
        """
        Method for validating the input arguments
        before a search is conducted.
        Should return bool indicating whether validation
        was successful and message (applicable if validation fails).
        """
        raise NotImplementedError()

    def executeSearch(self):
        """
        Implemented when the a search operation
        is executed. Should return tuple of formatted
        results for render in the tree view,raw
        object results and search word.
        """
        raise NotImplementedError(
            str(
                QApplication.translate(
                    "ViewSTR",
                    "Subclass must implement abstract method."
                )
            )
        )

    def loadAsync(self):
        """
        Any initialization that needs to be carried
        out when the parent container is activated.
        """
        pass

    def errorHandler(self, error):
        """
        Generic handler that logs error
        messages to the QGIS message log
        """
        # QgsMessageLog.logMessage(error,2)
        LOGGER.debug(error)

    def reset(self):
        """
        Clear search results.
        """
        pass


WIDGET2, BASE2 = uic.loadUiType(
    GuiUtils.get_ui_file_path('ui_str_view_entity.ui'))


class STRViewEntityWidget(WIDGET2, BASE2, EntitySearchItem):
    """
    A widget that represents options for searching through an entity.
    """
    asyncStarted = pyqtSignal()
    asyncFinished = pyqtSignal()

    def __init__(self, config, formatter=None, parent=None):
        QWidget.__init__(self, parent)
        EntitySearchItem.__init__(self, formatter)
        self.setupUi(self)

        self.tbSTRViewEntity.setTabIcon(0, GuiUtils.get_icon('filter.png'))
        self.tbSTRViewEntity.setTabIcon(1, GuiUtils.get_icon('period_blue.png'))

        self.config = config
        self.setConfigOptions()
        self.curr_profile = current_profile()
        self.social_tenure = self.curr_profile.social_tenure
        self.str_model = entity_model(self.social_tenure)
        # Model for storing display and actual mapping values
        self._completer_model = None
        self._proxy_completer_model = None

        # Hook up signals
        self.cboFilterCol.currentIndexChanged.connect(
            self._on_column_index_changed
        )
        self.init_validity_dates()
        self.validity_from_date.dateChanged.connect(
            self.set_minimum_to_date
        )
        self.validity.setDisabled(True)
        self.init_validity_checkbox()

    def init_validity_checkbox(self):
        self.check_box_list = []
        self.validity_checkbox = QCheckBox()

        self.check_box_list.append(self.validity_checkbox)
        self.tbSTRViewEntity.tabBar().setTabButton(
            self.tbSTRViewEntity.tabBar().count() - 1,
            QTabBar.LeftSide, self.validity_checkbox
        )
        self.validity_checkbox.stateChanged.connect(self.toggle_validity_period)

    def toggle_validity_period(self, state):
        if state == Qt.Checked:
            self.validity.setDisabled(False)
        else:
            self.validity.setDisabled(True)

    def set_minimum_to_date(self):
        """
        Set the minimum to date based on the
        change in value of from date.
        :return:
        :rtype:
        """
        self.validity_to_date.setMinimumDate(
            self.validity_from_date.date()
        )

    def init_validity_dates(self):
        """
        Initialize the dates by setting the current date.
        :return:
        :rtype:
        """
        self.validity_from_date.setDate(
            date.today()
        )
        self.validity_to_date.setDate(
            date.today()
        )

    def setConfigOptions(self):
        """
        Apply configuration options.
        """
        # Set filter columns and remove id column
        for col_name, display_name in self.config.filterColumns.items():
            if col_name != "id":
                self.cboFilterCol.addItem(
                    display_name, col_name
                )

    def loadAsync(self):
        """
        Asynchronously loads an entity's attribute values.
        """
        self.asyncStarted.emit()

        # Create model worker
        workerThread = QThread(self)
        modelWorker = ModelWorker()
        modelWorker.moveToThread(workerThread)

        # Connect signals
        modelWorker.error.connect(self.errorHandler)
        workerThread.started.connect(
            lambda: modelWorker.fetch(
                self.config.STRModel, self.currentFieldName()
            )
        )
        modelWorker.retrieved.connect(self._asyncFinished)
        modelWorker.retrieved.connect(workerThread.quit)
        workerThread.finished.connect(modelWorker.deleteLater)
        workerThread.finished.connect(workerThread.deleteLater)

        # Start thread
        workerThread.start()

    def validate(self):
        """
        Validate entity search widget
        """
        is_valid = True
        message = ""

        if self.txtFilterPattern.text() == "":
            message = QApplication.translate(
                "ViewSTR", "Search word cannot be empty."
            )
            is_valid = False

        return is_valid, message

    def executeSearch(self):
        """
        Base class override.
        Search for matching items for the specified entity and column.
        """
        model_root_node = None

        prog_dialog = QProgressDialog(self)
        prog_dialog.setFixedWidth(380)
        prog_dialog.setWindowTitle(
            QApplication.translate(
                "STRViewEntityWidget",
                "Searching for STR..."
            )
        )
        prog_dialog.show()
        prog_dialog.setRange(
            0, 10
        )
        search_term = self._searchTerm()

        prog_dialog.setValue(2)
        # Try to get the corresponding search term value from the completer model
        if self._completer_model is not None:
            reg_exp = QRegExp("^%s$" % search_term, Qt.CaseInsensitive,
                              QRegExp.RegExp2)
            self._proxy_completer_model.setFilterRegExp(reg_exp)

            if self._proxy_completer_model.rowCount() > 0:
                # Get corresponding actual value from the first matching item
                value_model_idx = self._proxy_completer_model.index(0, 1)
                source_model_idx = self._proxy_completer_model.mapToSource(
                    value_model_idx
                )
                prog_dialog.setValue(4)
                search_term = self._completer_model.data(
                    source_model_idx, Qt.DisplayRole
                )

        modelInstance = self.config.STRModel()

        modelQueryObj = modelInstance.queryObject()

        queryObjProperty = getattr(
            self.config.STRModel, self.currentFieldName()
        )

        entity_name = modelQueryObj._primary_entity._label_name

        entity = self.curr_profile.entity_by_name(entity_name)

        prog_dialog.setValue(6)
        # Get property type so that the filter can
        # be applied according to the appropriate type
        propType = queryObjProperty.property.columns[0].type
        results = []
        try:
            if not isinstance(propType, String):

                col_name = self.currentFieldName()
                col = entity.columns[self.currentFieldName()]

                if col.TYPE_INFO == 'LOOKUP':
                    lookup_entity = lookup_parent_entity(
                        self.curr_profile, col_name
                    )
                    lkp_model = entity_model(lookup_entity)
                    lkp_obj = lkp_model()
                    value_obj = getattr(
                        lkp_model, 'value'
                    )

                    result = lkp_obj.queryObject().filter(
                        func.lower(value_obj) == func.lower(search_term)
                    ).first()
                    if result is None:
                        result = lkp_obj.queryObject().filter(
                            func.lower(value_obj).like(search_term + '%')
                        ).first()

                    if result is not None:
                        results = modelQueryObj.filter(
                            queryObjProperty == result.id
                        ).all()

                    else:
                        results = []

            else:
                results = modelQueryObj.filter(
                    func.lower(queryObjProperty) == func.lower(search_term)
                ).all()

            if self.validity.isEnabled():
                valid_str_ids = self.str_validity_period_filter(results)
            else:
                valid_str_ids = None

            prog_dialog.setValue(7)
        except exc.StatementError:
            prog_dialog.deleteLater()
            del prog_dialog
            return model_root_node, [], search_term

        # if self.formatter is not None:
        # self.formatter.setData(results)
        # model_root_node = self.formatter.root(valid_str_ids)
        prog_dialog.setValue(10)
        prog_dialog.hide()

        prog_dialog.deleteLater()
        del prog_dialog

        return results, search_term

    def str_validity_period_filter(self, results):
        """
        Filter the entity results using validity period in STR table.
        :param results: Entity result
        :type results: SQLAlchemy result proxy
        :return: Valid list of STR ids
        :rtype: List
        """
        self.str_model_obj = self.str_model()
        valid_str_ids = []
        for result in results:
            from_date = self.validity_from_date.date().toPyDate()
            to_date = self.validity_to_date.date().toPyDate()
            entity_id = '{}_id'.format(result.__table__.name[3:])
            str_column_obj = getattr(self.str_model, entity_id)
            str_result = self.str_model_obj.queryObject().filter(
                self.str_model.validity_start >= from_date).filter(
                self.str_model.validity_end <= to_date
            ).filter(str_column_obj == result.id).all()

            for res in str_result:
                valid_str_ids.append(res.id)

        return valid_str_ids

    def reset(self):
        """
        Clear search input parameters.
        """
        self.txtFilterPattern.clear()
        if self.cboFilterCol.count() > 0:
            self.cboFilterCol.setCurrentIndex(0)

    def currentFieldName(self):
        """
        Returns the name of the database field
        from the current item in the combo box.
        """
        curr_index = self.cboFilterCol.currentIndex()
        field_name = self.cboFilterCol.itemData(curr_index)

        if field_name is None:
            return
        else:
            return field_name

    def _searchTerm(self):
        """
        Returns the search term specified by the user.
        """
        return self.txtFilterPattern.text()

    def _asyncFinished(self, model_values):
        """
        Slot raised when worker has finished retrieving items.
        """
        # Create QCompleter and add values to it.
        self._update_completer(model_values)
        self.asyncFinished.emit()

    def _update_completer(self, values):
        # Get the items in a tuple and put them in a list

        # Store display and actual values in a
        # model for easier mapping and
        # retrieval when carrying out searches

        model_attr_mapping = []

        # Check if there are formaters specified
        # for the current field name
        for mv in values:
            f_model_values = []

            m_val = mv[0]

            if m_val is not None:
                col_label = self.currentFieldName()
                if col_label in self.config.LookupFormatters:
                    formatter = self.config.LookupFormatters[col_label]
                    if formatter.column.TYPE_INFO == 'LOOKUP':
                        m_val = formatter.code_value(m_val)[0]
                    else:
                        m_val = formatter.format_column_value(m_val)
            f_model_values.extend([m_val, m_val])

            model_attr_mapping.append(f_model_values)

        self._completer_model = BaseSTDMTableModel(model_attr_mapping, ["", ""], self)

        # We will use the QSortFilterProxyModel for filtering purposes
        self._proxy_completer_model = QSortFilterProxyModel()
        self._proxy_completer_model.setDynamicSortFilter(True)
        self._proxy_completer_model.setSourceModel(self._completer_model)
        self._proxy_completer_model.setSortCaseSensitivity(Qt.CaseInsensitive)
        self._proxy_completer_model.setFilterKeyColumn(0)

        # Configure completer
        mod_completer = QCompleter(self._completer_model, self)
        mod_completer.setCaseSensitivity(Qt.CaseInsensitive)
        mod_completer.setCompletionMode(QCompleter.PopupCompletion)
        mod_completer.setCompletionColumn(0)
        mod_completer.setCompletionRole(Qt.DisplayRole)

        self.txtFilterPattern.setCompleter(mod_completer)

    def _on_column_index_changed(self, int):
        """
        Slot raised when the user selects a different filter column.
        """
        self.txtFilterPattern.clear()
        self.loadAsync()


class EntityConfiguration(object):
    """
    Specifies the configuration to apply when creating
    a new tab widget for performing entity searches.
    """
    browseDescription = "Click on the browse button below to load entity " \
                        "records and their corresponding social tenure " \
                        "relationship definitions."
    defaultFieldName = ""
    # Format of each dictionary item:
    # property/db column name - display name
    filterColumns = OrderedDict()
    displayColumns = OrderedDict()
    groupBy = ""
    STRModel = None
    Title = ""
    data_source_name = ""
    # Functions for formatting values before
    # they are loaded into the completer
    LookupFormatters = {}

    def __init__(self):
        # Reset filter and display columns
        self.filterColumns = OrderedDict()
        self.displayColumns = OrderedDict()


class ModelWorker(QObject):
    """
    Worker for retrieving model attribute
    values stored in the database.
    """
    retrieved = pyqtSignal(object)
    error = pyqtSignal(str)

    pyqtSlot(object, str)

    def fetch(self, model, fieldname):
        """
        Fetch attribute values from the
        database for the specified model
        and corresponding column name.
        """
        try:
            if hasattr(model, fieldname):
                modelInstance = model()
                obj_property = getattr(model, fieldname)
                model_values = modelInstance.queryObject(
                    [obj_property]
                ).distinct()
                self.retrieved.emit(model_values)

        except DummyException as ex:
            self.error.emit(str(ex))
