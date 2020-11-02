# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Create STDM Pro
Description          : A tool used to list all files of stdm with
                        translatable text into stdm.pro file.
Date                 : 30/June/2016
copyright            : (C) 2016 by UN-Habitat and implementing partners.
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
import os
import sys
import os.path
import io
# Memory file
mem_file = io.StringIO()

def translate_in_file(file_path):
    """
    Checks if the word translate exists in a file.
    :param file_path: The path of a file
    :type file_path: String
    :return: True if there is translate work
    or False if it doesn't exist.
    :rtype: Boolean
    """

    with open(file_path, "r") as file_inst:
        array = []
        for line in file_inst:
            array.append(line)

    if 'translate' in str(array):
        return True
    elif 'self.tr(' in str(array):
        return True
    else:
        return False

def format_file(file_path):
    """
    Removes forward slash at the end of a block of lines.
    :param file_path: The path of the file to be formatted
    :type file_path: String
    :return: None
    :rtype: NoneType
    """
    mem_file_lines = mem_file.getvalue().split('\n')
    # Lines at the end of file type list.
    last_line_indexes = []
    # Loop through memory file to get the lines before empty line
    for position, line1 in enumerate(mem_file_lines):
        # Get the index of the lines before empty line
        if line1 == '':
            last_line_indexes.append(position-1)

    file = open(file_path, "w+")
    # add lines of the memory file to actual file
    # replace backward slashes if they are last line
    # as backward slash is not needed there.
    for position, line1 in enumerate(mem_file_lines):
        if position in last_line_indexes:
            print(line1.replace(' \\', ''), file=file)
        else:
            print(line1, file=file)
    file.close()
    mem_file.close()


def create_pro_file(dir):
    """
    Creates a stdm.pro file to be used for translation.
    :param dir: Directory
    :type dir: String
    :return: None
    :rtype: NoneType
    """

    file = mem_file
    # Print into file.
    print('SOURCES = \\', file=file)
    space_length = len('SOURCES = ')

    space = ' '
    current_file_name = os.path.basename(sys.argv[0])
    # Set indentation based on the length on the heading.
    indentation = space_length * space
    # loop through dir recursively except third party
    #  folder to get py files
    for dirpath, dirnames, filenames in os.walk(dir):
       # print dirpath, filenames
        if 'third_party' not in dirpath:
            # List of py files
            py_files = [f for f in filenames if f.endswith('.py')]

            # print last_loop
            for i, filename in enumerate(py_files):
                # exclude init files
                if '__init__' not in filename and  \
                        not current_file_name in filename and 'ui_' not in filename:
                    file_path = os.path.join(dirpath, filename)

                    if translate_in_file(file_path):
                        print('{}{} \\'.format(
                            indentation,
                            file_path[len(dir)+1:]
                        ), file=file)
    print('', file=file)
    print('FORMS =	\\', file=file)
    space_length = len('FORMS = ')
    # Set indentation based on the length on the heading.
    indentation = space_length * space
    # loop through the current directory
    # recursively get ui files
    for dirpath, dirnames, filenames in os.walk(dir):
        # List of ui files
        ui_files = [f for f in filenames if f.endswith('.ui')]
        last_loop = len(ui_files) - 1
        for j, filename in enumerate(ui_files):
            file_path = os.path.join(dirpath, filename)

            print('{}{} \\'.format(
                indentation,
                file_path[len(dir) + 1:]
            ), file=file)
    print('', file=file)
    print('TRANSLATIONS    = i18n/stdm_fr.ts \\', file=file)
    print('                  i18n/stdm_pt.ts \\', file=file)
    print('                  i18n/stdm_de.ts \\', file=file)
    print('                  i18n/stdm_sw.ts \\', file=file)
    print('                  i18n/stdm_fi.ts \\', file=file)
    print('                  i18n/stdm_ar.ts \\', file=file)
    print('                  i18n/stdm_es.ts', file=file)
    print('', file=file)
    print('CODECFORTR      = UTF-8', file=file)
    print('', file=file)
    print('CODECFORSRC     = UTF-8', file=file)

    #file.close()
    format_file(dir+'\stdm.pro')

create_pro_file('.')