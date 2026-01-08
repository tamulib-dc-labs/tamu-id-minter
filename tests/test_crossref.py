import unittest
from xml.etree import ElementTree as ET
from unittest.mock import Mock, patch, mock_open
from tamu_id_minter.crossref.crossref import (
    CrossrefDepositHandler
)

from tamu_id_minter.crossref.templates import (
    PendingPublicationTemplate,
    ReportTemplate
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

    def test_stops_on_first_invalid_row(self):
        '''
        Test that processing stops on the first invalid row.
        When I call process_csv() with a CSV where an invalid row appears after valid rows, processing must stop and raise ValueError at the first invalid row.
        '''
        sample_csv = """Title,Contributor,Acceptance date,DOI,Resource
                        Valid Title,Dummy Name,2025-01-01,10.1234/example.d,https://example.com/resource
                        ,Another Name,2025-02-01,10.5678/another.d,https://example.com/another"""

        with patch("builtins.open", mock_open(read_data=sample_csv)):
            with self.assertRaises(ValueError) as context:
                self.handler.process_csv("dummy_path.csv")
        
        self.assertIn("Missing Title in row", str(context.exception))
        assert len(self.handler.completed) == 1  # Only the first valid row processed
        assert self.handler.completed[0]['title'] == 'Valid Title'

    # ------------------ TESTING THE BEHAVIOR OF GENERATE_DEPOSIT_XML METHOD ---------------------- #

    def test_template_selection_and_batch_id_pending_publication(self):
        mock_templates = Mock()
        mock_templates.create_doi_batch.return_value = ET.Element("doi_batch")
        mock_templates.prettify_xml.return_value = "<xml />"

        mock_datetime = Mock()
        mock_datetime.now.return_value.strftime.return_value = "20260105123456"

        content_config = ('pending_publication', PendingPublicationTemplate, "create_pending_publication", "TAMU-PENDING-PUBLICATION-")
        content_type, template_class, content_method, batch_prefix = content_config

        with patch("tamu_id_minter.crossref.crossref.PendingPublicationTemplate", return_value=mock_templates,), \
            patch("tamu_id_minter.crossref.crossref.datetime",mock_datetime,):
            self.handler.generate_deposit_xml(content_type, [{'Title':'Sample'}])

        args = mock_templates.create_doi_batch.call_args[0]
        batch_id = args[3]

        self.assertTrue(batch_id.startswith(batch_prefix))
        self.assertTrue(batch_id.endswith("20260105123456"))
        mock_templates.create_pending_publication.assert_called_once()
        mock_templates.create_report_paper.assert_not_called()

    
    # -------------------------------------- #

    def test_template_selection_and_batch_id_report(self):
        mock_templates = Mock()
        mock_templates.create_doi_batch.return_value = ET.Element("doi_batch")
        mock_templates.prettify_xml.return_value = "<xml />"

        mock_datetime = Mock()
        mock_datetime.now.return_value.strftime.return_value = "20260105123456"

        content_config = ('report', ReportTemplate, "create_report_paper", "TAMU-REPORT-")
        content_type, template_class, content_method, batch_prefix = content_config

        with patch("tamu_id_minter.crossref.crossref.ReportTemplate", return_value=mock_templates,), \
            patch("tamu_id_minter.crossref.crossref.datetime",mock_datetime,):
            self.handler.generate_deposit_xml(content_type, [{'Title':'Sample'}])

        args = mock_templates.create_doi_batch.call_args[0]
        batch_id = args[3]

        self.assertTrue(batch_id.startswith(batch_prefix))
        self.assertTrue(batch_id.endswith("20260105123456"))
        mock_templates.create_pending_publication.assert_not_called()
        mock_templates.create_report_paper.assert_called_once()

    # -------------------------------------- #

    def test_invalid_content_type_raises_value_error(self):
        '''
        Test that an invalid content type raises ValueError.
        When I call generate_deposit_xml() with an invalid content type, it must raise a ValueError.
        '''

        with self.assertRaises(ValueError) as context:
            self.handler.generate_deposit_xml("invalid_content_type", [])
        
        self.assertIn("Invalid content_type", str(context.exception))




    # ---------------- TESTING THE BEHAVIOR OF SAVE_XML METHOD ---------------------- #

    def test_save_xml(self):
        '''
        Test that XML content is saved correctly to a file.
        When I call save_xml() with known XML content and output file path, the file must be created with the correct content.
        '''

        xml_content = "<test>Sample XML Content</test>"
        output_file = "dummy_output.xml"

        m = mock_open()

        with patch("builtins.open", m):
            self.handler.save_xml(xml_content, output_file)
        
        m.assert_called_once_with(output_file, 'w', encoding='utf-8')
        handle = m()
        handle.write.assert_called_once_with(xml_content)
    
    # -------------------------------------- #

    # def test_create_batch_from_csv(self):
    #     '''
    #     Test the end-to-end process of creating a Crossref deposit XML from a CSV file.
    #     When I call create_batch_from_csv() with known inputs, the output XML file must be created with expected content.
    #     '''


    def test_create_batch_from_csv_full_flow(self):
        with patch.object(
            self.handler, "process_csv", return_value=[{"id": 1}]
        ) as mock_process, patch.object(
            self.handler, "generate_deposit_xml", return_value="<xml />"
        ) as mock_generate, patch.object(
            self.handler, "save_xml"
        ) as mock_save:
            
            result = self.handler.create_batch_from_csv(
                input_file="input.csv",
                output_file="out.xml",
                content_type="report",
            )

        self.assertEqual(result, "out.xml")
        mock_process.assert_called_once()
        mock_generate.assert_called_once()
        mock_save.assert_called_once()

    # -------------------------------------- #

    def test_create_batch_from_csv_generates_default_output_filename(self):

        mock_datetime = Mock()
        mock_datetime.now.return_value.strftime.return_value = "20260105_123456"

        with patch.object(
            self.handler, "process_csv", return_value=[{"id": 1}]
        ) as mock_process, patch.object(
            self.handler, "generate_deposit_xml", return_value="<xml />"
        ) as mock_generate, patch.object(
            self.handler, "save_xml"
        ) as mock_save, patch(
            "tamu_id_minter.crossref.crossref.datetime"
        ) as mock_datetime:

            mock_datetime.now.return_value.strftime.return_value = "20260105_123456"

            result = self.handler.create_batch_from_csv(
                input_file="input.csv",
                output_file=None,
                content_type="pending_publication",
            )

        expected_filename = "crossref-deposit-pending_publication-20260105_123456.xml"
        self.assertEqual(result, expected_filename)
        mock_process.assert_called_once()
        mock_generate.assert_called_once()
        mock_save.assert_called_once()
    
if __name__ == '__main__':
    unittest.main()