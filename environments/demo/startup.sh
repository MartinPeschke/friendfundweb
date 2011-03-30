#!/bin/bash

runpath=/opt/www/ff_test
binpath=/home/www-data/ff_test
config=./test_env.ini

export PYTHONPATH="$runpath:$binpath";
cd $runpath;
case "$1" in
  start)
    /server/pylons1.0/bin/paster serve --reload --daemon --pid-file=run/test.pid --log-file=./logs/test.log $config start
    ;;
  stop)
    /server/pylons1.0/bin/paster serve --reload --daemon --pid-file=run/test.pid --log-file=./logs/test.log  $config stop
    ;;
  restart)
    /server/pylons1.0/bin/paster serve --reload --daemon --pid-file=run/test.pid --log-file=./logs/test.log $config restart
    ;;
  *)
    echo $"Usage: $0 {start|stop|restart}"
    exit 1
esac
