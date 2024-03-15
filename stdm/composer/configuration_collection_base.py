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
import typing

from qgis.PyQt.QtWidgets import (
    QWidget
)
from qgis.PyQt.QtXml import (
    QDomElement,
    QDomDocument
)
from qgis.core import (
    QgsLayoutItem,
    QgsLayout,
    QgsLayoutMultiFrame
)


class ItemConfigBase:
    """
    Base class for composer item configuration.
    """

    '''
    Tag Name of the DOM element containing information regarding this
    configuration.
    '''
    tag_name = ""

    def __init__(self, item_id=None):
        self._item_id = item_id or ""

    def item_id(self) -> str:
        """
        :return: Identifier of the referenced composer item.
        :rtype: str
        """
        return self._item_id

    def set_item_id(self, item_id: str):
        """
        Sets the identifier of the referenced composer item.
        :param item_id: Unique identifier of the referenced composer item.
        :type item_id: str
        """
        self._item_id = item_id

    def create_handler(self, composition: QgsLayout, query_handler=None):
        """
        Returns an object for setting the value of the composer item
        specified by this configuration item.
        :param composition: Composition object.
        :type composition: QgsLayout
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
    def create(layout_item):
        """
        #TODO: Refactor the comments

        Create a configuration object from a QLayout or Multiframe instance.
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

    def __init__(self, item_id=None, linked_table=None, source_field=None, 
                 linked_field=None, table_layout_item=None, **kwargs):
        item_id = item_id or ""
        super().__init__(item_id)

        self._linked_table = linked_table or ""
        self._source_field = source_field or ""
        self._linked_field = linked_field or ""
        self._table_layout_item = table_layout_item or None

    def linked_table(self) -> str:
        """
        :return: Name of the referenced table.
        :rtype: str
        """
        return self._linked_table

    def set_linked_table(self, table: str):
        """
        Set the name of the referenced table.
        :param table: Table name.
        :type table: str
        """
        self._linked_table = table

    def source_field(self) -> str:
        """
        :return: Column name in the referenced data source.
        :rtype: str
        """
        return self._source_field

    def set_source_field(self, field: str):
        """
        Set the name of the column in the referenced data source.
        :param field: Column name.
        """
        self._source_field = field

    def linked_field(self) -> str:
        """
        :return: Name of the matching column in the linked table.
        :rtype: str
        """
        return self._linked_field

    def set_linked_column(self, field: str):
        """
        Set the name of the matching column in the linked table.
        :param field: Column name.
        :type field: str
        """
        self._linked_field = field

    def table_layout_item(self):
        return self._table_layout_item

    def extract_from_linked_table_properties(self, ltic):
        """
        Extracts properties from a LinkedTableItemConfiguration object.
        :param ltic: Configuration item containing linked table properties.
        :type ltic: LinkedTableItemConfiguration
        """
        self._linked_field = ltic.linked_field
        self._source_field = ltic.source_field
        self._linked_table = ltic.linked_table

    def write_to_dom_element(self, dom_element: QDomElement):
        """
        Appends the configuration information to the specified DOM element.
        :param dom_element: Composer item element.
        :type dom_element: QDomElement
        """
        dom_element.setAttribute("itemid", self._item_id)
        dom_element.setAttribute("table", self._linked_table)
        dom_element.setAttribute("referenced_field", self._source_field)
        dom_element.setAttribute("referencing_field", self._linked_field)

    def _extract_from_dom_element(self, dom_element: QDomElement):
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
        from stdm.ui.composer.referenced_table_editor import LinkedTableProps

        return LinkedTableProps(linked_table=self._linked_table,
                                source_field=self._source_field,
                                linked_field=self._linked_field)

    @staticmethod
    def linked_table_properties(dom_element: QDomElement):
        from stdm.ui.composer.referenced_table_editor import LinkedTableProps
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


class ItemConfigValueHandler:
    """
    Base class for setting the value of composer items based on the
    settings in the configuration item and data source value. This offloads
    handling of STDM composer item values from the document generator module
    and provides extensibility of value handling composer items. Custom
    composer item configurations need to inherit this class.
    """

    def __init__(self, composition: QgsLayout, config_item: ItemConfigBase, query_handler=None):
        self._composition = composition
        self._config_item = config_item
        self._query_handler = query_handler

    def config_item(self) -> ItemConfigBase:
        """
        :return: Returns the composer item configuration. This should be a
        sub-class of item configuration base.
        :rtype: ItemConfigBase
        """
        return self._config_item

    def composer_item(self) -> QgsLayoutItem:
        """
        :return: Returns a composer item based on the item ID contained in
        the configuration item. Returns None if no item was found in the
        composition.
        :rtype: QgsLayoutItem
        """
        return self._composition.itemById(self._config_item.item_id())

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


def col_values(cols, results) -> dict:
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

    values = {}

    for c in cols:
        values[c] = [getattr(r, c) for r in results if hasattr(r, c)]

    return values


class ConfigurationCollectionBase:
    # Name of the root node of the collection element.
    collection_root = ""
    # Editor widget type to match against when creating Dom elements.
    editor_type = None
    config_root = ""
    item_config = None
    layout_item_type = None
    is_multi_frame = False

    def __init__(self):
        self._config_collec = OrderedDict()

    def items(self) -> OrderedDict:
        """
        :return: Collection of item configurations mapped according to
        composer identifiers.
        :rtype: OrderedDict
        """
        return self._config_collec

    def add_item_configuration(self, item_config: ItemConfigBase):
        """
        Add configuration object to the collection.
        :param item_config: Custom configuration object.
        :type item_config: ItemConfigBase
        """
        item_id = item_config.item_id().strip()

        if not item_id:
            return

        self._config_collec[item_id] = item_config

    def add_from_layout_item(self, layout_item: typing.Union[QgsLayoutItem, QgsLayoutMultiFrame]):
        """
        #TODO: Refactor comments
        Creates an item configuration from a Dom element and adds it to the collection.
        :param item_el: Dom element.
        :type item_el: QDomElement
        :return: The created item configuration instance.
        :rtype: ItemConfigBase
        """
        if self.item_config is None:
            raise AttributeError("Item configuration class cannot be None.")

        item_conf = self.item_config.create(layout_item)

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

    def item_configuration(self, item_id: str):
        """
        Returns a configuration object corresponding to the specified item identifier.
        :param item_id:
        :return: Configuration object corresponding to the specified item identifier.
        :rtype: ItemConfigBase
        """
        return self._config_collec.get(item_id, None)

    @classmethod
    def dom_element(cls, composer_wrapper, dom_document: QDomElement):
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
        for uuid, item_editor in composer_wrapper.widgetMappings().items():
            composerItem = composer_wrapper.composition().itemByUuid(uuid)

            if composerItem is not None:
                if isinstance(item_editor, cls.editor_type):
                    item_config = item_editor.configuration()
                    item_config.set_item_id(uuid)
                    item_element = item_config.to_dom_element(dom_document)

                    collection_element.appendChild(item_element)

        return collection_element

    @classmethod
    def create(cls, layout: QgsLayout):
        """
        Returns an instance of a ConfigurationCollectionBase subclass containing
        item configurations.
        :param dom_document: Dom document representing composer configuration.
        :type dom_document: QDomocument
        :return: An instance of a ConfigurationCollectionBase subclass containing
        item configurations.
        :rtype: ConfigurationCollectionBase
        """
        config_collection = cls()

        if cls.is_multi_frame:
            multi_frames = layout.multiFrames()
            for multi_frame in multi_frames:
                if isinstance(multi_frame, cls.layout_item_type):
                    config_collection.add_from_layout_item(multi_frame)

        return config_collection

    @classmethod
    def create_layout_item(cls, layout_items:list[QgsLayoutItem]):
        config_collection = cls()
        for layout_item in layout_items:
            if isinstance(layout_item, cls.layout_item_type):
                config_collection.add_from_layout_item(layout_item)
        return config_collection

    @classmethod
    def create_chart_layout(cls, layout_items:list[QgsLayoutItem], dom_doc: QDomDocument=None):
        from stdm.composer.chart_configuration import ChartConfiguration

        node_list = dom_doc.elementsByTagName('Plot')
        dom_element = node_list.at(0).toElement()

        chart_configs = {}

        for layout_item in layout_items:
            plot_type = dom_element.attribute("type")
            if not plot_type:
                return None

            plot_type_config = ChartConfiguration.types.get(plot_type, None)
            if plot_type_config is None:
                return None

            if isinstance(layout_item, cls.layout_item_type):
                config_collection = plot_type_config.create(dom_element, layout_item)
                chart_configs[plot_type] = config_collection

        return chart_configs
