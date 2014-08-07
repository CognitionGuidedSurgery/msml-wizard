# -*- encoding: utf-8 -*-
__author__ = 'weigl'

import os
from path import path

FORMS_DIRECTORY = os.environ.get("MSML_WIZARD_FORMS", path(__file__).parent.parent / 'forms')
SECRET_KEY = "sdfjksdafhönavnsdasdabggsdaöog"