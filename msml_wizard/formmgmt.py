__author__ = 'weigl'

import json

from path import path
import BeautifulSoup
import msml_wizard.wzbuilder


class WizardRepository(object):
    def __init__(self, location):
        self.location = path(location)
        self._cache = {}

        print self.location

        assert self.location.isdir()

    def __getitem__(self, item):
        #if item in self._cache:#disable cache
        #    return self._cache[item]

        loc = self.location / item
        print "Look in %s" % loc
        if loc.isdir():
            self._cache[item] = Wizard(loc)
            return self._cache[item]

        raise KeyError("Could not find Wizard with %s" % item)

    def __iter__(self):
        for dir in self.location.listdir():
            yield self[dir] # looking for cache

def read(filename):
    with open(filename) as fp:
        return fp.read()


class Wizard(object):
    def __init__(self, loc):
        self.location = loc
        print loc/"meta.json"
        self.meta = json.loads(read(loc / 'meta.json'))

        self.name = self.meta['name']
        self.version = self.meta['version']
        self.key = str(self.location.basename())

        self.template_filename = loc / self.meta['template']
        #self.html_filename = loc / self.meta['html']
        self.wizard_filename = loc / self.meta['wizard']

        self.css_filename = loc / self.meta['css']

        self.template_content = read(self.template_filename)
        #self.html_content = read(self.html_filename)
        self.css_content = read(self.css_filename)

    @property
    def html_content(self):
        bldr = msml_wizard.wzbuilder.WizardHtmlBuilder()
        bldr.build_html_form(self.wizard_filename)
        return bldr.html

    def _parse_form_meta(self):
        html = BeautifulSoup.BeautifulSoup(self.html_content, isHTML=True)
        self._fields = html.findAll("input")
