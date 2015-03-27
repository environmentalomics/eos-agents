#!/usr/bin/python3

from eos_agents import agent, actions

restart_agent = agent.Agent("Restarting", [actions.restart_vm], "Started", "Started")

if __name__ == '__main__':
    restart_agent.dwell()
