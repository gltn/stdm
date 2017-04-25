"""

"""
from stdm.settings import current_profile


def read():
    """

    :param self:
    :return:dict of entity column and data type
    """
    profile_read = current_profile()
    return profile_read

def read1():
    """

    :param self:
    :return:dict of entity column and data type
    """
    '''print vars(current_profile())'''
    entity_prop = {}
    profile_read = current_profile()
    cols = profile_read.entity_by_name("lo_parcel").columns
    col_objs =cols.values()
    for obj in col_objs:
        entity_prop[obj.name] = obj.TYPE_INFO
    return entity_prop

def select_entity():
    """

    :return:
    """
    profile_read = current_profile()
    entity = profile_read.entity_by_name("lo_parcel")
    return entity