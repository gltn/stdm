# /***************************************************************************
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation; either version 2 of the License, or     *
# *   (at your option) any later version.                                   *
# *                                                                         *
# ***************************************************************************/

"""
Document Template
"""

from typing import Optional

from stdm.composer.composer_data_source import ComposerDataSource


class DocumentTemplate(object):
    """
    Contains basic information about a document template.
    """

    def __init__(self, name: Optional[str] = None, path: Optional[str] = None,
                 data_source: Optional[ComposerDataSource] = None):
        self.name = name or ''
        self.path = path or ''
        self.data_source = data_source

    @property
    def referenced_table_name(self):
        """
        :return: Returns the referenced table name.
        :rtype: str
        """
        if self.data_source is None:
            return ''

        return self.data_source.referenced_table_name

    @staticmethod
    def build_from_path(name: str, path: str):
        """
        Creates an instance of the _DocumentTemplate class from the path of
        a document template.
        :param name: Template name.
        :type name: str
        :param path: Absolute path to the document template.
        :type path: str
        :return: Returns an instance of the _DocumentTemplate class from the
        absolute path of the document template.
        :rtype: _DocumentTemplate
        """
        data_source = ComposerDataSource.from_template_file(path)
        return DocumentTemplate(name=name, path=path, data_source=data_source)
