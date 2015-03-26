#!/usr/bin/python3

import agent

boost_agent = agent.Agent("Prepared", [agent.set_state_to_boosting,
                                 agent.boost_vm_memory,
                                 agent.boost_vm_cores,
                                 ], "Starting", "Error")
boost_agent.dwell()