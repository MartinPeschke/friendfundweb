runpath=/opt/www/friendfund
binpath=/home/www-data/ff_dev
config=./development.ini

export PYTHONPATH="$runpath:$binpath";
python $binpath/friendfund/tasks/notifier.py -f $config

