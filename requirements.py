from fabric.api import cd, env, roles, run, settings, task
from fabric.colors import green


@roles('app')
@task
def install():
    """
    Install application requirements
    """

    print(green('Installing application requirements'))
    with settings(user=env.deployer['account']):
        with cd(env.app_path):
            run('./env/bin/pip -q install -r requirements/common.pip')


@roles('app')
@task
def upgrade():
    """
    Upgrade application requirements
    """

    print(green('Upgrading application requirements'))
    with settings(user=env.deployer['account']):
        with cd(env.app_path):
            run('./env/bin/pip -q install -U -r requirements/common.pip')
