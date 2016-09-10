import click
import os
import shlex
import subprocess
import psutil

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

def run_command(args, logfile=os.devnull):
    with open(logfile, 'w') as f:
        process = subprocess.Popen(args, stdout=f, stderr=subprocess.STDOUT)
    return process.pid


def start_service(service):
    if get_service_pid(service) != None:
        click.echo('%s service has already been started!' % service)
        return

    service_log_file = get_service_log_file(service)
    command = create_command(service)

    click.echo('Starting %s service...' % service)
    run_command(command, service_log_file)
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

    click.echo('%s service is stopped.' % service)

def stop_all_running_services():
    pass

def show_status_all_services():
    pass

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
@click.argument('service', default='basic', type=click.Choice(ACCEPT_SERVICES))
def stop(service):
    service_list = [service]
    if service == 'basic':
        service_list = BASIC_SERVICES
    for service_name in service_list:
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
