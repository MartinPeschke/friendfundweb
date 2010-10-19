/etc/init.d/memcached_dev restart
ps auxww | grep paster | awk '{print $2}' | xargs kill -9
ps auxww | grep celeryd_dev | awk '{print $2}' | xargs kill -9

/opt/www/friendfund/celery_start.sh &
/opt/www/ff_test/startup.sh


