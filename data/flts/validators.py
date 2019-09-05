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
    QObject,
    QThread
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
    def __init__(self, col_mapping=None):
        self._col_mapping = col_mapping
        if not self._col_mapping:
            self._col_mapping = OrderedDict()

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


def message_type_str(message_type):
    """
    Converts the message type enumeration to the equivalent string
    representation.
    :param message_type: Message type enumeration.
    :type message_type: int
    :return: Returns the string equivalent of the message type
    enumeration.
    :rtype: str
    """
    if message_type == SUCCESS:
        return 'Success'
    elif message_type == ERROR:
        return 'Error'
    elif message_type == WARNING:
        return 'Warning'
    elif message_type == UNDEFINED:
        return 'Undefined'
    else:
        return 'Unknown'


class ValidationMessage(object):
    """
    Container for a message returned from a validation process. It contains
    the message type (ERROR, WARNING or SUCCESS) and description.
    """
    def __init__(self, **kwargs):
        self.message_type = kwargs.pop('message_type', UNDEFINED)
        self.description = kwargs.pop('description', '')

    def __str__(self):
        return '{0}: {1}'.format(
            message_type_str(self.message_type).upper(),
            self.description
        )

    def __unicode__(self):
        return u'{0} - {1}'.format(
            message_type_str(self.message_type),
            self.description
        )

    def __repr__(self):
        return '{0}({1}, {2})'.format(
            self.__class__.__name__,
            message_type_str(self.message_type),
            self.description
        )


class AbstractColumnValidator(object):
    """
    Abstract class providing the framework for validating column values.
    """
    __metaclass__ = ABCMeta

    def __init__(self, column=None, next_validator=None):
        self._column = column
        if self._column:
            self.setup()
            
        self._validation_messages = []
        self._next_validator = next_validator
        if self._next_validator:
            self._validation_messages =self._next_validator.messages

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
        self._validation_messages = validator.messages

        return validator

    @property
    def messages(self):
        """
        :return: Returns a list of messages set by this as well as previous
        validators.
        :rtype: list
        """
        return self._validation_messages

    def add_validation_message(self, message):
        """
        Adds a message from a validation operation.
        :param message: Validation message.
        :type message: ValidationMessage
        """
        self._validation_messages.append(message)

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
            message_type=m_type,
            description=description
        )


class BaseColumnValidator(AbstractColumnValidator):
    """
    Validator using the BaseColumn properties.
    """
    def validate(self, value, messages=None):
        # Check if value has been defined against a mandatory column.
        mandatory = self._column.mandatory
        if mandatory and not value:
            msg = 'Value missing, this is a mandatory field.'
            v_msg = self._create_validation_message(ERROR, msg)
            self.add_validation_message(v_msg)
        else:
            v_msg = self._create_validation_message(SUCCESS, '')
            self.add_validation_message(v_msg)

        if self._next_validator:
            return self._next_validator.validate(value, messages)
        else:
            return self._validation_messages


class NumberValidator(AbstractColumnValidator):
    """
    Checks if a value is a number.
    """
    def validate(self, value, messages=None):
        # We still check for a value if it was not defined as mandatory.
        if value:
            try:
                num = float(value)
                v_msg = self._create_validation_message(SUCCESS, '')
                self.add_validation_message(v_msg)
            except ValueError:
                msg = 'Value is not a number.'
                v_msg = self._create_validation_message(ERROR, msg)
                self.add_validation_message(v_msg)

        if self._next_validator:
            return self._next_validator.validate(value, messages)
        else:
            return self._validation_messages


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
                self.add_validation_message(v_msg)
            else:
                v_msg = self._create_validation_message(SUCCESS, '')
                self.add_validation_message(v_msg)

        if self._next_validator:
            return self._next_validator.validate(value, messages)
        else:
            return self._validation_messages


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
                value = unicode(value)
                if len(value) > max_len:
                    msg = 'Exceeds length, maximum is {0}.'.format(max_len)
                    v_msg = self._create_validation_message(ERROR, msg)
                    self.add_validation_message(v_msg)
                else:
                    v_msg = self._create_validation_message(SUCCESS, '')
                    self.add_validation_message(v_msg)
            elif self._column.TYPE_INFO == 'INT' or \
                    self._column.TYPE_INFO == 'DOUBLE':
                if value < min_len:
                    msg = 'Lower than minimum, minimum is {0}.'.format(
                        min_len
                    )
                    v_msg = self._create_validation_message(ERROR, msg)
                    self.add_validation_message(v_msg)
                else:
                    v_msg = self._create_validation_message(SUCCESS, '')
                    self.add_validation_message(v_msg)

                if value > max_len:
                    msg = 'Greater than maximum, maximum is {0}.'.format(
                        max_len
                    )
                    v_msg = self._create_validation_message(ERROR, msg)
                    self.add_validation_message(v_msg)
                else:
                    v_msg = self._create_validation_message(SUCCESS, '')
                    self.add_validation_message(v_msg)

        if self._next_validator:
            return self._next_validator.validate(value, messages)
        else:
            return self._validation_messages


class LookupValidator(AbstractColumnValidator):
    """
    Checks if the specified value is a valid lookup option.
    """
    def __init__(self, **kwargs):
        self._lookup_entity = None
        c = kwargs.get('column', None)
        if c:
            self._lookup_entity = c.value_list

        self._lookup_items = {}
        self._lookup_values = []

        # Init parent
        super(LookupValidator, self).__init__(**kwargs)

    def setup(self):
        # Fetch items
        if not self._lookup_entity:
            return

        self._lookup_items = lookup_values(self._lookup_entity)
        # Convert values to lower case for comparison purposes
        self._lookup_values = [v.lower() for v in self._lookup_items.values()]

    def validate(self, value, messages=None):
        if value:
            value = unicode(value)
            if value.lower() in self._lookup_values:
                v_msg = self._create_validation_message(SUCCESS, '')
                self.add_validation_message(v_msg)
            else:
                msg = 'Value is not in the lookup list. \nAvailable options:' \
                      ' {0}'.format(', '.join(self._lookup_items.values()))
                v_msg = self._create_validation_message(ERROR, msg)
                self.add_validation_message(v_msg)

        if self._next_validator:
            return self._next_validator.validate(value, messages)
        else:
            return self._validation_messages


"""
Specify validators based on column TYPE_INFO. Please note that all columns 
will always use BaseColumnValidator hence the reason it is excluded from
the collection. The validators will be chained based on the order specified 
in the list.
"""
col_type_validators = {
    'VARCHAR': [RangeValidator],
    'INT': [NumberValidator, IntegerValidator, RangeValidator],
    'DOUBLE': [NumberValidator, RangeValidator,],
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
        cv_obj = cv(column=column)
        next_validator.set_next_validator(cv_obj)
        next_validator = cv_obj

    return init_validator


class ValidatorException(Exception):
    """
    Raises custom validation exceptions.
    """
    pass


class ValidationResult(object):
    """
    Container for messages from a validation process for a given data cell.
    """
    def __init__(self, ridx, cidx, messages):
        self.ridx = ridx
        self.cidx = cidx
        self.messages = messages
        self._success_msgs = []
        self._warning_msgs = []
        self._error_msgs = []

        # Disaggregate by message types
        if messages:
            self._disaggregate()

    def _disaggregate(self):
        # Disaggregate messages by type.
        self._success_msgs = self._messages_by_type(SUCCESS)
        self._warning_msgs = self._messages_by_type(WARNING)
        self._error_msgs = self._messages_by_type(ERROR)

    def _messages_by_type(self, msg_type):
        # Returns messages of the given type
        return [m for m in self.messages if m.message_type == msg_type]

    @property
    def success(self):
        """
        :return: Returns a list of successful messages, as a subset of the
        messages property.
        :rtype: list
        """
        return self._success_msgs

    @property
    def warnings(self):
        """
        :return: Returns a list of warning messages, as a subset of the
        messages property.
        :rtype: list
        """
        return self._warning_msgs

    @property
    def errors(self):
        """
        :return: Returns a list of error messages, as a subset of the
        messages property.
        :rtype: list
        """
        return self._error_msgs


class EntityVectorLayerValidator(QObject):
    """
    Validates a vector layer object against the given entity object
    """
    # Flag for validation status
    NOT_STARTED, NOT_COMPLETED, FINISHED = range(3)

    # Signals for validation process
    featureValidated = pyqtSignal(list)
    validationFinished = pyqtSignal()

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
            raise ValidatorException(
                'EntityVectorLayerColumnMapping could not be initialized.'
            )

        self._messages = OrderedDict()
        self._status = EntityVectorLayerValidator.NOT_STARTED

        # Flag to enabling canceling of validation operation
        self._is_cancelled = False

    @property
    def messages(self):
        """
        :return: Returns a container with all validation messages with the
        row_index as the key.
        :rtype: OrderedDict
        """
        return self._messages

    @property
    def row_warnings_errors(self):
        """
        Groups warning or error validation results, from a
        EntityVectorLayerValidator validation process, by row numbers.
        :return: Returns a collection containing a list of validation results
        for each row, with the row number as the key.
        :rtype: OrderedDict
        """
        error_warning_collec = OrderedDict()

        for row, results in self._messages.iteritems():
            warn_errors = [r for r in results
                          if len(r.errors) > 0 or len(r.warnings) > 0]

            if len(warn_errors) > 0:
                error_warning_collec[row] = warn_errors

        return error_warning_collec

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
        self._messages = OrderedDict()
        self._status = EntityVectorLayerValidator.NOT_STARTED
        self._is_cancelled = False

    def cancel(self):
        """
        Cancels an ongoing validation operation.
        """
        self._is_cancelled = True

    def _add_validation_result(self, row_index, v_res):
        # Adds validation result to the messages collection
        self._messages[row_index] = v_res

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

    @property
    def is_valid(self):
        """
        :return: Returns True if the validator is valid, else
        False. This property will return False if one of the following
        conditions is False:
        - Not all mandatory columns have been mapped.
        - The source columns do not exist in the data source.
        - If the status is NOT_STARTED or NOT_FINISHED.
        - If it contains one or more error messages.
        """
        if not self.validate_mandatory():
            return False

        if not self.validate_mapped_ds_columns():
            return False

        if not self.validate_entity_columns():
            return False

        if self.status == EntityVectorLayerValidator.NOT_STARTED or \
                self.status == EntityVectorLayerValidator.NOT_COMPLETED:
            return False

        return True

    def _column_validator(self, col_name):
        # Get the validator based on the given name of the entity column.
        ent_col = self._entity.column(col_name)
        if not ent_col:
            return None

        return column_validator_factory(ent_col)

    @property
    def count(self):
        """
        :return: Returns the number of features in the data source.
        :rtype: int
        """
        return self._vl.dataProvider().featureCount()

    def start(self):
        """
        Starts the validation process. It is important to ensure that
        the validation functions have been called prior to executing this
        function. Emits the featureValidated signal for each feature parsed
        in the vector layer.
        """
        # Assert if vector layer is valid
        if not self._vl.isValid():
            raise ValidatorException('Data source is invalid.')

        ridx = 0
        fields = self._vl.fields()
        feats = self._vl.getFeatures()

        # Update status
        self._status = EntityVectorLayerValidator.NOT_COMPLETED

        # Reset collection
        self._messages = OrderedDict()

        for feat in feats:
            cidx = 0
            feat_messages = []
            for f in fields:
                name = f.name()
                if self._ent_vl_mapping.contains_source_column(name):
                    col_name = self._ent_vl_mapping.destination_column(name)

                    validator = self._column_validator(col_name)
                    if not validator:
                        continue

                    attr_val = feat.attribute(name)
                    res = validator.validate(attr_val)

                    v_result = ValidationResult(ridx, cidx, res)
                    feat_messages.append(v_result)

                cidx += 1

            # Add result to the collection
            self._add_validation_result(ridx, feat_messages)

            # Emit signal
            self.featureValidated.emit(feat_messages)

            ridx += 1

        self._status = EntityVectorLayerValidator.FINISHED

        # Emit finished signal
        self.validationFinished.emit()


class ValidatorThread(QThread):
    """
    Thread for performing the validation process in the background.
    """
    # Propagate signals
    featureValidated = pyqtSignal(list)
    validationFinished = pyqtSignal()
    validationCanceled = pyqtSignal()

    def __init__(self, entity_vl_validator, parent=None):
        super(ValidatorThread, self).__init__(parent)
        self._ent_vl_validator = entity_vl_validator

        # Connect signals
        self._ent_vl_validator.featureValidated.connect(
            self._on_feature_validated
        )
        self._ent_vl_validator.validationFinished.connect(
            self._on_validation_finished
        )

    def run(self):
        # Start the validation process.
        self._ent_vl_validator.start()

    def _on_feature_validated(self, results):
        # Propagate signal
        self.featureValidated.emit(results)

    def _on_validation_finished(self):
        # Propagate signal
        self.validationFinished.emit()

    def stop(self):
        """
        Stop execution of the thread and raise validationCanceled signal.
        """
        self.exit(0)
        self.validationCanceled.emit()





