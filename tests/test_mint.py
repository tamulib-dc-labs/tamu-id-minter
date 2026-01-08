import unittest
from unittest import result
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from tamu_id_minter.mint import cli, create_arks, get_ark, switch_statuses, generate_crossref_deposit

class TestMint(unittest.TestCase):
    
    ''' Testcases for CLI commands. '''

    def setUp(self):
        self.runner = CliRunner()

    # -------------------------------------- #

    def test_cli_no_command(self):
        result = self.runner.invoke(cli) 
        self.assertEqual(result.exit_code, 2)
        self.assertIn("Usage: ", result.output)

    # -------------------------------------- #

    @patch('tamu_id_minter.mint.EZIDARKHandler')
    def test_create_arks_calls_handler(self, mock_handler_class):
        '''Test that create_arks command calls the handler.'''
        mock_handler = MagicMock()
        mock_handler.create_batch_from_csv.return_value = []
        mock_handler_class.return_value = mock_handler

        result = self.runner.invoke(create_arks, ['-i', 'test.csv'])

        self.assertEqual(result.exit_code, 0)
        mock_handler.create_batch_from_csv.assert_called_once()

    # -------------------------------------- #

    @patch('tamu_id_minter.mint.EZIDARKHandler')
    def test_get_ark_calls_handler(self, mock_handler_class):
        '''Test that get_ark command calls the handler.'''
        mock_handler = MagicMock()
        mock_handler_class.return_value = mock_handler

        result = self.runner.invoke(get_ark, ['-a', 'ark:/81423/test'])

        self.assertEqual(result.exit_code, 0)
        mock_handler.get_ark.assert_called_once_with('ark:/81423/test')

    # -------------------------------------- #

    @patch('tamu_id_minter.mint.EZIDARKHandler')
    def test_switch_statuses_calls_handler(self, mock_handler_class):
        '''Test that switch_statuses command calls the handler.'''
        mock_handler = MagicMock()
        mock_handler_class.return_value = mock_handler

        result = self.runner.invoke(switch_statuses, ['-i', 'test.csv', '-s', 'public'])

        self.assertEqual(result.exit_code, 0)
        mock_handler.batch_switch_status.assert_called_once()

    # -------------------------------------- #

    @patch('tamu_id_minter.mint.CrossrefDepositHandler')
    def test_generate_crossref_deposit_calls_handler(self, mock_handler_class):
        '''Test that generate_crossref_deposit command calls the handler.'''
        mock_handler = MagicMock()
        mock_handler.create_batch_from_csv.return_value = 'output.xml'
        mock_handler.completed = []
        mock_handler_class.return_value = mock_handler

        result = self.runner.invoke(generate_crossref_deposit, [
            '-i', 'test.csv',
            '-t', 'pending_publication'
        ])

        self.assertEqual(result.exit_code, 0)
        mock_handler.create_batch_from_csv.assert_called_once()

    # -------------------------------------- #

    def test_cli_help(self):
        '''Test that CLI help works.'''
        result = self.runner.invoke(cli, ['--help'])
        self.assertEqual(result.exit_code, 0)


if __name__ == '__main__':
    unittest.main()