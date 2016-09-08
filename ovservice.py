import click
import os
import shlex
import subprocess

#------------------------------------------------------------------------------#

BASIC_SERVICES = ['activemq', 'mongodb', 'ovclient', 'tomcat']
OTHER_SERVICES = ['redis', 'sip', 'vmmanager', 'scheduler']
ACCEPT_SERVICES = ['basic'] + BASIC_SERVICES + OTHER_SERVICES

NG_HOME = os.environ['NG_HOME']
WRAPPER_CMD = NG_HOME + '/bin/wrapper/wrapper'
SERVICES_DIR = NG_HOME + '/services'

LOG_DIR = '/tmp/ovservice'

#------------------------------------------------------------------------------#

def create_dir(dirname):
    try:
        os.makedirs(dirname)
    except OSError:
        pass

def get_service_log_dir(service_name):
    return LOG_DIR + '/' + service_name

def get_service_pid_file(service_name):
    service_log_dir= get_service_log_dir(service_name)
    return service_log_dir + '/pid'

def get_service_log_file(service_name):
    service_log_dir = get_service_log_dir(service_name)
    return service_log_dir + '/' + service_name + '.log'

def get_service_pid_from_pid_log_file(service_name):
    pid = None
    service_pid_file = get_service_pid_file(service_name)
    try:
        with open(service_pid_file, 'r') as pid_file:
            pid = int(pid_file.read())
    except IOError:
        pass
    return pid

def get_service_pid(service_name):
    pid = get_service_pid_from_pid_log_file(service_name)

    if pid == None:
        return None

    try:
        os.kill(pid, 0)
    except OSError:
        return None

    return pid

def store_pid(service_name, pid):
    service_pid_file = get_service_pid_file(service_name)
    with open(service_pid_file, 'w') as pid_file:
        pid_file.write(str(pid))

def delete_pid_file(service_name):
    service_pid_file = get_service_pid_file(service_name)
    try:
        os.remove(service_pid_file)
    except OSError:
        return False
    return True

def run_command(cmd, logfile=os.devnull):
    args = shlex.split(cmd)
    with open(logfile, 'w') as f:
        process = subprocess.Popen(args, stdout=f, stderr=subprocess.STDOUT)
    return process.pid


def start_mongodb():
    MONGO_CONFIG = '--config ' + SERVICES_DIR + '/mongodb/mongodb.conf'
    MONGO_CMD = SERVICES_DIR + '/mongodb/bin/mongod'
    cmd = MONGO_CMD + ' ' + MONGO_CONFIG
    service_log_file = get_service_log_file('mongodb')
    return run_command(cmd, service_log_file)

def start_redis():
    REDIS_CONFIG = SERVICES_DIR + '/redis/redis.conf'
    REDIS_CMD = SERVICES_DIR + '/redis/bin/redis-server'
    cmd = REDIS_CMD + ' ' + REDIS_CONFIG
    service_log_file = get_service_log_file('redis')
    return run_command(cmd, service_log_file)

def start_service_with_wrapper(service):
    WRAPPER_CONFIG = SERVICES_DIR + '/' + service + '/wrapper.conf'
    cmd = WRAPPER_CMD + ' ' + WRAPPER_CONFIG
    service_log_file = get_service_log_file(service)
    return run_command(cmd, service_log_file)

def start_service(service):
    service_log_dir = get_service_log_dir(service)
    create_dir(service_log_dir)

    if get_service_pid(service) != None:
        click.echo('%s service has been started!' % service)
        return

    click.echo('Starting %s service...' % service)

    if service == 'mongodb':
        pid = start_mongodb()
    elif service == 'redis':
        pid = start_redis()
    else:
        pid = start_service_with_wrapper(service)

    store_pid(service, pid)

    click.echo('%s is started.' % service)

def stop_service(service):
    pid = get_service_pid(service)

    if pid == None:
        click.echo('%s service is not started!' % service)
        return

    click.echo('Stopping %s service...' % service)

    os.kill(pid, 15)
    while True:
        if get_service_pid(service) == None:
            break

    delete_pid_file(service)

    click.echo('%s service is stopped.' % service)

@click.group()
def cli():
    create_dir(LOG_DIR)

@click.command()
@click.argument('service', default='basic', type=click.Choice(ACCEPT_SERVICES))
def start(service):
    service_list = [service]
    if service == 'basic':
        service_list = BASIC_SERVICES
    for service_name in service_list:
        start_service(service_name)

@click.command()
@click.argument('service', type=click.Choice(ACCEPT_SERVICES))
def stop(service):
    stop_service(service)

@click.command()
@click.argument('service', type=click.Choice(ACCEPT_SERVICES))
def restart(service):
    stop_service(service)
    start_service(service)

@click.command()
@click.argument('service', type=click.Choice(ACCEPT_SERVICES))
def status(service):
    status = 'Running' if get_service_pid(service) != None else 'NOT Running'
    click.echo('Status of %s service: %s' % (service, status))

#------------------------------------------------------------------------------#
cli.add_command(start)
cli.add_command(status)
cli.add_command(stop)
cli.add_command(restart)
