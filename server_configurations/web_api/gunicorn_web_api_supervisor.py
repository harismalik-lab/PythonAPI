"""
isort:skip_file
"""
# import gevent.monkey  # noqa
# gevent.monkey.patch_all()  # noqa

import multiprocessing  # noqa
import os  # noqa

parent_directory = os.getcwd()
chdir = parent_directory
pythonpath = '{path}/envname'.format(path=parent_directory)
accesslog = '{path}/logs/api_entertainer-access.log'.format(path=parent_directory)
errorlog = '{path}/logs/api_entertainer-error.log'.format(path=parent_directory)
capture_output = True
raw_env = 'APPLICATION_SETTINGS={path}/instance/production_settings.py'.format(path=parent_directory)

bind = '0.0.0.0:8081'
timeout = 120
workers = multiprocessing.cpu_count() * 2 + 1
# preload_app = True
proc_name = 'web_api'
worker_class = 'gevent'

files_to_create = [accesslog, errorlog]
for log_file in files_to_create:
    open(log_file, "wb").close()
