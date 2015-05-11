#!/usr/bin/python3

from eos_agents import agent, actions

class Start_Agent(agent.Agent):

    trigger_state = "Starting"
    success_state = "Started"
    failure_state = "Stopped"

    def act(self):
        self.do_action(actions.start_vm)

start_agent = Start_Agent()
if __name__ == '__main__':
    start_agent.dwell()
