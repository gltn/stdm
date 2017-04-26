"""

"""
from stdm.settings import current_profile



def read():
    """
    Test implementation hand codes the entity but would need to be
    implemented on the dialog for user to make their own selection
    :param self:
    :return:dict of entity column and data type
    """
    entity_prop = {}
    profile_reader = current_profile()
    cols = profile_reader.entity_by_name("lo_parcel").columns
    col_objs =cols.values()
    for obj in col_objs:
        entity_prop[obj.name] = obj.TYPE_INFO
    return entity_prop

def read_lookup_for_column(col, obj):
    """
    Check if the column has a lookup and get the associated lookup definition
    :return:
    """
    if isinstance(col, obj):
        if col.TYPE_INFO == "LOOKUP":
            value_list = obj.value_list
            for val in value_list.values.values():
                print obj.name, value_list.name, val.value, val.code




