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


    def get(self, url, **kwargs):
        newurl = self.db_url + url
        log.debug("GET from " + newurl + " with args " + str(kwargs))
        result = requests.get(newurl, auth=(self.username, self.password), **kwargs)
        self.last_status = result.status_code
        #For my purposes I expect a 200 response every time
        if result.status_code not in range(200,207):
            raise ValueError("HTTP error response")
        return result

    def post(self, url, **kwargs):
        newurl = self.db_url + url
        log.debug("POST to " + newurl + " with args " + str(kwargs))
        result = requests.post(newurl, auth=(self.username, self.password), **kwargs)
        self.last_status = result.status_code
        return result

    def get_machine_state_counts(self):
        # TODO, call Ben's new API call here
        return self.get("/states").json()

    #Gets all the servers currently in the requested state.
    def get_machines_in_state(self, state):
        return self.get("/states/" + state).json()

    #Gets deboost jobs
    def get_deboost_jobs(self, **kwargs):
        return self.get("/deboost_jobs", params=kwargs).json()

    #Check the state of a server
    def get_state(self, vm_id):
        """Gets the current state of a VM.  Only the deboost_daemon actually uses this.
        """
        return self.get("/servers/by_id/%s/state" % vm_id).json()

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


    def get_latest_specification(self, vm_id):
        r = self.get('/servers/by_id/%s/specification' % vm_id).json()
        return r['cores'], r['ram']

    def kill(self):
        """
        Closes the session.  Nothing to do, since the API is stateless and we are not
        using token-based auth.
        """
