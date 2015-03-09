"""
db_api_client: Routines to call to the DB API

The most recent HTTP result code is held in the variable "last_status", which
is initially set to -1. 
"""

import requests, json

class DBSession():
    """
    
    """    
    def __init__(self, username, password):
        """
        
        """
        self.last_status = -1
    
    def get_triggers(self, trigger):
        """Gets a list of all servers in the trigger state specified.
                
        :param trigger: Plaintext of the trigger which we are searching for.
        :returns: List of vm ids.
        """
        r = requests.get('http://localhost:6543/states?state=' + trigger)
        serverlist = r.keys
        return serverlist
    
    def get_prestart_item(self):
        r = requests.get('http://localhost:6543/states/Starting?state=Starting')
        return r.text
    
    def get_restart_item(self):
        r = requests.get('http://localhost:6543/states/Restarting?state=Restarting')
        return r.text
    
    def get_prestop_item(self):
        r = requests.get('http://localhost:6543/states/Stopping?state=Stopping')
        return r.text
    
    def get_prepare_item(self):
        r = requests.get('http://localhost:6543/states/Preparing?state=Preparing')
        return r.text
    
    def get_prepared_item(self):
        pass
    
    def get_boost_item(self):
        r = requests.get('http://localhost:6543/states/prepared?state=Prepared')
        return r.text
    
    def get_auto_deboost_item(self):
        r = requests.get('http://localhost:6543/states/boostexpired')
        return r.text
        
    def get_manual_deboost_item(self):
        r = requests.get('http://localhost:6543/states/deboosting?state=Deboosting')
        return r.text
    
    def get_predeboost_item(self):
        r = requests.get('http://localhost:6543/states/pre_deboosting?state=Pre_Deboosting')
        return r.text
    
    def set_state_to_predeboosted(self, vm_id):
        """
        
        """
        r = requests.post('http://localhost:6543/servers/asdf/pre_deboosted', data={"vm_id":vm_id})
        return None
    
    def set_state_to_deboosting(self, vm_id):
        """
        
        """
        r = requests.post('http://localhost:6543/servers/asdf/Deboosting', data={"vm_id":vm_id})
        return None
        
    def get_deboost_item(self):
        r = requests.get('http://localhost:6543/states/Pre_Deboosted?state=Pre_Deboosted')
        return r.text
        
    def set_state_to_deboosted(self):
        """
        
        """
        r = requests.post('http://localhost:6543/servers/asdf/deboosted', data={"vm_id":vm_id})
        return None
        
    def set_state_to_stopped(self, vm_id):
        """
        
        """
        r = requests.post('http://localhost:6543/servers/asdf/stopped', data={"vm_id":vm_id})
        return None
    
    def set_state_to_started(self, vm_id):
        """
        
        """
        r = requests.post('http://localhost:6543/servers/asdf/started', data={"vm_id":vm_id})
        return None
    
    def set_state_to_prepared(self, vm_id):
        """
        
        """
        r = requests.post('http://localhost:6543/servers/asdf/prepared', data={"vm_id":vm_id})
        return None
    
    def get_name(self,vm_id):
        r = requests.get('http://localhost:6543/servers/by_id/' + str(vm_id))
        return json.loads(r.text)['artifact_uuid']
    
    def set_state_to_starting(self, vm_id):
        """
        
        """
        r = requests.post('http://localhost:6543/servers/asdf/start', data={"vm_id":vm_id})
        return None
    
    def set_state_to_boosting(self, vm_id):
        """
        
        """
        r = requests.post('http://localhost:6543/servers/asdf/boost', data={"vm_id":vm_id})
        return None
    
    def get_latest_specification(self, vm_id):
        r = requests.get('http://localhost:6543/servers/by_id/' + str(vm_id))
        vm_name = json.loads(r.text)['artifact_uuid']
        r = requests.get('http://localhost:6543/servers/' + vm_name + '/specification')
        return json.loads(r.text)['cores'], json.loads(r.text)['ram']
    
    def set_specification(self, vm_name, cores, ram):
        r = requests.post('http://localhost:6543/servers/' + vm_name + '/specification', data={"vm_id":vm_name, "cores": cores, "ram": ram})
    
    def kill(self):
        """
        Closes the session.
        """
