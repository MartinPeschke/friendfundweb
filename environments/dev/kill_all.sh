/etc/init.d/memcached_dev restart
/etc/init.d/memcached_test restart
ps auxww | grep paster | awk '{print $2}' | xargs kill -9
ps auxww | grep celeryd | awk '{print $2}' | xargs kill -9

/opt/www/friendfund/celery_start.sh &
/opt/www/ff_test/celery_start.sh &

/opt/www/ff_test/startup.sh


