from fabric.api import cd, env, hide, roles, run, settings, task
from fabric.colors import green


@roles('db')
@task
def init():
    """
    Populate the application database and assign the database owner
    """

    print(green('Creating MySQL database for {0}'.format(env.app)))
    with hide('running'):
        run('mysql -u {0} -p{1} -e "CREATE DATABASE {2} CHARACTER SET utf8 COLLATE utf8_general_ci;"'.format(env.dba['user'], env.dba['password'], env.db['name']))
        run('mysql -u {0} -p{1} -e "CREATE USER \'{2}\'@\'localhost\' IDENTIFIED BY \'{3}\'"'.format(env.dba['user'], env.dba['password'], env.db['user'], env.db['password']))
        run('mysql -u {0} -p{1} -e "GRANT ALL PRIVILEGES ON {2}.* TO \'{3}\'@\'localhost\'"'.format(env.dba['user'], env.dba['password'], env.db['name'], env.db['user']))

    print(green('Initializing database for the first time'))
    with settings(user=env.deployer['account']):
        with cd(env.app_path):
            run('./env/bin/python manage.py syncdb --noinput --migrate')


@roles('db')
@task
def migrate():
    """
    Run database migrations
    """

    print(green('Applying database migrations'))
    with settings(user=env.deployer['account']):
        with cd(env.app_path):
            run('./env/bin/python manage.py migrate --delete-ghost-migrations')
