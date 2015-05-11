from eos_agents import actions, db_client
from requests.exceptions import ConnectionError
from time import sleep

# A global list of all active agents.
all_agents = {}

class JobException(Exception):
    pass

class Agent:
    """
    Agent is an abstract class.
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
    #Default sleep time, may be overridden or modified as needed
    sleep_time = 5

    def __init__(self):
        """All subclasses should ensure that this constructor is called, if they
           override __init__()
        """

        global all_agents

        # Add this agent to the global registry.
        if self.trigger_state:
            if self.trigger_state in all_agents :
                raise KeyError("You already have an agent registered to trigger on " +
                               self.trigger_state)
            else:
                all_agents[self.trigger_state] = self
        else:
            raise TypeError("Cannot instantiate anagent without a trigger_state. " +
                            "Are you trying to instantiate Agent() dirtectly?")

        #When an agent is acting, this will contain the UUID to act on.
        self.serveruuid = None
        self.vm_id = None

    def wait_on_job(self, job_id):
        status = ""
        while status not in ['success', 'error', 'canceled', 'aborted']:
            status = actions.get_status(job_id)
        return status

    def act():
        """Agents override this with what they want to do.  Actions on the server should
           be invoked by calls to self.do_action(action, *args) rather than by direct
           calls to action(server_uuid, args) so as to process the result status properly.
        """
        pass

    def dwell(self, session=None, persist=True):

        # Open DB Connection if none is provided.
        # Note that get_default_db_session examines sys.argv directly
        if session is None:
            session = db_client.get_default_db_session()

        while True:

            # Look for Machines in target state
            try:
                self.vm_id, self.serveruuid = session.get_machine_in_state(self.trigger_state)
            except ConnectionError:
                self.vm_id = None
                print("Connection error on DB." +
                      (" Will keep trying!" if persist else ""))

            if self.vm_id:
                if self.serveruuid:
                    print("Found action for server " + str(vm_id))
                    try:
                        self.act()
                    except:
                        #We might get various exceptions.  As far as I can see, all of them
                        #should just put the VM in the error state.
                        session.set_state(self.vm_id, self.failure_state)
                else:
                    #If there is no serveruuid then there is a database error and nothing more
                    #we can do with this server.
                    session.set_state(self.vm_id, "Error")
            else:
                if persist:
                    sleep(self.sleep_time)
                else:
                    break

    def do_action(job, *args):
        """This can be called by an Agents act() function to run a job on the server
           and monitor the result.  It needs to be passed a function from eos_agents.actions.
           The function will be run with serveruuid as the first parameter and will return a
           double of (status_code, job_id).  All the action functions should follow this spec.
        """
        if not self.serveruuid:
            #Only possible if do_action was called outside the regular dwell() loop.
            raise TypeError("self.serveruuid is not set")

        status_code, job_id = job(self.serveruuid, *args)  # Execute VM action
        print("Waiting for response")
        status = self.wait_on_job(job_id)  # Wait for job to complete

        if status == "success":
            #TODO - Ben's original plan was to report the progress of each action in
            #order to provide a more granular progress meter for the user.  We could emit
            #progress events here.
            #FIXME - this should be a log message
            print("Success")
            return status
        elif status in ("error", "canceled", "aborted"):
            #FIXME - this should be a log message, with more details for debugging
            print(status)  # Machine should now go to the failure_state
            raise JobException("%s - %s" % (self.serveruuid, status))
        else:
            print("Error: Status=" + str(status))

    def success():
        """Override this if the Agent needs to do something else on success
        """
        session.set_state(vm_id, self.success_state)

    def failure():
        """Override this if the Agent needs to clean up (eg. refund money) on
           failure.  You should not attempt any further actions on the VMs but may
           write to the database.
        """
        session.set_state(vm_id, self.failure_state)
