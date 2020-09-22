REG_EDITOR_CLS_EXTENSIONS = {}

from stdm.ui.forms.ext import *


def entity_dlg_extension(entity_dlg):
    """
    Creates an instance of the corresponding custom editor extension if one
    has been defined for the given profile and entity respectively.
    :param entity_dlg: Instance of entity dialog.
    :type entity_dlg: EntityEditorDialog
    :return: Returns instance of the corresponding custom editor extension if
    one has been defined for the given profile and entity respectively,
    otherwise it returns None.
    :rtype: AbstractEditorExtension
    """
    cls = editor_cls_extension(entity_dlg.entity)
    if cls is None:
        return None

    return cls(entity_dlg)


def editor_cls_extension(entity):
    """
    Get the AbstractEditorExtension subclass specified for the given entity.
    :param entity: Entity object.
    :type entity: Entity
    :return: Returns the AbstractEditorExtension subclass specified for the
    entity in the given profile. None is returned if there is no matching
    entity in the given profile.
    :rtype: AbstractEditorExtension
    """
    return REG_EDITOR_CLS_EXTENSIONS.get(
        (entity.profile.name, entity.short_name),
        None
    )