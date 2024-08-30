"""
/***************************************************************************
Name                 : Translator Configuration
Description          : Widget configuration options for value translators.
Date                 : 24/October/2014
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

from qgis.PyQt.QtWidgets import (
    QApplication,
    QDialog,
    QWidget
)

from stdm.ui.importexport.lookup_dialog import LookupDialog
from stdm.ui.importexport.multiple_enumeration_dialog import MultipleEnumerationDialog
from stdm.ui.importexport.related_table_dialog import RelatedTableDialog
from stdm.ui.importexport.source_document_dialog import SourceDocumentTranslatorDialog


class ValueTranslatorConfig(object):
    """
    Base class for all import widget translators.
    """
    translators = OrderedDict()
    key = ''

    @classmethod
    def register(cls):
        """
        Registers source value translators into the collection for use in the
        factory method.
        :param cls: Translator widget configuration which inherits from this
        class.
        :type cls: ValueTranslatorConfig
        """
        if issubclass(cls, ValueTranslatorConfig):
            ValueTranslatorConfig.translators[cls.key] = cls

    @staticmethod
    def create(parent, source_cols, dest_table, 
               dest_col, src_col):
        """
        :param parent: Parent widget.
        :type parent: QWidget
        :param source_cols: Columns from the source dataset.
        :type source_cols: list
        :param dest_table: Name of the destination table in the STDM database.
        :type dest_table: str
        :param dest_col: Name of the target column in the destination table.
        :type dest_col: str
        :param src_col: Name of the currently selected column in the source table.
        :type src_col: str
        :return: Create and returns a new instance of the translator configuration dialog.
        :rtype: QDialog
        """
        raise NotImplementedError


class RelatedTableTranslatorConfig(ValueTranslatorConfig):
    """
    Configuration for the RelatedTableTranslator widget.
    """
    key = QApplication.translate("RelatedTableTranslatorConfig",
                                 "Related table")

    @staticmethod
    def create(parent, source_cols, dest_table, 
               dest_col, src_col):
        return RelatedTableDialog(parent, source_cols, dest_table,
                                   dest_col, src_col)


RelatedTableTranslatorConfig.register()


class SourceDocumentTranslatorConfig(ValueTranslatorConfig):
    """
    Configuration for the SourceDocumentTranslator widget.
    """
    key = QApplication.translate("SourceDocumentTranslatorConfig",
                                 "Supporting documents")

    @staticmethod
    def create(parent, source_cols, dest_table, 
               dest_col, src_col):
        return SourceDocumentTranslatorDialog(
            parent,
            source_cols,
            dest_table,
            dest_col,
            src_col
        )


SourceDocumentTranslatorConfig.register()


class LookupTranslatorConfig(ValueTranslatorConfig):
    """
    Configuration for the SourceDocumentTranslator widget.
    """
    key = QApplication.translate("LookupTranslatorConfig",
                                 "Lookup values")

    @staticmethod
    def create(parent, source_cols, 
               dest_table, dest_col, src_col):
        return LookupDialog(
            parent,
            source_cols,
            dest_table,
            dest_col,
            src_col
        )


LookupTranslatorConfig.register()


class MultipleEnumerationTranslatorConfig(ValueTranslatorConfig):
    """
    Configuration for the MultipleEnumerationTranslator dialog.
    """
    key = QApplication.translate("MultipleSelectConfig",
                                 "Multiple select")

    @staticmethod
    def create(parent, source_cols, dest_table, 
               dest_col, src_col):
        return MultipleEnumerationDialog(parent, source_cols, dest_table,
                                         dest_col, src_col)


MultipleEnumerationTranslatorConfig.register()
