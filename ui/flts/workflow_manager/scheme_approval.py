class Status(object):
    """
    Scheme approval base class. Maintains shared attributes and methods
    """
    def __init__(self):
        self._checked_ids = self._workflow_pks = None
        self.data_service = self._lookup = None

    def set_check_ids(self, checked_ids):
        """
        Sets checked scheme record IDs
        :param checked_ids: Checked scheme record IDs
        :type checked_ids: OrderedDict
        """
        self._checked_ids = checked_ids

    def _checked_scheme_ids(self, status_option):
        """
        Return checked scheme IDs
        :return scheme_ids: Checked scheme IDs/primary keys
        :rtype scheme_ids: List
        """
        scheme_ids = [
            scheme_id for scheme_id, (row, status, scheme_number) in
            self._checked_ids.iteritems() if int(status) != status_option
        ]
        return scheme_ids

    @property
    def _workflow_ids(self):
        """
        Returns workflow IDs/primary keys
        :return _workflow_pks: Workflow record ID/primary keys
        :rtype _workflow_pks: List
        """
        if self._workflow_pks is None:
            self._workflow_pks = self.data_service.workflow_ids()
        return self._workflow_pks

    def _scheme_workflow_filter(self, scheme_id, workflow_id):
        """
        Scheme workflow update/query filters
        :param scheme_id: Scheme record id
        :type scheme_id: Integer
        :param workflow_id: Workflow record id
        :type workflow_id: Integer
        :return workflow_filter: Workflow type data filter
        :rtype workflow_filter: Dictionary
        """
        workflow_filter = {
            self._lookup.SCHEME_COLUMN: scheme_id,
            self._lookup.WORKFLOW_COLUMN: workflow_id
        }
        return workflow_filter

    def _filter_in(self, entity_name, filters):
        """
        Return query objects as a collection of filter using in_ operator
        :param entity_name: Name of entity to be queried
        :type entity_name: String
        :param filters: Query filter columns and values
        :type filters: Dictionary
        :return: Query object results
        :rtype: InstrumentedList
        """
        return self.data_service.filter_in(entity_name, filters).all()

    def scheme_workflow_id(self, query, column, scheme_id, workflow_id):
        """
        Return scheme workflow record IDs
        :return: Query object results
        :type: Query
        :param column: Column name
        :param column: String
        :param scheme_id: Scheme record ID
        :type scheme_id: Integer
        :param workflow_id: Workflow record ID
        :type workflow_id: Integer, List
        :return record_id: Scheme workflow record ID
        :return record_id: Integer or NoneType
        """
        record_id = []
        for q in query:
            q_scheme_id = getattr(q, self._lookup.SCHEME_COLUMN, None)
            q_workflow_id = getattr(q, self._lookup.WORKFLOW_COLUMN, None)
            if q_scheme_id == scheme_id:
                if isinstance(workflow_id, list) and q_workflow_id in workflow_id:
                    record_id.append(getattr(q, column, None))
                elif q_workflow_id == workflow_id:
                    record_id.append(getattr(q, column, None))
        if isinstance(workflow_id, list):
            return record_id
        elif record_id:
            return record_id[0]

    @ staticmethod
    def _get_config_option(config):
        """
        Returns save/update configuration options
        :param config: Save/update configuration options
        :type config: Named
        :return option: Save/update configuration option
        :rtype option: named tuple
        """
        for option in config:
            yield option


class Approve(Status):
    """
    Manages scheme approval in Scheme Establishment and
    First, Second and Third Examination and Scheme Revision FLTS workflows
    """
    def __init__(self, data_service, object_name):
        super(Approve, self).__init__()
        self.data_service = data_service
        self._lookup = self.data_service.lookups
        self._checked_ids = None
        self._object_name = object_name
        self._workflow_filter = None
        self._update_columns = self.data_service.update_columns
        self._save_columns = self.data_service.save_columns

    def approve_items(self, status_option):
        """
        Returns current workflow approve update values, columns and filters
        :param status_option: Approve or disapprove status
        :type status_option: Integer
        :return valid_items: Approve update values, columns and filters
        :rtype valid_items: Dictionary
        """
        valid_items = {}
        scheme_numbers = {"valid": [], "invalid": []}
        scheme_ids = self._checked_scheme_ids(status_option)
        prev_workflow_id = self._prev_workflow_id()
        filters = self._scheme_workflow_filter(scheme_ids, [prev_workflow_id])
        query_objects = self._filter_in("Scheme_workflow", filters)  # TODO: Place name in the config file
        for scheme_id, (row, status, scheme_number) in \
                self._checked_ids.iteritems():
            if int(status) != status_option:
                prev_approval_id = self.scheme_workflow_id(
                    query_objects, self._lookup.APPROVAL_COLUMN,
                    scheme_id, prev_workflow_id
                )
                update_items = self._approval_updates(
                    prev_approval_id, scheme_id, status_option
                )
                if update_items:
                    valid_items[row] = update_items
                    scheme_numbers["valid"].append(scheme_number)
                    continue
                scheme_numbers["invalid"].append((
                    scheme_number, prev_workflow_id, prev_approval_id
                ))
        return valid_items, scheme_numbers

    def _prev_workflow_id(self):
        """
        Return preceding workflow record id
        :return workflow_id: Preceding workflow record id
        :rtype workflow_id: Integer
        """
        workflow_id = self._get_workflow_id()
        index = self._workflow_ids.index(workflow_id)
        if index == 0:
            return self._workflow_ids[index]
        return self._workflow_ids[(index - 1)]

    def _approval_updates(self, approval_id, scheme_id, status):
        """
        Return valid approval update items
        :param approval_id: Preceding workflow approval record ID
        :type approval_id: Integer
        :param scheme_id: Checked items scheme record ID
        :type scheme_id: Integer
        :param status: Approve record ID status
        :type status: Integer
        :return update_items: Valid approval update items
        :rtype update_items: List
        """
        update_items = []
        for updates in self._get_config_option(self._update_columns):
            if approval_id == status or self._object_name == "schemeLodgement":
                update_filters = self._scheme_workflow_filter(
                    scheme_id, self._get_workflow_id()
                )
                update_items.append([updates.column, status, update_filters])
        return update_items

    def next_approval_items(self, approval_items):
        """
        Returns succeeding workflow approval update values, columns and filters
        :param approval_items: Current work flow update values, columns and filters
        :type approval_items: Dictionary
        :return update_items: Next workflow update values, columns and filters
        :rtype update_items: Dictionary
        :return save_items: Next workflow save values, columns and filters
        :rtype save_items: Dictionary
        """
        update_items = {}
        save_items = {}
        next_workflow_id = self._next_workflow_id()
        approval_updates, scheme_ids = self._next_approval_updates(
            approval_items, self._lookup.PENDING(), next_workflow_id
        )
        filters = self._scheme_workflow_filter(scheme_ids, [next_workflow_id])
        query_objects = self._filter_in("Scheme_workflow", filters)  # TODO: Place name in the config file
        current_workflow_id = self._get_workflow_id()
        for row, columns in approval_items.iteritems():
            items, scheme_id = approval_updates[row]
            workflow_id = self.scheme_workflow_id(
                query_objects, self._lookup.WORKFLOW_COLUMN,
                scheme_id, next_workflow_id
            )
            if items and current_workflow_id != self._workflow_ids[-1]:
                if workflow_id is not None:
                    update_items[row] = items
                    continue
                save_items[row] = self._save_items(items[0])
        return update_items, save_items

    def _save_items(self, items):
        """
        Returns save items
        :Param items: Save items; columns, values and filters
        :type items: List
        :return save_items: Save items; columns, values and entity
        :rtype save_items: List
        """
        save_items = []
        col, status, filters = items
        for option in self._get_config_option(self._save_columns):
            column = option.column
            name = self._get_dict_value(column)
            if name in filters:
                save_items.append([column, filters[name], option.entity])
            elif name == self._get_dict_value(col):
                status = status if status else self._lookup.PENDING()
                save_items.append([column, status, option.entity])
        return save_items

    @staticmethod
    def _get_dict_value(attr):
        """
        Returns values of a dictionary
        :param attr: Attribute
        :return: Attribute value
        :rtype: Dictionary/non-dictionary
        """
        if isinstance(attr, dict):
            value = attr.values()
            if len(value) == 1:
                value = value[0]
            return value
        return attr

    def _next_workflow_id(self):
        """
        Return succeeding workflow record id
        :return workflow_id: Succeeding workflow record id
        :rtype workflow_id: Integer
        """
        workflow_id = self._get_workflow_id()
        index = self._workflow_ids.index(workflow_id)
        if index == len(self._workflow_ids) - 1:
            return self._workflow_ids[index]
        return self._workflow_ids[(index + 1)]

    def _next_approval_updates(self, approval_items, new_value, workflow_id):
        """
        Return valid succeeding workflow approval update items
        :param approval_items: Current workflow update values, columns and filters
        :type approval_items: Dictionary
        :param new_value: Update value
        :type new_value: Multiple types
        :param workflow_id: Workflow record ID
        :type workflow_id: Integer
        :return update_items: Valid approval update items
        :rtype update_items: List
        :return modified_items: Modified approval items
        :rtype modified_items: Dictionary
        :return scheme_ids: Check scheme IDs/primary keys
        :rtype scheme_ids: List
        """
        update_items = {}
        scheme_ids = []
        for row, columns in approval_items.iteritems():
            items = []
            scheme_id = None
            for column, value, update_filters in columns:
                scheme_id = update_filters[self._lookup.SCHEME_COLUMN]
                filters = update_filters.copy()
                filters[self._lookup.WORKFLOW_COLUMN] = workflow_id
                items.append([column, new_value, filters])
            scheme_ids.append(scheme_id)
            update_items[row] = (items, scheme_id)
        return update_items, scheme_ids

    def _get_workflow_id(self):
        """
        Return workflow id/primary key
        :return: Workflow id/primary key
        :rtype: Integer
        """
        if self._workflow_filter:
            return self._workflow_filter[self._lookup.WORKFLOW_COLUMN]
        return self.data_service.get_workflow_id(self._object_name)


class Disapprove(Status):
    """
    Manages scheme disapproval in Scheme Establishment and
    First, Second and Third Examination FLTS workflows
    """
    def __init__(self, data_service):
        super(Disapprove, self).__init__()
        self.data_service = data_service
        self._lookup = self.data_service.lookups
        self._checked_ids = None
        self._update_columns = self.data_service.update_columns

    def disapprove_items(self, status_option):
        """
        Returns workflow disapprove update values, columns and filters
        :param status_option: Disapprove status
        :type status_option: Integer
        :return valid_items: Disapprove update values, columns and filters
        :rtype valid_items: Dictionary
        """
        valid_items = {}
        scheme_numbers = []
        scheme_ids = self._checked_scheme_ids(status_option)
        filters = self._scheme_workflow_filter(scheme_ids, self._workflow_ids)
        query_objects = self._filter_in("Scheme_workflow", filters)  # TODO: Place name in the config file
        for scheme_id, (row, status, scheme_number) in \
                self._checked_ids.iteritems():
            if int(status) != status_option:
                workflow_ids = self.scheme_workflow_id(
                    query_objects, self._lookup.WORKFLOW_COLUMN,
                    scheme_id, self._workflow_ids
                )
                update_items = self._disapproval_updates(
                    workflow_ids, scheme_id, status_option
                )
                if update_items:
                    valid_items[row] = update_items
                    scheme_numbers.append(scheme_number)
        return valid_items, scheme_numbers

    def _disapproval_updates(self, workflow_ids, record_id, status):
        """
        Return disapproval update items
        :param workflow_ids: Preceding and succeeding workflow record IDs
        :type workflow_ids: List
        :param record_id: Checked items scheme record ID
        :type record_id: Integer
        :param status: Disapprove record ID status
        :type status: Integer
        :return update_items: Disapproval update items
        :rtype update_items: List
        """
        update_items = []
        for updates in self._get_config_option(self._update_columns):
            for workflow_id in workflow_ids:
                if workflow_id is not None:
                    update_filters = self._scheme_workflow_filter(
                        record_id, workflow_id
                    )
                    update_items.append([updates.column, status, update_filters])
        return update_items
