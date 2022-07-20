import logging
from posixpath import join as urljoin

# from pprint import pprint

import pandas as pd

complex_portal_path = "pub/databases/IntAct/current/various/complex2pdb/"
complex_portal_https = "https://ftp.ebi.ac.uk/" + complex_portal_path
complex_portal_ftp = "ftp://ftp.ebi.ac.uk/" + complex_portal_path


class GetComplexPortalData:
    def __init__(self):
        self.complex_portal_ftp_root = complex_portal_ftp
        self.complex_portal_https_root = complex_portal_https
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
        for folder in self.folders_to_check:
            self.complex_portal_components.extend(
                self.get_data(
                    sub_folder=folder, file_name=self.complex_portal_components_tsv
                )
            )
            self.complex_portal_summary.extend(
                self.get_data(
                    sub_folder=folder, file_name=self.complex_portal_summary_tsv
                )
            )
        self.create_component_string()
        self.create_component_name_dict()

    def create_component_string(self):
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

    def create_component_name_dict(self):
        for row in self.complex_portal_summary:
            complex_id = row.get("complex_id")
            name = row.get("recommended_name")
            self.complex_portal_names[complex_id] = name

    # Returns Complex Portal entries with missing stoichiometry
    def get_complex_portal_component_string_no_stoch(self):
        return self.complex_portal_per_component_string_no_stoch

    """
    Returns some basic information related to each chain in a complex such as
    the Complex Portal ID it belongs to, accession, accession database and
    stoichiometry.
    """

    def get_complex_portal_components(self):
        return self.complex_portal_components

    """
    Return summary information which includes assembly type (heterodimer etc),
    Complex Portal ID, recommended name, systematic name and version num
    """

    def get_complex_portal_summary(self):
        return self.complex_portal_summary

    # Returns the name of the Complex Portal entries
    def get_complex_portal_names(self):
        return self.complex_portal_names

    # Returns Complex Portal entries and their chain composition in string format
    def get_complex_portal_components_string(self):
        return self.complex_portal_component_string

    """
    Returns the complex chain composition and the corresponding Complex Portal ID
    in string format
    """

    def get_complex_portal_per_component_string(self):
        return self.complex_portal_per_component_string

    """
    Returns Complex Portal entries and their chain composition in dictionary format
    where the key is the Complex Portal ID while the value is a list of accessions
    """

    def get_complex_portal_component_dict(self):
        return self.complex_portal_component_dict

    def get_data(self, sub_folder, file_name):
        for root_url in [self.complex_portal_ftp_root, self.complex_portal_https_root]:
            try:
                ftp_file = urljoin(root_url, sub_folder, file_name)
                df = pd.read_csv(ftp_file, sep="\t")
                data = df.to_dict("records")
                if data:
                    return data
            except Exception as e:
                logging.error(e)


# def main():
#     cd = GetComplexPortalData()
#     cd.run_process()
#     ret = cd.get_complex_portal_component_dict()
#     # print(ret)
#     for k, v in ret.items():
#         if k == "CPX-44":
#             print(v)


# if __name__ == '__main__':
#     main()
