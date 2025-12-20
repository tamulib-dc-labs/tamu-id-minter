import unittest
from xml.etree.ElementTree import Element
from tamu_id_minter.crossref.templates import (
    CrossrefXMLTemplate,
)


class TestCrossrefXMLTemplate(unittest.TestCase):
    """Test cases for CrossrefXMLTemplate base class."""

    def setUp(self):
        self.template = CrossrefXMLTemplate()

    def test_create_doi_batch_structure(self):
        """Test doi_batch element has correct namespaces and attributes."""
        root = self.template.create_doi_batch(
            depositor_name="Mark P. Baggett",
            depositor_email="mark.baggett@tamu.edu",
            registrant="Texas A&M University",
            batch_id="marks_test_batch"
        )

        self.assertEqual(root.tag, 'doi_batch')
        self.assertEqual(root.get('version'), '5.4.0')
        self.assertEqual(root.get('xmlns'), CrossrefXMLTemplate.NAMESPACE)
        self.assertIsNotNone(root.find('head'))

    def test_add_head_elements(self):
        """Test head section of XML doc has correct values.."""
        root = Element('doi_batch')
        self.template.add_head(
            root,
            depositor_name="Mark P. Baggett",
            depositor_email="mark.baggett@tamu.edu",
            registrant="Texas A&M University",
            batch_id="marks_test_batch"
        )

        head = root.find('head')
        self.assertIsNotNone(head)

        batch_id = head.find('doi_batch_id')
        self.assertEqual(batch_id.text, "marks_test_batch")

        timestamp = head.find('timestamp')
        self.assertIsNotNone(timestamp.text)
        self.assertEqual(len(timestamp.text), 14)
        self.assertTrue(timestamp.text.isdigit())

        depositor = head.find('depositor')
        self.assertEqual(depositor.find('depositor_name').text, "Mark P. Baggett")
        self.assertEqual(depositor.find('email_address').text, "mark.baggett@tamu.edu")

        registrant = head.find('registrant')
        self.assertEqual(registrant.text, "Texas A&M University")

    def test_parse_contributors_last_first_format(self):
        contributors = self.template.parse_contributors("Baggett, Mark P.")
        self.assertEqual(contributors, [("Mark P.", "Baggett")])


if __name__ == '__main__':
    unittest.main()