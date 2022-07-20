import csv


class GetAnnotatedName:
    def __init__(self, molecule_name_path, molecule_components_path):
        self.molecule_name_path = molecule_name_path
        self.molecule_components_path = molecule_components_path
        self.molecule_names = {}
        self.molecule_components = {}
        self.molecule_info = {}

    def get_data(self):
        """
        Gets the path of the csv files that contain the manually curated complexes
        annotation and invokes the methods that read the files.
        """
        # data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        # molecule_name_file = os.path.join(data_dir, "complexes_molecules.csv")
        # molecule_components_file = os.path.join(data_dir, "complexes_components.csv")
        self.read_molecule_names(self.molecule_name_path)
        self.read_components(self.molecule_components_path)
        self.collate_data()

    def read_molecule_names(self, molecule_name_file):
        """
        Reads the csv file and stores the complex name in a
        dictionary

        Args:
            molecule_name_file (csv file): Contains the description of the complex
        """
        with open(molecule_name_file) as in_file:
            data = csv.DictReader(in_file)
            for row in data:
                print(row)
                complex_id = row.get("complex_number")
                name = row.get("PDB101-name")

                self.molecule_names[complex_id.strip()] = name.strip()

    def read_components(self, component_file):
        """
        Reads the csv file and stores the complex components information
        in a dictionary

        Args:
            component_file (csv file): Contains the components of a complex with their
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

    def collate_data(self):
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

    def get_molecule_info(self):
        """
        Returns a dictionary of complexes containing their composition and
        names

        Returns:
            dict: The key of the dict is the complex components str while the value is
            the complex name
        """
        return self.molecule_info


if __name__ == "__main__":
    gan = GetAnnotatedName(
        "/Users/sria/desktop/complex-data-process/complexes/data/complexes_molecules.csv",
        "/Users/sria/desktop/complex-data-process/complexes/data/complexes_components.csv",
    )
    gan.get_data()
    ret = gan.get_molecule_info()
    print(len(ret))
