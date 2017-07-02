"""

"""

class EntityFormatter():
    """
    class handles entity as a string and processes the XForm model
    and various XForm attributes. 
    """

    def __init__(self, profile):
        """
        :param entity: string
        """
        self._haslookup = False
        self._profile = profile

        self._child_entity = None



    def xform__model_name(self):
        """

        :return: 
        """
        return self._entity

    def set_xform_model_name(self, entity):
        """

        :return: 
        """
        self._profile = entity
        return self._profile

    def format_foreign_key(self):
        """
        Format foreign key column to Xform representation
        :return:
        """
        pass

    def format_photo_blob(self):
        """
        Format image upload column to Xform format
        :return:
        """
        pass

    def format_document_upload(self):
        """
        Format the column for data upload to Xform document upload url
        :return:
        """

    def model_has_lookup(self):
        """

        :return: 
        """
        return self._haslookup

    def model_category_group(self, profile, item):
        """

        :param bool: 
        :return: 
        """
        return '/'+profile+'/{}'.format(item)

    def process_lookup(self):
        """

        :return: 
        """
        pass

    def process_group_categories(self):
        """

        :return: 
        """

    def format_model_attribute(self, attrib):
        """
        Format the entity attribute and extract the original column name
        :param attrib:
        :return:
        """
        typle_name = attrib.partition('.')
        return unicode(typle_name[2])

    def set_model_data_type(self, val):
        """
        Method to return the datatype of the selected entity in XForm types
        :param val: 
        :return: string
        """
        data_type = self.model_type_from_columntype(val)
        if data_type:
            return data_type
        else:
            return None

    def model_data_types(self, vals):
        """
        """
        value_list = []
        for val in vals.values():
            r_type = self.model_type_from_columntype(val)
            if r_type == None:
                continue
            value_list.append(r_type)
        return value_list

    def set_model_xpath(self, item, entity = None):
        """
        This method formats and returns an entity short path
        as required by model within the bind item section in the final document
        :return: string
        :type: string
        :return: string
        """
        if entity:
            return '/'+self._profile+'/'+entity+'/{}'.format(item)
        else:
            return '/'+self._profile+'/{}'.format(item)


    def model_xpaths(self, items):
        """
        Method to check if the passed items are dictionary 
        and then then convert the items and return a xpath format 
        from the entity attributes.
        :param items: dkc
        :type: dictionary
        :return: list
        """
        path_lst = []
        for key in items.keys():
            xpath = '/'+self._entity+'/'+key
            path_lst.append(xpath)
        return path_lst

    def model_unique_uuid(self):
        """
        Create a place holder to generate a unique id for the form
        :return:
        """
        unique_uuid = "concat('uuid:', uuid())"
        return unique_uuid

    @staticmethod
    def model_type_from_columntype(val):
        """
        Method to convert the entity column type to XForm type
        need to implement dynamic variation of types.. now handcoded
        :return: 
        """
        xform_type = {
            'VARCHAR': 'string',
            'DOUBLE': 'integer',
            'GEOMETRY': 'geoshape',
            'LOOKUP': 'select1',
            'MULTIPLE_SELECT': 'select',
            'BOOl': 'select',
            'ADMIN_SPATIAL_UNIT': 'string',
            'FOREIGN_KEY': 'string',
            'DATE': 'date',
            'DATETIME': 'datetime'
        }

        return xform_type.get(val)

    @staticmethod
    def xform_custom_params_types(val):
        """
        These formats are specific for XForm type and are default in the form
        :param val:
        :return:
        """
        param_type = {
            'start': 'dateTime',
            'end': 'dateTime',
            'today': 'date',
            'deviceid': 'string'
        }

        return param_type.get(val)
