import  logging

from collections import OrderedDict
from PyQt4.QtGui import *
#QColor
#QBrush
from PyQt4.QtCore import Qt

LOGGER = logging.getLogger('stdm')

class EntityModelItem(QStandardItem):
    headers_labels = ["Name", "Description"]
    
    def __init__(self, entity=None):
        self._entity = None
        
        super(EntityModelItem, self).__init__(entity.short_name)

        self.setColumnCount(len(self.headers_labels))

        if not entity is None:
            self.set_entity(entity)

    def entity(self):
        return self._entity

    def _create_item(self, text):
        item = QStandardItem(text)

        return item

    def _set_entity_properties(self):
        name_item = self._create_item(self._entity.short_name)
        description = self._create_item(unicode(self._entity.description))

        self.appendRow([name_item, description])

    def set_entity(self, entity):
        self._entity = entity
        self._set_entity_properties()
        
class EntitiesModel(QStandardItemModel):

    def __init__(self, parent=None):
        super(EntitiesModel, self).__init__(parent)
        
        self._entities = OrderedDict()
        
        self.setHorizontalHeaderLabels(EntityModelItem.headers_labels)

        self.setSupportedDragActions(Qt.MoveAction)

    def entity(self, name):
        if name in self._entities:
            return self._entities[name]
        
        return None

    def entity_byId(self, id):
        return self._entities.values()[id]

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
        mandatory_item = QStandardItem(unicode(entity.mandatory()))
        self.appendRow([name_item, mandatory_item])
        '''
        entity_item = EntityModelItem(entity)
        name_item = entity_item._create_item(entity.short_name)
        description = entity_item._create_item(entity.description)

        self.appendRow([name_item, description])

class BaseEntitySelectionMixin(object):
    def selected_entities(self):
        model = self.model()
        if not isinstance(model, EntitiesModel):
            raise TypeError('Model is not of type <EntitiesModel>')

        selected_names = self._selected_names(model)
        
        entities = model.entities()

        return [entities[name] for name in selected_names if name in entities]

    def _names_from_indexes(self, model, selected_indexes):
        return [unicode(model.itemFromIndex(idx).text()) for idx in selected_indexes if idx.isValid()]
       
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
        return [unicode(self.currentText())]

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
    headers_labels = ["Name", "Data Type", "Description"]
    
    def __init__(self, entity=None):
        self._entity = None
        
        super(ColumnEntityModelItem, self).__init__(entity.name)

        self.setColumnCount(len(self.headers_labels))

        if not entity is None:
            self.set_entity(entity)

    def entity(self):
        return self._entity

    def _create_item(self, text):
        item = QStandardItem(text)
        return item

    def _set_entity_properties(self):
        name_item = self._create_item(self._entity.name)
        col_data_type = self._create_item(self._entity.display_name())
        description = self._create_item(unicode(self._entity.description))

        self.appendRow([name_item, col_data_type, description])

    def set_entity(self, entity):
        self._entity = entity
        self._set_entity_properties()

        
class ColumnEntitiesModel(QStandardItemModel):
    def __init__(self, parent=None):
        super(ColumnEntitiesModel,self).__init__(parent)
        self._entities = OrderedDict()
        
        self.setHorizontalHeaderLabels(ColumnEntityModelItem.headers_labels)

        self.setSupportedDragActions(Qt.MoveAction)

    def entity(self, name):
        if name in self._entities:
            return self._entities[name]
        
        return None

    def entity_byId(self, id):
        return self._entities.values()[id]

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

    def _add_row(self, entity):
        brush = QBrush(QColor(255, 204, 204))
        entity_item = ColumnEntityModelItem(entity)
        if entity.mandatory:
            entity_item.setForeground(brush)

        name_item = entity_item._create_item(entity.name)
        col_data_type = entity_item._create_item(entity.display_name())
        description = entity_item._create_item(entity.description)
        self.appendRow([name_item, col_data_type, description])

######
# Lookup Entity item model
#########

class LookupEntityModelItem(QStandardItem):
    headers_labels = ["Name"]
    
    def __init__(self, entity=None):
        self._entity = None
        
        super(LookupEntityModelItem, self).__init__(entity.short_name)

        self.setColumnCount(len(self.headers_labels))

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
        
class LookupEntitiesModel(QStandardItemModel):
    def __init__(self, parent=None):
        super(LookupEntitiesModel,self).__init__(parent)
        self._entities = OrderedDict()
        
        self.setHorizontalHeaderLabels(LookupEntityModelItem.headers_labels)

    def entity(self, name):
        if name in self._entities:
            return self._entities[name]
        
        return None

    def entity_byId(self, id):
        return self._entities.values()[id]

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
            del self._entities[short_name]
            LOGGER.debug('%s model entity removed.', name)

    def delete_entity_byname(self, short_name):
        if short_name in self._entities:
            del self._entities[short_name]
            LOGGER.debug('%s model entity removed.', short_name)

    def _add_row(self, entity):
        entity_item = LookupEntityModelItem(entity)
        self.appendRow(entity_item)


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
        description = self._create_item(unicode(self._entity.description))

        self.appendRow([name_item, description])

    def set_entity(self, entity):
        self._entity = entity
        self._set_entity_properties()
        
class STRColumnEntitiesModel(QStandardItemModel):
    def __init__(self, parent=None):
        super(STRColumnEntitiesModel,self).__init__(parent)
        self._entities = OrderedDict()
        
        self.setHorizontalHeaderLabels(STREntityModelItem.headers_labels)

    def entity(self, name):
        if name in self._entities:
            return self._entities[name]
        
        return None

    def entity_byId(self, id):
        return self._entities.values()[id]

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
        mandatory_item = QStandardItem(unicode(entity.mandatory()))
        self.appendRow([name_item, mandatory_item])
        '''
        entity_item = STREntityModelItem(entity)
        self.appendRow(entity_item)
