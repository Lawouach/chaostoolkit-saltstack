# -*- coding: utf-8 -*-
import os
from typing import Any, Dict, List
import json

from saltstack import saltstack_api_client
import saltstack
from saltstack.machine.constants import OS_LINUX, OS_WINDOWS

from chaoslib.exceptions import FailedActivity
from chaoslib.types import Configuration, Secrets
from logzero import logger
from time import sleep

__all__ = ["stress_cpu", "fill_disk", "network_latency", "burn_io", 
           "network_loss", "network_corruption", "network_advanced"]

def stress_cpu(instance_ids: List[str] = None,
               execution_duration: str = "60",
               configuration: Configuration = None,
               secrets: Secrets = None):
    """
    Stress CPU up to 100% at random machines.

    Parameters
    ----------
    filter : str, optional
        Filter the virtual machines. If the filter is omitted all machines in
        the subscription will be selected as potential chaos candidates.
    duration : int, optional
        Duration of the stress test (in seconds) that generates high CPU usage.
        Defaults to 120 seconds.
    timeout : int
        Additional wait time (in seconds) for stress operation to be completed.
        Getting and sending data from/to Azure may take some time so it's not
        recommended to set this value to less than 30s. Defaults to 60 seconds.

    Examples
    --------
    Some calling examples. Deep dive into the filter syntax:
    https://docs.microsoft.com/en-us/azure/kusto/query/

    >>> stress_cpu("where resourceGroup=='rg'", configuration=c, secrets=s)
    Stress all machines from the group 'rg'

    >>> stress_cpu("where resourceGroup=='rg' and name='name'",
                    configuration=c, secrets=s)
    Stress the machine from the group 'rg' having the name 'name'

    >>> stress_cpu("where resourceGroup=='rg' | sample 2",
                    configuration=c, secrets=s)
    Stress two machines at random from the group 'rg'
    """

    logger.debug(
        "Start stress_cpu: configuration='{}', filter='{}'".format(
            configuration, filter))

    logger.debug(json.dumps(secrets))

    try:
        client = saltstack.saltstack_api_client(secrets)
        machines = client.get_grains_get(instance_ids, 'kernel')

        jids = dict()
        for k,v in machines.items():
            name = k
            os_type = v
            if os_type == OS_WINDOWS:
                command_id = '' #TODO
                script_name = "cpu_stress_test.ps1"
                cmd_param = "duration="+execution_duration+"\n" #TODO in ps1
            elif os_type == OS_LINUX:
                command_id = 'cmd.run'
                script_name = "cpu_stress_test.sh"
                cmd_param = "duration="+execution_duration+"\n"
            else:
                raise FailedActivity(
                    "Cannot run CPU stress test on OS: %s" % os_type)

            with open(os.path.join(os.path.dirname(__file__),
                                   "scripts", script_name)) as file:
                script_content = file.read()
            #merge duration
            script_content = cmd_param+script_content

            #Do aync cmd and get jid
            logger.debug("Stressing CPU of machine: {}".format(name))
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
            "failed issuing a execute of shell script via salt API" + str(x)
            )

    if results:
        for k,v in results.items():
            logger.info(k + " - " + v)  
    else:
        raise FailedActivity(
            "stress_cpu operation did not finish on time. "
        )


def fill_disk(filter: str = None,
              duration: int = 120,
              timeout: int = 60,
              size: int = 1000,
              configuration: Configuration = None,
              secrets: Secrets = None):
    """
    Fill the disk with random data.

    Parameters
    ----------
    filter : str, optional
        Filter the virtual machines. If the filter is omitted all machines in
        the subscription will be selected as potential chaos candidates.
    duration : int, optional
        Lifetime of the file created. Defaults to 120 seconds.
    timeout : int
        Additional wait time (in seconds)
        for filling operation to be completed.
        Getting and sending data from/to Azure may take some time so it's not
        recommended to set this value to less than 30s. Defaults to 60 seconds.
    size : int
        Size of the file created on the disk. Defaults to 1GB.


    Examples
    --------
    Some calling examples. Deep dive into the filter syntax:
    https://docs.microsoft.com/en-us/azure/kusto/query/

    >>> fill_disk("where resourceGroup=='rg'", configuration=c, secrets=s)
    Fill all machines from the group 'rg'

    >>> fill_disk("where resourceGroup=='rg' and name='name'",
                    configuration=c, secrets=s)
    Fill the machine from the group 'rg' having the name 'name'

    >>> fill_disk("where resourceGroup=='rg' | sample 2",
                    configuration=c, secrets=s)
    Fill two machines at random from the group 'rg'
    """

    # logger.debug(
    #     "Start fill_disk: configuration='{}', filter='{}'".format(
    #         configuration, filter))

    # machines = __fetch_machines(filter, configuration, secrets)
    # client = __compute_mgmt_client(secrets, configuration)

    # for m in machines:
    #     name = m['name']
    #     group = m['resourceGroup']
    #     os_type = __get_os_type(m)
    #     if os_type == OS_WINDOWS:
    #         command_id = 'RunPowerShellScript'
    #         script_name = "fill_disk.ps1"
    #     elif os_type == OS_LINUX:
    #         command_id = 'RunShellScript'
    #         script_name = "fill_disk.sh"
    #     else:
    #         raise FailedActivity(
    #             "Cannot run disk filling test on OS: %s" % os_type)

    #     with open(os.path.join(os.path.dirname(__file__),
    #                            "scripts", script_name)) as file:
    #         script_content = file.read()

    #     logger.debug("Script content: {}".format(script_content))
    #     parameters = {
    #         'command_id': command_id,
    #         'script': [script_content],
    #         'parameters': [
    #             {'name': "duration", 'value': duration},
    #             {'name': "size", 'value': size}
    #         ]
    #     }

    #     logger.debug("Filling disk of machine: {}".format(name))
    #     poller = client.virtual_machines.run_command(group, name, parameters)
    #     result = poller.result(duration + timeout)  # Blocking till executed
    #     logger.debug("Execution result: {}".format(poller))
    #     if result:
    #         logger.debug(result.value[0].message)  # stdout/stderr
    #     else:
    #         raise FailedActivity(
    #             "fill_disk operation did not finish on time. "
    #             "You may consider increasing timeout setting.")


def network_latency(filter: str = None,
                    duration: int = 60,
                    delay: int = 200,
                    jitter: int = 50,
                    timeout: int = 60,
                    configuration: Configuration = None,
                    secrets: Secrets = None):
    """
    Increases the response time of the virtual machine.

    Parameters
    ----------
    filter : str, optional
        Filter the virtual machines. If the filter is omitted all machines in
        the subscription will be selected as potential chaos candidates.
    duration : int, optional
        How long the latency lasts. Defaults to 60 seconds.
    timeout : int
        Additional wait time (in seconds) for filling operation to be completed
        Getting and sending data from/to Azure may take some time so it's not
        recommended to set this value to less than 30s. Defaults to 60 seconds.
    delay : int
        Added delay in ms. Defaults to 200.
    jitter : int
        Variance of the delay in ms. Defaults to 50.


    Examples
    --------
    Some calling examples. Deep dive into the filter syntax:
    https://docs.microsoft.com/en-us/azure/kusto/query/

    >>> network_latency("where resourceGroup=='rg'", configuration=c,
                    secrets=s)
    Increase the latency of all machines from the group 'rg'

    >>> network_latency("where resourceGroup=='rg' and name='name'",
                    configuration=c, secrets=s)
    Increase the latecy of the machine from the group 'rg' having the name
    'name'

    >>> network_latency("where resourceGroup=='rg' | sample 2",
                    configuration=c, secrets=s)
    Increase the latency of two machines at random from the group 'rg'
    """

    # logger.debug(
    #     "Start network_latency: configuration='{}', filter='{}'".format(
    #         configuration, filter))

    # machines = __fetch_machines(filter, configuration, secrets)
    # client = __compute_mgmt_client(secrets, configuration)

    # for m in machines:
    #     name = m['name']
    #     group = m['resourceGroup']
    #     os_type = __get_os_type(m)
    #     if os_type == OS_LINUX:
    #         command_id = 'RunShellScript'
    #         script_name = "network_latency.sh"
    #     else:
    #         raise FailedActivity(
    #             "Cannot run network latency test on OS: %s" % os_type)

    #     with open(os.path.join(os.path.dirname(__file__),
    #                            "scripts", script_name)) as file:
    #         script_content = file.read()

    #     logger.debug("Script content: {}".format(script_content))
    #     parameters = {
    #         'command_id': command_id,
    #         'script': [script_content],
    #         'parameters': [
    #             {'name': "duration", 'value': duration},
    #             {'name': "delay", 'value': delay},
    #             {'name': "jitter", 'value': jitter}
    #         ]
    #     }

    #     logger.debug("Increasing the latency of machine: {}".format(name))
    #     poller = client.virtual_machines.run_command(group, name, parameters)
    #     result = poller.result(duration + timeout)  # Blocking till executed
    #     logger.debug("Execution result: {}".format(poller))
    #     if result:
    #         logger.debug(result.value[0].message)  # stdout/stderr
    #     else:
    #         raise FailedActivity(
    #             "network_latency operation did not finish on time. "
    #             "You may consider increasing timeout setting.")


def burn_io(filter: str = None,
            duration: int = 60,
            timeout: int = 60,
            configuration: Configuration = None,
            secrets: Secrets = None):
    """
    Increases the Disk I/O operations per second of the virtual machine.

    Parameters
    ----------
    filter : str, optional
        Filter the virtual machines. If the filter is omitted all machines in
        the subscription will be selected as potential chaos candidates.
    duration : int, optional
        How long the burn lasts. Defaults to 60 seconds.
    timeout : int
        Additional wait time (in seconds) for filling operation to be completed
        Getting and sending data from/to Azure may take some time so it's not
        recommended to set this value to less than 30s. Defaults to 60 seconds.


    Examples
    --------
    Some calling examples. Deep dive into the filter syntax:
    https://docs.microsoft.com/en-us/azure/kusto/query/

    >>> burn_io("where resourceGroup=='rg'", configuration=c, secrets=s)
    Increase the I/O operations per second of all machines from the group 'rg'

    >>> burn_io("where resourceGroup=='rg' and name='name'",
                    configuration=c, secrets=s)
    Increase the I/O operations per second of the machine from the group 'rg'
    having the name 'name'

    >>> burn_io("where resourceGroup=='rg' | sample 2",
                    configuration=c, secrets=s)
    Increase the I/O operations per second of two machines at random from
    the group 'rg'
    """

    # logger.debug(
    #     "Start burn_io: configuration='{}', filter='{}'".format(
    #         configuration, filter))

    # machines = __fetch_machines(filter, configuration, secrets)
    # client = __compute_mgmt_client(secrets, configuration)

    # for m in machines:
    #     name = m['name']
    #     group = m['resourceGroup']
    #     os_type = __get_os_type(m)
    #     if os_type == OS_LINUX:
    #         command_id = 'RunShellScript'
    #         script_name = "burn_io.sh"
    #     else:
    #         raise FailedActivity(
    #             "Cannot run burn_io test on OS: %s" % os_type)

    #     with open(os.path.join(os.path.dirname(__file__),
    #                            "scripts", script_name)) as file:
    #         script_content = file.read()

    #     logger.debug("Script content: {}".format(script_content))
    #     parameters = {
    #         'command_id': command_id,
    #         'script': [script_content],
    #         'parameters': [
    #             {'name': "duration", 'value': duration},
    #         ]
    #     }

    #     logger.debug("Increasing the I/O operations per "
    #                  "second of machine: {}".format(name))
    #     poller = client.virtual_machines.run_command(group, name, parameters)
    #     result = poller.result(duration + timeout)  # Blocking till executed
    #     logger.debug("Execution result: {}".format(poller))
    #     if result:
    #         logger.debug(result.value[0].message)  # stdout/stderr
    #     else:
    #         raise FailedActivity(
    #             "burn_io operation did not finish on time. "
    #             "You may consider increasing timeout setting.")

def network_loss():
    return

def network_corruption():
    return

def network_advanced():
    return

###############################################################################
# Private helper functions
###############################################################################
# def __start_stopped_machines(client, stopped_machines):
#     for machine in stopped_machines:
#         logger.debug("Starting machine: {}".format(machine['name']))
#         client.virtual_machines.start(machine['resourceGroup'],
#                                       machine['name'])


# def __fetch_all_stopped_machines(client, machines) -> []:
#     stopped_machines = []
#     for m in machines:
#         i = client.virtual_machines.instance_view(m['resourceGroup'],
#                                                   m['name'])
#         for s in i.statuses:
#             status = s.code.lower().split('/')
#             if status[0] == 'powerstate' and (
#                     status[1] == 'deallocated' or status[1] == 'stopped'):
#                 stopped_machines.append(m)
#                 logger.debug("Found stopped machine: {}".format(m['name']))
#     return stopped_machines


# def __fetch_machines(filter, configuration, secrets) -> []:
#     machines = fetch_resources(filter, RES_TYPE_VM, secrets, configuration)
#     if not machines:
#         logger.warning("No virtual machines found")
#         raise FailedActivity("No virtual machines found")
#     else:
#         logger.debug(
#             "Fetched virtual machines: {}".format(
#                 [x['name'] for x in machines]))
#     return machines


# def __get_os_type(machine):
#     os_type = machine['properties']['storageProfile']['osDisk']['osType'] \
#         .lower()
#     if os_type not in (OS_LINUX, OS_WINDOWS):
#         raise FailedActivity("Unknown OS Type: %s" % os_type)

#     return os_type
