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

        self.itemAction = self.action()
        self.itemAction.setCheckable(True)
        self.itemAction.triggered.connect(self.on_action_triggered)

        # Add action to toolbar and connect 'triggered' signal
        self._composerWrapper.stdmToolBar().addAction(self.itemAction)

    def action(self):
        """
        Specify QAction that will be associated with the configuration item.
        """
        raise NotImplementedError

    def on_action_triggered(self, state):
        """
        Slot raised upon action trigger.
        """
        pass

    def mainWindow(self):
        """
        Returns the QMainWindow used by the composer view.
        """
        return self._composerWrapper.mainWindow()

    def composerWrapper(self):
        """
        Returns an instance of the composer wrapper.
        """
        return self._composerWrapper

    @classmethod
    def register(cls):
        """
        Add subclasses to the collection of config items.
        """
        ComposerItemConfig.itemConfigurations.append(cls)


class SaveTemplateConfig(ComposerItemConfig):
    """
    For saving user templates.
    """

    CONFIG_ITEM = "SaveTemplate"

    def __init__(self, composerWrapper):
        ComposerItemConfig.__init__(self, composerWrapper)
        self.itemAction.setCheckable(False)
        count = self.itemAction.receivers(self.itemAction.triggered)

    def action(self):
        saveTemplateAct = QAction(GuiUtils.get_icon("save_tb.png"),
                                  QApplication.translate("SaveTemplateConfig", "Save document template"),
                                  self.mainWindow())

        return saveTemplateAct

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
    CONFIG_ITEM = "OpenTemplate"

    def action(self):
        openTemplateAct = QAction(GuiUtils.get_icon("open_file.png"),
                                  QApplication.translate("OpenTemplateConfig", "Open document template"),
                                  self.mainWindow())

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
    CONFIG_ITEM = "ManageTemplate"

    def __init__(self, composerWrapper):
        ComposerItemConfig.__init__(self, composerWrapper)
        self.itemAction.setCheckable(False)

    def action(self):
        manageTemplatesAct = QAction(GuiUtils.get_icon("manage_templates.png"),
                                     QApplication.translate("ManageTemplatesConfig", "Manage document templates"),
                                     self.mainWindow())

        return manageTemplatesAct

    def on_action_triggered(self, state):
        """
        Show dialog for managing document templates.
        """
        docManager = TemplateDocumentSelector(self.mainWindow(), False)
        docManager.exec_()


ManageTemplatesConfig.register()
