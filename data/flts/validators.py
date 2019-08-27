"""
/***************************************************************************
Name                 : Vector Layer Validator
Description          : Module for validating a QgsVectorLayer data source
                       against the mapped entity in the database.
Date                 : 24/August/2019
copyright            : (C) 2019 by UN-Habitat and implementing partners.
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
from ConfigParser import ConfigParser
from abc import (
    ABCMeta,
    abstractmethod
)

from PyQt4.QtCore import (
    pyqtSignal,
    QObject
)

from stdm.settings import current_profile
from stdm.settings.registryconfig import (
    holders_config_path
)
from stdm.utils.reverse_dict import ReverseDict
from stdm.data.configuration import entity_model

CONFIG_COL_MAPPING_SECTION = 'ColumnMapping'

# Validation result
SUCCESS, WARNING, ERROR, UNDEFINED = range(4)


def entity_vector_layer_mapping():
    """
    :return: Returns the column mapping object based on the holders
    configuration file specified in the settings. Returns None if
    no path is defined in the settings.
    :rtype: EntityVectorLayerColumnMapping
    """
    conf_path = holders_config_path()
    if not conf_path:
        return None

    return EntityVectorLayerColumnMapping.from_configuration_file(conf_path)


def lookup_values(lookup_entity):
    """
    Fetches the lookup values and stores them in a reversible collection
    i.e. you can get the lookup values from the primary keys or the primary
    keys from the lookup values.
    :param lookup_entity: Entity for the lookup values
    :type lookup_entity: ValueList
    :return: A bi-directional collection.
    :rtype: ReverseDict
    """
    lookup_items = ReverseDict()

    # Add all lookup values in the value list table
    vl_cls = entity_model(lookup_entity)
    if not vl_cls is None:
        vl_obj = vl_cls()
        res = vl_obj.queryObject().all()
        for r in res:
            pk_id = r.id
            lk_value = r.value
            lookup_items[pk_id] = lk_value

    return lookup_items


class EntityVectorLayerColumnMapping(object):
    """
    Contains the mapping of vector layer columns to the corresponding entity
    columns as specified in the given configuration file.
    """
    def __init__(self, col_mapping=OrderedDict()):
        self._col_mapping = col_mapping

    @property
    def column_mapping(self):
        """
        :return: Returns the collection containing the column mappings in the
        source vector layer and corresponding target entity respectively i.e.
        keys correspond to the vector layer columns and values to the ones
        in the target entity.
        :rtype: OrderedDict
        """
        return self._col_mapping

    @column_mapping.setter
    def column_mapping(self, column_mapping):
        """
        Sets the collection containing the column mappings in the
        source vector layer and corresponding target entity respectively i.e.
        keys correspond to the vector layer columns and values to the ones
        :param column_mapping: Collection containg the column mapping.
        :type column_mapping: OrderedDict
        """
        self._col_mapping = column_mapping

    def is_empty(self):
        """
        :return: Returns True if there are no column mappings defined.
        :rtype: bool
        """
        return len(self._col_mapping) == 0

    def contains_source_column(self, name):
        """
        Checks if the given source column name exists.
        :param name: Name of the source column.
        :type name: str
        :return: Returns True if the source column exists, else False.
        :rtype: bool
        """
        return name in self._col_mapping

    def destination_column(self, source_column):
        """
        :param source_column: Name of the source column.
        :type source_column: str
        :return: Returns the name of the destination column matched to the
        given source column else None if the source column does not exist.
        :rtype: str
        """
        return self._col_mapping.get(source_column, None)

    @staticmethod
    def from_configuration_file(config_path):
        """
        Creates an EntityVectorLayerColumnMapping from the definition in a
        configuration file.
        :param config_path: Path to the config file.
        :type config_path: str
        :return: Returns an EntityVectorLayerColumnMapping object. Exceptions
        raised if the configuration file does not exist, the user does not
        have permissions to the file or the column mapping section is missing.
        :rtype: EntityVectorLayerColumnMapping
        """
        cp = ConfigParser()
        cp.optionxform = str
        cp.read(config_path)
        conf_mappings = cp.items(CONFIG_COL_MAPPING_SECTION)
        col_mapping = OrderedDict(conf_mappings)

        return EntityVectorLayerColumnMapping(col_mapping)


class ValidationMessage(object):
    """
    Container for a message returned from a validation process. It contains
    the message type (ERROR, WARNING or SUCCESS) and description.
    """
    def __init__(self, **kwargs):
        self.message_type = kwargs.pop('message_type', UNDEFINED)
        self.description = kwargs.pop('description', '')


class AbstractColumnValidator(object):
    """
    Abstract class providing the framework for validating column values.
    """
    __metaclass__ = ABCMeta

    def __init__(self, column=None, next_validator=None):
        self._column = column
        if self._column:
            self.setup()

        self._next_validator = next_validator

    @property
    def next_validator(self):
        """
        :return: Returns the next validator object. Returns None if not
        defined.
        :rtype: AbstractColumnValidator
        """
        return self._next_validator

    def set_next_validator(self, validator):
        """
        Sets the next validator object.
        :param validator: Validator object.
        :type validator: AbstractColumnValidator
        :return: Returns the set validator to enable chaining
        i.e. validator1.set_next_validator(validator2).set_next_validator(
        validator3
        )
        :rtype: AbstractColumnValidator
        """
        self._next_validator = validator

        return validator

    @property
    def column(self):
        """
        :return: Returns the STDM column object.
        :rtype: stdm.data.configuration.Column
        """
        return self._column

    @column.setter
    def column(self, column):
        """
        Sets the column object and performs any additional initialization
        defined in setup.
        :param column: STDM column object.
        :type column: stdm.data.configuration.Column
        """
        self._column = column
        if self._column:
            self.setup()

    def setup(self):
        """
        Perform any additional initialization once the column has been set.
        Default implementation does nothing.
        """
        pass

    @abstractmethod
    def validate(self, value, messages=None):
        """
        Validates the specified value against the column requirements based
        on its properties. Needs to be implemented by sub-classes.
        :param value: Column value.
        :type value: object
        :param messages: Messages from previous validators where applicable.
        :type messages: list
        :return: Returns a tuple containing the validation result enum
        and descriptive message. Successful validation results do not need
        any description.
        :rtype: tuple(int, str)
        """
        raise NotImplementedError

    def _create_validation_message(self, m_type, description):
        # Creates a validation message
        return ValidationMessage(
            m_type,
            description
        )


class BaseColumnValidator(AbstractColumnValidator):
    """
    Validator using the BaseColumn properties.
    """
    def validate(self, value, messages=None):
        # Check if value has been defined against a mandatory column.
        if not messages:
            messages = []

        mandatory = self._column.mandatory
        if mandatory and not value:
            msg = 'Value missing, this is a mandatory field.'
            v_msg = self._create_validation_message(ERROR, msg)
            messages.append(v_msg)
        else:
            v_msg = self._create_validation_message(SUCCESS, '')
            messages.append(v_msg)

        if self._next_validator:
            self._next_validator.validate(value, messages)
        else:
            return messages


class NumberValidator(AbstractColumnValidator):
    """
    Checks if a value is a number.
    """

    def validate(self, value, messages=None):
        if not messages:
            messages = []

        # We still check for a value if it was not defined as mandatory.
        if value:
            try:
                num = float(value)
                v_msg = self._create_validation_message(SUCCESS, '')
                messages.append(v_msg)
            except ValueError:
                msg = 'Value is not a number.'
                v_msg = self._create_validation_message(ERROR, msg)
                messages.append(v_msg)

        if self._next_validator:
            self._next_validator.validate(value, messages)
        else:
            return messages


class IntegerValidator(AbstractColumnValidator):
    """
    Check if a numeric value is an integer.
    """
    def validate(self, value, messages=None):
        if not messages:
            messages = []

        if value:
            if not isinstance(value, int):
                msg = 'Value is not an integer'
                v_msg = self._create_validation_message(WARNING, msg)
                messages.append(v_msg)
            else:
                v_msg = self._create_validation_message(SUCCESS, '')
                messages.append(v_msg)

        if self._next_validator:
            self._next_validator.validate(value, messages)
        else:
            return messages


class RangeValidator(AbstractColumnValidator):
    """
    Check against the minimum and maximum values.
    """
    def validate(self, value, messages=None):
        if not messages:
            messages = []

        if value:
            min_len = self._column.minimum
            max_len = self._column.maximum

            # Check for range based on column type
            if self._column.TYPE_INFO == 'VARCHAR':
                if len(value) > max_len:
                    msg = 'Exceeds length, maximum is {0}.'.format(max_len)
                    v_msg = self._create_validation_message(ERROR, msg)
                    messages.append(v_msg)
                else:
                    v_msg = self._create_validation_message(SUCCESS, '')
                    messages.append(v_msg)
            elif self._column.TYPE_INFO == 'INT' or \
                    self._column.TYPE_INFO == 'DOUBLE':
                if value < min_len:
                    msg = 'Lower than minimum, minimum is {0}.'.format(
                        min_len
                    )
                    v_msg = self._create_validation_message(ERROR, msg)
                    messages.append(v_msg)
                else:
                    v_msg = self._create_validation_message(SUCCESS, '')
                    messages.append(v_msg)

                if value > max_len:
                    msg = 'Greater than maximum, maximum is {0}.'.format(
                        max_len
                    )
                    v_msg = self._create_validation_message(ERROR, msg)
                    messages.append(v_msg)
                else:
                    v_msg = self._create_validation_message(SUCCESS, '')
                    messages.append(v_msg)

        if self._next_validator:
            self._next_validator.validate(value, messages)
        else:
            return messages


class LookupValidator(AbstractColumnValidator):
    """
    Checks if the specified value is a valid lookup option.
    """
    def __init__(self, **kwargs):
        super(LookupValidator, self).__init__(**kwargs)
        self._lookup_entity = kwargs.pop('lookup', None)
        self._lookup_items = {}

        # Fetch items
        if not self._lookup_entity:
            return

        self._lookup_items = lookup_values(self._lookup_entity)
        self._lookup_values = self._lookup_items.values()

    def validate(self, value, messages=None):
        if not messages:
            messages = []

        if value:
            value = unicode(value)
            if value in self._lookup_values:
                v_msg = self._create_validation_message(SUCCESS, '')
                messages.append(v_msg)
            else:
                msg = 'Value is not the lookup list'
                v_msg = self._create_validation_message(ERROR, msg)
                messages.append(v_msg)

        if self._next_validator:
            self._next_validator.validate(value, messages)
        else:
            return messages


"""
Specify validators based on column TYPE_INFO. Please note that all columns 
will always use BaseColumnValidator hence the reason it is excluded from
the collection. The validators will be chained based on the order specified 
in the list.
"""
col_type_validators = {
    'VARCHAR': [RangeValidator],
    'INT': [RangeValidator, NumberValidator, IntegerValidator],
    'DOUBLE': [RangeValidator, NumberValidator],
    'LOOKUP': [LookupValidator]
}


def column_validator_factory(column):
    """
    Creates a chain of validators using the column TYPE_INFO as defined in
    the mapping of col_type_validators. If the TYPE_INFO is not found in the
    collection then an instance of the BaseColumnValidator will be returned.
    :param column: Entity column object.
    :type column: stdm.data.configuration.columns.Column
    :return: Returns a chained list of column value validators.
    :rtype: BaseColumnValidator
    """
    init_validator = BaseColumnValidator(column)
    next_validator = init_validator

    # Return instance of BaseColumnValidator as default
    if column.TYPE_INFO not in col_type_validators:
        return init_validator

    c_validators = col_type_validators[column.TYPE_INFO]

    # Chain the validators
    for cv in c_validators:
        cv_obj = cv(column)
        next_validator.set_next_validator(cv_obj)
        next_validator = cv_obj

    return init_validator


class ValidatorException(Exception):
    """
    Raises custom validation exceptions.
    """
    pass


class EntityVectorLayerValidator(QObject):
    """
    Validates a vector layer object against the given entity object
    """
    # Flag for validation status
    NOT_STARTED, NOT_COMPLETED, FINISHED = range(3)

    # Signal for validated values
    # (row, column, list containing validation messages)
    featureValidated = pyqtSignal(tuple)

    def __init__(
            self,
            entity,
            vector_layer,
            column_mapping=None,
            exclude_columns=None,
            parent=None
    ):
        super(EntityVectorLayerValidator, self).__init__(parent)

        self._entity = entity
        # If entity is string then get the corresponding entity object
        if isinstance(self._entity, basestring):
            curr_profile = current_profile()
            if not curr_profile:
                raise TypeError('Current profile in None.')
            self._entity = curr_profile.entity(self._entity)

        self._vl = vector_layer
        self._exclude_cols = exclude_columns
        if not self._exclude_cols:
            self._exclude_cols = []

        self._ent_vl_mapping = column_mapping
        # If not defined, use default one based on file defined in the
        # settings
        if not self._ent_vl_mapping:
            self._ent_vl_mapping = entity_vector_layer_mapping()

        if not self._ent_vl_mapping:
            raise TypeError(
                'EntityVectorLayerColumnMapping could not be initialized.'
            )

        self._messages = OrderedDict()
        self._non_successful_messages = OrderedDict()
        self._status = EntityVectorLayerValidator.NOT_STARTED

    @property
    def messages(self):
        """
        :return: Returns a container with all validation messages with a
        tuple of the row_index, column_index as the key.
        :rtype: OrderedDict
        """
        return self._messages

    @property
    def non_successful_messages(self):
        """
        :return: Returns a container with only those messages that are warnings
        or errors.
        :rtype: OrderedDict
        """
        return self._non_successful_messages

    @property
    def status(self):
        """
        :return: Returns the validation status of the vector layer. Options
        are NOT_STARTED, NOT_COMPLETED (e.g. when the operation is cancelled)
        or FINISHED.
        :rtype: int
        """
        return self._status

    def reset(self):
        """
        Resets the validation session.
        """
        self._messages = []
        self._non_successful_messages = []
        self._status = EntityVectorLayerValidator.NOT_STARTED

    def _add_item_messages(self, row_index, column_index, messages):
        # Adds validation results to the respective collections
        self._messages[(row_index, column_index)] = messages

        warning_err_msgs = [m for m in messages if m.message_type == ERROR
                            or m.message_type == WARNING]
        self._non_successful_messages[(row_index, column_index)] \
            = warning_err_msgs

    @property
    def entity(self):
        """
        :return: Returns the entity object whose columns will form the basis
        of the validation based on the vector layer feature values.
        :rtype: Entity
        """
        return self._entity

    @property
    def vector_layer(self):
        """
        :return: Returns the vector layer whose features will be validated.
        :rtype: QgsVectorLayer
        """
        return self._vl

    def validate_mandatory(self):
        """
        Checks if all the mandatory columns have been specified in the
        source-destination column mapping.
        :return: Returns True if all the mandatory columns have been mapped
        else False. If False, it returns the list of mandatory column names
        that are missing.
        :rtype: tuple(bool, list)
        """
        mandatory_cols = [c.name for c in self._entity.columns.values() if c.mandatory]
        mapped_cols = self._ent_vl_mapping.column_mapping.values()

        # Get difference
        cols_difference = set(mandatory_cols).difference(set(mapped_cols))
        if len(cols_difference) == 0:
            return True, None

        return False, list(cols_difference)

    def validate_mapped_ds_columns(self):
        """
        Checks if at least one of the mapped data source columns exist in
        the vector layer.
        :return: Returns True if the one or more layers exist in the vector
        layer, else False.
        :rtype: bool
        """
        mapped_ds_cols = self._ent_vl_mapping.column_mapping.keys()
        vl_ds_cols = [f.name() for f in self._vl.fields()]

        common_cols = set(vl_ds_cols).intersection(set(mapped_ds_cols))
        if len(common_cols) == 0:
            return False

        return True

    def validate_entity_columns(self):
        """
        Checks if at least one of the mapped destination columns actually
        exist in the target entity.
        :return: Returns True if the one or more layers exist in the entity,
        else False.
        :rtype: bool
        """
        mapped_ent_cols = self._ent_vl_mapping.column_mapping.values()
        ent_cols = self._entity.columns.keys()

        common_cols = set(ent_cols).intersection(set(mapped_ent_cols))
        if len(common_cols) == 0:
            return False

        return True

    def _column_validator(self, col_name):
        # Get the validator based on the given name of the entity column.
        ent_col = self._entity.column(col_name)
        if not ent_col:
            return None

        return column_validator_factory(ent_col)

    def start(self):
        """
        Starts the validation process. It is important to ensure that
        :func:pre_validate has been called prior to executing this function.
        Emits the featureValidated signal for each feature parsed in the
        vector layer.
        """
        # Assert if vector layer is valid
        if not self._vl.isValid():
            raise ValidatorException('Data source is invalid.')

        ridx = 0
        fields = self._vl.fields()
        feats = self._vl.getFeatures()

        # Update status
        self._status = EntityVectorLayerValidator.NOT_COMPLETED

        for feat in feats:
            cidx = 0
            for f in fields:
                name = f.name()
                if self._ent_vl_mapping.contains_source_column(name):
                    col_name = self._ent_vl_mapping.destination_column(name)

                    validator = self._column_validator(col_name)
                    if not validator:
                        continue

                    attr_val = feat.attribute(name)
                    res = validator.validate(attr_val)

                    # Add result to the collection
                    self._add_item_messages(ridx, cidx, res)

                    # Raise signal
                    self.featureValidated.emit((ridx, cidx, res))

                cidx += 1

            ridx += 1

        self._status = EntityVectorLayerValidator.FINISHED





