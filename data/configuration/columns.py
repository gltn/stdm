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
from collections import OrderedDict
from datetime import (
    date,
    datetime
)

from PyQt4.QtCore import (
    QCoreApplication
)

from .column_updaters import (
    base_column_updater,
    date_updater,
    datetime_updater,
    double_updater,
    geometry_updater,
    integer_updater,
    serial_updater,
    text_updater,
    varchar_updater
)
from .db_items import (
    ColumnItem,
    DbItem
)
from .entity_relation import EntityRelation

LOGGER = logging.getLogger('stdm')

def tr(text):
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

    def __init__(self, name, entity, **kwargs):
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
        self.updated_db_attrs = {}

        ColumnItem.__init__(self, name)
        self.entity = entity
        self.profile = entity.profile
        self.description = kwargs.get('description', '')
        self.index = kwargs.get('index', False)
        self.mandatory = kwargs.get('mandatory', False)
        self.searchable = kwargs.get('searchable', True)
        self.unique = kwargs.get('unique', False)
        self.user_tip = kwargs.get('user_tip', '')

        #Attributes in the database that need to monitored for any changes
        self._monitor_attrs = ['mandatory', 'index', 'unique' ]
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
        :returns: A friendly display name for the column. To be implemented by subclasses.
        :rtype: str
        """
        raise NotImplementedError

    def update(self, table):
        """
        Update the column in the database for the given Table using the
        'sql_updater' callable.
        :returns: SQLAlchemy column.
        :rtype: Column
        """
        if self.sql_updater is None:
            LOGGER.debug('%s column, in %s entity, has no sql_updater '
                         'callable defined.', self.name, self.entity.name)

            return

        return self.sql_updater(self, table)

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
        Include code for cleaning up additional column references.
        """
        pass

    def __setattr__(self, key, value):
        if key in self._monitor_attrs:
            if getattr(self, key) != value:
                self.updated_db_attrs[key] = value

        if len(self.updated_db_attrs) > 0 and self.action == DbItem.NONE:
            self.action = DbItem.ALTER

            #Notify parent
            self.entity.append_updated_column(self)

        object.__setattr__(self, key, value)

class BoundsColumn(BaseColumn):
    """
    For columns types with constraints on minimum and maximum length.
    This class should not be instantiated directly but sub-classed.
    """
    TYPE_INFO = 'BOUNDS'
    SQL_MAX = 1000
    SQL_MIN = 0

    def __init__(self, name, entity, **kwargs):
        self._minimum = 0
        self._maximum = 1000

        self.minimum = kwargs.pop('minimum', 0)
        self.maximum = kwargs.pop('maximum', 1000)

        BaseColumn.__init__(self, name, entity, **kwargs)

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


class VarCharColumn(BoundsColumn):
    """
    Variable length text.
    """
    TYPE_INFO = 'VARCHAR'
    SQL_MAX = 4000
    SQL_MIN = 0
    sql_updater = varchar_updater

    def __init__(self, name, entity, **kwargs):
        BoundsColumn.__init__(self, name, entity, **kwargs)

        #Enable indexing for this column type
        self.index = True

    @classmethod
    def display_name(cls):
        return tr('Varying-length text')

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
        return tr('Unlimited-length text')

TextColumn.register()


class IntegerColumn(BoundsColumn):
    """
    Corresponds to bigint SQL type.
    """
    TYPE_INFO = 'BIGINT'
    SQL_MIN = -9223372036854775808
    SQL_MAX = 9223372036854775807
    sql_updater = integer_updater

    @classmethod
    def display_name(cls):
        return tr('Whole number')

IntegerColumn.register()


class DoubleColumn(BoundsColumn):
    """
    Corresponds to double precision data type.
    """
    TYPE_INFO = 'DOUBLE'
    SQL_MIN = sys.float_info.min
    SQL_MAX = sys.float_info.max
    sql_updater = double_updater

    def _check_type_min_max(self, val):
        #Skip the checks because there is virtually no 'limit'
        return val

    @classmethod
    def display_name(cls):
        return tr('Decimal number')

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


class DateColumn(BoundsColumn):
    """
    Corresponds to date data type.
    """
    TYPE_INFO = "DATE"
    SQL_MIN = date.min
    SQL_MAX = date.max
    sql_updater = date_updater

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

    @classmethod
    def display_name(cls):
        return tr('Date with time')

DateTimeColumn.register()


class GeometryColumn(BaseColumn):
    """
    Represents 2D vector types apart from GEOMETRYCOLLECTION type.
    """
    TYPE_INFO = 'GEOMETRY'
    sql_updater = geometry_updater
    POINT, LINE, POLYGON, MULTIPOINT, MULTILINE, MULTIPOLYGON = range(0,6)

    def __init__(self, name, entity, geom_type, **kwargs):
        self.srid = kwargs.pop('srid', 4326)
        self.geom_type = geom_type

        BaseColumn.__init__(self, name, entity, **kwargs)

    def geometry_type(self):
        """
        :returns: Returns the selected geometry type as a string.
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


class ForeignKeyColumn(IntegerColumn):
    """
    Corresponds to a foreign key reference. Child attributes are implicitly
    set hence, the caller only needs to set the parent attributes of the
    entity relation.
    """
    TYPE_INFO = 'FOREIGN_KEY'
    sql_updater = integer_updater

    def __init__(self, name, entity, **kwargs):
        self.entity_relation = kwargs.pop('entity_relation', EntityRelation(entity.profile))

        #Reset bounds
        kwargs['minimum'] = 0
        kwargs['maximum'] = self.SQL_MAX

        IntegerColumn.__init__(self, name, entity, **kwargs)

        self.entity_relation.child_column = self.name
        self.entity_relation.child = self.entity

    def set_entity_relation_attr(self, attr, val):
        """
        Sets the specified property of the entity relation object.
        :param attr: Name of the attribute.
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

ForeignKeyColumn.register()


class LookupColumn(ForeignKeyColumn):
    """
    Enables a single value to be selected from a ValueList table.
    """
    TYPE_INFO = 'LOOKUP'

    def __init__(self, name, entity, **kwargs):
        ForeignKeyColumn.__init__(self, name, entity,
                                  **kwargs)

        #Set the definite entity relation properties
        self.set_entity_relation_attr('parent_column', 'id')
        self.set_entity_relation_attr('display_cols', ['name', 'code'])

    def set_value_list(self, value_list):
        """
        Set the lookup source.
        :param value_list: ValueList reference.
        :type value_list: str or ValueList object.
        """
        self.set_entity_relation_attr('parent', value_list)

    @classmethod
    def display_name(cls):
        return tr('Single Select Lookup')

LookupColumn.register()


class AdministrativeSpatialUnitColumn(ForeignKeyColumn):
    """
    Enables attaching of AdminSpatialUnitSet information to the entity.
    """
    TYPE_INFO = 'ADMIN_SPATIAL_UNIT'

    def __init__(self, entity, **kwargs):
        ForeignKeyColumn.__init__(self, 'admin_spatial_unit', entity,
                                  **kwargs)

        #Set the parent info
        self.set_entity_relation_attr('parent', 'admin_spatial_unit_set')
        self.set_entity_relation_attr('parent_column', 'id')
        self.set_entity_relation_attr('display_cols', ['name', 'code'])

    @classmethod
    def display_name(cls):
        return tr('Administrative Spatial Unit')

AdministrativeSpatialUnitColumn.register()

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

    def __init__(self, name, entity, **kwargs):
        VirtualColumn.__init__(self, name, entity, **kwargs)
        self.association = self.profile.create_association_entity(name)
        self.association.second_parent = entity

        #Add association to the collection
        self.profile.add_entity(self.association)

        LOGGER.debug('%s multiple select column initialized.')

    @property
    def value_list(self):
        return self.association.first_parent

    @value_list.setter
    def value_list(self, val_list):
        """
        Set the lookup source.
        :param val_list: Lookup source.
        :type val_list: Name of the ValueList or object instance.
        """
        self.association.first_parent = val_list

    @classmethod
    def display_name(cls):
        return tr('Multiple Select Lookup')

MultipleSelectColumn.register()

#TODO: Include ExpressionColumn

