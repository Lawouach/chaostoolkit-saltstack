# -*- coding: utf-8 -*-
import os
from typing import Any, Dict, List
import json

from saltstack import saltstack_api_client
import saltstack
from saltstack.machine.constants import OS_LINUX, OS_WINDOWS
from saltstack.machine.constants import BURN_CPU, FILL_DISK, NETWORK_UTIL, BURN_IO

from chaoslib.exceptions import FailedActivity
from chaoslib.types import Configuration, Secrets
from logzero import logger
from time import sleep

__all__ = ["burn_cpu", "fill_disk", "network_latency", "burn_io", 
           "network_loss", "network_corruption", "network_advanced"]

def burn_cpu(instance_ids: List[str] = None,
               execution_duration: str = "60",
               configuration: Configuration = None,
               secrets: Secrets = None):
    """
    burn CPU up to 100% at random machines.

    Parameters
    ----------
    instance_ids : List[str]
        Filter the virtual machines. If the filter is omitted all machines in
        the subscription will be selected as potential chaos candidates.
    execution_duration : str, optional
        Duration of the stress test (in seconds) that generates high CPU usage.
        Defaults to 60 seconds.
    """

    logger.debug(
        "Start burn_cpu: configuration='{}', instance_ids='{}'".format(
            configuration, instance_ids))

    logger.debug(json.dumps(secrets))

    try:
        client = saltstack.saltstack_api_client(secrets)
        machines = client.get_grains_get(instance_ids, 'kernel')

        param = dict()
        param["execution_duration"]=execution_duration

        jids = dict()
        for k,v in machines.items():
            name = k
            os_type = v
            script_content = __construct_script_content__(BURN_CPU, os_type, param)

            #Do aync cmd and get jid
            logger.debug("Burning CPU of machine: {}".format(name))
            salt_method = 'cmd.run'
            jid = client.async_run_cmd( name, salt_method, script_content)
            jids[k] = jid
        logger.debug(json.dumps(jids))
        #Wait the duration as well
        sleep(int(execution_duration))

        #Check result
        results = dict()
        results_overview = True
        for k,v in jids.items():
            res = client.async_cmd_exit_success(v)[k]
            result = client.get_async_cmd_result(v)[k]

            results_overview = results_overview and res
            results[k]=result
    except Exception as x:
        raise FailedActivity(
            "failed issuing a execute of shell script via salt API " + str(x)
            )

    if results:
        for k,v in results.items():
            logger.info(k + " - " + v)  
    else:
        raise FailedActivity(
            "burn_cpu operation did not finish on time. "
        )


def fill_disk(instance_ids: str = None,
              execution_duration: int = 120,
              size: int = 1000,
              configuration: Configuration = None,
              secrets: Secrets = None):
    """
    For now do not have this scenario, 

    Fill the disk with random data.

    Parameters
    ----------
    instance_ids : List[str]
        Filter the virtual machines. If the filter is omitted all machines in
        the subscription will be selected as potential chaos candidates.
    execution_duration : str, optional
        Lifetime of the file created. Defaults to 120 seconds.
    size : int
        Size of the file created on the disk. Defaults to 1GB.
    """

    logger.debug(
        "Start fill_disk: configuration='{}', instance_ids='{}'".format(
            configuration, instance_ids))

    logger.debug(json.dumps(secrets))

    try:
        client = saltstack.saltstack_api_client(secrets)
        machines = client.get_grains_get(instance_ids, 'kernel')

        param = dict()
        param["execution_duration"]=execution_duration
        
        jids = dict()
        for k,v in machines.items():
            name = k
            os_type = v
            script_content = __construct_script_content__(FILL_DISK, os_type, param)

            #Do aync cmd and get jid
            logger.debug("Filling disk of machine: {}".format(name))
            salt_method = 'cmd.run'
            jid = client.async_run_cmd( name, salt_method, script_content)
            jids[k] = jid
        logger.debug(json.dumps(jids))
        #Wait the duration as well
        sleep(int(execution_duration))

        #Check result
        results = dict()
        results_overview = True
        for k,v in jids.items():
            res = client.async_cmd_exit_success(v)[k]
            result = client.get_async_cmd_result(v)[k]

            results_overview = results_overview and res
            results[k]=result
    except Exception as x:
        raise FailedActivity(
            "failed issuing a execute of shell script via salt API " + str(x)
            )

    if results:
        for k,v in results.items():
            logger.info(k + " - " + v)  
    else:
        raise FailedActivity(
            "fill_disk operation did not finish on time. "
        )

def burn_io(instance_ids: str = None,
            execution_duration: int = 60,
            configuration: Configuration = None,
            secrets: Secrets = None):
    """
    Increases the Disk I/O operations per second of the virtual machine.

    Parameters
    ----------
    instance_ids : List[str]
        Filter the virtual machines. If the filter is omitted all machines in
        the subscription will be selected as potential chaos candidates.
    execution_duration : str, optional
        Lifetime of the file created. Defaults to 120 seconds.
    """

    logger.debug(
        "Start burn_io: configuration='{}', instance_ids='{}'".format(
            configuration, instance_ids))

    logger.debug(json.dumps(secrets))

    try:
        client = saltstack.saltstack_api_client(secrets)
        machines = client.get_grains_get(instance_ids, 'kernel')

        param = dict()
        param["execution_duration"]=execution_duration
        
        jids = dict()
        for k,v in machines.items():
            name = k
            os_type = v
            script_content = __construct_script_content__(BURN_IO, os_type, param)

            #Do aync cmd and get jid
            logger.debug("Burning I/O of machine: {}".format(name))
            salt_method = 'cmd.run'
            jid = client.async_run_cmd( name, salt_method, script_content)
            jids[k] = jid
        logger.debug(json.dumps(jids))
        #Wait the duration as well
        sleep(int(execution_duration))

        #Check result
        results = dict()
        results_overview = True
        for k,v in jids.items():
            res = client.async_cmd_exit_success(v)[k]
            result = client.get_async_cmd_result(v)[k]

            results_overview = results_overview and res
            results[k]=result
    except Exception as x:
        raise FailedActivity(
            "failed issuing a execute of shell script via salt API " + str(x)
            )

    if results:
        for k,v in results.items():
            logger.info(k + " - " + v)  
    else:
        raise FailedActivity(
            "burn io operation did not finish on time. "
        )


def network_advanced():
    return

def network_loss():
    return

def network_corruption():
    return

def network_latency(instance_ids: str = None,
                    execution_duration: int = 60,
                    delay: int = 200,
                    jitter: int = 50,
                    timeout: int = 60,
                    configuration: Configuration = None,
                    secrets: Secrets = None):
    """
    Increases the response time of the virtual machine.

    Parameters
    ----------
    instance_ids : List[str]
        Filter the virtual machines. If the filter is omitted all machines in
        the subscription will be selected as potential chaos candidates.
    execution_duration : str, optional
        Lifetime of the file created. Defaults to 120 seconds.
    delay : int
        Added delay in ms. Defaults to 200.
    jitter : int
        Variance of the delay in ms. Defaults to 50.

    """
    return

# def restore_network_setting():
#     return
#
# def release_io():
#     return

###############################################################################
# Private helper functions
###############################################################################
def __construct_script_content__( action, os_type, parameters):

    if os_type == OS_WINDOWS:
        script_name = action+".ps1"
        #TODO in ps1
        cmd_param = '\n'.join(['='.join(k,v) for k,v in parameters.items()]) 
    elif os_type == OS_LINUX:
        script_name = action+".sh"
        cmd_param = '\n'.join(['='.join(k,v) for k,v in parameters.items()])
    else:
        raise FailedActivity(
            "Cannot find corresponding script for %s on OS: %s" % (action, os_type) )

    with open(os.path.join(os.path.dirname(__file__),
                           "scripts", script_name)) as file:
        script_content = file.read()
    #merge duration
    script_content = cmd_param+script_content
    return script_content


