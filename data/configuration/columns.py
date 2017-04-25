"""
/***************************************************************************
Name                 : BaseColumn
Description          : Container for table columns used by an Entity object.
Date                 : 26/December/2015
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
import sys
import logging
from copy import deepcopy
from collections import OrderedDict
from datetime import (
    date,
    datetime
)
from decimal import Decimal

from PyQt4.QtCore import (
    QCoreApplication
)
from PyQt4.QtGui import QApplication

from stdm.data.configuration.column_updaters import (
    base_column_updater,
    yes_no_updater,
    date_updater,
    datetime_updater,
    double_updater,
    geometry_updater,
    integer_updater,
    serial_updater,
    text_updater,
    varchar_updater
)

from stdm.data.configuration.db_items import (
    ColumnItem,
    DbItem
)
from stdm.data.configuration.entity_relation import EntityRelation
from stdm.data.pg_utils import table_view_dependencies

LOGGER = logging.getLogger('stdm')


def tr(text=''):
    """
    Alias for translating column display names so that they can be in the
    same context i.e. 'BaseColumn'.
    :param text: String to be translated.
    :type text: str
    :returns: Translated text if available, else the original string will be
    returned.
    :rtype: str
    """
    return QCoreApplication.translate('BaseColumn', text)

class BaseColumn(ColumnItem):
    """
    Represents a column which is appended to an Entity. All column types are
    registered through this BaseClass.
    """
    registered_types = OrderedDict()

    #Callable for updating the column in the database Table object.
    sql_updater = base_column_updater

    TYPE_INFO = 'BASE_COLUMN'

    def __init__(self, *args, **kwargs):
        """
        :param name: Unique name for identifying the column.
        :type name: str
        :param entity: The Entity object that the column belongs to.
        :type entity: Entity
        **Keyword arguments:**
        - *description:* Text providing more information about the column.
        - *Mandatory:* True if the column requires a value to be supplied
        when entering data. Default is False.
        - *Searchable:* True if the column can be used to filter records in
        the Entity browser. Default is True but is dependent on the subclass
        implementation.
        - *unique:* True to include a UNIQUE constraint for the column.
        - *user_tip:* Hint that will appear in the form editor as a tooltip
        for this column.
         - *index:* True to indicate that the column should be indexed.
        """
        if len(args) < 2:
            raise Exception('Constructor requires name and entity arguments.')

        name = args[0]
        entity = args[1]

        ColumnItem.__init__(self, name)

        #Internal flag used to check whether this constructor has been initialized
        self._intialized = True

        #Attributes in the database that need to monitored for any changes
        self._monitor_attrs = ['mandatory', 'searchable', 'index', 'unique' ]

        self.updated_db_attrs = {}

        self.entity = entity
        self.profile = entity.profile
        self.description = kwargs.get('description', '')
        self.index = kwargs.get('index', False)
        self.mandatory = kwargs.get('mandatory', False)
        self.searchable = kwargs.get('searchable', True)
        self.unique = kwargs.get('unique', False)
        self.user_tip = kwargs.get('user_tip', '')

        self.reset_updated_attrs()

        LOGGER.debug('%s column initialized in %s entity.',self.name, self.entity.name)

    def reset_updated_attrs(self):
        """
        Clears the collection of updated attributes.
        """
        self.updated_db_attrs = {}

    @classmethod
    def register(cls):
        """
        Registers the column type derived from this class.
        """
        BaseColumn.registered_types[cls.TYPE_INFO] = cls

    @classmethod
    def column_type(cls, type_info):
        """
        :param type_info: TYPE_INFO of the column type.
        :type type_info: str
        :return: Column type corresponding to the specified type info.
        Returns None if there is no match.
        :rtype: BaseColumn
        """
        return cls.registered_types.get(type_info, None)

    @classmethod
    def types_by_display_name(cls):
        """
        :returns: Returns a collection of registered column types by their display
        names.
        :rtype: OrderedDict
        """
        col_types_disp = OrderedDict()

        for ti, col_type in cls.registered_types.iteritems():
            col_types_disp[col_type.display_name()] = col_type

        return col_types_disp

    @classmethod
    def display_name(cls):
        """
        :returns: A friendly display name for the column. To be implemented
        by subclasses.
        :rtype: str
        """
        raise NotImplementedError

    def update(self, table, column_names):
        """
        Update the column in the database for the given Table using the
        'sql_updater' callable.
        :param table: SQLAlchemy table object that this column belongs to.
        :param column_names: Existing column names in the database for the
        given table.
        :returns: SQLAlchemy column.
        :rtype: Column
        """
        if self.sql_updater is None:
            LOGGER.debug('%s column, in %s entity, has no sql_updater '
                         'callable defined.', self.name, self.entity.name)

            return

        return self.sql_updater(table, column_names)

    def user_editable(self):
        """
        :returns: True if the column should be displayed in the list of
        columns in an Entity editor, else False.
        :rtype: bool
        """
        return True

    def property_display(self):
        """
        :returns: Return a user friendly string showing the object properties
        and corresponding values.
        :rtype: str
        """
        disp = []
        exclude = ['entity', 'profile', '_minimum', '_maximum',
                   'entity_relation']

        for k,v in self.__dict__:
            if not k in exclude:
                attr = k.replace('_', ' ').capitalize()
                disp.append(u'{0}: {1}'.format(attr, v))

        return ','.join(disp)

    def on_delete(self):
        """
        Include code for cleaning up additional column references. Default
        implementation does nothing.
        """
        pass

    def dependencies(self):
        """
        Gets the tables and views that are related to this column.
        :return: A dictionary containing a list of related entity names and
        views respectively.
        :rtype: dict
        """
        #Get all relations to this column
        child_relations = self.entity.column_children_relations(self.name)
        parent_relations = self.entity.column_parent_relations(self.name)

        r = child_relations + parent_relations

        #Get children entities
        parent_entities = [er.parent for er in child_relations if er.parent.action != DbItem.DROP]
        child_entities = [er.child for er in parent_relations if er.child.action != DbItem.DROP]

        all_entities = parent_entities + child_entities

        #Dependent entity names
        dep_ent_names = [e.name for e in all_entities]

        #Add views related to this column
        dep_views = table_view_dependencies(self.entity.name, self.name)

        return {'entities': dep_ent_names, 'views': dep_views}

    def child_entity_relations(self):
        """
        :return: Returns a list of entity relations for child entities which
        reference this column.
        :rtype: list
        """
        return self.entity.column_children_relations(self.name)

    def parent_entity_relations(self):
        """
        :return: Returns a list of entity relations for parent entities which
        reference this column. These basically correspond to entity relations
        foreign key columns.
        :rtype: list
        """
        return self.entity.column_parent_relations(self.name)

    def header(self):
        """
        :return: Returns the column name formatted with the first character
        for each word in uppercase. Underscores are replaced with a space and
        '_id' is removed if it exists.
        :rtype: str
        """
        id_text = QApplication.translate('BaseColumn', '_id')
        if id_text in self.name:
            # if foreign key or lookup column, hide 'id'
            if self.TYPE_INFO == 'FOREIGN_KEY' or self.TYPE_INFO == 'LOOKUP':
                display_name = self.name[:-3]
                display_name = display_name.replace('_', ' ').title()
            else:
            # for other columns, capitalize id to be ID
                display_name = '{} {}'.format(
                    self.name[:-3].title(), self.name[-2:].upper()
                )
        else:
            display_name = self.name.replace('_', ' ').title()

        return display_name

    def copy_attrs(self, column):
        """
        Copy the values of attributes specified in 'monitor_attrs' class
        member.
        :param column: The column object to copy attributes from.
        :type column: BaseColumn
        """
        for attr in self._monitor_attrs:
            attr_val = getattr(column, attr)

            #Set value
            setattr(self, attr, attr_val)

    def __setattr__(self, key, value):
        if hasattr(self, '_initialized'):
            if key in self._monitor_attrs:
                if getattr(self, key) != value:
                    self.updated_db_attrs[key] = value

            if len(self.updated_db_attrs) > 0 and self.action == DbItem.NONE:
                self.action = DbItem.ALTER

                #Notify parent
                self.entity.append_updated_column(self)

        object.__setattr__(self, key, value)

    def value_requires_quote(self):
        """
        :return: Return True if the column value requires quoting in an SQL
        statement. To be overidden by sub-classes.
        .. versionadded:: 1.5
        :rtype: bool
        """
        return False

    def __eq__(self, other):
        """
        Compares if the column name and entity name are equal with those
        of this object.
        :param other: Column object
        :type other: BaseColumn
        :return: Returns True if the column object is equal, else False.
        :rtype: bool
        """
        if other.name != self.name:
            return False

        if other.entity.name != self.entity.name:
            return False

        return True


class BoundsColumn(BaseColumn):
    """
    For columns types with constraints on minimum and maximum length.
    This class should not be instantiated directly but sub-classed.
    """
    TYPE_INFO = 'BOUNDS'
    SQL_MAX = 1000
    SQL_MIN = 0

    def __init__(self, *args, **kwargs):
        self._minimum = self.SQL_MIN
        self._maximum = self.SQL_MAX

        self.minimum = kwargs.pop('minimum', self.SQL_MIN)
        self.maximum = kwargs.pop('maximum', self.SQL_MAX)

        #Use default range if minimum and maximum are equal
        if self.minimum == self.maximum:
            self.minimum = self.SQL_MIN
            self.maximum = self.SQL_MAX

        BaseColumn.__init__(self, *args, **kwargs)

    def _check_type_min_max(self, val):
        """
        Ensures that the specified value is within the allowed type limits.
        """
        if val < self.SQL_MIN:
            return self.SQL_MIN

        if val > self.SQL_MAX:
            return self.SQL_MAX

        return val

    @property
    def minimum(self):
        return self._minimum

    @property
    def maximum(self):
        return self._maximum

    @minimum.setter
    def minimum(self, val):
        #Normalize to allowable limits
        val = self._check_type_min_max(val)

        if val > self._maximum:
            self._minimum = self._maximum

        else:
            self._minimum = val

    @maximum.setter
    def maximum(self, val):
        #Normalize to allowable limits
        val = self._check_type_min_max(val)

        if val < self._minimum:
            self._maximum = self._minimum

        else:
            self._maximum = val

    def can_create_check_constraints(self):
        """
        :return: Return True if the updater should issue check constraints
        for minimum and maximum values respectively.
        To be implemented by subclasses.
        .. versionadded:: 1.5
        :rtype: bool
        """
        return True


class VarCharColumn(BoundsColumn):
    """
    Variable length text.
    """
    TYPE_INFO = 'VARCHAR'
    SQL_MAX = 4000
    SQL_MIN = 0
    sql_updater = varchar_updater

    @classmethod
    def display_name(cls):
        return tr('Varying-length Text')

    def can_create_check_constraints(self):
        #No need to create constraints since the extents are set while
        # creating the column.
        return False

VarCharColumn.register()


class TextColumn(BoundsColumn):
    """
    Corresponds to the SQL text data type.
    """
    TYPE_INFO = 'TEXT'
    SQL_MIN = 0
    SQL_MAX = 1073741823
    sql_updater = text_updater

    @classmethod
    def display_name(cls):
        return tr('Unlimited-length Text')

    def can_create_check_constraints(self):
        #Not applicable.
        return False

TextColumn.register()


class IntegerColumn(BoundsColumn):
    """
    Corresponds to int SQL type.
    """
    TYPE_INFO = 'INT'
    SQL_MIN = -sys.maxint - 1
    SQL_MAX = sys.maxint
    sql_updater = integer_updater

    @classmethod
    def display_name(cls):
        return tr('Whole Number')

IntegerColumn.register()


_ff= Decimal.from_float


class DoubleColumn(BoundsColumn):
    """
    Corresponds to double precision data type.
    """
    TYPE_INFO = 'DOUBLE'
    SQL_MIN = _ff(-sys.float_info.min)
    SQL_MAX = _ff(sys.float_info.max)
    sql_updater = double_updater
    DEFAULT_PRECISION = 18
    DEFAULT_SCALE = 6

    def __init__(self, *args, **kwargs):
        # Added precision & scale in version 1.5, default is 6 decimal places
        self.precision = kwargs.pop('precision', self.DEFAULT_PRECISION)
        self.scale = kwargs.pop('scale', self.DEFAULT_SCALE)

        # Validate the numeric properties
        if self.precision < 1:
            self.precision = self.DEFAULT_PRECISION

        if self.scale < 0:
            self.scale = self.DEFAULT_SCALE

        BoundsColumn.__init__(self, *args, **kwargs)

    def _check_type_min_max(self, val):
        # Skip the checks because there is virtually no 'limit'
        return val

    @classmethod
    def display_name(cls):
        return tr('Decimal Number')

DoubleColumn.register()


class SerialColumn(IntegerColumn):
    """
    This column will not be registered and instead will be used internally
    by the configuration classes.
    """
    TYPE_INFO = 'SERIAL'
    sql_updater = serial_updater

    @classmethod
    def display_name(cls):
        return tr('Auto-increment')

    def user_editable(self):
        return False

    def can_create_check_constraints(self):
        # Values handled by the db hence no constraints should be created.
        return False


class DateColumn(BoundsColumn):
    """
    Corresponds to date data type.
    """
    TYPE_INFO = "DATE"
    SQL_MIN = date.min
    SQL_MAX = date.max
    sql_updater = date_updater
    min_use_current_date = False
    max_use_current_date = False

    def __init__(self, *args, **kwargs):
        self.min_use_current_date = kwargs.pop('min_use_current_date', False)
        self.max_use_current_date = kwargs.pop('max_use_current_date', False)

        BoundsColumn.__init__(self, *args, **kwargs)

    def value_requires_quote(self):
        return True

    @classmethod
    def display_name(cls):
        return tr('Date')

DateColumn.register()


class DateTimeColumn(BoundsColumn):
    """
    Corresponds to datetime data type.
    """
    TYPE_INFO = 'DATETIME'
    SQL_MIN = datetime.min
    SQL_MAX = datetime.max
    sql_updater = datetime_updater
    min_use_current_datetime = False
    max_use_current_datetime = False

    def __init__(self, *args, **kwargs):
        self.min_use_current_datetime = kwargs.pop(
            'min_use_current_datetime',
            False
        )
        self.max_use_current_datetime = kwargs.pop(
            'max_use_current_datetime',
            False
        )

        BoundsColumn.__init__(self, *args, **kwargs)

    def value_requires_quote(self):
        return True

    @classmethod
    def display_name(cls):
        return tr('Date with time')

DateTimeColumn.register()


class GeometryColumn(BaseColumn):
    """
    Represents 2D vector types apart from GEOMETRYCOLLECTION type.
    EPSG:4326 is the default type used if no SRID is specified.
    """
    TYPE_INFO = 'GEOMETRY'
    sql_updater = geometry_updater
    POINT, LINE, POLYGON, MULTIPOINT, MULTILINE, MULTIPOLYGON = range(0, 6)

    def __init__(self, *args, **kwargs):

        if len(args) < 3:
            raise Exception('Constructor requires name, entity and geometry '
                            'type arguments.')

        self.geom_type = args[2]
        self.srid = kwargs.pop('srid', 4326)
        self.layer_display_name = kwargs.pop('layer_display', '')

        BaseColumn.__init__(self, *args, **kwargs)

        self.searchable = False

    def layer_display(self):
        """
        :return: Name to show in the Layers TOC.
        :rtype: str
        """
        if self.layer_display_name:
            return self.layer_display_name

        return u'{0}.{1}'.format(self.entity.name, self.name)

    def geometry_type(self):
        """
        :returns: Returns the specified geometry type as a string.
        :rtype: str
        """
        if self.geom_type == GeometryColumn.POINT:
            return 'POINT'

        elif self.geom_type == GeometryColumn.LINE:
            return 'LINESTRING'

        elif self.geom_type == GeometryColumn.POLYGON:
            return 'POLYGON'

        elif self.geom_type == GeometryColumn.MULTIPOINT:
            return 'MULTIPOINT'

        elif self.geom_type == GeometryColumn.MULTILINE:
            return 'MULTILINESTRING'

        else:
            return 'MULTIPOLYGON'

    @classmethod
    def display_name(cls):
        return tr('Geometry')

GeometryColumn.register()

class BooleanColumn(BaseColumn):
    """
    Represents a True/False or Yes/No column.
    """
    TYPE_INFO = 'BOOL'
    sql_updater = yes_no_updater

    @classmethod
    def display_name(cls):
        return tr('Yes/No')

BooleanColumn.register()

class ForeignKeyColumn(IntegerColumn):
    """
    Corresponds to a foreign key reference. Child attributes are implicitly
    set hence, the caller only needs to set the parent attributes of the
    entity relation.
    """
    TYPE_INFO = 'FOREIGN_KEY'
    sql_updater = integer_updater

    def __init__(self, *args, **kwargs):
        #Reset bounds
        kwargs['minimum'] = 0
        kwargs['maximum'] = self.SQL_MAX

        IntegerColumn.__init__(self, *args, **kwargs)

        self.entity_relation = kwargs.pop('entity_relation',
                                          EntityRelation(self.entity.profile))

        self.entity_relation.child_column = self.name
        self.entity_relation.child = self.entity

        # If the entity relation is valid then add it right away to the profile
        if self.entity_relation.valid()[0]:
            self.profile.add_entity_relation(self.entity_relation)

    @property
    def parent(self):
        """
        :return: Returns the parent entity referenced by this foreign key.
        Returns None if not specified.
        .. versionadded:: 1.5
        :rtype: Entity
        """
        return self.entity_relation.parent

    def set_entity_relation_attr(self, attr, val):
        """
        Sets the specified property of the entity relation object.
        :param attr: Name of the attribute i.e. 'parent' or 'parent_column'.
        :type attr: str
        :param val: Attribute value.
        :type val: object
        """
        LOGGER.debug('Attempting to set value for %s attribute in %s '
                     'foreign key column.', attr, self.name)

        if not hasattr(self.entity_relation, attr):
            LOGGER.debug('%s attribute not found.', attr)

            return

        if attr != 'child' or attr != 'child_column':
            setattr(self.entity_relation, attr, val)

            LOGGER.debug('Value for %s attribute has been successfully set.', attr)

        '''
        Add entity relation to the collection only once the primary parent
        attributes have been set.
        '''
        if not self.entity_relation.parent is None and self.entity_relation.parent_column:
            self.profile.add_entity_relation(self.entity_relation)

    @classmethod
    def display_name(cls):
        return tr('Related Entity')

    def can_create_check_constraints(self):
        # No need since columns will be referencing pks
        return False

ForeignKeyColumn.register()


class LookupColumn(ForeignKeyColumn):
    """
    Enables a single value to be selected from a ValueList table.
    """
    TYPE_INFO = 'LOOKUP'

    def __init__(self, *args, **kwargs):
        ForeignKeyColumn.__init__(self, *args, **kwargs)

        #Set the definite entity relation properties
        self.set_entity_relation_attr('parent_column', 'id')
        self.set_entity_relation_attr('display_cols', ['name', 'code'])

    @property
    def value_list(self):
        """
        :return: Returns the value list for this lookup object
        :rtype: ValueList
        """
        return self.entity_relation.parent

    @value_list.setter
    def value_list(self, value_list):
        """
        Set the lookup ValueList object.
        :param value_list: ValueList reference.
        :type value_list: str or ValueList object.
        """
        self.set_entity_relation_attr('parent', value_list)

        #Add value list to the profile collection
        self.profile.add_entity(value_list)

    @classmethod
    def display_name(cls):
        return tr('Single Select Lookup')

LookupColumn.register()


class AdministrativeSpatialUnitColumn(ForeignKeyColumn):
    """
    Enables the attachment of AdminSpatialUnitSet information to the entity.
    """
    TYPE_INFO = 'ADMIN_SPATIAL_UNIT'

    def __init__(self, name, entity, **kwargs):
        args = [name, entity]

        ForeignKeyColumn.__init__(self, *args, **kwargs)

        #Set the parent info
        self.set_entity_relation_attr('parent', 'admin_spatial_unit_set')
        self.set_entity_relation_attr('parent_column', 'id')
        self.set_entity_relation_attr('display_cols', ['name', 'code'])

    @classmethod
    def display_name(cls):
        return tr('Administrative Spatial Unit')

AdministrativeSpatialUnitColumn.register()


class AutoGeneratedColumn(VarCharColumn):
    """
    Enables the attachment of a unique identifier code to the entity.
    .. versionadded:: 1.5
    """
    TYPE_INFO = 'AUTO_GENERATED'
    SQL_MAX = 4000
    SQL_MIN = 0
    sql_updater = varchar_updater

    def __init__(self, *args, **kwargs):

        self.prefix_source = kwargs.pop('prefix_source', '')
        self.leading_zero = kwargs.pop('leading_zero', '')
        self.separator = kwargs.pop('separator', '')

        VarCharColumn.__init__(self, *args, **kwargs)

    def can_create_check_constraints(self):
        # No need to create constraints since the extents are set while
        # creating the column.
        return False

    @classmethod
    def display_name(cls):
        return tr('Auto Generated Code')

AutoGeneratedColumn.register()

class VirtualColumn(BaseColumn):
    """
    Virtual columns are not created in the database, only the references are
    created.
    """
    TYPE_INFO = 'VIRTUAL'


class MultipleSelectColumn(VirtualColumn):
    """
    Enables the user to select one or more values from a ValueList table.
    """
    TYPE_INFO = 'MULTIPLE_SELECT'

    def __init__(self, *args, **kwargs):
        first_parent = kwargs.pop('first_parent', None)

        VirtualColumn.__init__(self, *args, **kwargs)

        self.association = self.profile.create_association_entity(
            self.name,
            first_parent=first_parent
        )
        self.association.second_parent = self.entity

        #Add association to the collection
        self.profile.add_entity(self.association)

        LOGGER.debug('%s multiple select column initialized.')

    @property
    def value_list(self):
        return self.association.first_parent

    @value_list.setter
    def value_list(self, value_list):
        """
        Set the lookup source.
        :param value_list: Lookup source.
        :type value_list: Name of the ValueList or object instance.
        """
        self.association.first_parent = value_list

    @property
    def model_attribute_name(self):
        """
        :return: Returns the corresponding attribute name of this column in
        an SQLALchemy model object.
        :rtype: str
        """
        return u'{0}_collection'.format(self.value_list.name)

    @classmethod
    def display_name(cls):
        return tr('Multiple Select Lookup')

MultipleSelectColumn.register()


class PercentColumn(DoubleColumn):
    """
    Provides a range of 0.0 to 100. Any user-defined minimum and/or maximum
    value will be overridden by 0 and 100 respectively.
    .. versionadded:: 1.5
    """
    TYPE_INFO = 'PERCENT'

    def __init__(self, *args, **kwargs):
        #Set/override user-defined min amd max respectively
        kwargs['minimum'] = 0
        kwargs['maximum'] = 100

        super(PercentColumn, self).__init__(*args, **kwargs)

    @classmethod
    def display_name(cls):
        return tr('Percent')

PercentColumn.register()

#TODO: Include ExpressionColumn

