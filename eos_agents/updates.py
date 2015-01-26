"""
ch_agents.updates

A library containing a function for each action which an agent can perform
on the database via the DB API. This module is exclusively aimed at 
interfacing with the database.
"""

from db_client import DBSession
from settings import DBDetails

def set_status(server, status):
    session = DBSession(DBDetails.username, DBDetails.password)
    session.set_state(server, status)
    session.kill()
    return session.last_status
    
def get_triggers(trigger):
    session = DBSession(DBDetails.username, DBDetails.password)
    server_list = session.get_triggers(trigger)
    session.kill()
    return server_list