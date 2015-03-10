#!/usr/bin/python3

import agent, actions

start_agent = agent.Agent("Stopping", [actions.stop_vm], "Stopped", "Started")
start_agent.dwell()