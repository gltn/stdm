# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Register Parcel
Description          : GUI classes for managing and viewing supporting
                       documents.
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
import os.path

def translate_in_file(file_path):
    with open(file_path, "r") as ins:
        array = []
        for line in ins:
            array.append(line)
    if 'translate' in str(array):
        return True
    else:
        return False

def create_pro_file(dir):

    """
    Creates a stdm.pro file to be used for translation.
    :param dir: Directory
    :type dir: String
    :return: None
    :rtype: NoneType
    """
    file = open(dir+'\stdm.pro', 'w')
    # Print into file.
    print >> file, 'SOURCES = '
    space_length = len('SOURCES = ')
    space = ' '
    # Set indentation based on the length on the heading.
    indentation = space_length * space
    # loop through dir recursively except third party
    #  folder to get py files
    for dirpath, dirnames, filenames in os.walk(dir):
       # print dirpath, filenames
        if 'third_party' not in dirpath:

            for filename in [
                    f for f in filenames if f.endswith('.py')
                ]:
                # exclude init files
                if '__init__' not in filename:
                    file_path = os.path.join(dirpath, filename).replace('\\', '/')
                    if translate_in_file(file_path):
                        print >> file, indentation+file_path[len(dir)+1:] +' \\'
    print >> file, 'FORMS =	'
    space_length = len('FORMS = ')
    # Set indentation based on the length on the heading.
    indentation = space_length * space
    # loop through the current directory
    # recursively get ui files
    for dirpath, dirnames, filenames in os.walk(dir):
        for filename in [
                f for f in filenames if f.endswith('.ui')
            ]:
            file_path = os.path.join(dirpath, filename).replace('\\', '/')

            print >> file, indentation+file_path[len(dir)+1:] +' \\'
    print >> file, ''
    print >> file, 'TRANSLATIONS    = i18n/stdm_fr.ts'
    print >> file, ''
    print >> file,'CODECFORTR      = UTF-8'
    print >> file, ''
    print >> file, 'CODECFORSRC     = UTF-8'

    file.close()

create_pro_file('.')