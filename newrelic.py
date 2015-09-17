from fabric.api import env, roles, sudo, task
from fabric.colors import green
from fabric.contrib.files import upload_template


@roles('app')
@task
def config():
    """
    Generate NewRelic configuration
    """

    print(green('Creating NewRelic configuration.'))
    sudo('mkdir -p /etc/%s' % env.app)

    context = {
        'app_name': env.app,
        'newrelic_key': env.newrelic_key,
    }

    upload_template('etc/conf/newrelic.ini.jinja',
                    '/etc/%s/newrelic.ini' % env.app,
                    context=context, use_jinja=True, use_sudo=True)
