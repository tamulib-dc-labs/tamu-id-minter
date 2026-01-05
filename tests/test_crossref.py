import unittest
from unittest.mock import patch, mock_open
from tamu_id_minter.crossref.crossref import (
    CrossrefDepositHandler
)

class TestCrossref(unittest.TestCase):
    
    ''' Testcases for Crossref functionality. '''

    def setUp(self):
        self.handler = CrossrefDepositHandler()

    # -------------------------------------- #

    def test_crossref_init(self):
        ''' 
        Test that CrossrefDepositHandler initializes correctly. 
        When I create an instance of CrossrefDepositHandler, its attributes must match the expected default values.
        '''
        self.assertEqual(self.handler.depositor_name, "TAMU Libraries")
        self.assertEqual(self.handler.depositor_email, "depositor@library.tamu.edu")
        self.assertEqual(self.handler.registrant, "Texas A&M University")

    # ------------------ TESTING THE BEHAVIOR OF THE PROCESS_CSV METHOD -------------------- #

    def test_processes_valid_csv(self):
        ''' 
        Test that a valid CSV is processed correctly. 
        When I call process_csv() with a valid CSV file, the returned list must contain expected metadata dictionaries.
        '''
        sample_csv = """Title,Contributor,Acceptance date,DOI,Resource
                        Sample Title,Dummy Name,2025-01-01,10.1234/example.d,https://example.com/resource"""
        
        with patch("builtins.open", mock_open(read_data=sample_csv)):
            metadata_list = self.handler.process_csv("dummy_path.csv")

        assert metadata_list == [
            {
                'title': 'Sample Title',
                'contributor': 'Dummy Name',
                'acceptance_date': '2025-01-01',
                'doi': '10.1234/example.d',
                'resource': 'https://example.com/resource'
            }  
        ]

    # -------------------------------------- #

    def test_missing_required_columns(self):
        ''' 
        Test that CSV with missing required columns raises ValueError. 
        When I call process_csv() with a CSV missing required columns, it must raise a ValueError.
        '''
        sample_csv = """Title,Contributor,DOI
                        Sample Title,Dummy Name,10.1234/example.d"""
        
        with patch("builtins.open", mock_open(read_data=sample_csv)):
            with self.assertRaises(ValueError) as context:
                self.handler.process_csv("dummy_path.csv")
        
        self.assertIn("CSV missing required columns", str(context.exception))
        self.assertIn("Acceptance date", str(context.exception))
        self.assertIn("Resource", str(context.exception))

    # -------------------------------------- #

    def test_missing_required_fields(self):
        ''' 
        Test that CSV with missing required fields raises ValueError. 
        When I call process_csv() with a CSV missing required fields, it must raise a ValueError.
        '''
        # TEST MISSING TITLE
        sample_csv_1 = """Title,Contributor,Acceptance date,DOI,Resource
                        ,Dummy Name,2025-01-01,,https://example.com/resource"""
        
        with patch("builtins.open", mock_open(read_data=sample_csv_1)):
            with self.assertRaises(ValueError) as context:
                self.handler.process_csv("dummy_path.csv")
        
        self.assertIn("Missing Title in row", str(context.exception))

        # TEST MISSING DOI
        sample_csv_2 = """Title,Contributor,Acceptance date,DOI,Resource
                        Dummy title,Some name,2025-01-01,,https://example.com/resource"""
        
        with patch("builtins.open", mock_open(read_data=sample_csv_2)):
            with self.assertRaises(ValueError) as context:
                self.handler.process_csv("dummy_path.csv")
        
        self.assertIn("Missing DOI in row", str(context.exception))

        # TEST MISSING RESOURCE
        sample_csv_3 = """Title,Contributor,Acceptance date,DOI,Resource
                        Dummy title,Some name,2025-01-01,1231.32/doi,"""
        
        with patch("builtins.open", mock_open(read_data=sample_csv_3)):
            with self.assertRaises(ValueError) as context:
                self.handler.process_csv("dummy_path.csv")
        
        self.assertIn("Missing Resource in row", str(context.exception))

    # -------------------------------------- #

    def test_skip_empty_rows(self):
        '''
        Test that empty rows in CSV are skipped.
        When I call process_csv() with a CSV containing empty rows, those rows must be skipped in the output metadata list.
        '''
        sample_csv = """Title,Contributor,Acceptance date,DOI,Resource
                        Sample Title,Dummy Name,2025-01-01,10.1234/example.d,https://example.com/resource
                        ,,,,,
                        ,,,,,
                        Another Title,Another Name,2025-02-01,10.5678/another.d,https://example.com/another"""

        with patch("builtins.open", mock_open(read_data=sample_csv)):
            metadata_list = self.handler.process_csv("dummy_path.csv")
        
        assert len(metadata_list) == 2
        assert metadata_list[0]['title'] == 'Sample Title'
        assert metadata_list[1]['title'] == 'Another Title'


    # def test_generate_deposit_xml(self):

    # -------------------------------------- #

    # def test_save_xml(self):
    #     '''
    #     Test that XML content is saved correctly to a file.
    #     When I call save_xml() with known XML content and output file path, the file must be created with the correct content.
        '''
    
    # -------------------------------------- #

    # def test_create_batch_from_csv(self):
    #     '''
    #     Test the end-to-end process of creating a Crossref deposit XML from a CSV file.
    #     When I call create_batch_from_csv() with known inputs, the output XML file must be created with expected content.
    #     '''