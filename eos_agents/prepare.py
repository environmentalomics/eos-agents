#!/usr/bin/python3

from eos_agents import agent, actions

class Prepare_Agent(agent.Agent):

    trigger_state = "Preparing"
    success_state = "Prepared"
    failure_state = "Started"

    def act(self):
        self.do_action(actions.shutdown_vm)

prepare_agent = Prepare_Agent()
if __name__ == '__main__':
    prepare_agent.dwell()
