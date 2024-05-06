"""
/***************************************************************************
Name                 : EntityEditorDialog
Description          : Creates an editor dialog for an entity object.
Date                 : 8/June/2016
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
from collections import OrderedDict

from qgis.PyQt.QtCore import (
    Qt,
    pyqtSignal
)
from qgis.PyQt.QtWidgets import (
    QDialogButtonBox,
    QFrame,
    QGridLayout,
    QLabel,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QApplication,
    QPushButton,
    QMessageBox,
    QToolButton
)
from qgis.gui import QgsGui

from stdm.ui.gui_utils import GuiUtils
from stdm.data.configuration import entity_model
from stdm.data.configuration.columns import (
    MultipleSelectColumn,
    VirtualColumn
)
from stdm.data.configuration.entity import Entity
from stdm.data.mapping import MapperMixin
from stdm.data.pg_utils import table_column_names
from stdm.navigation.content_group import (
    TableContentGroup
)
from stdm.security.user import User
from stdm.settings import (
    current_profile
)
from stdm.ui.forms import entity_dlg_extension
from stdm.ui.forms.documents import SupportingDocumentsWidget
from stdm.ui.forms.widgets import (
    ColumnWidgetRegistry,
    UserTipLabel
)
from stdm.ui.notification import NotificationBar
from stdm.utils.util import format_name


class EntityEditorDialog(MapperMixin):
    """
    Dialog for editing entity attributes.
    """
    addedModel = pyqtSignal(object)

    def __init__(
            self,
            entity: Entity,
            model=None,
            parent=None,
            manage_documents=True,
            collect_model=False,
            parent_entity=None,
            exclude_columns=None,
            plugin=None,
            allow_str_creation=True
    ):
        """
        Class constructor.
        :param entity: Entity object corresponding to a table object.
        :type entity: Entity
        :param model: Data object for loading data into the form widgets.
        If the model is set, then the editor dialog is assumed to be in edit
        mode.
        :type model: object
        :param parent: Parent widget that the form belongs to.
        :type parent: QWidget
        :param manage_documents: True if the dialog should provide controls
        for managing supporting documents. Only applicable if the entity
        allows for supporting documents to be attached.
        :type manage_documents: bool
        :param collect_model: If set to True only returns
        the filled form model without saving it to the database.
        :type collect_model: Boolean
        :param parent_entity: The parent entity of the editor
        :type parent_entity: Object
        :param exclude_columns: List of columns to be excluded if in a list.
        :type exclude_columns: List
        :return: If collect_model, returns SQLAlchemy Model
        """
        self._ent_document_model = None

        if entity.supports_documents:
            self.ent_model, self._ent_document_model = entity_model(
                entity,
                with_supporting_document=True
            )
        else:
            self.ent_model = entity_model(entity)

        super().__init__(parent=parent, model=self.ent_model, entity=entity)

        QgsGui.enableAutoGeometryRestore(self)

        self.collection_suffix = self.tr('Collection')

        # Set minimum width
        self.setMinimumWidth(450)

        self.plugin = plugin

        # Flag for mandatory columns
        self.has_mandatory = False
        self.reload_form = False
        self._entity = entity
        self.edit_model = model
        self.column_widgets = OrderedDict()
        self.columns = {}
        self._parent = parent
        self.exclude_columns = exclude_columns or []
        self.entity_tab_widget = None
        self._disable_collections = False
        self.filter_val = None
        self.parent_entity = parent_entity
        self.child_models = OrderedDict()
        self.entity_scroll_area = None
        self.entity_editor_widgets = OrderedDict()
        self.details_tree_view = None
        # Set notification layout bar
        self.vlNotification = QVBoxLayout()
        self.vlNotification.setObjectName('vlNotification')
        self._notifBar = NotificationBar(self.vlNotification)
        self.do_not_check_dirty = False

        # Set manage documents only if the entity supports documents
        if self._entity.supports_documents:
            self._manage_documents = manage_documents
        else:
            self._manage_documents = False

        if model is not None:
            self.ent_model = model

        self.init_mapper_mixin(self.ent_model, entity)

        self.collect_model = collect_model

        self.register_column_widgets()

        try:
            if isinstance(parent._parent, EntityEditorDialog):
                # hide collections form child editor
                self._disable_collections = True
        except AttributeError:
            self._parent._parent = None

        # Set title
        editor_trans = self.tr('Editor')
        if self._entity.label is not None:
            if self._entity.label != '':
                title_str = self._entity.label
            else:
                title_str = format_name(self._entity.short_name)
        else:
            title_str = format_name(self._entity.short_name)

        self.title = '{0} {1}'.format(title_str, editor_trans)

        self.setWindowTitle(self.title)

        # determine whether the entity is part of the STR relationship
        curr_profile = current_profile()
        self.participates_in_str, self.is_party_unit = curr_profile.social_tenure.entity_participates_in_str(self.entity)

        self._init_gui(show_str_tab=allow_str_creation and self.participates_in_str, is_party_unit=self.is_party_unit)
        self.adjustSize()

        self._get_entity_editor_widgets()

        if isinstance(parent._parent, EntityEditorDialog):
            self.parent_entity = parent.parent_entity
            self.set_parent_values()
            # make the size smaller to differentiate from parent and as it
            # only has few tabs.
            self.adjustSize()

        self.attribute_mappers = self._attr_mapper_collection

        # Exception title for editor extension exceptions
        self._ext_exc_msg = self.tr(
            'An error has occured while executing Python code in the editor '
            'extension:'
        )

        # Register custom editor extension if specified
        self._editor_ext = entity_dlg_extension(self)
        if self._editor_ext is not None:
            self._editor_ext.post_init()

            # Initialize CascadingFieldContext objects
            self._editor_ext.connect_cf_contexts()

    def _init_gui(self, show_str_tab: bool, is_party_unit: bool):
        # Setup base elements
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setObjectName('glMain')
        self.gridLayout.addLayout(
            self.vlNotification, 0, 0, 1, 1
        )

        # set widgets values
        column_widget_area = self._setup_columns_content_area()

        self.gridLayout.addWidget(
            column_widget_area, 1, 0, 1, 1
        )

        if show_str_tab:
            self._setup_str_tab(is_party_unit=is_party_unit)

        # Add notification for mandatory columns if applicable
        next_row = 2
        if self.has_mandatory:
            self.required_fields_lbl = QLabel(self)
            msg = self.tr(
                'Please fill out all required (*) fields.'
            )
            msg = self._highlight_asterisk(msg)
            self.required_fields_lbl.setText(msg)
            self.gridLayout.addWidget(
                self.required_fields_lbl, next_row, 0, 1, 2
            )
            # Bump up row reference
            next_row += 1

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setObjectName('buttonBox')
        self.gridLayout.addWidget(
            self.buttonBox, next_row, 0, 1, 1
        )

        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QDialogButtonBox.Cancel | QDialogButtonBox.Save
        )

        if self.edit_model is None:
            if not self.collect_model:
                self.save_new_button = QPushButton(
                    QApplication.translate(
                        'EntityEditorDialog', 'Save and New'
                    )
                )
                self.buttonBox.addButton(
                    self.save_new_button, QDialogButtonBox.ActionRole
                )

        # edit model, collect model
        # adding new record for child

        # Saving in parent editor
        if not isinstance(self._parent._parent, EntityEditorDialog):
            # adding a new record
            if self.edit_model is None:
                # saving when digitizing.
                if self.collect_model:
                    self.buttonBox.accepted.connect(self.on_model_added)
                # saving parent editor
                else:
                    self.buttonBox.accepted.connect(self.save_parent_editor)
                    self.save_new_button.clicked.connect(self.save_and_new)
            # updating existing record
            else:
                if not self.collect_model:
                    # updating existing record of the parent editor
                    self.buttonBox.accepted.connect(self.save_parent_editor)
                else:
                    self.buttonBox.accepted.connect(self.on_model_added)
        # Saving in child editor
        else:
            # save and new record
            if self.edit_model is None:
                self.buttonBox.accepted.connect(self.on_child_saved)
                self.save_new_button.clicked.connect(
                    lambda: self.on_child_saved(True)
                )
            else:
                # When updating an existing child editor save to the db
                self.buttonBox.accepted.connect(
                    self.on_child_saved
                )
                # self.buttonBox.accepted.connect(self.submit)

        self.buttonBox.rejected.connect(self.cancel)

    @property
    def notification_bar(self):
        """
        :return: Returns the dialog's notification bar.
        :rtype: NotificationBar
        """
        return self._notifBar

    def save_parent_editor(self):
        """
        Saves the parent editor and its children.
        """
        self.submit()
        self.save_children()

        self.accept()

    def set_parent_values(self):
        """
        Sets the parent display column for the child.
        """
        if self.parent_entity is None:
            return
        for col in self._entity.columns.values():
            if col.TYPE_INFO == 'FOREIGN_KEY':
                parent_entity = col.parent
                if parent_entity == self.parent_entity:
                    self.parent_widgets_value_setter(self._parent._parent, col)

    def parent_widgets_value_setter(self, parent, col):
        """
        Finds and sets the value from parent widget and set it to the column
        widget of a child using the child column.
        :param parent: The parent widget
        :type parent: QWidget
        :param col: The child column object
        :type col: Object
        """
        for parent_col_name, parent_widget in parent.column_widgets.items():
            parent_col = parent.columns[parent_col_name]
            if parent_col.name == col.name:
                self.single_parent_value_setter(col, parent_widget)
                break
            if parent_col.name in col.entity_relation.display_cols:
                self.single_parent_value_setter(col, parent_widget)
                break

    def single_parent_value_setter(self, col, parent_widget):
        """
        Gets value from parent widget and set it to the column widget of a
        child using the child column.
        :param parent: The parent widget
        :type parent: QWidget
        :param col: The child column object
        :type col: Object
        """
        local_widget = self.column_widgets[col.name]
        local_widget.show_clear_button()
        self.filter_val = parent_widget.text()
        local_widget.setText(self.filter_val)

    def save_and_new(self):
        """
        A slot raised when Save and New button is click. It saves the form
        without showing a success message. Then it sets reload_form property
        to True so that entity_browser can re-load the form.
        """
        from stdm.ui.entity_browser import (
            EntityBrowserWithEditor
        )

        save_model_todb=False
        save_and_new=True

        self.submit(save_model_todb, save_and_new)
        self.save_children()

        if self.is_valid:
            self.addedModel.emit(self.model())
            self.setModel(self.ent_model())
            self.clear()
            self.child_models.clear()
            for index in range(0, self.entity_tab_widget.count() - 1):
                if isinstance(
                        self.entity_tab_widget.widget(index),
                        EntityBrowserWithEditor
                ):
                    child_browser = self.entity_tab_widget.widget(index)
                    child_browser.remove_rows()

    def on_model_added(self):
        """
        A slot raised when a form is submitted with collect model set to True.
        There will be no success message and the form does not close.
        """
        self.submit(True)
        self.addedModel.emit(self.model())

    def closeEvent(self, event):
        """
        Raised when a request to close the window is received.
        Check the dirty state of input controls and prompt user to
        save if dirty.
        """

        if self.do_not_check_dirty:
            event.accept()
            return
        isDirty, userResponse = self.checkDirty()

        if isDirty:
            if userResponse == QMessageBox.Yes:
                # We need to ignore the event so that validation and
                # saving operations can be executed
                event.ignore()
                self.submit()
            elif userResponse == QMessageBox.No:
                event.accept()
            elif userResponse == QMessageBox.Cancel:
                event.ignore()
        else:
            event.accept()

    def on_child_saved(self, save_and_new=False):
        """
        A slot raised when the save or save and new button is clicked. It sets
        the child_models dictionary of the parent when saved.
        :param save_and_new: A boolean indicating the save and new button is
        clicked to trigger the slot.
        :type save_and_new: Boolean
        """
        if self.parent_entity is None:
            return

        self.submit(True)

        insert_pos = self._parent.tbEntity.model().rowCount() + 1
        # Save to parent editor so that it is persistent.
        self._parent._parent.child_models[insert_pos, self._entity.name] = \
            (self._entity, self.model())
        self.addedModel.emit(self.model())
        if not save_and_new:
            self.accept()

        else:
            if self.is_valid:
                # self.addedModel.emit(self.model())
                self.setModel(self.ent_model())

                self.clear()
                self.set_parent_values()

    def save_children(self):
        """
        Saves children models into the database by assigning the the id of the
        parent for foreign key column.
        """
        if len(self.child_models) < 1:
            return
        children_obj = []
        for row_entity, row_value in self.child_models.items():
            entity, model = row_value

            ent_model = entity_model(entity)
            entity_obj = ent_model()
            for col in entity.columns.values():
                if col.TYPE_INFO == 'FOREIGN_KEY':
                    if col.parent.name == self._entity.name:
                        setattr(model, col.name, self.model().id)
                        children_obj.append(model)
            entity_obj.saveMany(children_obj)

    def register_column_widgets(self):
        """
        Registers the column widgets.
        """
        # Append column labels and widgets
        table_name = self._entity.name
        columns = table_column_names(table_name)
        self.scroll_widget_contents = QWidget()
        self.scroll_widget_contents.setObjectName(
            'scrollAreaWidgetContents'
        )
        for c in self._entity.columns.values():

            if c.name in self.exclude_columns:
                continue

            if c.name not in columns and not isinstance(c, VirtualColumn):
                continue

            # Get widget factory
            column_widget = ColumnWidgetRegistry.create(
                c,
                self.scroll_widget_contents,
                host=self
            )

            self.columns[c.name] = c

            self.column_widgets[c.name] = column_widget

    def _setup_columns_content_area(self):
        # Only use this if entity supports documents
        # self.entity_tab_widget = None
        self.doc_widget = None

        self.entity_scroll_area = QScrollArea(self)
        self.entity_scroll_area.setFrameShape(QFrame.NoFrame)
        self.entity_scroll_area.setWidgetResizable(True)
        self.entity_scroll_area.setObjectName('scrollArea')

        # Grid layout for controls
        self.gl = QGridLayout(self.scroll_widget_contents)
        self.gl.setObjectName('gl_widget_contents')

        # Append column labels and widgets
        table_name = self._entity.name
        columns = table_column_names(table_name)
        # Iterate entity column and assert if they exist
        row_id = 0
        for column_name, column_widget in self.column_widgets.items():
            c = self.columns[column_name]

            if c.name in self.exclude_columns:
                continue

            if c.name not in columns and not isinstance(c, VirtualColumn):
                continue

            if column_widget is not None:
                header = c.ui_display()
                self.c_label = QLabel(self.scroll_widget_contents)

                # Format label text if it is a mandatory field
                if c.mandatory:
                    header = '{0} *'.format(c.ui_display())
                    # Highlight asterisk
                    header = self._highlight_asterisk(header)

                self.c_label.setText(header)
                self.gl.addWidget(self.c_label, row_id, 0, 1, 1)

                self.column_widget = column_widget
                self.gl.addWidget(self.column_widget, row_id, 1, 1, 1)

                # Add user tip if specified for the column configuration
                if c.user_tip:
                    self.tip_lbl = UserTipLabel(user_tip=c.user_tip)
                    self.gl.addWidget(self.tip_lbl, row_id, 2, 1, 1)

                if c.mandatory and not self.has_mandatory:
                    self.has_mandatory = True

                col_name = c.name
                # Replace name accordingly based on column type
                if isinstance(c, MultipleSelectColumn):
                    col_name = c.model_attribute_name

                # Add widget to MapperMixin collection
                self.addMapping(
                    col_name,
                    self.column_widget,
                    c.mandatory,
                    pseudoname=c.ui_display()
                )

                # Bump up row_id
                row_id += 1

        self.entity_scroll_area.setWidget(self.scroll_widget_contents)

        if self.entity_tab_widget is None:
            self.entity_tab_widget = QTabWidget(self)
        # Check if there are children and add foreign key browsers

        # Add primary tab if necessary
        self._add_primary_attr_widget()

        if not self._disable_collections:
            ch_entities = self.children_entities()

            for col, ch in ch_entities:
                if hasattr(col.entity_relation, 'show_in_parent'):
                    if col.entity_relation.show_in_parent != '0':
                        self._add_fk_browser(ch, col)
                else:
                    self._add_fk_browser(ch, col)

        # Add tab widget if entity supports documents
        if self._entity.supports_documents:
            self.doc_widget = SupportingDocumentsWidget(
                self._entity.supporting_doc,
                self._ent_document_model,
                self
            )

            # Map the source document manager object
            self.addMapping(
                'documents',
                self.doc_widget.source_document_manager
            )

            #
            # # Add attribute tab
            # self._add_primary_attr_widget()

            # Add supporting documents tab
            self.entity_tab_widget.addTab(
                self.doc_widget,
                self.tr('Supporting Documents')
            )

        # Return the correct widget
        if self.entity_tab_widget is not None:
            return self.entity_tab_widget

        return self.entity_scroll_area

    def _add_primary_attr_widget(self):
        # Check if the primary entity
        # exists and add if it does not
        pr_txt = self.tr('Primary')
        if self.entity_tab_widget is not None:
            tab_txt = self.entity_tab_widget.tabText(0)
            if not tab_txt == pr_txt:
                self.entity_tab_widget.addTab(
                    self.entity_scroll_area,
                    pr_txt
                )

    def _setup_str_tab(self, is_party_unit: bool):
        """
        Creates the STR relationship tab
        """
        from stdm.ui.feature_details import DetailsTreeView

        layout = QVBoxLayout()
        hl = QHBoxLayout()

        add_btn = QToolButton(self)
        add_btn.setText(self.tr('Create STR'))
        add_btn.setIcon(GuiUtils.get_icon('add.png'))
        hl.addWidget(add_btn)
        add_btn.clicked.connect(self._create_str)

        edit_btn = QToolButton(self)
        edit_btn.setText(self.tr('Edit'))
        edit_btn.setIcon(GuiUtils.get_icon('edit.png'))
        edit_btn.setDisabled(True)
        hl.addWidget(edit_btn)

        view_document_btn = QToolButton(self)
        view_document_btn.setText(self.tr('View Supporting Documents'))
        view_document_btn.setIcon(GuiUtils.get_icon('document.png'))
        view_document_btn.setDisabled(True)
        hl.addWidget(view_document_btn)

        hl.addStretch()
        layout.addLayout(hl)

        self.details_tree_view = DetailsTreeView(parent=self,
                                            plugin=self.plugin,
                                            edit_button=edit_btn,
                                            view_document_button=view_document_btn)
        self.details_tree_view.activate_feature_details(True, follow_layer_selection=False)
        self.details_tree_view.model.clear()

        if is_party_unit:
            self.details_tree_view.search_party(self.entity, [self.ent_model.id])
        else:
            self.details_tree_view.search_spatial_unit(self.entity, [self.ent_model.id])

        layout.addWidget(self.details_tree_view)
        w = QWidget()
        w.setLayout(layout)

        self.entity_tab_widget.addTab(
            w,
            self.tr('STR')
        )

    def _create_str(self):
        """
        Opens the dialog to create a new STR
        """
        from stdm.ui.social_tenure.str_editor import STREditor
        add_str_window = STREditor()

        #if is_party_unit:
        #    add_str.set_party_data(self.entity_model_obj)

        if add_str_window.exec_():
            # STR created - refresh STR view
            if self.is_party_unit:
                self.details_tree_view.search_party(self.entity, [self.ent_model.id])
            else:
                self.details_tree_view.search_spatial_unit(self.entity, [self.ent_model.id])

    def _add_fk_browser(self, child_entity, column):
        # Create and add foreign key
        # browser to the collection
        from stdm.ui.entity_browser import (
            ContentGroupEntityBrowser
        )

        attr = '{0}_collection'.format(child_entity.name)

        # Return if the attribute does not exist
        if not hasattr(self._model, attr):
            return

        table_content = TableContentGroup(User.CURRENT_USER.UserName, child_entity.short_name)

        if self.edit_model is not None:
            parent_id = self.edit_model.id
        else:
            parent_id = 0

        entity_browser = ContentGroupEntityBrowser(
            child_entity, table_content, rec_id=parent_id, parent=self, plugin=self.plugin, load_recs=False)

        # entity_browser = EntityBrowserWithEditor(
        # child_entity,
        # self,
        # MANAGE,
        # False,
        # plugin=self.plugin
        # )

        entity_browser.buttonBox.setVisible(False)
        entity_browser.record_filter = []

        if len(child_entity.label) > 2:
            column_label = child_entity.label
        else:
            # Split and join  to filter out entity name prefix
            # e.g. 'lo_parcel' to 'parcel'
            column_label = format_name(" ".join(child_entity.name.split("_", 1)[1:]))

        self.set_filter(child_entity, entity_browser)

        self.entity_tab_widget.addTab(
            entity_browser,
            '{0}'.format(
                column_label
            )
        )

    def set_filter(self, entity, browser):
        col = self.filter_col(entity)
        child_model = entity_model(entity)
        child_model_obj = child_model()
        col_obj = getattr(child_model, col.name)

        browser.filtered_records = []

        if self.model() is not None:
            if self.model().id is not None:
                browser.filtered_records = child_model_obj.queryObject().filter(
                    col_obj == self.model().id
                ).all()

        if self.edit_model is not None:
            browser.filtered_records = child_model_obj.queryObject().filter(
                col_obj == self.edit_model.id
            ).all()

    def filter_col(self, child_entity):
        for col in child_entity.columns.values():
            if col.TYPE_INFO == 'FOREIGN_KEY':
                parent_entity = col.parent
                if parent_entity == self._entity:
                    return col

    def children_entities(self):
        """
        :return: Returns a list of children entities (by name)
        that refer to the main entity as the parent.
        :rtype: OrderedDict
        """
        child_columns = []
        for ch in self._entity.children():
            if ch.TYPE_INFO == Entity.TYPE_INFO:
                for col in ch.columns.values():
                    if hasattr(col, 'entity_relation'):
                        print('ENTITY: ', self._entity.name)
                        print('COL   : ', col)
                        print('PARENT: ', col.parent)

                        if col.parent is not None:
                            print('PARENT NAME: ', col.parent.name)
                            if col.parent.name == self._entity.name:
                                child_columns.append((col, ch))
        return child_columns

    def document_widget(self):
        """
        :return: Returns the widget for managing
        the supporting documents for an entity if enabled.
        :rtype: SupportingDocumentsWidget
        """
        return self.doc_widget

    def source_document_manager(self):
        """
        :return: Returns an instance of the
        SourceDocumentManager only if supporting
        documents are enabled for the given entity. Otherwise,
        None if supporting documents are not enabled.
        :rtype: SourceDocumentManager
        """
        if self.doc_widget is None:
            return None

        return self.doc_widget.source_document_manager

    def _highlight_asterisk(self, text):
        # Highlight asterisk in red
        c = '*'

        # Do not format if there is no asterisk
        if text.find(c) == -1:
            return text

        asterisk_highlight = '<span style=\" color:#ff0000;\">*</span>'
        text = text.replace(c, asterisk_highlight)

        return '<html><head/><body><p>{0}</p></body></html>'.format(text)

    def _custom_validate(self):
        """
        Override of the MapperMixin which enables custom editor extensions to
        inject additional validation before saving form data.
        :return: Return True if the validation was successful,
        otherwise False.
        :rtype: bool
        """
        if self._editor_ext is not None:
            return self._editor_ext.validate()

        # Return True if there is no custom editor extension specified
        return True

    def _post_save(self, model):
        """
        Include additional post-save logic by custom extensions.
        :param model: SQLAlchemy model
        :type model: object
        """
        if self._editor_ext is not None:
            self._editor_ext.post_save(model)

    def _get_entity_editor_widgets(self):
        """
        Gets entity editor widgets and appends them to a dictionary
        """
        if self.entity_tab_widget:
            tab_count = self.entity_tab_widget.count()
            for i in range(tab_count):
                tab_object = self.entity_tab_widget.widget(i)
                tab_text = self.entity_tab_widget.tabText(i)
                self.entity_editor_widgets[tab_text] = tab_object
        else:
            self.entity_editor_widgets['no_tab'] = self.entity_scroll_area
