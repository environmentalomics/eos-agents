"""
db_api_client: Routines to call to the DB API

The most recent HTTP result code is held in the variable "last_status", which
is initially set to -1. 
"""
class DBSession():
    """
    
    """    
    def __init__(self, username, password):
        """
        
        """
        self.last_status = -1
        pass
    
    def get_next_pre_stop(self):
        """
        """
        return vm_id
    
    def get_next_pre_start(self):
        """
        """
        return vm_id
    
    def get_next_pre_reset(self):
        """
        """
        return vm_id
    
    def get_next_pre_decommission(self):
        """
        """
        return vm_id
    
    def set_state(self, vm_id, state_id):
        """
        """
        return status
    
    def kill(self):
        """
        Closes the session.
        """
