from fabric.api import env, roles, sudo, task
from fabric.colors import green


@roles('app')
@task
def start():
    """
    Start application
    """

    print(green('Starting app {0}'.format(env.app)))
    sudo('supervisorctl start {0}'.format(env.app))


@roles('app')
@task
def stop():
    """
    Stop application
    """

    print(green('Stopping app {0}'.format(env.app)))
    sudo('supervisorctl stop {0}'.format(env.app))


@roles('app')
@task
def restart():
    """
    Restart application
    """

    print(green('Restarting app {0}'.format(env.app)))
    sudo('supervisorctl restart {0}'.format(env.app))


@roles('app')
@task
def status():
    """
    Show application status
    """

    print(green('Getting app {0} status'.format(env.app)))
    sudo('supervisorctl status {0}'.format(env.app))
