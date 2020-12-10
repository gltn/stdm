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
from qgis.PyQt.QtCore import (
    QObject
)
from qgis.PyQt.QtWidgets import (
    QAction,
    QApplication,
    QDialog
)
from qgis.core import QgsLayout
from qgis.gui import QgsLayoutView

from stdm.composer.item_formatter import (
    ChartFormatter,
    MapFormatter,
    PhotoFormatter,
    QRCodeFormatter,
    TableFormatter
)
from stdm.ui.composer.composer_doc_selector import (
    TemplateDocumentSelector
)
from stdm.ui.gui_utils import GuiUtils


class ComposerItemConfig(QObject):
    """
    Base class for custom configurations for QgsComposer.
    """
    itemConfigurations = []

    def __init__(self, composerWrapper):
        QObject.__init__(self, composerWrapper.mainWindow())
        self._composerWrapper = composerWrapper
        self._itemFormatter = None

        self.itemAction = self.action()
        self.itemAction.setCheckable(True)
        self.itemAction.triggered.connect(self.on_action_triggered)
        self.itemAction.toggled.connect(self.on_action_toggled)

        # Add action to toolbar and connect 'triggered' signal
        self._composerWrapper.stdmToolBar().addAction(self.itemAction)

        # Add action to the composer items action group
        if self._composerWrapper.selectMoveAction() is not None and self.registerInItemGroup():
            actionGroup = self._composerWrapper.selectMoveAction().actionGroup()
            actionGroup.addAction(self.itemAction)

        # Connect signals
        # self.composerView().actionFinished.connect(self.onActionFinished)

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

    def on_action_triggered(self, state):
        """
        Slot raised upon action trigger.
        """
        pass

    def on_action_toggled(self, checked):
        """
        Slot raised when checked status of the action changes.
        """
        pass

    def mainWindow(self):
        """
        Returns the QMainWindow used by the composer view.
        """
        return self._composerWrapper.mainWindow()

    def composerView(self) -> QgsLayoutView:
        """
        Returns the composer view.
        """
        return self._composerWrapper.composerView()

    def composition(self) -> QgsLayout:
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
        if self._composerWrapper.selectMoveAction() is not None:
            self._composerWrapper.selectMoveAction().setChecked(True)

    def onSelectItemChanged(self, selected):
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


class TableConfig(ComposerItemConfig):
    """
    Table composer item.
    """

    def __init__(self, composer_wrapper):
        ComposerItemConfig.__init__(self, composer_wrapper)
        self._itemFormatter = TableFormatter()

    def action(self):
        tb_act = QAction(GuiUtils.get_icon("composer_table.png"),
                         QApplication.translate("TableConfig", "Add attribute table"), self.mainWindow())

        return tb_act

    def on_action_triggered(self, state):
        self.composerView().setCurrentTool(QgsComposerView.AddAttributeTable)

    def on_action_toggled(self, checked):
        if checked:
            self.composition().selectedItemChanged.connect(self.onSelectItemChanged)
        else:
            self.composition().selectedItemChanged.disconnect(self.onSelectItemChanged)

    def onSelectItemChanged(self, selected):
        """
        We use this method since there seems to be an issue with QgsComposition not raising
        signals when new composer items are added in the composition.
        """
        sel_items = self.composition().selectedLayoutItems()
        if len(sel_items) == 0:
            return

        table_item = sel_items[0]
        self._itemFormatter.apply(table_item, self.composerWrapper())


class MapConfig(ComposerItemConfig):
    """
    Enables users to add a map into the composition as well as define styling for spatial
    data sources.
    """

    def __init__(self, composerWrapper):
        ComposerItemConfig.__init__(self, composerWrapper)
        self._itemFormatter = MapFormatter()

    def action(self):
        mapAct = QAction(GuiUtils.get_icon("add_map.png"),
                         QApplication.translate("MapConfig", "Add map"), self.mainWindow())

        return mapAct

    def on_action_triggered(self, state):
        self.composerView().setCurrentTool(QgsComposerView.AddMap)

    def on_action_toggled(self, checked):
        if checked:
            self.composition().selectedItemChanged.connect(self.onSelectItemChanged)

        else:
            self.composition().selectedItemChanged.disconnect(self.onSelectItemChanged)

    def onSelectItemChanged(self, selected):
        """
        We use this method since there seems to be an issue with QgsComposition not raising
        signals when new composer items are added in the composition.
        """
        selItems = self.composition().selectedLayoutItems()
        if len(selItems) == 0:
            return

        templateMap = selItems[0]
        self._itemFormatter.apply(templateMap, self.composerWrapper())


class PhotoConfig(ComposerItemConfig):
    """
    Photo composer item based on type.
    """

    def __init__(self, composerWrapper):
        ComposerItemConfig.__init__(self, composerWrapper)
        self._itemFormatter = PhotoFormatter()

    def action(self):
        ph_act = QAction(GuiUtils.get_icon("photo_24.png"),
                         QApplication.translate("PhotoConfig", "Add photo"), self.mainWindow())

        return ph_act

    def on_action_triggered(self, state):
        self.composerView().setCurrentTool(QgsComposerView.AddPicture)

    def on_action_toggled(self, checked):
        if checked:
            self.composition().selectedItemChanged.connect(self.onSelectItemChanged)

        else:
            self.composition().selectedItemChanged.disconnect(self.onSelectItemChanged)

    def onSelectItemChanged(self, selected):
        """
        We use this method since there seems to be an issue with QgsComposition not raising
        signals when new composer items are added in the composition.
        """
        sel_items = self.composition().selectedLayoutItems()
        if len(sel_items) == 0:
            return

        photo_item = sel_items[0]
        self._itemFormatter.apply(photo_item, self.composerWrapper())


class ChartConfig(ComposerItemConfig):
    """
    Chart composer item which uses the QgsComposerPicture item for
    rendering graphs outputted as images.
    """

    def __init__(self, composerWrapper):
        ComposerItemConfig.__init__(self, composerWrapper)
        self._itemFormatter = ChartFormatter()

    def action(self):
        chart_act = QAction(GuiUtils.get_icon("chart.png"),
                            QApplication.translate("ChartConfig", "Add chart"), self.mainWindow())

        return chart_act

    def on_action_triggered(self, state):
        self.composerView().setCurrentTool(QgsComposerView.AddPicture)

    def on_action_toggled(self, checked):
        if checked:
            self.composition().selectedItemChanged.connect(self.onSelectItemChanged)

        else:
            self.composition().selectedItemChanged.disconnect(self.onSelectItemChanged)

    def onSelectItemChanged(self, selected):
        """
        We use this method since there seems to be an issue with QgsComposition not raising
        signals when new composer items are added in the composition.
        """
        sel_items = self.composition().selectedLayoutItems()
        if len(sel_items) == 0:
            return

        chart_item = sel_items[0]
        self._itemFormatter.apply(chart_item, self.composerWrapper())


class QRCodeConfig(PhotoConfig):
    """Composer item for QR codes."""

    def __init__(self, composerWrapper):
        ComposerItemConfig.__init__(self, composerWrapper)
        self._itemFormatter = QRCodeFormatter()

    def action(self):
        qrcode_act = QAction(GuiUtils.get_icon("qrcode.png"),
                             QApplication.translate("QRCodeConfig", "Add QR Code"), self.mainWindow())

        return qrcode_act


class SaveTemplateConfig(ComposerItemConfig):
    """
    For saving user templates.
    """

    def __init__(self, composerWrapper):
        ComposerItemConfig.__init__(self, composerWrapper)
        self.itemAction.setCheckable(False)

    def action(self):
        saveTemplateAct = QAction(GuiUtils.get_icon("save_tb.png"),
                                  QApplication.translate("SaveTemplateConfig", "Save document template"),
                                  self.composerView())

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
        openTemplateAct = QAction(GuiUtils.get_icon("open_file.png"),
                                  QApplication.translate("OpenTemplateConfig", "Open document template"),
                                  self.composerView())

        return openTemplateAct

    def on_action_triggered(self, state):
        """
        Load template document selector dialog then process selection.
        """
        docSelector = TemplateDocumentSelector(self.mainWindow())

        if docSelector.exec_() == QDialog.Accepted:
            docName, file_path = docSelector.documentMapping()

            self.composerWrapper().create_new_document_designer(file_path)


OpenTemplateConfig.register()


class ManageTemplatesConfig(ComposerItemConfig):
    """
    Action that loads dialog for managing user document templates.
    """

    def __init__(self, composerWrapper):
        ComposerItemConfig.__init__(self, composerWrapper)
        self.itemAction.setCheckable(False)

    def action(self):
        manageTemplatesAct = QAction(GuiUtils.get_icon("manage_templates.png"),
                                     QApplication.translate("ManageTemplatesConfig", "Manage document templates"),
                                     self.mainWindow())

        return manageTemplatesAct

    def registerInItemGroup(self):
        return False

    def on_action_triggered(self, state):
        """
        Show dialog for managing document templates.
        """
        docManager = TemplateDocumentSelector(self.mainWindow(), False)
        docManager.exec_()


ManageTemplatesConfig.register()
