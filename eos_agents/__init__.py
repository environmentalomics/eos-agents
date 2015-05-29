# A global list of all active agents.  See the code in agent.py.
all_agents = {}

# And a function to import all the agents.  Could attempt to 'discover' them but that
# leads to other problems, so if you add a new agent than add it manually to this list.
def load_all_agents():
    from eos_agents import (
                boost,
                deboost,
                predeboost,
                prepare,
                restart,
                start,
                start_boosted,
                stop ,
    )

    return all_agents
