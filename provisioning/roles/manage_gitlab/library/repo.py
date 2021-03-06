#!/usr/bin/env python

DOCUMENTATION='''
module: gitlab_repo
author: John Bond (gitlab-ansible@johnbond.org)
short_description: manage gitlab repos
requierments: 
description: 
  - Manage gitlab repos and there attributes
options:
    name:
        required: true
        aliases [ "gitlab_repo" ]
        description:
            - Name of the gitlab repo
    path:
        required: false
        description:
            - custom repository name for new project. By default generated based on name
    namespace_id:
        required: false
        description:
            - namespace for the new project (defaults to user)
    description:
        required: false
        description:
            - short project description
    issues_enabled:
        required: false
        description:
            - enable issues board
    merge_requests_enabled:
        required: false
        description:
            - enable merge requests
    builds_enabled:
        required: false
        description:
            - enable builds
    wiki_enabled:
        required: false
        description:
            - enable wiki
    snippets_enabled:
        required: false
        description:
            - ensable snippets
    public:
        required: false
        description:
            - if true same as setting visibility_level = 20
    visibility_level:
        required: false
        description:
            - set the visability level

'''

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

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


class GitlabRepo(object):

    id    = None
    project  = None
    exist = None

    def __init__(self, module):
        self.module                 = module
        self.state                  = module.params['state']
        self.name                   = module.params['name']
        self.path                   = module.params['path']
        self.namespace_id           = module.params['namespace_id']
        self.description            = module.params['description']
        self.issues_enabled         = module.params['issues_enabled']
        self.merge_requests_enabled = module.params['merge_requests_enabled']
        self.builds_enabled         = module.params['builds_enabled']
        self.wiki_enabled           = module.params['wiki_enabled']
        self.snippets_enabled       = module.params['snippets_enabled']
        self.public                 = module.params['public']
        self.visibility_level       = int(module.params['visibility_level'])
        self.gitlab_ctl             = gitlab.Gitlab(
                'https://127.0.0.1', get_auth_token(), ssl_verify=False)
        self.auth()

    def _gitlab_repo(self):
        return {
            'name'                  : self.name,
            'path'                  : self.path,
            'namespace_id'          : self.namespace_id,
            'description'           : self.description,
            'issues_enabled'        : self.issues_enabled,
            'merge_requests_enabled': self.merge_requests_enabled,
            'builds_enabled'        : self.builds_enabled,
            'wiki_enabled'          : self.wiki_enabled,
            'snippets_enabled'      : self.snippets_enabled,
            'public'                : self.public,
            'visibility_level'      : self.visibility_level}

    def auth(self):
        self.gitlab_ctl.auth()

    def exists(self):
        if self.exist == None:
            self.exist = False
            for project in self.gitlab_ctl.projects.all():
                if project.name == self.name:
                    self.id    = project.id
                    #see issue 
                    #https://github.com/gpocentek/python-gitlab/issues/104
                    self.project  = self.gitlab_ctl.projects.get(project.id)
                    self.exist = True
                    return self.exist
        return self.exist
    
    def remove(self):
        rc  = 0
        out = ''
        err = ''
        try:
            gitlab_ctl.projects.delete(self.id)
        except gitlab.GitlabDeleteError as e:
            rc  = 1
            err = e.message
        return  (rc, out, err)

    def create(self):
        rc  = 0
        out = ''
        err = ''
        try:
            repo = self._gitlab_repo()
            self.gitlab_ctl.projects.create(repo)
        except gitlab.GitlabCreateError as e:
            rc  = 1
            err = e.message
        return (rc, out, err)

    def update(self):
        rc  = None
        out = ''
        err = ''
        if self.path and self.path != self.project.path:
            self.project.path = self.path
            rc = 0
        if self.description and self.description != self.project.description:
            self.project.description = self.description
            rc = 0
        if self.merge_requests_enabled and self.merge_requests_enabled != self.project.merge_requests_enabled:
            self.project.merge_requests_enabled = self.merge_requests_enabled
            rc = 0
        if self.builds_enabled and self.builds_enabled != self.project.builds_enabled:
            self.project.builds_enabled = self.builds_enabled
            rc = 0
        if self.wiki_enabled and self.wiki_enabled != self.project.wiki_enabled:
            self.project.wiki_enabled = self.wiki_enabled
            rc = 0
        if self.snippets_enabled and self.snippets_enabled != self.project.snippets_enabled:
            self.project.snippets_enabled = self.snippets_enabled
            rc = 0
        if self.public and self.public != self.project.public:
            self.project.public = self.public
            rc = 0
        if self.visibility_level and self.visibility_level != self.project.visibility_level:
            self.project.visibility_level = self.visibility_level
            rc = 0
        if rc != None:
            out = self.project.save()
        return (rc, out, err)



def main():
    module = AnsibleModule(
            argument_spec=dict(
                state=dict(default='present', choices=['present', 'absent'], type='str'),
                name=dict(required=True, type='str'),
                path=dict(default=None, type='str'),
                namespace_id=dict(default=None, type='int'),
                description=dict(default=None, type='str'),
                issues_enabled=dict(default='yes', type='bool'),
                merge_requests_enabled=dict(default='yes', type='bool'),
                builds_enabled=dict(default='no', type='bool'),
                wiki_enabled=dict(default='yes', type='bool'),
                snippets_enabled=dict(default='no', type='bool'),
                public=dict(default='no', type='bool'),
                visibility_level=dict(default=None, type='str'),
            ),
            supports_check_mode=True
        )
    gitlab_repo = GitlabRepo(module)

    rc = None
    out = ''
    err = ''
    result = {}
    result['name']  = gitlab_repo.name
    result['state'] = gitlab_repo.state
    if gitlab_repo.state == 'absent':
        if gitlab_repo.exists():
            if module.check_mode:
                module.exit_json(changed=True)
            (rc, out, err) = user.remove_repo()
            if rc != 0:
                module.fail_json(name=gitlab_repo.name, msg=err, rc=rc)
    elif gitlab_repo.state == 'present':
        if not gitlab_repo.exists():
            if module.check_mode:
                module.exit_json(changed=True)
            (rc, out, err) = gitlab_repo.create()
        else:
            (rc, out, err) = gitlab_repo.update()

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

