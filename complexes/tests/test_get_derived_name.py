from complexes.utils.get_derived_name import DeriveName
from unittest import TestCase

test_params_one = {
    "A0A1V3DIZ9": {"name": "30S ribosomal protein S16", "go_terms": []},
    "B7I6V8": {"name": "50S ribosomal protein L27", "go_terms": []},
    "B7IA36": {"name": "50S ribosomal protein L2", "go_terms": []},
    "B7I7R9": {"name": "30S ribosomal protein S12", "go_terms": []},
    "B7IA26": {"name": "30S ribosomal protein S14", "go_terms": []},
    "V5VGC9": {"name": "50S ribosomal protein L20", "go_terms": []},
    "N8WQT6": {"name": "50S ribosomal protein L14", "go_terms": []},
}

test_params_two = {
    "B7IBC3": {"name": "50S ribosomal protein L9", "go_terms": []},
    "B7I7B6": {"name": "50S ribosomal protein L25", "go_terms": []},
    "B7IA23": {"name": "50S ribosomal protein L18", "go_terms": []},
    "B7IA38": {"name": "50S ribosomal protein L4", "go_terms": []},
    "N9DYI8": {"name": "50S ribosomal protein L34", "go_terms": []},
    "V5VGC9": {"name": "50S ribosomal protein L20", "go_terms": []},
    "B7IA24": {"name": "50S ribosomal protein L6", "go_terms": []},
    "S3NQR5": {"name": "50S ribosomal protein L28", "go_terms": []},
    "B7IA32": {"name": "50S ribosomal protein L16", "go_terms": []},
    "B7IA20": {"name": "50S ribosomal protein L15", "go_terms": []},
    "A0A1Y3CHB1": {"name": "50S ribosomal protein L36", "go_terms": []},
    "B7IA13": {"name": "50S ribosomal protein L17", "go_terms": []},
    "N8WQT6": {"name": "50S ribosomal protein L14", "go_terms": []},
    "B7IA31": {"name": "50S ribosomal protein L29", "go_terms": []},
    "B7IA36": {"name": "50S ribosomal protein L2", "go_terms": []},
    "B7IA39": {"name": "50S ribosomal protein L3", "go_terms": []},
    "B7IA27": {"name": "50S ribosomal protein L5", "go_terms": []},
    "B7IAS9": {"name": "50S ribosomal protein L19", "go_terms": []},
    "B7I6V9": {"name": "50S ribosomal protein L21", "go_terms": []},
    "B7I6V8": {"name": "50S ribosomal protein L27", "go_terms": []},
    "B7I7A4": {"name": "50S ribosomal protein L32", "go_terms": []},
    "B7I693": {"name": "50S ribosomal protein L35", "go_terms": []},
    "N9PPR9": {"name": "50S ribosomal protein L33", "go_terms": []},
    "B7IA37": {"name": "50S ribosomal protein L23", "go_terms": []},
    "B7IA28": {"name": "50S ribosomal protein L24", "go_terms": []},
    "N8V730": {"name": "50S ribosomal protein L30", "go_terms": []},
    "B7I9B0": {"name": "50S ribosomal protein L13", "go_terms": []},
    "A0A009QSN8": {"name": "50S ribosomal protein L22", "go_terms": []},
}

expected_ribosome_accessions = [
    "RF00001",  # 5S ribosomal RNA
    "RF00002",  # 5.8S ribosomal RNA
    "RF00177",  # Bacterial small subunit ribosomal RNA
    "RF01959",  # Archaeal small subunit ribosomal RNA
    "RF01960",  # Eukaryotic small subunit ribosomal RNA
    "RF02540",  # Archaeal large subunit ribosomal RNA
    "RF02541",  # Bacterial large subunit ribosomal RNA
    "RF02542",  # Microsporidia small subunit ribosomal RNA
    "RF02543",  # Eukaryotic large subunit ribosomal RNA
    "RF02545",  # Trypanosomatid mitochondrial small subunit ribosomal RNA
    "RF02546",  # Trypanosomatid mitochondrial large subunit ribosomal RNA
]


class TestGetDerivedName(TestCase):
    def setUp(self) -> None:
        self.dn = DeriveName()

    def test_get_name_from_go(self):
        # Test if method returns the correct GO name
        self.assertEqual(
            "Respiratory chain complex IV",
            self.dn.get_name_from_go(["respiratory chain complex IV"]),
        )
        # Test that the method doesn't break with incorrect GO name
        self.assertIsNone(self.dn.get_name_from_go(["foo"]))

    def test_has_ribosomal_rna(self):
        # Test whether rRNA Rfam accession is present
        message = "Test value is not true."
        self.assertTrue(self.dn.has_ribosomal_rna_or_trna(["RF00002"]), message)
        self.assertFalse(self.dn.has_ribosomal_rna_or_trna(["FOO"]), message)

    def test_has_trna(self):
        # Test whether tRNA Rfam accession is present
        message = "Test value is not true."
        self.assertTrue(self.dn.has_ribosomal_rna_or_trna(["RF00005"]), message)
        self.assertFalse(self.dn.has_ribosomal_rna_or_trna(["ASD"]), message)

    def test_get_name_from_names_for_ribosome(self):
        """
        Test the assignment of ribosome name based
        on the components presents
        """
        potential_name = self.dn.get_name_from_names_for_ribosome(
            test_params_one, cut_off=1
        )
        self.assertEqual("70S ribosome", potential_name)
