"""
/***************************************************************************
Name                 : Document Generator By Person
Description          : Dialog that enables a user to generate documents by
                       using person information.
Date                 : 21/May/2014
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
import logging
import os
import subprocess
import sys
from collections import OrderedDict

from qgis.PyQt import uic
from qgis.PyQt.QtCore import (
    Qt,
    QFileInfo,
    QTimer
)
from qgis.PyQt.QtGui import (
    QCursor,
    QImageWriter
)
from qgis.PyQt.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QApplication,
    QProgressDialog,
    QProgressBar,
    QMessageBox,
    QFileDialog,
    QTableView
)

from sqlalchemy.exc import SQLAlchemyError

from stdm.exceptions import DummyException
from stdm.composer.document_generator import DocumentGenerator
from stdm.data.configuration import entity_model
from stdm.settings import current_profile
from stdm.settings.registryconfig import (
    RegistryConfig,
    COMPOSER_OUTPUT
)
from stdm.ui.composer.composer_doc_selector import TemplateDocumentSelector
from stdm.ui.foreign_key_mapper import ForeignKeyMapper
from stdm.ui.gui_utils import GuiUtils
from stdm.ui.notification import NotificationBar
from stdm.ui.sourcedocument import (
    source_document_location,
    output_document_location
)
from stdm.utils.util import (
    format_name,
    entity_display_columns,
    enable_drag_sort,
    profile_entities
)

__all__ = ["DocumentGeneratorDialog", "EntityConfig"]

LOGGER = logging.getLogger('stdm')


class EntityConfig(object):
    """
    Configuration class for specifying
    the foreign key mapper and document
    generator settings.
    """

    def __init__(self, **kwargs):
        self._title = kwargs.pop("title", "")
        self._link_field = kwargs.pop("link_field", "")
        self._display_formatters = kwargs.pop("formatters", OrderedDict())

        self._data_source = kwargs.pop("data_source", "")
        self._ds_columns = []
        self.curr_profile = current_profile()
        self.ds_entity = self.curr_profile.entity_by_name(self._data_source)

        self._set_ds_columns()

        self._base_model = kwargs.pop("model", None)
        self._entity_selector = kwargs.pop("entity_selector", None)
        self._expression_builder = kwargs.pop("expression_builder", False)

    def title(self):
        return self._title

    def set_title(self, title):
        self._title = title

    def _set_ds_columns(self):
        if not self._data_source:
            self._ds_columns = []

        else:
            self._ds_columns = entity_display_columns(
                self.ds_entity
            )

    def model(self):
        return self._base_model

    def data_source(self) -> str:
        return self._data_source

    def data_source_columns(self):
        """
        Please note that these are only those columns of numeric or
        character type variants.
        """
        return self._ds_columns

    def set_data_source(self, ds):
        self._data_source = ds
        self._set_ds_columns()

    def entity_selector(self):
        return self._entity_selector

    def set_entity_selector(self, selector):
        self._entity_selector = selector

    def expression_builder(self):
        return self._expression_builder

    def set_expression_builder(self, state):
        self._expression_builder = state

    def formatters(self):
        return self._display_formatters

    def set_formatters(self, formatters):
        self._display_formatters = formatters

    def link_field(self):
        return self._link_field

    def set_link_field(self, field):
        self._link_field = field


class DocumentGeneratorDialogWrapper(object):
    """
    A utility class that fetches the tables in the active profile
    and creates the corresponding EntityConfig objects, which are then
    added to the DocumentGeneratorDialog.
    """

    def __init__(self, iface, access_templates, parent=None, plugin=None):
        self._iface = iface
        self._plugin = plugin

        self._doc_gen_dlg = DocumentGeneratorDialog(self._iface, access_templates, parent, plugin=plugin)
        self._notif_bar = self._doc_gen_dlg.notification_bar()

        self.curr_profile = current_profile()
        # Load entity configurations
        self._load_entity_configurations()

        self.access_templates = access_templates

    def _load_entity_configurations(self):
        """
        Uses tables' information in the current profile to create the
        corresponding EntityConfig objects.
        """
        try:
            entities = profile_entities(self.curr_profile)
            self._doc_gen_dlg.progress.setRange(0, len(entities) - 1)

            for i, t in enumerate(entities):
                QApplication.processEvents()
                # Exclude custom tenure entities
                if 'check' in t.name:
                    continue
                entity_cfg = self._entity_config_from_profile(
                    str(t.name), t.short_name
                )

                if entity_cfg is not None:
                    self._doc_gen_dlg.add_entity_config(entity_cfg, i)
            self._doc_gen_dlg.progress.hide()

            ########
            # TEST
            #######
            # self._doc_gen_dlg.tabWidget.setCurrentIndex(1)
            # fk_mapper = self._doc_gen_dlg.tabWidget.widget(1)
            # fk_mapper.onAddEntity()
            # fk_mapper._onRecordSelectedEntityBrowser(2, -1)
            # fk_mapper.entitySelector().onAccept()
            # fk_mapper.test_close_selector()
            # doc_name = 'household'
            # doc_path = 'C:/Users/Administrator/.stdm/reports/templates/Chart01.sdt'
            # self._docTemplatePath = doc_path
            # self._plugin.action_cache['prev_document_template_name'] = doc_name
            # self._plugin.action_cache['prev_document_template_path'] = doc_path
            # self._doc_gen_dlg.onGenerate()
            # fk_mapper.entitySelector().done(1)
            ########
            # TEST
            #######

        except DummyException as pe:
            self._notif_bar.clear()
            self._notif_bar.insertErrorNotification(str(pe))

    def _entity_config_from_profile(self, table_name, short_name):
        """
        Creates an EntityConfig object from the table name.
        :param table_name: Name of the database table.
        :type table_name: str
        :return: Entity configuration object.
        :rtype: EntityConfig
        """
        table_display_name = format_name(short_name)
        self.ds_entity = self.curr_profile.entity_by_name(table_name)

        model = entity_model(self.ds_entity)

        if model is not None:
            return EntityConfig(title=table_display_name,
                                data_source=table_name,
                                model=model,
                                expression_builder=True,
                                entity_selector=None)

        else:
            return None

    def dialog(self) -> 'DocumentGeneratorDialog':
        """
        :return: Returns an instance of the DocumentGeneratorDialog.
        :rtype: DocumentGeneratorDialog
        """
        return self._doc_gen_dlg

    def exec_(self) -> int:
        """
        Show the dialog as a modal dialog.
        :return: DialogCode result
        :rtype: int
        """
        return self._doc_gen_dlg.exec_()


WIDGET, BASE = uic.loadUiType(
    GuiUtils.get_ui_file_path('ui_doc_generator.ui'))


class DocumentGeneratorDialog(WIDGET, BASE):
    """
    Dialog that enables a user to generate documents by using configuration
    information for different entities.
    """

    def __init__(self, iface, access_templates, parent=None, plugin=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.btnSelectTemplate.setIcon(GuiUtils.get_icon('document.png'))

        self._iface = iface
        self.plugin = plugin
        self._docTemplatePath = ""
        self._outputFilePath = ""
        self.curr_profile = current_profile()
        self.last_data_source = None
        self._config_mapping = OrderedDict()

        self._notif_bar = NotificationBar(self.vlNotification)

        self._doc_generator = DocumentGenerator(self._iface, self)

        self._data_source = ""

        self.access_templates = access_templates

        enable_drag_sort(self.lstDocNaming)

        # Configure generate button
        generateBtn = self.buttonBox.button(QDialogButtonBox.Ok)
        if not generateBtn is None:
            generateBtn.setText(QApplication.translate("DocumentGeneratorDialog",
                                                       "Generate"))

        # Load supported image types
        supportedImageTypes = QImageWriter.supportedImageFormats()
        for imageType in supportedImageTypes:
            imageTypeStr = imageType.data().decode()
            self.cboImageType.addItem(imageTypeStr)

        self._init_progress_dialog()
        # Connect signals
        self.btnSelectTemplate.clicked.connect(self.onSelectTemplate)
        self.buttonBox.accepted.connect(self.onGenerate)
        self.chkUseOutputFolder.stateChanged.connect(self.onToggledOutputFolder)
        self.rbExpImage.toggled.connect(self.onToggleExportImage)
        self.tabWidget.currentChanged.connect(self.on_tab_index_changed)
        self.chk_template_datasource.stateChanged.connect(self.on_use_template_datasource)

        self.btnShowOutputFolder.clicked.connect(self.onShowOutputFolder)

        prev_doc_path = self.plugin.action_cache.get('prev_document_template_path', "")
        prev_doc_name = self.plugin.action_cache.get('prev_document_template_name', "")
        self.lblTemplateName.setText(prev_doc_name)
        self._docTemplatePath = prev_doc_path
        self.datasource_fields_loaded = False

        self.onToggleExportImage(False)

    def _init_progress_dialog(self):
        """
        Initializes the progress dialog.
        """
        self.progress = QProgressBar(self)
        self.progress.resize(self.width(), 10)
        self.progress.setTextVisible(False)

    def add_entity_configuration(self, **kwargs):
        ent_config = EntityConfig(**kwargs)
        self.add_entity_config(ent_config)

    def add_entity_config(self, ent_config, progress_value=0):
        QApplication.processEvents()
        if not self._config_mapping.get(ent_config.title(), ""):
            fk_mapper = self._create_fk_mapper(ent_config)
            self.tabWidget.addTab(fk_mapper, ent_config.title())
            self._config_mapping[ent_config.title()] = ent_config

            # Force list of column names to be loaded
            if self.tabWidget.currentIndex() != 0:
                self.tabWidget.setCurrentIndex(0)

            else:
                self.on_tab_index_changed(0)

        self.progress.setValue(progress_value)

    def on_tab_index_changed(self, index):
        if index == -1:
            return

        config = self.config(index)

        if not config is None:
            # Set data source name
            self._data_source = config.data_source()

    def on_use_template_datasource(self, state):
        if state == Qt.Checked:
            self.tabWidget.setEnabled(False)
            self.chkUseOutputFolder.setEnabled(False)
            self.chkUseOutputFolder.setChecked(False)

        elif state == Qt.Unchecked:
            self.tabWidget.setEnabled(True)
            self.chkUseOutputFolder.setEnabled(True)
            self.chkUseOutputFolder.setChecked(False)
            self.on_tab_index_changed(self.tabWidget.currentIndex())

    def onShowOutputFolder(self):
        reg_config = RegistryConfig()
        path = reg_config.read([COMPOSER_OUTPUT])
        output_path = path.get(COMPOSER_OUTPUT, '')

        # windows
        if sys.platform.startswith('win32'):
            os.startfile(output_path)

        # *nix systems
        if sys.platform.startswith('linux'):
            subprocess.Popen(['xdg-open', output_path])

        # macOS
        if sys.platform.startswith('darwin'):
            subprocess.Popen(['open', output_path])

    def notification_bar(self):
        """
        :return: Returns an instance of the notification bar.
        :rtype: NotificationBar
        """
        return self._notif_bar

    def config(self, index):
        """
        Returns the configuration for the current mapper in the tab widget.
        """
        tab_key = self.tabWidget.tabText(index)

        return self._config_mapping.get(tab_key, None)

    def current_config(self):
        """
        Returns the configuration corresponding to the current widget in the
        tab.
        """
        return self.config(self.tabWidget.currentIndex())

    def _load_model_columns(self, config):
        """
        Load model columns into the view for specifying file output name.
        Only those columns of display type variants will be
        used.
        """
        model_attr_mapping = OrderedDict()

        for c in config.data_source_columns():
            model_attr_mapping[c] = format_name(c)

        self.lstDocNaming.load_mapping(model_attr_mapping)

    def _load_data_source_columns(self, entity):
        """
        Load the columns of a data source for use in the file naming.
        """
        table_cols = entity_display_columns(entity, True)

        attr_mapping = OrderedDict()

        for c, header in table_cols.items():
            attr_mapping[c] = header

        self.lstDocNaming.load_mapping(attr_mapping)

    def _create_fk_mapper(self, config):
        fk_mapper = ForeignKeyMapper(
            config.ds_entity,
            self.tabWidget,
            self._notif_bar,
            enable_list=True,
            can_filter=True,
            plugin=self.plugin
        )

        fk_mapper.setDatabaseModel(config.model())
        fk_mapper.setSupportsList(True)
        fk_mapper.setDeleteonRemove(False)
        fk_mapper.setNotificationBar(self._notif_bar)

        return fk_mapper

    def onSelectTemplate(self):
        """
        Slot raised to load the template selector dialog.
        """
        current_config = self.current_config()
        if current_config is None:
            msg = QApplication.translate(
                'DocumentGeneratorDialog',
                'An error occured while trying to determine the data source '
                'for the current entity.\nPlease check your current profile '
                'settings.'
            )
            QMessageBox.critical(
                self,
                QApplication.translate(
                    'DocumentGeneratorDialog',
                    'Template Selector'
                ),
                msg
            )
            return

        # Set the template selector to only load those templates that
        # reference the current data source.
        filter_table = current_config.data_source()
        templateSelector = TemplateDocumentSelector(
            self,
            filter_data_source=filter_table,
            access_templates=self.access_templates
        )

        if templateSelector.exec_() == QDialog.Accepted:
            docName, docPath = templateSelector.documentMapping()

            self.lblTemplateName.setText(docName)
            self._docTemplatePath = docPath
            # Cache this selection
            self.plugin.action_cache['prev_document_template_name'] = docName
            self.plugin.action_cache['prev_document_template_path'] = docPath

            if filter_table != self.last_data_source:
                # Load template data source fields
                self._load_template_datasource_fields()
                self.datasource_fields_loaded = True

    def _load_template_datasource_fields(self):
        # If using template data source
        template_doc, err_msg = self._doc_generator.template_document(self._docTemplatePath)
        if template_doc is None:
            QMessageBox.critical(self, "Error Generating documents", QApplication.translate("DocumentGeneratorDialog",
                                                                                            "Error Generating documents - %s" % (
                                                                                                err_msg)))

            return

        composer_ds, err_msg = self._doc_generator.composer_data_source(template_doc)

        if composer_ds is None:
            QMessageBox.critical(self, "Error Generating documents", QApplication.translate("DocumentGeneratorDialog",
                                                                                            "Error Generating documents - %s" % (
                                                                                                err_msg)))

            return

        # Load data source columns
        self._data_source = self.current_config().data_source()

        self.ds_entity = self.curr_profile.entity_by_name(
            self._data_source
        )

        self._load_data_source_columns(self.ds_entity)

    def onToggledOutputFolder(self, state):
        """
        Slot raised to enable/disable the generated output documents to be
        written to the plugin composer output folder using the specified
        naming convention.
        """
        if state == Qt.Checked:
            self.gbDocNaming.setEnabled(True)

        elif state == Qt.Unchecked:
            self.gbDocNaming.setEnabled(False)

    def reset(self, success_status=False):
        """
        Clears/resets the dialog from user-defined options.
        """
        self._docTemplatePath = ""
        self._data_source = ""

        self.datasource_fields_loaded = False

        #self.lblTemplateName.setText("")
        # reset form only if generation is successful
        if success_status:
            fk_table_view = self.tabWidget.currentWidget(). \
                findChild(QTableView)
            while fk_table_view.model().rowCount() > 0:
                fk_table_view.model().rowCount(0)
                fk_table_view.model().removeRow(0)

            if self.tabWidget.count() > 0 and \
                    not self.chk_template_datasource.isChecked():
                self.on_tab_index_changed(0)

            if self.cboImageType.count() > 0:
                self.cboImageType.setCurrentIndex(0)

    def onToggleExportImage(self, state: bool):
        """
        Slot raised to enable/disable the image formats combobox.
        """
        self.cboImageType.setEnabled(state)

    def onGenerate(self):
        """
        Slot raised to initiate the certificate generation process.
        """
        self._notif_bar.clear()
        success_status = True

        config = self.current_config()
        self._docTemplatePath = self.plugin.action_cache.get('prev_document_template_path', "")

        self.last_data_source = config.data_source()
        if config is None:
            self._notif_bar.insertErrorNotification(QApplication.translate("DocumentGeneratorDialog", \
                                                                           "The entity configuration could not be extracted."))
            return

        # Get selected records and validate
        records = self.tabWidget.currentWidget().entities()

        if self.chk_template_datasource.isChecked():
            records = self._dummy_template_records()

        if len(records) == 0:
            self._notif_bar.insertErrorNotification(QApplication.translate("DocumentGeneratorDialog", \
                                                                           "Please load at least one entity record"))
            return

        if not self._docTemplatePath:
            self._notif_bar.insertErrorNotification(QApplication.translate("DocumentGeneratorDialog", \
                                                                           "Please select a document template to use"))
            return

        documentNamingAttrs = self.lstDocNaming.selectedMappings()

        if self.chkUseOutputFolder.checkState() == Qt.Checked and len(documentNamingAttrs) == 0:
            self._notif_bar.insertErrorNotification(QApplication.translate("DocumentGeneratorDialog", \
                                                                           "Please select at least one field for naming the output document"))
            return

        # Set output file properties
        if self.rbExpImage.isChecked():
            outputMode = DocumentGenerator.Image
            fileExtension = self.cboImageType.currentText()
            saveAsText = "Image File"
        else:
            outputMode = DocumentGenerator.PDF
            fileExtension = "pdf"
            saveAsText = "PDF File"

        # Show save file dialog if not using output folder
        if self.chkUseOutputFolder.checkState() == Qt.Unchecked:
            docDir = output_document_location()

            if self._outputFilePath:
                fileInfo = QFileInfo(self._outputFilePath)
                docDir = fileInfo.dir().path()

            self._outputFilePath, _ = QFileDialog.getSaveFileName(self,
                                                                  QApplication.translate("DocumentGeneratorDialog",
                                                                                         "Save Document"),
                                                                  docDir,
                                                                  "{0} (*.{1})".format(
                                                                      QApplication.translate("DocumentGeneratorDialog",
                                                                                             saveAsText),
                                                                      fileExtension))

            if not self._outputFilePath:
                self._notif_bar.insertErrorNotification(
                    QApplication.translate("DocumentGeneratorDialog",
                                           "Process aborted. No output file was specified."))

                return

            # Include extension in file name
            self._outputFilePath = self._outputFilePath  # + "." + fileExtension

        # else:
        # Multiple files to be generated.
        # pass

        if not self.datasource_fields_loaded:
            self._load_template_datasource_fields()

        self._doc_generator.set_link_field(config.link_field())

        self._doc_generator.clear_attr_value_formatters()

        if not self.chk_template_datasource.isChecked():
            # Apply cell formatters for naming output files
            self._doc_generator.set_attr_value_formatters(config.formatters())

        entity_field_name = "id"

        # Iterate through the selected records
        progressDlg = QProgressDialog(self)
        progressDlg.setMaximum(len(records))


        try:
            QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))

            for i, record in enumerate(records):
                progressDlg.setValue(i)

                if progressDlg.wasCanceled():
                    success_status = False
                    break
                # User-defined location
                if self.chkUseOutputFolder.checkState() == Qt.Unchecked:

                    status, msg = self._doc_generator.run(self._docTemplatePath, entity_field_name,
                                                        record.id, outputMode,
                                                        data_source=self.ds_entity.name,
                                                        filePath=self._outputFilePath)
                    self._doc_generator.clear_temporary_layers()


                # Output folder location using custom naming
                else:

                    status, msg = self._doc_generator.run(self._docTemplatePath, entity_field_name,
                                                          record.id, outputMode,
                                                          dataFields=documentNamingAttrs,
                                                          fileExtension=fileExtension,
                                                          data_source=self.ds_entity.name)
                    self._doc_generator.clear_temporary_layers()

                if not status:
                    result = QMessageBox.warning(self,
                                                 QApplication.translate("DocumentGeneratorDialog",
                                                                        "Document Generate Error"),
                                                 msg, QMessageBox.Ignore | QMessageBox.Abort)

                    if result == QMessageBox.Abort:
                        progressDlg.close()
                        progressDlg.deleteLater()
                        del progressDlg
                        success_status = False

                        # Restore cursor
                        QApplication.restoreOverrideCursor()

                    # If its the last record and user has selected to ignore
                    if i + 1 == len(records):
                        progressDlg.close()
                        progressDlg.deleteLater()
                        del progressDlg
                        success_status = False

                        # Restore cursor
                        QApplication.restoreOverrideCursor()

                        return

                else:
                    progressDlg.setValue(len(records))

            QApplication.restoreOverrideCursor()

            QMessageBox.information(self,
                                    QApplication.translate("DocumentGeneratorDialog",
                                                           "Document Generation Complete"),
                                    QApplication.translate("DocumentGeneratorDialog",
                                                           "Document generation has successfully completed.")
                                    )

        except SQLAlchemyError as sqlerr:
            LOGGER.debug(str(sqlerr))
            err_msg = QApplication.translate("DocumentGeneratorDialog",
                                             "Database error occured, check QGIS logs.")
            QApplication.restoreOverrideCursor()

            QMessageBox.critical(
                self,
                "STDM",
                QApplication.translate(
                    "DocumentGeneratorDialog",
                    "Error Generating documents - %s" % (err_msg)
                )
            )
            success_status = False

        except DummyException as ex:
            LOGGER.debug(str(ex))
            err_msg = sys.exc_info()[1]
            QApplication.restoreOverrideCursor()

            QMessageBox.critical(
                self,
                "STDM",
                QApplication.translate(
                    "DocumentGeneratorDialog",
                    "Error Generating documents - %s" % (err_msg)
                )
            )
            success_status = False

        progressDlg.deleteLater()
        del progressDlg

        # Reset UI
        QApplication.restoreOverrideCursor()
        self.reset(success_status)

    def _dummy_template_records(self):
        """
        This is applied when records from a template data source are to be
        used to generate the documents where no related entity will be used
        to filter matching records in the data source. The iteration of the
        data source records will be done internally within the
        DocumentGenerator class.
        """

        class _DummyRecord:
            id = 1

        return [_DummyRecord()]

    def showEvent(self, event):
        """
        Notifies if there are not entity configuration objects defined.
        :param event: Window event
        :type event: QShowEvent
        """
        QTimer.singleShot(500, self.check_entity_config)

        return QDialog.showEvent(self, event)

    def check_entity_config(self):
        if len(self._config_mapping) == 0:
            self._notif_bar.clear()

            msg = QApplication.translate("DocumentGeneratorDialog", "Table "
                                                                    "configurations do not exist or have not been configured properly")
            self._notif_bar.insertErrorNotification(msg)
