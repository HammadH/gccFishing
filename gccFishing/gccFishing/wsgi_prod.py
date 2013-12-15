import sys

sys.path.insert(0, '/home/hammad/webapps/gccfishing/gccFishing/gccFishing')

from gccFishing import settings_prod

import django.core.management
django.core.management.setup_environ(settings_prod)
utility = django.core.management.ManagementUtility()
command = utility.fetch_command('runserver')

command.validate()

import django.conf
import django.utils

django.utils.translation.activate(django.conf.settings.LANGUAGE_CODE)

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()