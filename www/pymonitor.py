import logging
import os
import subprocess
import sys
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

logging.basicConfig(level=logging.INFO)

'''
code Runner 这个插件运行的原理不清楚，但现在至少知道，
凡是要和用户交互的程序都不能用这个运行，只能在终端打开
'''

def log(s):
    print('[Monitor] %s' % s)


class MyFileSystemEventHander(FileSystemEventHandler):

    def __init__(self, fn):
        super(MyFileSystemEventHander, self).__init__()
        self.restart = fn

    def on_any_event(self, event):
        if event.src_path.endswith('.py'):
            log('Python source file changed: %s' % event.src_path)
            self.restart()

command = ['python', 'app.py']
process = None


def kill_process():
    global process
    if process:
        log('Kill process [%s]...' % process.pid)
        process.kill()
        process.wait()
        log('Process ended with code %s.' % process.returncode)
        process = None


def start_process():
    global process, command
    logging.info(str(command))
    log('Start process %s...' % ' '.join(command))
    process = subprocess.Popen(
        command, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)


def restart_process():
    kill_process()
    start_process()


def start_watch(path, callback):
    observer = Observer()
    observer.schedule(MyFileSystemEventHander(
        restart_process), path, recursive=True)
    observer.start()
    log('Watching directory %s...' % path)
    start_process()
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == '__main__':
    # argv = sys.argv[1:]
    # if not argv:
    #     print('in unix Usage: ./pymonitor your-script.py')
    #     exit(0)
    # if argv[0] != 'python3':
    #     argv.insert(0, 'python3')
    # command = argv
    path = os.path.dirname(os.path.realpath(__file__))
    logging.info(str(path))
    start_watch(path, None)
