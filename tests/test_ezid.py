import unittest
from tamu_id_minter.ezid.ezid import EZIDARKHandler

class TestEZID(unittest.TestCase):
    
    ''' Testcases for EZID functionality. '''

    def setUp(self):
        self.handler = EZIDARKHandler()

    
    def test_create_metadate(self):
        ''' 
        Test that metadata is formatted correctly. 
        When I call create_metadata() with known inputs, the returned value must contain specific formatted strings.
        '''

        metadata = self.handler.create_metadata(
            who = "Dummy name",
            what = "Dummy title",
            when = "2025",
            where = "http://example.com/resource"
        )


        self.assertIn("erc.who: Dummy name", metadata)
        self.assertIn("erc.what: Dummy title", metadata)
        self.assertIn("erc.when: 2025", metadata)
        self.assertIn("_target: http://example.com/resource", metadata)
        self.assertIn("_status: reserved", metadata)





if __name__ == '__main__':
    unittest.main()