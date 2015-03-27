#!/usr/bin/python3

from eos_agents import agent, actions

start_agent = agent.Agent("Starting", [actions.start_vm], "Started", "Stopped")

if __name__ == '__main__':
    start_agent.dwell()
