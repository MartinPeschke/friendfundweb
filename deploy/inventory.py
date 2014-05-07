import md5
from fabric.context_managers import lcd
from fabric.decorators import task
from fabric.operations import local
from fabric.state import env
from collections import namedtuple


SubSite = namedtuple("SubSite", ["location", "scripts", "styles"])
Style = namedtuple("Style", ["list", "hasBuster"])


class Environment(object):
    def __init__(self, env_name, repo, branch, project_name,
                 base_name, process_groups,
                 config_path, root='/server/www',
                 num_procs=1):
        self.env_name = env_name
        self.repo = repo
        self.branch = branch
        self.project_name = project_name
        self.base_name = base_name
        self.process_groups = process_groups
        self.config_path = config_path
        self.root = root
        self.num_procs = num_procs

        self.env_path = '%s/%s' % (self.root, project_name)
        self.deploy_path = "{}/{}".format(self.env_path, self.env_name)

    def get_code_path(self, version):
        return '{}/code/{}/'.format(self.deploy_path, version)

    def get_short_version(self, version):
        return md5.new(version).hexdigest()

    def get_config_file(self, name):
        return '%s/configs/%s/%s' % (self.repo_path, self.config_path, name)

    @property
    def supervisor_conf_name(self):
        return '%s_%s_%s.conf' % (self.project_name, self.base_name, self.env_name)

    @property
    def config_file_path(self):
        return '%s/code/config.ini' % self.deploy_path

    @property
    def supervisor_python_path(self):
        return '%s/code/current/%s' % (self.env_path, self.project_name)

    @property
    def repo_path(self):
        return '%s/repo.git' % self.deploy_path

    @property
    def log_path(self):
        return '%s/logs' % self.deploy_path


@task
def vagrant():
    # change from the default user to 'vagrant'
    env.user = 'vagrant'
    # connect to the port-forwarded ssh
    env.hosts = ['127.0.0.1:2222']

    # use vagrant ssh key
    with lcd('../vagrant/'):
        result = local('vagrant ssh-config | grep IdentityFile', capture=True)
    env.key_filename = result.split()[1]
