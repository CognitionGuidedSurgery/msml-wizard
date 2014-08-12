__author__ = 'Alexander Weigl'

from flask import *
from path import path
from flask.ext.restful import *
import msml_wizard.config as c


def delete_file(subpath):
    p = c.FILES_DIR / subpath

    if p.exists():
        p.remove()
        return "ok"

    abort(501, "File does not exists")


class FileManagement(Resource):
    def get(self):
        def a():
            files = c.FILES_DIR.walkfiles()
            for f in files:
                yield f.relpath(c.FILES_DIR)
        return list(a())

    def put(self):
        """Upload a file via http upload
        :return:
        """

        try:
            file = request.files['file']
        except:
            print request.files
            print request.path
            print request.args
            print request.form

            abort(501, "No file given in request.")

        category = c.FILES_DIR / request.form.get('category', '')

        if not category.exists():
            category.makedirs_p()

        if file:
            place = category / file.filename
            file.save(place)

            return {
                'filename' : place.relpath(c.FILES_DIR)
            }
        else:
            abort(501, "File is missing")


    def post(self):
        """Get a file from an url
        :return:
        """
        url = request.form['url']
        name = request.form['name']
        import urllib

        urllib.urlretrieve(url, c.FILES_DIR / name)

        return "ok"

    def delete(self):
        """Delete a file
        """
        pth = request.form['name']
        return delete_file(pth)

from .xnatbinding import XNAT

class XNATFile(Resource):
    def get(self):
        tmpfile = path("/tmp/xnat.json")

        if not tmpfile.exists():

            xnat = XNAT(c.XNAT_URL, c.XNAT_USER, c.XNAT_PASSWORD)
            data =  xnat.get_data()


            with tmpfile.open('w') as fp:
                json.dump(data, fp)
        else:
            with tmpfile.open() as fp:
                data = json.load(fp)

        print request.headers

        if request.headers['content-type'] == 'text/html' or request.args.get('html', False):
            resp = make_response(render_template('xnat-tree.html', data = data))
            resp.headers['content-type'] = 'text/html'
            return resp

        return data
