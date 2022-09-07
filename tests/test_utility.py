import os
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from pdbe_complexes.constants import complex_mapping_headers as csv_headers
from pdbe_complexes.utils.utility import export_csv, merge_csv_files, run_query

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


class TestCaseBase(TestCase):
    def assertIsFile(self, path):
        if not Path(path).resolve().is_file():
            raise AssertionError("File does not exist: %s" % str(path))


class TestUtility(TestCaseBase):
    def setUp(self) -> None:
        self.username = "mock_username"
        self.password = "mock_password"
        self.bolt_uri = "neo4j://"
        self.query = "mock_query"

    @patch("pdbe_complexes.utils.utility.Graph.run")
    def test_run_query(self, mock):
        mock.return_value = True
        db_info = (self.bolt_uri, self.username, self.password)
        data = run_query(db_info, self.query)
        self.assertTrue(data)

    def test_merge_csv_files(self):
        "Test if the merge_csv_files method creates a file"
        base_path = Path.cwd()
        mock_files_path = base_path.joinpath("tests").joinpath("data")
        filename1 = "mock_complexes_mapping.csv"
        filename2 = "mock_complexes_name.csv"
        merge_csv_files(mock_files_path, filename1, filename2)
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
        export_csv(mock_data, "md5_obj", csv_headers, output_file_path, filename)
        path = Path(output_file_path.joinpath(filename))

        if path:
            self.assertIsFile(path)
            # delete file at the end of the test
            os.remove(output_file_path.joinpath(filename))
