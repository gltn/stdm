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

import re
from collections import OrderedDict

from PyQt4.QtCore import QDate
from PyQt4.QtCore import QDateTime
from PyQt4.QtGui import (
    QDockWidget,
    QMessageBox,
    QTreeView,
    QStandardItem,
    QAbstractItemView,
    QStandardItemModel,
    QIcon,
    QApplication,
    QColor
)
from PyQt4.QtCore import (
    Qt
)
from qgis.gui import (
    QgsHighlight
)
from qgis.core import (
    QgsFeatureRequest,
    QgsExpression,
    QgsMapLayer
)

from stdm.settings import current_profile
from stdm.data.database import (
    STDMDb
)
from stdm.settings.registryconfig import (
    selection_color
)

from stdm.data.configuration import (
    entity_model
)
from stdm.data.pg_utils import (
    spatial_tables
)

from stdm.data.supporting_documents import (
    supporting_doc_tables,
    document_models
)
from stdm.ui.forms.editor_dialog import EntityEditorDialog

from stdm.ui.forms.widgets import ColumnWidgetRegistry
from stdm.utils.util import (
    format_name,
    entity_id_to_model,
    profile_spatial_tables

)

from stdm.ui.social_tenure.str_tree_view import EditSTRTreeView
from ui_feature_details import Ui_DetailsDock

class LayerSelectionHandler:
    def __init__(self, iface, plugin):
        self.layer = None
        self.iface = iface
        self._plugin = plugin
        self.sel_highlight = None

    def selected_features(self):
        """
        Returns a selected feature spatial unit
        id and code as key and value.
        :return: Dictionary
        """
        if self.stdm_layer(self.layer):
           # try:

            selected_features = self.layer.selectedFeatures()
            features = []
            field_names = [field.name() for field in self.layer.pendingFields()]
            for feature in selected_features:
                if 'id' in field_names:
                    features.append(feature['id'])
            return features
        else:

            return None

    def non_stdm_layer_error(self):
        not_feature_msg = QApplication.translate(
            'FeatureDetails',
            'You have selected a non-STDM layer. \n'
            'Please select an STDM layer to view \n'
            'the details.'
        )

        QMessageBox.warning(
            self.iface.mainWindow(),
            QApplication.translate('DetailsTreeView', 'Invalid Layer Error'),
            not_feature_msg
        )

    def get_layer_source(self, layer):
        """
        Get the layer table name if the source is from the database.
        :param layer: The layer for which the source is checked
        :type QGIS vectorlayer
        :return: String or None
        """
        if layer is None:
            return None
        source = layer.source()
        if source is None:
            return
        vals = dict(re.findall('(\S+)="?(.*?)"? ', source))
        try:
            table = vals['table'].split('.')
            tableName = table[1].strip('"')
            return tableName
        except KeyError:
            return None

    def active_layer_check(self):
        """
        Check if there is active layer and if not, displays
        a message box to select a feature layer.
        :return:
        """
        active_layer = self.iface.activeLayer()
        if active_layer is None:
            no_layer_msg = QApplication.translate(
                'LayerSelectionHandler',
                'Please select a spatial entity '
                'layer to view feature details.'
            )
            QMessageBox.critical(
                self.iface.mainWindow(),
                QApplication.translate('DetailsTreeView', 'Feature Details Error'),
                no_layer_msg
            )

    def stdm_layer(self, active_layer):
        """
        Check whether the layer is feature layer or not.
        :param active_layer: The layer to be checked
        :type QGIS vectorlayer
        :return: Boolean
        """
        layer_source = self.get_layer_source(active_layer)
        
        if layer_source is not None:
            return True
        else:
            return False


    def clear_feature_selection(self):
        """
        Clears selection of layer(s)
        :return: None
        """
        map = self.iface.mapCanvas()
        for layer in map.layers():
            if layer.type() == layer.VectorLayer:
                layer.removeSelection()
        map.refresh()

    def activate_select_tool(self):
        """
        Enables the select tool to be used to select features.
        :return:None
        """
        self.iface.actionSelect().trigger()
        layer_select_tool = self.iface.mapCanvas().mapTool()
        layer_select_tool.activate()

    def clear_sel_highlight(self):
        """
        Removes sel_highlight from the canvas.
        :return:
        """
        if self.sel_highlight is not None:
            self.sel_highlight = None


    def refresh_layers(self):
        """
        Refresh all database layers.
        :return: None
        :rtype: NoneType
        """
        layers = self.iface.legendInterface().layers()
        for layer in layers:
            layer.dataProvider().forceReload()
            layer.triggerRepaint()
        if not self.iface.activeLayer() is None:
            canvas = self.iface.mapCanvas()
            canvas.setExtent(
                self.iface.activeLayer().extent()
            )
            self.iface.mapCanvas().refresh()


    def multi_select_highlight(self, index):
        """
        Highlights a feature with rubberBald
        class when selecting
        features are more than one.
        :param index: Selected QTreeView item index
        :type Integer
        :return: None
        """
        pass

class DetailsDBHandler:
    def __init__(self):

        self._entity = None
        self.column_formatter = OrderedDict()
        self.formatted_columns = OrderedDict()
        self.current_profile = current_profile()
        self.formatted_record = OrderedDict()
        self.display_columns = None
        self._entity_supporting_doc_tables = {}

    def set_entity(self, entity):
        self._entity = entity

    def set_formatter(self, entity=None):
        self.format_columns(entity)

    def format_columns(self, entity=None):
        if entity is None:
            entity = self._entity
        if entity is None:
            return
        for col in entity.columns.values():
            col_name = col.name

            # Get widget factory so that we can use the value formatter
            widget_factory = ColumnWidgetRegistry.factory(
                col.TYPE_INFO
            )
            if not widget_factory is None:
                formatter = widget_factory(col)
                self.column_formatter[col_name] = formatter

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
                'ADMIN_SPATIAL_UNIT'
                #'MULTIPLE_SELECT'
            ]
            ]

    def feature_STR_link(self, feature_id):
        STR_model = entity_model(
            self.current_profile.social_tenure
        )
        model_obj = STR_model()
        result = model_obj.queryObject().filter(
            STR_model.spatial_unit_id == feature_id
        ).all()

        return result


    def column_widget_registry(self, model, entity):
        self.formatted_record.clear()
        self.display_column_object(entity)
        for col in self.display_columns:
            col_val = getattr(model, col.name)
            # Check if there are display formatters and apply if
            # one exists for the given attribute.
            if col.name in self.column_formatter:
                formatter = self.column_formatter[col.name]
                col_val = formatter.format_column_value(col_val)
            self.formatted_record[col.header()] = col_val


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
        #Only one document table per entity for now
        if entity_table in self._entity_supporting_doc_tables:
            doc_table_ref = self._entity_supporting_doc_tables[entity_table]
        else:
            doc_tables = supporting_doc_tables(entity_table)

            if len(doc_tables) > 0:
                doc_table_ref = doc_tables[0]
                self._entity_supporting_doc_tables[entity_table] = doc_table_ref

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

class DetailsDockWidget(QDockWidget, Ui_DetailsDock, LayerSelectionHandler):
    def __init__(self, iface, spatial_unit_dock):

        QDockWidget.__init__(self, iface.mainWindow())
        self.setupUi(self)
        self.plugin = spatial_unit_dock
        self.iface = iface
        self.edit_btn.setDisabled(True)
        self.delete_btn.setDisabled(True)
        self.view_document_btn.setDisabled(True)
        LayerSelectionHandler.__init__(self, iface, spatial_unit_dock)
        self.setBaseSize(300,5000)

    def init_dock(self):
        """
        creates dock on right dock widget area and set window title.
        :return: None
        """
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self)

        self.setWindowTitle(
            QApplication.translate(
                'DetailsDockWidget', 'Feature Details'
            )
        )


    def close_dock(self, tool):
        """
        Closes the dock by replacing select tool with pan tool,
        clearing feature selection, and hiding the dock.
        :param tool: Feature detail tool property
        :type QGIS tool
        :return: None
        """
        self.iface.actionPan().trigger()
        tool.setChecked(False)
        self.clear_feature_selection()
        self.clear_sel_highlight()
        self.hide()


    def closeEvent(self, event):
        """
        On close of the dock window, this event is executed
        to run close_dock method
        :param event: The close event
        :type QCloseEvent
        :return: None
        """
        self.close_dock(
            self.plugin.feature_details_act
        )

    def hideEvent(self, event):
        self.close_dock(
            self.plugin.feature_details_act
        )

class DetailsTreeView(DetailsDBHandler, DetailsDockWidget):
    def __init__(self, iface, plugin):

        """
        The method initializes the dockwidget.
        :param iface: QGIS user interface class
        :type class qgis.utils.iface
        :param plugin: The STDM plugin
        :type class
        :return: None
        """
        from stdm.ui.entity_browser import _EntityDocumentViewerHandler
        DetailsDockWidget.__init__(self, iface, plugin)

        DetailsDBHandler.__init__(self)

        self.plugin = plugin

        self.view = QTreeView()
        self.view.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )
        #self.feature_ids = []
        self.layer_table = None
        self.entity = None
        self.feature_models = {}
        self.party_models = {}
        self.STR_models = {}
        self.feature_STR_model = {}
        self.removed_feature = None
        self.selected_root = None
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
        self.view.setStyleSheet(
            '''
            QTreeView:!active {
                selection-background-color: #72a6d9;
            }
            '''
        )
        self.current_profile = current_profile()
        self.social_tenure = self.current_profile.social_tenure
        self.spatial_unit = self.social_tenure.spatial_unit
        self.party = self.social_tenure.party
        self.view.setMinimumWidth(250)
        self.doc_viewer_title = QApplication.translate(
            'DetailsTreeView',
            'Document Viewer'
        )
        self.doc_viewer = _EntityDocumentViewerHandler(
            self.doc_viewer_title, self.iface.mainWindow()
        )

    def set_layer_entity(self):
        self.layer_table = self.get_layer_source(
            self.iface.activeLayer()
        )
        if self.layer_table in spatial_tables():
            self.entity = self.current_profile.entity_by_name(
                self.layer_table
            )


    def activate_feature_details(self, button_clicked=True):
        """
        Action for showing feature details.
        :return:
        """

        # Get and set the active layer.
        self.layer = self.iface.activeLayer()
        # if no active layer, show error message
        # and uncheck the feature tool
        if self.layer is None:
            if button_clicked:
                self.active_layer_check()
            self.plugin.feature_details_act.setChecked(False)

            return
        # If the button is unchecked, close dock.
        if not self.plugin.feature_details_act.isChecked():
            self.close_dock(self.plugin.feature_details_act)
            self.feature_details = None
            return
        # if the selected layer is not an stdm layer,
        # show not feature layer.
        if not self.stdm_layer(self.layer):
            if button_clicked and self.isHidden():
                # show popup message if dock is hidden and button clicked
                self.non_stdm_layer_error()
                self.plugin.feature_details_act.setChecked(False)
            elif not button_clicked and not self.isHidden():
                # show tree message if dock is open and button clicked
                not_feature_msg = QApplication.translate(
                    'FeatureDetails',
                    'Please select an STDM layer to view \n'
                    'the details.'
                )
                self.model.clear()
                self.treeview_error(not_feature_msg)
        # If the selected layer is feature layer, get data and
        # display treeview in a dock widget
        else:
            self.prepare_for_selection()

    def prepare_for_selection(self):
        select_feature = 'Please select a feature ' \
                         'to view their details.'
        self.init_dock()
        self.add_tree_view()
        self.model.clear()
        self.treeview_error(select_feature)
        # enable the select tool
        self.activate_select_tool()
        self.update_tree_source(self.layer)

    def update_tree_source(self, active_layer):
        if active_layer.type() != QgsMapLayer.VectorLayer:
            return
        # set entity from active layer in the child class
        self.set_layer_entity()
        # set entity for the super class DetailModel
        self.set_entity(self.entity)
        # Registery column widget
        self.set_formatter()
        # set formatter for social tenure relationship.
        self.set_formatter(self.social_tenure)
        self.set_formatter(self.party)
        # pull data, show treeview
        active_layer.selectionChanged.connect(
            self.show_tree
        )
        self.steam_signals(self.entity)

    def add_tree_view(self):
        """
        Adds tree view to the dock widget and sets style.
        :return: None
        """
        self.tree_scrollArea.setWidget(self.view)

    def clear_feature_models(self):
        self.feature_models.clear()

    def reset_tree_view(self, no_feature=False):
        #clear feature_ids list, model and highlight
        self.model.clear()

        self.clear_sel_highlight() # remove sel_highlight
        self.disable_buttons(no_feature)
        if self.removed_feature is None:
            self.STR_models.clear()
            self.feature_models.clear()
        else:
            self.removed_feature = None
        features = self.selected_features()
        # if the selected feature is over 1,
        # activate multi_select_highlight
        if not features is None:
            self.view.clicked.connect(
                self.multi_select_highlight
            )
        if features is None:
            return
        # if there is at least one selected feature
        if len(features) > 0:
            self.add_tree_view()
            #self.feature_ids = features

    def disable_buttons(self, bool):
        self.edit_btn.setDisabled(bool)
        self.delete_btn.setDisabled(bool)
        self.view_document_btn.setDisabled(bool)

    def show_tree(self):
        if self.selected_features() is None:
            self.reset_tree_view()
            not_supported = 'Spatial Details is not ' \
                             'supported for this layer.'
            self.treeview_error(not_supported)
            return
        selected_features = self.selected_features()
        ### add non entity layer for views and shape files.
        if len(selected_features) < 1:
            self.reset_tree_view()
            self.disable_buttons(True)
            return
        layer_icon = QIcon(':/plugins/stdm/images/icons/layer.gif')

        if len(selected_features) < 1:
            self.disable_buttons(True)
            select_feature = 'You have not selected a feature.'
            self.treeview_error(select_feature)
            return
        if not self.entity is None:
            self.reset_tree_view()
            roots = self.add_parent_tree(
                layer_icon, format_name(self.entity.short_name)
            )

            for id, root in roots.iteritems():
                db_model = entity_id_to_model(self.entity, id)

                self.add_roots(db_model, root, id)
        else:
            self.reset_tree_view()
            self.disable_buttons(True)
            self.add_non_entity_parent(layer_icon)

    def add_non_entity_parent(self, layer_icon):
        # layer = self.iface.activeLayer()
        # if self.layer is None:
        #     return
        selected_features = self.layer.selectedFeatures()
        field_names = [field.name() for field in self.layer.pendingFields()]

        for elem in selected_features:
            parent = QStandardItem(
                layer_icon,
                format_name(self.layer.name())
            )
            feature_map = OrderedDict(
                zip(field_names, elem.attributes())
            )

            for k, v, in feature_map.iteritems():
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

    def add_parent_tree(self, icon, title):
        roots = OrderedDict()
        # if self.selected_features() is not None:
        for feature_id in self.selected_features():
            root = QStandardItem(icon, title)
            root.setData(feature_id)
            self.set_bold(root)
            self.model.appendRow(root)
            roots[feature_id] = root
        return roots

    def add_roots(self, model, parent, feature_id):
        self.feature_models[feature_id] = model
        if model is None:
            return
        self.column_widget_registry(model, self.entity)

        for i, (col, row) in enumerate(self.formatted_record.iteritems()):
            child = QStandardItem('{}: {}'.format(col, row))
            child.setSelectable(False)
            parent.appendRow([child])

            # Add Social Tenure Relationship steam as a last child
            if i == len(self.formatted_record)-1:
                self.add_STR_child(parent, feature_id)
        self.expand_node(parent)

    def add_STR_steam(self, parent, STR_id):
        str_icon = QIcon(
            ':/plugins/stdm/images/icons/social_tenure.png'
        )
        title = 'Social Tenure Relationship'
        str_root = QStandardItem(str_icon, title)
        str_root.setData(STR_id)
        self.set_bold(str_root)
        parent.appendRow([str_root])
        return str_root
    def add_no_STR_steam(self, parent):
        if self.entity.name == self.spatial_unit.name:
            no_str_icon = QIcon(
                ':/plugins/stdm/images/icons/remove.png'
            )
            title = 'No STR Defined'
            no_str_root = QStandardItem(no_str_icon, title)
            self.set_bold(no_str_root)
            parent.appendRow([no_str_root])

    def add_STR_child(self, parent, feature_id):
        if len(self.feature_STR_link(feature_id)) < 1:
            self.add_no_STR_steam(parent)
            return
        for record in self.feature_STR_link(feature_id):
            self.STR_models[record.id] = record
            str_root = self.add_STR_steam(parent, record.id)
            # add STR children
            self.column_widget_registry(record, self.social_tenure)
            for i, (col, row) in enumerate(
                    self.formatted_record.iteritems()
            ):
                STR_child = QStandardItem(
                    '{}: {}'.format(col, row)
                )
                STR_child.setSelectable(False)
                str_root.appendRow([STR_child])
                if i == len(self.formatted_record)-1:
                    self.add_party_child(
                        str_root, record.party_id
                    )
        self.feature_STR_model[feature_id] = self.STR_models.keys()

    def add_party_steam(self, parent, party_id):
        party_icon = QIcon(
            ':/plugins/stdm/images/icons/table.png'
        )
        title = format_name(self.party.short_name)
        party_root = QStandardItem(party_icon, title)
        party_root.setData(party_id)
        self.set_bold(party_root)

        parent.appendRow([party_root])
        party_root.setEditable(False)
        return party_root

    def add_party_child(self, parent, party_id):

        db_model = entity_id_to_model(self.party, party_id)
        self.party_models[party_id] = db_model
        party_root = self.add_party_steam(parent, party_id)
        # add STR children
        self.column_widget_registry(db_model, self.party)
        for col, row in self.formatted_record.iteritems():
            party_child = QStandardItem('{}: {}'.format(col, row))
            party_child.setSelectable(False)
            party_root.appendRow([party_child])

    def set_bold(self, standard_item):
        """
        Make a text of Qstandaritem to bold.
        :param standard_item: Qstandaritem
        :type: Qstandaritem
        :return: None
        """
        font = standard_item.font()
        font.setBold(True)
        standard_item.setFont(font)

    def treeview_error(self, message, icon=None):
        """
        Displays error message in feature details treeview.
        :param title: the title of the treeview.
        :type: String
        :param message: The message to be displayed.
        :type: String
        :param icon: The icon of the item.
        :type: Resource string
        :return: None
        """
        not_feature_ft_msg = QApplication.translate(
            'FeatureDetails', message
        )
        if icon== None:
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
        index = self.model.indexFromItem(parent)
        self.view.expand(index)


    def multi_select_highlight(self, index):
        """
        Highlights a feature with rubberBald class when selecting
        features are more than one.
        :param index: Selected QTreeView item index
        :type Integer
        :return: None
        """
        map = self.iface.mapCanvas()
        try:

            # Get the selected item text using the index
            selected_item = self.model.itemFromIndex(index)
            # Use mutli-select only when more than 1 items are selected.
            if self.layer.selectedFeatures() < 2:
                return
            self.selected_root = selected_item
            # Split the text to get the key and value.
            selected_item_text = selected_item.text()

            selected_value = selected_item.data()
            # If the first word is feature, expand & highlight.
            if selected_item_text == format_name(self.spatial_unit.short_name):
                self.view.expand(index)  # expand the item
                # Clear any existing highlight
                self.clear_sel_highlight()
                # Insert highlight
                # Create expression to target the selected feature
                expression = QgsExpression(
                    "\"id\"='" + str(selected_value) + "'"
                )
                # Get feature iteration based on the expression
                ft_iteration = self.layer.getFeatures(
                    QgsFeatureRequest(expression)
                )

                # Retrieve geometry and attributes
                for feature in ft_iteration:
                    # Fetch geometry
                    geom = feature.geometry()
                    self.sel_highlight = QgsHighlight(map, geom, self.layer)

                    self.sel_highlight.setFillColor(selection_color())
                    self.sel_highlight.setWidth(4)
                    self.sel_highlight.setColor(QColor(212,95,0, 255))
                    self.sel_highlight.show()
                    break
        except AttributeError:
            # pass attribute error on child items such as party
            pass
        except IndexError:
            pass

    def steam_signals(self, entity):
        self.edit_btn.clicked.connect(
            lambda : self.edit_selected_steam(
                entity
            )
        )
        self.delete_btn.clicked.connect(
            self.delete_selected_item
        )
        self.view_document_btn.clicked.connect(
            lambda : self.view_steam_document(
                entity
            )
        )

    def steam_data(self, mode):
        item = None
        # if self.view.currentIndex().text() == format_name(self.party):
        #     return None, None
        # One item is selected and number of feature is also 1
        if len(self.layer.selectedFeatures()) == 1 and \
                        len(self.view.selectedIndexes()) == 1:
            index = self.view.selectedIndexes()[0]
            item = self.model.itemFromIndex(index)
            result = item.data()

        # One item is selected on the map but not on the treeview
        elif len(self.layer.selectedFeatures()) == 1 and \
                        len(self.view.selectedIndexes()) == 0:
            item = self.model.item(0, 0)
            result = item.data()

        # multiple features are selected but one treeview item is selected
        elif len(self.layer.selectedFeatures()) > 1 and \
                        len(self.view.selectedIndexes()) == 1:
            item = self.selected_root
            result = self.selected_root.data()
        # multiple features are selected but no treeview item is selected
        elif len(self.layer.selectedFeatures()) > 1 and \
             len(self.view.selectedIndexes()) == 0:
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

    def edit_selected_steam(self, entity):
        id, item = self.steam_data('edit')

        feature_edit = True
        if id is None:
            return
        if isinstance(id, str):
            data_error = QApplication.translate('DetailsTreeView', id)
            QMessageBox.warning(
                self.iface.mainWindow(),
                QApplication.translate('DetailsTreeView', 'Edit Error'),
                data_error
            )
            return

        if item.text() == 'Social Tenure Relationship':
            model = self.STR_models[id]
            documents = self._supporting_doc_models(
                self.social_tenure.name, model
            )
            node_data = model, documents

            feature_edit = False
            edit_str = EditSTRTreeView(self._plugin, node_data)
            status = edit_str.exec_()
            print vars(edit_str.updated_str_obj)
            ##TODO add STR wizard edit mode here.
        elif item.text() == format_name(self.party.short_name):
            feature_edit = False

            model = self.party_models[id]
            editor = EntityEditorDialog(
                self.party, model, self.iface.mainWindow()
            )
            editor.exec_()
        else:
            model = self.feature_models[id]

            editor = EntityEditorDialog(
                entity, model, self.iface.mainWindow()
            )
            editor.exec_()
        #root = self.find_root(entity, id)
        self.view.expand(item.index())
        if feature_edit:
            self.update_edited_steam(entity, id)
        else:
            self.update_edited_steam(self.social_tenure, id)

    def delete_selected_item(self):
        str_edit = False
        id, item = self.steam_data('delete')

        if isinstance(id, str):
            data_error = QApplication.translate(
                'DetailsTreeView', id
            )
            QMessageBox.warning(
                self.iface.mainWindow(),
                QApplication.translate('DetailsTreeView', 'Delete Error'),
                data_error
            )
            return
        if item.text() == 'Social Tenure Relationship':
            str_edit = True
            db_model = self.STR_models[id]

        elif item.text() == format_name(self.spatial_unit.short_name) and \
            id not in self.feature_STR_model.keys():
            db_model = self.feature_models[id]

        # if spatial unit is linked to STR, don't allow delete
        elif item.text() == format_name(self.spatial_unit.short_name) and \
                        id in self.feature_STR_model.keys():


            delete_warning = QApplication.translate(
                'DetailsTreeView',
                'You have to first delete the social tenure \n'
                'relationship to delete the {} record.'.format(
                    item.text()
                )

            )
            QMessageBox.warning(
                self.iface.mainWindow(),
                QApplication.translate('DetailsTreeView', 'Delete Error'),
                delete_warning
            )
            return
        # If it is party node, STR exists and don't allow delete.
        elif item.text() == format_name(self.party.short_name):
            delete_warning = QApplication.translate(
                'DetailsTreeView',
                'You have to first delete the social tenure \n'
                'relationship to delete the {} record.'.format(
                    item.text()
                )
            )
            QMessageBox.warning(
                self.iface.mainWindow(),
                QApplication.translate('DetailsTreeView', 'Delete Error'),
                delete_warning
            )
            return
        else:
            return
        delete_warning = QApplication.translate(
            'DetailsTreeView',
            'Are you sure you want to delete '
            'the selected record(s)?\n'
            'This action cannot be undone.'
        )

        delete_question = QMessageBox.warning(
            self.iface.mainWindow(),
            QApplication.translate('DetailsTreeView', 'Delete Warning'),
            delete_warning,
            QMessageBox.Yes | QMessageBox.No
        )
        if delete_question == QMessageBox.Yes:
            db_model.delete()

            if str_edit:
                del self.STR_models[id]
            else:
                self.removed_feature = id
                del self.feature_models[id]

            self.updated_removed_steam(str_edit, item)
        else:
            return

    def update_edited_steam(self, entity, feature_id):

        # remove rows before adding the updated ones.
        self.layer.setSelectedFeatures(
            self.feature_models.keys()
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
        all_roots = self.model.findItems(
            format_name(entity.short_name)
        )
        root = None
        for item in all_roots:
            if item.data() == feature_id:
                root = item
                break
        return root

    def updated_removed_steam(self, STR_edit, item):
        if not STR_edit:
            if len(self.feature_models) > 1:
                self.refresh_layers()
            feature_ids = self.feature_models.keys()
            self.layer.setSelectedFeatures(
                feature_ids
            )
        else:
            item.removeRows(0, 2)
            item.setText('No STR Definded')
            no_str_icon = QIcon(
                ':/plugins/stdm/images/icons/remove.png'
            )
            item.setIcon(no_str_icon)

    def view_steam_document(self, entity):
        # Slot raised to show the document viewer for the selected entity

        id, item = self.steam_data('edit')

        if id is None:
            return
        if isinstance(id, str):
            data_error = QApplication.translate('DetailsTreeView', id)
            QMessageBox.warning(
                self.iface.mainWindow(),
                QApplication.translate('DetailsTreeView', 'Edit Error'),
                data_error
            )
            return
        if item.text() == 'Social Tenure Relationship':
            db_model = self.STR_models[id]
        else:
            db_model = self.feature_models[id]

        if not db_model is None:
            docs = db_model.documents
            # Notify there are no documents for the selected doc
            if len(docs) == 0:
                msg = QApplication.translate(
                    'EntityBrowser',
                    'There are no supporting documents '
                    'for the selected record.'
                )

                QMessageBox.warning(
                    self.iface.mainWindow(),
                    self.doc_viewer_title,
                    msg
                )
            else:
                self.doc_viewer.load(docs)
