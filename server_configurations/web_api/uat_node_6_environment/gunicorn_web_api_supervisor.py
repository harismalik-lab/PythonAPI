"""
isort:skip_file
"""
import gevent.monkey  # noqa
gevent.monkey.patch_all()  # noqa

import multiprocessing  # noqa
import os  # noqa

parent_directory = os.getcwd()
chdir = parent_directory
pythonpath = '{path}/envname'.format(path=parent_directory)
accesslog = '{path}/logs/api_entertainer-access.log'.format(path=parent_directory)
errorlog = '{path}/logs/api_entertainer-error.log'.format(path=parent_directory)
capture_output = True
raw_env = 'APPLICATION_SETTINGS={path}/instance/uat_settings.py'.format(path=parent_directory)

bind = '127.0.0.1:8086'
timeout = 120
workers = multiprocessing.cpu_count() * 2 + 1
# Disabling preload_app to log APM transactions with Gunicorn since it does not create live socket connections of APM
# for the workers if the app is pre-loaded i.e. before the workers are forked.
# preload_app = True
proc_name = 'web_api'
worker_class = 'gevent'

files_to_create = [accesslog, errorlog]
for log_file in files_to_create:
    open(log_file, "wb").close()
