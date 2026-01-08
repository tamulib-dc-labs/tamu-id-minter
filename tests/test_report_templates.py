import unittest
from xml.etree.ElementTree import Element
from tamu_id_minter.crossref.templates import (
    ReportTemplate,
)

class TestReportTemplates(unittest.TestCase):
    ''' Testcases for PendingPublicationTemplate base class'''

    def setUp(self):
        self.root = Element("root")
        self.template = ReportTemplate()

    # -------------------------------------- #

    def test_create_report_paper_values(self):
        metadata = {
            "title": "Report Title",
            "contributor": "Steve Smith",
            "acceptance_date": "2026-01-01",
            "doi": "doi/report",
            "resource": "https://example.com/report"
        }

        publisher = "Texas A&M University"
        institution = "Texas A&M University Libraries"

        self.template.create_report_paper(
            self.root, metadata, publisher, institution
        )

        report_metadata = self.root.find(
            "./report-paper/report-paper_metadata"
        )

        self.assertIsNotNone(report_metadata)

        # Title Check
        title = report_metadata.find("./titles/title")
        self.assertEqual(title.text, metadata["title"])

        # Publication date check
        pub_date = report_metadata.find("publication_date")
        self.assertEqual(pub_date.attrib["media_type"], "online")
        self.assertEqual(pub_date.find("month").text, "1")
        self.assertEqual(pub_date.find("day").text, "1")
        self.assertEqual(pub_date.find("year").text, "2026")

        # Publisher check
        publisher_elem = report_metadata.find("./publisher/publisher_name")
        self.assertEqual(publisher_elem.text, publisher)

        # Institution check
        institution_elem = report_metadata.find(
            "./institution/institution_name"
        )
        self.assertEqual(institution_elem.text, institution)

        # DOI data check
        doi = report_metadata.find(".//doi").text
        resource = report_metadata.find(".//resource").text
        self.assertEqual(doi, metadata["doi"])
        self.assertEqual(resource, metadata["resource"])


    # -------------------------------------- #



if __name__ == '__main__':
    unittest.main()