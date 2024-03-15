"""
/***************************************************************************
Name                 : Composer Symbol Editor
Description          : Widget for defining symbology properties for the
                       selected spatial field.
Date                 : 24/May/2014
copyright            : (C) 2014 by John Gitau
email                : gkahiu@gmail.com
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
import typing

from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QApplication,
    QMessageBox,
    QPushButton
)
from qgis.core import (
    QgsVectorLayer,
    QgsSimpleMarkerSymbolLayer,
    QgsSimpleFillSymbolLayer,
    QgsProject
)
from qgis.gui import (
    QgsSimpleMarkerSymbolLayerWidget,
    QgsSimpleLineSymbolLayerWidget,
    QgsSimpleFillSymbolLayerWidget
)

from stdm.composer.custom_items.map import StdmMapLayoutItem
from stdm.composer.layout_utils import LayoutUtils
from stdm.data.pg_utils import (
    table_column_names,
    geometryType
)
from stdm.ui.composer.composer_spcolumn_styler import (
        ComposerSpatialColumnEditor,
        SpatialFieldMapping
)
from stdm.ui.gui_utils import GuiUtils

WIDGET, BASE = uic.loadUiType(
    GuiUtils.get_ui_file_path('composer/ui_composer_symbol_editor.ui'))


class _SymbolLayerProxyWidgetMixin(object):
    """
    Removes data-defined properties button plus any additional
    customizations common across the symbol layer widgets.
    """

    def remove_data_defined_properties_button(self):
        btn_data_prop = self.findChild(QPushButton, "mDataDefinedPropertiesButton")
        if btn_data_prop is not None:
            btn_data_prop.setVisible(False)


class _SimpleMarkerSymbolLayerProxyWidget(QgsSimpleMarkerSymbolLayerWidget,
                                          _SymbolLayerProxyWidgetMixin):
    """
    Use this proxy so that we can manually create a marker symbol layer.
    """

    def __init__(self, vectorLayer, parent=None, symbol_layer=None):
        QgsSimpleMarkerSymbolLayerWidget.__init__(self, vectorLayer, parent)

        # Set symbol layer for the widget
        self._sym_layer = symbol_layer
        if self._sym_layer is None:
            self._sym_layer = QgsSimpleMarkerSymbolLayer()
            self._sym_layer.setBorderColor(Qt.red)
            self._sym_layer.setFillColor(Qt.yellow)

        self.setSymbolLayer(self._sym_layer)

        self.remove_data_defined_properties_button()


class _SimpleLineSymbolLayerProxyWidget(QgsSimpleLineSymbolLayerWidget,
                                        _SymbolLayerProxyWidgetMixin):
    """
    Use this proxy so that we can manually create a line symbol layer.
    """

    def __init__(self, vectorLayer, parent=None, symbol_layer=None):
        QgsSimpleLineSymbolLayerWidget.__init__(self, vectorLayer, parent)

        # Set symbol layer for the widget
        self._sym_layer = symbol_layer
        if self._sym_layer is None:
            self._sym_layer = QgsSimpleMarkerSymbolLayer()
            self._sym_layer.setColor(Qt.red)

        self.setSymbolLayer(self._sym_layer)

        self.remove_data_defined_properties_button()


class _SimpleFillSymbolLayerProxyWidget(QgsSimpleFillSymbolLayerWidget,
                                        _SymbolLayerProxyWidgetMixin):
    """
    We are using this proxy since on changing the fill color, the system crashes.
    This workaround disconnects all signals associated with the fill color button and manually
    reconnects using the 'colorChanged' signal to load color selection dialog.
    """

    def __init__(self, vectorLayer, parent=None, symbol_layer=None):
        QgsSimpleFillSymbolLayerWidget.__init__(self, vectorLayer, parent)

        # Set symbol layer for the widget
        self._sym_layer = symbol_layer
        if self._sym_layer is None:
            self._sym_layer = QgsSimpleFillSymbolLayer()
            self._sym_layer.setColor(Qt.cyan)
            self._sym_layer.setFillColor(Qt.yellow)

        self.setSymbolLayer(self._sym_layer)

        self.remove_data_defined_properties_button()

        self._btnFillColor = self.findChild(QPushButton, "btnChangeColor")
        if self._btnFillColor is not None:
            self._btnFillColor.colorChanged.disconnect()
            self._btnFillColor.colorChanged.connect(self.onSetFillColor)

    def onSetFillColor(self, color):
        self.symbolLayer().setFillColor(color)


class ComposerSymbolEditor(WIDGET, BASE):
    """
    Widget for defining symbology properties for the selected spatial field.
    """
    def __init__(self, item: StdmMapLayoutItem, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self._item = item
        self._layout = item.layout()
        self.btnAddField.setIcon(GuiUtils.get_icon('add.png'))
        self.btnClear.setIcon(GuiUtils.get_icon('reset.png'))

        self._editorMappings = {}


        # Load fields if the data source has been specified
        self._ds_name = LayoutUtils.get_stdm_data_source_for_layout(self._layout)


        if self._ds_name is not None:
            self._load_fields()

        # layout_man = QgsProject.instance().layoutManager()
        # layouts = layout_man.layouts()
        # for layout in layouts:
        #     for layout_item in layout.items():
        #         if isinstance(layout_item, StdmMapLayoutItem):
        #             print('** LABEL FIELD = ', layout_item.label_field)
        #             print('** SRID  = ', layout_item.srid)


        # Connect signals
        self._layout.variablesChanged.connect(self.layout_variables_changed)

        if item.name != '':
            idx = self.cboSpatialFields.findText(item.name)
            self.cboSpatialFields.setCurrentIndex(idx)

            sfm = SpatialFieldMapping(item.name, item.label_field)
            sfm.setGeometryType(item.geom_type)
            sfm.setZoomLevel(float(item.zoom))
            sfm.setSRID(item.srid)
            sfm.zoom_type = item.zoom_type

            self.add_styling_widget(sfm)  #(item.name)
            self.on_add_column_styler_widget()

        self.btnAddField.clicked.connect(self.on_add_column_styler_widget)
        self.btnClear.clicked.connect(self.on_clear_tabs)

    def layout_variables_changed(self):
        """
        When the user changes the data source then update the fields.
        """
        data_source_name = LayoutUtils.get_stdm_data_source_for_layout(self._layout)
        self.on_data_source_changed(data_source_name)

    def on_data_source_changed(self, data_source_name):
        """
        When the user changes the data source then update the fields.
        """
        self._ds_name = data_source_name

        self._load_fields()

    def on_clear_tabs(self):
        """
        Slot raised to clear all tabs.
        """
        self.tbFieldProperties.clear()
        self._editorMappings = {}

    def spatial_field_mappings(self):
        """
        Returns a list of 'SpatialFieldMapping' objects based on the configured spatial fields.
        """
        spFieldMappings = []

        editors = list(self._editorMappings.values())
        for ed in editors:
            spFieldMapping = ed.spatialFieldMapping()
            spFieldMappings.append(spFieldMapping)

        return spFieldMappings

    def set_current_spatial_field(self, spatial_field):
        """
        Selects the current spatial field column in the combo of available
        spatial columns.
        :param spatial_field: Name of the spatial field to select.
        :type spatial_field: str
        """
        GuiUtils.set_combo_current_index_by_text(self.cboSpatialFields, spatial_field)

    def add_spatial_field_mappings(self, spatial_field_mappings):
        """
        Adds a list of spatial field mapping objects into the symbol editor.
        """
        for sfm in spatial_field_mappings:
            self.add_spatial_field_mapping(sfm)

    def add_spatial_field_mapping(self, sp_field_mapping):
        """
        Add a style editor tab and apply settings defined in the object.
        """
        self.add_styling_widget(sp_field_mapping)

    def on_add_column_styler_widget(self):
        """
        Slot raised to add a styling and editing widget to the field tab widget.
        """
        spColumnName = self.cboSpatialFields.currentText()

        # Map item
        self._item.set_name(spColumnName)

        if not spColumnName:
            return

        if spColumnName in self._editorMappings:
            return

        style_editor = self.add_styling_widget(spColumnName)

        if style_editor is None:
            QMessageBox.critical(self,
                                 QApplication.translate("ComposerSymbolEditor",
                                                        "Symbol Editor"),
                                 QApplication.translate("ComposerSymbolEditor",
                                                        "The symbol editor could "
                                                        "not be created.\nPlease"
                                                        " check the geometry type"
                                                        " of the spatial column."))
            return

        self._add_editor(spColumnName, style_editor)
            

    def _add_editor(self, col_name: str, editor: ComposerSpatialColumnEditor):
        self._editorMappings[col_name] = editor

    def add_styling_widget(self, sp_field_mapping:typing.Union[str, SpatialFieldMapping]):
        """
        Add a styling widget to the field tab widget.
        """
        if isinstance(sp_field_mapping, str):
            sp_column_name = sp_field_mapping
            apply_mapping = False
        else:
            sp_column_name = sp_field_mapping.spatialField()  # SpatialFieldMapping
            apply_mapping = True

        if not self._build_symbol_widget(sp_field_mapping) is None:
            symbolEditor, geomType, srid = self._build_symbol_widget(
                sp_field_mapping
            )

            if symbolEditor is None:
                return None

            styleEditor = ComposerSpatialColumnEditor(
                sp_column_name,
                self._item
            )

            styleEditor.setSymbolEditor(symbolEditor)
            styleEditor.setGeomType(geomType)
            styleEditor.setSrid(srid)

            styleEditor.setLabelField(self._item.label_field)

            # Apply spatial field mapping
            if apply_mapping:
                styleEditor.applyMapping(sp_field_mapping)

            self.tbFieldProperties.addTab(styleEditor, sp_column_name)

            # Add column name and corresponding widget to the collection
            self._editorMappings[sp_column_name] = styleEditor

            # Set current spatial field in the combobox
            self.set_current_spatial_field(sp_column_name)

            return styleEditor

    def _build_symbol_widget(self, sp_field_mapping: typing.Union[str, SpatialFieldMapping]):
        """
        Build symbol widget based on geometry type.
        """
        if isinstance(sp_field_mapping, str):
            sp_column_name = sp_field_mapping
            sym_layer = None
        else:
            sp_column_name = sp_field_mapping.spatialField()
            sym_layer = sp_field_mapping.symbolLayer()

        geom_type, srid = geometryType(self._ds_name, sp_column_name)

        if not geom_type:
            return None

        vlGeomConfig = "{0}?crs=epsg:{1!s}".format(geom_type, srid)

        vl = QgsVectorLayer(vlGeomConfig, "stdm_proxy", "memory")

        if geom_type == "POINT" or geom_type == "MULTIPOINT":
            symbol_editor = _SimpleMarkerSymbolLayerProxyWidget(
                vl,
                symbol_layer=sym_layer
            )

        elif geom_type == "LINESTRING" or geom_type == "MULTILINESTRING":
            symbol_editor = _SimpleLineSymbolLayerProxyWidget(
                vl,
                symbol_layer=sym_layer
            )

        elif geom_type == "POLYGON" or geom_type == "MULTIPOLYGON":
            symbol_editor = _SimpleFillSymbolLayerProxyWidget(
                vl,
                symbol_layer=sym_layer
            )

        else:
            return None, '', -1

        return symbol_editor, geom_type, srid

    def _load_fields(self):
        """
        Load spatial fields/columns of the given data source.
        """

        if not self._ds_name:
            self.cboSpatialFields.clear()
            return

        prev_text = self.cboSpatialFields.currentText()

        spatialColumns = table_column_names(self._ds_name, True)

        if len(spatialColumns) == 0:
            return

        self.cboSpatialFields.clear()
        self.cboSpatialFields.addItem("")

        self.cboSpatialFields.addItems(spatialColumns)

        idx = self.cboSpatialFields.findText(prev_text)
        self.cboSpatialFields.setCurrentIndex(idx)


