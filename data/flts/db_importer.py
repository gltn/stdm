"""
/***************************************************************************
Name                 : EntityVectorLayerDbImporter
Description          : Imports data from a vector layer source to a table in
                       the STDM database.
Date                 : 31/August/2019
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
from abc import (
    ABCMeta,
    abstractmethod
)
from datetime import datetime

from PyQt4.QtCore import (
    pyqtSignal,
    QObject
)

from stdm.settings import current_profile
from stdm.data.flts.validators import (
    DATE_FORMAT,
    entity_vector_layer_mapping,
    lookup_values,
    ValidatorException
)
from stdm.data.configuration import entity_model


class AbstractValueTranslator(object):
    """
    Transforms a value from the data source to an entity-compatible value
    where applicable. It is important to ensure that the data source has been
    validated prior to initiating the import process.
    """
    __metaclass__ = ABCMeta

    def __init__(self, column):
        self._column = column
        self.setup()

    def setup(self):
        """
        Perform additional initialization of the class. Default
        implementation does nothing.
        """
        pass

    @property
    def column(self):
        """
        :return: Returns the STDM column object.
        :rtype: stdm.data.configuration.Column
        """
        return self._column

    @abstractmethod
    def transform(self, value):
        """
        Transforms the data source value to an entity compatible value.
        :param value: Value
        :type value: object
        :return: Translated value.
        :rtype: object
        """
        raise NotImplementedError


class VarCharValueTranslator(AbstractValueTranslator):
    """
    Asserts that number values are correctly converted to string.
    """
    def transform(self, value):
        try:
            value = int(value)
            return unicode(value)
        except ValueError:
            # It is a non-numeric value
            return value


class LookupValueTranslator(AbstractValueTranslator):
    """
    Transforms a lookup value to the corresponding primary key in the lookup
    table.
    """
    def setup(self):
        # Fetch the lookup items
        lookup_items = lookup_values(self.column.value_list)

        # Collection indexed by lower case of the lookup values.
        self._lookup_values = {v.lower(): pk
                               for v, pk in lookup_items.reverse.iteritems()}

    def transform(self, value):
        # Check if the value exists in the lookup values. If not return None.
        return self._lookup_values.get(value.lower(), None)


class DateValueTranslator(AbstractValueTranslator):
    """
    Transforms values in string format to the correct dates.
    """
    def transform(self, value):
        # Convert dates in string type to the corresponding date type.
        if not value:
            return None

        if isinstance(value, basestring):
            try:
                value = datetime.strptime(value, DATE_FORMAT)
            except ValueError:
                value = None

        return value


# Value translator class based on the column TYPE_INFO.
value_translators = {
    'DATE': DateValueTranslator,
    'LOOKUP': LookupValueTranslator,
    'VARCHAR': VarCharValueTranslator
}


class EntityVectorLayerDbImporter(QObject):
    """
    Imports data from a vector layer to an STDM table whose structure is
    represented by an entity object. It is assumed that the validation has
    been carried out prior to initiating the import process.
    """
    featureImported = pyqtSignal(tuple) # (is_new, entity_data_object)
    importFinished = pyqtSignal()

    def __init__(
            self,
            entity,
            vector_layer,
            column_mapping=None,
            unique_cols=None,
            parent=None
    ):
        """
        Class constructor.
        :param entity: Entity object representing the structure of the
        destination table.
        :type entity: stdm.data.configuration.entity.Entity
        :param vector_layer: Data source.
        :type vector_layer: QgsVectorLayer
        :param column_mapping: Object containing the mapping of
        source-destination column pairings. Only values for those columns
        defined in the mapping will be imported.
        :type column_mapping: stdm.data.flts.validators.
        EntityVectorLayerColumnMapping
        :param unique_cols: Specify list of columns, as defined in the entity
        table, whose values will be checked for uniqueness prior to
        importation. If not unique, then they will be skipped.
        :type unique_cols: list
        :param parent: Parent object
        :type parent: QObject
        """
        super(EntityVectorLayerDbImporter, self).__init__(parent)

        self._entity = entity
        # If entity is string then get the corresponding entity object
        if isinstance(self._entity, basestring):
            curr_profile = current_profile()
            if not curr_profile:
                raise TypeError('Current profile in None.')
            self._entity = curr_profile.entity(self._entity)

        # List of valid entity column names
        self._entity_col_names = self._entity.columns.keys()

        self._vl = vector_layer

        self._ent_vl_mapping = column_mapping
        # If not defined, use default one based on file defined in the
        # settings
        if not self._ent_vl_mapping:
            self._ent_vl_mapping = entity_vector_layer_mapping()
        if not self._ent_vl_mapping:
            raise ValidatorException(
                'EntityVectorLayerColumnMapping could not be initialized.'
            )

        # Unique entity column names to check for unique values
        self._unique_cols = unique_cols
        if not self._unique_cols:
            self._unique_cols = []

        # Get 'curated' list of unique column names i.e. actually exist.
        self._curated_unique_cols = list(
            set(self._entity_col_names).intersection(set(self._unique_cols))
        )

        # SQLAlchemy class representing the entity
        self._entity_cls = entity_model(self._entity)

        # Features skipped as they did not pass the uniqueness test but will
        # be fetched and stored for updating if additional model attributes
        # have been specified.
        self._skipped_ent_models = []

        # Specify additional attribute values that will be appended to the
        # entity data object when being created or updated in the database.
        self._ext_attribute_vals = {}

        # Column value translators
        self._col_val_translators = {}
        for c in self._entity.columns.values():
            if c.TYPE_INFO in value_translators:
                col_translator = value_translators[c.TYPE_INFO]
                self._col_val_translators[c.name] = col_translator(c)

    @property
    def vector_layer(self):
        """
        :return: Returns the data source object.
        :rtype: QgsVectorLayer
        """
        return self._vl

    @property
    def entity(self):
        """
        :return: Returns the object representing the structure of the
        destination table.
        :rtype: stdm.data.configuration.entity.Entity
        """
        return self._entity

    @property
    def column_mapping(self):
        """
        :return: Returns the object containing the source-destination column
        pairings.
        :rtype: stdm.data.flts.validators.EntityVectorLayerColumnMapping
        """
        return self._ent_vl_mapping

    @property
    def unique_columns(self):
        """
        :return: Returns a list containing column names whose values should
        be checked for uniqueness prior to importation.
        :rtype: list
        """
        return self._unique_cols

    @property
    def count(self):
        """
        :return: Returns the number of features in the data source.
        :rtype: int
        """
        return self._vl.dataProvider().featureCount()

    def extra_attribute_value(self, attr_name):
        """
        Gets the value of the additional attribute value that was specified
        from a separate process.
        :param attr_name: Attribute name.
        :type attr_name: str
        :return: Returns the value of the attribute with the given name or
        None if the attribute does not exist.
        :rtype: object
        """
        return self._ext_attribute_vals.get(attr_name, None)

    def set_extra_attribute_value(self, attr_name, value):
        """
        Sets the value of the additional attribute name that will be appended
        to the entity data object when being created or updated in the
        database. If there is an existing attribute with the same name, it will be overwritten.
        :param attr_name: Attribute name.
        :type attr_name: str
        :param value: Attribute value. Can be a string, number, list etc.
        :type value: object
        """
        self._ext_attribute_vals[attr_name] = value

    def remove_extra_attribute(self, attr_name):
        """
        Removes an existing attribute with the given name.
        :param attr_name: Attribute name.
        :type attr_name: str
        :return: Returns True if the operation succeeded, else False if the
        given attribute name does not exist.
        :rtype: bool
        """
        if attr_name not in self._ext_attribute_vals:
            return False

        del self._ext_attribute_vals[attr_name]

        return True

    def _feat_to_entity_model(self, feat, fields):
        """
        Converts a feature to an entity data object. Returns a tuple
        containing a bool value and entity data object. In the former, True
        indicates a new entity data object, False indicates that there is one
        or more existing entity data objects found after checking for unique
        values.
        """
        entity_objects = []
        is_new = True
        entity_obj = self._entity_cls()
        for f in fields:
            name = f.name()
            if self._ent_vl_mapping.contains_source_column(name):
                col_name = self._ent_vl_mapping.destination_column(name)
                attr_val = feat.attribute(name)
                if col_name in self._col_val_translators:
                    translator = self._col_val_translators[col_name]
                    attr_val = translator.transform(attr_val)

                # Check if there are existing records based on unique columns
                if col_name in self._curated_unique_cols:
                    col_attr = getattr(self._entity_cls, col_name)
                    records = entity_obj.queryObject().filter(
                        col_attr == attr_val
                    ).all()

                    if len(records) > 0:
                        is_new = False
                        entity_objects.extend(records)
                        continue

                # Set attribute value only if a new record
                if is_new:
                    # Set attribute value in data model
                    setattr(entity_obj, col_name, attr_val)

        # If entity_obj is a new record, add it to the collection
        if is_new:
            entity_objects.append(entity_obj)

        # Append additional extra attribute values to the data objects
        for ent_obj in entity_objects:
            for attr, val in self._ext_attribute_vals.iteritems():
                if hasattr(entity_obj, attr):
                    # If it is a list then extend it
                    if isinstance(val, list):
                        init_val = getattr(ent_obj, attr)
                        val.extend(init_val)
                    setattr(ent_obj, attr, val)

        return is_new, entity_objects

    def start(self):
        """
        Starts the data importation process. For each feature imported, the
        featureImported signal will be raised and will contain the SQLAlchemy
        data model. Upon completion, the importFinished signal will be raised.
        """
        # Assert if vector layer is valid
        if not self._vl.isValid():
            raise ValidatorException('Data source is invalid.')

        self._skipped_ent_models = []
        fields = self._vl.fields()
        feats = self._vl.getFeatures()

        for feat in feats:
            # Get entity objects and if existing
            is_new, entity_objects = self._feat_to_entity_model(
                feat,
                fields
            )
            for ent_obj in entity_objects:
                if is_new:
                    ent_obj.save()
                else:
                    ent_obj.update()
                    self._skipped_ent_models.append(ent_obj)

                # Emit signal
                self.featureImported.emit((is_new, ent_obj))

        self.importFinished.emit()