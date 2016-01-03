"""
/***************************************************************************
Name                 : Composer item formatters
Description          : Classes for formatting QgsComposerItems.
Date                 : 10/May/2014
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
    QApplication,
    QComboBox,
    QGroupBox,
    QPlainTextEdit,
    QCheckBox,
    QPushButton,
    QRadioButton,
    QWidget,
    QLabel,
    QLineEdit,
    QDoubleSpinBox,
    QMessageBox,
    QScrollArea,
    QToolButton
)
from PyQt4.QtCore import QFile

from qgis.gui import (
    QgsCollapsibleGroupBoxBasic
)
from qgis.core import (
    QgsComposerArrow,
    QgsComposerAttributeTable,
    QgsComposerLabel,
    QgsComposerMap,
    QgsComposerPicture,
    QGis
)

from stdm.ui.composer import (
    ComposerChartConfigEditor,
    ComposerFieldSelector,
    ComposerPhotoDataSourceEditor,
    ComposerSymbolEditor,
    ComposerTableDataSourceEditor
)
from stdm.utils import PLUGIN_DIR
                     
class BaseComposerItemFormatter(object):
    """
    Defines the abstract interface for implementation by subclasses.
    """
    def apply(self, composerItem, composerWrapper, fromTemplate=False):
        """
        Subclasses to implement this method for formatting composer items.
        """
        raise NotImplementedError
    
class LineFormatter(BaseComposerItemFormatter):
    """
    Removes the marker in an arrow composer item to depict a line.
    """
    def apply(self, arrow, composerWrapper, fromTemplate=False):
        """
        This code is not applicable since the method returns a QgsComposerItem instance
        instead of an arrow.
        if not isinstance(arrow,QgsComposerArrow):
            return
        """
        
        #Resorted to use the editor to manually edit the composer item to depict a line
        arrowEditor = composerWrapper.itemDock().widget()
        
        if arrowEditor != None:
            noMarkerRadioButton = arrowEditor.findChild(QRadioButton,"mNoMarkerRadioButton")
            #If exists, force remove of marker
            if noMarkerRadioButton != None:
                noMarkerRadioButton.toggle()
                
            #Hide arrow editor controls
            arrowMarkersGroup = arrowEditor.findChild(QWidget,"mArrowMarkersGroupBox")
            if arrowMarkersGroup != None:
                arrowMarkersGroup.setVisible(False)
                
            #Remove arrowhead width controls
            lblWidth = arrowEditor.findChild(QLabel,"label_2")
            if lblWidth != None:
                lblWidth.setVisible(False)
                
            widthSpinBox = arrowEditor.findChild(QDoubleSpinBox,"mArrowHeadWidthSpinBox")
            if widthSpinBox != None:
                widthSpinBox.setVisible(False)
        
class DataLabelFormatter(BaseComposerItemFormatter):
    """
    Adds text to indicate that the label is an STDM data field.
    """
    def apply(self, label, composerWrapper, fromTemplate=False):
        if not isinstance(label,QgsComposerLabel):
            return
        
        if not fromTemplate:
            #Set display text
            label.setText(QApplication.translate("DataLabelFormatter","[STDM Data Field]"))
        
            #Adjust width
            label.adjustSizeToText()
            
            fieldSelector = ComposerFieldSelector(composerWrapper, label)
            stdmDock = composerWrapper.stdmItemDock()
            stdmDock.setWidget(fieldSelector)
            
            #Add widget to the composer wrapper widget mapping collection
            composerWrapper.addWidgetMapping(label.uuid(), fieldSelector)

        #Set ID to match UUID
        label.setId(label.uuid())
        
        #Get the editor widget for the label
        labelEditor = composerWrapper.itemDock().widget()
        
        #Remove some of the editing controls
        if labelEditor != None:
            textEdit = labelEditor.findChild(QPlainTextEdit,"mTextEdit")
            if textEdit != None:
                textEdit.setVisible(False)
                
            renderHtmlCheck = labelEditor.findChild(QCheckBox,"mHtmlCheckBox")
            if renderHtmlCheck != None:
                renderHtmlCheck.setVisible(False)
                
            expressionBtn = labelEditor.findChild(QPushButton,"mInsertExpressionButton")
            if expressionBtn != None:
                expressionBtn.setVisible(False)
                
class MapFormatter(BaseComposerItemFormatter):
    """
    Add widget for formatting spatial data sources.
    """
    def apply(self, templateMap, composerWrapper, fromTemplate=False):
        if not isinstance(templateMap,QgsComposerMap):
            return
        
        if not fromTemplate:
            #Enable outline in map composer item
            frameWidth = 0.3
            templateMap.setFrameEnabled(True)
            templateMap.setFrameOutlineWidth(frameWidth)

            templateMap.setPreviewMode(QgsComposerMap.Rectangle)

            templateMap.setKeepLayerSet(True)

            #Enable the properties for the corresponding widget for the frame
            #Get the editor widget for the label
            mapEditor = composerWrapper.itemDock().widget()

            if mapEditor != None:
                frameGP = mapEditor.findChild(QgsCollapsibleGroupBoxBasic,"mGridFrameGroupBox")
                if frameGP != None:
                    frameGP.setCollapse(True)

                thicknessSpinBox = mapEditor.findChild(QDoubleSpinBox,"mGridFramePenSizeSpinBox")
                if thicknessSpinBox != None:
                    thicknessSpinBox.setValue(frameWidth)
        
            #Create styling editor and it to the dock widget
            composerSymbolEditor = ComposerSymbolEditor(composerWrapper)
            stdmDock = composerWrapper.stdmItemDock()
            stdmDock.setWidget(composerSymbolEditor)
                
            #Add widget to the composer wrapper widget mapping collection
            composerWrapper.addWidgetMapping(templateMap.uuid(), composerSymbolEditor)

        #Set ID to match UUID
        templateMap.setId(templateMap.uuid())

class PhotoFormatter(BaseComposerItemFormatter):
    """
    Add widget for formatting composer picture items.
    """
    def apply(self, photo_item, composerWrapper, fromTemplate=False):
        if not isinstance(photo_item, QgsComposerPicture):
            return

        #Get the main picture editor widget and configure widgets
        picture_editor = composerWrapper.itemDock().widget()
        if not picture_editor is None:
            self._configure_picture_editor_properties(picture_editor)

        if not fromTemplate:
            #Enable outline in map composer item
            frame_width = 0.15
            photo_item.setFrameEnabled(True)
            photo_item.setFrameOutlineWidth(frame_width)
            photo_item.setResizeMode(QgsComposerPicture.ZoomResizeFrame)

            #Create data properties editor and it to the dock widget
            photo_data_source_editor = ComposerPhotoDataSourceEditor(composerWrapper)
            stdmDock = composerWrapper.stdmItemDock()
            stdmDock.setWidget(photo_data_source_editor)

            #Add widget to the composer wrapper widget mapping collection
            composerWrapper.addWidgetMapping(photo_item.uuid(), photo_data_source_editor)

        #Set default photo properties
        default_photo = PLUGIN_DIR + "/images/icons/photo_512.png"
        if QFile.exists(default_photo):
            photo_item.setPictureFile(default_photo)

        #Set ID to match UUID
        photo_item.setId(photo_item.uuid())

    def _configure_picture_editor_properties(self, base_picture_editor):
        #Get scroll area first
        scroll_area = base_picture_editor.findChild(QScrollArea,"scrollArea")
        if not scroll_area is None:
            contents_widget = scroll_area.widget()

            properties_groupbox = contents_widget.findChild(QGroupBox, "mPreviewGroupBox")
            if not properties_groupbox is None:
                properties_groupbox.setVisible(False)

            search_directory_groupbox = contents_widget.findChild(QGroupBox,
                                                                  "mSearchDirectoriesGroupBox")
            if not search_directory_groupbox is None:
                search_directory_groupbox.setVisible(False)

            img_rotation_groupbox = contents_widget.findChild(QgsCollapsibleGroupBoxBasic,
                                                                 "mRotationGroupBox")
            if not img_rotation_groupbox is None:
                img_rotation_groupbox.setVisible(False)

            item_id_groupboxes = contents_widget.findChildren(QGroupBox, "groupBox")
            for gp in item_id_groupboxes:
                gp.setVisible(False)

class TableFormatter(BaseComposerItemFormatter):
    """
    Add widget for formatting an attribute table item.
    """
    def apply(self, table_item, composerWrapper, fromTemplate=False):
        if not isinstance(table_item, QgsComposerAttributeTable):
            return

        #Get the table editor widget and configure widgets
        table_editor = composerWrapper.itemDock().widget()
        if not table_editor is None:
            self._configure_table_editor_properties(table_editor)

        if not fromTemplate:
            table_item.setComposerMap(None)
            #Create data properties editor and it to the dock widget
            table_data_source_editor = ComposerTableDataSourceEditor(composerWrapper, table_item)
            stdmDock = composerWrapper.stdmItemDock()
            stdmDock.setWidget(table_data_source_editor)

            #Add widget to the composer wrapper widget mapping collection
            composerWrapper.addWidgetMapping(table_item.uuid(), table_data_source_editor)

        #Set ID to match UUID
        table_item.setId(table_item.uuid())

    def _configure_table_editor_properties(self, base_table_editor):
        qgis_version = QGis.QGIS_VERSION_INT

        #Get scroll area first
        scroll_area = base_table_editor.findChild(QScrollArea,"scrollArea")
        if not scroll_area is None:
            contents_widget = scroll_area.widget()

            main_properties_groupbox = contents_widget.findChild(QGroupBox, "groupBox")
            if not main_properties_groupbox is None:
                layer_lbl = main_properties_groupbox.findChild(QLabel, "mLayerLabel")
                if not layer_lbl is None:
                    layer_lbl.setVisible(False)

                layer_combo = main_properties_groupbox.findChild(QComboBox, "mLayerComboBox")
                if not layer_combo is None:
                    layer_combo.setVisible(False)

                refresh_btn = main_properties_groupbox.findChild(QPushButton, "mRefreshPushButton")
                if not refresh_btn is None:
                    refresh_btn.setVisible(False)

                #Version 2.4
                if qgis_version >= 20400 and qgis_version <= 20600:
                    self._hide_filter_controls(main_properties_groupbox)

            if qgis_version >= 20600:
                feature_filter_groupbox = contents_widget.findChild(QGroupBox, "groupBox_5")
                if not feature_filter_groupbox is None:
                    self._hide_filter_controls(feature_filter_groupbox)


    def _hide_filter_controls(self, groupbox):
        #Filter options
        filter_chk = groupbox.findChild(QCheckBox, "mFeatureFilterCheckBox")
        if not filter_chk is None:
            #Enable filter option if not enabled
            if not filter_chk.isChecked():
                filter_chk.setChecked(True)
            filter_chk.setVisible(False)

        txt_filter = groupbox.findChild(QLineEdit, "mFeatureFilterEdit")
        if not txt_filter is None:
            txt_filter.setVisible(False)

        filter_btn = groupbox.findChild(QToolButton, "mFeatureFilterButton")
        if not filter_btn is None:
            filter_btn.setVisible(False)

class ChartFormatter(PhotoFormatter):
    """
    Add widget for formatting composer picture items.
    """
    def apply(self, chart_item, composerWrapper, fromTemplate=False):
        if not isinstance(chart_item, QgsComposerPicture):
            return

        #Get the main picture editor widget and configure widgets
        picture_editor = composerWrapper.itemDock().widget()
        if not picture_editor is None:
            self._configure_picture_editor_properties(picture_editor)

        if not fromTemplate:
            #Disable outline in map composer item
            chart_item.setFrameEnabled(False)

            #Create data properties editor and it to the dock widget
            graph_config_editor = ComposerChartConfigEditor(composerWrapper)
            stdmDock = composerWrapper.stdmItemDock()
            stdmDock.setWidget(graph_config_editor)

            #Add widget to the composer wrapper widget mapping collection
            composerWrapper.addWidgetMapping(chart_item.uuid(), graph_config_editor)

        #Set default photo properties
        default_chart_pic = PLUGIN_DIR + "/images/icons/chart-512.png"
        if QFile.exists(default_chart_pic):
            chart_item.setPictureFile(default_chart_pic)

        #Set ID to match UUID
        chart_item.setId(chart_item.uuid())
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        

