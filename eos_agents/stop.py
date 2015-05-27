#!/usr/bin/python3

from eos_agents import agent, actions

class Stop_Agent(agent.Agent):

    trigger_state = "Stopping"
    success_state = "Stopped"
    failure_state = "Started"

    def act(self):
        self.do_action(actions.shutdown_vm)

stop_agent = Stop_Agent()
if __name__ == '__main__':
    stop_agent.dwell()
