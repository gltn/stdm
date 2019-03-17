"""
/***************************************************************************
Name                 : ConfigurationCollectionBase
Description          : Base class for handling a collection of custom widget
                       configurations for STDM composer items including
                       serialization of these configurations..
Date                 : 15/December/2014
copyright            : (C) 2014 by UN-Habitat and implementing partners.
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

from PyQt4.QtGui import (
    QWidget
)
from PyQt4.QtXml import (
    QDomElement
)

from qgis.core import (
    QgsComposerItem,
    QgsComposition
)

__all__ = ['ItemConfigBase', 'ConfigurationCollectionBase',
           'LinkedTableItemConfiguration']


class ItemConfigBase(object):
    """
    Base class for composer item configuration.
    """

    '''
    Tag Name of the DOM element containing information regarding this
    configuration.
    '''
    tag_name = ""

    def __init__(self, item_id=""):
        self._item_id = item_id

    def item_id(self):
        """
        :return: Identifier of the referenced composer item.
        :rtype: str
        """
        return self._item_id

    def set_item_id(self,item_id):
        """
        Sets the identifier of the referenced composer item.
        :param item_id: Unique identifier of the referenced composer item.
        :type item_id: str
        """
        self._item_id = item_id

    def create_handler(self, composition, query_handler=None):
        """
        Returns an object for setting the value of the composer item
        specified by this configuration item.
        :param composition: Composition object.
        :type composition: QgsComposition
        :param query_handler: Re-usable function for executing sub-queries
        that the value handler might require.
        :type query_handler: object
        :return: A sub-class of ItemConfigValueHandler for setting the value
        of a composer item.
        :rtype: ItemConfigValueHandler
        """
        return ItemConfigValueHandler(composition, self, query_handler)

    def to_dom_element(self, dom_document):
        """
        :param dom_document: Root composer element.
        :type dom_document: QDomDocument
        :return: A XML DOM element that contains the configuration
        settings.
        :rtype: QDomElement
        """
        raise NotImplementedError

    @staticmethod
    def create(dom_element):
        """
        Create a configuration object from a QDomDocument instance.
        :param dom_element: QDomElement that represents item configuration.
        :type dom_element: QDomElement
        :return: Configuration instance whose properties have been
        extracted from the composer document instance.
        :rtype: ItemConfigBase
        """
        raise NotImplementedError


class LinkedTableItemConfiguration(ItemConfigBase):
    """
    Configuration item for data sources linked via foreign keys.
    PhotoConfiguration and TableConfiguration classes inherit this
    class.
    """
    def __init__(self, **kwargs):
        item_id = kwargs.pop("item_id", "")
        ItemConfigBase.__init__(self, item_id)

        self._linked_table = kwargs.pop("linked_table", "")
        self._source_field = kwargs.pop("source_field", "")
        self._linked_field = kwargs.pop("linked_field", "")

    def linked_table(self):
        """
        :return: Name of the referenced table.
        :rtype: str
        """
        return self._linked_table

    def set_linked_table(self, table):
        """
        Set the name of the referenced table.
        :param table: Table name.
        :type table: str
        """
        self._linked_table = table

    def source_field(self):
        """
        :return: Column name in the referenced data source.
        :rtype: str
        """
        return self._source_field

    def set_source_field(self, field):
        """
        Set the name of the column in the referenced data source.
        :param column: Column name.
        :rtype: str
        """
        self._source_field = field

    def linked_field(self):
        """
        :return: Name of the matching column in the linked table.
        :rtype: str
        """
        return self._linked_field

    def set_linked_column(self, field):
        """
        Set the name of the matching column in the linked table.
        :param column: Column name.
        :type column: str
        """
        self._linked_field = field

    def extract_from_linked_table_properties(self, ltic):
        """
        Extracts properties from a LinkedTableItemConfiguration object.
        :param ltic: Configuration item containing linked table properties.
        :type ltic: LinkedTableItemConfiguration
        """
        self._linked_field = ltic.linked_field
        self._source_field = ltic.source_field
        self._linked_table = ltic.linked_table

    def write_to_dom_element(self, dom_element):
        """
        Appends the configuration information to the specified DOM element.
        :param dom_document: Composer item element.
        :type dom_document: QDomElement
        """
        dom_element.setAttribute("itemid", self._item_id)
        dom_element.setAttribute("table", self._linked_table)
        dom_element.setAttribute("referenced_field", self._source_field)
        dom_element.setAttribute("referencing_field", self._linked_field)

    def _extract_from_dom_element(self, dom_element):
        """
        Sets the object properties from the values specified in the dom
        element. This method is useful for subclasses.
        :param dom_element: QDomElement that represents composer item
        configuration.
        :type dom_element: QDomElement
        """
        self._linked_table = dom_element.attribute("table")
        self._source_field = dom_element.attribute("referenced_field")
        self._linked_field = dom_element.attribute("referencing_field")
        self._item_id = dom_element.attribute("itemid")

    def linked_table_props(self):
        """
        Creates a LinkedTableProps object which contains all the data
        properties of the linked table.
        This should be cleaned up with the similar static method.
        :return: Object containing data properties of the linked tables.
        :rtype: LinkedTableProps
        """
        from stdm.ui.composer import LinkedTableProps

        return LinkedTableProps(linked_table=self._linked_table,
                                      source_field=self._source_field,
                                      linked_field=self._linked_field)

    @staticmethod
    def linked_table_properties(dom_element):
        from stdm.ui.composer import LinkedTableProps
        """
        Creates a LinkedTableProps object which contains all the data
        properties of the linked table.
        :param dom_element: QDomElement that represents composer configuration.
        :type dom_element: QDomElement
        :return: Object containing data properties of the linked tables.
        :rtype: LinkedTableProps
        """
        linked_table = dom_element.attribute("table")
        source_field = dom_element.attribute("referenced_field")
        linked_field = dom_element.attribute("referencing_field")

        return LinkedTableProps(linked_table=linked_table,
                                              source_field=source_field,
                                              linked_field=linked_field)


class ItemConfigValueHandler(object):
    """
    Base class for setting the value of composer items based on the
    settings in the configuration item and data source value. This offloads
    handling of STDM composer item values from the document generator module
    and provides extensibility of value handling composer items. Custom
    composer item configurations need to inherit this class.
    """
    def __init__(self, composition, config_item, query_handler=None):
        self._composition = composition
        self._config_item = config_item
        self._query_handler = query_handler

    def config_item(self):
        """
        :return: Returns the composer item configuration. This should be a
        sub-class of item configuration base.
        :rtype: ItemConfigBase
        """
        return self._config_item

    def composer_item(self):
        """
        :return: Returns a composer item based on the item ID contained in
        the configuration item. Returns None if no item was found in the
        composition.
        :rtype: QgsComposerItem
        """
        return self._composition.getComposerItemById(self._config_item.item_id())

    def set_data_source_record(self, record):
        """
        Use the data source record to extract the relevant value and apply it
        to the composer item using information in the item configuration.
        Default implementation does nothing. Subclasses should override this
        method.
        :param record: Data source record containing column names and
        corresponding values.
        :type record: object
        """
        pass


class LinkedTableValueHandler(ItemConfigValueHandler):
    """
    Add supports for querying data based on information provided
    by a LinkedTableItemConfiguration object.
    """
    def _linked_table(self):
        return self.config_item().linked_table()

    def _linked_field(self):
        return self.config_item().linked_field()

    def _source_field(self):
        return self.config_item().source_field()

    def filter(self, source_value):
        """
        Query data from the linked table by matching the records whose
        linked table field matches the source value.
        :param source_value: Value in the linked table field that is used
        to filter rows in the linked table.
        :type source_value: object
        :return: Result set of the query.
        :rtype: object
        """
        if source_value is None:
            source_value = ""

        if not self._linked_table():
            return None

        ds_table, results = self._query_handler(self._linked_table(),
                                               self._linked_field(),
                                               source_value)

        return results

def col_values(cols, results):
        """
        :param cols: List containing column names whose values are to be
        retrieved from the results set.
        :type cols: list
        :param results: ResultProxy object containing values for row columns.
        :return: Returns values for the specified column names which exist
        in the results set.
        :rtype: dict
        """
        if results is None:
            return {}

        col_values = {}

        for c in cols:
            col_values[c] = [getattr(r,c) for r in results if hasattr(r,c)]

        return col_values


class ConfigurationCollectionBase(object):
    # Name of the root node of the collection element.
    collection_root = ""
    # Editor widget type to match against when creating Dom elements.
    editor_type = None
    config_root = ""
    item_config = None

    def __init__(self):
        self._config_collec = OrderedDict()

    def items(self):
        """
        :return: Collection of item configurations mapped according to
        composer identifiers.
        :rtype: OrderedDict
        """
        return self._config_collec

    def add_item_configuration(self, item_config):
        """
        Add configuration object to the collection.
        :param item_config: Custom configuration object.
        :type item_config: ItemConfigBase
        """
        item_id = item_config.item_id().strip()

        if not item_id:
            return

        self._config_collec[item_id] = item_config

    def add_item_from_element(self, item_el):
        """
        Creates an item configuration from a Dom element and adds it to the collection.
        :param item_el: Dom element.
        :type item_el: QDomElement
        :return: The created item configuration instance.
        :rtype: ItemConfigBase
        """
        if self.item_config is None:
            raise AttributeError("Item configuration class cannot be None.")

        item_conf = self.item_config.create(item_el)

        if item_conf is None:
            return None

        self.add_item_configuration(item_conf)

        return item_conf

    def collection_root(self):
        """
        :return: Name of the root node of the collection element.
        :rtype: str
        """
        raise NotImplementedError

    def editor_widget(self):
        """
        :return: Editor widget class to match against when creating Dom elements.
        :rtype: QWidget
        """
        raise NotImplementedError

    def item_configuration_root(self):
        """
        :return: Name of the root node for each item configuration in the collection.
        :rtype: str
        """
        raise NotImplementedError

    def mapping(self):
        """
        :return: A collection of item ids and corresponding configuration
        objects.
        :rtype: OrderedDict
        """
        return self._config_collec

    def item_configuration(self, item_id):
        """
        Returns a configuration object corresponding to the specified item identifier.
        :param item_id:
        :return: Configuration object corresponding to the specified item identifier.
        :rtype: ItemConfigBase
        """
        return self._config_collec.get(item_id, None)

    @classmethod
    def dom_element(cls, composer_wrapper, dom_document):
        """
        Returns a DOM element with sub-elements where each corresponds to the
        serializable properties of a configuration object.
        :param composer_wrapper: Instance of composer wrapper.
        :type composer_wrapper: ComposerWrapper
        :param dom_document: QDomDocument that represents composer configuration.
        :type dom_document: QDomDocument
        """
        if cls.editor_type is None:
            raise NotImplementedError("Item editor widget type cannot be None.")

        collection_element = dom_document.createElement(cls.collection_root)

        # Get configuration items
        for uuid,item_editor in composer_wrapper.widgetMappings().iteritems():
            composerItem = composer_wrapper.composition().getComposerItemByUuid(uuid)

            if not composerItem is None:
                if isinstance(item_editor, cls.editor_type):
                    item_config = item_editor.configuration()
                    item_config.set_item_id(uuid)
                    item_element = item_config.to_dom_element(dom_document)

                    collection_element.appendChild(item_element)

        return collection_element

    @classmethod
    def create(cls, dom_document):
        """
        Returns an instance of a ConfigurationCollectionBase subclass containing
        item configurations.
        :param dom_document: Dom document representing composer configuration.
        :type dom_document: QDomDocument
        :return: An instance of a ConfigurationCollectionBase subclass containing
        item configurations.
        :rtype: ConfigurationCollectionBase
        """
        data_source_el = dom_document.documentElement().firstChildElement("DataSource")

        if data_source_el is None:
            return None

        config_collection = cls()
        config_collec_el = data_source_el.firstChildElement(cls.collection_root)

        # Get config elements
        conf_el_list = config_collec_el.elementsByTagName(cls.config_root)
        num_items = conf_el_list.length()

        for i in range(num_items):
            conf_el = conf_el_list.item(i).toElement()

            config_collection.add_item_from_element(conf_el)

        return config_collection
