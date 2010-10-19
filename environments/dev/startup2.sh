export PYTHONPATH="/opt/www/friendfund";
cd /opt/www/friendfund;
case "$1" in
  start)
    /server/pylons1.0/bin/paster serve --reload --daemon --pid-file=run/friendfund2.pid --log-file=./logs/webserver2.log ./dev2.ini start
    ;;
  stop)
    /server/pylons1.0/bin/paster serve --reload --daemon --pid-file=run/friendfund2.pid --log-file=./logs/webserver2.log  ./dev2.ini stop
    ;;
  restart)
    /server/pylons1.0/bin/paster serve --reload --daemon --pid-file=run/friendfund2.pid --log-file=./logs/webserver2.log ./dev2.ini restart
    ;;
  *)
    echo $"Usage: $0 {start|stop|restart}"
    exit 1
esac
