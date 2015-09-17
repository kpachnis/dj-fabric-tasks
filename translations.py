from fabric.api import cd, env, roles, run, settings, task
from fabric.colors import green


@roles('app')
@task
def compile():
    """
    Compile gettext translations
    """

    print(green('Compiling gettext translations'))
    with settings(user=env.deployer['account']):
        with cd(env.app_path):
            run('./env/bin/python manage.py compilemessages')
