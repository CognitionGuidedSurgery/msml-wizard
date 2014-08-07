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


app = Flask(__name__)
app.config.from_object(config)

dtoolbar = DebugToolbarExtension(app)
Bootstrap(app)
api = swagger.docs(Api(app), apiVersion="0.1")


repository = WizardRepository(config.FORMS_DIRECTORY)

@app.route("/", endpoint='list')
def wizard_catalog():
    return render_template("index.html", repository = repository)

@app.route("/<string:name>", endpoint='wizard')
def wizard_display(name):
    wz = repository[name]
    # template = app.jinja_env.from_string(wz.html_content)
    return render_template("wizard.html", html_content = wz.html_content)


@app.route("/asset/<path:filename>")
def asset(filename):
    assets_dir = path(__file__).parent.parent / "assets"
    return send_from_directory(assets_dir, filename, as_attachment = False )

# -- --------------------------------------------------------------------------
# Rest Api


class Wizard(Resource):
    def get(self):
        pass

# -- --------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug = True, port=8080, host = "0.0.0.0")