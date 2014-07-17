#!/usr/bin/python

# Copyright (C) 2013-2014 Alexander Weigl
#
# If you have any questions please feel free to contact us via
#   http://github.com/CognitionGuidedSurgery/msml-wizard
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


from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from docopt import docopt

from lxml import etree

DOC = """Usage:
msml-wizard.py <wizardxml> <tplfile>
"""

_page_register =  {}

def register_page(fn):
    _page_register[fn.__name__.lower()] = fn
    return fn

class XmlWizardPage(QWizardPage):
    def __init__(self, xmlelement, parent = None):
        super(XmlWizardPage, self).__init__(parent)
        self.setTitle(xmlelement.get('title'))
        self.setSubTitle(xmlelement.get('subtitle'))

        self.variables = {}

    def get_variables(self):
        return {k: v() for k,v in self.variables.items()}


    def validatePage(self):
        """:rtype: bool
        """
        return True

@register_page
class HTMLPage(XmlWizardPage):
    def __init__(self, xmlelement, parent = None):
        super(HTMLPage, self).__init__(xmlelement, parent)

        self.webView = QWebView()

        if 'url' in xmlelement:
            self.webView.openUrl(xmlelement['url'])
        else:
            self.webView.setHtml(xmlelement.text)
        layout = QVBoxLayout()
        layout.addWidget(self.webView)
        self.setLayout(layout)

@register_page
class TextPage(XmlWizardPage):
    def __init__(self, xmlelement, parent = None):
        super(TextPage, self).__init__(xmlelement, parent)
        self.label = QLabel(xmlelement.text,self)
        print "TextPage",  xmlelement.text
        self.label.setWordWrap(True)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)


@register_page
class FormPage(XmlWizardPage):
    def __init__(self, xmlelement, parent = None):
        super(FormPage, self).__init__(xmlelement, parent)
        self.setTitle(xmlelement.get('title'))

        bldr = ElementBuilder(self)

        self.page_guard = xmlelement.get('enabled')

        for r, child in enumerate(xmlelement):
            bldr(child)

        self.setLayout(bldr.layout)
        self.variables = bldr.variables
        self.guards = bldr.guards

        for name, widget in bldr.fields.items():
            self.registerField(name, widget)

    def initializePage(self):
        self.evaluate_guards()

    def evaluate_guards(self):
        self.setEnabled(True)
        if self.page_guard and not eval(self.page_guard):
            self.setEnabled(False)
            return

        for guard, widgets in self.guards:
            if guard and eval(guard):
                e = True
            else:
                e = False

            print e, widgets
            for w in widgets:
                w.setEnabled(e)



class ElementBuilder(object):
    def __init__(self, page):
        self.page = page
        self.layout = QGridLayout()
        self.row = 0
        self.variables = {}
        self.fields = {}
        self.guards = []

    def __call__(self, xml):
        #dispatch
        try:
            name = xml.tag.lower()
        except:
            return

        fn = getattr(self, "_%s" % name)
        result = fn(xml)
        self.variables[xml.get('name')] = result
        self.row += 1
        return result

    def _add_change_signal(self, slot):
        slot.connect(self.page.evaluate_guards)

    def _add_row(self, *widgets):
        for i,w in enumerate(widgets):
            if isinstance(w, QWidget):
                self.layout.addWidget(w, self.row, i)
            else:
                self.layout.addItem(w, self.row, i)
        return widgets


    def _build_label(self, xml, buddy = None):
        label = QLabel(xml.get('label'))
        label.setWordWrap(True)
        label.setBuddy(buddy)
        return label

    def register_field(self, name, widget):
        self.fields[name] = widget

    def register_guard(self, guard, *widgets):
        if guard:
            self.guards.append((guard, widgets))

    def _slider(self, xml):
        slider = QSlider(Qt.Horizontal)

        m,M,s = xml.get('min'),xml.get('max'),xml.get('step')

        slider.setMinimum(int(m))
        slider.setMaximum(int(M))
        slider.setTickInterval(int(s))

        self._add_row(
            self._build_label(xml, slider),
            slider
        )

        self.register_field(xml.get('name'), slider)
        self.register_guard(xml.get('enabled'), slider)
        self._add_change_signal(slider.valueChanged)

        return slider.value

    def _spinbox(self, xml):
        slider = QSpinBox()

        self.register_field(xml.get('name'), slider)
        self.register_guard(xml.get('enabled'), slider)
        self._add_change_signal(slider.valueChanged)

        m,M,s = xml.get('min',0),xml.get('max',100),xml.get('step',1)
        suffix = xml.get('suffix')

        slider.setRange(int(m), int(M))

        if suffix:
            slider.setSuffix(suffix)

        self._add_row(
            self._build_label(xml, slider),
            slider
        )

        return slider.value


    def _file(self, xml):
        textfield = QLineEdit("")
        button = QPushButton('...')

        def browse():
            val = textfield.text()

            if not val:
                val = xml.get('value')

            if os.path.isfile(val):
                val = os.path.dirname(val)

            filt    = xml.get('pattern', 0)
            caption = xml.get('caption', "Choose file...")
            options = 0

            fn = QFileDialog.getOpenFileName

            if xml.get('save'):
                fn =  QFileDialog.getSaveFileName
            elif xml.get('multiple'):
                fn =  QFileDialog.getOpenFileNames

            val = fn(textfield, caption, val, filt)

            if isinstance(val, QStringList):
                val = '|'.join((str(x) for x in val))

            textfield.setText(val)

        def get():
            txt = textfield.text().split('|')

            if len(txt) == 1:
                return txt[0]
            return txt

        button.pressed.connect(browse)
        self._add_row(self._build_label(xml, textfield), textfield, button)
        return get

    def _textfield(self, xml):
        textField = QLineEdit(xml.get('value', ""))
        label = self._build_label(xml, textField)

        self.register_field(xml.get('name'), textField)
        self.register_guard(xml.get('enabled'), label, textField)
        self._add_change_signal(textField.textChanged)

        self._add_row(label, textField)
        return lambda: str(textField.text())

    def _select(self, xml):
        combo = QComboBox()
        label = self._build_label(xml, combo)

        values = parse_options(xml)
        for labl, value in values:
            combo.addItem(labl, value)


        self.register_field(xml.get('name'), combo)
        self.register_guard(xml.get('enabled'), label, combo)
        self._add_change_signal(combo.currentIndexChanged)
        self._add_row(label, combo)

        return lambda: str(combo.itemData(combo.currentIndex()).toPyObject())

    def _radio(self, xml):
        buttons,b =  self._build_togglebuttons(xml, QRadioButton, lambda x: x.isChecked())
        group = QButtonGroup()
        for radio in buttons:
            group.addButton(radio)
        return b

    def _checkbox(self, xml):
        checked = lambda cb: cb.checkState() == Qt.Checked
        a, b =  self._build_togglebuttons(xml, QCheckBox, checked)
        return b

    def _build_togglebuttons(self, xml, btn_factory, checked):
        values = parse_options(xml)
        widget = QHBoxLayout() if len(values) <= 3  else QVBoxLayout()

        checkboxes = {}
        prefix = xml.get('name') +"_%s"

        for label, value in values:
            cb = btn_factory(label)
            widget.addWidget(cb)
            checkboxes[cb] = value
            self.register_field(prefix % value,  cb)
            self._add_change_signal(cb.clicked)

        label  = self._build_label(xml)

        self.register_guard(xml.get('enabled'), *checkboxes.keys())
        self.register_guard(xml.get('enabled'), label)

        def get():
            s = set()
            for cb in checkboxes:
                if checked(cb):
                    s.add(checkboxes[cb])
            return s

        self._add_row(label, widget)
        return checkboxes.keys(), get

    def _content(self, xml):
        label = QLabel(xml.text)
        label.setWordWrap(True)
        self.layout.addWidget(label, self.row, 0, 1, 2, Qt.AlignLeft | Qt.AlignTop)
        self.row+=1
        return label

def parse_options(root):
    options = []

    values = root.get('values')
    if values:
        values = values.split("|")
        for v in values:
            options.append((v,v))

    for child in root:
        label, value = child.get('label'), child.get('value')
        if not label:
            label = value
        options.append((label, value))

    return options

def build_page(element):
    if element.tag in  _page_register:
        builder = _page_register[element.tag]
        return builder(element)
    else:
        print "No builder for tag %s found" % element.tag


import sys
from jinja2 import Template
from path import path
import os


def process_variables(pages, tplfile):
    def finish():
        variables = {}
        for p in pages:
            variables.update(p.get_variables())

        with open(tplfile) as fh:
            tpl = Template(fh.read())
            content = tpl.render(**variables)
            print content

    return finish


def main():
    args = docopt(DOC)
    #print args

    inputfile = path(args['<wizardxml>']).abspath()
    templatefile = path(args['<tplfile>']).abspath()

    with inputfile.open() as fh:
        root = etree.parse(fh)
        root = root.getroot()

    os.chdir(inputfile.dirname())

    app = QApplication(sys.argv)
    pages = [ build_page(child) for child in root ]

    wizard = QWizard()
    wizard.accepted.connect(process_variables(pages, templatefile))


    watermark = root.get('watermark')
    banner =  root.get('banner')
    logo =  root.get('logo')

    for t,v in zip((QWizard.WatermarkPixmap, QWizard.BannerPixmap, QWizard.LogoPixmap),
                 (watermark, banner, logo)):
        if v:
            wizard.setPixmap(t, QPixmap(v))

    #wizard.setWizardStyle(QWizard.AeroStyle)
    #wizard.setWizardStyle(QWizard.MacStyle)

    for p in pages:
        wizard.addPage(p)

    wizard.show()

    return app.exec_()


if "__main__" == __name__: main()
