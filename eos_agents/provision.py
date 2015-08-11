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
        vapp_uuid = actions.provision_vm(vm_info)

        # Retrieve the vapp_id and the primary ip address
        ip_addr = self.do_action

        # Send these back to the database
        self.session.update_server_info(['vapp_id' : vapp_id, 'ip_addr' : ip_addr])

        #... ['artifact_name'], vm_info['template_id'], vm_info['descripti)

my_agent = Provision_Agent()
if __name__ == '__main__':
    my_agent.dwell()
