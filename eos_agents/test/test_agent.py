#!python3

"""Tests for the agent(s)

   This is tricky without starting a database, but I want to avoid that
   dependency.  Therefore mock calls to both the database and the VM controller.
"""

import logging
import unittest
from unittest.mock import patch, call, Mock

from eos_agents import all_agents, actions

class TestAgent(unittest.TestCase):

    def setUp(self):
        #No log please
        logging.basicConfig(format="%(levelname)4.4s@%(asctime)s | %(message)s",
                            datefmt="%H:%M:%S",
                            level = logging.CRITICAL)

    # We'll fake session.get_machines_in_state, session.set_state, actions.restart_vm, and actions.get_status
    @patch('eos_agents.actions.restart_vm', return_value=("200","job1234"))
    @patch('eos_agents.actions.get_status', return_value="success")
    def test_restart_agent(self, mock_get_status, mock_restart):

        #Provide a fake database session that gives us a fake job.
        mock_sesh = Mock()
        mock_sesh.get_machines_in_state = Mock(
                return_value=[ dict(artifact_id='mock_id', artifact_uuid='mock_uuid') ] )
        mock_sesh.set_state = Mock()

        #Load up the agent
        from eos_agents import restart
        #Note that depending on how the tests were called we may have one agent or all of
        #them loaded in all_agents.
        self.assertTrue( "Restarting" in all_agents.keys() )

        #Run the agent
        all_agents["Restarting"].failure_state = "Test_Failed"
        all_agents["Restarting"].dwell(session=mock_sesh, persist=False)

        #Check that it behaved
        self.assertEqual( mock_sesh.get_machines_in_state.call_args, call("Restarting") )
        self.assertEqual( mock_restart.call_args, call("mock_uuid") )
        self.assertEqual( mock_get_status.call_args, call("job1234") )
        self.assertEqual( mock_sesh.set_state.call_args, call('mock_id', "Started") )

if __name__ == '__main__':
    unittest.main()
