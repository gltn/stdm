"""
/***************************************************************************
Name                 : Plot
Description          : Module for managing importing of a scheme plot
Date                 : 24/December/2019
copyright            : (C) 2019
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
import re
import itertools
from collections import OrderedDict
import csv
from PyQt4.QtCore import (
    Qt,
    QFile,
    QFileInfo,
    QIODevice,
    QVariant
)
from qgis.core import (
    QgsFeature,
    QgsField,
    QgsGeometry,
    QgsMapLayerRegistry,
    QgsProject,
    QgsVectorLayer
)
from qgis.utils import iface

NAME, IMPORT_AS, DELIMITER, HEADER_ROW, CRS_ID, \
GEOM_FIELD, GEOM_TYPE = range(7)

PARCEL_NUM, UPI_NUM, GEOMETRY, AREA = range(4)

WARNING = "Warning"


class PlotLayer:
    """
    Manages preview of plot geometric shape in a layer.
    """
    qgs_project = None

    def __init__(self, uri, name, provider_lib="memory", fields=None):
        self._uri = uri
        self._name = name
        self._provider_lib = provider_lib
        self._fields = fields
        self._data_provider = None
        self._layer = None
        self.project_instance().legendLayersAdded.connect(self._move_layer_top)

    @property
    def layer(self):
        """
        Returns created layer
        :return _layer: Layer
        :rtype _layer: QgsVectorLayer
        """
        return self._layer

    def create_layer(self):
        """
        Creates a vector layer
        """
        self._layer = QgsVectorLayer(self._uri, self._name, self._provider_lib)
        self._set_data_provider()
        self._layer.updateFields()

    def _set_data_provider(self):
        """
        Sets the data provider
        """
        self._data_provider = self._layer.dataProvider()
        fields = self._attribute_fields
        if fields:
            self._data_provider.addAttributes(fields)

    @property
    def _attribute_fields(self):
        """
        Returns QGIS attribute fields
        :return fields: QGIS attribute fields
        :rtype fields: QgsField
        """
        if not self._fields:
            return
        fields = [QgsField(name, type_)for name, type_ in self._fields]
        return fields

    def wkt_geometry(self, wkt, attributes):
        """
        Creates geometry from WKT and
        displays it in the map canvas
        :param wkt: Well-Known Text(WKT)
        :type wkt: String
        :param attributes: Attribute values
        :type attributes: Dictionary
        """
        geom = QgsGeometry.fromWkt(wkt)
        if not geom:
            return
        feature = QgsFeature()
        feature.setGeometry(geom)
        feature.setAttributes(self._attribute_values(attributes))
        self._data_provider.addFeatures([feature])

    def _attribute_values(self, attributes):
        """
        Returns attribute values given the attribute names
        :param attributes: Attribute values
        :type attributes: Dictionary
        :return values: Attribute values
        :return values: Object
        """
        if not self._fields:
            fields = self.get_fields(self._layer)
            self._fields = self._field_types(fields)
        values = [attributes.get(name) for name, type_ in self._fields]
        return values

    def get_fields(self, layer=None):
        """
        Returns a list of layer fields
        :param layer: Geometry layer
        :type layer: QgsVectorLayer
        """
        if not layer:
            layer = self._layer
        return layer.dataProvider().fields()

    @staticmethod
    def _field_types(fields):
        """
        Returns a list of layer fields and types
        :param fields: Layer fields
        :type fields: QgsField
        """
        if len(fields) > 0:
            fields = [(field.name(), field.type()) for field in fields]
            return fields

    @staticmethod
    def _move_layer_top(layers):
        """
        On new layer, move it to the top of the Layer Order Panel
        :param layers: List of layers
        :type layers: List
        """
        order = iface.layerTreeCanvasBridge().customLayerOrder()
        for _ in layers:
            order.insert(0, order.pop())
        iface.layerTreeCanvasBridge().setCustomLayerOrder(order)

    def add_map_layer(self):
        """
        Adds layer to the project
        """
        self.project_instance().addMapLayer(self._layer)

    def update_extents(self, layer=None):
        """
        Updates layer extent
        :param layer: QgsVectorLayer
        :type layer: QgsVectorLayer
        """
        if not layer:
            layer = self._layer
        layer.updateExtents()

    def remove_layer_by_name(self, name):
        """
        Removes a layer from the project given the name
        :param name: Layer name
        :type name: String
        """
        project = self.project_instance()
        layer = project.mapLayersByName(name)
        if len(layer) > 0:
            project.removeMapLayer(layer[0].id())

    @classmethod
    def remove_layer_by_id(cls, id_):
        """
        Removes a layer from the project given the id
        :param id_: Layer ID
        :type id_: String
        """
        cls.qgs_project.removeMapLayer(id_)

    def select_feature(self, layer, feature_ids):
        """
        Selects a feature given the identifier
        :param layer: Input layer
        :type layer: QgsVectorLayer
        :param feature_ids: Feature identifier
        :type feature_ids: Object
        """
        self._move_node_to_first(layer)
        if not self._is_active(layer):
            iface.setActiveLayer(layer)
        layer.select(feature_ids)

    def _move_node_to_first(self, layer):
        """
        Moves child node to first node position
        :param layer: Input layer
        :type layer: QgsVectorLayer
        """
        index = 0
        first_node = self._layer_child_node(index)
        if first_node.layerId() != layer.id():
            self._move_node(layer, index)

    @staticmethod
    def _layer_child_node(index):
        """
        Returns layer child node
        :param index: Child node index
        :param index: Integer
        :return child_node: Layer child node
        :rtype child_node: QgsLayerTreeLayer
        """
        project = QgsProject.instance()
        root = project.layerTreeRoot()
        child_node = root.children()[index]
        return child_node

    @staticmethod
    def _move_node(layer, index):
        """
        Moves child node
        :param layer: Input layer
        :type layer: QgsVectorLayer
        :param index: Index to move the node to
        :type index: Integer
        """
        project = QgsProject.instance()
        root = project.layerTreeRoot()
        layer_node = root.findLayer(layer.id())
        clone = layer_node.clone()
        parent = layer_node.parent()
        parent.insertChildNode(index, clone)
        parent.removeChildNode(layer_node)

    @staticmethod
    def _is_active(layer):
        """
        Checks if layer is active
        :param layer: Input layer
        :type layer: QgsVectorLayer
        :return: True if active
        :return: Boolean
        """
        if layer == iface.activeLayer():
            return True

    @staticmethod
    def clear_feature(layer):
        """
        Clears selected features in a layer
        :param layer: Input layer
        :type layer: QgsVectorLayer
        """
        if layer and layer.isValid():
            layer.removeSelection()

    @classmethod
    def remove_layers(cls, ids):
        """
        Removes list of layers from the project given the IDs
        :param ids: Layer IDs
        :type ids: List
        """
        cls.qgs_project.removeMapLayers(ids)

    @classmethod
    def project_instance(cls):
        """
        Returns the instance pointer
        """
        try:
            cls.qgs_project = QgsMapLayerRegistry.instance()
        except:
            cls.qgs_project = QgsProject.instance()
        else:
            return cls.qgs_project


class Item:
    """
    Items associated properties
    """
    def __init__(self, flags=None, tootltip=None, icon_id=None):
        self.flags = flags if flags else []
        self.tooltip = tootltip
        self.icon_id = icon_id


class Plot(object):
    """
    Plot associated methods
    """
    def __init__(self):
        self._reg_exes = {
            "type_str": re.compile(r'^\s*([\w\s]+)\s*\(\s*(.*)\s*\)\s*$'),
        }

    def geometry_type(self, fpath, hrow=0, delimiter=None):
        """
        Returns dominant geometry type of
        loaded plot import file - CSV/txt
        :param fpath: Plot import file absolute path
        :type fpath: String
        :param hrow: Header row number
        :type hrow: Integer
        :param delimiter: Delimiter
        :type delimiter: String
        :return: Geometry type
        :rtype: String
        """
        if self.is_pdf(fpath):
            return
        try:
            with open(fpath, 'r') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=delimiter)
                sample = itertools.islice(csv_reader, 5000)
                match_count = {}
                for row, data in enumerate(sample):
                    if row == hrow:
                        continue
                    for value in data:
                        if value is None or isinstance(value, list):
                            continue
                        geom_type, geom = self._geometry(value)
                        if geom_type:
                            if geom_type not in match_count:
                                match_count[geom_type] = 0
                                continue
                            match_count[geom_type] += 1
                return self._default_geometry_type(match_count)
        except (csv.Error, Exception) as e:
            raise e

    @staticmethod
    def is_pdf(fpath):
        """
        Checks if the file extension is PDF
        :param fpath: Plot import file absolute path
        :type fpath: String
        :return True: Returns true if the file extension is PDF
        :rtype True: Boolean
        """

        file_extension = QFileInfo(fpath).suffix()
        if file_extension == "pdf":
            return True

    def _geometry(self, wkt):
        """
        Returns geometry and geometry type given WKT data
        :param wkt: WKT data
        :type wkt: String
        :return geom_type: Geometry type
        :rtype geom_type: String
        :return geom: Geometry
        :rtype geom: QgsGeometry
        """
        geom_type = geom = None
        matches = self._reg_exes["type_str"].match(wkt)
        if matches:
            geom_type, coordinates = matches.groups()
            geom = QgsGeometry.fromWkt(wkt.strip())
            if geom_type:
                geom_type = geom_type.strip()
                geom_type = geom_type.lower().capitalize()
        return geom_type, geom

    @staticmethod
    def _default_geometry_type(type_count):
        """
        Returns default plot import file geometry type
        :param type_count: Geometry type count
        :type type_count: Dictionary
        :return geom_type: Default geometry type
        :rtype geom_type: String
        """
        geom_type = None
        if type_count:
            geom_type = max(
                type_count.iterkeys(),
                key=lambda k: type_count[k]
            )
        return geom_type

    @property
    def _geometry_types(self):
        """
        Returns a map of expected geometry types
        :return: Geometry types
        :rtype: OrderedDict
        """
        return OrderedDict({
            "Point": "Point", "Linestring": "Line", "Polygon": "Polygon"
        })

    @staticmethod
    def _decoration_tooltip(tip):
        """
        Returns decoration role tooltip item
        :param tip: Tooltip message
        :type tip: String
        :return: Decoration tooltip item
        :return: Item
        """
        return Item([Qt.DecorationRole, Qt.ToolTipRole], unicode(tip))


class UniqueParcelIdentifier:
    """
    Unique Parcel Identifier (UPI) object
    """
    def __init__(self, data_service, prefix):
        self._data_service = data_service
        self._prefix = prefix
        self._plot_counter = 0

    def aucode(self):
        """
        Returns the Scheme AUCODE
        :return: Scheme AUCODE
        :rtype: Unicode
        """
        relevant_authority = self._data_service.scheme_relevant_authority()
        return relevant_authority.au_code

    def plot_number(self):
        """
        Returns Scheme Plot Number
        :return: Plot number
        :rtype: String
        """
        if self._plot_counter == 0 and self._data_service.is_plot():
            plot_number = self._data_service.max_plot_number()
            if plot_number:
                return self._generate_plot_number(int(plot_number) + 1)
        return self._generate_plot_number(1)

    def _generate_plot_number(self, num):
        """
        Returns a new plot number
        :param num: New number
        :type num: Integer
        :return: Plot number
        :rtype: String
        """
        prefix = "000000"
        self._plot_counter += num
        suffix = str(self._plot_counter)
        prefix = prefix[:-len(suffix)]
        return prefix + suffix

    def upi(self, plot_number, aucode):
        """
        Returns Unique Parcel Identifier (UPI)
        :param plot_number: Plot number
        :type plot_number: String
        :param aucode: AUCODE
        :type aucode: Unicode
        :return upi: Unique Parcel Identifier
        :return upi: String
        """
        upi = "{0}/{1}/{2}".format(self._prefix, aucode, plot_number)
        return upi


class PlotPreview(Plot):
    """
    Manages preview of plot import data file contents
    """
    layers = {}
    dirty = {}
    type_count = {"Point": 1, "Line": 1, "Polygon": 1}

    def __init__(self, data_service, file_settings, scheme_number, parent_id):
        super(PlotPreview, self).__init__()
        self._data_service = data_service
        self._scheme_number = scheme_number
        self._parent_id = parent_id
        self._items = self._plot_layer = None
        self._num_errors = 0
        self._import_type = {"Point": "Beacons", "Line": "Servitudes", "Polygon": "Plots"}
        self._header_row = file_settings.get(HEADER_ROW) - 1
        self._delimiter = self._get_delimiter(file_settings.get(DELIMITER))
        self._geom_field = file_settings.get(GEOM_FIELD)
        self._geom_type = file_settings.get(GEOM_TYPE)
        self._crs_id = file_settings.get(CRS_ID)
        self._import_as = file_settings.get(IMPORT_AS)
        self._fpath = file_settings.get("fpath")
        self._file_fields = file_settings.get("fields")

    @staticmethod
    def _get_delimiter(name):
        """
        Returns a delimiter
        :param name: Delimiter name
        :param name: Unicode
        :return: Delimiter
        :rtype: String
        """
        delimiter = str(name.split(" ")[0]).strip()
        if delimiter == "t":
            delimiter = "\t"
        return delimiter

    def num_errors(self):
        """
        Returns number of errors encountered on preview
        :return: Number of errors on preview
        :return: Integer
        """
        return self._num_errors

    def load(self):
        """
        Loads plot import file contents
        :return: Plot import file data settings
        :rtype: List
        """
        try:
            qfile = QFile(self._fpath)
            if not qfile.open(QIODevice.ReadOnly):
                raise IOError(unicode(qfile.errorString()))
            return self._file_contents(self._fpath)
        except(IOError, OSError, csv.Error, NotImplementedError, Exception) as e:
            raise e

    def _file_contents(self, fpath):
        """
        Returns plot import file contents
        :param fpath: Plot import file absolute path
        :type fpath: String
        :return results: Plot import file contents
        :rtype results: List
        """
        results = []
        self._num_errors = 0
        try:
            upi = UniqueParcelIdentifier(self._data_service, "W")
            aucode = upi.aucode()
            with open(fpath, 'r') as csv_file:
                clean_line = self._filter_whitespace(csv_file, self._header_row)
                csv_reader = csv.DictReader(
                    clean_line,
                    fieldnames=self._file_fields,
                    delimiter=self._delimiter
                )
                self._geom_type = self._geometry_type()
                for row, data in enumerate(csv_reader):
                    contents = {}
                    self._items = {}
                    value = self._get_wkt(data, GEOMETRY)
                    if value:
                        contents[GEOMETRY] = unicode(value)
                        # value = self._get_value(
                        #     data, ("parcel", "parcel number", "id"), PARCEL_NUM
                        # )
                        # contents[PARCEL_NUM] = unicode(value)
                        value = upi.plot_number()
                        contents[PARCEL_NUM] = unicode(value)
                        contents[UPI_NUM] = unicode(upi.upi(aucode, value))
                        value = self._get_value(data, ("area",), AREA)
                        contents[AREA] = self._to_float(value, AREA)
                        contents["items"] = self._items
                        attributes = self._layer_attributes(contents)
                        self._create_layer(contents[GEOMETRY], attributes)
                        results.append(contents)
                if self._plot_layer:
                    self._plot_layer.update_extents()
                    self._plot_layer.add_map_layer()
                    self._signal_layers_removed()
        except (csv.Error, Exception) as e:
            raise e
        if results:
            PlotPreview.dirty[self._parent_id] = True
        return results

    @staticmethod
    def _filter_whitespace(in_file, hrow):
        """
        Returns non-whitespace line of data
        :param in_file: Input file
        :param in_file: TextIOWrapper
        :param hrow: Header row number
        :type hrow: Integer
        :return line: Non-whitespace line
        :return line: generator
        """
        for row, line in enumerate(in_file):
            if row == hrow:
                continue
            if not line.isspace():
                yield line

    def _geometry_type(self):
        """
        Returns dominant geometry type of
        loaded plot import file
        :return _geom_type: Dominant geometry type
        :rtype _geom_type: String
        """
        if self._geom_type not in self._geometry_types.values():
            self._geom_type = self.geometry_type(
                self._fpath, self._header_row, self._delimiter
            )
            type_ = self._geometry_types.get(self._geom_type)
            self._geom_type = type_ if type_ else self._geom_type
        return self._geom_type

    def _get_wkt(self, data, column):
        """
        Returns plot import file wkt value
        :param data: Plot import file contents
        :type data: generator
        :param column: Table view column position
        :type column: Integer
        :return value: Plot import file value
        :return value: Object
        """
        invalid_tip = self._display_tooltip("Invalid WKT", WARNING)
        value = data.get(self._geom_field)
        if value is None:
            return
        elif isinstance(value, list):
            self._items[column] = invalid_tip
            return value
        geom_type, geom = self._geometry(value)
        if not geom:
            self._items[column] = invalid_tip
            return value
        else:
            geom_type = self._geometry_types.get(geom_type)
            if not geom_type:
                self._items[column] = self._display_tooltip(
                    "Geometry type not allowed", WARNING
                )
            elif geom_type != self._geom_type:
                self._items[column] = self._display_tooltip(
                    "Does not match set geometry type ({})".format(self._geom_type),
                    WARNING
                )
            elif self._import_type.get(self._geom_type) != self._import_as:
                self._items[column] = self._display_tooltip(
                    "Does not match set import type ({})".format(self._import_as),
                    WARNING
                )
            return value

    def _get_value(self, data, field_names, column):
        """
        Returns plot import file value given field names
        :param data: Plot import file contents
        :type data: generator
        :param field_names: Plot import file field names
        :type field_names: Tuple/List
        :param column: Table view column position
        :type column: Integer
        :return value: Plot import file value
        :return value: Object
        """
        value = self._field_value(data, field_names)

        if value is None or not str(value).strip():
            value = WARNING
            self._items[column] = \
                self._decoration_tooltip("Missing value")
            self._num_errors += 1
        return value

    @staticmethod
    def _field_value(data, field_names):
        """
        Returns plot import file field value given field names
        :param data: Plot import file contents
        :type data: generator
        :param field_names: Plot import file field names
        :type field_names: Tuple/List
        :return value: Plot import file field value
        :rtype value: Object
        """
        fields = {name.lower(): name for name in data.keys()}
        for name in field_names:
            name = name.lower()
            if name in fields:
                return data.get(fields[name])

    def _to_float(self, value, column):
        """
        Casts value to float
        :param value: Value object
        :type value: Object
        :param column: Table view column position
        :type column: Integer
        :return value: Float or other object types
        :return value: Object
        """
        if self._is_number(value):
            value = float(value)
        else:
            if value != WARNING:
                self._items[column] = \
                    self._display_tooltip("Value is not a number", WARNING)
                self._num_errors += 1
        return value

    @staticmethod
    def _is_number(value):
        """
        Checks if value is a number
        :param value: Input value
        :type value: Object
        :return: True if number otherwise return False
        :rtype: Boolean
        """
        try:
            float(value)
            return True
        except (ValueError, TypeError, Exception):
            return False

    @staticmethod
    def _display_tooltip(tip, icon_id):
        """
        Returns display and decoration role tooltip item
        :param tip: Tooltip message
        :type tip: String
        :param icon_id: Icon identifier
        :type icon_id: String
        :return: Decoration tooltip item
        :return: Item
        """
        return Item(
            [Qt.DisplayRole, Qt.DecorationRole, Qt.ToolTipRole],
            unicode(tip),
            icon_id
        )

    def _layer_attributes(self, contents):
        """
        Returns layer attributes (field name, type, value)
        :param contents: Plot import file contents
        :type contents: Dictionary
        :return attributes: Layer attributes
        :rtype attributes: List
        """
        attributes = []
        headers = self.get_headers()
        for column, value in contents.items():
            attr = []
            if column == GEOMETRY or column == 'items':
                continue
            name = headers[column].name
            name = "_".join(name.split())[:10]
            attr.append(name)
            if headers[column].type == "float":
                value = self._attribute_to_float(value)
                attr.extend([QVariant.Double, value])
            else:
                value = self._replace_warning(value)
                attr.extend([QVariant.String, value])
            attributes.append(attr)
        return attributes

    @staticmethod
    def _attribute_to_float(value):
        """
        Returns float layer attribute
        :param value: Object value
        :type value: Object
        :return value: Float value
        :rtype value: Float
        """
        if isinstance(value, str):
            value = float(0)
        return value

    @staticmethod
    def _replace_warning(value):
        """
        Replaces WARNING with None type
        :param value: Object value
        :type value: Object
        :return value: String value
        :rtype value: String
        """
        if value == WARNING:
            value = None
        return value

    def _create_layer(self, wkt, attributes):
        """
        Creates a  vector layer
        :param wkt: WKT data
        :type wkt: String
        :param attributes:
        :return:
        """
        if not self._valid_setup(wkt):
            return
        if not self._plot_layer:
            geom_type, geom = self._geometry(wkt)
            uri = "{0}?crs={1}".format(geom_type, self._crs_id)
            fields = [(field, type_) for field, type_, value in attributes]
            name = self._generate_layer_name()
            self._plot_layer = PlotLayer(uri, name, fields=fields)
            self.remove_layer_by_id(self._parent_id)
            self._plot_layer.create_layer()
            self.layer.setReadOnly()
            PlotPreview.layers[self._parent_id] = self.layer
            self.type_count[self._geom_type] += 1
        value = {field: value for field, type_, value in attributes}
        self._plot_layer.wkt_geometry(wkt, value)

    def _valid_setup(self, wkt):
        """
        Checks if the setup items are
        valid for layer creation
        :param wkt: WKT data
        :type wkt: String
        :return: True if valid. Otherwise False
        :rtype: Boolean
        """
        geom_type, geom = self._geometry(wkt)
        type_name = self._geometry_types.get(geom_type)
        import_type = self._import_type.get(self._geom_type)
        if not type_name or \
                type_name != self._geom_type or \
                import_type != self._import_as:
            return False
        return True

    def _generate_layer_name(self):
        """
        Generates layer name
        :return layer_name: Layer name
        :rtype layer_name: String
        """
        layer_name = "{0}_{1}_{2}".format(
            self._scheme_number,
            self._import_type.get(self._geom_type),
            self.type_count[self._geom_type]
        )
        return layer_name

    @classmethod
    def remove_layer_by_id(cls, parent_id):
        """
        Removes layer from the registry/map canvas
        :param parent_id: Parent record/item identifier
        :type parent_id: String
        """
        if not cls.layers:
            return
        try:
            layer = cls.layers.get(parent_id)
            if layer:
                PlotLayer.remove_layer_by_id(layer.id())
        except (RuntimeError, OSError, Exception) as e:
            raise e

    @classmethod
    def remove_layers(cls):
        """
        Removes all layers from the registry/map canvas
        given layer IDs
        """
        if not cls.layers:
            return
        try:
            layer_ids = [layer.id() for layer in cls.layers.values()]
            if layer_ids:
                PlotLayer.remove_layers(layer_ids)
        except (RuntimeError, OSError, Exception) as e:
            raise e

    @property
    def layer(self):
        """
        Returns created layer
        :return _layer: Layer
        :rtype _layer: QgsVectorLayer
        """
        if self._plot_layer:
            return self._plot_layer.layer

    def _signal_layers_removed(self):
        """
        Emits layersWillBeRemoved signal
        """
        project = self._plot_layer.project_instance()
        project.layersWillBeRemoved.connect(PlotPreview._remove_stored_layer)

    @classmethod
    def _remove_stored_layer(cls, layer_ids):
        """
        Removes stored layer
        :param layer_ids: Layer IDs
        :param layer_ids: List
        """
        try:
            cls.layers = {
                key: layer
                for key, layer in cls.layers.items()
                if layer.id() not in layer_ids
            }
        except (RuntimeError, OSError, Exception) as e:
            raise e

    def select_feature(self, row):
        """
        Selects a feature given the row index
        :param row: Preview table view row index
        :type row: Integer
        """
        layer = PlotPreview.layers.get(self._parent_id)
        self._plot_layer.select_feature(layer, [row])

    def clear_feature(self, layer=None):
        """
        Clears selected features in a layer
        :param layer: Input layer
        :type layer: QgsVectorLayer
        """
        if not layer:
            layer = PlotPreview.layers.get(self._parent_id)
        self._plot_layer.clear_feature(layer)

    @classmethod
    def is_dirty(cls, fpath):
        """
        Checks if the file is valid for import
        :param fpath: Plot import file absolute path
        :type fpath: String
        :return: True
        :rtype: Boolean
        """
        return cls.dirty.get(fpath)

    @classmethod
    def dirty_file_names(cls):
        """
        Returns names of files which are valid for import
        :return file_names: Valid import file names
        :rtype file_names: List
        """
        file_names = [
            QFileInfo(fpath).fileName() for fpath in cls.dirty.keys()
        ]
        return file_names

    @classmethod
    def remove_dirty(cls, fpath):
        """
        Removes file name from dirty class variable
        :param fpath: Plot import file absolute path
        :type fpath: String
        """
        try:
            del cls.dirty[fpath]
        except KeyError:
            pass

    @classmethod
    def reset_dirty(cls):
        """
        Resets the dirty class variable
        """
        cls.dirty = {}

    def get_headers(self):
        """
        Returns column label configurations
        :return: Column/headers configurations - name and flags
        :rtype: List
        """
        return self._data_service.columns


class PlotFile(Plot):
    """
    Manages plot import data file settings
    """
    def __init__(self, data_service):
        """
        :param data_service: Plot import file data model service
        :type data_service: PlotImportFileDataService
        """
        self._data_service = data_service
        self._fpath = None
        self._fpaths = []
        self._formats = ["csv", "txt", "pdf"]
        super(PlotFile, self).__init__()

    def set_file_path(self, fpath):
        """
        Sets plot import file absolute path
        :param fpath: Plot import file absolute path
        :type fpath: String
        """
        self._fpath = fpath

    @property
    def file_path(self):
        """
        Returns plot import file absolute path
        :return _fpath: Plot import file absolute path
        :rtype _fpath: String
        """
        return self._fpath

    @property
    def file_paths(self):
        """
        Returns plot import file absolute paths
        :return _fpaths: Plot import file absolute paths
        :rtype _fpaths: List
        """
        return self._fpaths

    def remove_filepath(self, item):
        """
        Removes stored file path
        :param item: Item to be removed
        :type item: Object
        """
        if item in self._fpaths:
            self._fpaths.remove(item)

    def file_extensions(self):
        """
        Returns plot import file extensions
        :return extension: Plot import file extensions
        :rtype extension: List
        """
        extension = ["*." + fmt for fmt in self._formats]
        return extension

    @staticmethod
    def import_as():
        """
        Returns import types
        :return: Import types
        :rtype: List
        """
        return ["Beacons", "Plots", "Servitudes"]

    def delimiter_names(self):
        """
        Returns delimiters full name
        :return names: Delimiters full name
        :rtype names: OrderedDict
        """
        names = OrderedDict()
        for k, d in sorted(self.delimiters.items()):
            name = "{0} {1}".format(k, d)
            if k == "\t":
                k = "t"
                names[k] = "{0} {1}".format(k, d)
            else:
                names[k] = name
        return names

    @property
    def delimiters(self):
        """
        Returns delimiters
        :return: Delimiters
        :rtype: Dictionary
        """
        return OrderedDict({",": "Comma", ";": "Semicolon", "\t": "Tab"})

    @property
    def geometry_options(self):
        """
        Returns a map of expected geometry
        type options for the 'Type' column
        :return geom_options: Geometry type options
        :rtype geom_options: OrderedDict
        """
        geom_options = OrderedDict({"Detect": "Detect"})
        geom_options.update(self._geometry_types)
        return geom_options

    def load(self):
        """
        Loads plot import file data settings
        :return: Plot import file data settings
        :rtype: List
        """
        try:
            qfile = QFile(self._fpath)
            if not qfile.open(QIODevice.ReadOnly):
                raise IOError(unicode(qfile.errorString()))
            self.remove_filepath(self._fpath)
            if not self.is_pdf(self._fpath) and self._is_wkt(self._fpath):
                return self._file_settings(self._fpath)
            return self._file_settings(self._fpath)
        except(IOError, OSError, csv.Error, NotImplementedError, Exception) as e:
            raise e

    def _is_wkt(self, fpath):
        """
        Checks if the plot import file is a valid WKT
        :param fpath: Plot import file absolute path
        :type fpath: String
        :return: Returns true if valid
        :rtype: Boolean
        """
        try:
            fname = QFileInfo(fpath).fileName()
            if QFileInfo(fpath).size() == 0:
                raise NotImplementedError(
                    'The file "{}" is empty.'.format(fname)
                )
            delimiter = self._get_csv_delimiter(fpath)
            with open(fpath, 'r') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=delimiter)
                sample_size = 5000
                sample = itertools.islice(csv_reader, sample_size)
                count = 0
                for row, data in enumerate(sample):
                    for value in data:
                        if value is None or isinstance(value, list):
                            continue
                        geom_type, geom = self._geometry(value)
                        if geom:
                            count += 1
                total_rows = self.row_count(fpath)
                if self._calc_ratio(total_rows, sample_size, count) < 0.5:
                    raise NotImplementedError(
                        'Most of the lines in "{}" file are invalid'.format(fname)
                    )
        except (IOError, csv.Error, NotImplementedError, Exception) as e:
            raise e
        else:
            return True

    def _file_settings(self, fpath):
        """
        Returns plot import file data settings
        :param fpath: Plot import file absolute path
        :type fpath: String
        :return results: Plot import file data settings
        :rtype results: List
        """
        settings = {}
        items = {}
        try:
            header_row = 1
            row = header_row - 1
            delimiter = self._get_csv_delimiter(fpath)
            for pos, column in enumerate(self._data_service.columns):
                if pos == NAME:
                    settings[pos] = QFileInfo(fpath).fileName()
                elif pos == IMPORT_AS:
                    settings[pos] = unicode(self._get_import_type(fpath))
                elif pos == DELIMITER:
                    settings[pos] = unicode(self._delimiter_name(delimiter))
                elif pos == HEADER_ROW:
                    settings[pos] = header_row \
                        if not self.is_pdf(fpath) else unicode("")
                elif pos == GEOM_FIELD:
                    fields = self.get_csv_fields(fpath, row, delimiter)
                    settings["fields"] = fields
                    if fields:
                        fields = self.geometry_field(fpath, fields, row, delimiter)
                    else:
                        fields = ""
                    settings[pos] = unicode(fields)
                elif pos == GEOM_TYPE:
                    geom_type = self.geometry_type(fpath, row, delimiter)
                    geom_type = self._geometry_types.get(geom_type)
                    if not geom_type:
                        geom_type = "Detect"
                    settings[pos] = unicode(geom_type)
                elif pos == CRS_ID:
                    if not self.is_pdf(fpath):
                        settings[pos] = unicode(WARNING)
                        tip = "Missing Coordinate Reference System (CRS)"
                        items[pos] = self._decoration_tooltip(tip)
                settings["items"] = items
                settings["fpath"] = unicode(fpath)
        except (csv.Error, Exception) as e:
            raise e
        self._fpaths.append(fpath)
        results = [settings]
        return results

    def _get_csv_delimiter(self, fpath):
        """
        Returns default plain text common delimiter
        :param fpath: Plot import file absolute path
        :type fpath: String
        :return: Default common delimiter
        :rtype: Unicode
        """
        if self.is_pdf(fpath):
            return
        try:
            with open(fpath, 'r') as csv_file:
                dialect = csv.Sniffer().sniff(csv_file.readline(4096))
                return dialect.delimiter
        except (csv.Error, Exception) as e:
            raise e

    def _get_import_type(self, fpath):
        """
        Returns default import type based on file extension
        :param fpath: Plot import file absolute path
        :type fpath: String
        :return: Default import type
        :rtype: String
        """
        if self.is_pdf(fpath):
            return "Field Book"
        return "Plots"

    def _delimiter_name(self, delimiter):
        """
        Returns delimiter full name
        :param delimiter: Delimiter
        :type delimiter: String
        :return: Delimiter full name
        :return: String
        """
        if not delimiter:
            return ""
        elif delimiter not in self.delimiters.keys():
            return "{0} {1}".format(delimiter, "Custom")
        elif delimiter == "\t":
            return "{0} {1}".format("t", self.delimiters[delimiter])
        else:
            return "{0} {1}".format(delimiter, self.delimiters[delimiter])

    def get_csv_fields(self, fpath, hrow=0, delimiter=None):
        """
        Returns plain text field names
        :param fpath: Plot import file absolute path
        :type fpath: String
        :param hrow: Header row number
        :type hrow: Integer
        :param delimiter: Delimiter
        :type delimiter: String
        :return fields: CSV field names
        :rtype fields: List
        """
        if self.is_pdf(fpath):
            return
        try:
            with open(fpath, 'r') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=delimiter)
                fields = next(
                    (data for row, data in enumerate(csv_reader) if row == hrow), []
                )
                return fields
        except (csv.Error, Exception) as e:
            raise e

    def geometry_field(self, fpath, fields, hrow=0, delimiter=None):
        """
        Returns possible geometry field from
        list of fields given a plain text file
        :param fpath: Plot import file absolute path
        :type fpath: String
        :param fields: CSV field names
        :type fields: List
        :param hrow: Header row number
        :type hrow: Integer
        :param delimiter: Delimiter
        :type delimiter: String
        :return: Geometry field
        :rtype: String
        """
        if self.is_pdf(fpath):
            return
        try:
            with open(fpath, 'r') as csv_file:
                csv_reader = csv.DictReader(
                    csv_file, fieldnames=fields, delimiter=delimiter
                )
                match_count = {field: 0 for field in fields}
                sample = itertools.islice(csv_reader, 5000)
                for row, data in enumerate(sample):
                    if row == hrow:
                        continue
                    for field, value in data.items():
                        if value is None or isinstance(value, list):
                            continue
                        matches = self._reg_exes["type_str"].match(value)
                        if matches:
                            match_count[field] += 1
                return max(
                    match_count.iterkeys(),
                    key=lambda k: match_count[k]
                )
        except (csv.Error, Exception) as e:
            raise e

    @staticmethod
    def _calc_ratio(rows, sample, count):
        """
        Returns ratio of valid WKT lines to total or sample rows
        :param rows: Total rows/lines in a WKT file
        :type rows: Integer
        :param sample: Sampled rows/lines
        :type sample: Integer
        :param count: Number of valid rows
        :type count: Integer
        :return ratio: Ratio of valid WKT lines/rows
        :rtype ratio: Float
        """
        if sample <= rows:
            ratio = float(count) / float(sample)
        else:
            ratio = float(count) / float(rows)
        return ratio

    def row_count(self, fpath):
        """
        Returns total number of rows/lines in a CSV/txt file
        :param fpath: Plot import file absolute path
        :type fpath: String
        :return: Total number of rows/lines
        :rtype: Integer
        """
        if self.is_pdf(fpath):
            return
        try:
            with open(fpath, "r") as csv_file:
                return sum(1 for line in csv_file)
        except (csv.Error, Exception) as e:
            raise e

    def get_headers(self):
        """
        Returns column label configurations
        :return: Column/headers configurations - name and flags
        :rtype: List
        """
        return self._data_service.columns

