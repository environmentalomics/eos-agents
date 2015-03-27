from eos_agents import actions, db_client
from requests.exceptions import ConnectionError
from time import sleep

#A global list of all active agents.
all_agents = {}

def set_state_to_boosting(self, vm_id):
    """

    """
    session2 = db_client.DBSession(self.shared_username, self.shared_password)
    session2.set_state_to_boosting(vm_id)

def set_state_to_deboosting(self, vm_id):
    """

    """
    session2 = db_client.DBSession(self.shared_username, self.shared_password)
    session2.set_state_to_deboosting(vm_id)

def boost_vm_memory(self, vm_id):
    session2 = db_client.DBSession(self.shared_username, self.shared_password)
    cores, ram = session2.get_latest_specification(vm_id)
    actions.boost_vm_memory(vm_id, ram)

def boost_vm_cores(self, vm_id):
    session2 = db_client.DBSession(self.shared_username, self.shared_password)
    cores, ram = session2.get_latest_specification(vm_id)
    actions.boost_vm_cores(vm_id, cores)

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
    def __init__(self, trigger_state, action_list, success_state, error_state):

        global all_agents

        self.trigger_state = trigger_state
        self.action_list = action_list
        self.success_state = success_state
        self.error_state = error_state

#         self.shared_username = 'agent'
#         self.shared_password = 'asdf'

        #Add this agent to the global registry.
        all_agents[trigger_state] = self


    def wait_on_job(self, job_id):
        status = ""
        while status not in ['success', 'error', 'canceled', 'aborted']:
            status = actions.get_status(job_id)
        return status


    def dwell(self, session = None, persist=True):

        # Open DB Connection if none is provided.
        # Note that get_default_db_session examines sys.argv directly
        if session is None:
            session = db_client.get_default_db_session()

        while True:

            # Look for Machines in target state
            try:
                vm_id, uuid = session.get_machine_in_state(self.trigger_state)
            except ConnectionError:
                vm_id = None
                print("Connection error on DB."  +
                      ( " Will keep trying!" if persist else "") )

            if vm_id is not None:
                serveruuid = self.lookup_uuid(vm_id)
                if serveruuid != None:
                    print("Found action for server " + vm_id)
                    for job in self.action_list:

                        status_code, job_id = job(serveruuid) # Execute VM action
                        print("Waiting for response")
                        status = self.wait_on_job(job_id) # Wait for job to complete

                        if status == "success":
                            print("Success")
                            session.set_state(vm_id, self.success_state)    # Perform success action
                        elif status == "error":
                            print("Error")        # Flag machine as "alert" and return to previous state
                            session.set_state(vm_id, self.error_state)
                        elif status == "canceled":
                            print("Cancelled")    # Return machine state to previous state
                            session.set_state(vm_id, self.error_state)
                        elif status == "aborted":
                            print("Aborted")      # Return machine state to previous state
                            session.set_state(vm_id, self.error_state)
                        else:
                            print("Error: Status=" + str(status))
            else:
                if persist:
                    sleep(5)
                else:
                    break

"""

Start : Working
Stop: Working
Restart: Not Working
Prepare: -
Pre-Deboost: -

prepare_agent = Agent("Preparing", [actions.stop_vm], "Prepared", "Started")
predeboost_agent = Agent("Pre_Deboosting", [actions.stop_vm], "Pre_Deboosted", "Started")

boost_agent = Agent("Prepared", [set_state_to_boosting,
                                 boost_vm_memory,
                                 boost_vm_cores,
                                 ], "Starting", "Error")

deboost_agent = Agent("Pre_Deboosted", [set_state_to_deboosting,
                                 boost_vm_memory,
                                 boost_vm_cores,
                                 ], "Starting", "Error")


"""
