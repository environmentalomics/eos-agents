#!/usr/bin/python3

# See start.py for main comments.

from eos_agents import agent, actions

class Restart_Agent(agent.Agent):

    trigger_state = "Restarting"
    success_state = "Started"
    failure_state = "Started"

    def act(self):
        self.do_action(actions.restart_vm)

restart_agent = Restart_Agent()
if __name__ == '__main__':
    restart_agent.dwell()
