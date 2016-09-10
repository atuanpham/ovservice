import click
import os
import shlex
import subprocess
import psutil

#------------------------------------------------------------------------------#

class OVError(Exception):
    pass

class OVServiceNotRunning(OVError):
    pass

#------------------------------------------------------------------------------#

BASIC_SERVICES = [
        'activemq',
        'mongodb',
        'ovclient',
        'tomcat'
        ]
OTHER_SERVICES = [
        'redis',
        'sip',
        'vmmanager',
        'scheduler',
        'dal',
        'masterpoller',
        'workerpoller',
        'hsqldb'
        ]
ACCEPT_SERVICES = BASIC_SERVICES + OTHER_SERVICES

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

def get_service_log_file(service_name):
    return LOG_DIR + '/' + service_name + '.log'

def create_command(service):
    config = None
    cmd = None
    if service == 'mongodb':
        config = '--config ' + SERVICES_DIR + '/mongodb/mongodb.conf'
        cmd = SERVICES_DIR + '/mongodb/bin/mongod'
    elif service == 'redis':
        config = SERVICES_DIR + '/redis/redis.conf'
        cmd = SERVICES_DIR + '/redis/bin/redis-server'
    else:
        config = SERVICES_DIR + '/' + service + '/wrapper.conf'
        cmd = WRAPPER_CMD

    return shlex.split(cmd + ' ' + config)

def get_service_pid(service_name):
    cmd = create_command(service_name)
    processes = psutil.process_iter()
    for process in processes:
        if cmd == process.cmdline():
            return process.pid
    raise OVServiceNotRunning("%s service is not running!" % service_name)

def wait_until_service_stopped(service_name):
    while True:
        try:
            pid = get_service_pid(service_name)
        except OVServiceNotRunning:
            break
    return True

def run_command(args, logfile=os.devnull):
    with open(logfile, 'w') as f:
        process = subprocess.Popen(args, stdout=f, stderr=subprocess.STDOUT)
    return process.pid


def start_service(service):
    try:
        pid = get_service_pid(service)
        click.echo('%s service has already been started!' % service)
        return
    except OVServiceNotRunning:
        pass

    service_log_file = get_service_log_file(service)
    command = create_command(service)

    click.echo('Starting %s service...' % service)
    run_command(command, service_log_file)
    click.echo('%s is started.' % service)

def start_list_of_services(services):
    for service in services:
        start_service(service)

def stop_service(service):
    try:
        pid = get_service_pid(service)
        click.echo('Stopping %s service...' % service)
        os.kill(pid, 15)
        wait_until_service_stopped(service)
        click.echo('%s service is stopped.' % service)
        return True
    except OVServiceNotRunning:
        return False

def stop_list_of_services(services):
    for service in services:
        is_success = stop_service(service)
        if not is_success:
            click.echo('%s service is not running!' % service)

def show_status_of_service_list(service_list):
    for service in service_list:
        try:
            pid = get_service_pid(service)
            click.echo('%s service is RUNNING. - pid: %s' % (service, pid))
        except OVServiceNotRunning:
            click.echo('%s service is NOT RUNNING.' % service)

@click.group()
def cli():
    create_dir(LOG_DIR)

@click.command()
@click.option('--basic', is_flag=True)
@click.argument('service', required=False, type=click.Choice(ACCEPT_SERVICES))
def start(basic, service):
    service_list = BASIC_SERVICES

    if service != None:
        service_list = [service]

    if basic:
        service_list = BASIC_SERVICES

    start_list_of_services(service_list)

@click.command()
@click.option('--basic', is_flag=True)
@click.option('--all', is_flag=True)
@click.argument('service', required=False, type=click.Choice(ACCEPT_SERVICES))
def stop(basic, all, service):
    service_list = ACCEPT_SERVICES

    if service != None:
        service_list = [service]

    if basic:
        service_list = BASIC_SERVICES

    if all:
        service_list = ACCEPT_SERVICES

    stop_list_of_services(service_list)

@click.command()
@click.argument('service', type=click.Choice(ACCEPT_SERVICES))
def restart(service):
    stop_service(service)
    start_service(service)

@click.command()
@click.option('--all', is_flag=True)
@click.argument('service', required=False, type=click.Choice(ACCEPT_SERVICES))
def status(all, service):
    service_list = ACCEPT_SERVICES

    if service != None:
        service_list = [service]

    if all:
        service_list = ACCEPT_SERVICES

    show_status_of_service_list(service_list)

#------------------------------------------------------------------------------#
cli.add_command(start)
cli.add_command(status)
cli.add_command(stop)
cli.add_command(restart)
