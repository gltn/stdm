"""
/***************************************************************************
Name                 : ChartConfiguration
Description          : Container for supporting chart outputs in the
                       documents.
Date                 : 18/February/2015
copyright            : (C) 2015 by UN-Habitat and implementing partners.
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
from collections import (
    OrderedDict
)
from qgis.PyQt.QtXml import (
    QDomDocument,
    QDomElement
)
from qgis.PyQt.QtCore import (
    QTemporaryFile
)
from qgis.PyQt.QtGui import (
    QColor
)
from qgis.PyQt.QtWidgets import QApplication

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from .configuration_collection_base import (
    ConfigurationCollectionBase,
    LinkedTableValueHandler,
    LinkedTableItemConfiguration,
    col_values
)

legend_positions = OrderedDict({
    QApplication.translate("ChartConfiguration", "Automatic"): "best",
    QApplication.translate("ChartConfiguration", "Upper Right"): "upper right",
    QApplication.translate("ChartConfiguration", "Upper Left"): "upper left",
    QApplication.translate("ChartConfiguration", "Lower Left"): "lower left",
    QApplication.translate("ChartConfiguration", "Lower Right"): "lower right",
    QApplication.translate("ChartConfiguration", "Right"): "right",
    QApplication.translate("ChartConfiguration", "Center Left"): "center left",
    QApplication.translate("ChartConfiguration", "Center Right"): "center right",
    QApplication.translate("ChartConfiguration", "Lower Center"): "lower center",
    QApplication.translate("ChartConfiguration", "Upper Center"): "upper center",
    QApplication.translate("ChartConfiguration", "Center"): "center"
})

class BarValueConfiguration(object):
    tag_name = "Value"

    def __init__(self, **kwargs):
        self._value_field = kwargs.get("value_field", "")
        self._legend_name = kwargs.get("legend_name", "")
        self._fill_color = kwargs.get("fill_color", "")

    def value_field(self):
        return self._value_field

    def set_value_field(self, field):
        self._value_field = field

    def legend_name(self):
        return self._legend_name

    def set_legend_name(self, name):
        self._legend_name = name

    def fill_color(self):
        return self._fill_color

    def set_fill_color(self, color):
        if isinstance(color, QColor):
            color = color.name()

        self._fill_color = color

    def to_dom_element(self, dom_document, parent_element):
        """
        Serializes 'BarConfigurationValue' attributes to DOM element and
        appends it as a child of the 'parent_element'.
        :param dom_document: Root composer element.
        :type dom_document: QDomDocument
        :param parent_element: DOM element in which the
        'BarConfigurationValue' element will be appended to.
        :type parent_elemente: QDomElement
        """
        bar_cfg_element = dom_document.createElement(self.tag_name)
        bar_cfg_element.setAttribute("field", self._value_field)
        bar_cfg_element.setAttribute("legend_name", self._legend_name)
        bar_cfg_element.setAttribute("fill_color", self._fill_color)
        parent_element.appendChild(bar_cfg_element)

    @staticmethod
    def create(dom_element):
        """
        Creates a 'BarConfigurationValue' object from the corresponding
        DOM element.
        :param dom_element: DOM element containing 'BarConfigurationValue'
        attributes.
        :type dom_element: QDOMElement
        :return: 'BarConfigurationValue' object from the corresponding
        DOM element.
        :rtype: BarValueConfiguration
        """
        bar_cfg = BarValueConfiguration()
        bar_cfg.set_fill_color(dom_element.attribute("fill_color"))
        bar_cfg.set_legend_name(dom_element.attribute("legend_name"))
        bar_cfg.set_value_field(dom_element.attribute("field"))

        return bar_cfg

class ChartConfiguration(LinkedTableItemConfiguration):
    tag_name = "Plot"
    types = {}
    plot_type = ""
    _title = ""
    _axis_back_color = ""
    _legend = True
    _legend_pos = 'best'
    _legend_title = QApplication.translate("ChartConfiguration", "Legend")
    _x_label = ""
    _x_field = ""
    _y_label = ""
    _y_field = ""
    _replace_none_by_zero = True

    @classmethod
    def register(cls):
        """
        Registers plot configuration objects in the chart registry.
        :param cls: Contains configuration information for a specific
        chart type. Subclass of 'ChartConfiguration'.
        :type cls: ChartConfiguration
        """
        try:
            if cls.plot_type:
                ChartConfiguration.types[cls.plot_type] = cls

        except AttributeError:
            raise AttributeError("Plot type attribute is missing")

    def write_source_to_dom_element(self, dom_element):
        """
        Appends the linked table configuration information to the specified
        DOM element.
        :param dom_document: Composer item element.
        :type dom_document: QDomElement
        """
        dom_element.setAttribute("table", self._linked_table)
        dom_element.setAttribute("referenced_field", self._source_field)
        dom_element.setAttribute("referencing_field", self._linked_field)

    def to_dom_element(self, dom_document, plot_type):
        """
        :param dom_document: Root composer element.
        :type dom_document: QDomDocument
        :param plot_type: String denoting the type of the plot e.g. bar, pie.
        :type plot_type: str
        :return: A XML DOM element that contains the chart configuration
        settings.
        :rtype: QDomElement
        """
        plot_element = dom_document.createElement(self.tag_name)
        plot_element.setAttribute("itemid", self._item_id)
        plot_element.setAttribute("type", plot_type)
        plot_element.setAttribute("title", self._title)
        plot_element.setAttribute("back_color", self._axis_back_color)
        plot_element.setAttribute("legend", self._legend)
        plot_element.setAttribute("legend_position", self._legend_pos)
        plot_element.setAttribute("legend_title", self._legend_title)
        plot_element.setAttribute("x_label", self._x_label)
        plot_element.setAttribute("x_field", self._x_field)
        plot_element.setAttribute("y_label", self._y_label)
        plot_element.setAttribute("y_field", self._y_field)
        plot_element.setAttribute("replace_none_by_zero", self._replace_none_by_zero)

        self.write_source_to_dom_element(plot_element)

        return plot_element

    def title(self):
        """
        :return: Plot _title
        :rtype: str
        """
        return self._title

    def set_title(self,title):
        """
        Set the plot _title
        :param title: Plot _title
        :type title: str
        """
        self._title = title

    def axis_backcolor(self):
        """
        :return: Backcolor in the format '#RRGGBB'.
        :rtype: str
        """
        return self._axis_back_color

    def set_axis_backcolor(self, backcolor):
        """
        Set the backcolor of the plot axis
        :param backcolor: Backcolor of the plot axis in the format '#RRGGBB'.
        :type backcolor: str
        """
        self._axis_back_color = backcolor

    def insert_legend(self):
        """
        :return: Returns 'True' if a legend item is to be inserted in the
        axes else the legend will not be inserted.
        :rtype: bool
        """
        return self._legend

    def set_insert_legend(self, insert):
        """
        Set 'True' if a legend item is to be inserted else
        the legend will not be inserted.
        :param insert: 'True' to insert a legend item.
        :type insert: bool
        """
        if self._legend != insert:
            self._legend = insert

    def legend_position(self):
        """
        :return: Returns the location of the legend item.
        :rtype: str
        """
        return self._legend_pos

    def set_legend_position(self, pos):
        """
        Set the location of the legend item.
        :param pos: Location of the legend items
        :type pos: str
        """
        self._legend_pos = pos

    def legend_title(self):
        """
        :return: Display name to appear on top of the legend item.
        :rtype: str
        """
        return self._legend_title

    def set_legend_title(self, legend_title):
        """
        Set the display name of the legend item.
        :param legend_title: Display name of the legend item.
        :type legend_title: str
        """
        self._legend_title = legend_title

    def x_label(self):
        """
        :return: Title of the x-axis.
        :rtype: str
        """
        return self._x_label

    def set_x_label(self, x_label):
        """
        Set the _title of the x-axis.
        :param x_label: X-axis _title.
        :type x_label: str
        """
        self._x_label = x_label

    def x_field(self):
        """
        :return: Name of the database table/view column that contains values
        for the x-axis.
        :rtype: str
        """
        return self._x_field

    def set_x_field(self, x_field):
        """
        Set the name of the database table/view column that contains values
        for the x-axis.
        :param x_field: Name of the database table/view column that contains values
        for the x-axis.
        :type x_field: str
        """
        self._x_field = x_field

    def y_label(self):
        """
        :return: Title of the y-axis.
        :rtype: str
        """
        return self._y_label

    def set_y_label(self, y_label):
        """
        Set the _title of the y-axis.
        :param y_label: Y-axis _title.
        :type y_label: str
        """
        self._y_label = y_label

    def y_field(self):
        """
        :return: Name of the database table/view column that contains values
        for the y-axis.
        :rtype: str
        """
        return self._y_field

    def set_y_field(self, y_field):
        """
        Set the name of the database table/view column that contains values
        for the y-axis.
        :param y_field: Name of the database table/view column that contains values
        for the y-axis.
        :type y_field: str
        """
        self._y_field = y_field

    def replace_none_by_zero(self):
        """
        :return: True if 'None' datasource values should be replaced by zero.
        If False, then the values will be omitted.
        :rtype: bool
        """
        return self._replace_none_by_zero

    def set_replace_none_by_zero(self, replace):
        """
        Set True if None datasource values should be replaced by zero.
        If False, then the values will be omitted.
        :param replace: Replace 'None' values
        :type replace: bool
        """
        self._replace_none_by_zero = replace

    def _set_base_properties(self, dom_element):
        """
        Set the base properties of this object by extracting the property
        values from the dom_element.
        :param dom_element: Dom element containing chart properties.
        :type dom_element: QDomElement
        """
        self._title = dom_element.attribute("title")
        self._axis_back_color = dom_element.attribute("back_color")
        self._legend_pos = dom_element.attribute("legend_position")
        self._legend_title = dom_element.attribute("legend_title")
        self._x_label = dom_element.attribute("x_label")
        self._x_field = dom_element.attribute("x_field")
        self._y_label = dom_element.attribute("y_label")
        self._y_field = dom_element.attribute("y_field")

        insert_legend = dom_element.attribute("legend")
        if insert_legend == "0":
            self._legend = False
        else:
            self._legend = True

        replace_by_zero = dom_element.attribute("replace_none_by_zero")
        if replace_by_zero == "0":
            self._replace_none_by_zero = False
        else:
            self._replace_none_by_zero = True

        #Set base linked table properties
        self._extract_from_dom_element(dom_element)

    @staticmethod
    def create(dom_element):
        """
        Create a ChartConfiguration object from a QDomElement instance.
        :param dom_element: QDomElement that represents composer configuration.
        :type dom_element: QDomElement
        :return: ChartConfiguration instance whose properties have been
        extracted from the composer document instance.
        :rtype: TableConfiguration
        """
        plot_type = dom_element.attribute("type")
        if not plot_type:
            return None

        plot_type_config = ChartConfiguration.types.get(plot_type,None)
        if plot_type_config is None:
            return None

        return plot_type_config.create(dom_element)

    def create_handler(self, composition, query_handler=None):
        """
        :return: Returns the item value handler for the composer table item.
        :rtype: ItemConfigValueHandler
        """
        return NotImplementedError("Chart handlers only supported in subclasses")

class ChartConfigurationCollection(ConfigurationCollectionBase):
    """
    Class for managing a collection of ChartConfiguration objects.
    """
    from stdm.ui.composer.composer_chart_config import ComposerChartConfigEditor

    collection_root = "Charts"
    editor_type = ComposerChartConfigEditor
    config_root = ChartConfiguration.tag_name
    item_config = ChartConfiguration

class ChartItemValueHandler(LinkedTableValueHandler):
    """
    For implementing common functions that can shared across subclasses.
    """
    font_props = {'color' : '#000000',
        'weight' : 'bold'
        }
    def __init__(self, *args):
        LinkedTableValueHandler.__init__(self,*args)
        self._fig, self._ax = plt.subplots()
        self._legend_items = OrderedDict()

        #Clear figure and axes
        #self.clear_figure()
        #self.clear_axes()

    def add_legend_artist(self, label, artist):
        """
        Add a legend item to the collection for rendering legend items
        on the axes.
        """
        if len(artist) > 0:
            self._legend_items[label] = artist[0]

    def insert_legend(self):
        """
        Places a legend item in the axes using the items in the legend items
        collection.If there are no items then no legend will be inserted.
        """
        labels = self._legend_items.keys()
        artists = self._legend_items.values()

        if len(labels) > 0:
            self._ax.legend(tuple(artists), tuple(labels),
                            loc=self.config_item().legend_position(),
                            shadow=True)

    def set_y_label(self, label):
        if label:
            self._ax.set_ylabel(label, fontdict=self.axes_font_props())

    def set_x_ticklabels(self, labels):
        self._ax.set_xticklabels(labels)

    def set_title(self, title):
        self._ax.set_title(title, fontdict=self.title_font_props())

    def clear_figure(self):
        self._fig.clf()

    def clear_axes(self):
        self._ax.cla()

    def axes_font_props(self):
        """
        :return: Returns the default font properties for applying in axes
        labels.
        :rtype: dict
        """
        axes_font_props = dict(self.font_props)
        axes_font_props["size"] = 14

        return axes_font_props

    def title_font_props(self):
        """
        :return: Returns the default font properties for applying in the
        plot title.
        :rtype: dict
        """
        title_font_props = dict(self.font_props)
        title_font_props["size"] = 18

        return title_font_props

    def _recode_values(self, values):
        """
        Scans the input values for 'None' types and performs the
        appropriate actions based on the specified value of
        'replace_none_by_zero' property in the configuration object. If
        'replace_none_by_zero' is False then the (None or str type) values are
        removed from the collection; else it is replaced by zero.
        :param values: Raw collection containing the values to be scanned.
        :type values: list
        :return: A sequence where 'None' types have been removed or
        replaced depending on the configuration of 'replace_none_by_zero' in
        the configuration object.
        :rtype: tuple
        """
        val_arr = np.array(values)
        #Index of items to remove
        rem_idx = []

        if self.config_item().replace_none_by_zero():
            val_arr = np.where(val_arr == np.array(None), 0, val_arr)
            val_arr = val_arr.tolist()

        else:
            rem_idx = list(np.where(val_arr == np.array(None))[0])
            for i in rem_idx:
                values.pop(i)

            val_arr = values

        return val_arr, rem_idx

    def render_plot(self, tight_layout=False):
        """
        Saves the pyplot instance as an image in the OS's temp folder
        then refers the absolute path of the image to the QgsComposerPicture
        item.
        """
        chart_tmp = QTemporaryFile()
        if chart_tmp.open():
            tmp_file_name = chart_tmp.fileName()

            if tight_layout:
                plt.tight_layout()

            plt.savefig(tmp_file_name, format="tif", dpi=200)

            #Set path of picture item
            self.composer_item().setPicturePath(tmp_file_name)

        else:
            raise RuntimeError("Chart item could not be rendered")

class VerticalBarValueHandler(ChartItemValueHandler):
    """
    Handler for vertical bar graphs.
    """
    def set_data_source_record(self, record):
        chart_item = self.composer_item()

        if chart_item is None:
            return

        '''
        If there is no linked table then exit process since it is the primary
        data source.
        '''
        linked_table = self.config_item().linked_table()
        if not linked_table:
            return

        source_field = self._source_field()
        source_col_value = getattr(record, source_field, None)

        results = self.filter(source_col_value)
        if len(results) == 0:
            return

        value_fields = self.config_item().value_fields()

        #Append x-field to fetch x values as well
        col_value_fields = []
        col_value_fields.extend(value_fields)
        col_value_fields.append(self.config_item().x_field())
        column_values = col_values(col_value_fields,results)

        x_values = column_values[self.config_item().x_field()]

        N = len(x_values)
        pos = np.arange(N)
        width = 0.35

        #For use in setting limits along y-axis
        max_value = 0

        #Add vertical bars based on bar configuration values
        for i, vf in enumerate(value_fields):
            value_cfg = self.config_item().value_configuration_by_name(vf)
            if not value_cfg is None:
                #Recode values accordingly
                recoded_values, rem_idx = self._recode_values(column_values[vf])

                #Remove values based on indexes containing invalid values
                if len(rem_idx):
                    pass

                mv = max(recoded_values)
                if mv > max_value:
                    max_value = mv

                field_values = tuple(recoded_values)
                x_delta = width * i
                rect = self._ax.bar(pos + x_delta, field_values, width, color=value_cfg.fill_color())

                #Get legend label
                legend_label = value_cfg.legend_name()
                #If legend name is not defined then use the field name
                if not legend_label:
                    legend_label = vf

                self.add_legend_artist(legend_label, rect)

        self.set_y_label(self.config_item().y_label())

        #Centre x-tick labels
        x_tick_pos = (width * len(value_fields))/2
        self._ax.set_xticks(pos + x_tick_pos)

        self.set_x_ticklabels(tuple(x_values))
        self.set_title(self.config_item().title())
        self._ax.set_xlabel(self.config_item().x_label(), fontdict=self.axes_font_props())

        #Set limits for proper scaling of the bars along the respective axes
        self._ax.set_xlim((-0.05, len(x_values)))
        self._ax.set_ylim((0, (max_value + 0.1)))

        #Insert legend if enabled
        if self.config_item().insert_legend():
            self.insert_legend()

        self.render_plot()

class VerticalBarConfiguration(ChartConfiguration):
    """
    Configuration for vertical bar graph.
    """
    plot_type = "vbar"

    def __init__(self, **kwargs):
        super(VerticalBarConfiguration, self).__init__(**kwargs)
        self._value_cfgs = OrderedDict()

    def value_configurations(self):
        """
        :return: Returns a collection of value configurations contained in
        the object.
        :rtype: list
        """
        return self._value_cfgs.values()

    def value_fields(self):
        """
        :return: Returns a collection of names representing the
        database value fields.
        :rtype: list
        """
        return self._value_cfgs.keys()

    def add_value_configuration(self, value_cfg):
        """
        Adds a 'BarValueConfiguration' object into the collection. Any
        existing 'BarValueConfiguration' object with the same value field
        will be replaced.
        :param value_cfg: 'BarValueConfiguration' object.
        :type value_cfg: BarValueConfiguration
        """
        self._value_cfgs[value_cfg.value_field()] = value_cfg

    def value_configuration_by_name(self, field):
        """
        :param field: Name of the value field.
        :type field: str
        :return: Returns a 'BarValueConfiguration' object based on the
        name of the value field. 'None' is returned if no corresponding
        object is found.
        :rtype: BarValueConfiguration
        """
        return self._value_cfgs.get(field, None)

    def to_dom_element(self, dom_document):
        vbar_config_el = super(VerticalBarConfiguration, self).to_dom_element(dom_document, self.plot_type)

        #Append bar value configurations
        for cfg in self.value_configurations():
            cfg.to_dom_element(dom_document, vbar_config_el)

        return vbar_config_el

    def create_handler(self, composition, query_handler=None):
        return VerticalBarValueHandler(composition, self, query_handler)

    @staticmethod
    def create(dom_element):
        #Create new instance and extract properties from dom element.
        vbar_config = VerticalBarConfiguration()
        vbar_config._set_base_properties(dom_element)

        #Get barconfig elements
        bar_cfg_el_lst = dom_element.elementsByTagName(BarValueConfiguration.tag_name)
        for i in range(bar_cfg_el_lst.length()):
            bar_cfg_el = bar_cfg_el_lst.item(i).toElement()
            bar_cfg = BarValueConfiguration.create(bar_cfg_el)

            vbar_config.add_value_configuration(bar_cfg)

        return vbar_config

VerticalBarConfiguration.register()





