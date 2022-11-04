import os
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from pdbe_complexes.constants import complex_mapping_headers as csv_headers
from pdbe_complexes.utils import utility as ut

mock_data = {
    "a9f2c6e982b417463bc093e6b83c278b": {
        "pdb_complex_id": "PDB-CPX-100001",
        "complex_portal_id": None,
        "accession": "A0A003_2_67581",
        "entries": "6kvc_1,6kv9_1",
    },
    "a055875916e8e89b5f7da6a27eee3d24": {
        "pdb_complex_id": "PDB-CPX-100002",
        "complex_portal_id": None,
        "accession": "A0A009QSN8_1_1310637,A0A062C259_1_1310678,A0A062C3F9_1_1310678,A0A150HZL5_1_52133,A0A1T1GZ10_1_1960940,A0A1V3DIZ9_1_470,A0A1Y3CHB1_1_1977881,B7I3U0_1_480119,B7I5N9_1_480119,B7I693_1_480119,B7I6V8_1_480119,B7I6V9_1_480119,B7I7A4_1_480119,B7I7B6_1_480119,B7I7R9_1_480119,B7I7S0_1_480119,B7I9B0_1_480119,B7IA13_1_480119,B7IA15_1_480119,B7IA17_1_480119,B7IA20_1_480119,B7IA22_1_480119,B7IA23_1_480119,B7IA24_1_480119,B7IA25_1_480119,B7IA26_1_480119,B7IA27_1_480119,B7IA28_1_480119,B7IA30_1_480119,B7IA31_1_480119,B7IA32_1_480119,B7IA35_1_480119,B7IA36_1_480119,B7IA37_1_480119,B7IA38_1_480119,B7IA39_1_480119,B7IAS9_1_480119,B7IBC1_1_480119,B7IBC3_1_480119,N8V730_1_1144663,N8WQT6_1_1217710,N9DYI8_1_1217649,N9PPR9_1_1144670,RF00001,RF00177,RF01959,RF01960,RF02540,RF02541,RF02542,RF02543,S3NQR5_1_421052,V5V9N0_1_470,V5VBA5_1_470,V5VBC2_1_470,V5VGC9_1_470",  # noqa: B950
        "entries": "6v3b_1",
    },
    "08700a32c53cf2a2a81d48d11cf87277": {
        "pdb_complex_id": "PDB-CPX-100003",
        "complex_portal_id": None,
        "accession": "A0A009QSN8_1_1310637,A0A062C259_1_1310678,A0A062C3F9_1_1310678,A0A150HZL5_1_52133,A0A1T1GZ10_1_1960940,A0A1V3DIZ9_1_470,A0A1Y3CHB1_1_1977881,B7I3U0_1_480119,B7I5N9_1_480119,B7I693_1_480119,B7I6V8_1_480119,B7I6V9_1_480119,B7I7A4_1_480119,B7I7B6_1_480119,B7I7R9_1_480119,B7I7S0_1_480119,B7I9B0_1_480119,B7IA13_1_480119,B7IA15_1_480119,B7IA17_1_480119,B7IA20_1_480119,B7IA22_1_480119,B7IA23_1_480119,B7IA24_1_480119,B7IA25_1_480119,B7IA26_1_480119,B7IA27_1_480119,B7IA28_1_480119,B7IA30_1_480119,B7IA31_1_480119,B7IA32_1_480119,B7IA35_1_480119,B7IA36_1_480119,B7IA37_1_480119,B7IA38_1_480119,B7IA39_1_480119,B7IAS9_1_480119,B7IBC1_1_480119,B7IBC3_1_480119,N8V730_1_1144663,N8WQT6_1_1217710,N9DYI8_1_1217649,N9PPR9_1_1144670,RF00001,RF00005,RF00177,RF01959,RF01960,RF02540,RF02541,RF02542,RF02543,RNA:UNMAPPED,S3NQR5_1_421052,V5V9N0_1_470,V5VBA5_1_470,V5VBC2_1_470,V5VGC9_1_470",  # noqa: B950
        "entries": "6v39_1,6v3a_1",
    },
}

mock_uniprot_mapping = {
    "Q59FX0": "O95271",
    "A0A0K1NSD0": "A0A0B6EJR6",
    "A0A0F7JCM0": "A0A0C5PTY3",
}

mock_obsolete_uniprots = ["Q59FX0", "A0A0K1NSD0", "A0A0F7JCM0"]

mock_reference_mapping = {
    "pdb_complex_id": "PDB-CPX-164129",
    "complex_portal_id": "",
    "accession": "Q59FX0_1_9606",
    "entries": "7kkp_2,7kkq_1,7kko_1,7kkn_1,7kkm_1",
}

mock_complex_strings = [
    "Q59FX0_1_9606",
    "A0A003_2_67581",
    "Q95TS5_1_7227,Q9VAH9_1_7227,Q9W3E1_1_7227",
    "A0A003_2_67581,Q59FX0_1_9606",
]


class TestCaseBase(TestCase):
    def assertIsFile(self, path):
        if not Path(path).resolve().is_file():
            raise AssertionError("File does not exist: %s" % str(path))


class TestUtility(TestCaseBase):
    # def setUp(self) -> None:
    #     self.ndo = Neo4jDatabaseOperations(("neo4j://", "mock_username", "mock_password"))
    #     # self.username = "mock_username"
    #     # self.password = "mock_password"
    #     # self.bolt_uri = "neo4j://"
    #     self.query = "mock_query"

    # @patch("pdbe_complexes.utils.utility.Graph.run")
    # def test_run_query(self, mock):
    #     mock.return_value = True
    #     data = self.ndo.run_query(self.query)
    #     self.assertTrue(data)

    def test_get_uniprot_mapping(self):
        """
        Test if the method reads the UniProt mapping text file correctly
        """
        base_path = Path.cwd()
        mock_test_filepath = base_path.joinpath("tests").joinpath("data")
        mapping_uniprot_dict, obsolete_uniprot_accessions = ut.get_uniprot_mapping(
            mock_test_filepath
        )

        self.assertDictEqual(
            mapping_uniprot_dict,
            {
                "Q59FX0": "O95271",
                "A0A0K1NSD0": "A0A0B6EJR6",
                "A0A0F7JCM0": "A0A0C5PTY3",
            },
        )
        self.assertListEqual(
            obsolete_uniprot_accessions, ["Q59FX0", "A0A0K1NSD0", "A0A0F7JCM0"]
        )

    @patch("pdbe_complexes.utils.utility.get_uniprot_taxid")
    def test_get_uniprot_taxid(self, rq):
        """
        Test if the method returns the correct taxid for the given
        UniProt accession
        """
        rq.return_value = "9606"

        taxid = ut.get_uniprot_taxid("O95271")
        self.assertEqual(taxid, "9606")

    def test_find_complexes_with_obsolete_id(self):
        """
        Test if the method finds the complex string containing obsolete
        UniProt accessions
        """
        complexes_with_obsolete_id = ut.find_complexes_with_obsolete_id(
            mock_complex_strings, mock_obsolete_uniprots
        )
        self.assertEqual(
            complexes_with_obsolete_id,
            [("Q59FX0_1_9606", "Q59FX0"), ("A0A003_2_67581,Q59FX0_1_9606", "Q59FX0")],
        )

    def test_create_new_complex_string(self):
        """
        Test if the method creates the correct complex string based on updated
        UniProt accession
        """
        # single complex component
        updated_complex_strings = ut.create_new_complex_string(
            [("Q59FX0_1_9606", "Q59FX0")], mock_uniprot_mapping
        )
        self.assertDictEqual(
            updated_complex_strings, {"Q59FX0_1_9606": "O95271_1_9606"}
        )
        # multiple complex components
        updated_complex_strings = ut.create_new_complex_string(
            [("A0A003_2_67581,Q59FX0_1_9606", "Q59FX0")], mock_uniprot_mapping
        )
        self.assertDictEqual(
            updated_complex_strings,
            {"A0A003_2_67581,Q59FX0_1_9606": "A0A003_2_67581,O95271_1_9606"},
        )

    def test_merge_csv_files(self):
        "Test if the merge_csv_files method creates a file"
        base_path = Path.cwd()
        mock_files_path = base_path.joinpath("tests").joinpath("data")
        filename1 = "mock_complexes_mapping.csv"
        filename2 = "mock_complexes_name.csv"
        ut.merge_csv_files(mock_files_path, filename1, filename2)
        path = Path(mock_files_path.joinpath("complexes_master.csv"))

        if path:
            self.assertIsFile(path)
            # delete file at the end of the test
            os.remove(mock_files_path.joinpath("complexes_master.csv"))

    def test_export_csv(self):
        "Test if the export_csv method creates a file"
        base_path = Path.cwd()
        output_file_path = base_path.joinpath("tests").joinpath("data")
        filename = "mock_complexes_mapping_example.csv"
        csv_params = (mock_data, "md5_obj", csv_headers, output_file_path, filename)
        ut.export_csv(csv_params)
        path = Path(output_file_path.joinpath(filename))

        if path:
            self.assertIsFile(path)
            # delete file at the end of the test
            os.remove(output_file_path.joinpath(filename))
