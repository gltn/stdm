import copy
from stdm.data.pg_utils import (
       pg_table_exists,
       _execute
       )

class PrivilegeProvider(object):
    Privileges = {'Create':'INSERT','Select':'SELECT','Update':'UPDATE','Delete':'DELETE'}
    def __init__(self, content_name, profile=None):
        self.content_name = content_name
        self.content_short_name = self.fmt_short_name(self.content_name)
        self.titlized_short_name = self.content_short_name.title().replace(' ','')
        self.related_contents = {}
        self.profile = profile
        self.base_table_roles = self.get_base_table_roles()

    def fmt_short_name(self, name):
        raise NotImplementedError

    def grant_revoke_privilege(self, operation):
        raise NotImplementedError

    def grant_privilege(self):
        self.grant_revoke_privilege('GRANT')

    def revoke_privilege(self):
        self.grant_revoke_privilege('REVOKE')

    def grant_or_revoke(self, action, privilege, table, role):
        gr_str = 'TO' if action == 'GRANT' else 'FROM'
        stmt = '{} {} ON TABLE {} {} {}'.format(action, privilege, table, gr_str, role)
        _execute(stmt)

    def base_roles(self, table_name):
        results = set()
        sql = "Select grantee from information_schema.role_table_grants "\
                "where table_name = '{}' ".format(table_name)
        records = _execute(sql)

        for record in records:
            results.add(record['grantee'])

        return results

    def get_base_table_roles(self):
        base_tables =  ['content_base', 'content_roles', 'role']
        table_roles = {}
        for bt in base_tables:
            roles = self.base_roles(bt)
            table_roles[bt] = copy.deepcopy(roles)
        return table_roles

    def get_supporting_doc_table(self, entity_short_name):
        '''
        returns a supporting document entity
        '''
        support_doc_table = None
        if entity_short_name in self.profile.entities:
            entity = self.profile.entities[entity_short_name]
            if entity.supports_documents:
                support_doc_table = entity.supporting_doc
        return support_doc_table


class SinglePrivilegeProvider(PrivilegeProvider):
    def __init__(self, content_name, profile):
        super(SinglePrivilegeProvider, self).__init__(content_name, profile)
        self.fetch_related_content(self.titlized_short_name)
        self.content_table_name = self.table_name(self.content_short_name)
        self.supporting_doc_table = self.get_supporting_doc_table(self.titlized_short_name)
        self.support_doc_table_name =''
        self.support_doc_type_name = ''
        self._support_doc_names()
        self.role = ''

    def _support_doc_names(self):
        if self.supporting_doc_table is not None:
            self.support_doc_table_name = self.supporting_doc_table.name
            self.support_doc_type_name = self.supporting_doc_table.doc_type.value_list.name

    def fetch_related_content(self, entity_short_name):
        if entity_short_name in self.profile.entities:
            for column in self.profile.entities[entity_short_name].columns.values():
                if hasattr(column, 'entity_relation'):
                    self.related_contents[column.name] = column.entity_relation.parent.name

    def table_name(self, entity_short_name):
        table_name = ''
        if entity_short_name in self.profile.entities:
            table_name = self.profile.entities[entity_short_name].name
        return table_name

    def fmt_short_name(self, name):
        if name.find(' ') > 0:
            return name[name.index(' ')+1:]  #.replace(' ','_')
        else:
            return name

    def grant_privilege_base_table(self, role):
        base_tables =  ['content_base', 'content_roles', 'role']
        for bt in base_tables:
            if not role in self.base_table_roles[bt]:
                self.grant_or_revoke('GRANT', 'SELECT', bt, role)

    def grant_revoke_privilege(self, operation):
        try:
            privilege = PrivilegeProvider.Privileges[self.content_name[:self.content_name.index(' ')]]
        except:
            privilege = 'INSERT'

        if operation == 'GRANT':
            self.grant_privilege_base_table(self.role)

        if pg_table_exists(self.content_table_name):
            self.grant_or_revoke(operation, privilege, self.content_table_name, self.role)
            if privilege == 'INSERT':
                # INSERT privilege will also trigger an issue of SELECT privilege
                self.grant_or_revoke(operation, 'SELECT', self.content_table_name, self.role)

        for related_content in self.related_contents.values():
            self._grant_revoke(operation, privilege, related_content, self.role)

        if self.support_doc_table_name != '':
            self._grant_revoke(operation, privilege, self.support_doc_table_name, self.role)
            # Supporting document type
            self._grant_revoke(operation, privilege, self.support_doc_type_name, self.role)

    def _grant_revoke(self, op, priv, cont, role):
        self.grant_or_revoke(op, 'SELECT', cont, role)
        if priv != 'SELECT':
            self.grant_or_revoke(op, priv, cont, role)



class MultiPrivilegeProvider(PrivilegeProvider):
    def __init__(self, content_name):
        super(MultiPrivilegeProvider, self).__init__(content_name)
        self.roles = {}
        self.populate_roles()

    def fmt_short_name(self, name):
        return name.replace(' ','_')

    def add_related_content(self, column_name, content):
        self.related_contents[column_name] = content

    def populate_roles(self):
        """
        Inherit existing privileges for a given role. These are to be
        granted to the new content
        Structure of the roles dictionary:
        roles['manager'] = ['Select', 'Create']
        """
        stmt = "SELECT content_base.id, content_base.name AS content, " \
                         "content_roles.role_id, role.name AS role " \
                   " FROM content_base, content_roles, role " \
                  " WHERE content_roles.role_id = role.id " \
                    " AND content_base.id = content_roles.content_base_id " \
                    " AND content_base.name like '%%{}' " \
                  " ORDER BY role.name ".format(self.content_name)

        records = _execute(stmt)
        for row in records:
            content = row['content']
            role = row['role']
            if role == 'postgres':continue
            if role not in self.roles:
                self.roles[role] = []
            self.roles[role].append(content[:content.index(' ')])

    def grant_revoke_privilege(self, operation):
        for role, privileges in self.roles.iteritems():
            for p in privileges:
                privilege = PrivilegeProvider.Privileges[p]
                temp_content = ''
                for related_content in self.related_contents.values():
                    if temp_content == related_content:continue
                    if pg_table_exists(related_content):
                        temp_content = related_content
                        self.grant_or_revoke(operation, privilege, related_content, role)
                        self.grant_or_revoke(operation, 'SELECT', related_content, role)

