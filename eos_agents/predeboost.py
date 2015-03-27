#!/usr/bin/python3

from eos_agents import agent, actions

predeboost_agent = agent.Agent("Pre_Deboosting", [actions.stop_vm], "Pre_Deboosted", "Started")

if __name__ == '__main__':
    predeboost_agent.dwell()
