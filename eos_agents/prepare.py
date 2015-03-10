#!/usr/bin/python3

import agent, actions

prepare_agent = agent.Agent("Preparing", [actions.stop_vm], "Prepared", "Started")
prepare_agent.dwell()