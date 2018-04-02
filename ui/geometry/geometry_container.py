import inspect
from collections import OrderedDict

import re
from PyQt4.QtCore import Qt, pyqtSlot
from PyQt4.QtGui import QDockWidget, QApplication, QStatusBar, QWidget, \
    QMessageBox, QAction
from qgis.PyQt.QtCore import NULL, pyqtSignal, QObject
from qgis.core import QgsMapLayer, QgsFeatureRequest
from qgis.utils import iface

from stdm.data.pg_utils import spatial_tables, pg_views
# from stdm.ui.feature_details import LayerSelectionHandler

from stdm.ui.notification import NotificationBar
from ...geometry.geometry_utils import *
from stdm.data.configuration import entity_model
from stdm.settings import current_profile

from ui_geometry_container import Ui_GeometryContainer
from ui_move_line_area import Ui_MoveLineArea
from ui_offset_distance import Ui_OffsetDistance
from ui_one_point_area import Ui_OnePointArea
from ui_join_points import Ui_JoinPoints

GEOM_DOCK_ON = False
PREVIEW_POLYGON = 'Preview Polygon'
POLYGON_LINES = 'Polygon Lines'
LINE_POINTS = 'Line Points'
# TODO Line count is not showing on seond time load.
# TODO reset selected feature on toggle of geom combobox - Done partly
# TODO on selection of polygon, clear selection of line in the UI
class LayerSelectionHandler(object):
    """
     Handles all tasks related to the layer.
    """

    def __init__(self, iface, plugin):
        """
        Initializes the LayerSelectionHandler.
        :param iface: The QGIS Interface object
        :type iface: Object
        :param plugin: The STDM plugin object
        :type plugin: Object
        """
        self.layer = None
        self.iface = iface
        self.plugin = plugin
        self.sel_highlight = None
        self.current_profile = current_profile()

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
                for field in self.layer.pendingFields()]
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
                    self.iface.mainWindow(),
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
            self.iface.mainWindow(),
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
        :return: The table name or none if no table name found.
        :rtype: String or None
        """
        if layer is None:
            return None
        source = layer.source()
        if source is None:
            return None
        if re is None:
            return None
        vals = dict(re.findall('(\S+)="?(.*?)"? ', source))
        try:
            table = vals['table'].split('.')

            table_name = table[1].strip('"')
            if table_name in pg_views():
                return table_name

            entity_table = self.current_profile.entity_by_name(table_name)
            if entity_table is None:
                return None
            return table_name
        except KeyError:
            return None

    def active_layer_check(self):
        """
        Check if there is active layer and if not, displays
        a message box to select a feature layer.
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
        layer_source = self.get_layer_source(active_layer)

        if layer_source is not None:
            return True
        else:
            return False

    def clear_feature_selection(self):
        """
        Clears selection of layer(s).
        """
        map = self.iface.mapCanvas()
        for layer in map.layers():
            if layer.type() == layer.VectorLayer:
                layer.removeSelection()
        map.refresh()

    def activate_select_tool(self):
        """
        Enables the select tool to be used to select features.
        """
        self.iface.actionSelect().trigger()
        layer_select_tool = self.iface.mapCanvas().mapTool()
        layer_select_tool.deactivated.connect(self.disable_feature_details_btn)

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
        if self.sel_highlight is not None:
            self.sel_highlight = None

    def refresh_layers(self):
        """
        Refresh all database layers.
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
        :type index: Integer
        """
        pass


class GeometryToolsContainer(
    QDockWidget, Ui_GeometryContainer, LayerSelectionHandler
):
    """
    The logic for the spatial entity details dock widget.
    """
    # panel_loaded = pyqtSignal()

    def __init__(self, iface, plugin):
        """
        Initializes the DetailsDockWidget.
        :param iface: The QGIS interface
        :type iface: Object
        :param plugin: The STDM plugin object
        :type plugin: Object
        """
        QDockWidget.__init__(self, iface.mainWindow())
        self.setupUi(self)
        self.plugin = plugin
        self.iface = iface
        self._entity = None
        LayerSelectionHandler.__init__(self, iface, plugin)
        self.setBaseSize(300, 5000)
        self.layer = None
        self.line_layer = None
        # self.current_widget = None

    def init_dock(self):
        """
        Creates dock on right dock widget area and set window title.
        """

        self.iface.addDockWidget(Qt.RightDockWidgetArea, self)

        self.init_signals()


    def add_widgets(self):

        for i, factory in enumerate(GeometryWidgetRegistry.registered_factories.values()):
            widget = factory.create(self, self.geom_tools_widgets.widget(i))
            self.geom_tools_widgets.addWidget(widget)

            self.geom_tools_combo.addItem(factory.NAME, factory.OBJECT_NAME)

            widget.init_signals()
            # if i == 0:
            #     self.current_widget = widget


    def init_signals(self):
        self.geom_tools_combo.currentIndexChanged.connect(
            self.on_geom_tools_combo_changed
        )

    def on_geom_tools_combo_changed(self, index):
        self.geom_tools_widgets.setCurrentIndex(index)
        current_widget = self.geom_tools_widgets.widget(index)

        current_widget.set_widget(current_widget)
        current_widget.init_signals()
        current_widget.clear_inputs()

    def close_dock(self, tool):
        """
        Closes the dock by replacing select tool with pan tool,
        clearing feature selection, and hiding the dock.
        :param tool: Feature detail tool button
        :type tool: QAction
        """
        global GEOM_DOCK_ON
        self.iface.actionPan().trigger()
        tool.setChecked(False)
        self.clear_feature_selection()
        self.clear_sel_highlight()
        self.hide()
        GEOM_DOCK_ON = False

    def closeEvent(self, event):
        """
        On close of the dock window, this event is executed
        to run close_dock method
        :param event: The close event
        :type event: QCloseEvent
        :return: None
        """
        if self.plugin is None:
            return
        self.close_dock(
            self.plugin.geom_tools_cont_act
        )

    def hideEvent(self, event):
        """
        Listens to the hide event of the dock and properly close the dock
        using the close_dock method.
        :param event: The close event
        :type event: QCloseEvent
        """
        self.close_dock(
            self.plugin.geom_tools_cont_act
        )


    def activate_geometry_tools(self, button_clicked=True):
        """
        A slot raised when the feature details button is clicked.
        :param button_clicked: A boolean to identify if it is activated
        because of button click or because of change in the active layer.
        :type button_clicked: Boolean
        """
        # No need of activation as it is activated.
        # print 'hidden ', self.isHidden()
        if not self.isHidden():
            self.activate_select_tool()
            self.plugin.geom_tools_cont_act.setChecked(True)
            return
        # Get and set the active layer.

        self.layer = self.iface.activeLayer()

        if self.layer is not None:
            # if it is Polygon Lines layer that is selected, keep dock
            if self.stdm_layer(self.layer):
                self.layer = self.iface.activeLayer()
                self.line_layer = None
            if self.layer.name() == POLYGON_LINES:
                self.activate_select_tool()
                self.plugin.geom_tools_cont_act.setChecked(True)
                self.line_layer = self.layer
                return True
        # if no active layer, show error message
        # and uncheck the feature tool
        # print self.layer.name()
        if self.layer is None:
            if button_clicked:
                self.active_layer_check()
            self.plugin.geom_tools_cont_act.setChecked(False)
            return False
        # If the button is unchecked, close dock.
        if not self.plugin.geom_tools_cont_act.isChecked():
            self.close_dock(self.plugin.geom_tools_cont_act)
            self.geometry_tools = None
            return False
        # if the selected layer is not an STDM layer,
        # show not feature layer.
        if not self.stdm_layer(self.layer):
            if button_clicked and self.isHidden():
                # show popup message if dock is hidden and button clicked
                self.non_stdm_layer_error()
                self.plugin.geom_tools_cont_act.setChecked(False)
            return False
        # If the selected layer is feature layer, get data and
        # display geometry_tools in a dock widget
        # else:
        self.prepare_for_selection()
        return True
            # self.panel_loaded.emit()



    def prepare_for_selection(self):
        """
        Prepares the dock widget for data loading.
        """
        self.init_dock()

        self.activate_select_tool()
        self.update_layer_source(self.layer)


    def activate_select_tool(self):
        """
        Enables the select tool to be used to select features.
        """
        self.iface.actionSelect().trigger()
        layer_select_tool = self.iface.mapCanvas().mapTool()
        layer_select_tool.deactivated.connect(
            self.disable_feature_details_btn
        )

        layer_select_tool.activate()


    def disable_feature_details_btn(self):
        """
        Disables features details button.
        :return:
        :rtype:
        """
        self.plugin.geom_tools_cont_act.setChecked(False)


    def update_layer_source(self, active_layer):
        """
        Updates the layer source in case of layer change.
        :param active_layer: The active layer on the canvas.
        :type active_layer: QgsVectorLayer
        """
        if active_layer.type() != QgsMapLayer.VectorLayer:
            return
        # set entity from active layer in the child class
        self.set_layer_entity()
        # set entity for the super class DetailModel
        self.set_entity(self.entity)


    def feature_model(self, entity, id):
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
        result = model_obj.queryObject().filter(model.id == id).all()
        if len(result) > 0:
            return result[0]
        else:
            return None

    def set_layer_entity(self):
        """
        Sets the entity property using the layer table.
        """
        self.layer_table = self.get_layer_source(
            self.iface.activeLayer()
        )
        if self.layer_table is None:
            return

        if self.layer_table in spatial_tables() and \
                        self.layer_table not in pg_views():
            self.entity = self.current_profile.entity_by_name(
                self.layer_table
            )

    def set_entity(self, entity):
        """
        Sets the spatial entity.
        :param entity: The entity object
        :type entity: Object
        """
        self._entity = entity


class GeomWidgetsBase(object):


    def __init__(self, layer_settings, widget):
        # QObject.__init__(self, widget)
        global GEOM_DOCK_ON
        GEOM_DOCK_ON = True
        # print 'Geom widget activated 1'
        self.settings = layer_settings
        self.current_profile = current_profile()
        self.iface = iface

        self.settings = layer_settings
        self.widget = widget
        self.feature_count = 0
        self.features = []
        self.lines_count = 0
        self.points_count = 0
        self.lines = []
        self.points = []
        self.line_layer = None
        self.point_layer = None
        self.notice = NotificationBar(
            self.settings.notice_box
        )
        self.feature_ids = []
        self.executed = False
        self.preview_layer = None

        self.widget.preview_btn.clicked.connect(self.preview)
        self.widget.save_btn.clicked.connect(self.save)
        self.settings_layer_connected = False
        # self.line_layer_connected = False

    def init_signals(self):
        if not self.settings_layer_connected:
            # print 'Geom widget signal activated 1'
            self.settings.layer.selectionChanged.connect(
                self.on_feature_selected
            )
            self.settings_layer_connected = True

    def set_widget(self, widget):
        self.widget = widget

    def clear_inputs(self):
        if hasattr(self.widget, 'sel_features_lbl'):

            self.widget.sel_features_lbl.setText(str(0))

        if hasattr(self.widget, 'selected_line_lbl'):

            self.widget.selected_line_lbl.setText(str(0))

        if hasattr(self.widget, 'line_length_lbl'):

            self.widget.line_length_lbl.setText(str(0))

        if hasattr(self.widget, 'selected_points_lbl'):

            self.widget.selected_points_lbl.setText(str(0))


    def disconnect_signals(self):
        # print 'self.settings_layer_connected ', self.settings_layer_connected
        if self.settings_layer_connected:
            self.settings.layer.selectionChanged.disconnect(
                self.on_feature_selected
            )
            self.settings_layer_connected = False

    def on_feature_selection_finished(self):

        self.line_layer = polygon_to_lines(self.settings.layer, POLYGON_LINES)
        self.settings.line_layer = self.line_layer
        # print self.line_layer, self.line_layer_connected
        if self.line_layer is not None:

            self.line_layer.selectionChanged.connect(
                self.on_line_feature_selected
            )

            # self.line_layer_connected = True

    def hideEvent(self, event):
        self.widget_closed = True
        prev_layers = QgsMapLayerRegistry.instance().mapLayersByName(
            PREVIEW_POLYGON
        )
        if len(prev_layers) > 0:
            for prev_layer in prev_layers:
                QgsMapLayerRegistry.instance().removeMapLayer(prev_layer)
        line_layers = QgsMapLayerRegistry.instance().mapLayersByName(
            POLYGON_LINES
        )
        if len(line_layers) > 0:
            for line_layer in line_layers:
                QgsMapLayerRegistry.instance().removeMapLayer(line_layer)

        point_layers = QgsMapLayerRegistry.instance().mapLayersByName(
            LINE_POINTS
        )
        if len(point_layers) > 0:
            for point_layer in point_layers:
                QgsMapLayerRegistry.instance().removeMapLayer(point_layer)
        if self.settings.layer.isEditable():
            iface.mainWindow().findChild(QAction, 'mActionToggleEditing').trigger()

        self.disconnect_signals()

    def on_line_selection_finished(self):
        # self.preview()
        pass

    def on_feature_selected(self, feature):
        """
        Selects a feature and load line layer which is boundary of the polygon.
        :param feature: List of feature ids selected
        :type feature: List
        :return:
        :rtype:
        """
        if self.parent().currentWidget().objectName() != self.objectName():
            return

        self.set_widget(self.parent().currentWidget())

        if not GEOM_DOCK_ON:
            return

        if len(feature) == 0:
            return

        self.feature_ids = feature

        self.features = feature_id_to_feature(
            self.settings.layer, self.feature_ids
        )

        if self.settings.layer is None:
            return

        if iface.activeLayer().name() == POLYGON_LINES:
            return

        if self.settings.stdm_layer(self.settings.layer):
            if hasattr(self.widget, 'sel_features_lbl'):
                self.feature_count = self.selected_features_count()

                self.widget.sel_features_lbl.setText(str(self.feature_count))

                self.on_feature_selection_finished()

                # print inspect.stack()

    def on_line_feature_selected(self):
        # print self.settings.layer
        if self.settings.layer is None:
            return
        # print iface.activeLayer().name() , self.settings.layer
        if iface.activeLayer().name() != POLYGON_LINES:
            return
        # print self.line_layer.selectedFeatures()
        if len(self.line_layer.selectedFeatures()) == 0:
            return
        QApplication.processEvents()
        if hasattr(self.widget, 'selected_line_lbl'):
            self.lines[:] = []
            self.lines_count = self.selected_line_count()

            self.widget.selected_line_lbl.setText(str(self.lines_count))
            if self.lines_count > 1:
                message = QApplication.translate(
                    'GeomWidgetsBase',
                    'The first selected segment will be used.'
                )
                self.notice.insertWarningNotification(message)

            # self.line_selection_finished.emit()

    def selected_features_count(self):
        request = QgsFeatureRequest()
        feat_data = []

        for feat_id in self.feature_ids:
            request.setFilterFid(feat_id)
            features = self.settings.layer.getFeatures(request)
            for feature in features:
                self.features.append(feature)
                feat_data.append(feature.geometry().area())

        total_area = sum(feat_data)
        if hasattr(self.widget, 'split_polygon_area'):
            self.widget.split_polygon_area.setMaximum(total_area)

        if self.feature_ids is not None:
            return len(self.feature_ids)
        else:
            return 0

    def selected_line_count(self):
        if self.line_layer is None:
            return 0
        self.lines = self.line_layer.selectedFeatures()

        if self.lines is not None:
            return len(self.lines)
        else:
            return 0

    def selected_point_count(self):
        if self.point_layer is None:
            return 0

        points = self.point_layer.selectedFeatures()
        if len(self.lines) > 0:
            location = identify_selected_point_location(
                points[0], self.lines[0].geometry()
            )

            if location == 'middle':

                return 0
        # else:
        self.points = points

        if self.points is not None:
            return len(self.points)
        else:
            return 0

    def validate_save(self):
        if self.widget.split_polygon_area.value() == 0:
            message = QApplication.translate(
                'GeomWidgetsBase',
                'The area must be greater than 0.'
            )
            self.notice.insertErrorNotification(message)
            return False
        return True

    def save(self):
        pass


    def create_point_layer(self):
        prev_layers = QgsMapLayerRegistry.instance().mapLayersByName(
            LINE_POINTS
        )
        for prev_layer in prev_layers:
            clear_layer_features(prev_layer)

        if len(prev_layers) == 0:
            self.point_layer = create_temporary_layer(
                self.settings.layer, 'Point', LINE_POINTS, True
            )

    def create_preview_layer(self):
        prev_layers = QgsMapLayerRegistry.instance().mapLayersByName(
            PREVIEW_POLYGON
        )
        for prev_layer in prev_layers:
            clear_layer_features(prev_layer)

        if len(prev_layers) == 0:
            self.preview_layer = copy_layer_to_memory(
                self.settings.layer, PREVIEW_POLYGON, self.feature_ids, False
            )
        else:
            add_features_to_layer(self.preview_layer, self.features)
            # print 'feat count', self.preview_layer.featureCount()

        iface.legendInterface().setLayerVisible(self.preview_layer, False)

    def remove_preview_layers(self):
        preview_layers = QgsMapLayerRegistry.instance().mapLayersByName(
            PREVIEW_POLYGON
        )
        # prev_layer_ids = []
        for prev_layer in preview_layers:
            # prev_layer_ids.append(prev_layer.id())
            QgsMapLayerRegistry.instance().removeMapLayer(prev_layer)

    def preview(self):
        self.executed = True
        self.preview_layer = copy_layer_to_memory(
            self.settings.layer, PREVIEW_POLYGON, self.feature_ids, False)

        if len(self.lines) > 0:
            try:
                split_move_line_with_area(
                    self.preview_layer,
                    self.line_layer,
                    self.preview_layer,
                    self.lines[0],
                    self.widget.split_polygon_area.value()
                )
            except Exception as ex:
                self.notice.insertWarningNotification(ex)
            iface.mapCanvas().refresh()

    def cancel(self):
        pass


class MoveLineAreaWidget(QWidget, Ui_MoveLineArea, GeomWidgetsBase):

    def __init__(self, layer_settings, parent):
        QWidget.__init__(self)

        self.setupUi(self)
        GeomWidgetsBase.__init__(self, layer_settings, self)

    def validate_save(self):
        if self.widget.split_polygon_area.value() == 0:
            message = QApplication.translate(
                'GeomWidgetsBase',
                'The area must be greater than 0.'
            )
            self.notice.insertErrorNotification(message)
            return False
        return True

    def save(self):
        result = self.validate_save()
        if not result:
            return
        self.executed = True
        if self.settings_layer_connected:
            self.disconnect_signals()

        self.create_preview_layer()

        self.settings.layer.selectByIds(self.feature_ids)

        split_move_line_with_area(
            self.settings.layer,
            self.line_layer,
            self.preview_layer,
            self.lines[0],
            self.widget.split_polygon_area.value(),
            self.feature_ids
        )

        iface.setActiveLayer(self.settings.layer)
        self.init_signals()


class OffsetDistanceWidget(QWidget, Ui_OffsetDistance, GeomWidgetsBase):

    def __init__(self, layer_settings, parent):
        QWidget.__init__(self)

        self.setupUi(self)
        GeomWidgetsBase.__init__(self, layer_settings, self)
        self.offset_distance.valueChanged.connect(self.on_offset_distance_changed)
    def on_offset_distance_changed(self, new_value):
        if self.settings_layer_connected:
            self.disconnect_signals()

        self.create_preview_layer()

        result = split_offset_distance(
            self.settings.layer,
            self.line_layer,
            self.preview_layer,
            self.lines[0],
            new_value,
            self.feature_ids,
            validate=True
        )
        if not result:
            message = QApplication.translate(
                'OffsetDistanceWidget', 'The offset distance is too large.'
            )
            self.notice.insertErrorNotification(message)
        else:
            self.notice.clear()
        iface.setActiveLayer(self.settings.layer)
        self.init_signals()

    def validate_save(self):
        if self.widget.offset_distance.value() == 0:
            message = QApplication.translate(
                'GeomWidgetsBase',
                'The offset distance must be greater than 0.'
            )
            self.notice.insertErrorNotification(message)
            return False
        return True

    def save(self):
        result = self.validate_save()
        if not result:
            return
        self.executed = True
        if self.settings_layer_connected:
            self.disconnect_signals()

        self.create_preview_layer()

        self.settings.layer.selectByIds(self.feature_ids)
        result = split_offset_distance(
            self.settings.layer,
            self.line_layer,
            self.preview_layer,
            self.lines[0],
            self.widget.offset_distance.value(),
            self.feature_ids
        )
        if not result:
            message = QApplication.translate(
                'OffsetDistanceWidget', 'The offset distance is too large.'
            )
            self.notice.insertErrorNotification(message)
        iface.setActiveLayer(self.settings.layer)
        self.init_signals()



class OnePointAreaWidget(QWidget, Ui_OnePointArea, GeomWidgetsBase):
    line_selection_finished = pyqtSignal()
    def __init__(self, layer_settings, parent):
        QWidget.__init__(self)

        self.setupUi(self)
        GeomWidgetsBase.__init__(self, layer_settings, self)
        self.line_selection_finished.connect(self.on_line_selection_finished)
        self.length_from_point.valueChanged.connect(
            self.on_length_from_reference_point_changed
        )
        self.rotation_point = None

    def on_point_feature_selected(self):
        print self.settings.layer
        if self.settings.layer is None:
            return
        # print iface.activeLayer().name() , self.settings.layer
        if iface.activeLayer().name() != LINE_POINTS:
            return

        if len(self.point_layer.selectedFeatures()) == 0:
            return

        if hasattr(self.widget, 'selected_points_lbl'):

            self.points_count = self.selected_point_count()

            self.widget.selected_points_lbl.setText(str(self.points_count))
            if self.points_count > 1:
                message = QApplication.translate(
                    'GeomWidgetsBase',
                    'The first selected point will be used.'
                )
                self.notice.insertWarningNotification(message)

    def on_line_feature_selected(self):
        # print self.settings.layer
        if self.settings.layer is None:
            return
        # print iface.activeLayer().name() , self.settings.layer
        if iface.activeLayer().name() != POLYGON_LINES:
            return
        # print self.line_layer.selectedFeatures()
        if len(self.line_layer.selectedFeatures()) == 0:
            return

        if hasattr(self.widget, 'selected_line_lbl'):
            self.lines[:] = []
            self.lines_count = self.selected_line_count()

            self.widget.selected_line_lbl.setText(str(self.lines_count))
            if self.lines_count > 1:
                message = QApplication.translate(
                    'GeomWidgetsBase',
                    'The first selected segment will be used.'
                )
                self.notice.insertWarningNotification(message)

            self.line_selection_finished.emit()

    def on_length_from_reference_point_changed(self, new_value):
        # if len(self.point_layer.selectedFeatures()) > 0:
        print 'self.rotation_point ', self.rotation_point
        # self.point_layer.commitChanges()
        if self.rotation_point is not None:
            with edit(self.point_layer):
                point_features = [f.id() for f in self.point_layer.getFeatures()]
                rotation_point = point_features[-1:]
                self.point_layer.deleteFeature(rotation_point[0])

        self.rotation_point = point_by_distance(
            self.point_layer,
            self.points[0],
            self.lines[0].geometry(),
            new_value
        )
        # print self.rotation_point

    def on_line_selection_finished(self):
        self.rotation_point = None

        line_geom = self.lines[0].geometry()
        line_length = line_geom.length()
        # add line length for the user to see
        self.line_length_lbl.setText(str(round(line_length, 2)))
        self.length_from_point.setMaximum(math.modf(line_length)[1])
        # add points for the line.
        self.create_point_layer()
        add_line_points_to_map(self.point_layer, line_geom)
        self.points_count = self.selected_point_count()

        self.widget.selected_points_lbl.setText(str(self.points_count))


    def validate_save(self):
        state = True
        if self.rotation_point is None:
            message = QApplication.translate(
                'OnePointAreaWidget',
                'The rotation point is not added.'
            )
            self.notice.insertErrorNotification(message)
            state = False
        if self.widget.split_polygon_area.value() == 0:
            message = QApplication.translate(
                'OnePointAreaWidget',
                'The area must be greater than 0.'
            )
            self.notice.insertErrorNotification(message)
            if state == True:
                state = False
        return state

    def save(self):
        result = self.validate_save()
        if not result:
            return
        self.executed = True
        if self.settings_layer_connected:
            self.disconnect_signals()

        self.create_preview_layer()
        if self.clockwise.isChecked():
            clockwise = 1
        else:
            clockwise = -1

        self.settings.layer.selectByIds(self.feature_ids)
        selected_line_geom = self.lines[0].geometry()
        split_rotate_line_with_area(
            self.settings.layer,
            self.preview_layer,
            selected_line_geom,
            self.rotation_point.geometry(),
            self.split_polygon_area.value(),
            self.feature_ids,
            clockwise
        )
        iface.setActiveLayer(self.settings.layer)
        self.init_signals()


class JoinPointsWidget(QWidget, Ui_JoinPoints, GeomWidgetsBase):
    line_selection_finished = pyqtSignal()
    def __init__(self, layer_settings, parent):
        QWidget.__init__(self)
        self.setupUi(self)

        GeomWidgetsBase.__init__(self, layer_settings, self)
        self.line_selection_finished.connect(self.on_line_selection_finished)
        self.length_from_point.valueChanged.connect(
            self.on_length_from_reference_point_changed
        )
        self.rotation_point = None

    def create_point_layer(self):
        prev_layers = QgsMapLayerRegistry.instance().mapLayersByName(
            LINE_POINTS
        )
        for prev_layer in prev_layers:
            clear_layer_features(prev_layer)

        if len(prev_layers) == 0:
            self.point_layer = create_temporary_layer(
                self.settings.layer, 'Point', LINE_POINTS, True
            )
            self.point_layer.selectionChanged.connect(
                self.on_point_feature_selected
            )

    def on_feature_selected(self, feature):
        """
        Selects a feature and load line layer which is boundary of the polygon.
        :param feature: List of feature ids selected
        :type feature: List
        :return:
        :rtype:
        """
        if self.parent().currentWidget().objectName() != self.objectName():
            return

        self.set_widget(self.parent().currentWidget())

        if not GEOM_DOCK_ON:
            return

        if len(feature) == 0:
            return

        self.feature_ids = feature

        zoom_to_selected(self.settings.layer)
        self.features = feature_id_to_feature(
            self.settings.layer, self.feature_ids
        )

        if self.settings.layer is None:
            return

        if iface.activeLayer().name() == POLYGON_LINES:
            return

        if self.settings.stdm_layer(self.settings.layer):
            if hasattr(self.widget, 'sel_features_lbl'):
                self.feature_count = self.selected_features_count()

                self.widget.sel_features_lbl.setText(str(self.feature_count))

                self.on_feature_selection_finished()

    def on_feature_selection_finished(self):

        self.line_layer = polygon_to_lines(self.settings.layer, POLYGON_LINES)
        self.create_point_layer()
        polygon_to_points(self.settings.layer, self.line_layer,
                          self.point_layer,  POLYGON_LINES)
        self.settings.line_layer = self.line_layer
        # print self.line_layer, self.line_layer_connected
        if self.line_layer is not None:

            self.line_layer.selectionChanged.connect(
                self.on_line_feature_selected
            )

    def on_point_feature_selected(self):
        # print self.settings.layer
        if self.settings.layer is None:
            return
        # print iface.activeLayer().name() , self.settings.layer
        if iface.activeLayer().name() != LINE_POINTS:
            return

        if len(self.point_layer.selectedFeatures()) == 0:
            return

        if hasattr(self.widget, 'selected_points_lbl'):

            self.points_count = self.selected_point_count()

            self.widget.selected_points_lbl.setText(str(self.points_count))
            if self.points_count > 2:
                message = QApplication.translate(
                    'GeomWidgetsBase',
                    'The first two selected point will be used.'
                )
                self.notice.insertWarningNotification(message)

    def on_line_feature_selected(self):
        # print self.settings.layer
        if self.settings.layer is None:
            return
        # print iface.activeLayer().name() , self.settings.layer
        if iface.activeLayer().name() != POLYGON_LINES:
            return
        # print self.line_layer.selectedFeatures()
        if len(self.line_layer.selectedFeatures()) == 0:
            return

        if hasattr(self.widget, 'selected_line_lbl'):
            self.lines[:] = []
            self.lines_count = self.selected_line_count()

            self.widget.selected_line_lbl.setText(str(self.lines_count))
            if self.lines_count > 1:
                message = QApplication.translate(
                    'GeomWidgetsBase',
                    'The first selected segment will be used.'
                )
                self.notice.insertWarningNotification(message)

            self.line_selection_finished.emit()

    def on_length_from_reference_point_changed(self, new_value):
        # if len(self.point_layer.selectedFeatures()) > 0:
        print 'self.rotation_point ', self.rotation_point
        # self.point_layer.commitChanges()
        if self.rotation_point is not None:
            with edit(self.point_layer):
                point_features = [f.id() for f in self.point_layer.getFeatures()]
                rotation_point = point_features[-1:]
                self.point_layer.deleteFeature(rotation_point[0])

        self.rotation_point = point_by_distance(
            self.point_layer,
            self.points[0],
            self.lines[0].geometry(),
            new_value
        )
        # print self.rotation_point

    def on_line_selection_finished(self):
        self.rotation_point = None

        line_geom = self.lines[0].geometry()
        line_length = line_geom.length()
        # add line length for the user to see
        self.line_length_lbl.setText(str(round(line_length, 2)))
        self.length_from_point.setMaximum(math.modf(line_length)[1])
        # add points for the line.
        # self.create_point_layer()
        add_line_points_to_map(self.point_layer, line_geom, clear=False)
        self.points_count = self.selected_point_count()

        self.widget.selected_points_lbl.setText(str(self.points_count))


    def validate_save(self):
        state = True
        if self.points_count < 2:
            message = QApplication.translate(
                'OnePointAreaWidget',
                'Two points must be selected to split.'
            )
            self.notice.insertErrorNotification(message)
            state = False
        if self.points_count > 2:
            message = QApplication.translate(
                'GeomWidgetsBase',
                'The first two selected point will be used.'
            )
            self.notice.insertWarningNotification(message)

        return state

    def save(self):
        result = self.validate_save()
        if not result:
            return
        self.executed = True
        if self.settings_layer_connected:
            self.disconnect_signals()

        self.create_preview_layer()

        self.settings.layer.selectByIds(self.feature_ids)
        point_geoms = [f.geometry() for f in self.points]
        result = split_join_points(
            self.settings.layer,
            self.preview_layer, point_geoms, self.feature_ids
        )
        if not result:
            message = QApplication.translate(
                'JoinPointsWidget', 'Unable to split polygon.\nCheck the selected points.'
            )
            self.notice.insertErrorNotification(message)

        iface.setActiveLayer(self.settings.layer)
        self.init_signals()


class GeometryWidgetRegistry(object):
    """
    Base container for widget factories based on column types. It is used to
    create widgets based on column type.
    """
    registered_factories = OrderedDict()

    NAME = 'NA'
    OBJECT_NAME = NAME.replace(' ', '_')

    def __init__(self, widget):
        """
        Class constructor.
        :param column: Column object corresponding to the widget factory.
        :type column: BaseColumn
        """
        self._widget = widget

    @property
    def registered_widgets(self):
        """
        :return: Returns column object associated with this factory.
        :rtype: BaseColumn
        """
        return self.registered_factories

    @property
    def widget(self):
        """
        :return: Returns column object associated with this factory.
        :rtype: BaseColumn
        """
        return self._widget

    @classmethod
    def register(cls):
        """
        Adds the widget factory to the collection based on column type info.
        :param cls: Geometry Widget factory class.
        :type cla: GeometryWidgetRegistry
        """
        GeometryWidgetRegistry.registered_factories[cls.NAME] = cls

    @classmethod
    def create(cls, settings, parent=None):
        """
        Creates the appropriate widget.
        :param c: Column object for which to create a widget for.
        :type c: BaseColumn
        :param parent: Parent widget.
        :type parent: QWidget
        :return: Returns a widget for the given column type only if there is
        a corresponding factory in the registry, otherwise returns None.
        :rtype: QWidget
        """
        factory = GeometryWidgetRegistry.factory(cls.NAME)

        if not factory is None:
            w = factory._create_widget(settings, parent)
            factory._widget_configuration(w)

            return w

        return None

    @classmethod
    def factory(cls, name):
        """
        :param name: Type info of a given column.
        :type name: str
        :return: Returns a widget factory based on the corresponding type
        info, otherwise None if there is no registered factory with the given
        type_info name.
        """
        return GeometryWidgetRegistry.registered_factories.get(
                name,
                None
        )

    @classmethod
    def _create_widget(cls, settings, parent):
        #For implementation by sub-classes to create the appropriate widget.
        raise NotImplementedError

    @classmethod
    def _widget_configuration(cls, widget):
        """
        For optionally configurating the widget created by :func:`_create_widget`.
        To be implemnted by sub-classes as default implementation does nothing.
        """
        pass


class MoveLineAreaTool(GeometryWidgetRegistry, MoveLineAreaWidget):
    """
    Widget factory for Text column type.
    """
    NAME = QApplication.translate('MoveLineAreaTool',
                                  'Split Polygon: Move Line and Area')
    OBJECT_NAME = NAME.replace(' ', '_')

    @classmethod
    def _create_widget(cls, settings, parent):
        move_line = MoveLineAreaWidget(settings, parent)
        return move_line


MoveLineAreaTool.register()


class OffsetDistanceTool(GeometryWidgetRegistry, OffsetDistanceWidget):
    """
    Widget factory for Text column type.
    """
    NAME = QApplication.translate('OffsetDistanceTool', 'Split Polygon: Offset Distance')
    OBJECT_NAME = NAME.replace(' ', '_')
    
    @classmethod
    def _create_widget(cls, settings, parent):

        move_line = OffsetDistanceWidget(settings, parent)
        # cls.WIDGET = move_line
        return move_line

OffsetDistanceTool.register()


class OnePointAreaTool(GeometryWidgetRegistry, OnePointAreaWidget):
    """
    Widget factory for Text column type.
    """
    NAME = QApplication.translate('OnePointAreaTool', 'Split Polygon: One Point and Area')
    OBJECT_NAME = NAME.replace(' ', '_')
   
    @classmethod
    def _create_widget(cls, settings, parent):

        move_line = OnePointAreaWidget(settings, parent)
        # cls.WIDGET = move_line
        return move_line

OnePointAreaTool.register()


class JoinPointsTool(GeometryWidgetRegistry, JoinPointsWidget):
    """
    Widget factory for Text column type.
    """
    NAME = QApplication.translate('JoinPointsTool',
                                  'Split Polygon: Join Points')
    OBJECT_NAME = NAME.replace(' ', '_')

    @classmethod
    def _create_widget(cls, settings, parent):
        move_line = JoinPointsWidget(settings, parent)
        # cls.WIDGET = move_line
        return move_line


JoinPointsTool.register()

