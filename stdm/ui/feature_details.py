# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Feature Details Viewer
Description          : GUI widget for viewing details of a feature on
                        the map canvas.
Date                 : 10/October/2016
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
import logging
import re
from collections import OrderedDict
from typing import Optional

from qgis.PyQt import sip
from qgis.PyQt import uic
from qgis.PyQt.QtCore import (
    QDateTime,
    QDate
)
from qgis.PyQt.QtGui import (
    QStandardItem,
    QStandardItemModel,
    QIcon,
    QColor
)
from qgis.PyQt.QtWidgets import (
    QMessageBox,
    QTreeView,
    QAbstractItemView,
    QApplication,
    QWidget,
    QVBoxLayout
)
from qgis.core import (
    QgsFeatureRequest,
    QgsExpression,
    QgsMapLayer,
    NULL,
    QgsFeature,
    QgsProject
)
from qgis.gui import (
    QgsHighlight,
    QgsDockWidget,
    QgsMapCanvas
)
from qgis.utils import iface

from stdm.data.configuration import (
    entity_model,
)
from stdm.data.configuration.entity import Entity

from stdm.data.globals import ENTITY_FORMATTERS
from stdm.data.pg_utils import pg_table_exists
from stdm.data.pg_utils import (
    spatial_tables,
    pg_views
)
from stdm.data.supporting_documents import (
    supporting_doc_tables,
    document_models
)
from stdm.exceptions import DummyException
from stdm.settings import current_profile
from stdm.settings.registryconfig import (
    selection_color
)
from stdm.ui.forms.editor_dialog import EntityEditorDialog
from stdm.ui.forms.widgets import ColumnWidgetRegistry
from stdm.ui.gui_utils import GuiUtils
from stdm.ui.social_tenure.str_editor import EditSTREditor
from stdm.utils.util import (
    format_name,
    entity_attr_to_model
)

# TODO: the base class here shouldn't really be QWidget, but
# the levels of inheritance here prohibit us to make the subclass
# a QObject subclass without causing diamond inheritance issues

LOGGER = logging.getLogger("stdm")
LOGGER.setLevel(logging.DEBUG)

class LayerSelectionHandler(QWidget):
    """
     Handles all tasks related to the layer.
    """
    def __init__(self, parent, plugin):
        super().__init__(parent)
        """
        Initializes the LayerSelectionHandler.
        :param iface: The QGIS Interface object
        :type iface: Object
        :param plugin: The STDM plugin object
        :type plugin: Object
        """
        self.layer = None
        self.plugin = plugin
        self.sel_highlight: Optional[QgsHighlight] = None
        self.current_profile = current_profile()

        QgsProject.instance().layerWillBeRemoved[QgsMapLayer].connect(self._layer_will_be_removed)

    def __del__(self):
        # Gracefully cleanup layer highlight -- we don't have ownership of it
        self.clear_sel_highlight()

    def _layer_will_be_removed(self, layer: QgsMapLayer):
        """
        Triggered when a layer will be removed
        """
        if self.sel_highlight and layer == self.sel_highlight.layer():
            self.clear_sel_highlight()

    def selected_features(self):
        """
        Returns a selected feature spatial unit
        id and code as key and value.
        :return: Dictionary
        """
        if self.layer is None:
            return None

        if self.stdm_layer(self.layer):
            selected_features = self.layer.selectedFeatures()
            features = []
            field_names = [
                field.name()
                for field in self.layer.fields()]
            for feature in selected_features:
                if 'id' in field_names:
                    features.append(feature)
            if len(features) > 40:
                max_error = QApplication.translate(
                    'LayerSelectionHandler',
                    'You have exceeded the maximum number of features that \n'
                    'can be selected and queried by Spatial Entity Details. \n'
                    'Please select a maximum of 40 features.'
                )

                QMessageBox.warning(
                    iface.mainWindow(),
                    QApplication.translate(
                        'LayerSelectionHandler', 'Maximum Features Error'
                    ),
                    max_error
                )
                return None
            return features
        else:
            return None

    def non_stdm_layer_error(self):
        """
        Shows an error if the layer is not an STDM entity layer.
        """
        not_feature_msg = QApplication.translate(
            'LayerSelectionHandler',
            'You have selected a non-STDM layer. \n'
            'Please select an STDM layer to view \n'
            'the details.'
        )

        QMessageBox.warning(
            iface.mainWindow(),
            QApplication.translate(
                'LayerSelectionHandler', 'Invalid Layer Error'
            ),
            not_feature_msg
        )

    def get_layer_source(self, layer):
        """
        Get the layer table name if the source is from the database.
        :param layer: The layer for which the source is checked
        :type layer: QgsVectorLayer
        :return: Table name.
        :rtype: str
        """

        if layer is None:
            return ''

        source = layer.source()

        if source is None:
            return ''

        p_str = str(source)
        src1 = p_str.replace('"',"'")
        src3 = src1.replace("'public'.", '')


        # vals = dict(re.findall(r'(\S+)="?(.*?)"? ', src3))
        # table_name = ''
        # try:
        #     table = vals['table'].split('.')

        #     table_name = table[1].strip('"')
        # except KeyError:
        #     table_name = ''

        pattern = r"(\b[^=]+?)=('[^']*'|\d+)"
        result = dict()

        for match in re.findall(pattern, src3):
            key, value = match  # Now unpacking only two elements
            # If value is enclosed in quotes, remove them
            if value[0] == "'" and value[-1] == "'":
                value = value[1:-1]
            # Try converting to integer, otherwise keep as string
            try:
                result[key] = int(value)
            except ValueError:
                result[key] = value

        if len(result) > 0:
            table_name = result['table']
        else:
            return ""

        if table_name in pg_views():
            return table_name

        entity_table = self.current_profile.entity_by_name(table_name)

        return table_name

    def active_layer_check(self):
        """
        Check if there is active layer and if not, displays
        a message box to select a feature layer.
        """
        active_layer = iface.activeLayer()

        if active_layer is None:
            no_layer_msg = QApplication.translate(
                'LayerSelectionHandler',
                'Please select a spatial entity '
                'layer to view feature details.'
            )
            QMessageBox.critical(
                iface.mainWindow(),
                QApplication.translate(
                    'LayerSelectionHandler', 'Layer Error'
                ),
                no_layer_msg
            )

    def stdm_layer(self, active_layer):
        """
        Check whether the layer is feature layer or not.
        :param active_layer: The layer to be checked
        :type active_layer: QGIS VectorLayer
        :return: True if the active layer is STDM layer or False if it is not.
        :rtype: Boolean
        """
        source_found = True

        layer_source = self.get_layer_source(active_layer)

        if layer_source == '':
            source_found = False

        return source_found

    def activate_select_tool(self):
        """
        Enables the select tool to be used to select features.
        """
        iface.actionSelect().trigger()
        layer_select_tool = iface.mapCanvas().mapTool()

        layer_select_tool.activate()

    def disable_feature_details_btn(self):
        """
        Disables features details button.
        :return:
        :rtype:
        """
        self.plugin.feature_details_act.setChecked(False)

    def clear_sel_highlight(self):
        """
        Removes sel_highlight from the canvas.
        """
        if self.sel_highlight is not None and not sip.isdeleted(self.sel_highlight):
            iface.mapCanvas().scene().removeItem(self.sel_highlight)

        self.sel_highlight = None

    def refresh_layers(self):
        """
        Refresh all database layers.
        """
        layers = list(QgsProject.instance().mapLayers().values())
        for layer in layers:
            layer.dataProvider().forceReload()
            layer.triggerRepaint()
        if iface.activeLayer() is not None:
            canvas = iface.mapCanvas()
            canvas.setExtent(
                iface.activeLayer().extent()
            )
            iface.mapCanvas().refresh()

    def multi_select_highlight(self, index):
        """
        Highlights a feature with rubberBald
        class when selecting
        features are more than one.
        :param index: Selected QTreeView item index
        :type index: Integer
        """
        pass


class DetailsDBHandler(LayerSelectionHandler):
    """
    Handles the database linkage of the spatial entity details.
    """

    def __init__(self, parent, plugin):
        """
        Initializes the DetailsDBHandler.
        """
        self.plugin = plugin
        self._entity = None
        self.column_formatter = OrderedDict()
        self.formatted_columns = OrderedDict()
        self.current_profile = current_profile()
        self._formatted_record = OrderedDict()
        self.display_columns = None
        self._entity_supporting_doc_tables = {}
        super().__init__(parent, plugin)

    def set_entity(self, entity):
        """
        Sets the spatial entity.
        :param entity: The entity object
        :type entity: Object
        """
        self._entity = entity

    def set_formatter(self, entity=None):
        """
        Sets the column widget formatter.
        :param entity: The entity for which the columns are to be formatted.
        :type entity: Object
        """
        self.format_columns(entity)

    def format_columns(self, entity=None):
        """
        Formats the columns using the ColumnWidgetRegistry factory method.
        :param entity: The entity of the columns to be formatted.
        :type entity: Object
        """
        if entity is None:
            entity = self._entity

        if entity is None:
            return

        if entity.name in ENTITY_FORMATTERS.keys():
            self.column_formatter = ENTITY_FORMATTERS[entity.name]
            return

        for col in entity.columns.values():
            col_name = col.name

            # Get widget factory so that we can use the value formatter
            widget_factory = ColumnWidgetRegistry.factory(
                col.TYPE_INFO
            )
            if widget_factory is not None:
                formatter = widget_factory(col)
                self.column_formatter[col_name] = formatter
        ENTITY_FORMATTERS[entity.name] = self.column_formatter

    def display_column_object(self, entity):
        """
        Returns entity display columns.
        :param entity: Entity
        :type entity: Class
        :return: List of column names.
        :rtype: List
        """
        self.display_columns = [
            c
            for c in
            entity.columns.values()
            if c.TYPE_INFO in [
                'VARCHAR',
                'TEXT',
                'INT',
                'DOUBLE',
                'DATE',
                'DATETIME',
                'BOOL',
                'LOOKUP',
                'ADMIN_SPATIAL_UNIT',
                'PERCENT',
                'AUTO_GENERATED',
                'EXPRESSION'
            ]
        ]

    def feature_model(self, entity: Entity, id: int):
        """
        Gets the model of an entity based on an id and the entity.
        :param entity: Entity
        :type entity: Object
        :param id: Id of the record
        :type id: Integer
        :return: SQLAlchemy result proxy
        :rtype: Object
        """
        model = entity_model(entity)
        model_obj = model()

        if isinstance(id, QgsFeature):
            id = id.id()

        # result = model_obj.queryObject().filter(model.id == id).all()
        result = model_obj.queryObject().all()
        if len(result) == 0:
            return None

        try:
            for r in result:
                if int(r.id) == int(id):
                    return r

            return result[0]
        except:
            return None


    def feature_str_link(self, feature_id: int, entity=None) -> list:
        """
        Gets all STR records linked to a feature, if the layer is a
        spatial unit layer.
        :param feature_id: The feature id/id of the spatial unit
        :type feature_id: Integer
        :return: The list of social tenure records
        :rtype: List
        """
        str_model = entity_model(
            self.current_profile.social_tenure
        )
        if entity is None:
            spatial_unit_entity_id = '{}_id'.format(
                self._entity.short_name.replace(' ', '_').lower())
        else:
            spatial_unit_entity_id = '{}_id'.format(
                entity.short_name.replace(' ', '_').lower())

        spatial_unit_col_obj = getattr(str_model, spatial_unit_entity_id)
        model_obj = str_model()
        # TODO Check if str_model.spatial_unit_id is correct
        result = model_obj.queryObject().filter(
            spatial_unit_col_obj == feature_id
        ).all()

        return result

    def party_str_link(self, party_entity: Entity, party_id: int):
        """
        Gets all STR records linked to a party, if the record is party record.
        :param party_id: The party id/id of the spatial unit
        :type party_id: Integer
        :return: The list of social tenure records
        :rtype: List
        """
        str_model = entity_model(
            self.current_profile.social_tenure
        )
        model_obj = str_model()
        party_name = party_entity.name

        party_entity_id = f"{(party_entity.short_name.lower().replace(' ','_'))}_id"

        party_col_obj = getattr(str_model, party_entity_id)

        result = model_obj.queryObject().filter(
            party_col_obj == party_id
        ).all()

        return result

    def column_widget_registry(self, model, entity):
        """
        Registers the column widgets using the model and the entity.
        :param model: The model of the entity
        :type model: SQLAlchemy model
        :param entity: The entity object
        :type entity: Object
        """
        self._formatted_record.clear()

        self.display_column_object(entity)

        for col in self.display_columns:
            if isinstance(model, OrderedDict):
                if col.name in model.keys():
                    col_val = model[col.name]
                else:
                    continue
            else:
                col_val = getattr(model, col.name)
            # Check if there are display formatters and apply if
            # one exists for the given attribute.
            if col_val == NULL:
                col_val = None

            if col.name in self.column_formatter:
                formatter = self.column_formatter[col.name]
                col_val = formatter.format_column_value(col_val)

            if col.ui_display() == QApplication.translate(
                    'DetailsDBHandler', 'Tenure Share'
            ):
                share = '{} (%)'.format(col.ui_display())
                self._formatted_record[share] = col_val
            else:
                self._formatted_record[col.ui_display()] = col_val

    def _supporting_doc_models(self, entity_table, model_obj):
        """
        Creates supporting document models using information from the
        entity table and values in the model object.
        :param entity_table: Name of the entity table.
        :type entity_table: str
        :param model_obj: Model instance.
        :type model_obj: object
        :return: Supporting document models.
        :rtype: list
        """
        # Only one document table per entity for now
        if entity_table in self._entity_supporting_doc_tables:
            doc_table_ref = self._entity_supporting_doc_tables[entity_table]
        else:
            doc_tables = supporting_doc_tables(entity_table)

            if len(doc_tables) > 0:
                doc_table_ref = doc_tables[0]
                self._entity_supporting_doc_tables[
                    entity_table] = doc_table_ref

            else:
                return []

        doc_link_col, doc_link_table = doc_table_ref[0], doc_table_ref[1]

        if not hasattr(model_obj, 'id'):
            return []

        return document_models(
            self.current_profile.social_tenure,
            doc_link_col,
            model_obj.id
        )


WIDGET, BASE = uic.loadUiType(
    GuiUtils.get_ui_file_path('ui_feature_details.ui'))


class DetailsDockWidget(WIDGET, QgsDockWidget):
    """
    The logic for the spatial entity details dock widget.
    """

    def __init__(self, map_canvas: QgsMapCanvas, plugin):
        """
        Initializes the DetailsDockWidget.
        """
        super().__init__()

        self.setupUi(self)

        self.edit_btn.setIcon(GuiUtils.get_icon('edit.png'))
        self.delete_btn.setIcon(GuiUtils.get_icon('remove.png'))
        self.view_document_btn.setIcon(GuiUtils.get_icon('document.png'))

        self.map_canvas = map_canvas

        self.edit_btn.setDisabled(True)
        self.delete_btn.setDisabled(True)
        self.view_document_btn.setDisabled(True)
        self.setBaseSize(300, 5000)

        self.details_tree_view = DetailsTreeView(self, plugin, delete_button=self.delete_btn, edit_button=self.edit_btn,
                                                 view_document_button=self.view_document_btn)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.details_tree_view)
        self.tree_container.setLayout(layout)

        if map_canvas:
            map_canvas.currentLayerChanged.connect(
                lambda: self.details_tree_view.activate_feature_details(False)
            )

    def init_connections(self):
        """
        Initializes visibility based connections for the dock
        """
        self.visibilityChanged.connect(self._visibility_changed)

    def remove_connections(self):
        """
        Removes visibility based connections for the dock
        """
        self.visibilityChanged.disconnect(self._visibility_changed)

    def _visibility_changed(self, visible: bool):
        """
        Called when dock visibility is changed
        """
        if not visible:
            self.clear_feature_selection()
        else:
            self.details_tree_view.activate_feature_details(True)

    def clear_feature_selection(self):
        """
        Clears selection of layer(s).
        """

        if not self.map_canvas:
            return

        for layer in self.map_canvas.layers():
            if layer.type() == layer.VectorLayer:
                layer.removeSelection()
        self.map_canvas.refresh()


class DetailsTreeView(DetailsDBHandler):
    """
    Avails the treeview dock widget. This class must be called
    to add the widget.
    """

    def __init__(self, parent=None, plugin=None, edit_button=None, delete_button=None, view_document_button=None):
        """
        The method initializes the dockwidget.
        :param plugin: The STDM plugin
        :type plugin: class
        """
        from .entity_browser import _EntityDocumentViewerHandler
        super().__init__(parent, plugin=plugin)

        self.plugin = plugin

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.view = QTreeView()
        layout.addWidget(self.view)
        self.setLayout(layout)

        self.view.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.edit_button = edit_button
        self.delete_button = delete_button
        self.view_document_button = view_document_button

        self.layer_table = None
        self.entity = None
        self.feature_models = {}
        self.party_models = {}
        self.str_models = {}
        self.feature_str_model = {}
        self.removed_feature = None
        self.selected_root = None
        self.party_items = {}
        self._selected_features = []
        self.spatial_unit_items = {}
        self.model = QStandardItemModel()
        self.view.setModel(self.model)
        self.view.setUniformRowHeights(True)
        self.view.setRootIsDecorated(True)
        self.view.setAlternatingRowColors(True)
        self.view.setWordWrap(True)
        self.view.setHeaderHidden(True)
        self.view.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        self.str_text = QApplication.translate(
            'DetailsTreeView',
            'Social Tenure Relationship'
        )
        self.view.setStyleSheet(
            '''
            QTreeView:!active {
                selection-background-color: #72a6d9;
            }
            '''
        )
        self.current_profile = current_profile()
        if self.current_profile is None:
            return

        self.social_tenure = self.current_profile.social_tenure
        self.spatial_units = self.social_tenure.spatial_units

        self.view.setMinimumWidth(250)
        self.doc_viewer_title = QApplication.translate(
            'DetailsTreeView',
            'Document Viewer'
        )
        self.doc_viewer = _EntityDocumentViewerHandler(
            self.doc_viewer_title, iface.mainWindow()
        )

        self.view_selection = self.view.selectionModel()

        self.view_selection.currentChanged.connect(
            self._on_view_selection_changed
        )

        # show tree message if dock is open and button clicked
        if self.plugin is not None:
            not_feature_msg = QApplication.translate(
                'FeatureDetails',
                'Please select an STDM layer to view \n'
                'the details.'
            )

            self.treeview_error(not_feature_msg)

        if self.edit_button is not None:
            self.edit_button.clicked.connect(self.edit_selected_node)
        if self.delete_button is not None:
            self.delete_button.clicked.connect(self.delete_selected_item)
        if self.view_document_button is not None:
            self.view_document_button.clicked.connect(self.view_node_document)

    def zoom_to_selected(self, layer):
        """
        Zooms to selected features.
        :param layer: The layer of the features.
        :type layer: QgsVectorLayer
        :return:
        :rtype:
        """
        box = layer.boundingBoxOfSelected()
        box.scale(1.2)
        canvas = iface.mapCanvas()
        canvas.setExtent(box)
        canvas.refresh()

    def _on_view_selection_changed(self, current, previous):
        """
        Triggered when the view selection is changed
        """
        self.multi_select_highlight(current)

        selected_item = self.model.itemFromIndex(current)
        if self.delete_button is not None:
            self.delete_button.setEnabled(bool(selected_item is not None and selected_item.data() is not None))

        is_str_node = bool(
            selected_item is not None and selected_item.data() is not None and selected_item.text() == self.str_text)
        if self.edit_button is not None:
            self.edit_button.setEnabled(is_str_node)
        if self.view_document_button is not None:
            self.view_document_button.setEnabled(is_str_node)

    def set_layer_entity(self):
        """
        Sets the entity property using the layer table.
        """
        self.layer_table = self.get_layer_source(
            iface.activeLayer()
        )
        if self.layer_table == '':
            return

        if self.layer_table in spatial_tables() and \
                self.layer_table not in pg_views():
            self.entity = self.current_profile.entity_by_name(self.layer_table)

    #
    # def activate_feature_details(self, button_clicked=True):
    #     if cProfile is None:
    #         return
    #     cProfile.runctx('self._activate_feature_details(button_clicked)', globals(), locals())

    def db_configuration_done(self):
        config_done = True
        if not pg_table_exists(self.current_profile.social_tenure.name):
            config_done = False
            msg = QApplication.translate(
                "DetailsTreeView",
                'The system has detected that '
                'the required database tables are missing. \n'
                'Please run the configuration wizard to configure the database ')
            QMessageBox.critical(
                iface.mainWindow(),
                QApplication.translate(
                    "DetailsTreeView",
                    'Default Profile Error'
                ),
                msg
            )

        return config_done

    def activate_feature_details(self, checked: bool = True, follow_layer_selection: bool = True):
        """
        A slot raised when the feature details button is clicked.
        :param checked: A boolean to identify if it is activated
        because of button click or because of change in the active layer.
        :type checked: Boolean
        """
        if not checked:
            return

        # if self.plugin is None:
        # Registry column widget
        # set formatter for social tenure relationship.

        if not self.db_configuration_done():
            return

        self.set_formatter(self.social_tenure)
        for party in self.social_tenure.parties:
            self.set_formatter(party)

        for spatial_unit in self.social_tenure.spatial_units:
            self.set_formatter(spatial_unit)
            custom_attr_entity = self.social_tenure.spu_custom_attribute_entity(
                spatial_unit
            )
            self.set_formatter(custom_attr_entity)
            # return
        # Get and set the active layer.
        self.layer = iface.activeLayer()

        # if no active layer, show error message
        # and uncheck the feature tool

        # self.zoom_to_selected(self.layer)

        if follow_layer_selection and self.layer is None:
            self.active_layer_check()
            self.plugin.feature_details_act.setChecked(False)
            return

        # if the selected layer is not an STDM layer,
        # show not feature layer.
        if self.layer is not None and not self.stdm_layer(self.layer):
            # show popup message if dock is hidden and button clicked
            self.non_stdm_layer_error()
            self.plugin.feature_details_act.setChecked(False)

        # If the selected layer is feature layer, get data and
        # display treeview in a dock widget
        elif self.layer is not None:
            self.prepare_for_selection(follow_layer_selection)

    def prepare_for_selection(self, follow_layer_selection: bool = True):
        """
        Prepares the dock widget for data loading.
        """
        # enable the select tool
        if follow_layer_selection:
            self.activate_select_tool()
        self.update_tree_source(self.layer, follow_layer_selection)

    def update_tree_source(self, active_layer, follow_layer_selection: bool = True):
        """
        Updates the treeview source in case of layer change.
        :param active_layer: The active layer on the canvas.
        :type active_layer: QgsVectorLayer
        """
        if active_layer.type() != QgsMapLayer.VectorLayer:
            return
        # set entity from active layer in the child class
        self.set_layer_entity()

        # set entity for the super class DetailModel
        self.set_entity(self.entity)

        if follow_layer_selection:
            active_layer.selectionChanged.connect(
                self.layer_selection_changed
            )

    def reset_tree_view(self, features=None):
        """
        Resets the treeview by clearing feature highlights,
        disabling edit, delete, and view document buttons,
        and adding an empty treeview if a feature is selected.
        """
        # clear feature_ids list, model and highlight
        self.model.clear()

        self.clear_sel_highlight()  # remove sel_highlight
        if self.removed_feature is None:
            self.str_models.clear()
            self.feature_models.clear()
            self.party_items.clear()
            self.spatial_unit_items.clear()
        else:
            self.removed_feature = None

    def layer_selection_changed(self):
        """
        Triggered when the layer selection has changed.
        Shows the treeview.
        """

        str_records = []

        if self._selected_features is None:
            return

        self._selected_features[:] = []
        self._selected_features = self.selected_features()

        if self._selected_features is None:
            self.reset_tree_view()

            not_supported = QApplication.translate(
                'DetailsTreeView',
                'Spatial Entity Details is not supported for this layer.'
            )
            self.treeview_error(not_supported)
            return

        if len(self._selected_features) < 1:
            self.reset_tree_view(self._selected_features)
            return

        layer_icon = GuiUtils.get_icon('layer.gif')
        # add non entity layer for views.
        if self.entity is not None:
            self.reset_tree_view(self._selected_features)
            roots = self.add_parent_tree(
                layer_icon, format_name(self.entity.short_name)
            )

            if roots is None:
                return

            for feature, root in roots.items():

                self.spatial_unit_items[root.data()] = self.entity

                if isinstance(feature, QgsFeature):
                    id = feature.id()

                if not isinstance(id, int):
                    continue

                if self.entity in self.social_tenure.spatial_units:
                    str_records = self.feature_str_link(id)
 
                if len(str_records) > 0:
                    db_model = getattr(str_records[0], self.entity.name) # SQLAlchemy Object
                else:
                    data = self.features_data(id)

                    # if len(self.features_data(id)) > 0:
                    if len(data[0]) > 0:
                        db_model = data[0]  # OrderedDict
                    else:
                        db_model = self.feature_model(self.entity, id) # SQLAlchemy Object

                self.add_root_children(db_model, root, str_records)

        else:
            self.reset_tree_view(self._selected_features)
            self.add_non_entity_parent(layer_icon)

        # self.zoom_to_selected(self.layer)

    def search_spatial_unit(self, entity, spatial_unit_ids, select_matching_features: bool = True):
        """
        Shows the treeview.
        """
        self.reset_tree_view()
        layer_icon = GuiUtils.get_icon('layer.gif')
        # add non entity layer for views.

        # self.reset_tree_view(selected_features)
        for spu_id in spatial_unit_ids:

            root = QStandardItem(layer_icon, str(entity.short_name))
            root.setData(spu_id)
            self.spatial_unit_items[root.data()] = entity
            self.set_bold(root)
            self.model.appendRow(root)

            str_records = self.feature_str_link(spu_id, entity)


            if len(str_records) > 0:
                #db_model = getattr(str_records[list(str_records.keys())[0]], entity.name)
                db_model = getattr(str_records[0], entity.name)
            else:
                db_model = self.feature_model(entity, spu_id)

            self.add_root_children(db_model, root, str_records)

        if select_matching_features:
            #self.layer.selectByIds(list(self.feature_models.keys()))
            try:
                self.layer.selectByIds([spu_id])
            except DummyException:
                LOGGER.debug('No features selected')

        # self.zoom_to_selected(self.layer)

    def search_party(self, entity, party_ids):
        """
        Shows the treeview.
        """
        self.reset_tree_view()
        table_icon = GuiUtils.get_icon('table.png')
        # add non entity layer for views.

        str_records = []
        for spu_id in party_ids:
            str_records = self.party_str_link(entity, spu_id)

            root = QStandardItem(table_icon, str(entity.short_name))
            self.party_items[spu_id] = entity
            root.setData(spu_id)
            self.set_bold(root)
            self.model.appendRow(root)

            if len(str_records) > 0:
                db_model = getattr(str_records[0], entity.name)
            else:
                db_model = self.feature_model(entity, spu_id)

            self.add_root_children(db_model, root, str_records, True)

        if len(str_records) > 0 and self.layer_table is not None:
            if hasattr(str_records[0], 'id'):
                record = getattr(str_records[0], self.layer_table)  # Assuming we have an Id!!
                if record is not None:
                    return record.id
            else:
                return -1
        else:
            return -1

    def add_non_entity_parent(self, layer_icon):
        """
        Adds details of layers that are view based.
        :param layer_icon: The icon of the tree node.
        :type layer_icon: QIcon
        """
        for feature_map in self.features_data():
            parent = QStandardItem(
                layer_icon,
                format_name(str(self.layer.name()))
            )
            for k, v, in feature_map.items():
                if isinstance(v, QDate):
                    v = v.toPyDate()
                if isinstance(v, QDateTime):
                    v = v.toPyDateTime()
                if k != 'id':
                    child = QStandardItem('{}: {}'.format(
                        format_name(k, False), v)
                    )
                    child.setSelectable(False)
                    parent.appendRow([child])
            self.model.appendRow(parent)
            self.set_bold(parent)
            self.expand_node(parent)

    def features_data(self, feature_id: int=-1) -> list:
        """
        Gets data column and value of a feature from
        the selected layer and features.
        :param feature_id: The feature id
        :type feature_id: Integer
        :return: List of feature data with column and value
        """
        selected_features = self.layer.selectedFeatures()

        field_names = [field.name() for field in self.layer.fields()]
        feature_data = []

        for elem in selected_features:
            if feature_id != -1:
                if elem.id() == feature_id:
                    feature_map = OrderedDict(
                        list(zip(field_names, elem.attributes()))
                    )
                    feature_data.append(feature_map)
                    break
            else:
                feature_map = OrderedDict(
                    list(zip(field_names, elem.attributes()))
                )
                feature_data.append(feature_map)
        return feature_data

    def party_data(self, party_id=None):
        """
        Gets data column and value of a feature from party.
        :param party_id: The party id
        :type party_id: Integer
        :return: List of feature data with column and value
        :rtype: List
        """
        selected_features = self.layer.selectedFeatures()
        field_names = [field.name() for field in self.layer.fields()]
        feature_data = []

        for elem in selected_features:
            if party_id is not None:
                if elem.id() == party_id:
                    feature_map = OrderedDict(
                        list(zip(field_names, elem.attributes()))
                    )
                    feature_data.append(feature_map)
                    break
            else:
                feature_map = OrderedDict(
                    list(zip(field_names, elem.attributes()))
                )
                feature_data.append(feature_map)
        return feature_data

    def add_parent_tree(self, icon, title):
        """
        Adds the top root of the treeview into the model.
        :param icon: The icon of the item
        :type icon: QIcon
        :param title: The title of the item
        :type title: String
        :return: The root QStandardItem with the feature id
        :rtype: OrderedDict
        """

        roots = OrderedDict()
        selected_features = self._selected_features
        if selected_features is None:
            return None
        for feature_id in selected_features:
            root = QStandardItem(icon, str(title))
            root.setData(feature_id)
            self.set_bold(root)
            self.model.appendRow(root)
            roots[feature_id] = root
        return roots

    def add_root_children(self, model, parent, str_records, party_query=False):
        """
        Adds the root children.
        :param model: The entity model
        :type model: SQL Alchemy model
        :param parent: The root of the children
        :type parent: QStandardItem
        :param str_records: STR record models linked to the spatial unit.
        :type str_records: List
        """

        if model is None:
            return

        if isinstance(model, OrderedDict):
            feature_id = model['id']
        else:
            feature_id = model.id

        self.feature_models[feature_id] = model

        if not isinstance(model, OrderedDict):
            entity = self.current_profile.entity_by_name(model.__table__.name)

            self.column_widget_registry(model, entity)

        else:
            self.column_widget_registry(model, self.entity)

        for i, (col, row) in enumerate(self._formatted_record.items()):
            child = QStandardItem('{}: {}'.format(col, row))

            child.setSelectable(False)
            parent.appendRow([child])

            # Add Social Tenure Relationship node as a last child
            if i == len(self._formatted_record) - 1:
                if len(str_records) > 0:
                    self.add_str_child(parent, str_records, feature_id, party_query)
                elif self.entity is not None:

                    if self.entity in self.social_tenure.spatial_units:
                        self.add_no_str_steam(parent)

        self.expand_node(parent)

    def add_str_node(self, parent, str_id):
        """
        Adds the STR parent into the treeview.
        :param parent: The parent of the STR item, which is the
         child of the root.
        :type parent: QStandardItem
        :param str_id: The id of the STR record
        :type str_id: Integer
        :return: The STR root item
        :rtype: QStandardItem
        """
        str_icon = GuiUtils.get_icon(
            'social_tenure.png'
        )

        str_root = QStandardItem(str_icon, self.str_text)
        str_root.setData(str_id)
        self.set_bold(str_root)
        try:
            parent.appendRow([str_root])
        except RuntimeError:
            pass
        return str_root

    def add_no_str_steam(self, parent):
        """
        Adds NO STR Defined steam.
        :param parent: The root node.
        :type parent: QStandardItem
        """
        no_str_icon = GuiUtils.get_icon(
            'remove.png'
        )
        title = 'No STR Defined'
        no_str_root = QStandardItem(no_str_icon, str(title))
        self.set_bold(no_str_root)
        parent.appendRow([no_str_root])

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

        if parties is None:
            return

        for party in parties:
            party_name = party.short_name.lower().replace(' ', '_')
            party_id = '{}_id'.format(party_name)

            if party_id not in record:
                return None, None

            if record[party_id] is not None:
                return party, party_id

    def current_spatial_unit(self, record):
        """
        Gets the current party column name in STR
        table by finding party column with value
        other than None.
        :param record: The STR record or result.
        :type record: Dictionary
        :return: The party column name with value.
        :rtype: String
        """
        spatial_units = self.social_tenure.spatial_units

        for spatial_unit in spatial_units:
            spatial_unit_name = spatial_unit.name.split(self.current_profile.prefix, 1)[1]
            spatial_unit_id = '{}_id'.format(spatial_unit_name).lstrip('_')
            if spatial_unit_id not in record:
                return None, None
            if record[spatial_unit_id] is not None:
                return spatial_unit, spatial_unit_id

    def add_str_child(self, parent, str_records, feature_id, party_query=False):
        """
        Adds STR children into the treeview.
        :param parent: The root node.
        :type parent: QStandardItem
        :param str_records: STR record models linked to the spatial unit.
        :type str_records: List
        :param feature_id: The selected feature id.
        :type feature_id: Integer
        """
        if str_records is None:
            return

        # if self.layer_table is None and self.plugin is not None:
        #     return

        spatial_unit_names = [sp.name for sp in self.spatial_units]

        # If the layer table is not spatial unit table, don't show STR node.
        if self.layer_table is not None and self.layer_table not in spatial_unit_names and self.plugin is not None:
            return

        for record in str_records:
            result = self.current_spatial_unit(record.__dict__)
            if result is not None:
                spatial_unit, spatial_unit_id = result
            else:
                continue
            self.str_models[record.id] = record
            str_root = self.add_str_node(parent, record.id)
            # add STR children
            self.column_widget_registry(record, self.social_tenure)

            for i, (col, row) in enumerate(self._formatted_record.items()):
                str_child = QStandardItem(
                    '{}: {}'.format(col, row)
                )
                str_child.setSelectable(False)
                try:
                    str_root.appendRow([str_child])
                except RuntimeError:
                    pass
                record_dict = record.__dict__
                #party, party_id = self.current_party(record_dict)
                results = self.current_party(record_dict)
                if results is None:
                    return
                party, party_id = results
                party_model = None

                if party is not None:
                    party_model = getattr(record, party.name)

                if i == len(self._formatted_record) - 1:
                    custom_attr_entity = self.social_tenure.spu_custom_attribute_entity(
                        spatial_unit
                    )

                    if custom_attr_entity is not None and len(custom_attr_entity.columns) > 2:
                        try:
                            custom_attr_model = entity_attr_to_model(
                                custom_attr_entity,
                                'social_tenure_relationship_id', record_dict['id']
                            )
                        except DummyException:
                            custom_attr_model = None

                        if custom_attr_model is not None:
                            custom_attr_root = self.add_custom_attr_child(
                                str_root, custom_attr_entity, custom_attr_model
                            )

                    if not party_query:
                        if party_model is not None:
                            party_root = self.add_party_child(
                                str_root, party, party_model
                            )

                            self.party_items[party_model.id] = party
                    else:

                        record_dict = record.__dict__
                        spatial_unit, spatial_unit_id = self.current_spatial_unit(
                            record_dict
                        )
                        spatial_unit_model = getattr(record, spatial_unit.name)
                        spu_root = self.add_spatial_unit_child(
                            str_root, spatial_unit, spatial_unit_model
                        )
                        self.spatial_unit_items[spu_root.data()] = spatial_unit

        self.feature_str_model[feature_id] = list(self.str_models.keys())

    def add_party_node(self, parent, party_entity, party_id):
        """
        Add party steam with table icon and entity short name.
        :param parent: The parent of the party steam - STR steam.
        :type parent: QStandardItem
        :param party_entity: The party entity object.
        :type party_entity: Object
        :param party_id: The id of the party entity
        :type party_id: Integer
        :return: The party root item
        :rtype: QStandardItem
        """
        party_icon = GuiUtils.get_icon(
            'table.png'
        )
        title = format_name(party_entity.short_name)
        party_root = QStandardItem(party_icon, str(title))
        party_root.setData(party_id)
        self.set_bold(party_root)

        parent.appendRow([party_root])
        party_root.setEditable(False)
        return party_root

    def add_spatial_unit_node(self, parent, spatial_unit_entity, spatial_unit_id):
        """
        Add party steam with table icon and entity short name.
        :param parent: The parent of the party steam - STR steam.
        :type parent: QStandardItem
        :param party_entity: The party entity object.
        :type party_entity: Object
        :param party_id: The id of the party entity
        :type party_id: Integer
        :return: The party root item
        :rtype: QStandardItem
        """
        layer_icon = GuiUtils.get_icon('layer.gif')
        title = format_name(spatial_unit_entity.short_name)
        party_root = QStandardItem(layer_icon, str(title))
        party_root.setData(spatial_unit_id)
        self.set_bold(party_root)

        parent.appendRow([party_root])
        party_root.setEditable(False)
        return party_root

    def add_party_child(self, parent, party_entity, party_model):
        """
        Add party children to the treeview.
        :param parent: The parent of the tree child
        :type parent: QStandardItem
        :param party_entity: The current party entity object
        :type party_entity: Object
        :param party_model: The model of the party record
        :type party_model: SQLAlchemy Model
        :return: The party root item
        :rtype: QStandardItem
        """
        party_id = party_model.id
        self.party_models[party_id] = party_model
        party_root = self.add_party_node(
            parent, party_entity, party_id
        )
        # add STR children
        self.column_widget_registry(party_model, party_entity)
        for col, row in self._formatted_record.items():
            party_child = QStandardItem('{}: {}'.format(col, row))
            party_child.setSelectable(False)
            party_root.appendRow([party_child])
        return party_root

    def add_spatial_unit_child(self, parent, spatial_entity, spatial_unit_model):
        """
        Add party children to the treeview.
        :param parent: The parent of the tree child
        :type parent: QStandardItem
        :param party_entity: The current party entity object
        :type party_entity: Object
        :param party_model: The model of the party record
        :type party_model: SQLAlchemy Model
        :return: The party root item
        :rtype: QStandardItem
        """
        spatial_unit_id = spatial_unit_model.id
        # self.column_widget_registry(spatial_unit_model, spatial_entity)
        # self.party_models[spatial_unit_id] = spatial_unit_model
        party_root = self.add_spatial_unit_node(
            parent, spatial_entity, spatial_unit_id
        )
        # add STR children
        self.column_widget_registry(spatial_unit_model, spatial_entity)
        for col, row in self._formatted_record.items():
            party_child = QStandardItem('{}: {}'.format(col, row))
            party_child.setSelectable(False)
            party_root.appendRow([party_child])
        return party_root

    def add_custom_attr_node(self, parent):
        """
        Add party steam with table icon and entity short name.
        :param parent: The parent of the party steam - STR steam.
        :type parent: QStandardItem
        :param party_entity: The party entity object.
        :type party_entity: Object
        :param party_id: The id of the party entity
        :type party_id: Integer
        :return: The party root item
        :rtype: QStandardItem
        """
        custom_attr_icon = GuiUtils.get_icon('custom_tenure.png')

        title = QApplication.translate('DetailsTreeView',
                                       'Custom Tenure Information')
        custom_attr_root = QStandardItem(custom_attr_icon, str(title))
        # party_root.setData(party_id)
        self.set_bold(custom_attr_root)

        parent.appendRow([custom_attr_root])
        custom_attr_root.setEditable(False)
        return custom_attr_root

    def add_custom_attr_child(self, parent, custom_attr_entity,
                              custom_attr_model):
        """
        Add party children to the treeview.
        :param parent: The parent of the tree child
        :type parent: QStandardItem
        :param party_entity: The current party entity object
        :type party_entity: Object
        :param party_model: The model of the party record
        :type party_model: SQLAlchemy Model
        :return: The party root item
        :rtype: QStandardItem
        """
        custom_attr_id = custom_attr_model.id
        # self.party_models[party_id] = party_model
        custom_attr_root = self.add_custom_attr_node(parent)

        # add STR children
        self.column_widget_registry(custom_attr_model, custom_attr_entity)
        for col, row in self._formatted_record.items():
            custom_attr_child = QStandardItem('{}: {}'.format(col, row))
            custom_attr_child.setSelectable(False)
            custom_attr_root.appendRow([custom_attr_child])
        return custom_attr_root

    @staticmethod
    def set_bold(standard_item):
        """
        Make a text of QStandardItem to bold.
        :param standard_item: QStandardItem
        :type standard_item: QStandardItem
        """
        font = standard_item.font()
        font.setBold(True)
        standard_item.setFont(font)

    def treeview_error(self, not_feature_ft_msg, icon=None):
        """
        Displays error message in feature details treeview.
        :param title: the title of the treeview.
        :type: String
        :param message: The message to be displayed.
        :type: String
        :param icon: The icon of the item.

        """
        if icon is None:
            root = QStandardItem(not_feature_ft_msg)
        else:
            root = QStandardItem(icon, not_feature_ft_msg)

        self.view.setRootIsDecorated(False)
        self.model.appendRow(root)
        self.view.setRootIsDecorated(True)

    def expand_node(self, parent):
        """
        Make the last tree node expand.
        :param parent: The parent to expand
        :type QStandardItem
        :return:None
        """
        try:
            index = self.model.indexFromItem(parent)
            self.view.expand(index)
        except RuntimeError:
            pass

    def multi_select_highlight(self, index):
        """
        Highlights a feature with rubberBald class when selecting
        features are more than one.
        :param index: Selected QTreeView item index
        :type index: Integer
        """
        # Get the selected item text using the index
        selected_item = self.model.itemFromIndex(index)

        if selected_item is None or self.layer is None:
            return

        # Use multi-select only when more than 1 items are selected.
        if self.layer.selectedFeatureCount() < 2:
            return

        # If the first word is feature, expand & highlight.
        try:
            name = format_name(self.entity.short_name)
        except AttributeError:
            # escape attribute error on child items such as party
            return

        self.selected_root = selected_item

        # check parent nodes until we find the parent corresponding to the entity
        while selected_item is not None and selected_item.text() != name:
            selected_item = selected_item.parent()

        if selected_item is None:
            return

        selected_value = selected_item.data()

        self.view.expand(index)  # expand the item
        # Clear any existing highlight
        self.clear_sel_highlight()
        # Insert highlight

        # Create expression to target the selected feature
        # Get feature iteration based on the expression
        feature = next(self.layer.getFeatures(
            QgsFeatureRequest().setFilterExpression(
                QgsExpression.createFieldEqualityExpression('id', selected_value.id()))
        ))

        # Fetch geometry
        geom = feature.geometry()
        self.sel_highlight = QgsHighlight(iface.mapCanvas(), geom, self.layer)
        self.sel_highlight.setFillColor(selection_color())
        self.sel_highlight.setWidth(4)
        self.sel_highlight.setColor(QColor(212, 95, 0, 255))
        self.sel_highlight.show()

    def node_signals(self, entity):
        """
        Connects buttons to the nodes in the treeview.
        :param entity: The entity to be edited or its document viewed.
        :type entity: Object
        """

    def node_data(self, mode, results):
        """
        Gets tree item data to be used for editing and deleting a record.
        :param mode: The mode - edit or delete
        :type mode: String
        :param results: List of records/features selected.
        :type results: List
        :return: The item data (the id), and the item - QStandardItem
        :rtype: Tuple
        """

        item = None
        index = self.view.selectedIndexes()[0]
        item = self.model.itemFromIndex(index)
        result = item.data()
        return result, item

        # One item is selected and number of feature is also 1
        if len(results) == 1 and len(self.view.selectedIndexes()) == 1:
            index = self.view.selectedIndexes()[0]
            item = self.model.itemFromIndex(index)
            result = item.data()

        # One item is selected on the map but not on the treeview
        elif len(results) == 1 and len(self.view.selectedIndexes()) == 0:
            item = self.model.item(0, 0)
            result = item.data()

        # multiple features are selected but one treeview item is selected
        elif len(results) > 1 and len(self.view.selectedIndexes()) == 1:
            item = self.selected_root
            result = self.selected_root.data()
        # multiple features are selected but no treeview item is selected
        elif len(results) > 1 and len(self.view.selectedIndexes()) == 0:
            result = 'Please, select an item to {}.'.format(mode)
        else:
            result = 'Please, select at least one feature to {}.'.format(mode)

        if result is None:
            if item is None:
                item = self.model.item(0, 0)
                result = item.data()
            else:
                result = item.parent().data()

        return result, item

    def edit_selected_node(self):
        """
        Edits the record based on the selected item in the tree view.
        """
        if not self.view.selectedIndexes():
            return

        # data, item = self.node_data('edit', self._selected_features)
        index = self.view.selectedIndexes()[0]
        item = self.model.itemFromIndex(index)
        data = item.data()

        feature_edit = True

        if data is None:
            return

        if isinstance(data, str):
            data_error = QApplication.translate(
                'DetailsTreeView', data
            )
            QMessageBox.warning(
                iface.mainWindow(),
                QApplication.translate(
                    'DetailsTreeView', 'Edit Error'
                ),
                data_error
            )
            return

        # STR steam - edit social tenure relationship
        if item.text() == self.str_text:
            str_model_doc = []

            str_model_rec = self.str_models[data].__dict__

            for i in range(item.parent().rowCount()):
                child_ = item.parent().child(i)
                try:
                    model_ = self.str_models[child_.data()]
                    child_model_rec = model_.__dict__

                    # str_model_rec = self.str_models[item.data()].__dict__

                    spatial_unit_id = self.current_spatial_unit(child_model_rec)[1]

                    if child_model_rec[spatial_unit_id] == str_model_rec[spatial_unit_id]:
                        documents = self._supporting_doc_models(self.social_tenure.name, model_)
                        str_model_doc.append((model_, documents))
                except KeyError:
                    continue

            feature_edit = False
            edit_str = EditSTREditor(str_model_doc)
            edit_str.exec_()

        # party steam - edit party
        elif item.data() in self.party_items:

            entity = self.party_items[item.data()]

            model = self.feature_model(self.party_items[item.data()], data)
            editor = EntityEditorDialog(
                entity, model, iface.mainWindow()
            )
            editor.exec_()
        # Edit spatial entity
        elif item.data() in self.spatial_unit_items.keys():
            entity = self.spatial_unit_items[item.data()]

            model = self.feature_model(entity, data)

            editor = EntityEditorDialog(
                entity, model, iface.mainWindow()
            )
            editor.exec_()
        else:
            return
        self.view.expand(item.index())
        if feature_edit:
            self.update_edited_node(self.social_tenure, data)
        else:
            self.update_edited_node(self.social_tenure, data)

    def delete_selected_item(self):
        """
        Deletes a selected item.

        """
        str_edit = False
        id, item = self.node_data('delete', self._selected_features)

        if isinstance(id, str):
            data_error = QApplication.translate(
                'DetailsTreeView', id
            )
            QMessageBox.warning(
                iface.mainWindow(),
                QApplication.translate('DetailsTreeView', 'Delete Error'),
                data_error
            )
            return

        if item.text() == self.str_text:
            str_edit = True
            if id in self.str_models.keys():
                db_model = self.str_models[id]

        # if self.plugin is not None:
        elif item.text() == format_name(self.entity.short_name) and \
                id not in self.feature_str_model.keys():
            db_model = self.feature_model(self._entity, id)

        # if spatial unit is linked to STR, don't allow delete
        elif item.text() == format_name(self.entity.short_name) and \
                id in self.feature_str_model.keys():

            delete_warning = QApplication.translate(
                'DetailsTreeView',
                'You have to first delete the social tenure \n'
                'relationship to delete the {} record.'.format(
                    item.text()
                )
            )
            QMessageBox.warning(
                iface.mainWindow(),
                QApplication.translate('DetailsTreeView', 'Delete Error'),
                delete_warning
            )
            return
        else:
            return
        if str_edit:
            del_msg = QApplication.translate(
                'DetailsTreeView',
                "This action will remove the social tenure relationship "
                "and dependent supporting documents from the database and "
                "the documents folder. This action cannot be undone and "
                "once removed, it can only be recreated through"
                " the 'New Social Tenure Relationship' wizard."
                "Would you like to proceed?"
                "\nClick Yes to proceed or No to cancel."
            )
            delete_question = QMessageBox.critical(
                iface.mainWindow(),
                QApplication.translate(
                    'DetailsTreeView',
                    'Delete Social Tenure Relationship'
                ),
                del_msg,
                QMessageBox.Yes | QMessageBox.No
            )

        else:
            delete_warning = QApplication.translate(
                'DetailsTreeView',
                'Are you sure you want to delete '
                'the selected record(s)?\n'
                'This action cannot be undone.'
            )

            delete_question = QMessageBox.warning(
                iface.mainWindow(),
                QApplication.translate('DetailsTreeView', 'Delete Warning'),
                delete_warning,
                QMessageBox.Yes | QMessageBox.No
            )
        if delete_question == QMessageBox.Yes:
            db_model.delete()

            if str_edit:
                if id in self.str_models.keys():
                    del self.str_models[id]
                if id in self.feature_str_model.keys():
                    del self.feature_str_model[id]
            else:
                self.removed_feature = id
                if isinstance(id, QgsFeature):
                    id = id.id()

                del self.feature_models[id]

            remaining_str = len(self.str_models)

            self.updated_removed_node(str_edit, item, remaining_str)
            return
        else:
            return

    def update_edited_node(self, entity, feature_id):
        """
        Updates the treeview show the changes in the data.
        :param entity: The entity of the steam edited
        :type entity: Object
        :param feature_id: The feature id
        :type feature_id: Integer
        """
        # remove rows before adding the updated ones.
        if self.plugin is not None and self.layer is not None:
            self.layer.selectByIds(
                list(self.feature_models.keys())
            )
        root = self.find_root(entity, feature_id)
        if root is None:
            return
        self.view.selectionModel().select(
            root.index(), self.view.selectionModel().Select
        )
        self.expand_node(root)
        self.multi_select_highlight(root.index())

    def find_root(self, entity, feature_id):
        """
        Finds the root item - the spatial entity item using the entity and
        the feature id.
        :param entity: The entity of the root - spatial entity
        :type entity: Object
        :param feature_id: The feature id
        :type feature_id: Integer
        :return: The root item
        :rtype: QStandardItem
        """
        all_roots = self.model.findItems(
            format_name(entity.short_name)
        )
        root = None
        for item in all_roots:
            if item.data() == feature_id:
                root = item
                break
        return root

    def updated_removed_node(self, str_edit, item, remaining_str=0):
        """
        Updates a removed node on the treeview by showing No STR defined.
        :param str_edit: A boolean showing if the delete is on STR steam or
        the spatial root.
        :type str_edit: Boolean
        :param item: The root item to be removed
        :type item: QStandardItem
        :param remaining_str: Remaining STR nodes after the delete
        :type remaining_str: Integer
        """
        if not str_edit:
            if len(self.feature_models) > 1:
                self.refresh_layers()
            feature_ids = list(self.feature_models.keys())
            self.layer.selectByIds(
                feature_ids
            )
        else:
            item.removeRows(0, 5)  # <------------------------ What is the 5 magic number?
            # No other STR record remains for the spatial unit,
            # show No STR Defined
            if remaining_str == 0:
                item.setText('No STR Defined')
                no_str_icon = GuiUtils.get_icon(
                    'remove.png'
                )
                item.setIcon(no_str_icon)
            else:
                row = item.row()
                item.parent().removeRow(row)

    def view_node_document(self):
        """
        A slot raised when view document button is clicked. It opens document
        viewer and shows a document if a supporting document exists for the
        record.
        :type entity: Object

        """
        entity = self.entity
        if entity is None:
            return

        id, item = self.node_data('edit', self._selected_features)
        if isinstance(id, QgsFeature):
            id = id.id()
        if id is None:
            return
        if isinstance(id, str):
            data_error = QApplication.translate('DetailsTreeView', id)
            QMessageBox.warning(
                iface.mainWindow(),
                QApplication.translate('DetailsTreeView', 'Edit Error'),
                data_error
            )
            return

        if item.text() == self.str_text:
            db_model = self.str_models[id]
        elif item.data() in self.party_items:
            db_model = self.feature_model(self.party_items[item.data()], id)
        else:
            db_model = self.feature_model(entity, id)

        if db_model is not None:
            if not hasattr(db_model, 'documents'):
                docs = []
            else:
                docs = db_model.documents
            # Notify there are no documents for the selected doc
            if len(docs) == 0:
                msg = QApplication.translate(
                    'EntityBrowser',
                    'There are no supporting documents '
                    'for the selected record.'
                )

                QMessageBox.warning(
                    iface.mainWindow(),
                    self.doc_viewer_title,
                    msg
                )
            else:
                self.doc_viewer.load(docs)
