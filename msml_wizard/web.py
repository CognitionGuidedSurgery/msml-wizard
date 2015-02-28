# -*- encoding: utf-8 -*-

"""

"""

__author__ = 'Alexander Weigl <uiduw@student.kit.edu>'
__date__ = "2014-08-06"


from flask import *
from flask.ext.restful import Api, Resource
from flask_restful_swagger import swagger
from flask_bootstrap import Bootstrap
import msml_wizard.config as config
from msml_wizard.formmgmt import *
from flask_debugtoolbar import DebugToolbarExtension

from msml_wizard.filemgmt import FileManagement, XNATFile


app = Flask(__name__)
app.config.from_object(config)

dtoolbar = DebugToolbarExtension(app)
Bootstrap(app)
api = swagger.docs(Api(app), apiVersion="0.1")

repository = WizardRepository(config.FORMS_DIRECTORY)

@app.route("/", endpoint='list')
def wizard_catalog():
    return render_template("index.html", repository = repository, storage = Storage()._get_content())

@app.route("/w/<string:name>", endpoint='wizard')
def wizard_display(name):
    wz = repository[name]
    # template = app.jinja_env.from_string(wz.html_content)
    return render_template("wizard.html", html_content = wz.html_content,
                           wizard_name = name,
                           constraints = wz.constraints
    )

@app.route("/asset/<path:filename>")
@app.route("/assets/<path:filename>")
def asset(filename):
    assets_dir = path(__file__).parent.parent / "assets"
    return send_from_directory(assets_dir, filename, as_attachment = False )


# -- --------------------------------------------------------------------------
# Rest Api

class Generate(Resource):
    def post(self, name):
        wizard = repository[name]
        kwargs = dict(request.form)
        filename = wizard.generate(request.form)
        return send_file(filename, "text/xml", True)



class Storage(Resource):
    def _get_content(self):
        try:
            with open(config.FORM_STORAGE) as fp:
                data = json.load(fp)
        except:
            data = {}
        return data

    def post(self):
        data = self._get_content()
        wzname = request.form['__wizard_name__'];
        name = request.form['__name__'];

        if wzname not in data:
            data[wzname] = {}


        data[wzname][name] = dict(request.form.iteritems())

        with open(config.FORM_STORAGE, 'w') as fp:
            json.dump(data, fp)

    def get(self):
        template_name = request.args.get('template_name', False)
        data = self._get_content()

        if template_name:
            for values in data.values():
                if template_name in values:
                    return values[template_name]
        return data




api.add_resource(Generate, '/api/generate/<string:name>')
api.add_resource(FileManagement, '/api/file')
api.add_resource(Storage, '/api/templates')

api.add_resource(XNATFile, '/api/xnat')

class Wizard(Resource):
    def get(self):
        pass

# -- --------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug = True, port=8080, host = "0.0.0.0")