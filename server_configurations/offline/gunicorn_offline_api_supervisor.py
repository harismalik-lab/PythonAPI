import os
import multiprocessing

parent_directory = os.getcwd()
chdir = parent_directory
pythonpath = '{path}/envname'.format(path=parent_directory)
accesslog = '{path}/logs/api_entertainer-access.log'.format(path=parent_directory)
errorlog = '{path}/logs/api_entertainer-error.log'.format(path=parent_directory)
capture_output = True
raw_env = 'APPLICATION_SETTINGS={path}/instance/production_settings_offline.py'.format(path=parent_directory)

bind = 'unix:///tmp/python_offline_api.sock'.format(path=parent_directory)
timeout = 120
workers = multiprocessing.cpu_count() * 2 + 1
preload_app = True
proc_name = 'offline_api'

files_to_create = [accesslog, errorlog]
for log_file in files_to_create:
    open(log_file, "wb").close()

# usage: {path}/envname/gunicorn wsgi:app -c {envname}/server_configurations/offline/gunicorn_offline_api.py





