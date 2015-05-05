from eos_agents import db_client
from requests.exceptions import ConnectionError
from time import sleep

import logging
log = logging.getLogger(__name__)

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
    5. The daemon has to remember what messages it sent.  This is tricky.

    Since there is only one daemon in the system I will not attempt to abstract it.
    """

    def __init__(self):

        # This doesn't really apply to the Daemon as it does not trigger by state:
        # self.init_states = ( 'Stopped', 'Started' )
        # self.success_state = 'Pre_Deboosting'
        self.sleep_time = 5

        # Warn the user with 24 hours to go and then at 1 hour.  This needs a lot of
        # coding to make it work, not least a way to remember who I warned about what.
        self.warn_at([24 * 60, 1 * 60])

    def lurk(self, session=None, persist=True):

        # As with agents:
        # Open DB Connection if none is provided.
        # Note that get_default_db_session examines sys.argv directly
        if session is None:
            session = db_client.get_default_db_session()

        while True:

            # Look for Machines in expired state
            # TODO - implement this as a view, with agent permissions
            exp = list(session.get_auto_deboost_items())

            # Deal with all the machines in a loop, since there is a small possibility
            # one might fail and we don't want to then ignore the others.
            for vm in exp:

                try:
                    session.do_deboost(vm)

                    log.info("De-Boosted VM %s" % vm)

                    self.tell_user_vm_deboosted(vm)

                except Exception as e:
                    log.warning("VM %s did not deboost: %s" (v, e))

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

if __name__ == '__main__':
        #If the agents dwell() then maybe a daemon does this...
        logging.basicConfig(format="%(levelname)1.1s: %(message)s",
                            level = logging.DEBUG)
        deboost_daemon.lurk()
