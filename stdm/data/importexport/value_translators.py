"""
/***************************************************************************
Name                 : Import SourceValue Translator
Description          : Helper classes that are translator the value of one or
                       more columns in the source table to a single value
                       in the destination database table.
Date                 : 22/October/2014
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
import itertools
from collections import OrderedDict

from qgis.PyQt.QtCore import (
    QDir,
    QFile
)
from qgis.PyQt.QtWidgets import (
    QApplication,
    QVBoxLayout
)
from sqlalchemy import func, cast, String
from sqlalchemy.schema import (
    Table,
    MetaData
)

from stdm.data.configuration import entity_model
from stdm.data.database import (
    STDMDb
)
from stdm.data.pg_utils import table_column_names
from stdm.utils.util import (
    getIndex
)
from .exceptions import TranslatorException

__all__ = ["SourceValueTranslator", "ValueTranslatorManager",
           "RelatedTableTranslator", "IgnoreType"]


class IgnoreType:
    """
    Placeholder object that instructs the reader to ignore inserting any
    value if this type is returned by a calling function such as value
    translators.
    """
    pass


class SourceValueTranslator:
    """
    Abstract class for translating values from one or more columns in the
    source table to a single value in the destination database table.
    Use cases can be simple linkages through foreign keys; derived values
    using the expression builder or new values (such as timestamps) that
    are not dependent on the any value from the source table.
    """

    def __init__(self, parent=None):
        self._parent = None
        self._db_session = STDMDb.instance().session
        self.clear()

        # Primary entity
        self.entity = None

    def clear(self):
        self._referencing_table = ""
        self._referenced_table = ""

        # Some translators like the MultipleEnumeration require ordered items
        self._input_referenced_columns = OrderedDict()
        self._output_referenced_column = ""
        self._referencing_column = ""
        self._name = ""

    def referencing_table(self):
        """
        :return: Destination table name.
        :rtype: str
        """
        return self._referencing_table

    def set_referencing_table(self, table_name):
        """
        Set the destination table name.
        :param table_name: Name of the destination table.
        :type table_name: str
        """
        self._referencing_table = table_name

    def referencing_column(self):
        """
        :return: Name of the target column in the destination table.
        :rtype: str
        """
        return self._referencing_column

    def set_referencing_column(self, column):
        """
        Set the name of the target column in the destination table.
        :param column: Target column name.
        :type column: str
        """
        self._referencing_column = column

    def referenced_table(self):
        """
        :return: Table name containing the value in the source table.
        :rtype: str
        """
        return self._referenced_table

    def set_referenced_table(self, table_name):
        """
        Set the name of the table containing the value in the source table.
        :param table_name: Name of database table contain source value.
        :type table_name: str
        """
        self._referenced_table = table_name

    def output_referenced_column(self):
        """
        :return: The name of the output column whose value will be used by the
        import process in the referencing column.
        :rtype: str
        """
        return self._output_referenced_column

    def set_output_reference_column(self, column):
        """
        Set the name of the output column whose value will be used by the
        import process in the referencing column.
        :param column: Name of the column in the referenced table.
        :type column: str
        """
        self._output_referenced_column = column

    def input_referenced_columns(self):
        """
        :return: Column name pairs for the source table and referenced table
        respectively, and whose values will be used to
        derive the value for the referencing column.
        :rtype: dict
        """
        return self._input_referenced_columns

    def add_source_reference_column(self, source_column: str, ref_table_column: str):
        """
        Append the source column name and the matched reference table name
        whose value will participate in deducing the value for the
        referencing column.
        :param source_column: Source table column name
        :type source_column: str
        :param ref_table_column: Corresponding column name in the reference table.
        :type column: str
        """
        self._input_referenced_columns[source_column] = ref_table_column

    def set_input_referenced_columns(self, columns: dict):
        """
        Set column names whose respective values will be used in deducing
        the value for the referencing column.
        Note that any existing matched columns will be removed.
        :param columns: Pair of source table column names and referenced table
        column names.
        :type columns: dict
        """
        if isinstance(columns, dict):
            self._input_referenced_columns = columns

    def name(self) ->str:
        return self._name if self._name else self._referencing_column

    def set_name(self, name: str):
        """
        Set the name for identifying this translator.
        :param name: Name of an instance of this class.
        :type name: str
        """
        self._name = name

    def source_column_names(self) ->list[str]:
        """
        :return: List containing names of the mapped source table columns.
        :rtype: list
        """
        return list(self._input_referenced_columns.keys())

    def set_parent(self, parent):
        """
        Set the parent of this translator.
        :param parent: Parent object.
        """
        self._parent = parent

    def parent(self):
        """
        :return: Parent widget of this translator.
        """
        return self._parent

    def requires_source_document_manager(self):
        """
        :return: True if the subclass requires a source document manager
        object, otherwise False (default). To be implemented by
        subclasses.
        """
        return False

    def referencing_column_value(self, field_values):
        """
        Abstract method to be implemented by subclasses.
        :param field_values: Column name-value pairings that will be used to
        derive the value for the referencing column.
        :type field_values: dict
        :return: The value that will be inserted into the referencing column.
        """
        raise NotImplementedError

    def run_checks(self):
        """
        Assert translator configuration prior to commencing the translation
        process. This includes checking whether the defined tables and respective
        columns exist.
        :return: Whether the translator settings are correct.
        :rtype: bool
        """
        res = False

        # Check destination table
        if self._table(self._referencing_table) is None:
            msg = QApplication.translate("SourceValueTranslator",
                                         "Target table '%s' does not exist."
                                         % (self._referencing_table))
            raise TranslatorException(msg)

        # Check destination column
        dest_columns = self._table_columns(self._referencing_table)
        referencing_col_idx = getIndex(dest_columns, self._referencing_column)

        if referencing_col_idx == -1:
            msg = QApplication.translate("SourceValueTranslator",
                                         "Target column '%s' does not exist."
                                         % (self._referencing_column))
            raise TranslatorException(msg)

        # Check link table
        if self._table(self._referenced_table) is None:
            msg = QApplication.translate("SourceValueTranslator",
                                         "Linked table '%s' does not exist."
                                         % (self._referenced_table))
            raise TranslatorException(msg)

        return res

    def _table_columns(self, table_name):
        """
        Return the column names for a given table_name name.
        :param table_name: Table name
        :type table_name: str
        :return: Collection of column names. If not found then an empty list is returned.
        :rtype: list
        """
        return table_column_names(table_name)

    def _table(self, name):
        """
        Get an SQLAlchemy table object based on the name.
        :param name: Table Name
        :type name: str
        """
        meta = MetaData(bind=STDMDb.instance().engine)

        return Table(name, meta, autoload=True)


class ValueTranslatorManager:
    """
    This class manages multiple instances of source value translators.
    """

    def __init__(self, parent=None):
        self._parent = None
        self._translators = {}

    def add_translator(self, value_translator):
        """
        Add translator to the collection.
        :param value_translator: Sub-class of
        :class: 'stdm.importexport.SourceValueTranslator' base class
        :type value_translator: SourceValueTranslator
        """
        if not isinstance(value_translator, SourceValueTranslator):
            raise TypeError("Instance of 'SourceValueTranslator' expected.")

        if not value_translator.name():
            return

        self._translators[value_translator.name()] = value_translator
        value_translator.set_parent(self._parent)

    def set_translators(self, translators):
        """
        Set the list of translators to be used for this class instance.
        :param translators: Collection of subclasses of
        :class: 'stdm.importexport.SourceValueTranslator' base class.
        :type translators: list
        """
        for translator in translators:
            self.add_translator(translator)

    def count(self):
        """
        :return: Number of translators in the manager.
        :rtype: int
        """
        return len(self._translators)

    def translator(self, name: str) ->SourceValueTranslator:
        """
        :param name: Name of the translator or the name of the referencing column
        depending on the one that was specified for a given translator.
        :return: Translator with the given name.
        :rtype: SourceValueTranslator
        """
        return self._translators.get(name, None)

    def translators(self) -> dict:
        return self._translators

    def clear(self):
        """
        Removes all translators from the collection.
        """
        self._translators = {}

    def remove_translator_by_name(self, name):
        """
        Removes a translator with the given name from the collection.
        :param name: Name of the translator.
        :type name:str
        """
        if not self.translator(name) is None:
            del self._translators[name]

    def remove_translator(self, translator):
        """
        Removes the given translator from the collection if it exists.
        :param translator: Translator
        :type translator: SourceValueTranslator
        """
        if isinstance(translator, SourceValueTranslator):
            self.remove_translator_by_name(translator.name())


class RelatedTableTranslator(SourceValueTranslator):
    """
    This class translates values from one or more columns in the referenced
    table to the specified column in the referencing table.
    """

    def __init__(self):
        SourceValueTranslator.__init__(self)

    def referencing_column_value(self, field_values):
        """
        Searches a corresponding record from the linked table using one or more
        pairs of field names and their corresponding values.
        :param field_values: Pair of field names and corresponding values i.e.
        {field1:value1, field2:value2, field3:value3...}
        :type field_values: dict
        :return: Value of the referenced column in the linked table.
        :rtype: object
        """
        link_table_columns = self._table_columns(self._referenced_table)

        query_attrs = {}

        for source_col, val in field_values.items():
            ref_table_col = self._input_referenced_columns.get(source_col, None)

            if ref_table_col is not None:
                col_idx = getIndex(link_table_columns, ref_table_col)

                # If column is found, add it to the query fields collection
                if col_idx != -1:
                    # TODO use the column object to cast based on column data type
                    query_attrs[ref_table_col] = cast(val, String)

        # Create link table object
        link_table = self._table(self._referenced_table)

        # Use AND operator
        link_table_rec = self._db_session.query(link_table).filter_by(**query_attrs).first()

        if link_table_rec is None:
            return IgnoreType()

        else:
            return getattr(link_table_rec, self._output_referenced_column, IgnoreType())


class LookupValueTranslator(RelatedTableTranslator):
    """
    Translator for lookup values.
    """
    def __init__(self, **kwargs):
        super(LookupValueTranslator, self).__init__()

        self._default_value = kwargs.get('default', '')
        self._lk_value_column = 'value'

    def set_default_value(self, deflt_value):
        self._default_value = deflt_value

    def default_value(self):
        return self._default_value

    def referencing_column_value(self, field_values):
        """
        Searches a corresponding record from the linked table using one or more
        pairs of field names and their corresponding values.
        :param field_values: Pair of field names and corresponding values i.e.
        {field1:value1, field2:value2, field3:value3...}
        :type field_values: dict
        :return: Value of the referenced column in the linked table.
        :rtype: object
        """
        if not self._referenced_table:
            msg = QApplication.translate(
                'LookupValueTranslator',
                'Lookup table has not been set.'
            )
            raise ValueError(msg)

        if len(field_values) == 0:
            return IgnoreType

        source_column = list(field_values.keys())[0]

        # Check if the source column is in the field_values
        if source_column not in field_values:
            return IgnoreType

        # Assume the source column is the first (and only) one in field_values
        source_column = list(field_values.keys())[0]
        lookup_value = field_values.get(source_column)

        # Create lookup table object
        lookup_table = self._table(self._referenced_table)

        lk_value_column_obj = getattr(lookup_table.c, self._lk_value_column)

        # Get corresponding lookup value record
        lookup_rec = self._db_session.query(lookup_table).filter(
            func.lower(lk_value_column_obj) == func.lower(cast(lookup_value, String))
        ).first()

        # Use default value if record is empty
        if lookup_rec is None and self._default_value:
            lookup_rec = self._db_session.query(lookup_table).filter(
                lk_value_column_obj == self._default_value
            ).first()

        if lookup_rec is None:
            return IgnoreType()

        return getattr(lookup_rec, 'id', IgnoreType())


class MultipleEnumerationTranslator(SourceValueTranslator):
    """
    This class translates enumeration values from a source column separated by
    a delimiter specified by the user..
    """

    def __init__(self):
        SourceValueTranslator.__init__(self)
        self._separator = ""

        # Container for lookup id and corresponding values
        self._lk_up_id_vals = {}

    def separator(self):
        """
        :return: The enum separator in the source table's column.
        :rtype: str
        """
        return self._separator

    def set_separator(self, sep):
        """
        Set the enum separator for the value in the source table's column.
        if an empty string, then whitespace is set as the separator.
        :param sep: Enum separator.
        :type sep: str
        """
        if sep:
            self._separator = sep
        else:
            self._separator = " "

    def referencing_column_value(self, field_values):
        """
        Gets a list of lookup objects corresponding to the values extracted
        from the source using the separator.
        :param field_values: Pair of field names and corresponding values i.e.
        {field1:value1, field2:value2, field3:value3...}
        :type field_values: dict
        :return: One or more object instances of lookup value objects.
        :rtype: list
        """
        if len(self._input_referenced_columns) == 0:
            return None

        num_cols = len(self._input_referenced_columns)
        cols_iter = itertools.islice(
            list(self._input_referenced_columns.items()),
            num_cols
        )

        # Tuple of one or two items.The format is -
        # (source primary enum column, enum table primary column)
        enum_cols_pairs = list(cols_iter)
        source_primary_col, enum_primary_col = enum_cols_pairs[0]

        delimited_source_value = field_values.get(source_primary_col, None)
        if not delimited_source_value:
            return IgnoreType()

        if not isinstance(delimited_source_value, str):
            return IgnoreType()

        # Get the lookup values used in the multiple select
        dest_col_obj = self.entity.column(enum_primary_col)
        if not dest_col_obj:
            return IgnoreType()

        # Get lookup entity and corresponding SQLAlchemy class
        lk_entity = dest_col_obj.value_list
        lookup_mapped_cls = entity_model(lk_entity)

        # Lookup objects corresponding to the values in the source string
        lk_objs = []
        lk_vals = delimited_source_value.split(self._separator)

        # Get the lookup objects corresponding to the separated source values
        for kv in lk_vals:
            kv = kv.strip()
            if kv:
                # Get corresponding lookup value object based on a
                # case-insensitive search
                lookup_obj = self._db_session.query(lookup_mapped_cls).filter(
                    func.lower(lookup_mapped_cls.value) == func.lower(kv)
                ).first()
                if lookup_obj:
                    lk_objs.append(lookup_obj)

        return lk_objs


class SourceDocumentTranslator(SourceValueTranslator):
    """
    Reads document paths from the source table and uploads them to the
    application document repository.
    """

    def __init__(self):
        SourceValueTranslator.__init__(self)

        # Needs to be set prior to uploading the document
        self.source_document_manager = None

        # Source directory
        self._source_directory = None

        # Document type id
        self._document_type_id = None

        # Document type name
        self._document_type = None

    def requires_source_document_manager(self):
        return True

    def document_type_id(self):
        return self._document_type_id

    def document_type(self):
        return self._document_type

    def source_directory(self):
        return self._source_directory

    def _create_uploaded_docs_dir(self):
        # Creates an 'uploaded' directory where uploaded documents are moved to.
        uploaded_dir = QDir(self._source_directory)
        uploaded_dir.mkdir('uploaded')

    def referencing_column_value(self, field_values):
        """
        Uploads documents based on the file name specified in the source
        column.
        :param field_values: Pair of field names and corresponding values i.e.
        {field1:value1, field2:value2, field3:value3...}
        :type field_values: dict
        :return: Ignore type since te source document manager will handle the
        supporting document uploads.
        :rtype: IgnoreType
        """
        if self.source_document_manager is None or self.entity is None:
            return IgnoreType

        if self._document_type_id is None:
            msg = QApplication.translate(
                'SourceDocumentTranslator',
                'Document type has not been set for the source document '
                'translator.'
            )
            raise RuntimeError(msg)

        if self._source_directory is None:
            msg = QApplication.translate(
                'SourceDocumentTranslator',
                'Source directory for {0} has not been set.'.format(
                    self._document_type
                )
            )
            raise RuntimeError(msg)

        source_dir = QDir()
        if not source_dir.exists(self._source_directory):
            msg = QApplication.translate(
                'SourceDocumentTranslator',
                'Source directory for {0} does not exist.'.format(
                    self._document_type
                )
            )
            raise IOError(msg)

        if len(field_values) == 0:
            return IgnoreType

        source_column = list(field_values.keys())[0]

        # Check if the source column is in the field_values
        if source_column not in field_values:
            return IgnoreType

        # Get file name
        doc_file_name = field_values.get(source_column)

        if not doc_file_name:
            return IgnoreType

        # Separate files
        docs = doc_file_name.split(';')

        # Create document container
        doc_container = QVBoxLayout()

        # Register container
        self.source_document_manager.registerContainer(
            doc_container,
            self._document_type_id
        )

        for d in docs:
            if not d:
                continue

            # Normalize slashes
            d_name = d.replace('\\', '/').strip()

            # Build absolute document path
            abs_doc_path = '{0}/{1}'.format(self._source_directory, d_name)

            if not QFile.exists(abs_doc_path):
                msg = QApplication.translate(
                    'SourceDocumentTranslator',
                    'Supporting document {0} does not exist.'.format(
                        abs_doc_path
                    )
                )

                raise IOError(msg)

            # Upload supporting document
            self.source_document_manager.insertDocumentFromFile(
                abs_doc_path,
                self._document_type_id,
                self.entity
            )

        # Move file to 'uploaded' directory

        # Documents are handles by the source document manager so we just
        # instruct the system to ignore the return value
        return IgnoreType
