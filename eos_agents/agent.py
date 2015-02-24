import actions, updates, db_client
from time import sleep

class Agent():
    """
    An agent performs activities within the system as follows:
    
    1.    Regularly polls the DB API to check for artifacts which are in a
          state which requires their action.
    2.    If this is the case, carries out the series of actions as defined
          by the agent's class.
    3.    Having performed this series of actions, updates the API to a new
          state.
          
    As such, each agent should have a trigger state, and a list of functions to
    perform on the artifact identified.
    
    """
    def __init__(self, trigger, actions, success_state, error_state):
        self.trigger = trigger
        self.actions = actions
        self.success_state = success_state
        self.error_state = error_state

    def get_triggers(self):
        server_list = updates.get_triggers(self.trigger)
        return server_list
    
    def set_status(self, server, status):
        result = updates.set_status(server, status)
        return result
    
    def get_status(self, server_id):
        """
        Get latest status of vCloud action pushed to Director.
        
        Assumes that a job id has been assigned to the server.
        """
        result = actions.get_status(server_progress[server]['job_id'])
        return result
    
    def lookup_uuid(self, id):
        if id == '1':
            return 'asd'
        if id == '2':
            return 'vm-99d7ee8d-69a2-4eaa-a332-11b5413ca827'
        if id == '3':
            return 'asd'
        return None
    
    def startservice(self):
        session = db_client.DBSession('roger','asdf')
        while True:
            vm_id = session.get_prestart_item()
            if vm_id != None:
                serveruuid = self.lookup_uuid(vm_id)
                if serveruuid != None:
                    try:
                        status, job_id = actions.start_vm(serveruuid)
                        self.wait_on_job(job_id)
                        session.set_state_to_started(vm_id)
                    except:
                        print "Server UUID not found"
            sleep(5)
        
    def stopservice(self):
        session = db_client.DBSession('roger','asdf')
        while True:
            vm_id = session.get_prestop_item()
            if vm_id != None:
                serveruuid = self.lookup_uuid(vm_id)
                if serveruuid != None:
                    try:
                        status, job_id = actions.stop_vm(serveruuid)
                        print ("Stopping vm: " + serveruuid + ". Job: " + job_id + '. HTTP result ' + status + '.')
                        self.wait_on_job(job_id)
                        session.set_state_to_stopped(vm_id)
                    except:
                        pass
            sleep(5)
    
    def prepareservice(self):
        session = db_client.DBSession('roger','asdf')
        while True:
            vm_id = session.get_prepare_item()
            if vm_id != None:
                serveruuid = self.lookup_uuid(vm_id)
                if serveruuid != None:
                    try:
                        status, job_id =  actions.stop_vm(serveruuid)
                        self.wait_on_job(job_id)
                        session.set_state_to_prepared(vm_id)
                    except:
                        print "Server UUID not found"
            sleep(5)
    
    def boostservice(self):
        session = db_client.DBSession('roger','asdf')
        while True:
            vm_id = session.get_boost_item()
            if vm_id != None:
                serveruuid = self.lookup_uuid(vm_id)
                if serveruuid != None:
                    try:
                        cores, ram = session.get_latest_specification(vm_id)
                        print("Latest spec: " + str(cores) + " cores, " + str(ram) + "GB RAM.")
                                                
                        session.set_state_to_boosting(vm_id)
                        
                        status, job_id = actions.boost_vm_memory(serveruuid, ram)
                        print ("Boosting vm RAM: " + str(serveruuid) + ". Job: " + str(job_id) + '. HTTP result ' + str(status) + '.')
                        self.wait_on_job(job_id)
                        
                        status, job_id = actions.boost_vm_cpu(serveruuid, cores)
                        print ("Boosting vm CPU: " + str(serveruuid) + ". Job: " + str(job_id) + '. HTTP result ' + str(status) + '.')
                        self.wait_on_job(job_id)
                        
                        session.set_state_to_starting(vm_id)
                    except:
                        print "Server UUID not found"
            sleep(5)
    
    def wait_on_job(self, job_id):
        status = ""
        while status not in ['success', 'error', 'canceled', 'aborted']:
            status = actions.get_status(job_id)
        
    def run(self):
        """
        This is the main loop which operates the agent, checking for triggers
        and executing API calls.
        
        Each time the loop repeats, the agent queries the DB API for a list of
        servers in the appropriate trigger state.
        
        If it already knows about the server, it will attempt to get an update
        on progress from the vCloud API, and move to the next function if that
        previous function was completed.
        
        If all functions are completed, it will update the DB API with its
        success state. If an error occurs at any point, it will set the
        DB API state of the VM to the given error state.
        
        """
        server_progress = {}
        while True:
            triggers = self.get_triggers()
            for server in triggers:
                sleep(0)
                if server in server_progress:
                    if self.get_status(server_progress[server]) == 100:
                        server_progress[server] += 1
                        if self.functions[server_progress[server]]:
                            result = self.functions[server_progress[server]]
                            if result == -1:
                                self.set_status(server, self.error_status)
                        else:
                            self.set_status(server, self.success_status)
                else:
                    server_progress[server] = 0
                    result = self.functions[server_progress[server]]
                    if result == -1:
                        self.set_status(server, self.error_status)
            

class Start(Agent):
    """
    The Start Agent looks for devices in a state of "Pre-Start" and starts
    them, before setting their status to "Started".
    """
    def __init__(self):
        Agent.__init__(self, "Pre-Start", [actions.start_vm], "Started", "Error (Start)")
    
class Stop(Agent):
    """
    The Stop Agent looks for devices in a state of "Pre-Stop" and stops them,
    before setting their status to "Stopped".
    """
    def __init__(self):
        Agent.__init__(self, "Pre-Stop", [actions.stop_vm], "Stopped", "Error (Stop)")

class Boost(Agent):
    def __init__(self):
        Agent.__init__("Pre-Boost", 
                       [actions.stop_vm, 
                        actions.boost_vm, 
                        actions.start_vm], 
                       "Boosted", 
                       "Error (Boost)")

class Provision(Agent):
    pass
    
class Delete(Agent):
    pass
    
class Check(Agent):    
    pass