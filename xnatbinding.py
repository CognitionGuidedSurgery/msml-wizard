__author__ = 'Alexander Weigl <Alexander.Weigl@uiduw.student.kit.edu>'

from pprint import pprint

import requests


class HTTPError(BaseException):
    def __init__(self, response):
        super(HTTPError, self).__init__()
        self._response = response


def _handle(resp):
    print resp.url
    if resp.status_code == 200:
        if resp.headers['content-type'] == "application/json":
            return resp.json()
        else:
            return resp.content

    raise HTTPError(resp)


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
        url =self._host  + '/data/archive/projects/{ID}/resources'.format(ID=projectId)
        resp = self.session.get(url)
        return _handle(resp)

    def get_project_files(self, projectId):
        pass


    def get_project_subjects(self, projectId):
        resp = self.session.get(self._host + '/data/archive/projects/{ID}/subjects'.format(ID=projectId))
        return _handle(resp)

    def get_project_subjects_experiments(self,projectId, subjectId):
        url =self._host  + '/data/archive/projects/{ID}/subjects/{SID}/experiments'.format(ID=projectId, SID=subjectId)
        resp = self.session.get(self._host + '/data/archive/projects/{ID}/subjects'.format(ID=projectId))
        return _handle(resp)




xnat = XNAT("https://xnat.sfb125.de", "weigl", "DummyEntry")

#pprint(xnat.get_users())
#pprint(xnat.get_projects(owner=True))
#pprint(xnat.get_project_info("MSML_TEST"))
pprint(xnat.get_project_resources("MSML_TEST"))