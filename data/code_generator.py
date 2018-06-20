"""
/***************************************************************************
Name                 : Code Generator
Description          : Code generator of a column using prefix, separator
                        and leading zero.
Date                 : 23/February/2017
copyright            : (C) 2017 by UN-Habitat and implementing partners.
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
import re
from stdm.data.configuration import entity_model
from stdm.settings import current_profile

class CodeGenerator(object):
    """
    Generate unique code for a column using prefix, separator and leading zero
    parameters.
    """
    def __init__(self, entity, column):
        """
        Initializes entity and column property.
        :param entity: The entity object of the column
        :type entity: Object
        :param column: The column object
        :type column: Object
        """
        #TODO disable once committed to the database
        self.entity = entity
        self.current_profile = current_profile()
        self.code_entity = self.current_profile.auto_generate_code

        self.code_model = entity_model(self.code_entity)

        self.code_model_obj = self.code_model()
        self.column = column

    def generate(self, prefix, separator, leading_zero, hide_prefix=False):
        """
        Generates the next unique code by checking what is saved in the
        database for a specific column.
        :param prefix: The code prefix in front of the serial number.
        :type prefix: String
        :param separator: The separator used to separate code prefixes and
        serial numbers within a code.
        :type separator: String
        :param leading_zero: The leading zeros to be added in front of
        serial number.
        :type leading_zero: String
        :return: Returns the next unique code for the column
        :rtype: String
        """
        matches = self.search_similar_code(prefix, separator)
        # matches is list with tuple items.
        # To access them 0 index is used
        record_match = []
    
        for item in matches:

            if len(item) > 0:
                try:
                    # for code with prefix
                    if prefix == item[0].rsplit(separator, 1)[0]:
                        record_match.append(item[0])
                    # for serial number code
                    if prefix == '':
                        record_match.append(item[0])
                # if the separator is empty - '', escape the value error
                # and append.
                except ValueError:
                    record_match.append(item[0])

        # if no match found, start with 1
        if len(record_match) == 0:
            code = '{0}{1}{2}1'.format(prefix, separator, leading_zero)
            self.save_code(code)
            if hide_prefix:
                code = '{0}1'.format(leading_zero)
            return code

        else:
            last_serial = None
            if prefix == '':
                # get the serial number
                last_serial = record_match[0]

            else:
                last_code = []
                # get the serial number
                try:
                    last_code = record_match[0].rsplit(separator, 1)
                # if the separator is empty - '', split by numbers and letters.

                except ValueError:
                    if separator == '':
                        last_serial = record_match[0].replace(prefix, '')
                    else:
                        prefix_and_serial = record_match[0].split(separator)
                        if len(prefix_and_serial) > 0:
                            last_serial = prefix_and_serial[len(prefix_and_serial)-1]
                    # match = re.match(
                    #     r'([a-zA-Z]+)([0-9]+)', record_match[0], re.I
                    # )
                #     if match:
                #         text_numbers = match.groups()
                #         if len(text_numbers) == 2:
                #             last_code = text_numbers
                #
                # if len(last_code) > 1:
                #     last_serial = last_code[1]

            if last_serial is None:
                # print last_serial, 'last '
                return None

            # convert to integer and add 1
            next_serial = int(last_serial) + 1
            # Add 1 to append correct number of leading zero at the beginning.
            leading_zero_len = len(leading_zero) + 1
            # format again with leading 0
            formatted_serial = "%0{}d".format(leading_zero_len) % (next_serial,)

            code = '{0}{1}{2}'.format(prefix, separator, formatted_serial)
            self.save_code(code)

            if hide_prefix:
                code = formatted_serial

            # add new code with the formatted number
            return code

    def save_code(self, code):
        """
        Saves the code to the code table.
        :param code: The unique code generated.
        :type code: String
        :return:
        :rtype:
        """
        self.code_model_obj.code = code
        self.code_model_obj.save()

    def search_similar_code(self, prefix, separator):
        """
        Queries the database on the column to get all the values matching
        the supplied prefix.
        :param prefix: The code prefix in front of the serial number.
        :type prefix: String
        :param separator: The separator used to separate code prefixes and
        serial numbers within a code.
        :type separator: String
        :return: Matching database result
        :rtype: SQLAlchemy result proxy
        """
        column_obj = getattr(self.code_model, 'code')
        matches = self.code_model_obj.queryObject([column_obj]
                                                ).filter(
            column_obj.op('~')(u'^{}{}[0-9]'.format(prefix, separator))
            ).order_by(column_obj.desc()).all()

        return matches
    #
    # def search_code(self, code):
    #     """
    #     Queries the database on the column to get all the values matching
    #     the supplied prefix.
    #     :param code: The code generated.
    #     :type code: String
    #     :return: Matching database result
    #     :rtype: SQLAlchemy result proxy
    #     """
    #
    #     column_obj = getattr(self.code_model, 'code')
    #     matches = self.code_model_obj.queryObject([column_obj]
    #                                             ).filter(
    #         column_obj.op('~')(u'^{}'.format(code))
    #         ).order_by(column_obj.desc()).all()
    #
    #     return matches
    #
