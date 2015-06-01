#!python3

"""Tests for the agent master controller

   This is tricky without starting a database, but I want to avoid that
   dependency.
"""

import unittest
import logging
from unittest.mock import patch
from eos_agents import controller

class TestController(unittest.TestCase):

    def setUp(self):
        #No log please
        logging.basicConfig(format="%(levelname)4.4s@%(asctime)s | %(message)s",
                            datefmt="%H:%M:%S",
                            level = logging.CRITICAL)

    def test_listagents(self):
        self.assertEqual(len(controller.all_agents), 8)


    def test_reap_no_job(self):
        """Test base case for reap
        """
        self.assertEqual(controller.reap_all_jobs(), 0)

    # Here's how to fake a fork+wait!
    @patch('os.fork', return_value=101)
    @patch('os.waitpid', side_effect=[ ( 101, 0), ChildProcessError('mock') ] )
    def test_start_reap_job(self, *args):
        """Start a no-op job and reap it
           Using len() as a sample function
           Actually, forking in unit tests is a no-no, hence the mock fork - see
           http://www.reddit.com/r/Python/comments/19704u/how_would_you_unit_test_code_that_calls_osfork/
        """
        self.assertTrue(controller.start_job('test', len, 'foo'))

        self.assertEqual(controller.reap_all_jobs(), 1)

