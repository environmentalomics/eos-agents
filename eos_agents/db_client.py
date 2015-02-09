"""
db_api_client: Routines to call to the DB API

The most recent HTTP result code is held in the variable "last_status", which
is initially set to -1. 
"""

import requests

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
    
    def get_prestop_item(self):
        r = requests.get('http://localhost:6543/states/Stopping?state=Stopping')
        return r.text
    
    def set_state(self, vm_id, state_id):
        """
        """
        return None
    
    def kill(self):
        """
        Closes the session.
        """
