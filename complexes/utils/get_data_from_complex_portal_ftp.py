import logging
from posixpath import join as urljoin
import pandas as pd


class GetComplexPortalData:
    """
    This class deals with getting data from the Complex Portal
    """

    def __init__(self, complex_portal_path):
        self.complex_portal_ftp_root = "ftp://ftp.ebi.ac.uk/" + complex_portal_path
        self.complex_portal_https_root = "https://ftp.ebi.ac.uk/" + complex_portal_path
        self.complex_portal_components_tsv = "complex_portal_components.tsv"
        self.complex_portal_summary_tsv = "complex_portal_complexes.tsv"
        self.folders_to_check = ["released", "curation"]
        self.complex_portal_components = []
        self.complex_portal_summary = []
        self.complex_portal_names = {}
        self.complex_portal_component_string = {}
        self.complex_portal_per_component_string = {}
        self.complex_portal_per_component_string_no_stoch = {}
        self.complex_portal_component_dict = {}

    def run_process(self):
        """
        Runs the process of getting data from the Complex Portal
        Returns: None

        """
        for folder in self.folders_to_check:
            self.complex_portal_components.extend(
                self._get_data(
                    sub_folder=folder, file_name=self.complex_portal_components_tsv
                )
            )
            self.complex_portal_summary.extend(
                self._get_data(
                    sub_folder=folder, file_name=self.complex_portal_summary_tsv
                )
            )
        self._create_component_string()
        self._create_component_name_dict()

    def _create_component_string(self):
        """
        Creates the component string, e.g. 'CPX-7381': 'P27540_1,Q16665_1'
        """
        complex_portal_component_dict_no_stoch = {}
        complex_portal_component_dict = {}
        for row in self.complex_portal_components:
            complex_id = row.get("complex_id")
            database_accession = row.get("database_ac")
            database_name = row.get("database_name")
            stoichiometry = row.get("stoichiometry")
            if database_name == "uniprotkb":
                if database_accession in complex_portal_component_dict.get(
                    complex_id, {}
                ):
                    current_stoichiometry = complex_portal_component_dict.get(
                        complex_id, {}
                    )[database_accession]
                    stoichiometry = int(stoichiometry) + int(current_stoichiometry)
                    complex_portal_component_dict.setdefault(complex_id, {})[
                        database_accession
                    ] = int(stoichiometry)
                else:
                    complex_portal_component_dict.setdefault(complex_id, {})[
                        database_accession
                    ] = int(stoichiometry)

                complex_portal_component_dict_no_stoch.setdefault(
                    complex_id, set()
                ).add(database_accession)

        for complex_id in complex_portal_component_dict:
            for database_accession in complex_portal_component_dict[complex_id]:
                stoichiometry = complex_portal_component_dict[complex_id][
                    database_accession
                ]
                accession_with_stoichiometry = "{}_{}".format(
                    database_accession, stoichiometry
                )
                self.complex_portal_component_dict.setdefault(complex_id, []).append(
                    accession_with_stoichiometry
                )

        for complex_id in self.complex_portal_component_dict:
            component_string = ",".join(
                sorted(list(self.complex_portal_component_dict[complex_id]))
            )
            self.complex_portal_component_string[complex_id] = component_string
            self.complex_portal_per_component_string[component_string] = complex_id
            self.complex_portal_per_component_string_no_stoch[
                ",".join(
                    sorted(list(complex_portal_component_dict_no_stoch.get(complex_id)))
                )
            ] = complex_id

    def _create_component_name_dict(self):
        """
        Gets complex id and recommended name from Complex Portal data and
        assigns the name to the id in a dictionary
        """
        for row in self.complex_portal_summary:
            complex_id = row.get("complex_id")
            name = row.get("recommended_name")
            self.complex_portal_names[complex_id] = name

    def _get_data(self, sub_folder, file_name):
        """
        Retrieves data from the Complex Portal FTP and HTTPS
        Args:
            sub_folder: type str - Name of the subfolder
            file_name: type str - Name of the file

        Returns:

        """
        for root_url in [self.complex_portal_ftp_root, self.complex_portal_https_root]:
            try:
                ftp_file = urljoin(root_url, sub_folder, file_name)
                df = pd.read_csv(ftp_file, sep="\t")
                data = df.to_dict("records")
                if data:
                    return data
            except Exception as e:
                logging.error(e)
