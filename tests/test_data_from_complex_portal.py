from complexes.utils.get_data_from_complex_portal_ftp import GetComplexPortalData
from unittest import TestCase

# from unittest.mock import patch

mock_components = [
    {
        "complex_id": "CPX-7381",
        "database_ac": "Q16665",
        "database_name": "uniprotkb",
        "stoichiometry": 1,
        "version": 1,
    },
    {
        "complex_id": "CPX-7381",
        "database_ac": "P27540",
        "database_name": "uniprotkb",
        "stoichiometry": 1,
        "version": 1,
    },
]

mock_summary = [
    {
        "complex_assembly": "Heterotetramer",
        "complex_id": "CPX-7343",
        "recommended_name": "Crotoxin complex, aCA3-bCA1-CBa variant",
        "systematic_name": "CA:CBa",
        "version": 1,
    },
    {
        "complex_assembly": None,
        "complex_id": "CPX-7114",
        "recommended_name": "Endoplasmic Reticulum Membrane Complex",
        "systematic_name": "Emc1:Emc2:Emc3:Emc4:Emc5:Emc6:Emc10:Sop4",
        "version": 1,
    },
]

mock_component_dict = {"CPX-7381": ["Q16665_1", "P27540_1"]}
mock_per_component_string = {"P27540_1,Q16665_1": "CPX-7381"}
mock_component_string = {"CPX-7381": "P27540_1,Q16665_1"}
mock_names = {
    "CPX-7343": "Crotoxin complex, aCA3-bCA1-CBa variant",
    "CPX-7114": "Endoplasmic Reticulum Membrane Complex",
}


class TestGetComplexPortalData(TestCase):
    def setUp(self) -> None:
        self.cp = GetComplexPortalData()

    def test_create_component_string(self):
        """
        Test whether the method creates complex components string
        using Complex Portal data
        """

        # Testing with empty {}
        result = self.cp.complex_portal_component_string
        self.assertEqual(result, {})

        # Testing the per component string with valid mock input
        self.cp.complex_portal_components = mock_components
        self.cp.create_component_string()
        self.assertEqual(self.cp.complex_portal_component_dict, mock_component_dict)
        self.assertEqual(
            self.cp.complex_portal_per_component_string, mock_per_component_string
        )

    def create_component_name(self):
        """
        Test whether the method creates complex names
        """

        # Testing with empty {}
        result = self.cp.complex_portal_names
        self.assertEqual(result, {})

        # Testing the name with valid mock input
        self.cp.complex_portal_summary = mock_summary
        self.cp.create_component_name_dict()
        self.assertEqual(
            self.cp.complex_portal_names["CPX-7114"], mock_names["CPX-7114"]
        )

    def test_get_complex_portal_components(self):
        # Test whether the method returns the Complex Portal components
        self.cp.complex_portal_components = mock_components
        result = self.cp.get_complex_portal_components()

        self.assertDictEqual(result[0], mock_components[0])

    def test_get_complex_portal_summary(self):
        # Test whether the method returns the Complex Portal summary
        self.cp.complex_portal_summary = mock_summary
        result = self.cp.get_complex_portal_summary()

        self.assertDictEqual(result[0], mock_summary[0])

    def test_get_complex_portal_names(self):
        # Test whether the method returns the complexes name
        self.cp.complex_portal_summary = mock_summary
        self.cp.create_component_name_dict()

        result = self.cp.get_complex_portal_names()

        self.assertDictEqual(result, mock_names)

    def test_get_complex_portal_component_dict(self):
        # Test whether the method returns the complex portal component dict
        self.cp.complex_portal_components = mock_components
        self.cp.create_component_string()

        result = self.cp.get_complex_portal_component_dict()

        self.assertDictEqual(result, mock_component_dict)

    def test_get_complex_portal_components_string(self):
        # Test whether the method returns the complex composition string
        self.cp.complex_portal_components = mock_components
        self.cp.create_component_string()

        result = self.cp.get_complex_portal_components_string()

        self.assertDictEqual(result, mock_component_string)

    def test_get_complex_portal_per_component_string(self):
        # Test whether the method returns the complex per component composition string
        self.cp.complex_portal_components = mock_components
        self.cp.create_component_string()

        result = self.cp.get_complex_portal_per_component_string()

        self.assertDictEqual(result, mock_per_component_string)
