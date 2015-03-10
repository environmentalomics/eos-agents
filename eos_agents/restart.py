#!/usr/bin/python3

import agent, actions

restart_agent = agent.Agent("Restarting", [actions.restart_vm], "Started", "Started")
restart_agent.dwell()