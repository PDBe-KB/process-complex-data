from complexes.utils.get_data_from_graph_db import GetComplexData
from unittest import TestCase
from unittest.mock import patch

mock_uniprot_data = [
    {"accession": "A0A5X7JX66", "description": "Hemin uptake protein HemP"},
    {"accession": "A0A635N2X1", "description": "Flagellar biosynthesis protein FlgN"},
    {
        "accession": "A0A0H3VFB7",
        "description": "DNA-directed RNA polymerase (Fragment)",
    },
    {
        "accession": "A0A5U6N950",
        "description": "Branched-chain-amino-acid aminotransferase",
    },
    {
        "accession": "A0A5X6EKF7",
        "description": "SPI-1 type III secretion system export apparatus protein SpaR",
    },
]

mock_uniprot_molecule_names = {
    "A0A5X7JX66": "Hemin uptake protein HemP",
    "A0A635N2X1": "Flagellar biosynthesis protein FlgN",
    "A0A0H3VFB7": "DNA-directed RNA polymerase (Fragment)",
    "A0A5U6N950": "Branched-chain-amino-acid aminotransferase",
    "A0A5X6EKF7": "SPI-1 type III secretion system export apparatus protein SpaR",
}

mock_entity_data = [
    {"entity_uniqid": "6axm_3", "description": "PYROPHOSPHATE 2-"},
    {"entity_uniqid": "6axm_4", "description": "N-benzyl-N,N-diethylethanaminium"},
    {"entity_uniqid": "6b5y_1", "description": "Beta-lactamase"},
    {"entity_uniqid": "6b5y_2", "description": "PHOSPHATE ION"},
    {"entity_uniqid": "6b5y_3", "description": "Ceftriaxone"},
]

mock_entity_molecule_names = {
    "6axm_3": "PYROPHOSPHATE 2-",
    "6axm_4": "N-benzyl-N,N-diethylethanaminium",
    "6b5y_1": "Beta-lactamase",
    "6b5y_2": "PHOSPHATE ION",
    "6b5y_3": "Ceftriaxone",
}

mock_rfam_data = [
    {"accession": "RF04129", "description": "MIR4240 microRNA precursor family"},
    {"accession": "RF04130", "description": "MIR7996 microRNA precursor family"},
    {"accession": "RF04131", "description": "mir-2032 microRNA precursor family"},
    {"accession": "RF04132", "description": "mir-4436 microRNA precursor family"},
    {"accession": "RF04133", "description": "MIR2646 microRNA precursor family"},
]

mock_rfam_molecule_names = {
    "RF04129": "MIR4240 microRNA precursor family",
    "RF04130": "MIR7996 microRNA precursor family",
    "RF04131": "mir-2032 microRNA precursor family",
    "RF04132": "mir-4436 microRNA precursor family",
    "RF04133": "MIR2646 microRNA precursor family",
}

mock_pdb_complex_data = [
    {
        "complex_id": "PDB-CPX-1",
        "component_db": ["Assembly"],
        "component_type": "homo",
        "stoichiometry": None,
        "accession": None,
        "rfam_accession": None,
        "polymer_type": None,
        "taxonomy": None,
        "entry_assembly": "6kvc_1",
        "entity": "6kvc_1",
        "antibody": False,
        "entity_length": None,
    },
    {
        "complex_id": "PDB-CPX-1",
        "component_db": ["Assembly"],
        "component_type": "homo",
        "stoichiometry": None,
        "accession": None,
        "rfam_accession": None,
        "polymer_type": None,
        "taxonomy": None,
        "entry_assembly": "6kv9_1",
        "entity": "6kv9_1",
        "antibody": False,
        "entity_length": None,
    },
    {
        "complex_id": "PDB-CPX-1",
        "component_db": ["UniProt"],
        "component_type": None,
        "stoichiometry": "2",
        "accession": "A0A003",
        "rfam_accession": None,
        "polymer_type": None,
        "taxonomy": "67581",
        "entry_assembly": None,
        "entity": None,
        "antibody": False,
        "entity_length": None,
    },
    {
        "complex_id": "PDB-CPX-2",
        "component_db": ["Assembly"],
        "component_type": "hetero",
        "stoichiometry": None,
        "accession": None,
        "rfam_accession": None,
        "polymer_type": None,
        "taxonomy": None,
        "entry_assembly": "6v3b_1",
        "entity": "6v3b_1",
        "antibody": False,
        "entity_length": None,
    },
    {
        "complex_id": "PDB-CPX-2",
        "component_db": ["RfamFamily"],
        "component_type": None,
        "stoichiometry": None,
        "accession": None,
        "rfam_accession": "RF02543",
        "polymer_type": None,
        "taxonomy": None,
        "entry_assembly": None,
        "entity": None,
        "antibody": False,
        "entity_length": None,
    },
    {
        "complex_id": "PDB-CPX-2",
        "component_db": ["RfamFamily"],
        "component_type": None,
        "stoichiometry": None,
        "accession": None,
        "rfam_accession": "RF02540",
        "polymer_type": None,
        "taxonomy": None,
        "entry_assembly": None,
        "entity": None,
        "antibody": False,
        "entity_length": None,
    },
    {
        "complex_id": "PDB-CPX-2",
        "component_db": ["RfamFamily"],
        "component_type": None,
        "stoichiometry": None,
        "accession": None,
        "rfam_accession": "RF02541",
        "polymer_type": None,
        "taxonomy": None,
        "entry_assembly": None,
        "entity": None,
        "antibody": False,
        "entity_length": None,
    },
    {
        "complex_id": "PDB-CPX-2",
        "component_db": ["RfamFamily"],
        "component_type": None,
        "stoichiometry": None,
        "accession": None,
        "rfam_accession": "RF00001",
        "polymer_type": None,
        "taxonomy": None,
        "entry_assembly": None,
        "entity": None,
        "antibody": False,
        "entity_length": None,
    },
    {
        "complex_id": "PDB-CPX-2",
        "component_db": ["RfamFamily"],
        "component_type": None,
        "stoichiometry": None,
        "accession": None,
        "rfam_accession": "RF01959",
        "polymer_type": None,
        "taxonomy": None,
        "entry_assembly": None,
        "entity": None,
        "antibody": False,
        "entity_length": None,
    },
    {
        "complex_id": "PDB-CPX-2",
        "component_db": ["RfamFamily"],
        "component_type": None,
        "stoichiometry": None,
        "accession": None,
        "rfam_accession": "RF00177",
        "polymer_type": None,
        "taxonomy": None,
        "entry_assembly": None,
        "entity": None,
        "antibody": False,
        "entity_length": None,
    },
    {
        "complex_id": "PDB-CPX-53",
        "component_db": ["Assembly"],
        "component_type": "hetero",
        "stoichiometry": None,
        "accession": None,
        "rfam_accession": None,
        "polymer_type": None,
        "taxonomy": None,
        "entry_assembly": "7kcr_1",
        "entity": "7kcr_1",
        "antibody": False,
        "entity_length": None,
    },
    {
        "complex_id": "PDB-CPX-53",
        "component_db": ["Entity"],
        "component_type": "p",
        "stoichiometry": "60",
        "accession": None,
        "rfam_accession": None,
        "polymer_type": "P",
        "taxonomy": "9606",
        "entry_assembly": None,
        "entity": "7kcr_1",
        "antibody": True,
        "entity_length": "121",
    },
    {
        "complex_id": "PDB-CPX-53",
        "component_db": ["Entity"],
        "component_type": "p",
        "stoichiometry": "60",
        "accession": None,
        "rfam_accession": None,
        "polymer_type": "P",
        "taxonomy": "9606",
        "entry_assembly": None,
        "entity": "7kcr_2",
        "antibody": True,
        "entity_length": "107",
    },
    {
        "complex_id": "PDB-CPX-53",
        "component_db": ["UniProt"],
        "component_type": None,
        "stoichiometry": "180",
        "accession": "A0A024B7W1",
        "rfam_accession": None,
        "polymer_type": None,
        "taxonomy": "2043570",
        "entry_assembly": None,
        "entity": None,
        "antibody": False,
        "entity_length": None,
    },
    {
        "complex_id": "PDB-CPX-37",
        "component_db": ["Assembly"],
        "component_type": "hetero",
        "stoichiometry": None,
        "accession": None,
        "rfam_accession": None,
        "polymer_type": None,
        "taxonomy": None,
        "entry_assembly": "5j37_1",
        "entity": "5j37_1",
        "antibody": False,
        "entity_length": None,
    },
    {
        "complex_id": "PDB-CPX-37",
        "component_db": ["UnmappedPolymer"],
        "component_type": "DNA",
        "stoichiometry": None,
        "accession": None,
        "rfam_accession": None,
        "polymer_type": None,
        "taxonomy": None,
        "entry_assembly": None,
        "entity": None,
        "antibody": False,
        "entity_length": None,
    },
    {
        "complex_id": "PDB-CPX-37",
        "component_db": ["UniProt"],
        "component_type": None,
        "stoichiometry": "60",
        "accession": "A0A023R6W2",
        "rfam_accession": None,
        "polymer_type": None,
        "taxonomy": "77856",
        "entry_assembly": None,
        "entity": None,
        "antibody": False,
        "entity_length": None,
    },
]

mock_pdb_complexes = {
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
                "molecule_name": None,
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
                "molecule_name": None,
            },
            {
                "stoichiometry": 0,
                "tax_id": "",
                "accession": "RF02540",
                "database": "Rfam",
                "polymer_type": "RNA",
                "molecule_name": None,
            },
            {
                "stoichiometry": 0,
                "tax_id": "",
                "accession": "RF02541",
                "database": "Rfam",
                "polymer_type": "RNA",
                "molecule_name": None,
            },
            {
                "stoichiometry": 0,
                "tax_id": "",
                "accession": "RF00001",
                "database": "Rfam",
                "polymer_type": "RNA",
                "molecule_name": None,
            },
            {
                "stoichiometry": 0,
                "tax_id": "",
                "accession": "RF01959",
                "database": "Rfam",
                "polymer_type": "RNA",
                "molecule_name": None,
            },
            {
                "stoichiometry": 0,
                "tax_id": "",
                "accession": "RF00177",
                "database": "Rfam",
                "polymer_type": "RNA",
                "molecule_name": None,
            },
        ],
    },
    "PDB-CPX-53": {
        "pdb_complex_id": "PDB-CPX-53",
        "pdb_entries": ["7kcr"],
        "pdb_entries_with_assemblies": ["7kcr_1"],
        "components": [
            {
                "stoichiometry": "60",
                "tax_id": "9606",
                "polymer_type": "PROTEIN",
                "molecule_name": None,
                "is_antibody": True,
                "pdb_entity": "7kcr_1",
                "entity_length": 121,
            },
            {
                "stoichiometry": "60",
                "tax_id": "9606",
                "polymer_type": "PROTEIN",
                "molecule_name": None,
                "is_antibody": True,
                "pdb_entity": "7kcr_2",
                "entity_length": 107,
            },
            {
                "stoichiometry": "180",
                "tax_id": "2043570",
                "accession": "A0A024B7W1",
                "accession_with_isoform": "A0A024B7W1",
                "database": "UNP",
                "polymer_type": "PROTEIN",
                "molecule_name": None,
            },
        ],
    },
    "PDB-CPX-37": {
        "pdb_complex_id": "PDB-CPX-37",
        "pdb_entries": ["5j37"],
        "pdb_entries_with_assemblies": ["5j37_1"],
        "components": [
            {
                "stoichiometry": 0,
                "tax_id": "",
                "polymer_type": "DNA",
                "molecule_name": "DNA",
            },
            {
                "stoichiometry": "60",
                "tax_id": "77856",
                "accession": "A0A023R6W2",
                "accession_with_isoform": "A0A023R6W2",
                "database": "UNP",
                "polymer_type": "PROTEIN",
                "molecule_name": None,
            },
        ],
    },
}


class TestComplexData(TestCase):
    def setUp(self) -> None:
        self.username = "mock_username"
        self.password = "mock_password"
        self.bolt_uri = "neo4j://"

    @patch("complexes.utils.get_data_from_graph_db.GetComplexData._run_query")
    def test_uniprot_molecule_names(self, rq):
        complex_obj = GetComplexData(self.bolt_uri, self.username, self.password)
        rq.return_value = mock_uniprot_data
        complex_obj._populate_molecule_names_from_uniprot_or_rfam("uniprot")
        self.assertDictEqual(complex_obj.molecule_names, mock_uniprot_molecule_names)

    @patch("complexes.utils.get_data_from_graph_db.GetComplexData._run_query")
    def test_rfam_molecule_names(self, rq):
        complex_obj = GetComplexData(self.bolt_uri, self.username, self.password)
        rq.return_value = mock_rfam_data
        complex_obj._populate_molecule_names_from_uniprot_or_rfam("rfam")
        self.assertDictEqual(complex_obj.molecule_names, mock_rfam_molecule_names)

    @patch("complexes.utils.get_data_from_graph_db.GetComplexData._run_query")
    def test_entity_molecule_names(self, rq):
        complex_obj = GetComplexData(self.bolt_uri, self.username, self.password)
        rq.return_value = mock_entity_data
        complex_obj._populate_molecule_names_from_entity()
        self.assertDictEqual(complex_obj.molecule_names, mock_entity_molecule_names)

    @patch("complexes.utils.get_data_from_graph_db.GetComplexData._run_query")
    def test_get_pdb_complex_data(self, rq):
        complex_obj = GetComplexData(self.bolt_uri, self.username, self.password)
        rq.return_value = mock_pdb_complex_data
        complex_obj.get_pdb_complex_data()
        self.assertDictEqual(complex_obj.pdb_complexes, mock_pdb_complexes)

    @patch("complexes.utils.get_data_from_graph_db.Graph.run")
    def test_run_query(self, mock):
        mock.return_value = True
        complex_obj = GetComplexData(self.bolt_uri, self.username, self.password)
        complex_obj._run_query("foo")
        self.assertTrue(complex_obj.graph)