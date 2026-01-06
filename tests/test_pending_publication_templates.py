import unittest
from xml.etree.ElementTree import Element
from tamu_id_minter.crossref.templates import (
    PendingPublicationTemplate,
)

class TestPendingPublicationTemplates(unittest.TestCase):
    ''' Testcases for PendingPublicationTemplate base class'''

    def setUp(self):
        self.root = Element("root")
        self.template = PendingPublicationTemplate()

    # -------------------------------------- #

    def test_create_pending_publication_values(self):
        metadata = {
            "title": "Pending Sample Paper",
            "contributor": "Steve Smith",
            "acceptance_date": "2026-01-01",
            "doi": "doi/pending",
            "resource": "https://example.com/pending"
        }

        self.template.create_pending_publication(self.root, metadata)

        pending = self.root.find("pending_publication")
        self.assertIsNotNone(pending)
        self.assertEqual(pending.attrib["language"], "en")

        # Contributors
        surname = pending.find(".//contributors/person_name/surname")
        self.assertIsNotNone(surname)
        self.assertEqual(surname.text, "Smith")

        # Title
        title = pending.find(".//titles/title")
        self.assertIsNotNone(title)
        self.assertEqual(title.text, metadata["title"])

        # Acceptance date
        acceptance = pending.find("acceptance_date")
        self.assertEqual(acceptance.find("month").text, "1")
        self.assertEqual(acceptance.find("day").text, "1")
        self.assertEqual(acceptance.find("year").text, "2026")

        # DOI data
        doi = pending.find(".//doi").text
        resource = pending.find(".//resource").text
        self.assertEqual(doi, metadata["doi"])
        self.assertEqual(resource, metadata["resource"])

    # -------------------------------------- #



if __name__ == '__main__':
    unittest.main()