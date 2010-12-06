#!/bin/bash

exec_name=gad
runpath=/opt/www/great_american_days
binpath=/home/www-data/partners_depl
config=./development.ini

export PYTHONPATH="$runpath:$binpath";
cd $runpath;
case "$1" in
  start)
    /server/pylons1.0/bin/paster serve --reload --daemon --pid-file=run/${exec_name}.pid --log-file=./logs/webserver_${exec_name}.log $config start
    ;;
  stop)
    /server/pylons1.0/bin/paster serve --reload --daemon --pid-file=run/${exec_name}.pid --log-file=./logs/webserver_${exec_name}.log  $config stop
    ;;
  restart)
    /server/pylons1.0/bin/paster serve --reload --daemon --pid-file=run/${exec_name}.pid --log-file=./logs/webserver_${exec_name}.log $config restart
    ;;
  *)
    echo $"Usage: $0 {start|stop|restart}"
    exit 1
esac
