export PYTHONPATH="/opt/www/friendfund";
cd /opt/www/friendfund;
case "$1" in
  start)
    /server/pylons1.0/bin/paster serve --reload --daemon --pid-file=run/friendfund.pid --log-file=./logs/webserver.log ./development.ini start
    ;;
  stop)
    /server/pylons1.0/bin/paster serve --reload --daemon --pid-file=run/friendfund.pid --log-file=./logs/webserver.log  ./development.ini stop
    ;;
  restart)
    /server/pylons1.0/bin/paster serve --reload --daemon --pid-file=run/friendfund.pid --log-file=./logs/webserver.log ./development.ini restart
    ;;
  *)
    echo $"Usage: $0 {start|stop|restart}"
    exit 1
esac
