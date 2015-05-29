#!/usr/bin/python3

# See start.py for main comments.

from eos_agents import agent, actions

class Prepare_Agent(agent.Agent):

    trigger_state = "Preparing"
    success_state = "Prepared"
    failure_state = "Started"

    def act(self):
        self.do_action(actions.shutdown_vm)

my_agent = Prepare_Agent()
if __name__ == '__main__':
    my_agent.dwell()
