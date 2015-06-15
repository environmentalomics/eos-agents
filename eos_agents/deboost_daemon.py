from eos_agents import db_client
from time import sleep

import logging
log = logging.getLogger(__name__)
#Used to suppress multiple warnings on failed DB connection:
fail_flag = False

class Daemon():
    """
    This daemon is a bit like an agent, in that it waits for a VM to be in a certain
    state within eos_db and then acts on it, changing the state in the database.
    But that's where the similarity ends:

    1. The daemon triggers based on the presence of an expired or expiring boost,
       not on a specific trigger state.
    2. The daemon does not talk to VCloud at all, only the database
    3. As such, the daemon has no error state, but it may fail to deboost the machine
       if the API rejects the request
    4. The daemon is responsible for reporting things back to the user.  In fact,
       this is most of the functionality.
    5. The daemon would like to remember what messages it sent, even if it is restarted.
       This is tricky.

    Since there is only one daemon in the system I will not attempt to abstract it.
    """

    def __init__(self):

        # Only act on the VM if it is in one of these states...
        self.init_states = set(( 'Stopped', 'Started' ))
        # Putting the machine into this state automatically resets the
        # specification.
        self.success_state = 'Pre_Deboosting'

        # Look for jobs every 15 seconds, seems sensible
        self.sleep_time = 15

        # If a machine is more that 2 hours late for deboost, don't touch it
        self.ignore_after = 2 * 60

        # Warn the user with 24 hours to go and then at 1 hour.  This needs a lot of
        # coding to make it work, not least a way to remember who I warned about what.
        # Or do I just need to remember the time of the last message I sent??
        self.warn_at([24 * 60, 1 * 60])

    def warn_at(self, mins_array):
        # Need to work out how best to do this.
        self._warn_at = mins_array

    def lurk(self, session=None, persist=True):

        global fail_flag

        # As with agents:
        # Open DB Connection if none is provided.
        # Note that get_default_db_session examines sys.argv directly
        if session is None:
            session = db_client.get_default_db_session()
        self.session = session

        while True:

            # Look for Machines in expired state.  The API call returns an array of dicts:
            # [dict(boost_remain=123, artifact_id=44, artifact_name='baz'), ...]
            # where boost_remain is in seconds.
            exp = ()
            try:
                exp = session.get_deboost_jobs(past=self.ignore_after, future=0)
                fail_flag = False
            except (db_client.ConnectionError, ValueError):
                if not fail_flag:
                    log.warning("Connection error on DB in Deboost Daemon." +
                                (" Will keep trying!" if persist else ""))
                    fail_flag = True

            # Deal with all the machines in a loop, we probably only got one but you never
            # know.
            for vm in exp:
                vm_id = vm['artifact_id']

                try:
                    #Back off if the server is in the middle of something.  Yes, this is racey but it
                    #should be OK.  We're assuming the server will transition back to a stable state
                    #very soon and then we'll go and Deboost it.
                    old_state = session.get_state(vm_id)
                    if old_state not in self.init_states:
                        raise Exception("Refusing to de-boost a server in state %s." % old_state)

                    #Do it.
                    session.set_state(vm_id, self.success_state)

                    log.info("De-Boosted VM %s" % vm)

                    try:
                        self.tell_user_vm_deboosted(vm)
                    except:
                        log.warning("Failed to inform user about the de-boost action.")

                except Exception as e:
                    log.warning("Server %s did not deboost: %s" % (vm_id, e))

            if persist:
                sleep(self.sleep_time)
            else:
                break

    #FIXME - once this is working, split the text into settings.py
    def tell_user_vm_deboosted(self, vm):

        user = session.get_user_for_machine(vm)
        user_email = session.get_email_for_user(user)

        subject = "EOS Cloud Automatic Alert: %s boost period ended" % vm
        body = "Dear " + user + """,
Your virtual machine is being automatically restored to baseline hardware specification,
as the configured boost period has ended.
In order to do this, the system will be restarted immediately.

You may now continue to use your system as normal.  If you have any problems please contact
the system support address.

    Regards,

    The EOS Cloud Team
"""

        send_ze_mail(user_email, subject, body)

    def tell_user_vm_will_deboost(self, vm):
        pass

        class MessageCache():
            def __init__():
                pass


deboost_daemon = Daemon()
def lurk(*args, **kwargs):
    deboost_daemon.lurk(*args, **kwargs)

if __name__ == '__main__':
        #If the agents dwell() then maybe a daemon does this...
        logging.basicConfig(format="%(levelname)1.1s: %(message)s",
                            level = logging.DEBUG)
        lurk()
