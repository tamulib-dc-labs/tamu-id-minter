import unittest
from unittest.mock import patch, MagicMock
from tamu_id_minter.ezid.ezid import (
    EZIDARKHandler
)

class TestEZID(unittest.TestCase):
    
    ''' Testcases for EZID functionality. '''

    def setUp(self):
        self.handler = EZIDARKHandler()

    # -------------------------------------- #

    def test_create_metadata(self):
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
    
    # -------------------------------------- #

    @patch('tamu_id_minter.ezid.ezid.requests.post')
    def test_create_ark_success(self, mock_post):
        '''
        Test that an ARK is created successfully.
        When I call create_ark() with known inputs, the returned value must contain an 'ark' key with a non-empty value.
        '''

        mock_response = MagicMock()
        mock_response.content = b'success ark:/81423/d2tg6j'
        mock_post.return_value = mock_response

        result = self.handler.create_ark(
            who = "Dummy name",
            what = "Dummy title",
            when = "2025",
            where = "http://example.com/resource"
        )

        self.assertEqual(result['ark'], 'https://n2t.net/ark:/81423/d2tg6j')
        self.assertEqual(result['who'], 'Dummy name')
        self.assertEqual(result['what'], 'Dummy title')
        self.assertEqual(result['when'], '2025')

    # -------------------------------------- #

    @patch.object(EZIDARKHandler, 'create_ark')
    @patch('builtins.open')
    def test_process_csv(self, mock_open, mock_create_ark):
        '''
        Test that a CSV file is processed correctly and ARKs are created for each row.
        When I call process_csv() with a sample CSV file, the returned list must contain entries for each row in the CSV.
        '''

        csv_content = "who,what,when,where\nJohn Doe,Test Doc,2025,http://example.com\nJane Smith,Another Doc,2024,http://example2.com"
        mock_open.return_value.__enter__.return_value = csv_content.splitlines(True)
        
        mock_create_ark.return_value = {
            'who': 'John Doe',
            'what': 'Test Doc',
            'when': '2025',
            'where': 'http://example.com',
            'message': 'success',
            'ark': 'ark:/81423/test'
        }

        self.handler.process_csv('test.csv')

        # Should be called twice (one for each row in CSV)
        self.assertEqual(mock_create_ark.call_count, 2)
        self.assertEqual(len(self.handler.completed), 2)

    # -------------------------------------- #

    @patch('builtins.open')
    def test_save_results(self, mock_open):
        '''
        Test that results are saved to a CSV file correctly.
        When I call save_results() with a sample output file, the file must be written with the correct data.
        '''

        self.handler.completed = [
            {
                'who': 'Dummy name',
                'what': 'Dummy title',
                'when': '2025',
                'where': 'http://example.com/resource',
                'message': 'success ark:/81423/d2tg6j',
                'ark': 'https://n2t.net/ark:/81423/d2tg6j'
            }
        ]

        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        self.handler.save_results('output.csv')

        mock_open.assert_called_once_with('output.csv', 'w', newline='')
        mock_file.write.assert_called()
        self.assertTrue(mock_file.write.called or mock_file.__enter__.return_value.write.called)

    # -------------------------------------- #

    @patch('tamu_id_minter.ezid.ezid.requests.get')
    @patch('builtins.print')
    def test_get_ark(self, mock_print, mock_get):
        '''
        Test that an ARK can be retrieved.
        When I call get_ark() with a known ARK, the returned value must contain the correct metadata.
        '''

        mock_response = MagicMock()
        mock_response.content = b"success: ark:/81423/d2test123\nerc.who: John Doe\nerc.what: Test Document"
        mock_get.return_value = mock_response

        self.handler.get_ark("ark:/81423/d2test123")

        mock_print.assert_called_once()
        mock_get.assert_called_once()

    # -------------------------------------- #

    @patch.object(EZIDARKHandler, 'save_results')
    @patch.object(EZIDARKHandler, 'process_csv')
    def test_create_batch_from_csv(self, mock_process, mock_save):
        '''
        Test that a batch of ARKs can be created from a CSV file.
        When I call create_batch_from_csv() with input and output files, process_csv and save_results must be called.
        '''

        self.handler.completed = [{'ark': 'ark:/81423/d2test123'}]

        result = self.handler.create_batch_from_csv('input.csv', 'output.csv')

        mock_process.assert_called_once_with('input.csv')
        mock_save.assert_called_once_with('output.csv')
        self.assertEqual(result, self.handler.completed)

    # -------------------------------------- #

    @patch('tamu_id_minter.ezid.ezid.requests.post')
    def test_switch_status_success(self, mock_post):
        '''
        Test that ARK status can be switched successfully.
        When I call switch_status() with valid inputs, it should return True and a success message.
        '''
        mock_response = MagicMock()
        mock_response.content = b'success: ark:/81423/d2test123'
        mock_post.return_value = mock_response

        success, message = self.handler.switch_status("ark:/81423/d2test123", "public")

        self.assertTrue(success)
        self.assertIn("successfully changed to public", message)
        mock_post.assert_called_once()

    # -------------------------------------- #

    @patch.object(EZIDARKHandler, 'switch_status')
    @patch('builtins.open')
    def test_batch_switch_status(self, mock_open, mock_switch):
        '''
        Test batch status switching from CSV.
        When I call batch_switch_status(), it should switch status for all ARKs in the CSV.
        '''

        csv_content = "ark\nark:/81423/test1\nark:/81423/test2"
        mock_input_file = MagicMock()
        mock_input_file.__enter__.return_value = csv_content.splitlines(True)
        
        mock_output_file = MagicMock()
        
        mock_open.side_effect = [mock_input_file, mock_output_file]
        
        mock_switch.return_value = (True, "success")

        self.handler.batch_switch_status('arks.csv', 'public')

        self.assertEqual(mock_switch.call_count, 2)
        self.assertEqual(mock_open.call_count, 2)

    # -------------------------------------- #

    @patch('tamu_id_minter.ezid.ezid.requests.post')
    def test_switch_status_failure(self, mock_post):
        '''
        Test that ARK status can be switched successfully.
        When I call switch_status() with valid inputs, it should return True and a success message.
        '''
        mock_response = MagicMock()
        mock_response.content = b'error: does not exist'
        mock_post.return_value = mock_response

        success, message = self.handler.switch_status("ark:/81423/d2test123", "public")

        self.assertFalse(success)
        self.assertIn("status failed with", message)
        mock_post.assert_called_once()

if __name__ == '__main__':
    unittest.main()