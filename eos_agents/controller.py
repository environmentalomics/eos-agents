#!python3

# This will eventually be merged with control.py to make an actuall job controller.
# Having worked out the timing aspects, here is what I need to do now:
#  1) Obtain the shared secret
#  2) Obtain a connection to the eos-db
#  3) Work out which job runners I have available and be ready to run them
#  4) Ask the database what jobs are pending
#  5) Merge control.py


import os
import signal
import argparse
import logging
from sys import exit
# Prior to python3.3 we could instead 'import time as clock'
from time import sleep, monotonic as clock
# This requires the python3-setproctitle DEB pakage installed.
# In Perl you just assign to $0, cos Perl is awesome.
try:
    from setproctitle import setproctitle
except ImportError:
    setproctitle = lambda t: None

# Global state
from eos_agents import db_client
from eos_agents.agent import all_agents
jobs_running = {}

# And import all the agents.  Could attempt to 'discover' them but that leads to other
# problems, so if you add a new agent than add it to the list.
from eos_agents import (
            boost,
            deboost,
            predeboost,
            prepare,
            restart,
            start,
            stop ,
)

log = logging.getLogger(__name__)

def main():

    long_help = (
        "Note that connection settings to vCD must be supplied in settings.py" +
        "and cannot be set on the command-line."
    )

    parser = argparse.ArgumentParser(description='Start eos-agents master controller.',
                                     epilog=long_help)

    parser.add_argument('-l', '--list',        help='List all active agents and quit', action='store_true')
    parser.add_argument('-d', '--dry-run',     help='List all pending actions and quit', action='store_true')
    parser.add_argument('-s', '--secretfile',  help='Say where the shared secret is kept')
    parser.add_argument('-u', '--url',         help='Explicitly set the base URL for eos-db calls')
    parser.add_argument('-p', '--poll-interval', help='Set the poll interval in seconds', default="5")
    parser.add_argument('-q', '--quiet',       help='Suppress most messages', action='store_true')

    args = parser.parse_args()

    if args.list:
        for k, v in all_agents.items():
            print( "%s  => %s" % (k, v.success_state) )
        exit()

    logging.basicConfig(format="%(levelname)1.1s: %(message)s",
                        level = (logging.WARNING if args.quiet else logging.INFO))

    shared_password = 'test'
    if args.secretfile:
        with args.secretfile as ssfile:
            shared_password=ssfile.read().rstrip('\n')
    else:
        log.warning("Warning - using password '%s'.  Use -s <secretfile> to provide a proper one." % shared_password)


    ### Get a handle on the eos-db

    # Could do this, but I want to process argv explicitly here
    #db_session = db_client.get_default_db_session()

    db_session = db_client.DBSession('agent', shared_password, args.url)

    if args.dry_run:
        for a in get_required_actions():
            log.info("Starting agent for %s" % a)

    ## Start the main loop
    # TODO - allow clean exit on Ctrl+C

    poll_interval = int(args.poll_interval)

    try:
        while True:
            for a in get_required_actions(db_session):
                start_job("eos-agents - %s" % a, all_agents[a].dwell,
                          session=db_session, persist=False)

            sleep_n_reap(poll_interval)

    except KeyboardInterrupt:
        #Catch this so that cleanup gets called.
        pass

    #Do this before quitting
    reap_all_jobs()

def get_required_actions(db_session):
    """Queries the eos-db for what needs doing.  The eos-db return a JSON dict
       of status=>count.  Where the count > 0 and where I have a suitable agent to
       process the work I will return the agent name.
    """

    # status_table = db_session.get_machine_state_counts()

    #Since the call in eos-db is unimplemented just have a dummy dict for now
    # 'Starting' and 'Prepared' should be returned.
    status_table = { 'Starting' :  2,
                     'Prepared' :  1,
                     'Running'  :  2,
                     'Stopping' :  0 }

    for k, v in status_table.items():
        if v > 0 and k in all_agents:
            yield k


def sleep_n_reap(n):
    """Wait for a given timeout while reaping child processes as soon as they finish.
       This relies on sleep() being interrupted by SIGCHLD, which it normally isn't.
       Setting a SIGCHLD handler is problematic in general but if only for the duration
       of sleep() we're OK.
       You could say this is silly and I should just sleep then reap, but I think this looks
       slicker and hopefully makes logs more readable.
       Note there is a possible race condition if a child exits between 'waitpid' and
       'sleep' and in that case the sleep will not be interrupted.  I can't see a way to
       fix this.  The child will be reaped on the next iteration.
    """
    n = float(n)
    starttime = clock()

    # Run the loop at least once so we reap even if n=0
    # Do reaping first to catch any jobs that finished while we were
    # doing other stuff.
    while True:
        try:
            while True:
                #Loop to reap any processes that are ready to go
                #Probably just 1 but don't bet on it.
                pid, status = os.waitpid(-1, os.WNOHANG)
                if pid == 0:
                    #Nothing more to reap
                    break
                retval = status // 0x0100
                sigrcvd = status %  0x0100
                jobname = jobs_running[pid]

                log.info("Reaped job %s, pid=%i ret=%i sig=%i" % (jobname, pid, retval, sigrcvd))
                if retval or sigrcvd:
                    log.warning("WARNING - job %s did not exit normally." % jobname)
                del jobs_running[pid]
        except ChildProcessError as e:
            #No child to wait for, says waitpid, so we're done
            pass

        #If we've done enough sleeping then quit.
        if clock() >= starttime + n : break

        try:
            signal.signal(signal.SIGCHLD, lambda s, f: None)
            sleep(n + starttime - clock())
        except ValueError:
            # We tried to sleep for a negative time, no worries
            pass
        #Go back to ignoring SIGCHLD as it can cause problems in I/O
        #Then go back round the loop to see if there is anything to clean up.
        signal.signal(signal.SIGCHLD, signal.SIG_DFL)

def reap_all_jobs():
    """Cleanup function waits for all jobs to complete
    """
    reaped = 0
    errors = 0
    # We expect to get back exactly what is in the jobs_running table
    log.info("Waiting to reap %i remaining jobs" % len(jobs_running))
    while True:
        try:
            pid, status = os.waitpid(-1, 0)
            if status: errors = errors + 1
            reaped = reaped + 1
            del jobs_running[pid]
        except InterruptedError:
            #Change this to 'continue' to inhibit interruptions:
            break
        except ChildProcessError:
            #we is done
            break
    (log.warning if errors else log.info)("Reaped %i jobs with %i non-zero exit" % (reaped, errors))

    return reaped

def start_job(name, func, *args, **kwargs):
    if name in jobs_running.values():
        log.info("Job %s already running." % name)
        return False
    else:
        log.info("Starting job %s" % name)

        pid = os.fork()
        if pid == 0:
            #child.  If the job crashes we'll get a non-zero exit status
            setproctitle(name)
            func(*args, **kwargs)
            exit(0)
        elif pid == -1:
            raise Error("Unable to fork job %s" % name)
        else:
            jobs_running[pid] = name
    return True

if __name__ == '__main__':
    main()