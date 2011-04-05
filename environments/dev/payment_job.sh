runpath=/opt/www/friendfund
binpath=/home/www-data/ff_dev
config=./development.ini

export PYTHONPATH="$runpath:$binpath";
python $binpath/friendfund/tasks/payment_job.py -f $config

