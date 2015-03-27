#!/usr/bin/python3

from eos_agents import agent

boost_agent = agent.Agent("Prepared", [agent.set_state_to_boosting,
                                 agent.boost_vm_memory,
                                 agent.boost_vm_cores,
                                 ], "Starting", "Error")

if __name__ == '__main__':
    boost_agent.dwell()
