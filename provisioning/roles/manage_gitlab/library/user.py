#!/usr/bin/env python

DOCUMENTATION='''
module: gitlab_user
author: John Bond (gitlab-ansible@johnbond.org)
short_description: manage gitlab users
requierments: 
description: 
  - Manage gitlab users and there attributes
options:
    name:
        required: true
        aliases [ "gitlab_user" ]
        description:
            - Name of the gitlab user
    email:
        required: true
        description:
            - email address of user
    linkedin:
        required: false
        description:
            - linked in id
    skype:
        required: false
        description:
            - skype id
    twitter:
        required: false
        description:
            - twitter id

'''

import os
import gitlab
import psycopg2
from pwd import getpwnam

def get_auth_token():
    os.setuid(getpwnam('gitlab-psql').pw_uid)
    conn = psycopg2.connect(
            host='/var/opt/gitlab/postgresql', 
            database='gitlabhq_production')
    cur = conn.cursor()
    cur.execute('select authentication_token from users where admin = %s limit 1', 't')
    key = cur.fetchone()[0]
    conn.close()
    return key


class GitlabUser(object):

    id    = None
    user  = None
    exist = None

    def __init__(self, module):
        self.module         = module
        self.state          = module.params['state']
        self.name           = module.params['name']
        self.email          = module.params['email']
        self.username       = module.params['username']
        if not self.username:
            self.username = name
        self.password       = module.params['password']
        if not self.password:
            self.password = 'something randome'
        self.skype          = module.params['skype']
        self.linkedin       = module.params['linkedin']
        self.twitter        = module.params['twitter']
        self.admin          = module.params['admin']
        self.gitlab_ctl     = gitlab.Gitlab(
                'http://127.0.0.1', get_auth_token(), ssl_verify=False)
        self.auth()

    def _gitlab_user(self):
        return {
            'name'     : self.name,
            'email'    : self.email,
            'username' : self.username,
            'password' : self.password,
            'skype'    : self.skype,
            'linkedin' : self.linkedin,
            'twitter'  : self.twitter,
            'admin'    : self.admin}

    def auth(self):
        self.gitlab_ctl.auth()

    def exists(self):
        if self.exist == None:
            self.exist = False
            for user in self.gitlab_ctl.users.all():
                if user.name == self.name:
                    self.id    = user.id
                    self.user  = user
                    self.exist = True
        return self.exist
    
    def remove(self):
        rc  = 0
        out = ''
        err = ''
        try:
            gitlab_ctl.users.delete(self.id)
        except gitlab.GitlabDeleteError as e:
            rc  = 1
            err = e.message
        return  (rc, out, err)

    def create(self):
        rc  = 0
        out = ''
        err = ''
        try:
            self.gitlab_ctl.users.create(self._gitlab_user())
        except gitlab_user.GitlabCreateError as e:
            rc  = 1
            err = e.message
        return (rc, out, err)

    def update(self):
        rc  = None
        out = ''
        err = ''
        if rc != None:
            out = self.gitlab_ctl.update(self.user)
        return (rc, out, err)



def main():
    module = AnsibleModule(
            argument_spec=dict(
                state=dict(default='present', choices=['present', 'absent'], type='str'),
                name=dict(required=True, type='str'),
                email=dict(required=True, type='str'),
                username=dict(default=None, type='str'),
                skype=dict(default=None, type='str'),
                linkedin=dict(default=None, type='str'),
                twitter=dict(default=None, type='str'),
                admin=dict(default='no', type='bool'),
            ),
            supports_check_mode=True
        )
    gitlab_user = GitlabUser(module)

    rc = None
    out = ''
    err = ''
    result = {}
    result['name']  = gitlab_user.name
    result['state'] = gitlab_user.state
    if gitlab_user.state == 'absent':
        if gitlab_user.exists():
            if module.check_mode:
                module.exit_json(changed=True)
            (rc, out, err) = user.remove_user()
            if rc != 0:
                module.fail_json(name=gitlab_user.name, msg=err, rc=rc)
    elif gitlab_user.state == 'present':
        if not gitlab_user.exists():
            if module.check_mode:
                module.exit_json(changed=True)
            (rc, out, err) = gitlab_user.create()
        else:
            (rc, out, err) = gitlab_user.update()

    if rc is None:
        result['changed'] = False
    else:
        result['changed'] = True
    if out:
        result['stdout'] = out
    if err:
        result['stderr'] = err

    module.exit_json(**result)


from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()

