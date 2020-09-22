"""
/***************************************************************************
Name                 : Custom STDM composer configuration tools.
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
from PyQt4.QtCore import (
    QObject
)
from PyQt4.QtGui import (
    QAction,
    QIcon,
    QApplication,
    QDialog
)

from qgis.gui import QgsComposerView

from stdm import (
    TemplateDocumentSelector
)

from .item_formatter import (
    ChartFormatter,
    DataLabelFormatter,
    LineFormatter,
    MapFormatter,
    PhotoFormatter,
    QRCodeFormatter,
    TableFormatter
 )

class ComposerItemConfig(QObject):
    """
    Base class for custom configurations for QgsComposer.
    """
    itemConfigurations = []

    def __init__(self,composerWrapper):
        QObject.__init__(self,composerWrapper.composerView())
        self._composerWrapper = composerWrapper
        self._itemFormatter = None

        self.itemAction = self.action()
        self.itemAction.setCheckable(True)
        self.itemAction.triggered.connect(self.on_action_triggered)
        self.itemAction.toggled.connect(self.on_action_toggled)

        #Add action to toolbar and connect 'triggered' signal
        self._composerWrapper.stdmToolBar().addAction(self.itemAction)

        #Add action to the composer items action group
        if self._composerWrapper.selectMoveAction() != None and self.registerInItemGroup():
            actionGroup = self._composerWrapper.selectMoveAction().actionGroup()
            actionGroup.addAction(self.itemAction)

        #Connect signals
        self.composerView().actionFinished.connect(self.onActionFinished)

    def action(self):
        """
        Specify QAction that will be associated with the configuration item.
        """
        raise NotImplementedError

    def registerInItemGroup(self):
        """
        Returns whether the action associated with this config should be registered in the item group
        for adding composer items.
        """
        return True

    def on_action_triggered(self,state):
        """
        Slot raised upon action trigger.
        """
        pass

    def on_action_toggled(self,checked):
        """
        Slot raised when checked status of the action changes.
        """
        pass

    def mainWindow(self):
        """
        Returns the QMainWindow used by the composer view.
        """
        return self._composerWrapper.mainWindow()

    def composerView(self):
        """
        Returns the composer view.
        """
        return self._composerWrapper.composerView()

    def composition(self):
        """
        Returns the QgsComposition instance.
        """
        return self._composerWrapper.composition()

    def composerWrapper(self):
        """
        Returns an instance of the composer wrapper.
        """
        return self._composerWrapper

    def itemFormatter(self):
        """
        Returns the formatter configured for the item configuration.
        """
        return self._itemFormatter

    def onActionFinished(self):
        """
        Slot raised when the specified action has finished drawing in the composition.
        This checks the default move/select action and uncheck the QAction for the
        current configuration item.
        """
        self.itemAction.setChecked(False)
        if self._composerWrapper.selectMoveAction() != None:
            self._composerWrapper.selectMoveAction().setChecked(True)

    def onSelectItemChanged(self,selected):
        """
        Slot raised when selection changes.
        """
        pass

    @classmethod
    def register(cls):
        """
        Add subclasses to the collection of config items.
        """
        ComposerItemConfig.itemConfigurations.append(cls)

class LineItemConfig(ComposerItemConfig):
    """
    For drawing lines in the composition. This uses the arrow composer item as the base.
    """
    def __init__(self,composerWrapper):
        ComposerItemConfig.__init__(self, composerWrapper)
        self._itemFormatter = LineFormatter()

    def action(self):
        lineAct = QAction(QIcon(":/plugins/stdm/images/icons/line.png"), \
        QApplication.translate("LineItemConfig","Add line"), self.composerView())

        return lineAct

    def on_action_triggered(self,state):
        self.composerView().setCurrentTool(QgsComposerView.AddArrow)

    def on_action_toggled(self, checked):
        if checked:
            self.composerView().selectedItemChanged.connect(self.onSelectItemChanged)

        else:
            self.composerView().selectedItemChanged.disconnect(self.onSelectItemChanged)

    def onSelectItemChanged(self, selected):
        """
        We use this method since there seems to be an issue with QgsComposition not raising
        signals when new composer items are added in the composition.
        """
        selItems = self.composition().selectedComposerItems()
        if len(selItems) == 0:
            return

        arrow = selItems[0]
        self._itemFormatter.apply(arrow,self.composerWrapper())

LineItemConfig.register()

class DataLabelConfig(ComposerItemConfig):
    """
    Enables users to define values for QgsComposerLabels from database sources.
    """
    def __init__(self,composerWrapper):
        ComposerItemConfig.__init__(self, composerWrapper)
        self._itemFormatter = DataLabelFormatter()

    def action(self):
        dataLabelAct = QAction(QIcon(":/plugins/stdm/images/icons/db_field.png"), \
        QApplication.translate("DataLabelConfig","Add data label"), self.composerView())

        return dataLabelAct

    def on_action_triggered(self, state):
        self.composerView().setCurrentTool(QgsComposerView.AddLabel)

    def on_action_toggled(self, checked):
        if checked:
            self.composerView().selectedItemChanged.connect(self.onSelectItemChanged)

        else:
            self.composerView().selectedItemChanged.disconnect(self.onSelectItemChanged)

    def onSelectItemChanged(self, selected):
        """
        We use this method since there seems to be an issue with QgsComposition not raising
        signals when new composer items are added in the composition.
        """
        selItems = self.composition().selectedComposerItems()
        if len(selItems) == 0:
            return

        label = selItems[0]
        self._itemFormatter.apply(label,self.composerWrapper())

DataLabelConfig.register()

class TableConfig(ComposerItemConfig):
    """
    Table composer item.
    """
    def __init__(self, composer_wrapper):
        ComposerItemConfig.__init__(self, composer_wrapper)
        self._itemFormatter = TableFormatter()

    def action(self):
        tb_act = QAction(QIcon(":/plugins/stdm/images/icons/composer_table.png"), \
        QApplication.translate("TableConfig","Add attribute table"), self.composerView())

        return tb_act

    def on_action_triggered(self, state):
        self.composerView().setCurrentTool(QgsComposerView.AddAttributeTable)

    def on_action_toggled(self, checked):
        if checked:
            self.composerView().selectedItemChanged.connect(self.onSelectItemChanged)
        else:
            self.composerView().selectedItemChanged.disconnect(self.onSelectItemChanged)

    def onSelectItemChanged(self, selected):
        """
        We use this method since there seems to be an issue with QgsComposition not raising
        signals when new composer items are added in the composition.
        """
        sel_items = self.composition().selectedComposerItems()
        if len(sel_items) == 0:
            return

        table_item = sel_items[0]
        self._itemFormatter.apply(table_item, self.composerWrapper())


TableConfig.register()

class MapConfig(ComposerItemConfig):
    """
    Enables users to add a map into the composition as well as define styling for spatial
    data sources.
    """
    def __init__(self,composerWrapper):
        ComposerItemConfig.__init__(self, composerWrapper)
        self._itemFormatter = MapFormatter()

    def action(self):
        mapAct = QAction(QIcon(":/plugins/stdm/images/icons/add_map.png"), \
        QApplication.translate("MapConfig","Add map"), self.composerView())

        return mapAct

    def on_action_triggered(self, state):
        self.composerView().setCurrentTool(QgsComposerView.AddMap)

    def on_action_toggled(self, checked):
        if checked:
            self.composerView().selectedItemChanged.connect(self.onSelectItemChanged)

        else:
            self.composerView().selectedItemChanged.disconnect(self.onSelectItemChanged)

    def onSelectItemChanged(self, selected):
        """
        We use this method since there seems to be an issue with QgsComposition not raising
        signals when new composer items are added in the composition.
        """
        selItems = self.composition().selectedComposerItems()
        if len(selItems) == 0:
            return

        templateMap = selItems[0]
        self._itemFormatter.apply(templateMap,self.composerWrapper())

MapConfig.register()

class PhotoConfig(ComposerItemConfig):
    """
    Photo composer item based on type.
    """
    def __init__(self,composerWrapper):
        ComposerItemConfig.__init__(self, composerWrapper)
        self._itemFormatter = PhotoFormatter()

    def action(self):
        ph_act = QAction(QIcon(":/plugins/stdm/images/icons/photo_24.png"), \
        QApplication.translate("PhotoConfig","Add photo"), self.composerView())

        return ph_act

    def on_action_triggered(self, state):
        self.composerView().setCurrentTool(QgsComposerView.AddPicture)

    def on_action_toggled(self, checked):
        if checked:
            self.composerView().selectedItemChanged.connect(self.onSelectItemChanged)

        else:
            self.composerView().selectedItemChanged.disconnect(self.onSelectItemChanged)

    def onSelectItemChanged(self, selected):
        """
        We use this method since there seems to be an issue with QgsComposition not raising
        signals when new composer items are added in the composition.
        """
        sel_items = self.composition().selectedComposerItems()
        if len(sel_items) == 0:
            return

        photo_item = sel_items[0]
        self._itemFormatter.apply(photo_item, self.composerWrapper())

PhotoConfig.register()


class ChartConfig(ComposerItemConfig):
    """
    Chart composer item which uses the QgsComposerPicture item for
    rendering graphs outputted as images.
    """
    def __init__(self,composerWrapper):
        ComposerItemConfig.__init__(self, composerWrapper)
        self._itemFormatter = ChartFormatter()

    def action(self):
        chart_act = QAction(QIcon(":/plugins/stdm/images/icons/chart.png"), \
        QApplication.translate("ChartConfig","Add chart"), self.composerView())

        return chart_act

    def on_action_triggered(self, state):
        self.composerView().setCurrentTool(QgsComposerView.AddPicture)

    def on_action_toggled(self, checked):
        if checked:
            self.composerView().selectedItemChanged.connect(self.onSelectItemChanged)

        else:
            self.composerView().selectedItemChanged.disconnect(self.onSelectItemChanged)

    def onSelectItemChanged(self, selected):
        """
        We use this method since there seems to be an issue with QgsComposition not raising
        signals when new composer items are added in the composition.
        """
        sel_items = self.composition().selectedComposerItems()
        if len(sel_items) == 0:
            return

        chart_item = sel_items[0]
        self._itemFormatter.apply(chart_item, self.composerWrapper())


ChartConfig.register()


class QRCodeConfig(PhotoConfig):
    """Composer item for QR codes."""
    def __init__(self,composerWrapper):
        ComposerItemConfig.__init__(self, composerWrapper)
        self._itemFormatter = QRCodeFormatter()

    def action(self):
        qrcode_act = QAction(QIcon(":/plugins/stdm/images/icons/qrcode.png"), \
        QApplication.translate("QRCodeConfig","Add QR Code"), self.composerView())

        return qrcode_act


QRCodeConfig.register()


class SeparatorConfig(ComposerItemConfig):
    """
    Simple toolbar separator.
    """
    def __init__(self,composerWrapper):
        ComposerItemConfig.__init__(self, composerWrapper)

    def action(self):
        separatorAct = QAction(self.composerView())
        separatorAct.setSeparator(True)

        return separatorAct

    def registerInItemGroup(self):
        return False

SeparatorConfig.register()

class SaveTemplateConfig(ComposerItemConfig):
    """
    For saving user templates.
    """
    def __init__(self,composerWrapper):
        ComposerItemConfig.__init__(self, composerWrapper)
        self.itemAction.setCheckable(False)

    def action(self):
        saveTemplateAct = QAction(QIcon(":/plugins/stdm/images/icons/save_tb.png"), \
        QApplication.translate("SaveTemplateConfig","Save document template"), self.composerView())

        return saveTemplateAct

    def registerInItemGroup(self):
        return False

    def on_action_triggered(self, state):
        """
        Save document template.
        """
        self.composerWrapper().saveTemplate()

SaveTemplateConfig.register()

class OpenTemplateConfig(SaveTemplateConfig):
    """
    Opens user templates.
    """
    def action(self):
        openTemplateAct = QAction(QIcon(":/plugins/stdm/images/icons/open_file.png"), \
        QApplication.translate("OpenTemplateConfig","Open document template"), self.composerView())

        return openTemplateAct

    def on_action_triggered(self, state):
        """
        Load template document selector dialog then process selection.
        """
        docSelector = TemplateDocumentSelector(self.composerView())

        if docSelector.exec_() == QDialog.Accepted:
            docName, file_path = docSelector.documentMapping()

            self.composerWrapper().create_new_document_designer(file_path)

OpenTemplateConfig.register()

class ManageTemplatesConfig(ComposerItemConfig):
    """
    Action that loads dialog for managing user document templates.
    """
    def __init__(self,composerWrapper):
        ComposerItemConfig.__init__(self, composerWrapper)
        self.itemAction.setCheckable(False)

    def action(self):
        manageTemplatesAct = QAction(QIcon(":/plugins/stdm/images/icons/manage_templates.png"), \
        QApplication.translate("ManageTemplatesConfig","Manage document templates"), self.composerView())

        return manageTemplatesAct

    def registerInItemGroup(self):
        return False

    def on_action_triggered(self, state):
        """
        Show dialog for managing document templates.
        """
        docManager = TemplateDocumentSelector(self.composerView(),False)
        docManager.exec_()

ManageTemplatesConfig.register()


