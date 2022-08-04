import csv
import logging


class GetAnnotatedName:
    """
    This class contains methods required for adding manually curated complex
    names to the complex naming process
    """

    def __init__(self, molecule_name_path, molecule_components_path):
        self.molecule_name_path = molecule_name_path
        self.molecule_components_path = molecule_components_path
        self.molecule_names = {}
        self.molecule_components = {}
        self.molecule_info = {}

    def get_data(self):
        """
        Gets the path of the csv files that contain the manually curated
        complexes annotation and invokes the methods that read the files.
        """
        logging.debug("Reading %s" % self.molecule_name_path)
        self._read_molecule_names(self.molecule_name_path)
        logging.debug("Reading %s" % self.molecule_components_path)
        self._read_components(self.molecule_components_path)
        logging.debug("Collating data")
        self._collate_data()

    def _read_molecule_names(self, molecule_name_file):
        """
        Reads the csv file and stores the complex name in a
        dictionary

        Args:
            molecule_name_file (csv file): Contains the description
            of the complex
        """
        with open(molecule_name_file) as in_file:
            data = csv.DictReader(in_file)
            for row in data:
                complex_id = row.get("complex_number")
                name = row.get("PDB101-name")

                self.molecule_names[complex_id.strip()] = name.strip()

    def _read_components(self, component_file):
        """
        Reads the csv file and stores the complex components information
        in a dictionary

        Args:
            component_file (csv file): Contains the components of
            a complex with their
            accessions
        """
        with open(component_file) as in_file:
            data = csv.DictReader(in_file)
            for row in data:
                complex_id = row.get("complex_number")
                accession = row.get("accession")
                stoichiometry = row.get("stoichiometry")
                if accession not in ["none", "", None]:
                    row_dict = {
                        "accession": accession.strip(),
                        "stoichiometry": stoichiometry.strip(),
                        "accession_stoichiometry": "{}_{}".format(
                            accession.strip(), stoichiometry.strip()
                        ),
                    }
                    self.molecule_components.setdefault(complex_id.strip(), []).append(
                        row_dict
                    )

    def _collate_data(self):
        """
        Aggregates the complexes components and names into a new
        dictionary
        """
        for complex_id in self.molecule_components:
            complex_name = self.molecule_names.get(complex_id)
            components = []
            for component in self.molecule_components[complex_id]:
                components.append(component.get("accession_stoichiometry"))
            if components:
                components_str = ",".join(sorted(components))
                self.molecule_info[components_str] = complex_name
