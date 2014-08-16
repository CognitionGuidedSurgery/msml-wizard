__author__ = 'Alexander Weigl <Alexander.Weigl@uiduw.student.kit.edu>'

from pprint import pprint

import requests

from lxml import etree

class HTTPError(BaseException):
    def __init__(self, response):
        super(HTTPError, self).__init__()
        print response.content
        self._response = response


def _handle(resp):
    print resp.url
    if resp.status_code == 200:
        if resp.headers['content-type'] == "application/json":
            return resp.json()['ResultSet']['Result']
        elif resp.headers['content-type'] == "text/xml":
            xml = etree.fromstring(resp.content)
            if xml.tag == '{http://nrg.wustl.edu/catalog}Catalog':
                return handle_catalog(xml)
            else:
                return xml
        else:
            return resp.content

    raise HTTPError(resp)

def handle_catalog(root):
    result = []
    entries = root.find('{http://nrg.wustl.edu/catalog}entries')
    if entries:
        for entry in entries.iterchildren():
            result.append({'ID': entry.get('ID'), 'name': entry.get('name') })
    return result


class XNAT(object):
    def __init__(self, host, username, password):
        self._host = host
        self._username = username
        self._password = password

        self.session = requests.Session()
        self.session.auth = (self._username, self._password)
        self.session.headers.update({
            "content-type": "application/json"
        })

        # SSL Cert is non verifiable
        self.session.verify = False


    @property
    def auth(self):
        return self._username, self._password

    def get_users(self):
        resp = self.session.get(self._host + '/data/users')
        return _handle(resp)

    def get_projects(self,
                     accessible=None,
                     owner=None,
                     member=None,
                     collaborator=None,
                     recent=None,
                     favorite=None):
        query = {
            "accessible": accessible,
            "owner": owner,
            "member": member,
            "collaborator": collaborator,
            "recent": recent,
            "favorite": favorite, }

        resp = self.session.get(self._host + '/data/archive/projects',
                                params=query)
        return _handle(resp)

    def get_project_info(self, projectId):
        resp = self.session.get(self._host + '/data/archive/projects/%s' % projectId)
        return _handle(resp)


    def get_project_resources(self, projectId):
        url = self._host + '/data/archive/projects/{ID}/resources'.format(ID=projectId)
        resp = self.session.get(url)
        return _handle(resp)

    def get_project_files(self, projectId):
        pass


    def get_project_subjects(self, projectId):
        resp = self.session.get(self._host + '/data/archive/projects/{ID}/subjects'.format(ID=projectId))
        return _handle(resp)

    def get_project_subject_experiments(self, projectId, subjectId):
        url = self._host + '/data/archive/projects/{ID}/subjects/{SID}/experiments'.format(ID=projectId, SID=subjectId)
        resp = self.session.get(url)
        return _handle(resp)

    def get_project_subject_resources(self, projectId, subjectId):
        url = self._host + '/data/archive/projects/{p}/subjects/{s}/resources'.format(p=projectId, s=subjectId)
        resp = self.session.get(url)
        aids = map(lambda x: x['xnat_abstractresource_id'], _handle(resp))
        files = []
        for aid in aids:
            url = self._host + '/data/archive/projects/{p}/subjects/{s}/resources/{i}'\
                .format(p=projectId, s=subjectId, i = aid)
            resp = _handle(self.session.get(url))
            files+=resp
        return files


    def get_project_resource_files(self, projectId, resourceId):
        url = self._host + '/data/archive/projects/{p}/resources/{s}'.format(p=projectId, s=resourceId)
        resp = self.session.get(url)
        return _handle(resp)

    def get_data(self):
        projects = self.get_projects()
        data = []
        for p in projects:
            project = {'ID': p['ID'], 'name': p['name'], 'description': p['description']}


            project['_resources'] = []
            for r in self.get_project_resources(p['ID']):
                resource = {
                    'label': r['label'],
                    '_files': self.get_project_resource_files(p['ID'], r['label'])
                }


            subjects = self.get_project_subjects(p['ID'])
            project['_subjects'] = []
            for s in subjects:
                subject = {'ID': s['ID'], 'name' : s['ID']}
                res = self.get_project_subject_resources(p['ID'], s['ID'])
                subject['_resources'] = res


                #experiments = xnat.get_project_subject_experiments(p['ID'], s['ID'])
                #for e in experiments:
                #    pass

                project['_subjects'].append(subject)

            data.append(project)

        return data
