from fabric.context_managers import cd
from fabric.contrib.files import append, upload_template
from fabric.decorators import task
from fabric.operations import sudo, run, put
from fabric.contrib import files
from inventory import vagrant

__author__ = 'Martin'



SYSTEM_PACKAGES = ["sudo"
                  , "build-essential"
                  , "libjpeg62-dev"
                  , "libxml2-dev"
                  , "libxslt1-dev"
                  , "unzip"
                  , "libpng12-dev"
                  , "libfreetype6-dev"
                  , "libpcre3-dev"
                  , "libpcre3-dev"
                  , "libssl-dev"
                  , "apache2-utils"
                  , "lib32bz2-dev"
                  , "curl"
                  , "vim"
                  , "libreadline6"
                  , "libreadline6-dev"
                  , "libmhash2"
                  , "libmhash-dev"
                  , "libmcrypt4"
                  , "libtomcrypt-dev"
                  , "libssl-dev"
                  , "libevent-dev"
                  , "git", "curl"]

EXTRA_PACKAGES = ['supervisor',
                  'imagemagick',
                  'memcached',
                  'libmemcached-dev',
                  'unixodbc',
                  'unixodbc-dev']

VERSIONS = {
    "PYTHON":"2.7.6"
    , "NGINX":"1.5.12"
    , "MEMCACHED":"1.4.15"
    , "REDIS":"2.6.17"
    , "NODE":"0.10.26"
    , "FREETDS": "0.91.102"
    , "GEOIP": "1.6.0"
}

NEWRELIC_LICENSEKEY='0b05ef93874b87d2b6fb3878e68299db385c15c5'
KEYS = [
  "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCtJYB+2da2RK60ZBqagi5/x9hRD2uxGt5Td1FbsPioFF2+8Nmb5pL0byutXvF03bIbxWFnb0F4mY0kO5zJYOqvZoIsrmBmWMSQNH9CzXbPxjgQCXKukPjl7Xsb8S7hmIZ6I7PH0XSQl67i9eTOzOJGx9BI2P2nhXli9g+WT75x6P3dL86oyf9+MHMZl4z89RDJvebj8s+19xrCmmAEiR6gdpjW4xPCx8z/CDA9PbvMs5deOUTV5pKmBkNfJahzjkY9eJD4FDfE6r+9H5gr2+0I3mnmPYg+mJJf9bfylQo/Z1nccCKqp1aPjT7P+urIBaSMdlwtD9nUa4uzwnBBdswkVER3Y3U4Zv1RvbU59qH32xwt0CuMLA/GSqY7eWZ19RnRYk9CP0Ukx2LGahOVeUiIRizhzaIjhSNw2Kp1qTASwpoREl8VDPmXTTePkAUNJ/Jxn3218qcMrRjHY5tFgfy9Sj8WdqJoVm29x9aZCB0487oOS2zLEgWjPkQ9e4TacfkVYqzqYIHTQ0LVkeFarOHKLAUBRid6aVs+Earf78ipJIg7H+0w1xEv7+Z3Y5x5oaRfg9Z6s6kccJ2U+Ne9OuHs77fa0tI4gV626Q4KQgpDpMOgN1picEOwxVLeJGW4Kaa07UAEdwSsxAK/m1LqSXc2I/oOp/oA3O1lttv/EIYS9Q== www-data@hnchudson"
]

# required for execution
__IMPORT_KEEP__ = lambda x: vagrant


def update_sys():
    sudo("apt-get update")
    sudo("apt-get install -y {}".format(" ".join(SYSTEM_PACKAGES)))


def add_python():
    with cd("/tmp"):
        sudo("wget http://www.python.org/ftp/python/{0}/Python-{0}.tgz".format(VERSIONS['PYTHON']))
        sudo("tar xfv Python-{}.tgz".format(VERSIONS['PYTHON']))
        with cd("Python-{}".format(VERSIONS['PYTHON'])):
            sudo("./configure && make && make install")
            sudo("wget http://peak.telecommunity.com/dist/ez_setup.py")
            sudo("python ez_setup.py")
            sudo("easy_install virtualenv Cython ctypes")


def add_rabbit_mq():
    files.append('/etc/apt/sources.list', 'deb http://www.rabbitmq.com/debian/ testing main', use_sudo=True)
    run('wget http://www.rabbitmq.com/rabbitmq-signing-key-public.asc')
    sudo('sudo apt-key add rabbitmq-signing-key-public.asc')
    sudo('apt-get update')
    sudo('apt-get install -y rabbitmq-server')
    sudo('rabbitmqctl add_user rabbitmquser rabbitmqpassword')
    sudo('rabbitmqctl add_vhost rabbitmqvhost')
    sudo('rabbitmqctl set_permissions -p rabbitmqvhost rabbitmquser ".*" ".*" ".*"')

def add_freetds():
    with cd('/tmp'):
        name = "freetds-%s" % VERSIONS['FREETDS']
        sudo('wget ftp://ftp.freetds.org/pub/freetds/stable/%s.tar.gz' % name)
        sudo('tar xfv %s.tar.gz' % name)
        with cd(name):
            sudo('./configure')
            sudo('make')
            sudo('make install')
    upload_template('./templates/odbcinst.ini', '/etc/odbcinst.ini', backup=False, use_sudo=True)


def set_nginx_startup():
    files.upload_template("templates/nginx.initd", "/etc/init.d/nginx",
                          {'NGINX_VERSION': VERSIONS['NGINX']}, use_sudo=True)
    sudo("chmod +x /etc/init.d/nginx")
    sudo("update-rc.d nginx defaults")


def set_nginx_conf():
    sudo("mkdir -p /server/nginx/etc/{sites.enabled,sites.disabled}")
    files.upload_template("templates/nginx.conf", "/server/nginx/etc/nginx.conf",
                          VERSIONS, use_sudo=True)
    sudo("/etc/init.d/nginx reload")


@task
def add_ff_conf():
    files.upload_template("templates/website.conf", "/server/nginx/etc/sites.enabled/ff_dev.conf", VERSIONS, use_sudo=True, backup=False)
    sudo("/etc/init.d/nginx reload")


def add_geoip_lib():
    with cd('/tmp'):
        sudo('wget https://github.com/maxmind/geoip-api-c/releases/download/v1.6.0/GeoIP-%s.tar.gz' % VERSIONS['GEOIP'])
        sudo('tar xfv GeoIP-%s.tar.gz' % VERSIONS['GEOIP'])
        with cd('GeoIP-%s' % VERSIONS['GEOIP']):
            sudo('./configure')
            sudo('make')
            sudo('make install')

def add_geoip_db():
    with cd('/server/nginx/etc'):
        sudo('wget -N http://geolite.maxmind.com/download/geoip/database/GeoLiteCountry/GeoIP.dat.gz')
        sudo('gunzip GeoIP.dat.gz')


@task
def add_nginx():
    add_geoip_lib()
    with cd("/tmp"):
        sudo("wget http://nginx.org/download/nginx-{}.tar.gz".format(VERSIONS['NGINX']))
        sudo("tar xfv nginx-{}.tar.gz".format(VERSIONS['NGINX']))
        with cd("nginx-{}".format(VERSIONS['NGINX'])):
            sudo("./configure "
                 "--group=www-data "
                 "--user=www-data "
                 "--with-http_ssl_module "
                 "--prefix=/server/nginx/{} "
                 "--conf-path=/server/nginx/etc/nginx.conf "
                 "--error-log-path=/server/nginx/logs/error.log "
                 "--pid-path=/server/nginx/run/nginx.pid "
                 "--lock-path=/server/nginx/run/nginx.lock "
                 "--with-http_geoip_module "
                 "--with-http_gzip_static_module && "
                 "make && "
                 "make install".format(VERSIONS['NGINX']))
    set_nginx_startup()
    set_nginx_conf()
    add_geoip_db()
    add_ff_conf()


@task
def provision():
    update_sys()
    add_python()
    add_rabbit_mq()
    add_freetds()
    add_nginx()
    sudo('apt-get install -y {}'.format(' '.join(EXTRA_PACKAGES)))

