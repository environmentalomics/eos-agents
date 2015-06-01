"""
db_api_client: Routines to call to the DB API, normally on port 6543

The most recent HTTP result code is held in the variable "last_status", which
is initially set to -1.
"""

import sys
import requests
import logging

#Clients can import and trap this without caring that it belongs to requests under
#the hood.
ConnectionError = requests.exceptions.ConnectionError

log = logging.getLogger(__name__)

#I don't need all the chatter from requests, even if the root logger is set to
#debugging.
logging.getLogger('requests').setLevel(logging.ERROR)

def catch_disconnection(dbfunc):
    """Ben called this 'safe_function' but clearly this was a typo as swallowing
       an exception is not a 'safe' thing to do."""
    def unsafe_function(*args):
        try:
            return dbfunc(*args)
        except requests.exceptions.ConnectionError:
            return None
    return unsafe_function


def get_default_db_session():
        """ Contructs a default DB session by looking at how the program was
            invoked.
            It examines sys.argv directly.  If this is no good, create the session
            externally.
        """

        # If no shared secret is set, assume that the server is running in test mode.
        shared_username = 'agent'
        shared_password = 'test'

        # This is probably extraeous, but useful if we need to run just
        # single agent:
        # $ python3 pre_deboost.py ss=/var/run/mysecret
        db_url = None  # Will default to http://localhost:6543

        for arg in sys.argv[1:]:
            if arg.startswith('ss='):
                with open(arg.split('=', 1)[1]) as ssfile:
                    shared_password = ssfile.read().rstrip('\n')
            elif arg.startswith('url='):
                db_url = arg.split('=', 1)[1]

        return DBSession(shared_username, shared_password, db_url)

class DBSession():
    """ Represents communication with the eos-db which is normally running on
        localhost:6543.  Agents have privileged access to the database which they
        obtain by use of a shared secret (username+password) generated at runtime.
    """
    def __init__(self, username, password, db_url=None):

        """
        Set "Last Status" to -1, to indicate that no database calls have occured yet.
        """
        self.last_status = -1
        self.username = username
        self.password = password
        self.db_url = db_url or 'http://localhost:6543'

        log.debug("Starting DB session on %s:%s@%s" %
                   ( self.username, '*' * len(self.password), self.db_url ))


    def get(self, *args):
        newargs = ( self.db_url + args[0], ) + args[1:]
        log.debug("GET from " + str(newargs))
        result = requests.get(*newargs, auth=(self.username, self.password))
        self.last_status = result.status_code
        #For my purposes I expect a 200 response every time
        if result.status_code not in range(200,207):
            raise ValueError("HTTP error response")
        return result

    def post(self, *args):
        newargs = ( self.db_url + args[0], ) + args[1:]
        log.debug("POST to " + str(newargs))
        result = requests.post(*newargs, auth=(self.username, self.password))
        self.last_status = result.status_code
        return result

    #FIXME - I suspect this connects to nothing in the DB
    #FIXME 2 - I need a list back
    @catch_disconnection
    def get_auto_deboost_item(self):
        return self.get('/states/boostexpired').json()

    def get_machine_state_counts(self):
        # TODO, call Ben's new API call here
        return self.get("/states").json()

    #Gets all the servers currently in the requested state.
    def get_machines_in_state(self, state):
        return self.get("/states/" + state).json()

    #FIXME - This should fail if the VM is not in a de-boostable state, just as it
    # should when a manual deboost is tried on a machine not ready to be deboosted.
    def do_deboost(self, vm_id):
        """Puts the given machine into state PreDeboosting so that the agents
           will come along and deboost it"""
        r = self.post('/servers/%s/%s' % (vm_id, 'PreDeboosting'))
        if r.status_code not in range(200,207):
            raise Exception("Some Error???")
        return r

    #If this fails, the agent will just end up triggering again, and this should be fine,
    #as long as there is not a tight loop.
    def set_state(self, vm_id, state):
        """Sets the state of the VM in the database.  Returns True on success, False
           on failure and None if there was a netowrk error.
        """
        r = None
        try:
            r = self.post('/servers/by_id/%s/%s' % (vm_id, state))
        except ConnectionError:
            return None
        return (r.status_code in range(200,207))


    def get_uuid(self, vm_id):
        return (self.get('/servers/by_id/%s' % vm_id).json())['artifact_uuid']


    @catch_disconnection
    def get_latest_specification(self, vm_id):
        r = self.get('/servers/by_id/%s/specification' % vm_id).json()
        return r['cores'], r['ram']

    @catch_disconnection
    def set_specification(self, vm_id, cores, ram):
        r = self.post('/servers/by_id/%s/specification' % vm_id,
                      data={"cores": cores, "ram": ram})

    def kill(self):
        """
        Closes the session.  Nothing to do, since the API is stateless and we are not
        using token-based auth.
        """
