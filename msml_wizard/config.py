# -*- encoding: utf-8 -*-
__author__ = 'weigl'

import os
from path import path

XNAT_URL = "https://xnat.sfb125.de"
XNAT_USER = os.environ.get('MSML_WIZARD_XNAT_USER')
XNAT_PASSWORD = os.environ.get('MSML_WIZARD_XNAT_PASSWORD')


FORM_STORAGE = path(os.environ.get('MSML_WIZARD_STORAGE', "/tmp/msml_wizard_storage.json"))

FORMS_DIRECTORY = path(os.environ.get("MSML_WIZARD_FORMS", path(__file__).parent.parent / 'forms'))
SECRET_KEY = os.environ.get('MSML_WIZARD_SECRET', "sdfjksdafhönavnsdasdabggsdaöog")
FILES_DIR = path(os.environ.get("MSML_WIZARD_FILES", "/tmp/msml_wizard_files"))

UPLOAD_FOLDER = '/tmp/'



if not FORMS_DIRECTORY:
    FORMS_DIRECTORY.makedirs_p()

if not FILES_DIR.exists():
    FILES_DIR.makedirs_p()

#if not FORM_STORAGE.exists():
#    FORM_STORAGE.makedirs_p()