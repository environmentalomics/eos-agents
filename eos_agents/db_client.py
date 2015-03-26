"""
db_api_client: Routines to call to the DB API

The most recent HTTP result code is held in the variable "last_status", which
is initially set to -1. 
"""

import requests, json

def catch_disconnection(dbfunc):
    def safe_function(*args):
        try:
            return dbfunc(*args)
        except requests.exceptions.ConnectionError:
            return None
    return safe_function

class DBSession():
    """
    
    """

    def __init__(self, username, password):
        """
        Set "Last Status" to -1, to indicate that no database calls have occured yet.
        """
        self.last_status = -1
        self.username = username
        self.password = password

    def request_get(self, *args):
        result = requests.get(*args, auth=(self.username, self.password))
        self.last_status = result.status_code
        return result

    def request_post(self, *args):
        result = requests.post(*args, auth=(self.username, self.password))
        self.last_status = result.status_code
        return result

    @catch_disconnection
    def get_triggers(self, trigger):
        """Gets a list of all servers in the trigger state specified.
                
        :param trigger: Plaintext of the trigger which we are searching for.
        :returns: List of vm ids.
        """
        r = requests.get('http://localhost:6543/states?state=' + trigger)
        serverlist = r.keys
        return serverlist

    @catch_disconnection
    def get_prestart_item(self):
        r = requests.get('http://localhost:6543/states/Starting?state=Starting')
        return r.text

    @catch_disconnection
    def get_restart_item(self):
        r = requests.get('http://localhost:6543/states/Restarting?state=Restarting')
        return r.text

    @catch_disconnection
    def get_prestop_item(self):
        r = requests.get('http://localhost:6543/states/Stopping?state=Stopping')
        return r.text

    @catch_disconnection
    def get_prepare_item(self):
        r = requests.get('http://localhost:6543/states/Preparing?state=Preparing')
        return r.text

    @catch_disconnection
    def get_boost_item(self):
        r = requests.get('http://localhost:6543/states/prepared?state=Prepared')
        return r.text

    @catch_disconnection
    def get_auto_deboost_item(self):
        r = requests.get('http://localhost:6543/states/boostexpired')
        return r.text

    @catch_disconnection
    def get_manual_deboost_item(self):
        r = requests.get('http://localhost:6543/states/deboosting?state=Deboosting')
        return r.text

    @catch_disconnection
    def get_predeboost_item(self):
        r = requests.get('http://localhost:6543/states/pre_deboosting?state=Pre_Deboosting')
        return r.text

    @catch_disconnection
    def set_state_to_predeboosted(self, vm_id):
        """
        
        """
        r = requests.post('http://localhost:6543/servers/asdf/pre_deboosted', data={"vm_id":vm_id})
        return None

    @catch_disconnection
    def set_state(self, vm_id, state):
        r = requests.post('http://localhost:6543/servers/asdf/' + state, data={"vm_id":vm_id}, auth=(self.username, self.password))

    @catch_disconnection
    def set_state_to_deboosting(self, vm_id):
        """
        
        """
        r = requests.post('http://localhost:6543/servers/asdf/Deboosting', data={"vm_id":vm_id})
        return None

    @catch_disconnection
    def get_deboost_item(self):
        r = requests.get('http://localhost:6543/states/Pre_Deboosted?state=Pre_Deboosted')
        return r.text

    @catch_disconnection
    def get_machine_in_state(self, state):
        r = self.request_get("http://localhost:6543/states/" + state + "?state=" + state)
        return json.loads(r.text)['artifact_id'], json.loads(r.text)['artifact_uuid']

    @catch_disconnection
    def set_state_to_deboosted(self):
        """
        
        """
        r = requests.post('http://localhost:6543/servers/asdf/deboosted', data={"vm_id":vm_id})
        return None

    @catch_disconnection
    def set_state_to_stopped(self, vm_id):
        """
        
        """
        r = requests.post('http://localhost:6543/servers/asdf/stopped', data={"vm_id":vm_id})
        return None

    @catch_disconnection
    def set_state_to_started(self, vm_id):
        """
        
        """
        r = requests.post('http://localhost:6543/servers/asdf/started', data={"vm_id":vm_id})
        return None

    @catch_disconnection
    def set_state_to_prepared(self, vm_id):
        """
        
        """
        r = requests.post('http://localhost:6543/servers/asdf/prepared', data={"vm_id":vm_id})
        return None

    @catch_disconnection
    def get_name(self, vm_id):
        r = requests.get('http://localhost:6543/servers/by_id/' + str(vm_id))
        return json.loads(r.text)['artifact_uuid']

    @catch_disconnection
    def set_state_to_starting(self, vm_id):
        """
        
        """
        r = requests.post('http://localhost:6543/servers/asdf/start', data={"vm_id":vm_id})
        return None

    @catch_disconnection
    def set_state_to_boosting(self, vm_id):
        """
        
        """
        r = requests.post('http://localhost:6543/servers/asdf/boost', data={"vm_id":vm_id})
        return None

    @catch_disconnection
    def get_latest_specification(self, vm_id):
        r = requests.get('http://localhost:6543/servers/by_id/' + str(vm_id))
        vm_name = json.loads(r.text)['artifact_uuid']
        r = requests.get('http://localhost:6543/servers/' + vm_name + '/specification')
        return json.loads(r.text)['cores'], json.loads(r.text)['ram']

    @catch_disconnection
    def set_specification(self, vm_name, cores, ram):
        r = requests.post('http://localhost:6543/servers/' + vm_name + '/specification', data={"vm_id":vm_name, "cores": cores, "ram": ram})

    def kill(self):
        """
        Closes the session.
        """
