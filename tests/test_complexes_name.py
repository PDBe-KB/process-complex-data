import os

from complexes.get_complex_name import ProcessComplexName
from unittest import TestCase

mock_pdb_complexes_data_one = {
    "PDB-CPX-1": {
        "pdb_complex_id": "PDB-CPX-1",
        "pdb_entries": ["6kvc", "6kv9"],
        "pdb_entries_with_assemblies": ["6kvc_1", "6kv9_1"],
        "components": [
            {
                "stoichiometry": "2",
                "tax_id": "67581",
                "accession": "A0A003",
                "accession_with_isoform": "A0A003",
                "database": "UNP",
                "polymer_type": "PROTEIN",
                "molecule_name": "MoeE5",
            }
        ],
    },
    "PDB-CPX-2": {
        "pdb_complex_id": "PDB-CPX-2",
        "pdb_entries": ["6v3b"],
        "pdb_entries_with_assemblies": ["6v3b_1"],
        "components": [
            {
                "stoichiometry": 0,
                "tax_id": "",
                "accession": "RF02543",
                "database": "Rfam",
                "polymer_type": "RNA",
                "molecule_name": "Eukaryotic large subunit ribosomal RNA",
            },
            {
                "stoichiometry": 0,
                "tax_id": "",
                "accession": "RF02540",
                "database": "Rfam",
                "polymer_type": "RNA",
                "molecule_name": "Archaeal large subunit ribosomal RNA",
            },
            {
                "stoichiometry": 0,
                "tax_id": "",
                "accession": "RF02541",
                "database": "Rfam",
                "polymer_type": "RNA",
                "molecule_name": "Bacterial large subunit ribosomal RNA",
            },
            {
                "stoichiometry": 0,
                "tax_id": "",
                "accession": "RF00001",
                "database": "Rfam",
                "polymer_type": "RNA",
                "molecule_name": "5S ribosomal RNA",
            },
            {
                "stoichiometry": 0,
                "tax_id": "",
                "accession": "RF01959",
                "database": "Rfam",
                "polymer_type": "RNA",
                "molecule_name": "Archaeal small subunit ribosomal RNA",
            },
            {
                "stoichiometry": 0,
                "tax_id": "",
                "accession": "RF00177",
                "database": "Rfam",
                "polymer_type": "RNA",
                "molecule_name": "Bacterial small subunit ribosomal RNA",
            },
            {
                "stoichiometry": "1",
                "tax_id": "480119",
                "accession": "B7IA31",
                "accession_with_isoform": "B7IA31",
                "database": "UNP",
                "polymer_type": "PROTEIN",
                "molecule_name": "50S ribosomal protein L29",
            },
            {
                "stoichiometry": "1",
                "tax_id": "470",
                "accession": "A0A1V3DIZ9",
                "accession_with_isoform": "A0A1V3DIZ9",
                "database": "UNP",
                "polymer_type": "PROTEIN",
                "molecule_name": "30S ribosomal protein S16",
            },
            {
                "stoichiometry": "1",
                "tax_id": "1310678",
                "accession": "A0A062C259",
                "accession_with_isoform": "A0A062C259",
                "database": "UNP",
                "polymer_type": "PROTEIN",
                "molecule_name": "30S ribosomal protein S11",
            },
            {
                "stoichiometry": "1",
                "tax_id": "421052",
                "accession": "S3NQR5",
                "accession_with_isoform": "S3NQR5",
                "database": "UNP",
                "polymer_type": "PROTEIN",
                "molecule_name": "50S ribosomal protein L28",
            },
            {
                "stoichiometry": "1",
                "tax_id": "480119",
                "accession": "B7IA26",
                "accession_with_isoform": "B7IA26",
                "database": "UNP",
                "polymer_type": "PROTEIN",
                "molecule_name": "30S ribosomal protein S14",
            },
        ],
    },
}

mock_pdb_complexes_data_two = {
    "PDB-CPX-7330": {
        "pdb_complex_id": "PDB-CPX-7330",
        "pdb_entries": ["2k2i"],
        "pdb_entries_with_assemblies": ["2k2i_1"],
        "components": [
            {
                "stoichiometry": "1",
                "tax_id": "9606",
                "accession": "P41208",
                "accession_with_isoform": "P41208",
                "database": "UNP",
                "polymer_type": "PROTEIN",
                "molecule_name": "Centrin-2",
            },
            {
                "stoichiometry": "1",
                "tax_id": "9606",
                "accession": "A8K8P3",
                "accession_with_isoform": "A8K8P3",
                "database": "UNP",
                "polymer_type": "PROTEIN",
                "molecule_name": "Protein SFI1 homolog",
            },
        ],
    }
}

mock_complex_portal_per_component_string_two = {"A8K8P3_1,P41208_1": "CPX-724"}
mock_complex_portal_component_string_no_stoch_two = {"P27540,Q16665": "CPX-7381"}
mock_complex_portal_names_two = {"CPX-724": "Centrin-2-SFI1 complex"}
mock_complex_portal_component_dict_two = {"CPX-724": ["P41208_1", "A8K8P3_1"]}

mock_pdb_complexes_data_three = {
    "PDB-CPX-60": {
        "pdb_complex_id": "PDB-CPX-60",
        "pdb_entries": ["5kve"],
        "pdb_entries_with_assemblies": ["5kve_1"],
        "components": [
            {
                "stoichiometry": "1",
                "tax_id": "10090",
                "polymer_type": "PROTEIN",
                "molecule_name": "ZV-48 Antibody scFv",
                "is_antibody": True,
                "pdb_entity": "5kve_2",
                "entity_length": 245,
            },
            {
                "stoichiometry": "1",
                "tax_id": "10090",
                "polymer_type": "PROTEIN",
                "molecule_name": "ZV-48 Antibody scFv",
                "is_antibody": True,
                "pdb_entity": "5kve_2",
                "entity_length": 245,
            },
            {
                "stoichiometry": "1",
                "tax_id": "2043570",
                "accession": "A0A024B7W1",
                "accession_with_isoform": "A0A024B7W1",
                "database": "UNP",
                "polymer_type": "PROTEIN",
                "molecule_name": "Genome polyprotein",
            },
        ],
    }
}

mock_pdb_complexes_data_four = {
    "PDB-CPX-79007": {
        "pdb_complex_id": "PDB-CPX-79007",
        "pdb_entries": ["6ufh", "486d", "6ufg", "6ufm", "4mgn", "6pmo", "6pom"],
        "pdb_entries_with_assemblies": [
            "6ufh_1",
            "486d_1",
            "6ufg_1",
            "6ufm_1",
            "4mgn_1",
            "6pmo_1",
            "6pom_1",
        ],
        "components": [
            {
                "stoichiometry": 0,
                "tax_id": "",
                "accession": "RF00005",
                "database": "Rfam",
                "polymer_type": "RNA",
                "molecule_name": "tRNA",
            },
            {
                "stoichiometry": 0,
                "tax_id": "",
                "polymer_type": "RNA",
                "molecule_name": "RNA",
            },
        ],
    }
}

mock_pdb_complexes_data_five = {
    "PDB-CPX-50289": {
        "pdb_complex_id": "PDB-CPX-50289",
        "pdb_entries": ["5vsu"],
        "pdb_entries_with_assemblies": ["5vsu_1"],
        "components": [
            {
                "stoichiometry": 0,
                "tax_id": "",
                "accession": "RF00026",
                "database": "Rfam",
                "polymer_type": "RNA",
                "molecule_name": "U6 spliceosomal RNA",
            },
            {
                "stoichiometry": "1",
                "tax_id": "559292",
                "accession": "P53905",
                "accession_with_isoform": "P53905",
                "database": "UNP",
                "polymer_type": "PROTEIN",
                "molecule_name": "U6 snRNA-associated Sm-like protein LSm7",
            },
            {
                "stoichiometry": "1",
                "tax_id": "559292",
                "accession": "P49960",
                "accession_with_isoform": "P49960",
                "database": "UNP",
                "polymer_type": "PROTEIN",
                "molecule_name": "U4/U6 snRNA-associated-splicing factor PRP24",
            },
            {
                "stoichiometry": "1",
                "tax_id": "559292",
                "accession": "P40089",
                "accession_with_isoform": "P40089",
                "database": "UNP",
                "polymer_type": "PROTEIN",
                "molecule_name": "U6 snRNA-associated Sm-like protein LSm5",
            },
            {
                "stoichiometry": "1",
                "tax_id": "559292",
                "accession": "Q06406",
                "accession_with_isoform": "Q06406",
                "database": "UNP",
                "polymer_type": "PROTEIN",
                "molecule_name": "U6 snRNA-associated Sm-like protein LSm6",
            },
            {
                "stoichiometry": "1",
                "tax_id": "559292",
                "accession": "P38203",
                "accession_with_isoform": "P38203",
                "database": "UNP",
                "polymer_type": "PROTEIN",
                "molecule_name": "U6 snRNA-associated Sm-like protein LSm2",
            },
            {
                "stoichiometry": "1",
                "tax_id": "559292",
                "accession": "P47093",
                "accession_with_isoform": "P47093",
                "database": "UNP",
                "polymer_type": "PROTEIN",
                "molecule_name": "U6 snRNA-associated Sm-like protein LSm8",
            },
            {
                "stoichiometry": "1",
                "tax_id": "559292",
                "accession": "P40070",
                "accession_with_isoform": "P40070",
                "database": "UNP",
                "polymer_type": "PROTEIN",
                "molecule_name": "U6 snRNA-associated Sm-like protein LSm4",
            },
            {
                "stoichiometry": "1",
                "tax_id": "559292",
                "accession": "P57743",
                "accession_with_isoform": "P57743",
                "database": "UNP",
                "polymer_type": "PROTEIN",
                "molecule_name": "U6 snRNA-associated Sm-like protein LSm3",
            },
        ],
    }
}

mock_complex_portal_per_component_string_five = {"A8K8P3_1,P41208_1": "CPX-44"}
mock_complex_portal_component_string_no_stoch_five = {}
mock_complex_portal_names_five = {"CPX-44": "LSM2-8 complex"}
mock_complex_portal_component_dict_five = {
    "CPX-44": [
        "P40089_1",
        "P53905_1",
        "P38203_1",
        "Q06406_1",
        "P47093_1",
        "P40070_1",
        "P57743_1",
    ]
}

mock_pdb_complexes_data_six = {
    "PDB-CPX-317": {
        "pdb_complex_id": "PDB-CPX-317",
        "pdb_entries": ["7lgj"],
        "pdb_entries_with_assemblies": ["7lgj_1"],
        "components": [
            {
                "stoichiometry": "4",
                "tax_id": "32630",
                "polymer_type": "PROTEIN",
                "molecule_name": "synthetic short peptide",
                "is_antibody": False,
                "pdb_entity": "7lgj_2",
                "entity_length": 9,
            },
            {
                "stoichiometry": "4",
                "tax_id": "1147",
                "accession": "A0A068N621",
                "accession_with_isoform": "A0A068N621",
                "database": "UNP",
                "polymer_type": "PROTEIN",
                "molecule_name": "Cyanophycin synthetase",
            },
        ],
    }
}

mock_pdb_complexes_data_seven = {
    "PDB-CPX-551": {
        "pdb_complex_id": "PDB-CPX-551",
        "pdb_entries": ["6o7k"],
        "pdb_entries_with_assemblies": ["6o7k_1"],
        "components": [
            {
                "stoichiometry": 0,
                "tax_id": "",
                "accession": "RF00177",
                "database": "Rfam",
                "polymer_type": "RNA",
                "molecule_name": "Bacterial small subunit ribosomal RNA",
            },
            {
                "stoichiometry": 0,
                "tax_id": "",
                "accession": "RF02542",
                "database": "Rfam",
                "polymer_type": "RNA",
                "molecule_name": "Microsporidia small subunit ribosomal RNA",
            },
            {
                "stoichiometry": 0,
                "tax_id": "",
                "accession": "RF01959",
                "database": "Rfam",
                "polymer_type": "RNA",
                "molecule_name": "Archaeal small subunit ribosomal RNA",
            },
            {
                "stoichiometry": 0,
                "tax_id": "",
                "accession": "RF00005",
                "database": "Rfam",
                "polymer_type": "RNA",
                "molecule_name": "tRNA",
            },
            {
                "stoichiometry": 0,
                "tax_id": "",
                "accession": "RF01960",
                "database": "Rfam",
                "polymer_type": "RNA",
                "molecule_name": "Eukaryotic small subunit ribosomal RNA",
            },
            {
                "stoichiometry": 0,
                "tax_id": "",
                "polymer_type": "RNA",
                "molecule_name": "RNA",
            },
            {
                "stoichiometry": "1",
                "tax_id": "562",
                "polymer_type": "PROTEIN",
                "molecule_name": "30S ribosomal protein S12",
                "is_antibody": False,
                "pdb_entity": "6o7k_7",
                "entity_length": 123,
            },
            {
                "stoichiometry": "1",
                "tax_id": "562",
                "polymer_type": "PROTEIN",
                "molecule_name": "30S ribosomal protein S20",
                "is_antibody": False,
                "pdb_entity": "6o7k_15",
                "entity_length": 85,
            },
            {
                "stoichiometry": "1",
                "tax_id": "562",
                "polymer_type": "PROTEIN",
                "molecule_name": "30S ribosomal protein S19",
                "is_antibody": False,
                "pdb_entity": "6o7k_13",
                "entity_length": 79,
            },
            {
                "stoichiometry": "1",
                "tax_id": "562",
                "polymer_type": "PROTEIN",
                "molecule_name": "30S ribosomal protein S6",
                "is_antibody": False,
                "pdb_entity": "6o7k_20",
                "entity_length": 100,
            },
            {
                "stoichiometry": "1",
                "tax_id": "562",
                "polymer_type": "PROTEIN",
                "molecule_name": "30S ribosomal protein S17",
                "is_antibody": False,
                "pdb_entity": "6o7k_4",
                "entity_length": 80,
            },
            {
                "stoichiometry": "1",
                "tax_id": "562",
                "polymer_type": "PROTEIN",
                "molecule_name": "30S ribosomal protein S7",
                "is_antibody": False,
                "pdb_entity": "6o7k_21",
                "entity_length": 151,
            },
            {
                "stoichiometry": "1",
                "tax_id": "562",
                "polymer_type": "PROTEIN",
                "molecule_name": "Translation initiation factor IF-2",
                "is_antibody": False,
                "pdb_entity": "6o7k_2",
                "entity_length": 509,
            },
            {
                "stoichiometry": "1",
                "tax_id": "562",
                "polymer_type": "PROTEIN",
                "molecule_name": "30S ribosomal protein S9",
                "is_antibody": False,
                "pdb_entity": "6o7k_23",
                "entity_length": 127,
            },
            {
                "stoichiometry": "1",
                "tax_id": "562",
                "polymer_type": "PROTEIN",
                "molecule_name": "Translation initiation factor IF-1",
                "is_antibody": False,
                "pdb_entity": "6o7k_1",
                "entity_length": 71,
            },
            {
                "stoichiometry": "1",
                "tax_id": "562",
                "polymer_type": "PROTEIN",
                "molecule_name": "30S ribosomal protein S18",
                "is_antibody": False,
                "pdb_entity": "6o7k_12",
                "entity_length": 55,
            },
            {
                "stoichiometry": "1",
                "tax_id": "562",
                "polymer_type": "PROTEIN",
                "molecule_name": "30S ribosomal protein S21",
                "is_antibody": False,
                "pdb_entity": "6o7k_16",
                "entity_length": 51,
            },
            {
                "stoichiometry": "1",
                "tax_id": "562",
                "polymer_type": "PROTEIN",
                "molecule_name": "30S ribosomal protein S10",
                "is_antibody": False,
                "pdb_entity": "6o7k_5",
                "entity_length": 98,
            },
            {
                "stoichiometry": "1",
                "tax_id": "562",
                "polymer_type": "PROTEIN",
                "molecule_name": "30S ribosomal protein S5",
                "is_antibody": False,
                "pdb_entity": "6o7k_19",
                "entity_length": 150,
            },
            {
                "stoichiometry": "1",
                "tax_id": "749533",
                "accession": "D7XN21",
                "accession_with_isoform": "D7XN21",
                "database": "UNP",
                "polymer_type": "PROTEIN",
                "molecule_name": "30S ribosomal protein S15",
            },
            {
                "stoichiometry": "1",
                "tax_id": "585035",
                "accession": "B7MIU7",
                "accession_with_isoform": "B7MIU7",
                "database": "UNP",
                "polymer_type": "PROTEIN",
                "molecule_name": "30S ribosomal protein S16",
            },
            {
                "stoichiometry": "1",
                "tax_id": "1269007",
                "accession": "U9ZNW8",
                "accession_with_isoform": "U9ZNW8",
                "database": "UNP",
                "polymer_type": "PROTEIN",
                "molecule_name": "30S ribosomal protein S2",
            },
            {
                "stoichiometry": "1",
                "tax_id": "1182682",
                "accession": "L3PZ69",
                "accession_with_isoform": "L3PZ69",
                "database": "UNP",
                "polymer_type": "PROTEIN",
                "molecule_name": "30S ribosomal protein S4",
            },
            {
                "stoichiometry": "1",
                "tax_id": "562",
                "accession": "A0A376HTV6",
                "accession_with_isoform": "A0A376HTV6",
                "database": "UNP",
                "polymer_type": "PROTEIN",
                "molecule_name": "30S ribosomal protein S3",
            },
            {
                "stoichiometry": "1",
                "tax_id": "656400",
                "accession": "A0A1X3KX08",
                "accession_with_isoform": "A0A1X3KX08",
                "database": "UNP",
                "polymer_type": "PROTEIN",
                "molecule_name": "30S ribosomal protein S13",
            },
            {
                "stoichiometry": "1",
                "tax_id": "562",
                "accession": "A0A090BZT4",
                "accession_with_isoform": "A0A090BZT4",
                "database": "UNP",
                "polymer_type": "PROTEIN",
                "molecule_name": "30S ribosomal protein S14",
            },
            {
                "stoichiometry": "1",
                "tax_id": "83333",
                "accession": "P0A7R9",
                "accession_with_isoform": "P0A7R9",
                "database": "UNP",
                "polymer_type": "PROTEIN",
                "molecule_name": "30S ribosomal protein S11",
            },
            {
                "stoichiometry": "1",
                "tax_id": "749527",
                "accession": "D8A1L7",
                "accession_with_isoform": "D8A1L7",
                "database": "UNP",
                "polymer_type": "PROTEIN",
                "molecule_name": "30S ribosomal protein S8",
            },
        ],
    }
}

mock_pdb_complexes_data_eight = {
    "PDB-CPX-13341": {
        "pdb_complex_id": "PDB-CPX-13341",
        "pdb_entries": ["6r4o", "6r3q", "7pdf", "6r4p", "7pde"],
        "pdb_entries_with_assemblies": [
            "6r4o_1",
            "6r3q_1",
            "7pdf_1",
            "6r4p_1",
            "7pde_1",
        ],
        "components": [
            {
                "stoichiometry": "1",
                "tax_id": "9913",
                "accession": "E1BM79",
                "accession_with_isoform": "E1BM79",
                "database": "UNP",
                "polymer_type": "PROTEIN",
                "molecule_name": "Adenylate cyclase 9",
            },
            {
                "stoichiometry": "1",
                "tax_id": "9913",
                "accession": "P04896",
                "accession_with_isoform": "P04896",
                "database": "UNP",
                "polymer_type": "PROTEIN",
                "molecule_name": "Guanine nucleotide-binding protein G(s) subunit alpha isoforms short",  # noqa: B950
            },
        ],
    }
}

mock_pdb_complexes_data_nine = {
    "PDB-CPX-709": {
        "pdb_complex_id": "PDB-CPX-709",
        "pdb_entries": ["7e1s"],
        "pdb_entries_with_assemblies": ["7e1s_1"],
        "components": [
            {
                "stoichiometry": "1",
                "tax_id": "210",
                "accession": "A0A2T6RV84",
                "accession_with_isoform": "A0A2T6RV84",
                "database": "UNP",
                "polymer_type": "PROTEIN",
                "molecule_name": "Acyl carrier protein",
            },
            {
                "stoichiometry": "1",
                "tax_id": "210",
                "accession": "A0A0B2DUK3",
                "accession_with_isoform": "A0A0B2DUK3",
                "database": "UNP",
                "polymer_type": "PROTEIN",
                "molecule_name": "Acyl carrier protein",
            },
            {
                "stoichiometry": "1",
                "tax_id": "210",
                "accession": "A0A0B2E3F3",
                "accession_with_isoform": "A0A0B2E3F3",
                "database": "UNP",
                "polymer_type": "PROTEIN",
                "molecule_name": "2-nitropropane dioxygenase",
            },
        ],
    }
}


class TestComplexName(TestCase):
    def setUp(self) -> None:
        self.username = "mock_username"
        self.password = "mock_password"
        self.bolt_uri = "neo4j://"
        self.csv_path = "test_path"
        # might need to remove this
        self.complex_portal_path = "pub/databases/IntAct/current/various/complex2pdb/"

    def test_complex_name(self):
        # test whether the method is returning complex name for general cases
        complex_obj = ProcessComplexName(
            self.bolt_uri,
            self.username,
            self.password,
            self.csv_path,
            os.path.join("tests", "data", "complexes_molecules.csv"),
            os.path.join("tests", "data", "complexes_components.csv"),
            self.complex_portal_path,
        )
        complex_obj.complex_data = mock_pdb_complexes_data_one
        complex_obj.process_complex_name()
        self.assertEqual(
            complex_obj.complex_data_dict["PDB-CPX-1"]["complex_name"], "MoeE5"
        )

    def test_complex_name_from_complex_portal(self):
        # test whether the method returns the complex name that has match to
        # Complex Portal
        complex_obj = ProcessComplexName(
            self.bolt_uri,
            self.username,
            self.password,
            self.csv_path,
            os.path.join("tests", "data", "complexes_molecules.csv"),
            os.path.join("tests", "data", "complexes_components.csv"),
            self.complex_portal_path,
        )
        complex_obj.complex_portal_entries = (
            mock_complex_portal_per_component_string_two
        )
        complex_obj.complex_portal_entries_no_stoch = (
            mock_complex_portal_component_string_no_stoch_two
        )
        complex_obj.complex_portal_names = mock_complex_portal_names_two
        complex_obj.complex_portal_dict = mock_complex_portal_component_dict_two
        complex_obj.complex_data = mock_pdb_complexes_data_two
        complex_obj.process_complex_name()
        print(complex_obj.complex_data_dict["PDB-CPX-7330"].keys())
        # self.assertEqual(
        #     complex_obj.complex_data_dict["PDB-CPX-7330"]["complex_portal_id"],
        #     "CPX-724",
        # )
        self.assertEqual(
            complex_obj.complex_data_dict["PDB-CPX-7330"]["complex_name"],
            "Centrin-2-SFI1 complex",
        )

    def test_complex_name_with_antibody(self):
        # test whether the method returns the complex name with antibody
        complex_obj = ProcessComplexName(
            self.bolt_uri,
            self.username,
            self.password,
            self.csv_path,
            os.path.join("tests", "data", "complexes_molecules.csv"),
            os.path.join("tests", "data", "complexes_components.csv"),
            self.complex_portal_path,
        )
        complex_obj.complex_data = mock_pdb_complexes_data_three
        complex_obj.process_complex_name()
        self.assertEqual(
            complex_obj.complex_data_dict["PDB-CPX-60"]["complex_name_type"],
            "protein name from UniProt and antibody",
        )
        self.assertEqual(
            complex_obj.complex_data_dict["PDB-CPX-60"]["complex_name"],
            "Genome polyprotein and ZV-48 Antibody scFv and ZV-48 Antibody scFv",
        )

    def test_rna_complex_name(self):
        # test whether the method returns rna-only complex name
        complex_obj = ProcessComplexName(
            self.bolt_uri,
            self.username,
            self.password,
            self.csv_path,
            os.path.join("tests", "data", "complexes_molecules.csv"),
            os.path.join("tests", "data", "complexes_components.csv"),
            self.complex_portal_path,
        )
        complex_obj.complex_data = mock_pdb_complexes_data_four
        complex_obj.process_complex_name()
        self.assertEqual(
            complex_obj.complex_data_dict["PDB-CPX-79007"]["complex_name"],
            "RNA",
        )

    def test_complex_name_with_additional_components(self):
        # test whether the method returns the complex name with additional components
        complex_obj = ProcessComplexName(
            self.bolt_uri,
            self.username,
            self.password,
            self.csv_path,
            os.path.join("tests", "data", "complexes_molecules.csv"),
            os.path.join("tests", "data", "complexes_components.csv"),
            self.complex_portal_path,
        )
        complex_obj.complex_portal_entries = (
            mock_complex_portal_per_component_string_five
        )
        complex_obj.complex_portal_entries_no_stoch = (
            mock_complex_portal_component_string_no_stoch_five
        )
        complex_obj.complex_portal_names = mock_complex_portal_names_five
        complex_obj.complex_portal_dict = mock_complex_portal_component_dict_five
        complex_obj.complex_data = mock_pdb_complexes_data_five
        complex_obj.process_complex_name()
        self.assertEqual(
            complex_obj.complex_data_dict["PDB-CPX-50289"]["complex_name_type"],
            "complex portal and RNA",
        )
        self.assertEqual(
            complex_obj.complex_data_dict["PDB-CPX-50289"]["complex_name"],
            "LSM2-8 complex and U4/U6 snRNA-associated-splicing factor PRP24 and RNA",
        )

    def test_complex_name_with_peptide(self):
        # test whether the method returns the complex name with peptide
        complex_obj = ProcessComplexName(
            self.bolt_uri,
            self.username,
            self.password,
            self.csv_path,
            os.path.join("tests", "data", "complexes_molecules.csv"),
            os.path.join("tests", "data", "complexes_components.csv"),
            self.complex_portal_path,
        )
        complex_obj.complex_data = mock_pdb_complexes_data_six
        complex_obj.process_complex_name()
        self.assertEqual(
            complex_obj.complex_data_dict["PDB-CPX-317"]["complex_name_type"],
            "protein name from UniProt and peptide",
        )
        self.assertEqual(
            complex_obj.complex_data_dict["PDB-CPX-317"]["complex_name"],
            "Cyanophycin synthetase and peptide",
        )

    def test_ribosome_complex_name(self):
        # test whether the method returns ribosome complex name
        complex_obj = ProcessComplexName(
            self.bolt_uri,
            self.username,
            self.password,
            self.csv_path,
            os.path.join("tests", "data", "complexes_molecules.csv"),
            os.path.join("tests", "data", "complexes_components.csv"),
            self.complex_portal_path,
        )
        complex_obj.complex_data = mock_pdb_complexes_data_seven
        complex_obj.process_complex_name()
        self.assertEqual(
            complex_obj.complex_data_dict["PDB-CPX-551"]["complex_name_type"],
            "ribosome",
        )
        self.assertEqual(
            complex_obj.complex_data_dict["PDB-CPX-551"]["derived_complex_name"],
            "30S ribosome subunit and tRNA and RNA",
        )

    # def test_pdbe_curated_complex_name(self):
    #     # test whether the method returns pdbe curated complex name
    #     complex_obj = ProcessComplexName(self.bolt_uri, self.username, self.password)
    #     complex_obj.complex_data = mock_pdb_complexes_data_eight
    #     complex_obj.process_complex_name()
    #     self.assertEqual(
    #         complex_obj.complex_data_dict["PDB-CPX-13341"]["complex_name_type"],
    #         "PDBe curated",
    #     )
    #     self.assertEqual(
    #         complex_obj.complex_data_dict["PDB-CPX-13341"]["complex_name"],
    #         "Adenylyl Cyclase",
    #     )

    def test_heterodimer_complex_name(self):
        # test whether the method returns heterodimer complex name
        complex_obj = ProcessComplexName(
            self.bolt_uri,
            self.username,
            self.password,
            self.csv_path,
            os.path.join("tests", "data", "complexes_molecules.csv"),
            os.path.join("tests", "data", "complexes_components.csv"),
            self.complex_portal_path,
        )
        complex_obj.complex_data = mock_pdb_complexes_data_nine
        complex_obj.process_complex_name()
        self.assertEqual(
            complex_obj.complex_data_dict["PDB-CPX-709"]["complex_name_type"],
            "heterodimer",
        )
