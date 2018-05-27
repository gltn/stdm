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
from PyQt4.QtGui import (
    QMessageBox,
    QPushButton,
    QWidget
)
from PyQt4.QtCore import Qt

from qgis.core import (
    QgsSimpleFillSymbolLayerV2,
    QgsSymbolLayerV2Utils,
    QgsCoordinateReferenceSystem, QgsUnitTypes)

from stdm.data.pg_utils import (
    table_column_names, column_spatial_reference
)
from stdm.settings import current_profile

from .ui_composer_spcolumn_styler import Ui_frmComposerSpatialColumnEditor

class SpatialFieldMapping(object):
    """
    Symbol and labeling configuration for an individual spatial field.
    """
    # TODO show warning the feature will not work if it is geographic projection
    def __init__(self,spatialField="",labelField=""):
        self._spatialField = spatialField
        self._labelField = labelField
        self._symbol = None
        self._itemId = ""
        self._layerType = ""
        self._srid = -1
        self._geomType = ""
        self._zoom_level = 4
        self._scale = 0
        self._length_prefix = ''
        self._area_prefix = ''
        self._length_suffix = ''
        self._area_suffix = ''
        self._crs = None
        self._length_prefix_type = ''
        self._area_prefix_type = ''
        self._length_suffix_type = ''
        self._area_suffix_type = ''
        # self._output_crs = 0
        
    def setSpatialField(self,spatialField):
        """
        Set the name of the spatial field.
        """
        self._spatialField = spatialField
        
    def spatialField(self):
        """
        Returns the name of the currently configured spatial field.
        """
        return self._spatialField
    
    def setLabelField(self,labelField):
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
        
        if not self._symbol is None:
            self._layerType = self._symbol.layerType()
        
    def symbolLayer(self):
        """
        Return the symbol layer configured for the spatial field.
        """
        return self._symbol
    
    def setItemId(self,itemId):
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
    
    def setSRID(self,srid):
        """
        Set the SRID of the spatial column.
        """
        self._crs = QgsCoordinateReferenceSystem(
            srid, QgsCoordinateReferenceSystem.EpsgCrsId
        )
        self._srid = srid
        
    def geometryType(self):
        """
        Return the geometry type string representation of the spatial column.
        """
        return self._geomType
    
    def setGeometryType(self,geomType):
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
    
    def setZoomLevel(self,zoomLevel):
        """
        Set zoom out scale factor.
        """
        self._zoom_level = zoomLevel
        self._scale = 0

    def scale(self):
        """
        Return the scale of the map canvas.
        """
        return self._scale

    def set_scale(self, scale):
        """
        Set zoom out scale factor.
        """
        self._scale = scale
        self._zoom_level = 0

    def set_area_prefix_type(self, area_prefix_type):
        """
        Sets area prefix type.
        :param area_prefix_type: Area prefix type
        :type area_prefix_type: String
        :return: 
        :rtype: 
        """
        self._area_prefix_type = area_prefix_type

    def set_length_prefix_type(self, length_prefix_type):
        """
        Sets area prefix type.
        :param length_prefix_type: Length prefix type
        :type length_prefix_type: String
        :return: 
        :rtype: 
        """
        self._length_prefix_type = length_prefix_type

    def set_area_suffix_type(self, area_suffix_type):
        """
        Sets area suffix type.
        :param area_suffix_type: Area suffix type
        :type area_suffix_type: String
        :return: 
        :rtype: 
        """
        self._area_suffix_type = area_suffix_type

    def set_length_suffix_type(self, length_suffix_type):
        """
        Sets area suffix type.
        :param length_suffix_type: Length suffix type
        :type length_suffix_type: String
        :return: 
        :rtype: 
        """
        self._length_suffix_type = length_suffix_type
    
    def set_area_prefix(self, area_prefix):
        """
        Sets area prefix.
        :param area_prefix: Area prefix
        :type area_prefix: String
        :return: 
        :rtype: 
        """
        self._area_prefix = area_prefix

    def set_length_prefix(self, length_prefix):
        """
        Sets area prefix.
        :param length_prefix: Length prefix
        :type length_prefix: String
        :return: 
        :rtype: 
        """
        self._length_prefix = length_prefix

    def set_area_suffix(self, area_suffix):
        """
        Sets area suffix.
        :param area_suffix: Area suffix
        :type area_suffix: String
        :return: 
        :rtype: 
        """
        self._area_suffix = area_suffix


    def set_length_suffix(self, length_suffix):
        """
        Sets area suffix.
        :param length_suffix: Length suffix
        :type length_suffix: String
        :return: 
        :rtype: 
        """
        self._length_suffix = length_suffix

    def get_length_prefix(self):
        return self._length_prefix

    def get_area_prefix(self):
        return self._area_prefix

    def get_length_suffix(self):
        return self._length_suffix

    def get_area_suffix(self):
        return self._area_suffix

    def get_length_prefix_type(self):
        return self._length_prefix_type

    def get_area_prefix_type(self):
        return self._area_prefix_type

    def get_length_suffix_type(self):
        return self._length_suffix_type

    def get_area_suffix_type(self):
        return self._area_suffix_type

    # def get_output_crs(self):
    #     return self._output_crs
        
    def toVectorURI(self):
        """
        Returns a QgsVectorLayer URI using the geometry type and SRID information.
        """
        return  "{0}?crs=epsg:{1!s}".format(self._geomType,self._srid)
    
    def toDomElement(self, domDocument):
        """
        Returns a QDomElement with the object instance settings
        """
        # print self._area_prefix, self.area_suffix()
        spColumnElement = domDocument.createElement("SpatialField")
        spColumnElement.setAttribute("name",self._spatialField)
        spColumnElement.setAttribute("labelField",self._labelField)
        spColumnElement.setAttribute("itemid",self._itemId)
        spColumnElement.setAttribute("srid",self._srid)
        spColumnElement.setAttribute("geomType",self._geomType)

        spColumnElement.setAttribute("areaPrefixType", self._area_prefix_type)
        spColumnElement.setAttribute("lengthPrefixType", self._length_prefix_type)
        spColumnElement.setAttribute("areaSuffixType", self._area_suffix_type)
        spColumnElement.setAttribute("lengthSuffixType", self._length_suffix_type)

        spColumnElement.setAttribute("areaPrefix", self._area_prefix)
        spColumnElement.setAttribute("lengthPrefix", self._length_prefix)
        spColumnElement.setAttribute("areaSuffix", self._area_suffix)
        spColumnElement.setAttribute("lengthSuffix", self._length_suffix)

        spColumnElement.setAttribute("zoom",str(self._zoom_level))
        spColumnElement.setAttribute("scale", str(self._scale))

        symbolElement = domDocument.createElement("Symbol")
        
        #Append symbol properties element
        if not self._symbol is None:
            prop = self._symbol.properties()
            QgsSymbolLayerV2Utils.saveProperties(prop,domDocument,symbolElement)
            symbolElement.setAttribute("layerType",self._layerType)
        
        spColumnElement.appendChild(symbolElement)
        
        return spColumnElement

class ComposerSpatialColumnEditor(QWidget,Ui_frmComposerSpatialColumnEditor):
    """
    Widget for defining symbology and labeling properties for the selected spatial field.
    """
    def __init__(self, spColumnName, composerWrapper, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.current_profile = current_profile()

        self._composerWrapper = composerWrapper
        # Load fields if the data source has been specified
        self._dsName = self._composerWrapper.selectedDataSource()
        self._spColumnName = spColumnName
        
        self._symbol_editor = None

        self._zoom_out_level = 1.3
        self._scale = 0
        self.sb_zoom.setValue(self._zoom_out_level)
        
        self._srid = -1
        self._crs = None
        self._geomType = ""

        self._length_prefix = ''

        self._area_prefix = ''

        self._length_suffix = ''

        self._area_suffix = ''

        self._loadFields()

        self._length_prefix_type = self.length_prefix_type.currentText()

        self._area_prefix_type = self.area_prefix_type.currentText()

        self._length_suffix_type = self.length_suffix_type.currentText()

        self._area_suffix_type = self.area_suffix_type.currentText()

        #Connect signals
        self._composerWrapper.dataSourceSelected.connect(
            self.onDataSourceChanged
        )

        self.sb_zoom.valueChanged.connect(self.on_zoom_level_changed)

        self.zoom_rad.clicked.connect(self.on_zoom_radio_clicked)

        self.scale_rad.clicked.connect(self.on_scale_radio_clicked)

        self.length_prefix_type.currentIndexChanged[str].connect(
            self.on_length_prefix_type_changed
        )
        self.area_prefix_type.currentIndexChanged[str].connect(
            self.on_area_prefix_type_changed
        )

        self.length_suffix_type.currentIndexChanged[str].connect(
            self.on_length_suffix_type_changed
        )
        self.area_suffix_type.currentIndexChanged[str].connect(
            self.on_area_suffix_type_changed
        )

        self.length_prefix.textChanged.connect(
            self.on_length_prefix_changed
        )
        self.area_prefix.textChanged.connect(
            self.on_area_prefix_changed
        )

        self.length_suffix.textChanged.connect(
            self.on_length_suffix_changed
        )
        self.area_suffix.textChanged.connect(
            self.on_area_suffix_changed
        )

    def on_zoom_radio_clicked(self, state):
        self._zoom_out_level = 0
        self._scale = 1

    def on_scale_radio_clicked(self, state):
        self._zoom_out_level = 1
        self._scale = 0

    def onDataSourceChanged(self, dataSourceName):
        """
        When the user changes the data source then update the fields.
        """
        self._dsName = dataSourceName
        self._loadFields()  
        
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
    
    def setGeomType(self,geomType):
        """
        Set the geometry type of the specified spatial unit.
        """
        self._geomType = geomType
        
    def geomType(self):
        """
        Return the geometry type of the specified spatial unit.
        """
        return self._geomType
    
    def setSrid(self,srid):
        """
        Set the SRID of the specified spatial unit.
        """
        self._crs = QgsCoordinateReferenceSystem(
            srid, QgsCoordinateReferenceSystem.EpsgCrsId
        )
        self._srid = srid
        
    def srid(self):
        """
        Return the SRID of the specified spatial unit.
        """
        return self._srid

    def set_area_prefix(self, area_prefix):
        """
        Sets area prefix.
        :param area_prefix: Area prefix
        :type area_prefix: String
        :return:
        :rtype:
        """
        self._area_prefix = area_prefix

    def set_length_prefix(self, length_prefix):
        """
        Sets area prefix.
        :param length_prefix: Length prefix
        :type length_prefix: String
        :return:
        :rtype:
        """
        self._length_prefix = length_prefix

    def set_area_suffix(self, area_suffix):
        """
        Sets area suffix.
        :param area_suffix: Area suffix
        :type area_suffix: String
        :return:
        :rtype:
        """
        self._area_suffix = area_suffix

    def set_length_suffix(self, length_suffix):
        """
        Sets area suffix.
        :param length_suffix: Length suffix
        :type length_suffix: String
        :return:
        :rtype:
        """
        self._length_suffix = length_suffix

    def spatialFieldMapping(self):
        """
        Returns a SpatialFieldMapping object instance configured to the current settings.
        """
        sp_field_mapping = SpatialFieldMapping(
            self._spColumnName, self.cboLabelField.currentText()
        )

        sp_field_mapping.setSymbolLayer(self.symbolLayer())
        sp_field_mapping.setSRID(self._srid)
        sp_field_mapping.setGeometryType(self._geomType)

        if self.zoom_rad.isChecked():
            sp_field_mapping.setZoomLevel(self.sb_zoom.value())
        else:
            sp_field_mapping.set_scale(self.sb_zoom.value())

        sp_field_mapping.set_area_prefix_type(self._area_prefix_type)
        sp_field_mapping.set_length_prefix_type(self._length_prefix_type)
        sp_field_mapping.set_area_suffix_type(self._area_suffix_type)
        sp_field_mapping.set_length_suffix_type(self._length_suffix_type)

        sp_field_mapping.set_area_prefix(self._area_prefix)
        sp_field_mapping.set_length_prefix(self._length_prefix)
        sp_field_mapping.set_area_suffix(self._area_suffix)
        sp_field_mapping.set_length_suffix(self._length_suffix)

        return sp_field_mapping
    
    def applyMapping(self, spatialFieldMapping):
        """
        Configures the widget to use the specified spatial field mapping.
        """
        #Configure widget based on the mapping 
        self._spColumnName = spatialFieldMapping.spatialField()
        self.setLabelField(spatialFieldMapping.labelField())
        self._srid = spatialFieldMapping.srid()
        self._geomType = spatialFieldMapping.geometryType()

        if self.zoom_rad.isChecked():
            self.sb_zoom.setValue(spatialFieldMapping.zoomLevel())
        else:
            self.sb_zoom.setValue(spatialFieldMapping.scale())

        self.area_suffix.setText(spatialFieldMapping.get_area_suffix())
        self.area_prefix.setText(spatialFieldMapping.get_area_prefix())
        self.length_suffix.setText(spatialFieldMapping.get_length_suffix())
        self.length_prefix.setText(spatialFieldMapping.get_length_prefix())

        self.set_current_cbo_item(
            self.area_suffix_type, spatialFieldMapping.get_area_suffix_type()
        )
        self.set_current_cbo_item(
            self.area_prefix_type, spatialFieldMapping.get_area_prefix_type()
        )
        self.set_current_cbo_item(
            self.length_suffix_type, spatialFieldMapping.get_length_suffix_type()
        )
        self.set_current_cbo_item(
            self.length_prefix_type, spatialFieldMapping.get_length_prefix_type()
        )

    def setLabelField(self,labelField):
        """
        Select field label item.
        """
        fieldIndex = self.cboLabelField.findText(labelField)
        
        if fieldIndex != -1:
            self.cboLabelField.setCurrentIndex(fieldIndex)

    def on_zoom_level_changed(self, value):
        """
        Slot raised when the spin box value, representing the zoom level,
        changes.
        """
        if self._zoom_out_level != value:
            self._zoom_out_level = value

    def on_length_prefix_type_changed(self, value):
        """
        A slot raised when length prefix type changes.
        :param value: The new value.
        :type value: String
        :return:
        :rtype:
        """
        if value == 'None':
            self._length_prefix = ''
            self.length_prefix.clear()
            self.length_prefix.setDisabled(True)

        elif value == 'Map Unit':
            unit = self._crs.mapUnits()
            unit_text = QgsUnitTypes.toString(unit).title()
            self.length_prefix.setDisabled(False)
            self.length_prefix.setText(unit_text)

        elif value == 'Custom':
            self._length_prefix = ''
            self.length_prefix.clear()
            self.length_prefix.setDisabled(False)

        self._length_prefix_type = value

    def on_area_prefix_type_changed(self, value):
        """
        A slot raised when area prefix type changes.
        :param value: The new value.
        :type value: String
        :return:
        :rtype:
        """
        if value == 'None':
            self._area_prefix = ''
            self.area_prefix.clear()
            self.area_prefix.setDisabled(True)

        elif value == 'Map Unit':
            unit = self._crs.mapUnits()
            area_unit = QgsUnitTypes.distanceToAreaUnit(unit)
            unit_text = QgsUnitTypes.toString(area_unit).title()
            self.area_prefix.setDisabled(False)
            self.area_prefix.setText(unit_text)

        elif value == 'Custom':
            self._area_prefix = ''
            self.area_prefix.clear()
            self.area_prefix.setDisabled(False)

        elif value == 'Hectares':
            self._area_prefix = ''
            self.area_prefix.clear()
            self.area_prefix.setDisabled(True)
            self._area_prefix = 'Hectares'
            self.area_prefix.setDisabled(False)
            self.area_prefix.setText(self._area_prefix)

        self._area_prefix_type = value

    def on_length_suffix_type_changed(self, value):
        """
        A slot raised when length suffix type changes.
        :param value: The new value.
        :type value: String
        :return:
        :rtype:
        """
        if value == 'None':
            self._length_suffix = ''
            self.length_suffix.clear()
            self.length_suffix.setDisabled(True)

        elif value == 'Map Unit':
            unit = self._crs.mapUnits()
            unit_text = QgsUnitTypes.toString(unit).title()
            self.length_suffix.setDisabled(False)
            self.length_suffix.setText(unit_text)

        elif value == 'Custom':
            self._length_suffix = ''
            self.length_suffix.clear()
            self.length_suffix.setDisabled(False)

        self._length_suffix_type = value

    def on_area_suffix_type_changed(self, value):
        """
        A slot raised when area suffix type changes.
        :param value: The new value.
        :type value: String
        :return:
        :rtype:
        """
        if value == 'None':
            self._area_suffix = ''
            self.area_suffix.clear()
            self.area_suffix.setDisabled(True)

        elif value == 'Map Unit':
            unit = self._crs.mapUnits()
            area_unit = QgsUnitTypes.distanceToAreaUnit(unit)
            unit_text = QgsUnitTypes.toString(area_unit).title()
            self.area_suffix.setDisabled(False)
            self.area_suffix.setText(unit_text)

        elif value == 'Custom':
            self._area_suffix = ''
            self.area_suffix.clear()
            self.area_suffix.setDisabled(False)

        elif value == 'Hectares':
            self._area_suffix = ''
            self.area_suffix.clear()
            self.area_suffix.setDisabled(True)
            self._area_suffix = 'Hectares'
            self.area_suffix.setDisabled(False)
            self.area_suffix.setText(self._area_suffix)

        self._area_suffix_type = value

    def on_length_prefix_changed(self, value):
        """
        A slot raised when length prefix type changes.
        :param value: The new value.
        :type value: String
        :return:
        :rtype:
        """
        self._length_prefix = self.length_prefix.text()

    def on_area_prefix_changed(self, value):
        """
        A slot raised when area prefix type changes.
        :param value: The new value.
        :type value: String
        :return:
        :rtype:
        """
        self._area_prefix = self.area_prefix.text()

    def on_length_suffix_changed(self, value):
        """
        A slot raised when length suffix type changes.
        :param value: The new value.
        :type value: String
        :return:
        :rtype:
        """
        self._length_suffix = self.length_suffix.text()

    def on_area_suffix_changed(self, value):
        """
        A slot raised when area suffix type changes.
        :param value: The new value.
        :type value: String
        :return:
        :rtype:
        """
        self._area_suffix = self.area_suffix.text()

    # def on_output_projection_changed(self, value):
    #
    #     self._output_crs = value.srsid()

    def _loadFields(self):
        """
        Load labeling fields/columns.
        """
        if not self._dsName:
            self.cboLabelField.clear()
            return
        
        cols = table_column_names(self._dsName)
        spatialCols = table_column_names(self._dsName,True)
        
        spSet = set(spatialCols)
        nonSpatialCols = [c for c in cols if c not in spSet]
        
        if len(nonSpatialCols) == 0:
            return
        
        self.cboLabelField.clear()
        self.cboLabelField.addItem("")
        
        self.cboLabelField.addItems(nonSpatialCols)

    def set_current_cbo_item(self, combo, name):
        # Set current combo item on a combobox using name.

        if name != '':
            index = combo.findText(name, Qt.MatchFixedString)
            if index >= 0:
                combo.setCurrentIndex(index)
        else:
            if combo.count() > 0:
                combo.setCurrentIndex(0)
