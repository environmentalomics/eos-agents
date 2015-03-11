#!/usr/bin/python3

# A job runner demo, as discussed with Ben on Friday

# In CloudHands, this starts jobs by polling the API for outstanding tasks and
# then starting the appropriate agent(s).  The agent re-queries to find out what to
# do and exits when it runs out of work.  It's possible that an agent will be in the
# process of exiting when a new task appears for it and so will not be started but will also
# quit without processing the work.  Not a problem, as it will be re-started on the next poll.

import os
import signal
from sys import exit
# Prior to python3.3 we could instead 'import time as clock'
from time import sleep, monotonic as clock
# This requires the python3-setproctitle DEB pakage installed.
# In Perl you just assign to $0, cos Perl is awesome.
try:
    from setproctitle import setproctitle
except ImportError:
    setproctitle = lambda t: None

# Using a global job registry for now, since I've not wrapped this in a class
# dict holds pid => name
jobs_running = {}

# The point of this 'job' is to load the CPU and therefore to show up in the
# output of 'top' for 5 seconds.
def ajob(name="unnamed", duration=5.0):

    from math import sin, cos

    count = 0
    starttime = clock()

    while clock() < starttime + duration :
        for n in range(1,200000):
            if cos(float(n)) > sin(float(n)):
                count = count + 1
            else:
                count = count - 1
        count = count + 100

    #A simulated error.  I could raise an Exception but having the stack trace
    #just clutters the output.
    if name.endswith('_e'):
        print("--Job %s reporting some sort of error." % name)
        exit(1)

    print("--Job %s finishing. Count was %i" % (name, count))

# How to wait for a given timeout while reaping child processes as soon as they finish?
# This relies on sleep() being interrupted by SIGCHLD, which it normally isn't.
# Setting a SIGCHLD handler is problematic in general but if only for the duration
# of sleep() we're OK.
# You could say this is silly and I should just sleep then reap, but I think this looks
# slicker and hopefully makes logs more readable.
# Note there is a possible race condition if a child exits between 'waitpid' and
# 'sleep' and in that case the sleep will not be interrupted.  I can't see a way to
# fix this.
def sleep_n_reap(n):
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
                print("Reaped job %s, pid=%i ret=%i sig=%i" % (jobname, pid, retval, sigrcvd))
                if retval or sigrcvd:
                    print("WARNING - job %s did not exit normally." % jobname)
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
    #Reap meeeee. Reap me, my friend.
    reaped = 0
    errors = 0
    # We expect to get back exactly what is in the jobs_running table
    print("Waiting to reap %i remaining jobs" % len(jobs_running))
    while True:
        try:
            pid, status = os.waitpid(-1, 0)
            if status: errors = errors + 1
            reaped = reaped + 1
            del jobs_running[pid]
        except InterruptedError:
            #Please don't interrupt me.  Go again
            continue
        except ChildProcessError:
            #we is done
            break
    print("Reaped %i jobs with %i non-zero exit" % (reaped, errors))

def start_job(name):
    if name in jobs_running.values():
        print("Job %s already running." % name)
    else:
        print("Starting job %s" % name)

        pid = os.fork()
        if pid == 0:
            #child.  If the job crashes we'll get a non-zero exit status
            setproctitle(name)
            ajob(name)
            exit(0)
        else:
            jobs_running[pid] = name

def main():
    start_job('agent1')
    start_job('agent2_e') # Should run but exit with an error
    sleep_n_reap(2)
    start_job('agent1') # Should say already running
    start_job('agent3')
    sleep_n_reap(2)
    start_job('agent1') # Should say already running
    start_job('agent2_e') # Should say already running
    start_job('agent4_e')
    sleep_n_reap(2)
    start_job('agent1') # Should start
    sleep_n_reap(2)
    reap_all_jobs() # Should wait for all jobs to finish, for a clean exit


if __name__ == '__main__':
    main()
