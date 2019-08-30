# -*- coding: utf-8 -*-
from chaoslib.types import Configuration, Secrets
from typing import Any, List
from logzero import logger
from saltstack import saltstack_api_client
import saltstack

__all__ = ["is_minion_online","is_iproute_tc_installed"]


def is_minion_online(instance_ids: List[str],
                      configuration: Configuration = None,
                      secrets: Secrets = None):
    """
        test.ping salt minions

        Parameters
        ----------
        clients : str or List
            same as 
                salt --list ['client1','client2','client3'] test.ping 
        api return a dict {'client1': True, 'client2': False}
        this function will return dict otherwise raise execption
            {'client1': 'Online', 'client2': 'Offline', 'client3':'Not a Salt Minion' }
    """
    try:
        client = saltstack.saltstack_api_client(secrets)
        machines = client.run_cmd(instance_ids, 'test.ping')

        result = dict()

        for k, v in machines.items():
            if k not in instance_ids:
                result[k] = "Not a Salt Minion"
            else:
                if v == False:
                    result[k] = "Offline"
                else:
                    result[k] = "Online"

        return result

    except Exception as x:
        raise FailedActivity(
            "failed issuing a execute of shell script via salt API " + str(x)
            )


def is_iproute_tc_installed(instance_ids: List[str],
                      configuration: Configuration = None,
                      secrets: Secrets = None):
    """
        cmd.run tc -help

        Parameters
        ----------
        clients : str or List
            same as 
                salt --list ['client1','client2','client3'] cmd.run tc -help
        api return a dict {'client1': 'xxxxxx', 'client2': 'xxxxxx'}
        this function will return dict otherwise raise execption
            {'PCNCMCNSA0018': 'Usage: tc [ OPTIONS ] OBJECT { COMMAND | help }       
            tc [-force] -batch filename where  OBJECT := { qdisc | class | filter | action | monitor | exec }       
            OPTIONS := { -s[tatistics] | -d[etails] | -r[aw] | -p[retty] | -b[atch] [filename] | -n[etns] name |  
            -nm | -nam[es] | { -cf | -conf } path }', 'PCNCMCNSA0016': 'Usage: tc [ OPTIONS ] OBJECT { COMMAND | help }     
            tc [-force] -batch filename where  OBJECT := { qdisc | class | filter | action | monitor | exec }
            OPTIONS := { -s[tatistics] | -d[etails] | -r[aw] | -p[retty] | -b[atch] [filename] | -n[etns] name |
            -nm | -nam[es] | { -cf | -conf } path }'}
    """
    try:
        client = saltstack.saltstack_api_client(secrets)
        machines = client.run_cmd(instance_ids, 'cmd.run', 'tc -help')

        result = dict()

        for k, v in machines.items():
            if k not in instance_ids:
                result[k] = "Not a Salt Minion"
            else:
                if v.startsWith("Usage: tc"):
                    result[k] = "Installed"
                else:
                    result[k] = "Not Installed"

        return result

    except Exception as x:
        raise FailedActivity(
            "failed issuing a execute of shell script via salt API " + str(x)
            )