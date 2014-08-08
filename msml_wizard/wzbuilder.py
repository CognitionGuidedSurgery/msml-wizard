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


from StringIO import StringIO
from collections import defaultdict

from lxml import etree
from jinja2 import Template, Environment, PackageLoader

from itertools import starmap


class WizardHtmlBuilder(object):
    def __init__(self, name):
        self._html = StringIO()
        self._js = StringIO()
        self.env = Environment(loader=PackageLoader(__name__))
        self._constraints = defaultdict(list)
        self._fields = []
        self.name = name

    @property
    def html(self):
        return self._html.getvalue()

    @property
    def javascript(self):
        return self._js.getvalue()

    def _add_constraint(self, node, *ids):
        cs = node.get('enabled') or node.get('constraint')
        if cs:
            for i in ids:
                self._constraints[i].append(cs)

    def _add_fields(self, *ids):
        self._fields += ids

    @property
    def constraints(self):
        cs = {}
        fields = { x : '"%s"' % x for x in self._fields}

        for k,v in self._constraints.iteritems():
            pred = ' && '.join(v)
            try:
                func = "function() {return %s;}" % pred.format(**fields)
            except KeyError as e:
                raise KeyError("you refered to an unknown field '%s'. Currently known is: %s" % (e.message, fields.keys()))
            cs[k] = func

        return cs


    def build_html_form(self, filename):
        with open(filename) as fh:
            parser = etree.XMLParser(remove_comments=True, remove_blank_text=True, remove_pis=True)
            root = etree.parse(fh, parser)
            root = root.getroot()
        return self.dispatch(root)

    def dispatch(self, e):
        return getattr(self, e.tag)(e)

    def wizard(self, e):
        self._html.write("<form role='form' action='/api/generate/%s' method='post'>" % self.name)
        self._html.write("<h1>%s</h1>" % e.get('title', ""))
        for c in e.iterchildren():
            self.dispatch(c)

        self._html.write('<input type="submit" class="btn-primary btn" value="Generate">')
        self._html.write("</form>")

    def textpage(self, e):
        title = e.get('title')
        subtitle = e.get('subtitle')

        i = generate_name()
        self._add_constraint(e, i);
        self.render_html("element_textpage.html",
                         id = i,
                         title=title,
                         content=e.text)

    def formpage(self, e):
        html = StringIO()
        title = e.get('title')
        i = generate_name()
        self._add_constraint(e, i)
        self._html.write('''<div class="panel panel-default">
                            <div class="panel-heading">
                                <h3 class="panel-title">%s</h3>
                            </div>
                            <div class="panel-body" id="%s">''' % (title, i))

        for sub in e.iterchildren():
            self.dispatch(sub)

        self._html.write("</div></div>")

    def slider(self, xml):
        default = {
            'step': 1,
            'min': 0,
            'max': 100,
            'value': 1,
        }

        self._add_constraint(xml, xml.get('id'))
        self._add_fields(xml.get('id'))
        default.update(xml.attrib)
        self.render_html("element_slider.html", **default)


    def render_html(self, template, *args, **kwargs):
        self._html.write(self.env.get_template(template).render(*args, **kwargs))

    def activate(self, e):
        self._add_constraint(e, e.get('id'))
        self._add_fields(e.get('id'))
        self.render_html("element_activate.html", **e.attrib)

    def spinbox(self, xml):
        m, M, s = xml.get('min', 0), xml.get('max', 100), xml.get('step', 1)
        suffix = xml.get('suffix', "")
        name = xml.get('id')
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
        self._add_fields(xml.get('id'))
        self._add_constraint(xml, xml.get('id'))
        self.render_html("element_file.html", **xml.attrib)

    def textfield(self, xml):
        self._add_fields(xml.get('id'))
        self._add_constraint(xml, xml.get('id'))
        self.render_html("element_textfield.html", **xml.attrib)

    def select(self, xml):
        self._add_fields(xml.get('id'))
        self._add_constraint(xml, xml.get('id'))
        values = parse_options(xml)
        self.render_html("element_select.html", options=values, **xml.attrib)

    def radio(self, xml):

        prefix = xml.get('id')
        ids = tuple(starmap(
            lambda k, v: prefix + "_" + k,
            parse_options(xml)
        ))
        self._add_constraint(xml, *ids)
        self._add_fields(*ids)
        self._add_fields(prefix)
        self.render_html("element_radio.html", options=parse_options(xml), **xml.attrib)

    def checkbox(self, xml):
        prefix = xml.get('id')
        ids = tuple(starmap(
            lambda k, v: prefix + "_" + k,
            parse_options(xml)
        ))

        self._add_fields(*ids)
        self._add_fields(prefix)

        self._add_constraint(xml, *ids)
        self.render_html("element_checkbox.html", options=parse_options(xml), **xml.attrib)


    def content(self, xml):
        i = generate_name()
        c = xml.get('class', "")
        self._add_constraint(xml, i)
        self._html.write("""
            <p id="%s" class="content-box %s">%s</p>
        """ % (i, c, xml.text))


def generate_name(prefix="id_"):
    if not hasattr(generate_name, 'counter'):
        generate_name.counter = 0
    generate_name.counter += 1
    return prefix + str(generate_name.counter)



def parse_options(root):
    options = []

    values = root.get('values')
    if values:
        values = values.split("|")
        for v in values:
            options.append((v, v))

    for child in root:
        label, value = child.get('label'), child.get('value')
        label = label or child.text or value
        options.append((label, value))

    return options
