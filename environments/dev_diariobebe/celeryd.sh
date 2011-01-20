#!/bin/sh -e
# ============================================
# celeryd - Starts the Celery worker daemon.
# ============================================
#
# :Usage: /etc/init.d/celeryd {start|stop|force-reload|restart|try-restart|status}
#
# :Configuration file: /etc/default/celeryd
#
# To configure celeryd you probably need to tell it where to chdir.
#
# EXAMPLE CONFIGURATION
# =====================
#
# this is an example configuration for a Python project:
#
# /etc/default/celeryd:
#
# # Where to chdir at start.
# CELERYD_CHDIR="/opt/Myproject/"
#
# # Extra arguments to celeryd
# CELERYD_OPTS="--time-limit 300"
#
# # Name of the celery config module.#
# CELERY_CONFIG_MODULE="celeryconfig"
#
# EXAMPLE DJANGO CONFIGURATION
# ============================
#
# # Where the Django project is.
# CELERYD_CHDIR="/opt/Project/"
#
# # Name of the projects settings module.
# DJANGO_SETTINGS_MODULE="settings"
#
# # Path to celeryd
# CELERYD="/opt/Project/manage.py celeryd"
#
# AVAILABLE OPTIONS
# =================
#
# * CELERYD_OPTS
# Additional arguments to celeryd, see ``celeryd --help`` for a list.
#
# * CELERYD_CHDIR
# Path to chdir at start. Default is to stay in the current directory.
#
# * CELERYD_PID_FILE
# Full path to the pidfile. Default is /var/run/celeryd.pid.
#
# * CELERYD_LOG_FILE
# Full path to the celeryd logfile. Default is /var/log/celeryd.log
#
# * CELERYD_LOG_LEVEL
# Log level to use for celeryd. Default is INFO.
#
# * CELERYD
# Path to the celeryd program. Default is ``celeryd``.
# You can point this to an virtualenv, or even use manage.py for django.
#
# * CELERYD_USER
# User to run celeryd as. Default is current user.
#
# * CELERYD_GROUP
# Group to run celeryd as. Default is current user.


### BEGIN INIT INFO
# Provides: celeryd
# Required-Start: $network $local_fs $remote_fs
# Required-Stop: $network $local_fs $remote_fs
# Default-Start: 2 3 4 5
# Default-Stop: 0 1 6
# Short-Description: celery task worker daemon
### END INIT INFO

set -e

runpath="diariobebe"
binpath="ff_dev"

export PYTHONPATH="/opt/www/$runpath:/home/www-data/$binpath"
DEFAULT_CELERYD="/server/pylons1.0/bin/celeryd"
CELERYD="/server/pylons1.0/bin/celeryd"
CELERYD_LOG_FILE="/opt/www/$runpath/logs/celeryd_dev_gad.log"
CELERYD_PID_FILE="/opt/www/$runpath/run/celeryd_dev_gad.pid"
CELERYD_CHDIR="/opt/www/$runpath"
CELERYD_USER="www-data"
CELERYD_GROUP="www-data"

# /etc/init.d/ssh: start and stop the celery task worker daemon.

if test -f /etc/default/celeryd; then
    . /etc/default/celeryd
fi

CELERYD_LOG_FILE=${CELERYD_LOG_FILE:-${CELERYD_LOGFILE:-"/var/log/celeryd.log"}}
CELERYD_PID_FILE=${CELERYD_PID_FILE:-${CELERYD_PIDFILE:-"/var/run/celeryd.pid"}}
CELERYD_LOG_LEVEL=${CELERYD_LOG_LEVEL:-${CELERYD_LOGLEVEL:-"INFO"}}

CELERYD=${CELERYD:-$DEFAULT_CELERYD}

export CELERY_LOADER

. /lib/lsb/init-functions

CELERYD_OPTS="$CELERYD_OPTS -f $CELERYD_LOG_FILE -l $CELERYD_LOG_LEVEL"

if [ -n "$2" ]; then
CELERYD_OPTS="$CELERYD_OPTS $2"
fi

# Extra /sbin/start-stop-daemon options, like user/group.
if [ -n "$CELERYD_USER" ]; then
DAEMON_OPTS="$DAEMON_OPTS --chuid $CELERYD_USER"
fi
if [ -n "$CELERYD_GROUP" ]; then
DAEMON_OPTS="$DAEMON_OPTS --group $CELERYD_GROUP"
fi

if [ -n "$CELERYD_CHDIR" ]; then
DAEMON_OPTS="$DAEMON_OPTS --chdir $CELERYD_CHDIR"
fi


# Are we running from init?
run_by_init() {
    ([ "$previous" ] && [ "$runlevel" ]) || [ "$runlevel" = S ]
}


check_dev_null() {
    if [ ! -c /dev/null ]; then
if [ "$1" = log_end_msg ]; then
log_end_msg 1 || true
fi
if ! run_by_init; then
log_action_msg "/dev/null is not a character device!"
    fi
exit 1
    fi
}


export PATH="${PATH:+$PATH:}/usr/sbin:/sbin"


stop_worker () {
    cmd="/sbin/start-stop-daemon --stop \
--quiet \
$* \
--pidfile $CELERYD_PID_FILE"
    if $cmd; then
log_end_msg 0
    else
log_end_msg 1
    fi
}

start_worker () {
    cmd="/sbin/start-stop-daemon --start $DAEMON_OPTS \
--quiet \
--oknodo \
--background \
--make-pidfile \
$* \
--pidfile $CELERYD_PID_FILE
--exec $CELERYD -- $CELERYD_OPTS"
    if $cmd; then
log_end_msg 0
    else
log_end_msg 1
    fi
}



case "$1" in
  start)
    check_dev_null
    log_daemon_msg "Starting celery task worker server"
    start_worker
    ;;
  stop)
    log_daemon_msg "Stopping celery task worker server"
    stop_worker --oknodo
    ;;

  reload|force-reload)
    echo "Use start+stop"
    ;;

  restart)
    log_daemon_msg "Restarting celery task worker server"
    stop_worker --oknodo --retry 30
    check_dev_null log_end_msg
    start_worker
    ;;

  try-restart)
    log_daemon_msg "Restarting celery task worker server"
    set +e
    stop_worker --retry 30
    RET="$?"
    set -e
    case $RET in
        0)
        # old daemon stopped
        check_dev_null log_end_msg
        start_worker
        ;;
        1)
        # daemon not running
        log_progress_msg "(not running)"
        log_end_msg 0
        ;;
        *)
        # failed to stop
        log_progress_msg "(failed to stop)"
        log_end_msg 1
        ;;
    esac
    ;;

  status)
    status_of_proc -p $CELERYD_PID_FILE $CELERYD celeryd && exit 0 || exit $?
    ;;

  *)
    log_action_msg "Usage: $CELERYD {start|stop|force-reload|restart|try-restart|status}"
    exit 1
esac

exit 0
