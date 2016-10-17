from collections import OrderedDict

from PyQt4.QtCore import (
    Qt,
    QSize,
    QModelIndex
)
from PyQt4.QtGui import (
    QComboBox,
    QItemDelegate,
    QTableView,
    QAbstractItemView,
    QGraphicsDropShadowEffect,
    QHeaderView,
    QSizePolicy,
    QSortFilterProxyModel
)
from stdm.data.qtmodels import BaseSTDMTableModel
from stdm.settings import current_profile
from stdm.data.configuration import entity_model
from stdm.utils.util import (
    entity_display_columns
)

class ComboBoxDelegate(QItemDelegate):

    def __init__(self, str_type_id=0, parent=None):
        """
        It is a combobox delegate embedded in STR Type column.
        :param str_type_id:
        :type str_type_id:
        :param parent:
        :type parent:
        :return:
        :rtype:
        """
        QItemDelegate.__init__(self, parent)
        self.row = 0
        self.str_type_id = str_type_id
        self.curr_profile = current_profile()
        self.social_tenure = self.curr_profile.social_tenure

    def str_type_combo (self):
        """
        A slot raised to add new str type
        matched with the party.
        :return: None
        """
        str_type_cbo = QComboBox()
        str_type_cbo.setObjectName(
            'STRTypeCbo'+str(self.row+1)
        )
        self.row = self.row + 1
        return str_type_cbo

    def str_type_set_data(self):
        """
        Sets str type combobox items.
        :return: STR type id and value.
        :rtype: OrderedDict
        """
        str_lookup_obj = self.social_tenure.tenure_type_collection
        str_types = entity_model(str_lookup_obj, True)
        str_type_obj = str_types()
        self.str_type_data = str_type_obj.queryObject().all()
        str_type = [
            (lookup.id, lookup.value)
            for lookup in self.str_type_data
        ]

        return OrderedDict(str_type)

    def createEditor(self, parent, option, index):
        """
        Creates the combobox inside a parent.
        :param parent: The container of the cobobox
        :type parent: QWidget
        :param option:
        :type option:
        :param index: The index where the combobox
         will be added.
        :type index: QModelIndex
        :return: The combobox
        :rtype: QComboBox
        """
        str_combo = QComboBox(parent)
        str_combo.insertItem(0, " ")
        for id, type in self.str_type_set_data().iteritems():
            str_combo.addItem(type, id)

        str_combo.setCurrentIndex(
            self.str_type_id
        )

        return str_combo

    def setEditorData(self, comboBox, index):
        """
        Set data to the Combobox.
        :param comboBox: The STR Type combobox
        :type comboBox: QCombobox
        :param index: The model index
        :type index: QModelIndex
        :return: None
        :rtype: NoneType
        """
        list_item_index = None
        if not index.model() is None:
            list_item_index = index.model().data(
                index, Qt.DisplayRole
            )
        if list_item_index is not None and \
                not isinstance(list_item_index, (unicode, str)):
            value = list_item_index.toInt()
            comboBox.blockSignals(True)
            comboBox.setCurrentIndex(value[0])
            comboBox.blockSignals(False)

    def setModelData(self, editor, model, index):
        """
        Gets data from the editor widget and stores
        it in the specified model at the item index.
        :param editor: STR Type combobox
        :type editor: QComboBox
        :param model: QModel
        :type model: QModel
        :param index: The index of the data
        to be inserted.
        :type index: QModelIndex
        :return: None
        :rtype: NoneType
        """
        value = editor.currentIndex()
        model.setData(
            index,
            editor.itemData(
            value, Qt.DisplayRole)
        )

    def updateEditorGeometry(self, editor, option, index):
        """
        Updates the editor for the item specified
        by index according to the style option given.
        :param editor: STR Type combobox
        :type editor: QCombobox
        :param option: style options
        :type option: QStyle
        :param index: index of the combobox item
        :type index: QModelIndex
        :return:
        :rtype:
        """
        editor.setGeometry(option.rect)

class FreezeTableWidget(QTableView):

    def __init__(
            self, table_data, headers, parent = None, *args
    ):
        QTableView.__init__(self, parent, *args)
        # set the table model
        table_model = BaseSTDMTableModel(
            table_data, headers, parent
        )

        # set the proxy model
        proxy_model = QSortFilterProxyModel(self)
        proxy_model.setSourceModel(table_model)

        # Assign a data model for TableView
        self.setModel(table_model)

        # frozen_table_view - first column
        self.frozen_table_view = QTableView(self)
        # Set the model for the widget, fixed column
        self.frozen_table_view.setModel(table_model)
        # Hide row headers
        self.frozen_table_view.verticalHeader().hide()
        # Widget does not accept focus
        self.frozen_table_view.setFocusPolicy(
            Qt.StrongFocus|Qt.TabFocus|Qt.ClickFocus
        )
        # The user can not resize columns
        self.frozen_table_view.horizontalHeader().\
            setResizeMode(QHeaderView.Fixed)
        self.frozen_table_view.setObjectName('frozen_table')
        # Style frozentable view
        self.frozen_table_view.setStyleSheet(
            '''
            #frozen_table{
                border-top:none;
            }
            '''
        )
        self.setSelectionMode(QAbstractItemView.NoSelection)

        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(5)
        self.shadow.setOffset(2)
        self.shadow.setYOffset(0)
        self.frozen_table_view.setGraphicsEffect(self.shadow)

        # Remove the scroll bar
        self.frozen_table_view.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )
        self.frozen_table_view.setVerticalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        # Puts more widgets to the foreground
        self.viewport().stackUnder(self.frozen_table_view)
        # # Log in to edit mode - even with one click
        # Set the properties of the column headings
        hh = self.horizontalHeader()
        # Text alignment centered
        hh.setDefaultAlignment(Qt.AlignCenter)

        # Set the width of columns
        columns_count = table_model.columnCount(self)
        for col in xrange(columns_count):
            if col == 0:
                # Set the size
                self.horizontalHeader().resizeSection(
                    col, 60
                )
                # Fix width
                self.horizontalHeader().setResizeMode(
                    col, QHeaderView.Fixed
                )
                # Width of a fixed column - as in the main widget
                self.frozen_table_view.setColumnWidth(
                    col, self.columnWidth(col)
                )
            elif col == 1:
                self.horizontalHeader().resizeSection(
                    col, 150
                )
                self.horizontalHeader().setResizeMode(
                    col, QHeaderView.Fixed
                )
                self.frozen_table_view.setColumnWidth(
                    col, self.columnWidth(col)
                )
            else:
                self.horizontalHeader().resizeSection(
                    col, 100
                )
                # Hide unnecessary columns in the widget fixed columns
                self.frozen_table_view.setColumnHidden(
                    col, True
                )

        # Set properties header lines
        vh = self.verticalHeader()
        vh.setDefaultSectionSize(25) # height lines
        # text alignment centered
        vh.setDefaultAlignment(Qt.AlignCenter)
        vh.setVisible(True)
        # Height of rows - as in the main widget
        self.frozen_table_view.verticalHeader().\
            setDefaultSectionSize(
            vh.defaultSectionSize()
        )

        # Show frozen table view
        self.frozen_table_view.show()
        # Set the size of him like the main
        self.update_frozen_table_geometry()

        self.setHorizontalScrollMode(
            QAbstractItemView.ScrollPerPixel
        )
        self.setVerticalScrollMode(
            QAbstractItemView.ScrollPerPixel
        )
        self.frozen_table_view.setVerticalScrollMode(
            QAbstractItemView.ScrollPerPixel
        )


        self.frozen_table_view.selectColumn(0)

        self.frozen_table_view.setEditTriggers(
            QAbstractItemView.AllEditTriggers
        )
        size_policy = QSizePolicy(
            QSizePolicy.Fixed, QSizePolicy.Fixed
        )
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(
            self.sizePolicy().hasHeightForWidth()
        )
        self.setSizePolicy(size_policy)
        self.setMinimumSize(QSize(55, 75))
        self.setMaximumSize(QSize(5550, 5555))
        #self.setGeometry(QRect(0, 0, 619, 75))
        self.SelectionMode(
            QAbstractItemView.SelectColumns
        )

        # set column width to fit contents
        self.frozen_table_view.resizeColumnsToContents()
        # set row height
        self.frozen_table_view.resizeRowsToContents()

        # Connect the headers and scrollbars of
        # both tableviews together
        self.horizontalHeader().sectionResized.connect(
            self.update_section_width
        )
        self.verticalHeader().sectionResized.connect(
            self.update_section_height
        )
        self.frozen_table_view.verticalScrollBar().\
            valueChanged.connect(
            self.verticalScrollBar().setValue
        )
        self.verticalScrollBar().valueChanged.connect(
            self.frozen_table_view.verticalScrollBar().setValue
        )
    def add_combobox(self, str_type_id, insert_row):
        delegate = ComboBoxDelegate(str_type_id)
        # Set delegate to add combobox under
        # social tenure type column
        self.frozen_table_view.setItemDelegate(
            delegate
        )
        self.frozen_table_view.setItemDelegateForColumn(
            0, delegate
        )
        index = self.frozen_table_view.model().index(
            insert_row, 0, QModelIndex()
        )
        self.frozen_table_view.model().setData(
            index, '', Qt.EditRole
        )

    def update_section_width(
            self, logicalIndex, oldSize, newSize
    ):
        if logicalIndex==0 or logicalIndex==1:
            self.frozen_table_view.setColumnWidth(
                logicalIndex, newSize
            )
            self.update_frozen_table_geometry()

    def update_section_height(
            self, logicalIndex, oldSize, newSize
    ):
        self.frozen_table_view.setRowHeight(
            logicalIndex, newSize
        )

    def resizeEvent(self, event):
        QTableView.resizeEvent(self, event)
        try:
            self.update_frozen_table_geometry()
        except Exception as log:
            LOGGER.debug(str(log))


    def scrollTo(self, index, hint):
        if index.column() > 1:
            QTableView.scrollTo(self, index, hint)

    def update_frozen_table_geometry(self):
        if self.verticalHeader().isVisible():
            self.frozen_table_view.setGeometry(
                self.verticalHeader().width() +
                self.frameWidth(),
                self.frameWidth(),
                self.columnWidth(0) +
                self.columnWidth(1),
                self.viewport().height() +
                self.horizontalHeader().height()
            )
        else:
            self.frozen_table_view.setGeometry(
                self.frameWidth(),
                self.frameWidth(),
                self.columnWidth(0) + self.columnWidth(1),
                self.viewport().height() +
                self.horizontalHeader().height()
            )

    # move_cursor override function for correct
    # left to scroll the keyboard.
    def move_cursor(self, cursor_action, modifiers):
        current = QTableView.move_cursor(
            self, cursor_action, modifiers
        )
        if cursor_action == self.MoveLeft and current.column() > 1 and \
                        self.visualRect(current).topLeft().x() < \
                        (self.frozen_table_view.columnWidth(0) +
                             self.frozen_table_view.columnWidth(1)):
            new_value = self.horizontalScrollBar().value() + \
                       self.visualRect(current).topLeft().x() - \
                       (self.frozen_table_view.columnWidth(0) +
                        self.frozen_table_view.columnWidth(1))
            self.horizontalScrollBar().setValue(new_value)
        return current

class EntityConfig(object):
    """
    Configuration class for specifying the
    foreign key mapper and document
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

    def _set_ds_columns(self):
        if not self._data_source:
            self._ds_columns = []

        else:
            self._ds_columns = entity_display_columns(
                self.ds_entity
            )

    def model(self):
        return self._base_model
