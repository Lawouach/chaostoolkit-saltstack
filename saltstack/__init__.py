# -*- coding: utf-8 -*-
import json
import os
import os.path
from typing import List

from chaoslib.discovery.discover import discover_actions, discover_probes, \
    initialize_discovery_result
from chaoslib.exceptions import DiscoveryFailed
from chaoslib.types import Discovery, DiscoveredActivities, \
    DiscoveredSystemInfo, Secrets
from logzero import logger
import requests
import ssl
# context = ssl._create_unverified_context()
from requests.packages.urllib3.exceptions import InsecureRequestWarning

__all__ = ["saltstack_api_client", "discover", "__version__"]
__version__ = '0.0.1'

class salt_api_client:

    def ApiClient(self, configuration):
        self.url = configuration['url']
        self.username = configuration['username']
        self.password = configuration['password']
        #Default settings for Salt Master
        self.headers = {"Content-type": "application/json"}
        self.params = {'client': 'local', 'fun': '', 'tgt': ''}
        #Use User/Pass
        self.login_url = self.url + "login"
        self.login_params = {'username': self.username, 'password': self.password, 'eauth': 'pam'}
        #Use Token
        if configuration['token'] is not None:
            self.useToken = True
            self.token = configuration['token']
            self.headers['X-Auth-Token'] = self.token

    def run_cmd(self, tgt, method, arg=None):
        """
           remote run commands，same with:
               salt 'client1' cmd.run 'ls -li'
        """
        if arg:
            params = {'client':'local', 'fun': method, 'tgt': tgt, 'arg': arg, 'tgt_type':'list' }

        else:
            params = {'client':'local', 'fun': method, 'tgt': tgt, 'tgt_type':'list' }

        #Refresh token for each execution
        self.__check_token__()
        result = self.__get_http_data__(self.url, params)
        return result

    def async_run_cmd(self, tgt, method, arg=None):
        return None

    def get_cmd_result(self, tgt, method, arg=None):
        return None

    def get_grains_get(self, tgt, item):
        params = {'client':'local', 'fun': 'grains.get', 'tgt': tgt, 'arg':item, 'tgt_type':'list' }
        self.__check_token__()
        result = self.__get_http_data__(self.url, params)
        return result

    ###############################################################################
    # Private functions
    ###############################################################################
    def __get_http_data__(self, url, params):
        send_data = json.dumps(params)
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        request = requests.post(url, data=send_data, headers=self.headers, verify=False)
        response = request.json()
        result = dict(response)
        return result['return'][0]

    def __obtain_token__(self):
        self.token = self.__get_http_data__(self.login_url, self.login_params).get('token')
        self.headers['X-Auth-Token'] = self.token

    def __check_token__(self):
        if self.useToken != True:
            self.__obtain_token__()

#TODO Not implemented
def is_saltmaster_local():
    # config_path = os.path.expanduser(
    #     os.environ.get('KUBECONFIG', '~/.kube/config'))
    # return os.path.exists(config_path)
    return False

def saltstack_api_client(secrets: Secrets = None) -> salt_api_client.ApiClient:
    """
    Create a SaltStack http(s) client from:

    1. Useranme & Password. 
       -d username='salt' -d password='1QaZ2WsX456F' -d eauth='pam'
       Then a token in obrained via <salt_url>/login 

    2. Token
       A token directly, same with the backend of 1.

    3. Key, only from Salt Master


        * SALTMASTER_HOST: Salt Master API address

        You can authenticate with user / password via:
        * SALTMASTER_USER: the user name 
        * SALTMASTER_PASSWORD: the password

        Or via a token: 
        * SALTMASTER_TOKEN

        Or via local config if you are running this on Salt Master

        You may pass a secrets dictionary, in which case, values will be looked
        there before the environ.
    """
    env = os.environ
    secrets = secrets or {}

    def lookup(k: str, d: str = None) -> str:
        return secrets.get(k, env.get(k, d))

    if is_saltmaster_local():

        #TODO Not implemented
        configuration = dict()
        return salt_api_client.ApiClient(configuration)

    else:

        configuration = dict()
        configuration['debug'] = True
        configuration['url'] = lookup("SALTMASTER_HOST", "http://localhost")

        if "SALTMASTER_HOST" in env or "SALTMASTER_HOST" in secrets:
            configuration['url'] = lookup("SALTMASTER_HOST", "http://localhost")
        if "SALTMASTER_USER" in env or "SALTMASTER_USER" in secrets:
            configuration['username'] = lookup("SALTMASTER_USER", "")
            configuration['password'] = lookup("SALTMASTER_PASSWORD", "")
        if "SALTMASTER_TOKEN" in env or "SALTMASTER_TOKEN" in secrets:
            configuration['token'] = lookup("SALTMASTER_TOKEN")

    return client.ApiClient(configuration)


def discover(discover_system: bool = True) -> Discovery:
    """
    Discover SaltStack capabilities offered by this extension.
    """
    logger.info("Discovering capabilities from chaostoolkit-saltstack")

    discovery = initialize_discovery_result(
        "chaostoolkit-saltstack", __version__, "saltstack")
    discovery["activities"].extend(load_exported_activities())
    return discovery


###############################################################################
# Private functions
###############################################################################
def load_exported_activities() -> List[DiscoveredActivities]:
    """
    Extract metadata from actions and probes exposed by this extension.
    """
    activities = []
    activities.extend(discover_actions("saltstack.machine.actions"))
    activities.extend(discover_probes("saltstack.machine.probes"))
    return activities
