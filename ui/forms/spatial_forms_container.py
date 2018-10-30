
from collections import OrderedDict

from PyQt4.QtCore import QTimer, Qt, QCoreApplication
from PyQt4.QtGui import (
    QIcon,
    QStandardItemModel,
    QStandardItem,
    QTreeView,
    QApplication,
    QDialog,
    QAbstractItemView,
    QWidget,
    QMessageBox,
    QDialogButtonBox,
    QItemSelectionModel,
    QVBoxLayout,
    QDoubleSpinBox,
    QMdiArea, QTabWidget, QPushButton)

from qgis.utils import (
    iface
)

from stdm.ui.forms.editor_dialog import EntityEditorDialog
from ui_spatial_forms_container import Ui_SpatialFormsContainer
from stdm.settings import current_profile
from stdm.ui.notification import NotificationBar
from stdm.utils.util import entity_display_columns
from stdm.geometry.geometry_utils import (
    zoom_to_selected, active_spatial_column, get_wkt
)


class SpatialFormsContainer(QDialog, Ui_SpatialFormsContainer):
    """
    Wrapper class for STR Editor for new STR record editor user interface.
    """
    def __init__(self, entity, layer, feature_models, plugin):
        """
        Initializes the STR editor.
        """
        QDialog.__init__(self, iface.mainWindow())
        self.setupUi(self)
        self.iface = iface
        self.spatial_parent_number = 0
        self.layer = layer
        self.form_count = 0
        self.entity = entity
        self.plugin = plugin
        self._init_tree_view()
        self.spatial_form_items = {}
        self.translate_spatial_form_items()
        self.current_profile = current_profile()
        self.feature_models = feature_models
        self.custom_tenure_info_component = None
        self.column_formatters = self.plugin.entity_formatters[entity.name]
        self._init_editor()
        self.add_tree_node()
        self.form_error = {}
        self.editing = True
        self.active_spatial_column = active_spatial_column(entity, layer)
        self.notice = NotificationBar(self.str_notification)
        self.discard_btn.clicked.connect(self.discard)
        self.layer.editingStopped.connect(self.discard)
        save_btn = self.buttonBox.button(QDialogButtonBox.Save)
        save_btn.clicked.connect(self.save)

    def discard(self):
        for i in range(len(self.feature_models)):
            self.layer.undoStack().undo()

        for feature in self.plugin.geom_tools_container.original_features:
            self.layer.updateFeature(feature)
            self.layer.undoStack().undo()
        self.plugin.geom_tools_container.remove_memory_layers(True)
        self.feature_models.clear()
        self.reject()

    def _init_editor(self):
        """
        Initializes the GUI of the STR editor.
        """
        self._init_notification()
        self.splitter.isCollapsible(False)
        self.splitter.setSizes([220, 550])
        self.splitter.setChildrenCollapsible(False)
        self.discard_btn = QPushButton(
            QApplication.translate(
                'SpatialFormsContainer', 'Discard'
            )
        )
        self.buttonBox.addButton(
            self.discard_btn, QDialogButtonBox.ActionRole
        )

        self.setWindowFlags(
            Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint
        )

    def _init_notification(self):
        """
        Initializes the notification object and
        connects signals and slot that toggles
        top description and the notification bar.
        """
        self.notice = NotificationBar(
            self.str_notification
        )

    def _init_tree_view(self):
        """
        Initializes the tree view and model
        and adds it into the left scrollArea.
        """
        self.tree_view_model = QStandardItemModel()
        headers = []
        headers.append('')

        col_headers = [
            (c.name, c.ui_display()) for c in self.entity.columns.values()
            if c.name in entity_display_columns(self.entity)
            if c.name != 'id'
        ]

        self.column_headers = OrderedDict(col_headers)
        # print self.column_headers, 2
        self.tree_view_model.setHorizontalHeaderLabels(
            self.column_headers.values()
        )
        self.tree_view.setModel(self.tree_view_model)
        # self.tree_view.setHeaderHidden(True)
        self.tree_view.setAlternatingRowColors(True)
        self.tree_view.setRootIsDecorated(True)
        self.tree_view.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )
        self.tree_view.setStyleSheet(
            '''
            QTreeView:!active {
                selection-background-color: #72a6d9;
            }
            '''
        )
        self.view_selection = self.tree_view.selectionModel()

        self.view_selection.currentChanged.connect(
            self.on_tree_view_item_clicked
        )

    def save(self):

        error_found = False
      
        for i in range(0, self.spatial_parent_number):

            widget = self.component_container.widget(i)
            feature_id = widget.feature_id

            editor = widget.entity_editor
            errors = editor.validate_all()
            if len(errors) > 0:
                for error in errors:
                    self.notice.insertErrorNotification(error)
                if not error_found:
                    error_found = True
                self.form_error[feature_id] = errors
            if widget.feature_id > 0:
                editor._mode = 2201
            else:
                editor._mode = 2200

            model = editor.model()

            if feature_id <= 0:
                geom_wkt = get_wkt(
                    self.entity, self.layer,
                    self.active_spatial_column, feature_id
                )

                if geom_wkt is None:
                    title = QApplication.translate(
                        'SpatialFormsContainer',
                        u'Spatial Entity Form Error',
                        None,
                        QCoreApplication.UnicodeUTF8
                    )
                    msg = QApplication.translate(
                        'SpatialFormsContainer',
                        u'The feature you have added is invalid. \n'
                        'To fix this issue, check if the feature '
                        'is digitized correctly.  \n'
                        'Make sure you have added a base layer to digitize on.',
                        None,
                        QCoreApplication.UnicodeUTF8
                    )
                    # Message: Spatial column information
                    # could not be found
                    QMessageBox.critical(
                        iface.mainWindow(),
                        title,
                        msg
                    )
                    return
                srid = None

                # get srid with EPSG text
                full_srid = self.layer.crs().authid().split(':')

                if len(full_srid) > 0:
                    # Only extract the number
                    srid = full_srid[1]

                if not geom_wkt is None:
                    # add geometry into the model
                    setattr(
                        model,
                        self.active_spatial_column,
                        'SRID={};{}'.format(srid, geom_wkt)
                    )

                # editor.setModel(model)
            # if editor.is_valid:
            if not error_found:
                if feature_id <= 0:
                    editor._mode = 2200
                    self.iface.mainWindow().blockSignals(True)

                    editor.save_parent_editor(save_and_new=True)
                    self.layer.deleteFeature(feature_id)

                    self.iface.mainWindow().blockSignals(False)
                else:
                    editor._mode = 2201
                    editor.save_parent_editor(save_and_new=True)

        if not error_found:
            QMessageBox.information(
                self,
                QApplication.translate("SpatialFormsContainer", "Entity Editor"),
                QApplication.translate(
                    "SpatialFormsContainer",
                    "Record has been successfully added/updated."
                )
            )
            self.done(1)
            self.editing = False
        else:
            self.reject()

    # def on_form_saved(self, model):
    #     """
    #     A slot raised when the save button is clicked
    #     in spatial unit form. It adds the feature model
    #     in feature_models ordered dictionary to be saved
    #     later.
    #     :param model: The model holding feature geometry
    #     and attributes obtained from the form
    #     :type model: SQLAlchemy Model
    #     :return: None
    #     :rtype: NoneType
    #     """
    #     editor = self.sender()
    #     if not model is None:
    #         if editor.is_valid:
    #
    #             editor.accept()

    def on_tree_view_item_clicked(self, current, previous):
        """
        Disables the delete button if the party node is clicked and enable it
        if other items are clicked.
        :param current: The newly clicked item index
        :type current: QModelIndex
        :param previous: The previous item index
        :type previous: QModelIndex
        """
        selected_item = self.tree_view_model.itemFromIndex(current)
        if selected_item is None:
            return
        QTimer.singleShot(50, lambda : self.select_feature(selected_item))
        self.component_container.setCurrentWidget(
            self.component_container.widget(selected_item.row())
        )

    def select_feature(self, selected_item):
        self.iface.setActiveLayer(self.layer)
        self.layer.setSelectedFeatures([selected_item.data()])
        if selected_item.data() in self.form_error.keys():
            errors = self.form_error[selected_item.data()]
            for error in errors:
                self.notice.insertErrorNotification(error)

        zoom_to_selected(self.layer)

    def add_entity_editor(self, model, feature_id):
        """
        Adds custom tenure info tab with editor form. It could load data if
        the custom_model is not none.
        :param party_entity: The associated party entity
        :type party_entity: Object
        :param spatial_unit_entity: The associated spatial unit entity
        :type spatial_unit_entity: Object
        :param party_model: The party model associated with custom tenure info
        record.
        :type party_model: Object
        :param str_number: The STR record number
        :type str_number: Integer
        :param row_number: The row number of the party entry
        :type row_number: Integer
        :param custom_model: The custom tenure model that populates the tab
        forms.
        :type custom_model: Integer
        :return: True if the editor is created and false if not created.
        :rtype: Boolean
        """
        # Get the custom attribute entity
        widget = QWidget()
        editor = EntityEditorDialog(
            self.entity, parent=widget,
            manage_documents=False,
            model=model,
            collect_model=True
        )

        tab_widget = QTabWidget(widget)
        setattr(widget, '_entity', self.entity)
        setattr(widget, 'entity_editor', editor)
        setattr(widget, 'feature_id', feature_id)
        setattr(widget, 'model', model)
        layout = QVBoxLayout(widget)
        layout.addWidget(tab_widget)
        editor.buttonBox.hide()  # Hide entity editor buttons

        for tab_text, tab_object in editor.entity_editor_widgets.items():

            if tab_text != 'no_tab':
                tab_widget.addTab(tab_object, str(tab_text))
            else:
                tab_widget.addTab(tab_object, 'Primary')

        self.component_container.addWidget(widget)

    def translate_spatial_form_items(self):
        """
        Translates the texts of the STR items.
        """
        self.parent_feature_text = QApplication.translate(
            'SpatialFormsContainer', 'Parent Feature'
        )
        self.split_feature_text = QApplication.translate(
            'SpatialFormsContainer', 'Split Feature'
        )

    def str_node(self):
        """
        Creates features node.
        """
        self.str_children()
        self.tree_view.expandAll()
        # self.tree_view.expandAll()

    def add_tree_node(self):
        """
        Creates STR children and
        populates self.spatial_form_items dictionary.
        :param str_root: The STR root item.
        :type str_root: QStandardItem
        """
        # children = []
        # children.append(self.split_feature_text)
        # print 'start 2'
        # children.append(self.split_feature_text)
        for feature_id, model in self.feature_models.iteritems():

            for i, (name, header) in enumerate(self.column_headers.iteritems()):
                # print feature_id, model, name, header
                # print feature_id, vars(model), dir(model)
            #     item = self.child_item(str_root, name)
            #
            #     self.spatial_form_items[
            #         '%s%s' % (name, self.spatial_parent_number)] = item
            #
            # self.spatial_form_items[
            #     '%s%s' % (self.parent_feature_text, self.spatial_parent_number)
            # ] = str_root
                col_val = getattr(model, name)
                # print col_val, 'v22'
                if name in self.column_formatters:
                    formatter = self.column_formatters[name]

                    col_val = formatter.format_column_value(col_val)

                item = self.child_item(col_val, i, feature_id)
            self.add_entity_editor(model, feature_id)
            self.spatial_parent_number = self.spatial_parent_number + 1
                # self._formatted_record[header] = self.feature_models[]
        self.tree_view.expandAll()

    def child_item(self, name, column, feature_id):
        """
        Creates the child item of str_root.
        :param str_root:  The STR root item.
        :type str_root: QStandardItem
        :param name: The item name
        :type name: String

        :return: The child item
        :rtype: QStandardItem
        """
        if name is None or name == 'None':
            name = ''
        if column == 0:
            if feature_id > 0:
                q_icon = QIcon(
                    u':/plugins/stdm/images/icons/geometry_map_tool.png')
            else:
                q_icon = QIcon(
                    u':/plugins/stdm/images/icons/layer_polygon.png')

            item = QStandardItem(q_icon, unicode(name))
        else:

            item = QStandardItem(unicode(name))
        item.setData(feature_id)
        # print 'start 3'
        self.tree_view_model.setItem(self.spatial_parent_number, column, item)
        # print 'start 4'
        return item

    def current_item(self):
        """
        Gets the currently selected tree_view item.
        :return: The currently selected item
        :rtype: QStandardItem
        """
        index = self.tree_view.currentIndex()
        item = self.tree_view_model.itemFromIndex(index)
        return item

    def spatial_form_item(self, text, sp_parent_number):
        """
        Gets the spatial_form_item by text and sp_parent_number.
        :param text: The translated text of items.
        :type text: String
        :param sp_parent_number: The current STR number
        :type sp_parent_number: Integer
        """
        item = self.spatial_form_items['%s%s' % (text, sp_parent_number)]
        return item

    def remove_str_tree_node(self):
        """
        Remove the STR node.
        """
        selected_indexes = self.tree_view.selectedIndexes()
        result = self.validate_str_delete(selected_indexes)
        if not result:
            return
        index = selected_indexes[0]
        selected_item = self.tree_view_model.itemFromIndex(index)
        spatial_parent_number = selected_item.data()
        self.tree_view_model.removeRows(index.row(), 1)

        self.remove_str_node_models(spatial_parent_number)
        self.validate.enable_save_button()

    def remove_str_node_models(self, spatial_parent_number):
        """
        Removes the STR node data store from the data store dictionary.
        :param spatial_parent_number: The STR node number
        :type spatial_parent_number: Integer
        """
        del self.data_store[spatial_parent_number]
