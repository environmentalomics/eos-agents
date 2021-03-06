#!/usr/bin/python3

# See start.py for main comments.

from eos_agents import agent, actions

class Deboost_Agent(agent.Agent):

    trigger_state = "Pre_Deboosted"
    success_state = "Starting"
    failure_state = "Error"

    def act(self):
        self.session.set_state(self.vm_id, "Deboosting")

        cores, ram = self.session.get_latest_specification(self.vm_id)
        self.do_action(actions.boost_vm_memory, ram)
        self.do_action(actions.boost_vm_cores, cores)

#This has the side effect of registering the instance, even if it isn't run.
my_agent = Deboost_Agent()
if __name__ == '__main__':
    my_agent.dwell()
