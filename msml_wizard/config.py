# -*- encoding: utf-8 -*-
__author__ = 'weigl'

import os
from path import path

FORMS_DIRECTORY = path(os.environ.get("MSML_WIZARD_FORMS", path(__file__).parent.parent / 'forms'))
SECRET_KEY = "sdfjksdafhönavnsdasdabggsdaöog"
FILES_DIR = path(os.environ.get("MSML_WIZARD_FILES", "/tmp/msml_wizard_files"))

UPLOAD_FOLDER = '/tmp/'

if not FORMS_DIRECTORY:
    FORMS_DIRECTORY.makedirs_p()

if not FILES_DIR.exists():
    FILES_DIR.makedirs_p()