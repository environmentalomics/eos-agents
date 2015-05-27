#!/usr/bin/python3

from eos_agents import agent, actions

class Predeboost_Agent(agent.Agent):

    trigger_state = "Pre_Deboosting"
    success_state = "Pre_Deboosted"
    failure_state = "Started"

    def act():
        self.do_action(actions.shutdown_vm)

predeboost_agent = Predeboost_Agent()
if __name__ == '__main__':
    predeboost_agent.dwell()
