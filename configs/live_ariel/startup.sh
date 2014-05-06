export PYTHONPATH="/opt/www/ff_live:/home/www-data/deployment/ff_current";
cd /opt/www/ff_live;
case "$1" in
  start)
    /server/pylons1.0/bin/paster serve --daemon --pid-file=/opt/www/ff_live/run/friendfund.pid --log-file=/opt/www/ff_live/logs/webserver.log /opt/www/ff_live/ariel_1_paste.ini start
    ;;
  stop)
    /server/pylons1.0/bin/paster serve --daemon --pid-file=/opt/www/ff_live/run/friendfund.pid --log-file=/opt/www/ff_live/logs/webserver.log  /opt/www/ff_live/ariel_1_paste.ini stop
    ;;
  restart)
    /server/pylons1.0/bin/paster serve --daemon --pid-file=/opt/www/ff_live/run/friendfund.pid --log-file=/opt/www/ff_live/logs/webserver.log /opt/www/ff_live/ariel_1_paste.ini restart
    ;;
  *)
    echo $"Usage: $0 {start|stop|restart}"
    exit 1
esac
