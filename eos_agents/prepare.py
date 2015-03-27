#!/usr/bin/python3

from eos_agents import agent, actions

prepare_agent = agent.Agent("Preparing", [actions.stop_vm], "Prepared", "Started")

if __name__ == '__main__':
    prepare_agent.dwell()
