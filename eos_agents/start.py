#!/usr/bin/python3

import agent, actions

start_agent = agent.Agent("Starting", [actions.start_vm], "Started", "Stopped")
start_agent.dwell()
