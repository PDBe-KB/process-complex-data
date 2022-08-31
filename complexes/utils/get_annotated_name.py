import csv
import logging
import requests


class GetAnnotatedName:
    """
    This class contains methods required for adding manually curated complex
    names to the complex naming process
    """

    def __init__(self):
        self.molecule_name_url = """https://docs.google.com/spreadsheets/d/e/
                                    2PACX-1vT0qkSe3zrNxGFNkM
                                    _V0Y8fyhWWdrV6X50_gpObL3EAbnVbrw5VgFBr_
                                    GxEQCz0oLeQdzWFbGKuoFqU/
                                    pub?output=csv"""
        self.molecule_components_url = """https://docs.google.com/spreadsheets/d/e/
                                          2PACX-1vRUKkRAdzaVL9lDr2n4skuD_
                                          drXy9eAqSYnkNN2nBuCs6RRBiQ0n0Dq1RtiobaaXkm_
                                          y-Z3RzSfmu8m/
                                          pub?output=csv"""
        self.molecule_names = {}
        self.molecule_components = {}
        self.molecule_info = {}

    def get_data(self):
        """
        Gets the path of the csv files that contain the manually curated
        complexes annotation and invokes the methods that read the files.
        """
        logging.debug("Reading %s" % self.molecule_name_url)
        self._read_molecule_names(self.molecule_name_url)
        logging.debug("Reading %s" % self.molecule_components_url)
        self._read_components(self.molecule_components_url)
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
        with requests.get(molecule_name_file, stream=True) as r:
            lines = (line.decode("utf-8") for line in r.iter_lines())
            next(lines)
            for row in csv.reader(lines):
                complex_id = row[0].strip()
                name = row[1].strip()
                self.molecule_names[complex_id] = name

    def _read_components(self, component_file):
        """
        Reads the csv file and stores the complex components information
        in a dictionary

        Args:
            component_file (csv file): Contains the components of
            a complex with their
            accessions
        """
        with requests.get(component_file, stream=True) as r:
            lines = (line.decode("utf-8") for line in r.iter_lines())
            next(lines)
            for row in csv.reader(lines):
                complex_id = row[0].strip()
                accession = row[1].strip()
                stoichiometry = row[2].strip()
                if accession not in ["none", "", None]:
                    row_dict = {
                        "accession": accession,
                        "stoichiometry": stoichiometry,
                        "accession_stoichiometry": "{}_{}".format(
                            accession, stoichiometry
                        ),
                    }
                    self.molecule_components.setdefault(complex_id, []).append(row_dict)

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
