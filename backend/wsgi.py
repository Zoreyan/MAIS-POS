import os
import sys
import platform
sys.path.insert(0, '/home/c/cl17008/deer/public_html')
sys.path.insert(0, '/home/c/cl17008/deer/public_html/backend')
sys.path.insert(0, '/home/c/cl17008/deer/venv/lib/python3.10/site-packages')
os.environ["DJANGO_SETTINGS_MODULE"] = "backend.settings"

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()