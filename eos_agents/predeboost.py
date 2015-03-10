#!/usr/bin/python3

import agent, actions

predeboost_agent = agent.Agent("Pre_Deboosting", [actions.stop_vm], "Pre_Deboosted", "Started")
predeboost_agent.dwell()