import os
import multiprocessing

# Gunicorn configuration file.

#
# Server socket
#
#   bind - The socket to bind.
#
#       A string of the form: 'HOST', 'HOST:PORT', 'unix:PATH'.
#       An IP is a valid HOST.
#
#   backlog - The number of pending connections. This refers
#       to the number of clients that can be waiting to be
#       served. Exceeding this number results in the client
#       getting an error when attempting to connect. It should
#       only affect servers under significant load.
#
#       Must be a positive integer. Generally set in the 64-2048
#       range.
#

bind = '0.0.0.0:1027'
backlog = os.environ['GUNICORN_BACKLOG'] if 'GUNICORN_BACKLOG' in os.environ else 2048

#
# Worker processes
#
#   workers - The number of worker processes that this server
#       should keep alive for handling requests.
#
#       A positive integer generally in the 2-4 x $(NUM_CORES)
#       range. You'll want to vary this a bit to find the best
#       for your particular application's work load.
#
#   worker_class - The type of workers to use. The default
#       sync class should handle most 'normal' types of work
#       loads. You'll want to read
#       http://docs.gunicorn.org/en/latest/design.html#choosing-a-worker-type
#       for information on when you might want to choose one
#       of the other worker classes.
#
#       A string referring to a Python path to a subclass of
#       gunicorn.workers.base.Worker. The default provided values
#       can be seen at
#       http://docs.gunicorn.org/en/latest/settings.html#worker-class
#
#   threads - The number of worker threads for handling requests.
#
#       Run each worker with the specified number of threads.
#       A positive integer generally in the 2-4 x $(NUM_CORES) range.
#       You’ll want to vary this a bit to find the best for your particular application’s work load.
#       If it is not defined, the default is 1.
#       This setting only affects the Gthread worker type.
#
#   worker_connections - For the eventlet and gevent worker classes
#       this limits the maximum number of simultaneous clients that
#       a single process can handle.
#
#       A positive integer generally set to around 1000.
#
#   timeout - If a worker does not notify the master process in this
#       number of seconds it is killed and a new worker is spawned
#       to replace it.
#
#       Generally set to thirty seconds. Only set this noticeably
#       higher if you're sure of the repercussions for sync workers.
#       For the non sync workers it just means that the worker
#       process is still communicating and is not tied to the length
#       of time required to handle a single request.
#
#   max_requests - The maximum number of requests a worker will process before restarting.
#
#       Any value greater than zero will limit the number of requests a work will process before
#       automatically restarting. This is a simple method to help limit the damage of memory leaks.
#       If this is set to zero (the default) then the automatic worker restarts are disabled.

workers = os.environ[
    'GUNICORN_N_WORKERS'] if 'GUNICORN_N_WORKERS' in os.environ else multiprocessing.cpu_count() * 2 + 1
worker_class = os.environ['GUNICORN_WORKER_CLASS'] if 'GUNICORN_WORKER_CLASS' in os.environ else 'sync'
threads = os.environ['GUNICORN_THREADS'] if 'GUNICORN_THREADS' in os.environ else 1
worker_connections = os.environ['GUNICORN_WORKER_CONNECTIONS'] if 'GUNICORN_WORKER_CONNECTIONS' in os.environ else 1000
timeout = os.environ['GUNICORN_WORKER_TIMEOUT'] if 'GUNICORN_WORKER_TIMEOUT' in os.environ else 90
max_requests = os.environ['GUNICORN_MAX_REQUESTS'] if 'GUNICORN_MAX_REQUESTS' in os.environ else 0

#
#   Logging
#
#   accesslog - The path to a log file to write to.
#
#       A path string. "-" means log to stdout.
#
#   errorlog - The path to a log file to write to.
#
#       A path string. "-" means log to stderr.
#
#   loglevel - The granularity of log output
#
#       A string of "debug", "info", "warning", "error", "critical"
#

errorlog = '-'
accesslog = '-'
loglevel = 'debug'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

#
# Process naming
#
#   proc_name - A base to use with setproctitle to change the way
#       that Gunicorn processes are reported in the system process
#       table. This affects things like 'ps' and 'top'. If you're
#       going to be running more than one instance of Gunicorn you'll
#       probably want to set a name to tell them apart. This requires
#       that you install the setproctitle module.
#
#       A string or None to choose a default of something like 'gunicorn'.
#

proc_name = 'nima'


# Server hooks
#
#   on_starting - Called just before the master process is initialized.
#
#       The callable needs to accept a single instance variable for the Arbiter.
#
#   when_ready - Called just after the server is started.
#
#       The callable needs to accept a single instance variable for the Arbiter.
#
#   post_fork - Called just after a worker has been forked.
#
#       A callable that takes a server and worker instance
#       as arguments.
#
#   pre_fork - Called just prior to forking the worker subprocess.
#
#       A callable that accepts the same arguments as after_fork
#
#   pre_exec - Called just prior to forking off a secondary
#       master process during things like config reloading.
#
#       A callable that takes a server instance as the sole argument.
#
#   worker_int - Called just after a worker exited on SIGINT or SIGQUIT.
#
#       The callable needs to accept one instance variable for the initialized Worker.
#
#   worker_abort - Called when a worker received the SIGABRT signal.
#
#       This call generally happens on timeout.
#
#       The callable needs to accept one instance variable for the initialized Worker.
#
#   worker_exit - Called just after a worker has been exited, in the worker process.
#
#       The callable needs to accept two instance variables for the Arbiter and the just-exited Worker.
#
#   pre_request - Called just before a worker processes the request.
#
#       The callable needs to accept two instance variables for the Worker and the Request.

def on_starting(server):
    server.log.info("Server is starting.")


def when_ready(server):
    server.log.info("Server is ready. Spawning workers")


def pre_fork(server, worker):
    server.log.info("Worker will be spawned (pid: %s)", worker.pid)


def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)


def worker_int(worker):
    worker.log.info("worker received INT or QUIT signal")


def worker_abort(worker):
    worker.log.info("worker received SIGABRT signal")


def worker_exit(server, worker):
    worker.log.info("worker exitted")


def pre_request(worker, req):
    worker.log.debug("%s %s" % (req.method, req.path))
