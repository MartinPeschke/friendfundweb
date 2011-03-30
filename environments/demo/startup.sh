#!/bin/bash

runpath=/opt/www/demo
binpath=/home/www-data/ff_demo
config=./demo.ini

export PYTHONPATH="$runpath:$binpath";
cd $runpath;
case "$1" in
  start)
    /server/pylons1.0/bin/paster serve --reload --daemon --pid-file=run/demo.pid --log-file=./logs/demo.log $config start
    ;;
  stop)
    /server/pylons1.0/bin/paster serve --reload --daemon --pid-file=run/demo.pid --log-file=./logs/demo.log  $config stop
    ;;
  restart)
    /server/pylons1.0/bin/paster serve --reload --daemon --pid-file=run/demo.pid --log-file=./logs/demo.log $config restart
    ;;
  *)
    echo $"Usage: $0 {start|stop|restart}"
    exit 1
esac
