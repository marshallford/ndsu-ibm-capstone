import unittest

from pprint import pprint

from openstack_gerrit.collector import main


class GerritIntegrationTestCase(unittest.TestCase):

    def test_query_change(self):
        gs = main.GerritSession()

        change = gs.query_change('423782')

        # check if we have some expected keys
        self.assertIn('project', change)
        self.assertIn('status', change)
        self.assertIn('subject', change)

