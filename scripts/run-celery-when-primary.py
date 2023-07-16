# every second, check if the `/litefs/.primary` file exists. If it does not,
# then the current node is the primary and Celery should be started, if not
# already running. If the file does exist, a different node is the primary
# and Celery should be stopped if it is currently running.
import os
import time

celery_running = False
while True:
    if os.path.exists('/litefs/.primary'):
        if celery_running:
            print('Stopping Celery')
            os.system('pkill -f "celery worker"')
            celery_running = False
    else:
        if not celery_running:
            print('Starting Celery')
            os.system('celery -A splashcat worker -l INFO -B &')
            celery_running = True
    time.sleep(1)
