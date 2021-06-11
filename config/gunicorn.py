import multiprocessing
import config

#unix = "/app/app.sock"
bind = "0.0.0.0:5000"
workers = config.GUNICORN_WORKERS
#workers = multiprocessing.cpu_count() - 1
#workers = int(os.getenv('WORKERS', multiprocessing.cpu_count() * 2 -1))
threads = config.GUNICORN_MAX_THREADS

# SSL
#certfile = "./config/certs/local.fullchain.pem"
#keyfile = "./config/certs/local.key"

accesslog = '-'
access_log_format = "%(h)s %(l)s %(u)s %(t)s '%(r)s' %(s)s %(b)s '%(f)s' '%(a)s' in %(D)sµs"

reload = config.GUNICORN_RELOAD