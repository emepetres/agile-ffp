#!/bin/bash
set -e

pushd "$(dirname "$0")"

LOG_DIR="./logs"
mkdir -p "$LOG_DIR"

gunicorn -w 2 -k uvicorn.workers.UvicornWorker agileffp.app:app --bind 0.0.0.0:8000 \
    --log-file="$LOG_DIR/gunicorn.log" \
    --log-config= <<EOF
[loggers]
keys=root, gunicorn.error, gunicorn.access

[handlers]
keys=console, error_file, access_file

[formatters]
keys=generic, access

[logger_root]
level=INFO
handlers=console

[logger_gunicorn.error]
level=INFO
handlers=error_file
propagate=0
qualname=gunicorn.error

[logger_gunicorn.access]
level=INFO
handlers=access_file
propagate=0
qualname=gunicorn.access

[handler_console]
class=StreamHandler
formatter=generic
args=(sys.stdout, )

[handler_error_file]
class=logging.handlers.RotatingFileHandler
formatter=generic
args=('$LOG_DIR/gunicorn.error.log', 'a', 1000000, 3)

[handler_access_file]
class=logging.handlers.RotatingFileHandler
formatter=access
args=('$LOG_DIR/gunicorn.access.log', 'a', 1000000, 3)

[formatter_generic]
format=%(asctime)s [%(process)d] [%(levelname)s] %(message)s
datefmt=%Y-%m-%d %H:%M:%S
class=logging.Formatter

[formatter_access]
format=%(asctime)s [%(process)d] [%(levelname)s] %(message)s
datefmt=%Y-%m-%d %H:%M:%S
class=logging.Formatter
EOF

popd
