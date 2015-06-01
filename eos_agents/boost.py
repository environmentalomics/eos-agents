#!/usr/bin/python3

# See start.py for main comments.

from eos_agents import agent, actions

# Really this should be "Prepared_Agent"
class Boost_Agent(agent.Agent):

    trigger_state = "Prepared"
    success_state = "Starting_Boosted"
    failure_state = "Pre_Deboosting"

    def act(self):
        #Set transitional state
        self.session.set_state(self.vm_id, "Boosting")

        cores, ram = self.session.get_latest_specification(self.vm_id)
        self.do_action(actions.boost_vm_memory, ram)
        self.do_action(actions.boost_vm_cores, cores)

my_agent = Boost_Agent()
if __name__ == '__main__':
    my_agent.dwell()
