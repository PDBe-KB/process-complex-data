from unittest import TestCase
from unittest.mock import patch

from pdbe_complexes.process_complex import Neo4JProcessComplex

mock_complex_portal_data = [
    {
        "complex_id": "CPX-5621",
        "uniq_accessions": "A0A024RAD5_1_9606,P04843_1_9606,P04844_1_9606,P0C6T2_1_9606,P46977_1_9606,P61165_1_9606,P61803_1_9606,Q9NRP0_1_9606",  # noqa: B950
        "entries_str": "6s7o",
    },
    {
        "complex_id": "CPX-6482",
        "uniq_accessions": "A0A5B9_1_9606,P01848_1_9606,P04234_1_9606,P07766_2_9606,P09693_1_9606,P20963_2_9606",  # noqa: B950
        "entries_str": "6jxr",
    },
    {
        "complex_id": "CPX-3227",
        "uniq_accessions": "A0JLT2_0_9606,O43513_0_9606,O60244_0_9606,O75448_0_9606,O75586_0_9606,O95402_0_9606,Q13503_0_9606,Q15528_0_9606,Q15648_0_9606,Q6P2C8_0_9606,Q71SY5_0_9606,Q96G25_0_9606,Q96HR3_0_9606,Q96RN5_0_9606,Q9BTT4_0_9606,Q9BUE0_0_9606,Q9H204_0_9606,Q9H944_0_9606,Q9NPJ6_0_9606,Q9NVC6_0_9606,Q9NWA0_0_9606,Q9NX70_0_9606,Q9P086_0_9606,Q9ULK4_0_9606,Q9Y2X0_0_9606,Q9Y3C7_0_9606",  # noqa: B950
        "entries_str": None,
    },
    {
        "complex_id": "CPX-3264",
        "uniq_accessions": "A2ABV5_0_10090,Q62276_0_10090,Q6PGF3_0_10090,Q80YQ2_0_10090,Q8C1S0_0_10090,Q8VCB2_0_10090,Q8VCD5_0_10090,Q8VCS6_0_10090,Q920D3_0_10090,Q921D4_0_10090,Q924H2_0_10090,Q925J9_0_10090,Q99K74_0_10090,Q9CQ39_0_10090,Q9CQA5_0_10090,Q9CQI9_0_10090,Q9CXU0_0_10090,Q9CXU1_0_10090,Q9CZ82_0_10090,Q9CZB6_0_10090,Q9D7W5_0_10090,Q9D8C6_0_10090,Q9DB40_0_10090,Q9DB91_0_10090,Q9R0X0_0_10090",  # noqa: B950
        "entries_str": None,
    },
    {"complex_id": "CPX-127", "uniq_accessions": "A2ASS6_2_10090", "entries_str": None},
    {
        "complex_id": "CPX-586",
        "uniq_accessions": "A4GXA9_1_9606,Q96NY9_1_9606",
        "entries_str": None,
    },
    {
        "complex_id": "CPX-273",
        "uniq_accessions": "A5X5Y0_0_9606,P46098_0_9606",
        "entries_str": None,
    },
    {
        "complex_id": "CPX-2522",
        "uniq_accessions": "A5YKK6_0_9606,O75175_0_9606,O95628_0_9606,Q92600_0_9606,Q96LI5_0_9606,Q9NZN8_0_9606,Q9UIV1_0_9606",  # noqa: B950
        "entries_str": "7ax1,4c0d,4gmj,5fu6",
    },
    {
        "complex_id": "CPX-2535",
        "uniq_accessions": "A5YKK6_0_9606,O75175_0_9606,O95628_0_9606,Q92600_0_9606,Q96LI5_0_9606,Q9NZN8_0_9606",  # noqa: B950
        "entries_str": "7ax1,4c0d,4gmj,5fu6",
    },
    {
        "complex_id": "CPX-2849",
        "uniq_accessions": "A5YKK6_0_9606,O75175_0_9606,O95628_0_9606,Q92600_0_9606,Q9NZN8_0_9606,Q9ULM6_0_9606",  # noqa: B950
        "entries_str": "7ax1,4c0d,4gmj,5fu6",
    },
]

mock_dict_complex_portal_id = {
    "A0A024RAD5_1_9606,P04843_1_9606,P04844_1_9606,P0C6T2_1_9606,P46977_1_9606,P61165_1_9606,P61803_1_9606,Q9NRP0_1_9606": "CPX-5621",  # noqa: B950
    "A0A5B9_1_9606,P01848_1_9606,P04234_1_9606,P07766_2_9606,P09693_1_9606,P20963_2_9606": "CPX-6482",  # noqa: B950
    "A0JLT2_0_9606,O43513_0_9606,O60244_0_9606,O75448_0_9606,O75586_0_9606,O95402_0_9606,Q13503_0_9606,Q15528_0_9606,Q15648_0_9606,Q6P2C8_0_9606,Q71SY5_0_9606,Q96G25_0_9606,Q96HR3_0_9606,Q96RN5_0_9606,Q9BTT4_0_9606,Q9BUE0_0_9606,Q9H204_0_9606,Q9H944_0_9606,Q9NPJ6_0_9606,Q9NVC6_0_9606,Q9NWA0_0_9606,Q9NX70_0_9606,Q9P086_0_9606,Q9ULK4_0_9606,Q9Y2X0_0_9606,Q9Y3C7_0_9606": "CPX-3227",  # noqa: B950
    "A2ABV5_0_10090,Q62276_0_10090,Q6PGF3_0_10090,Q80YQ2_0_10090,Q8C1S0_0_10090,Q8VCB2_0_10090,Q8VCD5_0_10090,Q8VCS6_0_10090,Q920D3_0_10090,Q921D4_0_10090,Q924H2_0_10090,Q925J9_0_10090,Q99K74_0_10090,Q9CQ39_0_10090,Q9CQA5_0_10090,Q9CQI9_0_10090,Q9CXU0_0_10090,Q9CXU1_0_10090,Q9CZ82_0_10090,Q9CZB6_0_10090,Q9D7W5_0_10090,Q9D8C6_0_10090,Q9DB40_0_10090,Q9DB91_0_10090,Q9R0X0_0_10090": "CPX-3264",  # noqa: B950
    "A2ASS6_2_10090": "CPX-127",
    "A4GXA9_1_9606,Q96NY9_1_9606": "CPX-586",
    "A5X5Y0_0_9606,P46098_0_9606": "CPX-273",
    "A5YKK6_0_9606,O75175_0_9606,O95628_0_9606,Q92600_0_9606,Q96LI5_0_9606,Q9NZN8_0_9606,Q9UIV1_0_9606": "CPX-2522",  # noqa: B950
    "A5YKK6_0_9606,O75175_0_9606,O95628_0_9606,Q92600_0_9606,Q96LI5_0_9606,Q9NZN8_0_9606": "CPX-2535",  # noqa: B950
    "A5YKK6_0_9606,O75175_0_9606,O95628_0_9606,Q92600_0_9606,Q9NZN8_0_9606,Q9ULM6_0_9606": "CPX-2849",  # noqa: B950
}

mock_dict_complex_portal_entries = {
    "CPX-5621": "6s7o",
    "CPX-6482": "6jxr",
    "CPX-3227": None,
    "CPX-3264": None,
    "CPX-127": None,
    "CPX-586": None,
    "CPX-273": None,
    "CPX-2522": "7ax1,4c0d,4gmj,5fu6",
    "CPX-2535": "7ax1,4c0d,4gmj,5fu6",
    "CPX-2849": "7ax1,4c0d,4gmj,5fu6",
}

mock_pdb_assembly_data = [
    {"accessions": "A0A003_2_67581", "assemblies": "6kvc_1,6kv9_1"},
    {
        "accessions": "A0A009QSN8_1_1310637,A0A062C259_1_1310678,A0A062C3F9_1_1310678,A0A150HZL5_1_52133,A0A1T1GZ10_1_1960940,A0A1V3DIZ9_1_470,A0A1Y3CHB1_1_1977881,B7I3U0_1_480119,B7I5N9_1_480119,B7I693_1_480119,B7I6V8_1_480119,B7I6V9_1_480119,B7I7A4_1_480119,B7I7B6_1_480119,B7I7R9_1_480119,B7I7S0_1_480119,B7I9B0_1_480119,B7IA13_1_480119,B7IA15_1_480119,B7IA17_1_480119,B7IA20_1_480119,B7IA22_1_480119,B7IA23_1_480119,B7IA24_1_480119,B7IA25_1_480119,B7IA26_1_480119,B7IA27_1_480119,B7IA28_1_480119,B7IA30_1_480119,B7IA31_1_480119,B7IA32_1_480119,B7IA35_1_480119,B7IA36_1_480119,B7IA37_1_480119,B7IA38_1_480119,B7IA39_1_480119,B7IAS9_1_480119,B7IBC1_1_480119,B7IBC3_1_480119,N8V730_1_1144663,N8WQT6_1_1217710,N9DYI8_1_1217649,N9PPR9_1_1144670,RF00001,RF00177,RF01959,RF01960,RF02540,RF02541,RF02542,RF02543,S3NQR5_1_421052,V5V9N0_1_470,V5VBA5_1_470,V5VBC2_1_470,V5VGC9_1_470",  # noqa: B950
        "assemblies": "6v3b_1",
    },
    {
        "accessions": "A0A009QSN8_1_1310637,A0A1Y3CHB1_1_1977881,B7I693_1_480119,B7I6V8_1_480119,B7I6V9_1_480119,B7I7A4_1_480119,B7I7B6_1_480119,B7I9B0_1_480119,B7IA13_1_480119,B7IA20_1_480119,B7IA23_1_480119,B7IA24_1_480119,B7IA27_1_480119,B7IA28_1_480119,B7IA31_1_480119,B7IA32_1_480119,B7IA36_1_480119,B7IA37_1_480119,B7IA38_1_480119,B7IA39_1_480119,B7IAS9_1_480119,B7IBC3_1_480119,N8V730_1_1144663,N8WQT6_1_1217710,N9DYI8_1_1217649,N9PPR9_1_1144670,RF00001,RF02540,RF02541,RF02543,S3NQR5_1_421052,V5VGC9_1_470",  # noqa: B950
        "assemblies": "6v3d_1",
    },
    {
        "accessions": "A0A009QSN8_1_1310637,A0A062C259_1_1310678,A0A062C3F9_1_1310678,A0A150HZL5_1_52133,A0A1T1GZ10_1_1960940,A0A1V3DIZ9_1_470,A0A1Y3CHB1_1_1977881,B7I3U0_1_480119,B7I5N9_1_480119,B7I693_1_480119,B7I6V8_1_480119,B7I6V9_1_480119,B7I7A4_1_480119,B7I7B6_1_480119,B7I7R9_1_480119,B7I7S0_1_480119,B7I9B0_1_480119,B7IA13_1_480119,B7IA15_1_480119,B7IA17_1_480119,B7IA20_1_480119,B7IA22_1_480119,B7IA23_1_480119,B7IA24_1_480119,B7IA25_1_480119,B7IA26_1_480119,B7IA27_1_480119,B7IA28_1_480119,B7IA30_1_480119,B7IA31_1_480119,B7IA32_1_480119,B7IA35_1_480119,B7IA36_1_480119,B7IA37_1_480119,B7IA38_1_480119,B7IA39_1_480119,B7IAS9_1_480119,B7IBC1_1_480119,B7IBC3_1_480119,N8V730_1_1144663,N8WQT6_1_1217710,N9DYI8_1_1217649,N9PPR9_1_1144670,RF00001,RF00005,RF00177,RF01959,RF01960,RF02540,RF02541,RF02542,RF02543,RNA:UNMAPPED,S3NQR5_1_421052,V5V9N0_1_470,V5VBA5_1_470,V5VBC2_1_470,V5VGC9_1_470",  # noqa: B950
        "assemblies": "6v39_1,6v3a_1",
    },
    {
        "accessions": "A0A010_2_67581,P39476_2_273057",
        "assemblies": "5b03_1,6j8v_2,5gww_2,5b0j_2,5b0i_1,5b02_1,5gwv_2,5b0k_1,5b0m_4,5b0l_1,6j8w_2",  # noqa: B950
    },
]

mock_rfam_params_list = [
    {"complex_id": "PDB-CPX-100002", "rfam_acc": "RF00001"},
    {"complex_id": "PDB-CPX-100002", "rfam_acc": "RF00177"},
    {"complex_id": "PDB-CPX-100002", "rfam_acc": "RF01959"},
    {"complex_id": "PDB-CPX-100002", "rfam_acc": "RF01960"},
    {"complex_id": "PDB-CPX-100002", "rfam_acc": "RF02540"},
    {"complex_id": "PDB-CPX-100002", "rfam_acc": "RF02541"},
    {"complex_id": "PDB-CPX-100002", "rfam_acc": "RF02542"},
    {"complex_id": "PDB-CPX-100002", "rfam_acc": "RF02543"},
    {"complex_id": "PDB-CPX-100003", "rfam_acc": "RF00001"},
    {"complex_id": "PDB-CPX-100003", "rfam_acc": "RF02540"},
    {"complex_id": "PDB-CPX-100003", "rfam_acc": "RF02541"},
    {"complex_id": "PDB-CPX-100003", "rfam_acc": "RF02543"},
    {"complex_id": "PDB-CPX-100004", "rfam_acc": "RF00001"},
    {"complex_id": "PDB-CPX-100004", "rfam_acc": "RF00005"},
    {"complex_id": "PDB-CPX-100004", "rfam_acc": "RF00177"},
    {"complex_id": "PDB-CPX-100004", "rfam_acc": "RF01959"},
    {"complex_id": "PDB-CPX-100004", "rfam_acc": "RF01960"},
    {"complex_id": "PDB-CPX-100004", "rfam_acc": "RF02540"},
    {"complex_id": "PDB-CPX-100004", "rfam_acc": "RF02541"},
    {"complex_id": "PDB-CPX-100004", "rfam_acc": "RF02542"},
    {"complex_id": "PDB-CPX-100004", "rfam_acc": "RF02543"},
]


class TestProcessComplex(TestCase):
    def setUp(self) -> None:
        self.username = "mock_username"
        self.password = "mock_password"
        self.bolt_uri = "neo4j://"
        self.csv_path = "test_csv_path"
        self.uniprot_mapping_path = "test_uniprot_path"

    @patch("pdbe_complexes.utils.operations.Neo4jDatabaseOperations.run_query")
    def test_get_complex_portal_data(self, rq):
        complex_obj = Neo4JProcessComplex(
            self.bolt_uri,
            self.username,
            self.password,
            self.csv_path,
            self.uniprot_mapping_path,
        )
        rq.return_value = mock_complex_portal_data
        # print(rq.return_value)
        complex_obj.get_complex_portal_data()
        # print(mock_dict_complex_portal_id)
        self.assertEqual(
            complex_obj.dict_complex_portal_id, mock_dict_complex_portal_id
        )

        self.assertDictEqual(
            complex_obj.dict_complex_portal_entries, mock_dict_complex_portal_entries
        )

    @patch("pdbe_complexes.utils.operations.Neo4jDatabaseOperations.run_query")
    def test_process_pdb_assembly_data(self, rq):
        complex_obj = Neo4JProcessComplex(
            self.bolt_uri,
            self.username,
            self.password,
            self.csv_path,
            self.uniprot_mapping_path,
        )
        rq.return_value = mock_pdb_assembly_data
        # print(rq.return_value)
        complex_obj.process_assembly_data()
        self.assertEqual(complex_obj.rfam_params_list, mock_rfam_params_list)

        # self.assertDictEqual(
        #     complex_obj.dict_complex_portal_entries, mock_dict_complex_portal_entries
        # )

    @patch("pdbe_complexes.utils.operations.Neo4jDatabaseOperations.run_query")
    def test_use_persistent_identifier(self, rq):
        # Test whether the method return the correct pdb_complex_id based on mock data
        complex_obj = Neo4JProcessComplex(
            self.bolt_uri,
            self.username,
            self.password,
            self.csv_path,
            self.uniprot_mapping_path,
        )
        rq.return_value = mock_pdb_assembly_data
        complex_obj.process_assembly_data()

        # a new complex id is returned if the hash obj is not in the mock data
        pdb_complex_id = complex_obj._use_persistent_identifier(
            # made-up hash obj
            "c0009f",
            None,
            None,
            None,
        )
        self.assertEqual(pdb_complex_id, "PDB-CPX-100006")

        # an existing complex id is returned based on the mock data
        pdb_complex_id = complex_obj._use_persistent_identifier(
            "a9f2c6e982b417463bc093e6b83c278b", None, None, None
        )
        self.assertEqual(pdb_complex_id, "PDB-CPX-100001")
