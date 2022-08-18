from collections import OrderedDict

mock_csv_data = OrderedDict(
    [
        (
            "a9f2c6e982b417463bc093e6b83c278b",
            {
                "pdb_complex_id": "PDB-CPX-1",
                "accession": "A0A003_2_67581",
                "complex_portal_id": None,
                "entries": "6kv9_1,6kvc_1",
            },
        ),
        (
            "dcaa52ff436355defa5b1910253d402f",
            {
                "pdb_complex_id": "PDB-CPX-2",
                "accession": "A0A009QSN8_1_1310637,A0A1Y3CHB1_1_1977881, \
                              B7I693_1_480119,B7I6V8_1_480119,B7I6V9_1_480119, \
                              B7I7A4_1_480119,B7I7B6_1_480119,B7I9B0_1_480119, \
                              B7IA13_1_480119,B7IA20_1_480119,B7IA23_1_480119, \
                              B7IA24_1_480119,B7IA27_1_480119,B7IA28_1_480119, \
                              B7IA31_1_480119,B7IA32_1_480119,B7IA36_1_480119, \
                              B7IA37_1_480119,B7IA38_1_480119,B7IA39_1_480119, \
                              B7IAS9_1_480119,B7IBC3_1_480119,N8V730_1_1144663, \
                              N8WQT6_1_1217710,N9DYI8_1_1217649,N9PPR9_1_1144670, \
                              RF00001,RF02540,RF02541,RF02543,S3NQR5_1_421052,V5VGC9_1_470",
                "complex_portal_id": None,
                "entries": "6v3d_1",
            },
        ),
        (
            "a055875916e8e89b5f7da6a27eee3d24",
            {
                "pdb_complex_id": "PDB-CPX-3",
                "accession": "A0A009QSN8_1_1310637,A0A062C259_1_1310678,A0A062C3F9_1_1310678, \
                              A0A150HZL5_1_52133,A0A1T1GZ10_1_1960940,A0A1V3DIZ9_1_470, \
                              A0A1Y3CHB1_1_1977881,B7I3U0_1_480119,B7I5N9_1_480119, \
                              B7I693_1_480119,B7I6V8_1_480119,B7I6V9_1_480119,B7I7A4_1_480119, \
                              B7I7B6_1_480119,B7I7R9_1_480119,B7I7S0_1_480119,B7I9B0_1_480119, \
                              B7IA13_1_480119,B7IA15_1_480119,B7IA17_1_480119,B7IA20_1_480119, \
                              B7IA22_1_480119,B7IA23_1_480119,B7IA24_1_480119,B7IA25_1_480119, \
                              B7IA26_1_480119,B7IA27_1_480119,B7IA28_1_480119,B7IA30_1_480119, \
                              B7IA31_1_480119,B7IA32_1_480119,B7IA35_1_480119,B7IA36_1_480119, \
                              B7IA37_1_480119,B7IA38_1_480119,B7IA39_1_480119,B7IAS9_1_480119, \
                              B7IBC1_1_480119,B7IBC3_1_480119,N8V730_1_1144663, \
                              N8WQT6_1_1217710, \
                              N9DYI8_1_1217649,N9PPR9_1_1144670,RF00001, \
                              RF00177,RF01959,RF01960, \
                              RF02540,RF02541,RF02542,RF02543,S3NQR5_1_421052,V5V9N0_1_470, \
                              V5VBA5_1_470,V5VBC2_1_470,V5VGC9_1_470",
                "complex_portal_id": None,
                "entries": "6v3b_1",
            },
        ),
        (
            "08700a32c53cf2a2a81d48d11cf87277",
            {
                "pdb_complex_id": "PDB-CPX-4",
                "accession": "A0A009QSN8_1_1310637,A0A062C259_1_1310678,A0A062C3F9_1_1310678, \
                              A0A150HZL5_1_52133,A0A1T1GZ10_1_1960940,A0A1V3DIZ9_1_470, \
                              A0A1Y3CHB1_1_1977881,B7I3U0_1_480119,B7I5N9_1_480119, \
                              B7I693_1_480119,B7I6V8_1_480119,B7I6V9_1_480119, \
                              B7I7A4_1_480119,B7I7B6_1_480119,B7I7R9_1_480119, \
                              B7I7S0_1_480119,B7I9B0_1_480119,B7IA13_1_480119, \
                              B7IA15_1_480119,B7IA17_1_480119,B7IA20_1_480119, \
                              B7IA22_1_480119,B7IA23_1_480119,B7IA24_1_480119, \
                              B7IA25_1_480119,B7IA26_1_480119,B7IA27_1_480119, \
                              B7IA28_1_480119,B7IA30_1_480119,B7IA31_1_480119, \
                              B7IA32_1_480119,B7IA35_1_480119,B7IA36_1_480119, \
                              B7IA37_1_480119,B7IA38_1_480119,B7IA39_1_480119, \
                              B7IAS9_1_480119,B7IBC1_1_480119,B7IBC3_1_480119, \
                              N8V730_1_1144663,N8WQT6_1_1217710,N9DYI8_1_1217649, \
                              N9PPR9_1_1144670,RF00001,RF00005,RF00177,RF01959, \
                              RF01960,RF02540,RF02541,RF02542,RF02543, \
                              RNA:UNMAPPED,S3NQR5_1_421052,V5V9N0_1_470, \
                              V5VBA5_1_470,V5VBC2_1_470,V5VGC9_1_470",
                "complex_portal_id": None,
                "entries": "6v3a_1,6v39_1",
            },
        ),
        (
            "7c00b8f789af59343374a06c65cdbb95",
            {
                "pdb_complex_id": "PDB-CPX-5",
                "accession": "A0A010_2_67581,P39476_2_273057",
                "complex_portal_id": None,
                "entries": "5b0k_1,5gww_2,5b0j_2,5b03_1,5b0m_4,5b0i_1, \
                            5b02_1,6j8w_2,5b0l_1,5gwv_2,6j8v_2",
            },
        ),
        (
            "52fce5e893d4552c319724c8b6ae7dab",
            {
                "pdb_complex_id": "PDB-CPX-6",
                "accession": "A0A010_2_67581",
                "complex_portal_id": None,
                "entries": "5b00_1,5b01_1",
            },
        ),
        (
            "e894061d1c2d6dd1e4683de2073998d0",
            {
                "pdb_complex_id": "PDB-CPX-7",
                "accession": "A0A011_2_67581",
                "complex_portal_id": None,
                "entries": "3vkc_1,3vk5_1,3vkd_1,3vkb_1,3vka_1",
            },
        ),
        (
            "4fea44b9d12043c924d68c4db918cdd5",
            {
                "pdb_complex_id": "PDB-CPX-8",
                "accession": "A0A014C6J9_2_1310912",
                "complex_portal_id": None,
                "entries": "6br7_1",
            },
        ),
        (
            "6c18bde5b9d22b482f74dbc78456982f",
            {
                "pdb_complex_id": "PDB-CPX-9",
                "accession": "A0A014M399_2_1188239",
                "complex_portal_id": None,
                "entries": "7dg0_1,7dfx_1",
            },
        ),
        (
            "1b45964aee5709cc22f7d1707ebbd05e",
            {
                "pdb_complex_id": "PDB-CPX-10",
                "accession": "A0A016UNP9_1_53326",
                "complex_portal_id": None,
                "entries": "2md0_1",
            },
        ),
    ]
)
