export PYTHONPATH="/opt/www/ff_test:/home/www-data/ff_test";
cd /opt/www/ff_test
nohup /server/pylons1.0/bin/paster serve --reload test_env.ini &

