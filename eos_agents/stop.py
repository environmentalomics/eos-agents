#!/usr/bin/python3

from eos_agents import agent, actions

stop_agent = agent.Agent("Stopping", [actions.stop_vm], "Stopped", "Started")

if __name__ == '__main__':
    stop_agent.dwell()
