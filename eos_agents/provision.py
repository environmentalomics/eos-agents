#!/usr/bin/python3

""" The first agent that runs when a new VM is to be instantiated from a
    template.
"""

from eos_agents import agent, actions

class Provision_Agent(agent.Agent):

    trigger_state = "Provisioning"
    success_state = "Post_Provisioning"
    failure_state = "Cleanup"
    # TODO - check if this is right or not.
    ignore_bad_requests = True

    def act(self):
        #Make a call to servers/by_id/{self.vm_id}
        vm_info = self.session.server_data(self.vm_id)
        # New action to instantiate a VM
        self.do_action(actions.provision_vm, vm_info)

        
        #... ['artifact_name'], vm_info['template_id'], vm_info['descripti)

my_agent = Provision_Agent()
if __name__ == '__main__':
    my_agent.dwell()
