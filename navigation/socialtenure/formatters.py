"""
/***************************************************************************
Name                 : STR Formatters
Description          : Module that provides formatters for defining how 
                       social tenure relationship information is represented
                       in the tree view.
                       the 
Date                 : 11/November/2014
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
    QApplication,
    QMessageBox
)

from sqlalchemy import (
    func,
    String
)

from stdm.ui.stdmdialog import DeclareMapping
from stdm.utils import getIndex

from .nodes import (
    BaseSTRNode,
    EntityNode,
    NoSTRNode,
    SpatialUnitNode,
    STRNode
)


class STRNodeFormatter(object):
    """
    Base class for all STR formatters.
    """

    def __init__(self, config, treeview=None, parentwidget=None):
        self._config = config

        headers = self._config.displayColumns.values()
        idx = getIndex(headers, "Id")
        if idx != -1:
            id_ref = headers.pop(idx)
        self._headers = headers

        self._data = []

        self.rootNode = BaseSTRNode(self._headers, view=treeview,
                                    parentWidget=parentwidget)

    def setData(self, data):
        """
        Set the data to be formatted through the nodes.
        """
        self._data = data

    def config(self):
        """
        :return: Entity configuration of the model.
        """
        return self._config

    def headerData(self):
        """
        Header labels.
        """
        return self._headers

    def root(self):
        """
        To be implemented by subclasses.
        Should return an object of type 'stdm.navigation.BaseSTRNode'
        """
        raise NotImplementedError(QApplication.translate("STRFormatterBase",
                                                         "Method should be implemented by subclasses"))


class TestFormatter(STRNodeFormatter):

    def root(self):
        return self.rootNode


class EntityNodeFormatter(STRNodeFormatter):
    """
    Generic formatter for rendering an STR entity's values and dependent nodes.
    """

    def __init__(self, config, treeview, parent=None):
        from stdm.data import (
            foreign_key_parent_tables,
            numeric_varchar_columns,
            spatial_tables
        )

        super(EntityNodeFormatter, self).__init__(config, treeview, parent)

        self._str_ref = "social_tenure_relationship"
        self._str_title = QApplication.translate("STRFormatterBase",
                                                 "Social Tenure Relationship")

        self._str_model = DeclareMapping.instance().tableMapping(self._str_ref)

        '''
        Set STR display mapping due to a bug in the 'displayMapping'
        function
        '''
        self._str_model_disp_mapping = {}
        if not self._str_model is None:
            self._str_model_disp_mapping = self._str_model.displayMapping()

        self._str_num_char_cols = numeric_varchar_columns(self._str_ref)
        self._fk_references = foreign_key_parent_tables(self._str_ref)
        self._current_data_source_fk_ref = self._current_data_source_foreign_key_reference()
        self._numeric_char_cols = numeric_varchar_columns(
            config.data_source_name)
        self._spatial_data_sources = spatial_tables()

    def _format_display_mapping(self, model, display_cols, filter_cols):
        """
        Creates a collection containing a tuple of column name and display
        name as the key and value (from the model) as the value.
        :return:
        """
        disp_mapping = OrderedDict()

        for c in display_cols.keys():
            if c != "id" and c in filter_cols:
                if hasattr(model, c):
                    k = c, c.replace("_", " ").title()
                    disp_mapping[k] = getattr(model, c)

        return disp_mapping

    def _foreign_key_reference_by_tablename(self, table_name):
        """
        :param table_name:
        :return: Returns foreign key information for the specified table name
        which participates in the definition of a social tenure relationship.
        """
        if len(self._fk_references) == 0:
            return None

        mod_fk_ref = None

        for fkr in self._fk_references:
            str_col, mod_table, mod_col = fkr[0], fkr[1], fkr[2]

            if mod_table == table_name:
                mod_fk_ref = mod_col, str_col

                break

        return mod_fk_ref

    def _current_data_source_foreign_key_reference(self):
        """
        :return: A tuple containing the local column name and the related
        foreign key column in the social_tenure_relationship table.
        :rtype: tuple
        """
        return self._foreign_key_reference_by_tablename(self._config.data_source_name)

    def foreign_key_references(self):
        """
        :return: Returns a list of tuples containing information on tables
        and columns related to social tenure relationship.
        :rtype: list
        """
        return self._fk_references

    def _related_str_models(self, entity_model):
        """
        :param entity_model: Related STR entity
        :type entity_model: object
        :return: Returns the related SocialTenureRelationship models based
        on the value of the corresponding entity model such as spatial
        unit, party or supporting document linked through the appropriate
        foreign keys.
        :rtype: list
        """
        if self._current_data_source_fk_ref is None:
            return []

        ent_col, str_col = self._current_data_source_fk_ref[0],\
            self._current_data_source_fk_ref[1]

        return self._models_from_fk_reference(entity_model, ent_col,
                                              self._str_model,
                                              str_col)

    def is_str_defined(self, entity_model):
        """
        :param entity_model: Related STR entity
        :type entity_model: object
        :return: Returns True if there is an existing STR relationship for a
        related STR entity.
        Otherwise False.
        :rtype: bool
        """
        str_model = self._related_str_models(entity_model)

        if str_model is None:
            return False

        else:
            return True

    def _create_str_node(self, parent_node, str_model, **kwargs):
        """
        Creates an STR Node and corresponding child nodes (from related
        entities).
        :param parent_node: Parent node
        :param str_model: STR model
        :param kwargs: Optional arguments to be passed to the STR node.
        :return: STR Node
        :rtype: STRNode
        """
        from stdm.data import numeric_varchar_columns

        display_mapping = self._format_display_mapping(str_model,
                                                       self._str_model_disp_mapping,
                                                       self._str_num_char_cols)

        str_node = STRNode(display_mapping, parent=parent_node,
                           model=str_model, **kwargs)

        # Get related entities and create their corresponding nodes
        for fkr in self._fk_references:
            str_col, mod_table, mod_col = fkr[0], fkr[1], fkr[2]

            if mod_table != self._config.data_source_name:
                mod_fk_ref = mod_col, mod_table, str_col

                r_entities = self._models_from_fk_reference(str_model, str_col,
                                                            mod_table, mod_col)

                entity_display_cols = numeric_varchar_columns(mod_table)

                for r in r_entities:
                    dm = self._format_display_mapping(r,
                                                      r.__class__.displayMapping(),
                                                      entity_display_cols)

                    node = self._spatial_textual_node(mod_table)

                    entity_node = node(dm, parent=str_node,
                                       header=mod_table.replace('_',
                                                                ' ').title(),
                                       isChild=True,
                                       model=r)

        return str_node

    def _models_from_fk_reference(self, source_model, source_column,
                                  referenced_model, referenced_column):
        """
        :return: Retrieves data models based on the foreign key reference
        information.
        """
        ref_model = referenced_model

        if hasattr(source_model, source_column):
            source_col_value = getattr(source_model, source_column)

            # Create model if string is used as referenced model
            if isinstance(ref_model, str) or isinstance(ref_model, unicode):
                ref_model = DeclareMapping.instance().tableMapping(ref_model)

            if ref_model is None:
                return []

            if hasattr(ref_model, referenced_column):
                col_prop = getattr(ref_model, referenced_column)

                # Get property type so that the filter can be applied according
                # to the appropriate type
                col_prop_type = col_prop.property.columns[0].type

                ref_model_instance = ref_model()
                ref_query_obj = ref_model_instance.queryObject()

                if not isinstance(col_prop_type, String):
                    results = ref_query_obj.filter(
                        col_prop == source_col_value).all()

                else:
                    results = ref_query_obj.filter(func.lower(
                        col_prop) == func.lower(source_col_value)).all()

                if len(results) == 0:
                    return []

                else:
                    return results

        return []

    def _is_spatial_data_source(self, ds):
        """
        Searches the data source name against the list of spatial tables.
        :param ds: Data source name
        :type ds: str
        :return: True if 'ds' is a spatial table, otherwise False.
        :rtype: bool
        """
        sp_idx = getIndex(self._spatial_data_sources, ds)

        if sp_idx == -1:
            return False

        return True

    def _spatial_textual_node(self, ds):
        """
        :param ds: Data source name
        :type ds: str
        :return: Returns an appropriate node based on whether the data source
        is a spatial or textual table or view.
        """
        if self._is_spatial_data_source(ds):
            return SpatialUnitNode

        else:
            return EntityNode

    def root(self):
        for ed in self._data:
            disp_mapping = self._format_display_mapping(ed,
                                                        self._config.displayColumns,
                                                        self._numeric_char_cols)

            # Get the related STR entities
            if self._config.data_source_name != self._str_ref:
                # Get appropriate node if data source is (non) spatial
                node = self._spatial_textual_node(
                    self._config.data_source_name)
                entity_node = node(disp_mapping, parent=self.rootNode,
                                   model=ed)
                str_entities = self._related_str_models(ed)

                # Show no STR
                if len(str_entities) == 0:
                    no_str_node = NoSTRNode(entity_node)

                else:
                    for s in str_entities:
                        str_node = self._create_str_node(entity_node, s,
                                                         isChild=True,
                                                         header=self._str_title)

            else:
                # The parent node now refers to STR data so we render
                # accordingly
                str_node = self._create_str_node(self.rootNode, ed)

        return self.rootNode
