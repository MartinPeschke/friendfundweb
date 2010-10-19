#!/bin/bash

runpath=/opt/www/friendfund
binpath=/home/www-data/ff_dev
config=./development.ini

export PYTHONPATH="$runpath:$binpath";
cd $runpath;
case "$1" in
  start)
    /server/pylons1.0/bin/paster serve --reload --daemon --pid-file=run/friendfund.pid --log-file=./logs/webserver.log $config start
    ;;
  stop)
    /server/pylons1.0/bin/paster serve --reload --daemon --pid-file=run/friendfund.pid --log-file=./logs/webserver.log  $config stop
    ;;
  restart)
    /server/pylons1.0/bin/paster serve --reload --daemon --pid-file=run/friendfund.pid --log-file=./logs/webserver.log $config restart
    ;;
  *)
    echo $"Usage: $0 {start|stop|restart}"
    exit 1
esac
