import os
import multiprocessing

parent_directory = os.getcwd()
chdir = parent_directory
pythonpath = '{path}/envname'.format(path=parent_directory)
pidfile = '{path}/python_offline_api.pid'.format(path=parent_directory)
accesslog = '{path}/logs/python_offline_api.log'.format(path=parent_directory)
errorlog = '{path}/logs/python_offline_api.log'.format(path=parent_directory)
capture_output = True
daemon = True
raw_env = 'APPLICATION_SETTINGS={path}/instance/offline_staging_settings.py'.format(path=parent_directory)

bind = 'unix:///var/tmp/python_offline_api.sock'.format(path=parent_directory)
timeout = 120
workers = multiprocessing.cpu_count() * 2 + 1
preload_app = True
proc_name = 'offline_api'

files_to_create = [accesslog, errorlog]
for log_file in files_to_create:
    open(log_file, "wb").close()

# usage: {path}/envname/gunicorn wsgi:app -c {envname}/server_configurations/offline/gunicorn_offline_api.py





