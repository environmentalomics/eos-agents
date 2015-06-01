#!/usr/bin/python3

from eos_agents import agent, actions

class Predeboost_Agent(agent.Agent):

    trigger_state = "Pre_Deboosting"
    success_state = "Pre_Deboosted"
    failure_state = "Started"
    # Don't get fussed if the machine is already off.
    ignore_bad_requests = True

    def act(self):
        self.do_action(actions.shutdown_vm)

my_agent = Predeboost_Agent()
if __name__ == '__main__':
    my_agent.dwell()
