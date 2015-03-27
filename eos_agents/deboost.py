#!/usr/bin/python3

from eos_agents import agent

# Fixme - this is just the boost agent again.
deboost_agent = agent.Agent("Pre_Deboosted", [agent.set_state_to_deboosting,
                                 agent.boost_vm_memory,
                                 agent.boost_vm_cores,
                                 ], "Starting", "Error")

if __name__ == '__main__':
    boost_agent.dwell()
