import datetime

from fabric.api import (
    cd,
    env,
    execute,
    local,
    roles,
    run,
    settings,
    sudo,
    task,
)

from fabric.colors import green
from fabric.contrib.files import append
from fabric.contrib.files import upload_template

import db
import requirements
import service
import translations


@roles('app')
@task
def setup():
    """
    Prepare production server(s)
    """

    execute(create_accounts)
    execute(initialize_application)
    execute(config)
    execute(requirements.install)
    execute(db.init)

    print(green('Updating nginx configuration'))
    with cd('/etc/nginx/sites-enabled'):
        sudo('ln -s {0}/etc/nginx/{1}.conf .'.format(env.app_path, env.app))

    print(green('Updating supervisord configuration'))
    with cd('/etc/supervisor/conf.d'):
        sudo('ln -s {0}/etc/supervisor/conf.d/{1}.conf .'.format(env.app_path, env.app))

    print(green('Creating required dirs'))
    with cd('/var'):
        sudo('mkdir log/{0}'.format(env.app))
        sudo('chown {0}:{1} log/{2}'.format(env.service_account, env.service_account, env.app))
        sudo('mkdir run/{0}'.format(env.app))
        sudo('chown {0}:{1} run/{2}'.format(env.service_account, env.service_account, env.app))


@roles('app')
@task
def release(release_no=datetime.datetime.now().strftime('%d%m%Y%H%M%S')):
    """
    Deploy a new release
    """

    local('git tag -a {0} -m "Production release {1}"'.format(release_no, release_no))
    local('git push origin {0}'.format(release_no))
    update_code(release_no)
    execute(requirements.upgrade)
    execute(translations.compile)
#    execute(collectstatic)
    execute(db.migrate)
    execute(service.restart)

    print(green('Optimizing images'))
    with settings(user=env.deployer['account']):
        with cd('{}/src/mstr/static/images'.format(env.app_path)):
            run('find . -name \*.png -exec optipng -quiet "{}" \;')
            run('find . -name \*.jpg -exec jpegoptim --quiet --strip-all "{}" \;')


@roles('app')
@task
def update_code(release_no):
    """
    Update project codebase
    """

    print(green('Updating {0} code'.format(env.app)))
    with settings(user=env.deployer['account']):
        with cd(env.app_path):
            run('git pull --tags --quiet origin {0}'.format(env.git['branch']))
            run('git checkout -b production_{0} {1}'.format(release_no, release_no))


@roles('app')
@task
def collectstatic():
    """
    Run django collectstatic command
    """

    print(green('Building assets'))
    with settings(user=env.deployer['account']):
        with cd(env.app_path):
            run('./env/bin/python manage.py collectstatic -v 0 --noinput -c ')


@roles('app')
@task
def config():
    """
    Create project local configuration
    """

    context = {
        'secret_key': env.secret_key,
        'db': {
            'name': env.db['name'],
            'user': env.db['user'],
            'password': env.db['password'],
            'host': env.db['host'],
            'port': env.db['port'],
        },
        'recaptcha': {
            'public_key': env.recaptcha['public_key'],
            'private_key': env.recaptcha['private_key'],
        },
        'email': {
            'host': env.email['host'],
            'user': env.email['user'],
            'password': env.email['password'],
            'port': env.email['port'],
            'ssl': env.email['ssl'],
        }
    }

    print('Creating project local configuration')
    with settings(user=env.deployer['account']):
        upload_template('local.py.jinja',
                        '{0}/src/mstr/conf/local.py'.format(env.app_path),
                        context=context, use_jinja=True, template_dir='etc/conf')


def create_accounts():
    """
    Setup the account used to deploy the application.
    """

    print(green('Creating deployer account'))
    sudo('useradd -c "{0} application deployer" -p "{1}" -m -s /bin/bash {2}'.format(env.app, env.deployer['password'], env.deployer['account']))

    print(green('Creating {0} application service account'.format(env.app)))
    sudo('useradd -c "{0} service" --system {1}'.format(env.app, env.app))

    print(green('Uploading SSH keys for deployer account:'))
    with cd('/home/{0}'.format(env.deployer['account'])):
        sudo('mkdir .ssh; chmod 700 .ssh; chown {0}:{1} .ssh'.format(env.deployer['account'], env.deployer['account']))

    with cd('/home/%s/.ssh' % env.deployer['account']):
        sudo('touch authorized_keys; chmod 600 authorized_keys; chown {0}:{1} authorized_keys'.format(env.deployer['account'], env.deployer['account']))
    append('/home/{0}/.ssh/authorized_keys'.format(env.deployer['account']), env.deployer['key'], use_sudo=True)


def initialize_application():
    """
    Create the application path, set the correct permissions and clone the
    application from the repote repository.
    """

    print(green('Creating application path: {0}'.format(env.app_path)))
    sudo('mkdir -p {0}'.format(env.app_path))

    print(green('Updating {0} permissions for account {1}'.format(env.app_path, env.deployer['account'])))
    sudo('chown {0}:{1} {2}'.format(env.deployer['account'], env.deployer['account'], env.app_path))

    print(green('Cloning {0} repo'.format(env.app)))
    with settings(user=env.deployer['account']):
        with cd(env.app_path):
            run('git clone --quiet {0} .'.format(env.git['url']))

    print(green('Creating python virtualenv for app {0}'.format(env.app)))
    with settings(user=env.deployer['account']):
        with cd(env.app_path):
            run('virtualenv --no-site-packages --distribute --prompt="({0}) " env'.format(env.app))
