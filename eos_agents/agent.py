from eos_agents import actions, db_client
from requests.exceptions import ConnectionError
from time import sleep

# A global list of all active agents.
all_agents = {}

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

        self.sleep_time = 5

        # Add this agent to the global registry.
        all_agents[trigger_state] = self

    def wait_on_job(self, job_id):
        status = ""
        while status not in ['success', 'error', 'canceled', 'aborted']:
            status = actions.get_status(job_id)
        return status

    def dwell(self, session=None, persist=True):

        # Open DB Connection if none is provided.
        # Note that get_default_db_session examines sys.argv directly
        if session is None:
            session = db_client.get_default_db_session()

        while True:

            # Look for Machines in target state
            try:
                vm_id, serveruuid = session.get_machine_in_state(self.trigger_state)
            except ConnectionError:
                vm_id = None
                print("Connection error on DB." +
                      (" Will keep trying!" if persist else ""))

            if vm_id:
                if serveruuid:
                    print("Found action for server " + str(vm_id))
                    for job in self.action_list:
                        try:
                            status_code, job_id = job(serveruuid)  # Execute VM action
                            print("Waiting for response")
                            status = self.wait_on_job(job_id)  # Wait for job to complete

                            if status == "success":
                                print("Success")
                                session.set_state(vm_id, self.success_state)  # Perform success action
                            elif status == "error":
                                print("Error")  # Flag machine as "alert" and return to previous state
                                session.set_state(vm_id, self.error_state)
                            elif status == "canceled":
                                print("Cancelled")  # Return machine state to previous state
                                session.set_state(vm_id, self.error_state)
                            elif status == "aborted":
                                print("Aborted")  # Return machine state to previous state
                                session.set_state(vm_id, self.error_state)
                            else:
                                print("Error: Status=" + str(status))
                        except KeyError:
                            session.set_state(vm_id, self.error_state)
                else:
                    session.set_state(vm_id, self.error_state)
            else:
                if persist:
                    sleep(self.sleep_time)
                else:
                    break
