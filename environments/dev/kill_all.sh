/etc/init.d/memcached_dev restart
/etc/init.d/memcached_test restart
ps auxww | grep paster | awk '{print $2}' | xargs kill -9
ps auxww | grep celeryd | awk '{print $2}' | xargs kill -9


/opt/www/friendfund/celeryd.sh start
/opt/www/ff_test/celeryd.sh start
/opt/www/demo/celeryd.sh start

/opt/www/ff_test/startup.sh start
/opt/www/demo/startup.sh start 



