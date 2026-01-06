import unittest
from xml.etree.ElementTree import Element
from tamu_id_minter.crossref.templates import (
    CrossrefXMLTemplate,
)


class TestCrossrefXMLTemplate(unittest.TestCase):
    """Test cases for CrossrefXMLTemplate base class."""

    def setUp(self):
        self.template = CrossrefXMLTemplate()
        self.root = Element("root")

    # -------------------------------------- #

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

    # -------------------------------------- #

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

    # -------------------------------------- #

    def test_parse_contributors_last_first_format(self):

        # ---- Testing Last, First Format ---- #
        contributors = self.template.parse_contributors("Baggett, Mark P.")
        self.assertEqual(contributors, [("Mark P.", "Baggett")])

        # ---- Testing First Last Format ---- #
        contributors = self.template.parse_contributors("Steve Smith")
        self.assertEqual(contributors, [("Steve", "Smith")])

        # ---- Testing Just LastName Format ---- #
        contributors = self.template.parse_contributors("Smith")
        self.assertEqual(contributors, [("","Smith")])

        # ---- Testing with "and" "|" ";" seperators ---- #
        contributors = self.template.parse_contributors("Smith and Williamson")
        self.assertEqual(contributors, [("","Smith"),('','Williamson')])

        contributors = self.template.parse_contributors("Johnson ; Webster")
        self.assertEqual(contributors, [("","Johnson"),('','Webster')])

        contributors = self.template.parse_contributors("Johnson | Webster")
        self.assertEqual(contributors, [("","Johnson"),('','Webster')])

        # ---- Testing extra seperators in input ---- #
        contributors = self.template.parse_contributors("Johnson | Webster | ")
        self.assertEqual(contributors, [("","Johnson"),('','Webster')])

    # -------------------------------------- #

    def test_add_titles(self):
        self.template.add_titles(self.root,"Title")
        title = self.root.find("./titles/title")
        self.assertIsNotNone(title)
        self.assertEqual(title.text, "Title")

    # -------------------------------------- #

    def test_parse_date_iso(self):
        month, day, year = self.template.parse_date("2026-05-01")
        self.assertEqual((month, day, year), ("5", "1", "2026"))

    # -------------------------------------- #

    def test_parse_date_slash_formats(self):
        self.assertEqual(
            self.template.parse_date("05/01/2026"),
            ("5", "1", "2026")
        )

        self.assertEqual(
            self.template.parse_date("01/05/2026"),
            ("1", "5", "2026")
        )
        
        self.assertEqual(
            self.template.parse_date("2026/05/01"),
            ("5", "1", "2026")
        )

    # -------------------------------------- #

    def test_parse_date_invalid_raises(self):
        with self.assertRaises(ValueError):
            self.template.parse_date("Jan 31 2026")

    # -------------------------------------- #

    def test_add_doi_data_normalizes_doi(self):
        self.template.add_doi_data(
            self.root,
            "https://doi.org/test/test.doi",
            "https://example.com"
        )

        doi = self.root.find(".//doi").text
        resource = self.root.find(".//resource").text

        self.assertEqual(doi, "test/test.doi")
        self.assertEqual(resource, "https://example.com")
        self.assertNotEqual(resource,"testFail")

    # -------------------------------------- #

    def test_prettify_xml_returns_string(self):
        self.template.add_titles(self.root, "Pretty XML")

        xml_str = self.template.prettify_xml(self.root)

        self.assertIsInstance(xml_str, str)
        self.assertIn("<titles>", xml_str)
        self.assertIn("<title>Pretty XML</title>", xml_str)
    
    def test_add_contributors_creates_structure(self):
        self.template.add_contributors(self.root, "Steve Smith and Joe Root")

        contributors = self.root.find("contributors")
        self.assertIsNotNone(contributors)

        persons = contributors.findall("person_name")
        self.assertEqual(len(persons), 2)

        self.assertEqual(persons[0].attrib["sequence"], "first")
        self.assertEqual(persons[1].attrib["sequence"], "additional")

        self.assertEqual(persons[0].find("given_name").text, "Steve")
        self.assertEqual(persons[0].find("surname").text, "Smith")
        
        
        self.assertEqual(persons[1].find("given_name").text, "Joe")
        self.assertEqual(persons[1].find("surname").text, "Root")



if __name__ == '__main__':
    unittest.main()