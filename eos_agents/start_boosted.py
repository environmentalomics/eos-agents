#!/usr/bin/python3

# See start.py for main comments.

from eos_agents import agent, actions

class Start_Boosted_Agent(agent.Agent):

    trigger_state = "Starting_Boosted"
    success_state = "Started"
    failure_state = "Pre_Deboosting"

    def act(self):
        self.do_action(actions.start_vm)

my_agent = Start_Boosted_Agent()
if __name__ == '__main__':
    my_agent.dwell()
