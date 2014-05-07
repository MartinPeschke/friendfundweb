from datetime import datetime

from fabric.decorators import task

from fabric.api import run, cd
from fabric.contrib import files
from fabric.operations import sudo

from inventory import vagrant, Environment, Style, SubSite



############## CONFIG #########################

PROJECTNAME="friendfund"
SUBSITES = [
    SubSite(location = '.', scripts=[], styles=Style(['less/website.less', 'less/admin.less'], True))
]

CLEAN_SESSIONS = False


ENVIRONMENT_LIST = [
    Environment('dev',
                repo="git@github.com:MartinPeschke/friendfundweb.git",
                branch='master',
                project_name='friendfund',
                base_name='ff_web',
                process_groups=['ff_web_p1'],
                config_path='dev'),
    Environment('live',
                repo="git@github.com:MartinPeschke/friendfundweb.git",
                branch='master',
                project_name='friendfund',
                base_name='ff_web',
                process_groups=['ff_web_p1','ff_web_p2'],
                config_path='live_azure')
]

ENVIRONMENT_LOOKUP = {e.env_name:e for e in ENVIRONMENT_LIST}


EXTRA_SETUP = ['./env/bin/pip install git+git://github.com/bbangert/beaker_extensions.git']

############## DONT TOUCH THIS ################

# required for execution
__IMPORT_KEEP__ = lambda x: vagrant


root = '/server/www/{}/'.format(PROJECTNAME)


@task
def add_supervisor_conf(env):
    environment = ENVIRONMENT_LOOKUP[env]
    spv_name = "/etc/supervisor/conf.d/%s" % environment.supervisor_conf_name
    if files.exists(spv_name):
        sudo("rm %s" % spv_name)
    files.upload_template("supervisor_web.cfg", spv_name, {
        'process_groups': environment.process_groups,
        'num_procs': environment.num_procs,
        'project_part': environment.project_name,
        'deploy_path': environment.deploy_path,
        'log_path': environment.log_path,
        'python_path': environment.supervisor_python_path,
        'config_file': environment.config_file_path
    }, use_jinja=True, use_sudo=True)
    sudo("supervisorctl reload")


@task
def create_env(env):
    files.append(" ~/.ssh/config", ['Host github.com', '\tStrictHostKeyChecking no'])
    environment = ENVIRONMENT_LOOKUP[env]
    if files.exists(environment.deploy_path):
        with cd(environment.deploy_path):
            run("rm -rf *")
            run("mkdir -p {run,logs,code,env,repo.git,static}")
    else:
        run("mkdir -p %s/{run,logs,code,env,repo.git,static}" %
            environment.deploy_path)

    with cd(environment.repo_path):
        run("git clone {} .".format(environment.repo))
        run("git checkout {}".format(environment.branch))

    with cd(environment.deploy_path):
        run("virtualenv --no-site-packages env")
        for extra in EXTRA_SETUP:
            run(extra)
    add_supervisor_conf(env)


def update(env):
    environment = ENVIRONMENT_LOOKUP[env]
    with cd(environment.repo_path):
        run("git pull")


def build(env, version):
    environment = ENVIRONMENT_LOOKUP[env]
    code_path = environment.get_code_path(version)
    run("mkdir %s " %code_path)
    with cd(code_path):
        run("cp -R %s/webapp/* ." % environment.repo_path)


def build_statics(env, version):
    environment = ENVIRONMENT_LOOKUP[env]
    code_path = environment.get_code_path(version)
    return

def switch(env, version):
    environment = ENVIRONMENT_LOOKUP[env]
    code_path = environment.get_code_path(version)

    with cd(code_path):
        run("%s/env/bin/pip install -r requires_install.txt" % environment.deploy_path)
        run("%s/env/bin/python setup.py develop" % environment.deploy_path)

    with cd(environment.deploy_path):
        run("cp %s %s" % (environment.get_config_file("config_web.ini"), environment.config_file_path))

        with cd("code"):
            run("rm current;ln -s {} current".format(version))



@task
def deploy(env):
    VERSION_TOKEN = datetime.now().strftime("%Y%m%d-%H%M%S-%f")[:-3]
    update(env)
    build(env, VERSION_TOKEN)
    build_statics(env, VERSION_TOKEN)
    switch(env, VERSION_TOKEN)