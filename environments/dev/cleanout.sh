python tools/dbtools.py development.ini clean
/etc/init.d/memcached_dev restart
./celeryd.sh restart
rm -rf data/s/*

