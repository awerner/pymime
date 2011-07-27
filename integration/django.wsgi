import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
os.environ['DJANGO_SETTINGS_MODULE'] = 'django_attachmentstore.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

