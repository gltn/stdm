"""
/***************************************************************************
Name                 : Composer Spatial Column Editor
Description          : Widget for defining symbology and labeling properties
                       for the selected spatial field.
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
from qgis.PyQt import uic
from qgis.core import (
    QgsSymbolLayerUtils
)

from stdm.composer.layout_utils import LayoutUtils
from stdm.data.pg_utils import (
    table_column_names
)
from stdm.ui.gui_utils import GuiUtils


class SpatialFieldMapping(object):
    """
    Symbol and labeling configuration for an individual spatial field.
    """

    def __init__(self, spatialField="", labelField=""):

        print('SpatialFieldMapping ...')

        self._spatialField = spatialField
        self._labelField = labelField
        self._symbol = None
        self._itemId = ""
        self._layerType = ""
        self._srid = -1
        self._geomType = ""
        self._zoom_level = 4
        self._zoom_type = 'RELATIVE'

    @property
    def zoom_type(self):
        return self._zoom_type

    @zoom_type.setter
    def zoom_type(self, zm_type):
        self._zoom_type = zm_type

    def setSpatialField(self, spatialField):
        """
        Set the name of the spatial field.
        """
        self._spatialField = spatialField

    def spatialField(self):
        """
        Returns the name of the currently configured spatial field.
        """
        return self._spatialField

    def setLabelField(self, labelField):
        """
        Set the name of the field that will be used to label the feature.
        """
        self._labelField = labelField

    def labelField(self):
        """
        Return the field for labeling the spatial feature.
        """
        return self._labelField

    def setSymbolLayer(self, symbol):
        """
        Set the symbol layer associated with the spatial field.
        The symbol should be a subclass of QgsSymbolLayerV2.
        """
        self._symbol = symbol

        if self._symbol is not None:
            self._layerType = self._symbol.layerType()

    def symbolLayer(self):
        """
        Return the symbol layer configured for the spatial field.
        """
        return self._symbol

    def setItemId(self, itemId):
        """
        Returns the composer item id (QgsComposerMap uuid) associated with the spatial field.
        """
        self._itemId = itemId

    def itemId(self):
        """
        Returns the composer item id associated with the spatial field.
        """
        return self._itemId

    def symbolLayerType(self):
        """
        Returns the symbol layer type associated with the the symbol layer.
        """
        return self._layerType

    def srid(self):
        """
        Return the SRID of the referenced spatial column.
        """
        return self._srid

    def setSRID(self, srid):
        """
        Set the SRID of the spatial column.
        """
        self._srid = srid

    def geometryType(self):
        """
        Return the geometry type string representation of the spatial column.
        """
        return self._geomType

    def setGeometryType(self, geomType):
        """
        Set the geometry type of the spatial column.
        """
        self._geomType = geomType

    def zoomLevel(self):
        """
        Return the zoom out scale factor that should be applied relative
        to the extents of a spatial unit.
        """
        return self._zoom_level

    def setZoomLevel(self, zoomLevel):
        """
        Set zoom out scale factor.
        """
        self._zoom_level = zoomLevel

    def toVectorURI(self):
        """
        Returns a QgsVectorLayer URI using the geometry type and SRID information.
        """
        return "{0}?crs=epsg:{1!s}".format(self._geomType, self._srid)

    def toDomElement(self, domDocument):
        """
        Returns a QDomElement with the object instance settings
        """
        spColumnElement = domDocument.createElement("SpatialField")
        spColumnElement.setAttribute("name", self._spatialField)
        spColumnElement.setAttribute("labelField", self._labelField)
        spColumnElement.setAttribute("itemid", self._itemId)
        spColumnElement.setAttribute("srid", self._srid)
        spColumnElement.setAttribute("geomType", self._geomType)
        spColumnElement.setAttribute('zoomType', self._zoom_type)
        spColumnElement.setAttribute("zoom", str(self._zoom_level))
        symbolElement = domDocument.createElement("Symbol")

        # Append symbol properties element
        if self._symbol is not None:
            prop = self._symbol.properties()
            QgsSymbolLayerUtils.saveProperties(prop, domDocument, symbolElement)
            symbolElement.setAttribute("layerType", self._layerType)

        spColumnElement.appendChild(symbolElement)

        return spColumnElement


WIDGET, BASE = uic.loadUiType(
    GuiUtils.get_ui_file_path('composer/ui_composer_spcolumn_styler.ui'))


class ComposerSpatialColumnEditor(WIDGET, BASE):
    """
    Widget for defining symbology and labeling properties for the selected spatial field.
    """

    def __init__(self, spColumnName, layout_item, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        print('class ComposerSpatialColumnEditor ...')

        self._layout = layout_item.layout()
        self._map_item = layout_item

        self._spColumnName = spColumnName

        self._symbol_editor = None

        self._zoom_out_level = 16

        self._zoom_fixed_scale = 1000

        self.sb_zoom.setValue(self._zoom_out_level)

        self.sb_fixed_zoom.setValue(self._zoom_fixed_scale)

        self._srid = -1

        self._geomType = ""

        # Load fields if the data source has been specified
        self._dsName = LayoutUtils.get_stdm_data_source_for_layout(self._layout)
        self._loadFields()

        # Connect signals
        self._layout.variablesChanged.connect(self.layout_variables_changed)
        self.sb_zoom.valueChanged.connect(self.on_zoom_level_changed)
        self.sb_fixed_zoom.valueChanged.connect(self.on_zoom_fixed_scale_changed)
        self.rb_relative_zoom.toggled.connect(self.on_relative_zoom_checked)
        self.cboLabelField.currentTextChanged.connect(self.on_label_field_changed)

        # Set relative zoom level as the default selected option for the radio buttons
        self.rb_relative_zoom.setChecked(True)

    def layout_variables_changed(self):
        """
        When the user changes the data source then update the fields.
        """
        data_source_name = LayoutUtils.get_stdm_data_source_for_layout(self._layout)
        self.onDataSourceChanged(data_source_name)

    def onDataSourceChanged(self, dataSourceName):
        """
        When the user changes the data source then update the fields.
        """
        self._dsName = dataSourceName
        self._loadFields()

    def on_relative_zoom_checked(self, state):
        # Slot when the radio button for relative zoom is checked/unchecked.
        if state:
            self.sb_zoom.setEnabled(True)
            self.sb_fixed_zoom.setEnabled(False)
        else:
            self.sb_zoom.setEnabled(False)
            self.sb_fixed_zoom.setEnabled(True)
        self._map_item.set_zoom_type('RELATIVE')

    def on_fixed_scale_zoom_checked(self, state):
        # Slot riased when the radio button for fixed scale zoom is selected.
        self._map_item.set_zoom_type('FIXED')
        pass

    def on_zoom_level_changed(self, value):
        """
        Slot raised when the spin box value, representing the zoom level,
        changes.
        """
        if self._zoom_out_level != value:
            self._zoom_out_level = value

        self._map_item.set_zoom(value)

    def on_label_field_changed(self, text: str):
        self._map_item.set_label_field(text)

    def setSymbolEditor(self, editor):
        """
        Set the widget's symbol editor.
        """
        self._symbol_editor = editor
        self.styleLayout.addWidget(editor)

    def symbolEditor(self):
        """
        Returns the current symbol editor.
        """
        return self._symbol_editor

    def symbolLayer(self):
        """
        Returns the symbol layer specified in the symbol editor.
        """
        return self._symbol_editor.symbolLayer()

    def setGeomType(self, geomType):
        """
        Set the geometry type of the specified spatial unit.
        """
        self._geomType = geomType
        self._map_item.set_geom_type(geomType)

    def geomType(self):
        """
        Return the geometry type of the specified spatial unit.
        """
        return self._geomType

    def setSrid(self, srid):
        """
        Set the SRID of the specified spatial unit.
        """
        self._srid = srid
        self._map_item.set_srid(srid)

    def srid(self):
        """
        Return the SRID of the specified spatial unit.
        """
        return self._srid

    def spatialFieldMapping(self):
        """
        Returns a SpatialFieldMapping object instance configured to the current settings.
        """
        try:
            sp_field_mapping = SpatialFieldMapping(self._spColumnName, self.cboLabelField.currentText())

            sp_field_mapping.setSymbolLayer(self.symbolLayer())
            sp_field_mapping.setSRID(self._srid)
            sp_field_mapping.setGeometryType(self._geomType)
            if self.rb_relative_zoom.isChecked():
                zm_type = 'RELATIVE'
                zoom = self.sb_zoom.value()
            elif self.rb_fixed_scale.isChecked():
                zm_type = 'FIXED'
                zoom = self.sb_fixed_zoom.value()

            sp_field_mapping.zoom_type = zm_type
            sp_field_mapping.setZoomLevel(zoom)

            return sp_field_mapping
        except:
            return None

    def applyMapping(self, spatialFieldMapping):
        """
        Configures the widget to use the specified spatial field mapping.
        """
        # Configure widget based on the mapping
        self._spColumnName = spatialFieldMapping.spatialField()
        self.setLabelField(spatialFieldMapping.labelField())
        self._srid = spatialFieldMapping.srid()
        self._geomType = spatialFieldMapping.geometryType()
        zoom_level = spatialFieldMapping.zoomLevel()
        zoom_type = spatialFieldMapping.zoom_type
        if zoom_type == 'RELATIVE':
            self.rb_relative_zoom.setChecked(True)
            self.sb_zoom.setValue(float(zoom_level))
        elif zoom_type == 'FIXED':
            self.rb_fixed_scale.setChecked(True)
            self.sb_fixed_zoom.setValue(float(zoom_level))

    def setLabelField(self, labelField):
        """
        Select field label item.
        """
        fieldIndex = self.cboLabelField.findText(labelField)

        if fieldIndex != -1:
            self.cboLabelField.setCurrentIndex(fieldIndex)


    def _loadFields(self):
        """
        Load labeling fields/columns.
        """
        if not self._dsName:
            self.cboLabelField.clear()
            return

        cols = table_column_names(self._dsName)

        spatialCols = table_column_names(self._dsName, True)

        spSet = set(spatialCols)
        nonSpatialCols = [c for c in cols if c not in spSet]

        if len(nonSpatialCols) == 0:
            return

        self.cboLabelField.clear()
        self.cboLabelField.addItem("")
        self.cboLabelField.addItems(nonSpatialCols)

    def on_zoom_fixed_scale_changed(self, value):
        """
        Slot raised when the fixed scale widget value changes.
        """
        if self._zoom_fixed_scale != value:
            self._zoom_fixed_scale = value
