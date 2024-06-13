import logging
from collections import OrderedDict

from qgis.PyQt.QtCore import (
    Qt
)
from qgis.PyQt.QtGui import (
    QStandardItem,
    QStandardItemModel,
    QBrush,
    QColor,
    QIcon
)
from qgis.PyQt.QtWidgets import (
    QTableView,
    QAbstractItemView,
    QComboBox,
    QListView
)

from stdm.ui.gui_utils import GuiUtils

LOGGER = logging.getLogger('stdm')


class EntityModelItem(QStandardItem):
    def __init__(self, entity_name):
        self._entity = None

        super(EntityModelItem, self).__init__(entity_name)

class EntitiesModel(QStandardItemModel):
    headers_labels = ["Name", "Has Supporting Document?", "Description"]

    def __init__(self, parent=None):
        super(EntitiesModel, self).__init__(parent)

        self._entities = OrderedDict()

        self.setHorizontalHeaderLabels(EntitiesModel.headers_labels)

    def supportedDragActions(self):
        return Qt.MoveAction

    def entity(self, name):
        if name in self._entities:
            return self._entities[name]

        return None

    def entity_byId(self, id):
        return list(self._entities.values())[id]

    def entities(self):
        return self._entities

    def add_entity(self, entity):
        if not entity.short_name in self._entities:
            self._add_row(entity)
            self._entities[entity.short_name] = entity

    def edit_entity(self, old_entity_name, new_entity):
        self._entities[old_entity_name] = new_entity
        self._entities[new_entity.short_name] = \
            self._entities.pop(old_entity_name)

    # ++
    def delete_entity(self, entity):
        if entity.short_name in self._entities:
            name = entity.short_name
            del self._entities[name]
            LOGGER.debug('%s model entity removed.', name)

    def delete_entity_byname(self, short_name):
        if short_name in self._entities:
            del self._entities[short_name]
            LOGGER.debug('%s model entity removed.', short_name)

    def _add_row(self, entity):
        '''
        name_item = QStandardItem(entity.name())
        mandatory_item = QStandardItem(str(entity.mandatory()))
        self.appendRow([name_item, mandatory_item])
        '''
        # entity_item = EntityModelItem(entity)
        name_item = EntityModelItem(entity.short_name)
        name_item.setData(GuiUtils.get_icon_pixmap("table02.png"), Qt.DecorationRole)

        support_doc = EntityModelItem(self.bool_to_yesno(entity.supports_documents))
        support_doc.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
        description = EntityModelItem(entity.description)

        self.appendRow([name_item, support_doc, description])

    def bool_to_yesno(self, state: bool) -> str:
        CHECK_STATE = {True: 'Yes', False: 'No'}
        return CHECK_STATE[state]


class BaseEntitySelectionMixin(object):
    def selected_entities(self):
        model = self.model()
        if not isinstance(model, EntitiesModel):
            raise TypeError('Model is not of type <EntitiesModel>')

        selected_names = self._selected_names(model)

        entities = model.entities()

        return [entities[name] for name in selected_names if name in entities]

    def _names_from_indexes(self, model, selected_indexes):
        return [str(model.itemFromIndex(idx).text()) for idx in selected_indexes if idx.isValid()]

    def _selected_names(self, model):
        raise NotImplementedError('Please use the sub-class object of <BaseEntitySelectionMixin>')


class EntityTableSelectionMixin(BaseEntitySelectionMixin):
    def _selected_names(self, model):
        sel_indexes = self.selectionModel().selectedRows()

        return self._names_from_indexes(model, sel_indexes)


class EntityListSelectionMixin(BaseEntitySelectionMixin):
    def _selected_names(self, model):
        sel_indexes = self.selectionModel().selectedIndexes()

        return self._names_from_indexes(model, sel_indexes)


class EntityComboBoxSelectionMixin(BaseEntitySelectionMixin):
    def _selected_names(self, model):
        return [str(self.currentText())]

    def current_entity(self):
        entities = self.selected_entities()

        if len(entities) > 0:
            return entities[0]

        return None


class EntitiesTableView(QTableView, EntityTableSelectionMixin):
    def __init__(self, parent=None):
        super(EntitiesTableView, self).__init__(parent)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.ContiguousSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)


class EntitiesListView(QListView, EntityListSelectionMixin):
    def __init__(self, parent=None):
        super(EntitiesListView, self).__init__(parent)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)


class EntitiesComboView(QComboBox, EntityComboBoxSelectionMixin):
    def __init__(self, parent=None):
        super(EntitiesComboView, self).__init__(parent)


####
# Column Entity model item
############

class ColumnEntityModelItem(QStandardItem):
    def __init__(self, column_name: str =""):
        self._column_name = column_name
        super(ColumnEntityModelItem, self).__init__(column_name)

class ColumnEntitiesModel(QStandardItemModel):
    headers_labels = ["Name", "Data Type", "Mandatory", "Unique", "Description"]

    def __init__(self, parent=None):
        super(ColumnEntitiesModel, self).__init__(parent)
        self._entities = OrderedDict()

        self.setHorizontalHeaderLabels(ColumnEntitiesModel.headers_labels)

    def _add_row(self, column: 'Column'):
        name_column = ColumnEntityModelItem(column.name)

        data_type_name = column.display_name()

        if column.TYPE_INFO == 'VARCHAR':
            data_type_name = f'{data_type_name} ({column.maximum})'

        if column.TYPE_INFO == 'GEOMETRY':
            data_type_name = f"{data_type_name} ({column.geometry_type()} - EPSG: {column.get_srid()})"

        data_type_column = ColumnEntityModelItem(data_type_name)

        mandt_column = ColumnEntityModelItem(
            self.bool_to_yesno(column.mandatory))
        mandt_column.setTextAlignment(Qt.AlignHCenter| Qt.AlignVCenter)
        if column.mandatory:
            brush = QBrush(Qt.red)
            mandt_column.setForeground(brush)

        unique_column = ColumnEntityModelItem(
            self.bool_to_yesno(column.unique)
        )
        unique_column.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)

        description_column = ColumnEntityModelItem(column.description)

        self.appendRow([name_column, data_type_column, 
                     mandt_column, unique_column, description_column])

    def bool_to_yesno(self, state: bool) -> str:
        CHECK_STATE = {True: 'Yes', False: 'No'}
        return CHECK_STATE[state]

    def supportedDragActions(self):
        return Qt.MoveAction

    def entity(self, name):
        if name in self._entities:
            return self._entities[name]
        return None

    def entity_byId(self, id):
        return list(self._entities.values())[id]

    def entities(self):
        return self._entities

    def add_entity(self, entity):
        if not entity.name in self._entities:
            self._add_row(entity)
            self._entities[entity.name] = entity

    def edit_entity(self, old_entity, new_entity):
        self._entities[old_entity.name] = new_entity
        old_key = old_entity.name
        new_key = new_entity.name
        self._replace_key(old_key, new_key)

    # ++
    def delete_entity(self, entity):
        if entity.name in self._entities:
            name = entity.name
            del self._entities[name]
            LOGGER.debug('%s model entity removed.', name)

    def delete_entity_byname(self, short_name):
        if short_name in self._entities:
            del self._entities[short_name]
            LOGGER.debug('%s model entity removed.', short_name)
            self._refresh_entities()

    def _replace_key(self, old_key, new_key):
        """
        Relace a dictionary key
        :param old_key: name of the key to replace
        :type old_key: str
        :param new_key: name of new key
        :type new_key: str
        """
        self._entities = OrderedDict([(new_key, v)
                                      if k == old_key else (k, v) for k, v in self._entities.items()])


######
# Lookup Entity item model
#########

class LookupEntityModelItem(QStandardItem):
    def __init__(self, entity=None):
        self._entity = None

        super(LookupEntityModelItem, self).__init__(entity.short_name)

        #self.setColumnCount(len(self.headers_labels))

        if not entity is None:
            self.set_entity(entity)

    def entity(self):
        return self._entity

    def _create_item(self, text):
        item = QStandardItem(text)

        return item

    def _set_entity_properties(self):
        item_name = self._create_item(self._entity.short_name)

        self.appendRow([item_name])

    def set_entity(self, entity):
        self._entity = entity
        self._set_entity_properties()

    def set_default_bg_color(self):
        brush = QBrush(Qt.black)
        self.setForeground(brush)

    def indicate_as_empty(self):
        brush = QBrush(Qt.red)
        self.setForeground(brush)

class LookupEntitiesModel(QStandardItemModel):
    headers_labels = ["Name"]
    def __init__(self, parent=None):
        super(LookupEntitiesModel, self).__init__(parent)
        self._entities = OrderedDict()

        self.setHorizontalHeaderLabels(LookupEntitiesModel.headers_labels)

    def entity(self, name):
        if name in self._entities:
            return self._entities[name]

        return None

    def entity_byId(self, id):
        return list(self._entities.values())[id]

    def entities(self):
        return self._entities

    def add_entity(self, entity):
        if not entity.short_name in self._entities:
            self._add_row(entity)
            self._entities[entity.short_name] = entity

    def edit_entity(self, old_entity_name, new_entity):
        self._entities[old_entity_name] = new_entity
        self._entities[new_entity.short_name] = \
            self._entities.pop(old_entity_name)

    # ++
    def delete_entity(self, entity):
        if entity.short_name in self._entities:
            name = entity.short_name
            del self._entities[name]
            LOGGER.debug('%s model entity removed.', name)

    def delete_entity_byname(self, short_name):
        if short_name in self._entities:
            del self._entities[short_name]
            LOGGER.debug('%s model entity removed.', short_name)

    def _add_row(self, entity):
        entity_item = LookupEntityModelItem(entity)
        entity_item.setData(GuiUtils.get_icon_pixmap("bullets_sm.png"), Qt.DecorationRole)
        if entity.is_empty():
            brush = QBrush(Qt.red)
            entity_item.setForeground(brush)
        self.appendRow(entity_item)

    def model_item(self, row: int) -> LookupEntityModelItem:
        return self.item(row)




################
# Social Tenure Relationship model item
class STREntityModelItem(QStandardItem):
    headers_labels = ["Name", "Description"]

    def __init__(self, entity=None):
        self._entity = None
        self.name = ""

        super(STREntityModelItem, self).__init__(entity.name)

        self.setColumnCount(len(self.headers_labels))
        self.setCheckable(True)

        if not entity is None:
            self.set_entity(entity)

    def entity(self):
        return self._entity

    def _create_item(self, text):
        item = QStandardItem(text)

        return item

    def _set_entity_properties(self):
        name_item = self._create_item(self._entity.name)
        self.name = name_item
        description = self._create_item(str(self._entity.description))

        self.appendRow([name_item, description])

    def set_entity(self, entity):
        self._entity = entity
        self._set_entity_properties()


class STRColumnEntitiesModel(QStandardItemModel):
    def __init__(self, parent=None):
        super(STRColumnEntitiesModel, self).__init__(parent)
        self._entities = OrderedDict()

        self.setHorizontalHeaderLabels(STREntityModelItem.headers_labels)

    def entity(self, name):
        if name in self._entities:
            return self._entities[name]

        return None

    def entity_byId(self, id):
        return list(self._entities.values())[id]

    def entities(self):
        return self._entities

    def add_entity(self, entity):
        if not entity.name in self._entities:
            self._add_row(entity)
            self._entities[entity.name] = entity

    # ++
    def delete_entity(self, entity):
        if entity.name in self._entities:
            name = entity.name
            del self._entities[name]
            LOGGER.debug('%s model entity removed.', name)

    def delete_entity_byname(self, short_name):
        if short_name in self._entities:
            del self._entities[short_name]
            LOGGER.debug('%s model entity removed.', short_name)

    def _add_row(self, entity):
        '''
        name_item = QStandardItem(entity.name())
        mandatory_item = QStandardItem(str(entity.mandatory()))
        self.appendRow([name_item, mandatory_item])
        '''
        entity_item = STREntityModelItem(entity)
        self.appendRow(entity_item)
