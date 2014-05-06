export PYTHONPATH="/opt/www/ff_live:/home/www-data/deployment/ff_current";
cd /opt/www/ff_live;
python /home/www-data/deployment/ff_next/friendfund/tasks/api_crawler_zanox.py -f aff_import.ini -r de
python /home/www-data/deployment/ff_next/friendfund/tasks/api_crawler_zanox.py -f aff_import.ini -r gb
python /home/www-data/deployment/ff_next/friendfund/tasks/api_crawler_zanox.py -f aff_import.ini -r us
