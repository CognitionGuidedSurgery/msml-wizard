# !/usr/bin/python

# Copyright (C) 2013-2014 Alexander Weigl
#
# If you have any questions please feel free to contact us via
# http://github.com/CognitionGuidedSurgery/msml-wizard
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import os
from lxml import etree
from StringIO import StringIO
from jinja2 import Template, Environment, PackageLoader

class WizardHtmlBuilder(object):
    def __init__(self):
        self._html = StringIO()
        self._js = StringIO()
        self.env = Environment(loader=PackageLoader(__name__))

    @property
    def html(self):
        return self._html.getvalue()

    @property
    def javascript(self):
        return self._js.getvalue()

    def build_html_form(self, filename):
        with open(filename) as fh:
            root = etree.parse(fh)
            root = root.getroot()
        return self.dispatch(root)

    def dispatch(self, e):
        return getattr(self, e.tag)(e)

    def wizard(self, e):
        self._html.write("<form role='form'>")
        self._html.write("<h1>%s</h1>" % e.get('title', ""))
        for c in e.iterchildren():
            self.dispatch(c)
        self._html.write("</form>")

    def textpage(self, e):
        title = e.get('title')
        subtitle = e.get('subtitle')
        return """<div class='page'>
            <h1>%s</h1>
        %s</div>""" % (title, e.text)

    def formpage(self, e):
        html = StringIO()
        title = e.get('title')
        self._html.write("<h1>%s</h1>" % title)

        for sub in e.iterchildren():
            html.write(self.dispatch(sub))
        return '<div class="page form-page">%s</div>' % html.getvalue()

    def slider(self, xml):
        self._js.write(Template("""
           $(window).load(function() {
                $('#{{name}}').spinner({
                    min : {{min}}, max:{{max}}, step: {{step}}
                }).parent().addClass('form-control');
           });
        """).render(**xml.attrib))

        self.render_html("element_slider.html", **xml.attrib)


    def render_html(self, template, *args, **kwargs):
        self._html.write(self.env.get_template(template).render(*args, **kwargs))

    def spinbox(self, xml):
        m, M, s = xml.get('min', 0), xml.get('max', 100), xml.get('step', 1)
        suffix = xml.get('suffix', "")
        name = xml.get('name')
        label = xml.get('label')

        self._js.write(Template("""
           $(window).load(function() {
                $('#{{name}}').spinner({
                    min : {{min}}, max:{{max}}, step: {{step}}
                }).parent().addClass('form-control');
           });
        """).render(**xml.attrib))

        self.render_html("element_spinbox.html", **xml.attrib)

    def file(self, xml):
        self.render_html("element_file.html", **xml.attrib)

    def textfield(self, xml):
        self.render_html("element_textfield.html", **xml.attrib)

    def select(self, xml):
        values = parse_options(xml)
        self.render_html("element_select.html", options = values, **xml.attrib)

    def radio(self, xml):
        self.render_html("element_radio.html", options = parse_options(xml), **xml.attrib)

    def checkbox(self, xml):
        self.render_html("element_checkbox.html", options = parse_options(xml), **xml.attrib)


    def content(self, xml):
        self._html.write("""
            <div>%s</div>
        """ % xml.text)


def parse_options(root):
    options = []

    values = root.get('values')
    if values:
        values = values.split("|")
        for v in values:
            options.append((v, v))

    for child in root:
        label, value = child.get('label'), child.get('value')
        if not label:
            label = value
        options.append((label, value))

    return options
