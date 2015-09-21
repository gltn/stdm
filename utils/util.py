"""
/***************************************************************************
Name                 : Generic application utility methods
Description          : Util functions
Date                 : 26/May/2013
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

import os
import os.path
import tempfile
from decimal import Decimal
import binascii
import string
import random
from collections import OrderedDict
from qgis.gui import QgsEncodingFileDialog

from PyQt4.QtCore import (
    QDir,
    Qt,
    QSettings,
    QFileInfo
)
from PyQt4.QtGui import QPixmap, QFileDialog, QDialog

from settings import RegistryConfig

PLUGIN_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir)).replace("\\", "/")
CURRENCY_CODE = ""  # TODO: Put in the registry
DOUBLE_FILE_EXTENSIONS = ['tar.gz', 'tar.bz2']


def get_index(list_obj, item):
    """
    Get the index of the list item without raising an
    error if the item is not found
    :rtype : int
    :param list_obj:
    :param item:
    """
    index = -1
    try:
        index = list_obj.index(item)
    except ValueError:
        pass
    return index


def load_combo_selections(combo_ref, obj):
    """
    Convenience method for loading lookup values in combo boxes
    :param combo_ref:
    :param obj:
    """
    model_instance = obj()
    model_items = model_instance.queryObject().all()
    combo_ref.addItem("")
    for item in model_items:
        combo_ref.addItem(item.value, item.id)


def read_combo_selections(obj):
    """
    Convenience method for loading lookup values in combo boxes
    :rtype : object
    :param obj:
    """
    model_instance = obj()
    model_items = model_instance.queryObject().all()
    return model_items


def set_model_attr_from_combo(model, attribute_name, combo,
                              ignore_first_item=True):
    """
    Convenience method for checking whether an item in the combo box
    has been selected an get the corresponding integer stored in the
    item data.
    :param model:
    :param attribute_name:
    :param combo:
    :param ignore_first_item:
    """
    if combo.count() is 0:
        return

    if ignore_first_item is True:
        if combo.currentIndex() is 0:
            return

    item_value = combo.itemData(combo.currentIndex())
    setattr(model, attribute_name, item_value)


def set_combo_current_index_with_item_data(combo, item_data,
                                           on_none_set_current_index=True):
    """
    Convenience method for setting the current index of the combo item
    with the specified value of the item data.
    :param combo:
    :param item_data:
    :param on_none_set_current_index:
    """
    if item_data is None and on_none_set_current_index:
        combo.setCurrentIndex(0)
    elif item_data is None and not on_none_set_current_index:
        return

    curr_index = combo.findData(item_data)
    if curr_index is not -1:
        combo.setCurrentIndex(curr_index)


def set_combo_current_index_with_text(combo, text):
    """
    Convenience method for setting the current index of the combo item
    with the specified value of the corresponding display text.
    :param combo:
    :param text:
    """
    txt_index = combo.findText(text)
    if txt_index != -1:
        combo.setCurrentIndex(txt_index)


def create_query_set(column_list, result_set, image_fields):
    """
    Create a list consisting of dictionary items
    derived from the database result set.
    For image fields, the fxn will write the binary object to disk
    and insert the full path of the image into the dictionary.
    :rtype : str, list
    :param column_list:
    :param result_set:
    :param image_fields:
    """
    q_set = []
    # Create root directory name to be used for storing the current session's
    # image files
    rt_dir = ''
    if len(image_fields) > 0:
        rt_dir = tempfile.mkdtemp()
    for r in result_set:
        row_items = {}
        for c in range(len(column_list)):
            clm_name = str(column_list[c])
            # Get the index of the image field, if one has been defined
            img_index = get_index(image_fields, clm_name)
            if img_index != -1:
                img_path = _write_image(rt_dir, str(r[c]))
                row_items[clm_name] = img_path
            else:
                row_items[clm_name] = str(r[c])
        q_set.append(row_items)

    return rt_dir, q_set


def _write_image(root_dir, image_str):
    """
    Write an image object to disk under the root directory in the
    system's temp directory.
    The method returns the absolute path to the image.
    :rtype : str
    :param root_dir:
    :param image_str:
    :return : Path to images
    """
    img_temp = PLUGIN_DIR + '/images/icons/img_not_available.jpg'

    try:
        os_hnd, img_path = tempfile.mkstemp(suffix='.JPG', dir=root_dir)
        pimg_pix = QPixmap()
        img_pix = pimg_pix.scaled(80, 60, aspectRatioMode=Qt.KeepAspectRatio)
        l_status = img_pix.loadFromData(image_str)  # Load Status

        if l_status:
            w_status = img_pix.save(img_path)  # Write Status
            if w_status:
                img_temp = img_path
        os.close(os_hnd)

    except:
        pass

    return img_temp


def copyattrs(obj_from, obj_to, names):
    """
    Copies named attributes over to another object
    :param obj_from:
    :param obj_to:
    :param names:
    """
    for n in names:
        if hasattr(obj_from, n):
            v = getattr(obj_from, n)
            setattr(obj_to, n, v)


def compare_lists(valid_list, user_list):
    """
    Method for validating if items defined in the user list actually exist
    in the valid list
    :param valid_list:
    :param user_list:
    :return: List of user defined list
    """
    valid_list = [x for x in user_list if x in valid_list]
    # Get invalid items in the user list
    invalid_list = [x for x in user_list if x not in valid_list]

    return valid_list, invalid_list


def replace_none_text(db_value, replace_with=""):
    """
    Replaces 'None' string with more friendly text.
    :rtype : str
    :param db_value:
    :param replace_with:
    """
    if str(db_value) is "None":
        return replace_with
    else:
        return db_value


def money_fmt(value, places=2, curr=CURRENCY_CODE, sep=',', dp='.', pos='',
              neg='-', trail_neg=''):
    """Convert Decimal to a money formatted string.
    :rtype : str
    :param value:
    :param places: required number of places after the decimal point
    :param curr: optional currency symbol before the sign (may be blank)
    :param sep: optional grouping separator (comma, period, space, or blank)
    :param dp: decimal point indicator (comma or period)
             only specify as blank when places is zero
    :param pos: optional sign for positive numbers: '+', space or blank
    :param neg: optional sign for negative numbers: '-', '(', space or blank
    :param trail_neg: optional trailing minus indicator:  '-', ')', space or
    blank
    """
    q = Decimal(10) ** -places
    sign, digits, exp = value.quantize(q).as_tuple()
    result = []
    digits = map(str, digits)
    build, next = result.append, digits.pop
    if sign:
        build(trail_neg)
    for i in range(places):
        build(next() if digits else '0')
    build(dp)
    if not digits:
        build('0')
    i = 0
    while digits:
        build(next())
        i += 1
        if i == 3 and digits:
            i = 0
            build(sep)
    build(curr)
    build(neg if sign else pos)
    return ''.join(reversed(result))


def guess_extension(filename):
    """
    Extracts the file extension from the file name. It is also enabled to work
    with files containing double extensions.
    :rtype : str
    :param filename:
    """
    root, ext = os.path.splitext(filename)
    if any([filename.endswith(x) for x in DOUBLE_FILE_EXTENSIONS]):
        root, first_ext = os.path.splitext(root)
        ext += first_ext
    return root, ext


def gen_random_string(num_bytes=10):
    """
    Generates a random string based on the number of bytes specified.
    :rtype : binascii
    :type num_bytes: int
    """
    return binascii.b2a_hex(os.urandom(num_bytes))


def random_code_generator(size=8):
    """
    Automatically generates a string containing a random sequence of numbers
    and uppercase ASCII letters.
    :rtype : str
    :param size: int
    """
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(size))


def document_templates():
    """
    Return a dictionary of document names and their corresponding absolute file
    paths.
    :rtype : OrderedDict
    """
    doc_templates = OrderedDict()

    reg_config = RegistryConfig()
    key_name = "ComposerTemplates"

    path_config = reg_config.read([key_name])

    if len(path_config) > 0:
        template_dir = path_config[key_name]

        path_dir = QDir(template_dir)
        path_dir.setNameFilters(["*.sdt"])
        doc_file_infos = path_dir.entryInfoList(QDir.Files, QDir.Name)

        for df in doc_file_infos:
            doc_templates[df.completeBaseName()] = df.absoluteFilePath()

    return doc_templates


def open_dialog(parent, filtering="GPX (*.gpx)", dialog_mode="SingleFile"):
    """
    Opens dialog
    :rtype : str
    :param parent:
    :param filtering:
    :param dialog_mode:
    :return:
    """
    settings = QSettings()
    dir_name = settings.value("/UI/lastShapefileDir")
    encode = settings.value("/UI/encoding")
    file_dialog = QgsEncodingFileDialog(
        parent, "Save output file", dir_name, filtering, encode)
    file_dialog.setFileMode(QFileDialog.ExistingFiles)
    file_dialog.setAcceptMode(QFileDialog.AcceptOpen)
    if not file_dialog.exec_() == QDialog.Accepted:
        return None, None
    files = file_dialog.selectedFiles()
    settings.setValue("/UI/lastShapefileDir",
                      QFileInfo(unicode(files[0])).absolutePath())
    if dialog_mode == "SingleFile":
        return unicode(files[0]), unicode(file_dialog.encoding())
    else:
        return (files, unicode(file_dialog.encoding()))
