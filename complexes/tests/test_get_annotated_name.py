from unittest import TestCase

from complexes.utils.get_annotated_name import GetAnnotatedName


class TestGetAnnotatedName(TestCase):
    def setUp(self) -> None:
        self.gan = GetAnnotatedName()

    def test_get_data(self):
        self.gan.get_data()

        # Test if method returns the correct name
        self.assertEqual("AAA+ proteases", self.gan.molecule_names["1"])
        self.assertEqual(
            "ABO Blood Type Glycosyltransferases", self.gan.molecule_names["2"]
        )

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
