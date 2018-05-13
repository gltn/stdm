from stdm.data.pg_utils import (
       pg_table_exists,
       _execute
       )

class PrivilegeProvider(object):
    Privileges = {'Create':'INSERT','Select':'SELECT','Update':'UPDATE','Delete':'DELETE'}
    def __init__(self, content_name, profile=None):
        self.content_name = content_name
        self.content_short_name = self.fmt_short_name(self.content_name)
        self.related_contents = {}
        self.profile = profile 

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


class SinglePrivilegeProvider(PrivilegeProvider):
    def __init__(self, content_name, profile):
        super(SinglePrivilegeProvider, self).__init__(content_name, profile)
        self.fetch_related_content(self.content_short_name)
        self.content_table_name = self.table_name(self.content_short_name)
        self.role = ''

    def fetch_related_content(self, short_name):
        if short_name in self.profile.entities:
            for column in self.profile.entities[short_name].columns.values():
                if hasattr(column, 'entity_relation'):
                    self.related_contents[column.name] = column.entity_relation.parent.name

    def table_name(self, short_name):
        table_name = ''
        if short_name in self.profile.entities:
            table_name = self.profile.entities[short_name].name
        return table_name

    def fmt_short_name(self, name):
        return name[name.index(' ')+1:].replace(' ','_')

    def grant_revoke_privilege(self, operation):
        try:
            privilege = PrivilegeProvider.Privileges[self.content_name[:self.content_name.index(' ')]]
        except:
            privilege = 'INSERT'

        if pg_table_exists(self.content_table_name):
            self.grant_or_revoke(operation, privilege, self.content_table_name, self.role)
        for related_content in self.related_contents.values():
            self.grant_or_revoke(operation, 'SELECT', related_content, self.role)
            if privilege <> 'SELECT':
                self.grant_or_revoke(operation, privilege, related_content, self.role)


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

