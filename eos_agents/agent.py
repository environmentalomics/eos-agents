from eos_agents import actions, db_client, all_agents
from time import sleep

import logging
log = logging.getLogger(__name__)

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
    #Delay when polling for updates from VCD
    poll_time = 2

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
        """Keep asking VCD about the job until we get a result.
        """
        status = actions.get_status(job_id)
        while status not in ['success', 'error', 'canceled', 'aborted']:
            sleep(self.poll_time)
            status = actions.get_status(job_id)
        return status

    def act(self):
        """Agents override this with what they want to do.  Actions on the server should
           be invoked by calls to self.do_action(action, *args) rather than by direct
           calls to action(server_uuid, args) so as to process the result status properly.
        """
        pass

    def dwell(self, session=None, persist=True):

        #This should only be applied if no logging was already set - ie. the agent is
        #being run directly and not via the controller.
        logging.basicConfig(format="%(levelname)4.4s@%(asctime)s | %(message)s | %(name)s",
                            datefmt="%H:%M:%S",
                            level = logging.DEBUG)

        # Guess params for DB Connection if none is provided.
        # Note that get_default_db_session examines sys.argv directly
        # Also note if you want to re-use the old session you explicitly need to call
        # my_agent.dwell(session = my_agent.session )
        if session is None:
            session = db_client.get_default_db_session()
        self.session = session

        # This will store the VMs we need to work on, as returned by get_machines_in_state
        # In the original design we just got the first VM, but this is a problem if that VM
        # gets jammed in some particular state and we just keep retrying it, never moving on
        # to any others that want attention.
        queue = []

        while True:

            # Look for Machines in target state
            try:
                self.vm_id = None
                if not queue:
                    queue = session.get_machines_in_state(self.trigger_state)
                #Having maybe fetched new items, try again.
                if queue:
                    i = queue.pop(0)
                    self.vm_id, self.serveruuid = i["artifact_id"], i["artifact_uuid"]
            except db_client.ConnectionError:
                log.warning("Connection error on DB." +
                            (" Will keep trying!" if persist else ""))

            if self.vm_id:
                if self.serveruuid:
                    log.debug("Found action for server " + str(self.vm_id))
                    try:
                        self.act()
                    except Exception as e:
                        #We might get various exceptions.  As far as I can see, all of them
                        #should call the failure() handler.
                        log.debug("Exception: %s", e)
                        self.failure()
                    #The point of this 'if' is that should setting the status fail for some
                    #reason we at least take a pause before racing round to repeat the action.
                    if self.success():
                        continue
                else:
                    #If there is no serveruuid then there is a database error and nothing more
                    #we can do with this server.
                    session.set_state(self.vm_id, "Error")

            #If we ran out of jobs, or if something failed, either pause or quit.
            if persist:
                sleep(self.sleep_time)
            else:
                break

    def do_action(self, job, *args):
        """This can be called by an Agents act() function to run a job on the server
           and monitor the result.  It needs to be passed a function from eos_agents.actions.
           The function will be run with serveruuid as the first parameter and will return a
           double of (status_code, job_id).  All the action functions should follow this spec.
        """
        if not self.serveruuid:
            #Only possible if do_action was called outside the regular dwell() loop.
            raise TypeError("self.serveruuid is not set")

        status_code, job_id = job(self.serveruuid, *args)  # Execute VM action
        log.debug("Waiting for response on job " + str(job_id))
        status = self.wait_on_job(job_id)  # Wait for job to complete

        if status == "success":
            #TODO - Ben's original plan was to report the progress of each action in
            #order to provide a more granular progress meter for the user.  We could emit
            #progress events here.
            log.debug("Success on job " + str(job_id))
            return status
        elif status in ("error", "canceled", "aborted"):
            #FIXME - this should be a log message, with more details for debugging
            log.debug(status + " on job " + str(job_id))  # Machine should now go to the failure_state
            raise JobException("%s - %s" % (self.serveruuid, status))
        else:
            print("Error: Status=" + str(status))

    def success(self):
        """Override this if the Agent needs to do something else on success
        """
        self.session.set_state(self.vm_id, self.success_state)

    def failure(self):
        """Override this if the Agent needs to clean up (eg. refund money) on
           failure.  You should not attempt any further actions on the VMs but may
           write to the database.
        """
        self.session.set_state(self.vm_id, self.failure_state)
