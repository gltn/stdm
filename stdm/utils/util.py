"""
/***************************************************************************
Name                 : Generic application utility methods
Description          : Util functions
Date                 : 26/May/2013
copyright            : (C) 2013 by John Gitau
email                : gkahiu@gmail.com
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

import binascii
import os
import os.path
import random
import re
import string
import tempfile
from collections import OrderedDict
from datetime import (
    date,
    datetime
)
from decimal import Decimal

from qgis.PyQt.QtCore import (
    QDir,
    Qt,
    QSettings,
    QFileInfo)
from qgis.PyQt.QtGui import (
    QPixmap)
from qgis.PyQt.QtWidgets import (
    QFileDialog,
    QDialog,
    QAbstractItemView,
    QVBoxLayout,
    QLabel,
    QCheckBox,
    QDialogButtonBox,
    QListWidget)
from qgis.gui import QgsEncodingFileDialog
from sqlalchemy import (
    func
)

from stdm.data.configuration import (
    entity_model
)
from stdm.exceptions import DummyException

PLUGIN_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir)).replace("\\", "/")
CURRENCY_CODE = ""  # TODO: Put in the registry
DOUBLE_FILE_EXTENSIONS = ['tar.gz', 'tar.bz2']


def getIndex(listObj, item):
    """
    Get the index of the list item without raising an
    error if the item is not found
    """
    index = -1
    try:
        index = listObj.index(item)
    except ValueError:
        pass
    return index


def loadComboSelections(comboref, obj):
    """
    Convenience method for loading lookup values in combo boxes
    """
    modelinstance = obj()
    modelItems = modelinstance.queryObject().all()
    comboref.addItem("")
    for item in modelItems:
        comboref.addItem(item.value, item.id)


def readComboSelections(obj):
    """
    Convenience method for loading lookup values in combo boxes
    """
    modelinstance = obj()
    modelItems = modelinstance.queryObject().all()
    return modelItems


def setModelAttrFromCombo(model, attributename, combo, ignorefirstitem=True):
    """
    Convenience method for checking whether an item in the combo box
    has been selected an get the corresponding integer stored in the
    item data.
    """
    if combo.count() == 0:
        return

    if ignorefirstitem:
        if combo.currentIndex() == 0:
            return

    itemValue = combo.itemData(combo.currentIndex())
    setattr(model, attributename, itemValue)


def createQuerySet(columnList, resultSet, imageFields):
    """
    Create a list consisting of dictionary items
    derived from the database result set.
    For image fields, the fxn will write the binary object to disk
    and insert the full path of the image into the dictionary.
    """
    qSet = []
    # Create root directory name to be used for storing the current session's image files
    rtDir = ''
    if len(imageFields) > 0:
        rtDir = tempfile.mkdtemp()
    for r in resultSet:
        rowItems = {}
        for c in range(len(columnList)):
            clmName = str(columnList[c])
            # Get the index of the image field, if one has been defined
            imgIndex = getIndex(imageFields, clmName)
            if imgIndex != -1:
                imgPath = writeImage(rtDir, str(r[c]))
                rowItems[clmName] = imgPath
            else:
                rowItems[clmName] = str(r[c])
        qSet.append(rowItems)

    return rtDir, qSet


def writeImage(rootDir, imageStr):
    """
    Write an image object to disk under the root directory in the
    system's temp directory.
    The method returns the absolute path to the image.
    """
    imgTemp = PLUGIN_DIR + '/images/icons/img_not_available.jpg'

    try:
        os_hnd, imgPath = tempfile.mkstemp(suffix='.JPG', dir=rootDir)
        pimgPix = QPixmap()
        imgPix = pimgPix.scaled(80, 60, aspectRatioMode=Qt.KeepAspectRatio)
        lStatus = imgPix.loadFromData(imageStr)  # Load Status

        if lStatus:
            wStatus = imgPix.save(imgPath)  # Write Status
            if wStatus:
                imgTemp = imgPath
        os.close(os_hnd)

    except DummyException:
        pass

    return imgTemp


def copyattrs(objfrom, objto, names):
    # Copies named attributes over to another object
    for n in names:
        if hasattr(objfrom, n):
            v = getattr(objfrom, n)
            setattr(objto, n, v)


def compareLists(validList, userList):
    # Method for validating if items defined in the user list actually exist in the valid list
    validList = [x for x in userList if x in validList]
    # Get invalid items in the user list
    invalidList = [x for x in userList if x not in validList]

    return validList, invalidList


def replaceNoneText(dbvalue, replacewith=""):
    """
    Replaces 'None' string with more friendly text.
    """
    if str(dbvalue) == "None":
        return replacewith
    else:
        return dbvalue


def moneyfmt(value, places=2, curr=CURRENCY_CODE, sep=',', dp='.',
             pos='', neg='-', trailneg=''):
    """Convert Decimal to a money formatted string.

    places:  required number of places after the decimal point
    curr:    optional currency symbol before the sign (may be blank)
    sep:     optional grouping separator (comma, period, space, or blank)
    dp:      decimal point indicator (comma or period)
             only specify as blank when places is zero
    pos:     optional sign for positive numbers: '+', space or blank
    neg:     optional sign for negative numbers: '-', '(', space or blank
    trailneg:optional trailing minus indicator:  '-', ')', space or blank

    """
    q = Decimal(10) ** -places
    sign, digits, exp = value.quantize(q).as_tuple()
    result = []
    digits = list(map(str, digits))
    build, next = result.append, digits.pop
    if sign:
        build(trailneg)
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
    Extracts the file extension from the file name. It is also enabled to work with files
    containing double extensions.
    """
    root, ext = os.path.splitext(filename)
    if any([filename.endswith(x) for x in DOUBLE_FILE_EXTENSIONS]):
        root, first_ext = os.path.splitext(root)
        ext = first_ext + ext
    return root, ext


def gen_random_string(numbytes=10):
    """
    Generates a random string based on the number of bytes specified.
    """
    return binascii.b2a_hex(os.urandom(numbytes))


def randomCodeGenerator(size=8):
    """
    Automatically generates a string containing a random sequence of numbers and uppercase ASCII letters.
    """
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(size))


def documentTemplates():
    """
    Return a dictionary of document names and their corresponding absolute file paths.
    """
    from stdm.settings.registryconfig import RegistryConfig

    docTemplates = OrderedDict()

    regConfig = RegistryConfig()
    keyName = "ComposerTemplates"

    pathConfig = regConfig.read([keyName])

    if len(pathConfig) > 0:
        templateDir = pathConfig[keyName]

        pathDir = QDir(templateDir)
        pathDir.setNameFilters(["*.sdt"])
        docFileInfos = pathDir.entryInfoList(QDir.Files, QDir.Name)

        for df in docFileInfos:
            docTemplates[df.completeBaseName()] = df.absoluteFilePath()

    return docTemplates


def openDialog(parent, filtering="GPX (*.gpx)", dialogMode="SingleFile"):
    settings = QSettings()
    dirName = settings.value("/UI/lastShapefileDir")
    encode = settings.value("/UI/encoding")
    fileDialog = QgsEncodingFileDialog(parent, "Save output file", dirName, filtering, encode)
    fileDialog.setFileMode(QFileDialog.ExistingFiles)
    fileDialog.setAcceptMode(QFileDialog.AcceptOpen)
    if not fileDialog.exec_() == QDialog.Accepted:
        return None, None
    files = fileDialog.selectedFiles()
    settings.setValue("/UI/lastShapefileDir", QFileInfo(str(files[0])).absolutePath())
    if dialogMode == "SingleFile":
        return (str(files[0]), str(fileDialog.encoding()))
    else:
        return (files, str(fileDialog.encoding()))


def datetime_from_string(str_val):
    """
    Converts a datetime in string value to the corresponding datetime object.
    :param str_val: Datetime
    :type str_val: str
    :return: Returns a datetime object from the corresponding string value.
    :rtype: datetime
    """
    return datetime.strptime(str(str_val), '%Y-%m-%d %H:%M:%S')


def date_from_string(str_val):
    """
    Converts a date in string value to the corresponding date object.
    :param str_val: Date in string.
    :type str_val: str
    :return: Returns a date object from the corresponding string value.
    :rtype: date
    """
    return datetime.strptime(str(str_val), '%Y-%m-%d').date()


def format_name(attr, trim_id=True):
    """
    Formats the column names by removing id
    from lookups and fk columns and capitalize.
    Used for title and form labels
    :param attr: column name
    :return: string - formatted column name
    """
    if '_id' in attr and trim_id:
        if attr != 'national_id':
            display_name = attr[:-3]
            display_name = display_name.replace('_', ' ').title()
        else:
            display_name = 'National ID'
    else:
        display_name = attr.replace('_', ' ').title()

    return display_name


def entity_display_columns(entity, with_header=False, exclude=[]):
    """
    Returns entity display columns.
    :param entity: Entity
    :type entity: Class
    :param with_header: If header is needed or not.
    :type with_header: Boolean
    :return: List of column names or dictionary with column header.
    :rtype: List or Dictionary
    """
    display_type_info = [
        'VARCHAR',
        'SERIAL',
        'TEXT',
        'INT',
        'DOUBLE',
        'DATE',
        'DATETIME',
        'BOOL',
        'LOOKUP',
        'ADMIN_SPATIAL_UNIT',
        'FOREIGN_KEY',
        'MULTIPLE_SELECT',
        'PERCENT',
        'AUTO_GENERATED',
        'EXPRESSION'
    ]
    if with_header:
        display_column = [
            (c.name, c.header())
            for c in
            entity.columns.values()
            if c.TYPE_INFO in display_type_info
            if c.TYPE_INFO not in exclude
        ]
        display_column = OrderedDict(display_column)
        return display_column
    else:
        display_column = [
            c.name
            for c in
            entity.columns.values()
            if c.TYPE_INFO in display_type_info
            if c.TYPE_INFO not in exclude
        ]

        return display_column


def entity_searchable_columns(entity):
    """
    Returns searchable entity columns.
    :param entity: Entity
    :type entity: Class
    :return: List of searchable columns
    :rtype: List
    """
    searchable_column = [
        c.name
        for c in
        entity.columns.values()
        if c.searchable
    ]
    return searchable_column


def model_obj_display_data(model, entity, profile):
    """
    Formats a model object data with a formatted column name and
    a value converted to lookup value instead of id, if a lookup column.
    :param model: The model object
    :type model: Object
    :param entity: Entity
    :type entity: Class
    :param profile: Current Profile
    :type profile: Class
    :return: Dictionary of formatted column with formatted value.
    :rtype: OrderedDict
    """
    model_display = OrderedDict()
    model_dic = model.__dict__
    for key, value in model_dic.items():
        if key in entity_display_columns(entity) and key != 'id':
            value = lookup_id_to_value(profile, key, value)
            model_display[format_name(key)] = value
    return model_display


def model_display_mapping(model, entity):
    """
    Formats model display columns.
    :param model: Entity model
    :type model: Class
    :param entity: Entity
    :type entity: Class
    :return: Dictionary of formatted column name
    with unformatted column name.
    :rtype: OrderedDict
    """
    model_display_cols = OrderedDict()
    model_dic = model.__dict__

    for col in model_dic:
        if col in entity_display_columns(entity) and col != 'id':
            model_display_cols[col] = format_name(col)
    return model_display_cols


def profile_spatial_tables(profile, include_read_only: bool = True):
    """
    Returns the current profile spatial tables.
    :param profile: Current Profile
    :type profile: Class
    :return: Dictionary of spatial tables short name and name
    :param include_read_only: if set to False, then only user editable tables will be returned
    :rtype: Dictionary
    """
    entities = [e for e in profile.entities.values() if e.TYPE_INFO == 'ENTITY' and e.has_geometry_column()]

    if not include_read_only:
        entities = [e for e in entities if e.user_editable]

    spatial_tables = dict([(e.name, e.ui_display()) for e in entities])
    return spatial_tables


def profile_user_tables(profile, include_views=True, admin=False, sort=False, include_read_only: bool = True):
    """
    Returns user accessible tables from current profile and pg_views
    .
    :param profile: Current Profile
    :type profile: Class
    :param include_views: A Boolean that includes or excludes Views
    :type include_views: Boolean
    :return: Dictionary of user tables with name and
    short name as a key and value.
    :param admin: A Boolean that enables administrative unit table if True.
    :type admin: Boolean
    :param include_read_only: if set to False, then only user editable tables will be returned
    :rtype: Dictionary
    """
    from stdm.data.pg_utils import (
        pg_views
    )

    valid_types = [
        'ENTITY',
        'ENTITY_SUPPORTING_DOCUMENT',
        'SOCIAL_TENURE',
        'SUPPORTING_DOCUMENT',
        'VALUE_LIST',
        'ASSOCIATION_ENTITY'
    ]
    if admin:
        valid_types.append('ADMINISTRATIVE_SPATIAL_UNIT')

    entities = [e for e in profile.entities.values() if e.TYPE_INFO in valid_types]

    if not include_read_only:
        entities = [e for e in entities if e.user_editable]

    tables = OrderedDict([(e.name, e.ui_display()) for e in entities])
    if include_views:
        for view in pg_views():
            tables[view] = view

    if sort:
        names = list(tables.keys())
        names = sorted(names)
        sorted_table = OrderedDict()
        for name in names:
            sorted_table[name] = tables[name]
        return sorted_table
    return tables


def db_user_tables(profile):
    """
    Returns user accessible tables from database.
    :param profile: Current Profile
    :param include_views: A Boolean that includes or excludes Views
    :type include_views: Boolean
    :return: Dictionary of user tables with name and
    short name as a key and value.
    :rtype: Dictionary
    """
    from stdm.data.pg_utils import (
        pg_tables
    )
    db_tables = []
    tables = [
        e.name
        for e in
        profile.entities.values()
        if e.TYPE_INFO in [
            'ENTITY',
            'ENTITY_SUPPORTING_DOCUMENT',
            'SOCIAL_TENURE',
            'SUPPORTING_DOCUMENT',
            'VALUE_LIST'
        ]
    ]
    for table in tables:
        if table in pg_tables():
            db_tables.append(table)

    return db_tables


def profile_lookup_columns(profile):
    """
    Returns the list of lookup columns in a profile.
    :param profile: Current Profile
    :type profile: Class
    :return: list of lookup columns
    :rtype: List
    """
    lookup_columns = [
        r.child_column for r in profile.relations.values()
    ]
    return lookup_columns


def lookup_parent_entity(profile, col):
    """
    Gets lookup column's parent entity.
    :param profile:  Object
    :param col: The lookup's child column name
    :type col: String
    :return: Parent lookup entity
    :rtype: Object
    """
    # for r in profile.relations.values():
    #     if r.child_column == col and 'check_' in r.parent.name:
    #         print(vars(r.parent))
    parent_entity = [
        r.parent for r in profile.relations.values()
        if r.child_column == col and 'check_' in r.parent.name
    ]
    if len(parent_entity) > 0:
        return parent_entity[0]
    else:
        return None


def lookup_id_to_value(profile, col, id):
    """
    Converts a lookup id into its value
    using current profile class.
    :param profile: Current profile
    :type profile: Class
    :param col: The column value
    :type col: String
    :param id: The id of the column
    :type id: Integer
    :return: Id of the lookup table or the
    value if no match is found.
    :rtype: Integer or String
    """
    if col in profile_lookup_columns(profile):
        parent_entity = lookup_parent_entity(profile, col)

        if parent_entity is not None:
            db_model = entity_model(parent_entity)
            db_obj = db_model()
            query = db_obj.queryObject().filter(
                db_model.id == id
            ).first()

            if query is not None:
                value = getattr(
                    query,
                    'value',
                    None
                )

                return value
            else:
                return id
        # if the column is a related entity column
        else:
            return id
    else:
        return id


def get_db_attr(db_model, source_col, source_attr, destination_col):
    """
    Gets the column value when supplied with the destination column.
    :param db_model: Database model
    :type db_model: Class
    :param source_col: Column object of the source table.
    :type source_col: Object
    :param source_attr: The source column value
    :type source_attr: String or integer
    :param destination_col: THe destination column name
    :type destination_col: String
    :return: Another column value for the same record
    :rtype: Integer or List
    """
    db_obj = db_model()
    query_result = db_obj.queryObject().filter(
        source_col == source_attr
    ).first()

    if query_result is not None:
        destination_attr = getattr(
            query_result,
            destination_col,
            None
        )
        return destination_attr


def entity_id_to_attr(entity, attr, id):
    """
    Converts an entity column id to another
    column value of the same record.
    :param entity: Entity
    :type entity: Class
    :param attr: Column name
    :type attr: String
    :param id: Id of the entity
    :type id: Integer
    :return: a column value if a match found
    :rtype: Integer or String
    """
    doc_type_model = entity_model(entity)
    doc_type_obj = doc_type_model()
    result = doc_type_obj.queryObject().filter(
        doc_type_model.id == id
    ).first()
    if result is not None:
        attr_val = getattr(
            result,
            attr,
            None
        )
    else:
        attr_val = id

    return attr_val


def entity_id_to_display_col(entity, column, id):
    """
    Converts an entity column id to another
    column value of the same record.
    :param entity: Entity
    :type entity: Class
    :param column: Column name
    :type column: String
    :param id: Id of the entity
    :type id: Integer
    :return: a column value if a match found
    :rtype: Integer or String
    """

    display_cols = entity.columns[column].entity_relation.display_cols
    parent_entity = entity.columns[column].entity_relation.parent
    model = entity_model(parent_entity)
    model_obj = model()
    result = model_obj.queryObject().filter(
        model.id == id
    ).first()
    attr_vals = []

    if result is not None:
        for col in display_cols:

            attr_val = getattr(
                result,
                col,
                None
            )
            if attr_val is not None:
                attr_vals.append(attr_val)

    else:
        attr_vals = [id]

    return ', '.join(attr_vals)


def entity_id_to_model(entity, id):
    """
    Gets the model of an entity based on an id and the entity.
    :param entity: Entity
    :type entity: Object
    :param id: Id of the record
    :type id: Integer
    :return: SQLAlchemy result proxy
    :rtype: Object
    """
    model = entity_model(entity)
    model_obj = model()
    result = model_obj.queryObject().filter(model.id == id).first()
    return result


def entity_attr_to_model(entity, attr, value):
    """
    Gets the first model of an entity based on an attribute and the entity.
    Important- the value needs to be unique.
    :param entity: Entity
    :type entity: Object
    :param attr: Attribute of the record
    :type attr: Any
    :return: SQLAlchemy result proxy
    :rtype: Object
    """
    model = entity_model(entity)
    model_obj = model()
    attr_col_obj = getattr(model, attr)

    result = model_obj.queryObject().filter(
        attr_col_obj == value
    ).first()

    return result


def entity_attr_to_id(entity, col_name, attr_val, lower=False):
    """
    Coverts other column values to id value
    of the same table.
    :param entity: Entity
    :type entity: Class
    :param col_name: The table column name
    :type col_name: String
    :param attr_val: Any value of a source column
    :type attr_val: Any
    :return: The Id of the entity or the attribute
    value if no id is found or the attribute is not valid.
    :rtype: Integer or NoneType
    """
    doc_type_model = entity_model(entity)

    doc_type_obj = doc_type_model()

    model_col = getattr(doc_type_model, col_name)
    if model_col is None:
        raise AttributeError('Specified column does not exist')

    if lower:

        result = doc_type_obj.queryObject().filter(
            func.lower(col_name) == func.lower(attr_val)
        ).first()

    else:
        result = doc_type_obj.queryObject().filter(
            model_col == attr_val
        ).first()

    if result is not None:
        attr_id = getattr(
            result,
            'id',
            None
        )
    else:
        attr_id = attr_val

    return attr_id


def profile_entities(profile):
    """
    Return the current profile primary entity tables.
    :param profile: Profile object
    :type profile: Object
    :return: List a list of entities
    :rtype: List
    """
    entities = [
        e
        for e in
        profile.entities.values()
        if e.TYPE_INFO == 'ENTITY'
    ]
    return entities


def enable_drag_sort(mv_widget):
    """
    Enables internal drag and drop sorting in
    model/view widgets.
    :param mv_widget: The model/view widget for which
    drag and drop sort is enabled
    :type mv_widget: QTableView, QListView
    """
    mv_widget.setDragEnabled(True)
    mv_widget.setAcceptDrops(True)

    # mv_widget.setSelectionMode(
    #     QAbstractItemView.SingleSelection
    # )

    mv_widget.setDragDropOverwriteMode(False)
    mv_widget.setDropIndicatorShown(True)

    mv_widget.setDragDropMode(
        QAbstractItemView.InternalMove
    )

    def drop_event(mv_widget, event):
        """
        A drop event function that prevents overwriting of
        destination rows if a row or cell is a destination
        target.
        :param mv_widget: The model/view widget for which
        drag and drop sort is enabled
        :type mv_widget: QTableView, QListView
        :param event: The drop event
        :type event: QDropEvent.QDropEvent
        :return: None
        :rtype: NoneType
        """
        if isinstance(mv_widget, QListWidget):
            return
        if event.source() == mv_widget:
            view = True
            rows = set(
                [mi.row()
                 for mi in mv_widget.selectedIndexes()
                 ]
            )

            target_row = mv_widget.indexAt(
                event.pos()
            ).row()

            rows.discard(target_row)
            rows = sorted(rows)

            if not rows:
                return

            if target_row == -1:
                target_row = mv_widget.model().rowCount()

            for i in range(len(rows)):
                mv_widget.model().insertRow(target_row)

            row_mapping = dict()  # Src row to target row.
            for idx, row in enumerate(rows):
                if row < target_row:
                    row_mapping[row] = target_row + idx
                else:
                    row_mapping[row + len(rows)] = target_row + idx
            try:
                colCount = mv_widget.model().columnCount()
            except DummyException:
                colCount = mv_widget.columnCount()

            for src_row, tgt_row in sorted(row_mapping.items()):
                for col in range(0, colCount):
                    try:

                        mv_widget.model().setItem(
                            tgt_row,
                            col,
                            mv_widget.model().takeItem(
                                src_row, col
                            )
                        )
                    except DummyException:
                        mv_widget.setItem(
                            tgt_row,
                            col,
                            mv_widget.takeItem(
                                src_row, col
                            )
                        )

            for row in reversed(
                    sorted(row_mapping.keys())
            ):
                mv_widget.model().removeRow(row)

            event.accept()

            return

    mv_widget.__class__.dropEvent = drop_event


def enable_drag_sort_widgets(qt_widget):
    """
    Enables internal drag and drop sorting in
    model/view widgets.
    :param mv_widget: The model/view widget for which
    drag and drop sort is enabled
    :type mv_widget: QTableView, QListView
    """
    qt_widget.setDragEnabled(True)
    qt_widget.setAcceptDrops(True)
    qt_widget.setSelectionMode(
        QAbstractItemView.SingleSelection
    )
    qt_widget.setDragDropOverwriteMode(False)
    qt_widget.setDropIndicatorShown(True)
    qt_widget.setDefaultDropAction(Qt.TargetMoveAction)
    qt_widget.setDragDropMode(
        QAbstractItemView.InternalMove
    )

    def widget_drop_event(qt_widget, event):
        """
        A drop event function that prevents overwriting of destination
        rows if a row or cell is a destination target.
        :param qt_widget: QT widget for which drag and drop sort is enabled
        :param event: The drop event
        :return: None
        :rtype: None
        """

        if event.source() == qt_widget:

            rows = set(
                [mi.row()
                 for mi in qt_widget.selectedIndexes()
                 ]
            )

            widget_item = qt_widget.itemAt(event.pos())
            target_row = qt_widget.row(widget_item)

            rows.discard(target_row)
            rows = sorted(rows)

            if not rows:
                return

            if target_row == -1:
                target_row = qt_widget.count()

            for i in range(len(rows)):
                qt_widget.insertItem(target_row, widget_item)

            row_mapping = dict()  # Src row to target row.
            for idx, row in enumerate(rows):
                if row < target_row:
                    row_mapping[row] = target_row + idx
                else:
                    row_mapping[row + len(rows)] = target_row + idx
            # try:
            #     colCount = qt_widget.model().columnCount()
            # except DummyException:
            #     colCount = qt_widget.columnCount()

            # for src_row, tgt_row in sorted(row_mapping.items()):
            #     for col in range(0, colCount):
            #         try:
            #
            #             qt_widget.model().setItem(
            #                 tgt_row,
            #                 col,
            #                 qt_widget.model().takeItem(
            #                     src_row, col
            #                 )
            #             )
            #         except DummyException:
            for src_row, tgt_row in sorted(row_mapping.items()):
                tgt_widget_item = qt_widget.item(tgt_row)
                tgt_widget = qt_widget.itemWidget(tgt_widget_item)
                qt_widget.setItemWidget(tgt_widget_item, tgt_widget)
                qt_widget.takeItem(src_row)

            for row in reversed(
                    sorted(row_mapping.keys())
            ):
                qt_widget.removeItemWidget(qt_widget.item(row))

            event.accept()

            return

    qt_widget.__class__.dropEvent = widget_drop_event


def simple_dialog(parent, title, message, checkbox_text=None, yes_no=True):
    """
    A simple dialog the enable you show an html message with checkbox.
    :param parent: The parent of the dialog.
    :type parent: QWidget
    :param title: The title of the dialog
    :type title: String
    :param message: The message of the dialog. Use <br>
    to add a new line as it is html.
    :type message: String
    :param checkbox_text: Add a checkbox text, if None,
    the checkbox will not be shown.
    :type checkbox_text: String
    :param yes_no: A boolean to add the Yes No buttons.
    If false, the Ok button is shown.
    :type yes_no: Boolean
    :return: Tuple containing the dialog exec_ result
    and the checkbox result.
    :rtype: Tuple
    """
    simple_dialog = QDialog(
        parent,
        Qt.WindowSystemMenuHint | Qt.WindowTitleHint
    )
    simple_layout = QVBoxLayout(simple_dialog)
    simple_label = QLabel()

    simple_dialog.setWindowTitle(title)
    simple_label.setTextFormat(Qt.RichText)
    simple_label.setText(message)

    simple_layout.addWidget(simple_label)

    if checkbox_text:
        confirm_checkbox = QCheckBox()
        confirm_checkbox.setText(checkbox_text)
        simple_layout.addWidget(confirm_checkbox)
    simple_buttons = QDialogButtonBox()

    if yes_no:
        simple_buttons.setStandardButtons(
            QDialogButtonBox.Yes | QDialogButtonBox.No
        )
        simple_buttons.rejected.connect(simple_dialog.reject)

    else:
        simple_buttons.setStandardButtons(
            QDialogButtonBox.Ok
        )
    simple_buttons.accepted.connect(simple_dialog.accept)

    simple_layout.addWidget(simple_buttons)

    simple_dialog.setModal(True)
    result = simple_dialog.exec_()
    if checkbox_text is not None:
        return result, confirm_checkbox.isChecked()
    else:
        return result, False


def file_text(path: str) -> str:
    """
    Read any readable file.
    :param path: The file path
    :type path: String
    :return: The text of the file
    :rtype: String
    """
    try:
        with open(path, 'r', encoding='windows=1252') as inf:
            text = inf.read()
        return text
    except IOError as ex:
        raise ex


def profile_and_user_views(profile, check_party=False):
    """
    Gets current profile and user views. If views has a valid profile prefix
    and not valid current profile entity, it will be excluded.
    :param profile: The profile object
    :type profile: Object
    :param check_party: A boolean to filter out party views based on multi_party
    If check party is True and multi_party is True, it excludes party views
    from the return
    :type check_party: Boolean
    :return: List of profile and user views
    :rtype: List
    """
    from stdm.data.pg_utils import (
        pg_views
    )
    from stdm.data.configuration.stdm_configuration import (
        StdmConfiguration
    )

    source_tables = []

    social_tenure = profile.social_tenure

    for view, entity in social_tenure.views.items():
        source_tables.append(view)

        # For party views, if check party is true, add party views.
        # If multi-party is false. Otherwise, add all party views - this is not
        # recommended for composer data source.
        #if entity in social_tenure.parties:
            #if check_party:
                #if not social_tenure.multi_party:
                    #source_tables.append(view)
            #else:
                #source_tables.append(view)
        #else:
            #source_tables.append(view)

    stdm_config = StdmConfiguration.instance()
    all_str_views = []
    for prof in list(stdm_config.profiles.values()):
        all_str_views.extend(list(prof.social_tenure.views.keys()))

    for value in pg_views():
        # if value not in all_str_views:  #and value not in source_tables:
         if value[:2] == profile.prefix:
            if value not in source_tables:
                source_tables.append(value)

    return source_tables


def user_non_profile_views():
    """
    Gets and return user based views excluding profile views in the configuration.
    :return: User views
    :rtype: List
    """
    from stdm.data.configuration.stdm_configuration import (
        StdmConfiguration
    )
    from stdm.data.pg_utils import (
        pg_views
    )
    source_tables = []
    stdm_config = StdmConfiguration.instance()
    all_str_views = []
    for prof in list(stdm_config.profiles.values()):
        all_str_views.extend(list(prof.social_tenure.views.keys()))

    for value in pg_views():
        if value not in all_str_views:
            source_tables.append(value)
    return source_tables


def value_from_metadata(key: string) ->str:
    """
    Returns a value from the metadata file.
    """
    with open('{}/metadata.txt'.format(PLUGIN_DIR)) as meta:
        lines = meta.readlines()
        value = ""
        for line in lines:
            if key in line:
                key_line = line.split('=')
                value = key_line[1]
                break
        return value


def code_columns(entity, current_column_name):
    """
    Gets the code columns in an entity.
    :param entity: The entity object
    :type entity: Object
    :param current_column_name: The exclude/current column name.
    :type current_column_name: String
    :return: List code column names.
    :rtype: List
    """
    code_columns = []
    for col in entity.columns.values():
        if col.name != current_column_name:
            if col.TYPE_INFO == 'AUTO_GENERATED':
                code_columns.append(col.name)
    return code_columns


def string_to_boolean(string_bool, default):
    """
    Converts string to boolean.
    :param string_bool: The string containing a boolean text.
    :type string_bool: String
    :param default: Default boolean value.
    :type default: Boolean
    :return: Converted boolean
    :rtype: Boolean
    """
    if not isinstance(string_bool, bool):
        if string_bool == '':
            result = default
        elif string_bool is None:
            result = default
        elif string_bool.lower() == 'true':
            result = True
        elif string_bool.lower() == 'false':
            result = False
        else:
            result = default
        return result
    else:
        return string_bool


def is_ascii(s):
    """Checks if a string contains non ASCII characters."""
    return bool(re.match(r'[\x00-\x7F]+$', s))
