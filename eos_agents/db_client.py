"""
db_api_client: Routines to call to the DB API

The most recent HTTP result code is held in the variable "last_status", which
is initially set to -1.
"""

import sys
import requests, json

def catch_disconnection(dbfunc):
    def safe_function(*args):
        try:
            return dbfunc(*args)
        except requests.exceptions.ConnectionError:
            return None
    return safe_function


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

    def request_get(self, *args):
        result = requests.get(*args, auth=(self.username, self.password))
        self.last_status = result.status_code
        return result

    def request_post(self, *args):
        result = requests.post(*args, auth=(self.username, self.password))
        self.last_status = result.status_code
        return result

    @catch_disconnection
    def get_triggers(self, trigger):
        """Gets a list of all servers in the trigger state specified.

        :param trigger: Plaintext of the trigger which we are searching for.
        :returns: List of vm ids.
        """
        r = requests.get(self.db_url + '/states?state=' + trigger)
        serverlist = r.keys
        return serverlist

    @catch_disconnection
    def get_prestart_item(self):
        r = requests.get(self.db_url + '/states/Starting')
        return r.text

    @catch_disconnection
    def get_restart_item(self):
        r = requests.get(self.db_url + '/states/Restarting')
        return r.text

    @catch_disconnection
    def get_prestop_item(self):
        r = requests.get(self.db_url + '/states/Stopping')
        return r.text

    @catch_disconnection
    def get_prepare_item(self):
        r = requests.get(self.db_url + '/states/Preparing')
        return r.text

    @catch_disconnection
    def get_boost_item(self):
        r = requests.get(self.db_url + '/states/Prepared')
        return r.text

    @catch_disconnection
    def get_auto_deboost_item(self):
        r = requests.get(self.db_url + '/states/boostexpired')
        return r.text

    @catch_disconnection
    def get_manual_deboost_item(self):
        r = requests.get(self.db_url + '/states/Deboosting')
        return r.text

    @catch_disconnection
    def get_predeboost_item(self):
        r = requests.get(self.db_url + '/states/Pre_Deboosting')
        return r.text

    @catch_disconnection
    def set_state_to_predeboosted(self, vm_id):
        """

        """
        r = requests.post(self.db_url + '/servers/%s/pre_deboosted' % vm_id)
        return None

    @catch_disconnection
    def set_state(self, vm_id, state):
        r = requests.post(self.db_url + '/servers/%s/' + state % vm_id)

    @catch_disconnection
    def set_state_to_deboosting(self, vm_id):
        """

        """
        r = requests.post(self.db_url + '/servers/%s/Deboosting' % vm_id)
        return None

    @catch_disconnection
    def get_deboost_item(self):
        r = requests.get(self.db_url + '/states/Pre_Deboosted')
        return r.text

    def get_machine_in_state(self, state):
        r = self.request_get(self.db_url + "/states/" + state + "?state=" + state)
        return json.loads(r.text)['artifact_id'], json.loads(r.text)['artifact_uuid']


    def get_machine_state_counts(self):
        # TODO, call Ben's new API call here
        r = self.request_get(self.db_url + "/states/" + "asdf" + "asdf")
        return json.loads(r.text)

    @catch_disconnection
    def set_state_to_deboosted(self, vm_id):
        """

        """
        r = requests.post(self.db_url + '/servers/%s/Deboosted' % vm_id)
        return None

    @catch_disconnection
    def set_state_to_stopped(self, vm_id):
        """

        """
        r = requests.post(self.db_url + '/servers/%s/stopped' % vm_id)
        return None

    @catch_disconnection
    def set_state_to_started(self, vm_id):
        """

        """
        r = requests.post(self.db_url + '/servers/%s/started' % vm_id)
        return None

    @catch_disconnection
    def set_state_to_prepared(self, vm_id):
        """

        """
        r = requests.post(self.db_url + '/servers/%s/prepared' % vm_id)
        return None

    @catch_disconnection

    def get_name(self, vm_id):
        r = requests.get(self.db_url + '/servers/by_id/%s' % vm_id)
        return json.loads(r.text)['artifact_uuid']

    @catch_disconnection
    def set_state_to_starting(self, vm_id):
        """

        """
        r = requests.post(self.db_url + '/servers/%s/start' % vm_id)
        return None

    @catch_disconnection
    def set_state_to_boosting(self, vm_id):
        """

        """
        r = requests.post(self.db_url + '/servers/%s/boost' % vm_id)
        return None

    @catch_disconnection
    def get_latest_specification(self, vm_id):
        r = requests.get(self.db_url + '/servers/by_id/%s' % vm_id)
        vm_name = json.loads(r.text)['artifact_uuid']
        r = requests.get(self.db_url + '/servers/' + vm_name + '/specification')
        return json.loads(r.text)['cores'], json.loads(r.text)['ram']

    @catch_disconnection
    def set_specification(self, vm_name, cores, ram):
        r = requests.post(self.db_url + '/servers/' + vm_name + '/specification', data={"vm_id":vm_name, "cores": cores, "ram": ram})

    def kill(self):
        """
        Closes the session.
        """
