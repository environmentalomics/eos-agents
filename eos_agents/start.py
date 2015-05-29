#!/usr/bin/python3

from eos_agents import agent, actions

# Each agent needs to subclass agent.Agent and to declare its
# three target states.  The trigger_state needs to be unique.
# Also, it is important that each agent instantiates one instance of itself
# upon loading, which is why 'my_agent = Start_Agent()' below is outside of
# the 'if' clause.
# Agents should override act() (unless they really mean to be a no-op) and may
# override 'success()' and 'failure()', for example to reimburse credits.
# Agents should make use of self.do_action(action) which knows how to associate
# actions with the current VM and how to wait for and assess results from
# VCloud Director.

class Start_Agent(agent.Agent):

    trigger_state = "Starting"
    success_state = "Started"
    failure_state = "Stopped"

    def act(self):
        self.do_action(actions.start_vm)

my_agent = Start_Agent()
if __name__ == '__main__':
    my_agent.dwell()
