from unittest import TestCase
from unittest.mock import patch
import os

from complexes.utils.get_annotated_name import GetAnnotatedName


stub_data = [
    {
        "complex_number": "1",
        "PDB101-name": "AAA+ proteases",
        "Source organism": "Haemophilus influenzae",
        "pdbid": "1g3i",
        "…mer": "24",
        "none1": "",
        "note": "1yyf - hetero 24mer, A,B P0A6H5, C,D P39070",
        "": "",
    }
]


class TestGetAnnotatedName(TestCase):
    # TODO Convert all the other tests to this format

    def setUp(self) -> None:
        self.gan = GetAnnotatedName(
            os.path.join('tests', 'data', 'complexes_molecules.csv'),
            os.path.join('tests', 'data', 'complexes_components.csv'))

    def test_get_data(self):
        self.gan.get_data()

        # Test if method returns the correct name
        self.assertEqual("AAA+ proteases",
                         self.gan.molecule_names["1"])
        self.assertEqual("ABO Blood Type Glycosyltransferases",
                         self.gan.molecule_names["2"])

        # Test if method returns the correct components name
        expected_result = [
            {
                "accession": "P43773",
                "stoichiometry": "12",
                "accession_stoichiometry": "P43773_12",
            },
            {
                "accession": "P43772",
                "stoichiometry": "12",
                "accession_stoichiometry": "P43772_12",
            },
        ]
        self.assertEqual(expected_result, self.gan.molecule_components["1"])


