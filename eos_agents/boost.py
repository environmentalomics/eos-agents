#!/usr/bin/python3

from eos_agents import agent, actions

class Boost_Agent(agent.Agent):

    #FIXME - The states here are all wrong.
    trigger_state = "Prepared"
    success_state = "Starting"
    failure_state = "Error"

    def act(self):
        self.session.set_state_to_boosting(self.vm_id)

        cores, ram = self.session.get_latest_specification(self.vm_id)
        self.do_action(actions.boost_vm_memory, ram)
        self.do_action(actions.boost_vm_cores, cores)

#This has the side effect of registering the instance, even if it isn't run.
boost_agent = Boost_Agent()
if __name__ == '__main__':
    boost_agent.dwell()
