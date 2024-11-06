import os
import multiprocessing

parent_directory = os.getcwd()
chdir = parent_directory
pythonpath = '{path}/envname'.format(path=parent_directory)
pidfile = '{path}/python_analytics_api.pid'.format(path=parent_directory)
accesslog = '/var/log/python_analytics_api.log'
errorlog = '/var/log/python_analytics_api.log'
capture_output = True
daemon = True
raw_env = 'APPLICATION_SETTINGS={path}/instance/analytics_staging_settings.py'.format(path=parent_directory)

bind = 'unix:///var/tmp/python_analytics_api.sock'.format(path=parent_directory)
timeout = 120
workers = multiprocessing.cpu_count() * 2 + 1
preload_app = True
proc_name = 'analytics_api'

files_to_create = [accesslog, errorlog]
for log_file in files_to_create:
    open(log_file, "wb").close()





