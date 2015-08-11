#!/usr/bin/python3

# See start.py for main comments.

from eos_agents import agent, actions

class Post_Provision_Agent(agent.Agent):

    trigger_state = "Post_Provisioning"
    success_state = "Stopped"
    failure_state = "Cleanup"
    # TODO - check if this is right
    ignore_bad_requests = True

    def act(self):
            # Some action to do the networking
            self.do_action(actions.shutdown_vm)
            # Retrieve the IP address and do stuff



my_agent = Post_Provision_Agent()
if __name__ == '__main__':
    my_agent.dwell()
