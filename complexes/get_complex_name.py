import argparse
from collections import Counter, OrderedDict
import csv

# from pdbecommon.graph import neo4j
# import neo4j
import logging

# from collections import OrderedDict
# from orc.base.log import logger

from complexes.utils.get_data_from_graph_db import GetComplexData

from complexes.utils.get_annotated_name import GetAnnotatedName
from complexes.utils.get_derived_name import DeriveName
from complexes.utils.get_data_from_complex_portal_ftp import GetComplexPortalData
import os

name_exclude_list = ["subunit", "component", "chain"]


class ProcessComplexName:
    # def __init__(self, complex_data):
    def __init__(
        self,
        bolt_uri,
        username,
        password,
        csv_path,
        molecule_name_path,
        molecule_components_path,
    ):
        # self._driver = neo4j.GraphDatabase.driver(bolt_uri, auth=(username, password))
        # self.complex_data = complex_data
        self.bolt_host = bolt_uri
        self.username = username
        self.password = password
        self.csv_path = csv_path
        self.molecule_name_path = molecule_name_path
        self.molecule_components_path = molecule_components_path
        self.complex_data = {}
        self.complex_data_dict = OrderedDict()
        self.complex_portal_entries = {}
        self.complex_portal_entries_no_stoch = {}
        self.complex_portal_names = {}
        self.complex_portal_dict = {}
        self.pdb_descriptions = {}
        self.pdb_info = {}
        self.annotated_names = {}
        self.antibody_names = {}
        self.prd_names = {}

        self.summary_data = []

        self.monomer_data = {}
        self.pdb_data = {}
        self.all_compositions = []
        self.pdb_entry_data = {}
        self.seen_complex_ids = set()
        self.unp_component_dict_with_stoch_per_complex_id = {}
        self.unp_component_dict_no_stoch_per_complex_id = {}
        self.unp_component_dict_with_stoch_dict_per_complex_id = {}
        self.unp_component_dict = {}
        self.non_unp_polymer_components_per_complex_id = {}
        self.individual_unp_component_dict = {}

        # individual components
        self.all_protein = True
        self.all_unp = True
        self.all_protein_unp = False
        self.components = []
        self.components_with_stoch = []
        self.unp_components_with_stoch_dict = {}
        self.unp_only_components = []
        self.unp_name_and_accession = {}
        self.unp_only_components_no_stoch = []
        self.antibody_components = []
        self.peptide_components = []
        self.peptide_components_names = []
        self.prd_components = []
        self.other_protein_components = []
        self.other_protein_components_names = set()
        self.rna_polymer_components = []
        self.rna_polymer_accessions = []
        self.rna_no_accession = []
        self.dna_polymer_components = []
        self.other_polymer_components = []
        self.non_unp_polymer_components = []
        self.go_terms = {}
        self.common_go_terms = []
        self.taxids = []
        self.polymers = []
        self.databases = []
        self.names = []
        self.unp_names = set()
        self.name_counter = Counter()
        self.derived_complex_name_list = []
        self.partial_complex_portal_id = []
        self.partial_mapping_to_complex_portal = {}
        self.stoichiometry_count = 0
        self.complex_portal_id = None
        self.unp_only_complex_portal_id = None
        self.pdb_entries = []
        self.entry_symmetry = {}
        self.complex_name_type = ""

    def run_processes(self):
        self.get_complex_portal_entries()
        self.get_pdb_complex_entries()
        self.process_complex_name()
        self.export_csv()

    def export_csv(self):
        headers = [
            # "complex_portal_id",
            "complex_name",
            "derived_complex_name",
            "complex_name_type",
        ]
        # base_path = Path.cwd()
        base_path = self.csv_path
        filename = "complexes_names.csv"
        # csv_filename = (
        #     base_path.joinpath("complexes").joinpath("output").joinpath(filename)
        # )  # noqa: F841
        complete_path = os.path.join(base_path, filename)
        with open(complete_path, "w", newline="") as complex_names:
            file_csv = csv.writer(complex_names)
            file_csv.writerow(["pdb_complex_id", *headers])
            for key, val in self.complex_data_dict.items():
                file_csv.writerow([key] + [val.get(i, "") for i in headers])
        print("Complexes names file has been produced")

    def get_complex_portal_entries(self):
        """
        Get complexes related data from Complex Portal
        """
        print("starting getting complex portal entries")
        cd = GetComplexPortalData()
        cd.run_process()
        self.complex_portal_entries = cd.get_complex_portal_per_component_string()
        self.complex_portal_entries_no_stoch = (
            cd.get_complex_portal_component_string_no_stoch()
        )
        self.complex_portal_names = cd.get_complex_portal_names()
        self.complex_portal_dict = cd.get_complex_portal_component_dict()
        print("finished getting complex portal entries")

    def get_pdb_complex_entries(self):
        """
        Get complexes related data from PDB graph database

        Returns:
            dict: Contains data relevant for complexes with the key
            being the PDB Complex ID
        """
        print("starting getting pdb complex entries")
        cd = GetComplexData(self.bolt_host, self.username, self.password)
        self.complex_data = cd.get_pdb_complex_data()
        print("finished getting pdb complex entries")
        return self.complex_data

    def get_annotated_names(self):
        gan = GetAnnotatedName(self.molecule_name_path, self.molecule_components_path)
        gan.get_data()
        self.annotated_names = gan.get_molecule_info()

    def check_annotated_name(self):
        """
        Returns the manually curated complex name if present

        Returns:
            str: manually curated complex name
        """
        if not self.annotated_names:
            self.get_annotated_names()
        unp_components_with_stoch_string = ",".join(sorted(self.unp_only_components))
        annotated_name = self.annotated_names.get(unp_components_with_stoch_string)
        return annotated_name

    def get_complex_portal_id(self, component_string):
        """
        Returns the Complex Portal ID for the given complex
        composition str

        Args:
            component_string (str): complex composition string

        Returns:
            str: Complex Portal ID
        """
        return str(self.complex_portal_entries.get(component_string, ""))

    def get_complex_portal_id_no_stoch(self, component_string_no_stoch):
        """
        Returns the Complex Portal ID for the given complex
        composition str without stoichiometry information

        Args:
            component_string (str): complex composition string without
            stoichiometry

        Returns:
            str: Complex Portal ID
        """
        return str(
            self.complex_portal_entries_no_stoch.get(component_string_no_stoch, "")
        )

    def get_partial_complex_portal_mapping(self):
        """
        Gets the Complex Portal entry that has partial mapping to the
        protein components

        Returns:
            dict: Contains the Complex Portal entry and its partial mapping
        """
        results = {}
        if self.unp_only_components:
            test_set = set(self.unp_only_components)
            for complex_portal_id in self.complex_portal_dict:
                complex_portal_data = set(self.complex_portal_dict[complex_portal_id])
                if complex_portal_data.issubset(test_set):
                    results[complex_portal_id] = self.complex_portal_dict[
                        complex_portal_id
                    ]

        return results

    def process_partial_complex_portal_mapping(self):
        """
        Processes and assigns name to complexes that have partial
        mappings to Complex Portal entries

        Returns:
            str: complex name
        """
        complex_name = ""
        potential_name_list = []
        complex_portal_names = []
        for complex_portal_id in self.partial_mapping_to_complex_portal:
            self.partial_complex_portal_id.append(complex_portal_id)
            unp_accessions_with_stoch = self.partial_mapping_to_complex_portal.get(
                complex_portal_id
            )
            for unp_accession_with_stoch in unp_accessions_with_stoch:
                unp_accession = unp_accession_with_stoch.split("_")[0]
                self.unp_name_and_accession.pop(unp_accession, None)
            ret = self.complex_portal_names.get(complex_portal_id, None)
            if ret:
                complex_portal_names.append(ret)

        if complex_portal_names:
            complex_portal_names_string = " and ".join(complex_portal_names)
            unp_name_list = []

            for unp in self.unp_name_and_accession:
                unp_name_list.append(self.unp_name_and_accession[unp].get("name"))

            # if no UNP accessions remain then this is a complex of Complex Portal complexes
            if len(unp_name_list) == 0:
                complex_name = complex_portal_names_string
                self.complex_name_type = "multi complex portal complex"
            # if only one UNP accession remaining then this is a binary complex
            # with one part being Complex Portal name
            elif len(unp_name_list) == 1:
                complex_name = "{} and {}".format(
                    complex_portal_names_string, "".join(unp_name_list)
                )
                self.complex_name_type = "complex portal and protein"
            else:
                potential_name_list.append(complex_portal_names_string)
            if complex_name:
                if self.rna_polymer_components:
                    complex_name = complex_name + " and RNA"
                    self.complex_name_type = "complex portal and RNA"
                if self.dna_polymer_components:
                    complex_name = complex_name + " and DNA"
                    self.complex_name_type = "complex portal and DNA"

        return complex_name, potential_name_list

    def get_complex_portal_name(self):
        """
        Returns complex name from Complex Portal if a match is present

        Returns:
            str: complex name
        """
        complex_name = ""
        if self.complex_portal_id:
            complex_name = self.complex_portal_names.get(self.complex_portal_id)
        elif self.unp_only_complex_portal_id:
            complex_name = self.complex_portal_names.get(
                self.unp_only_complex_portal_id
            )
            if self.rna_polymer_components:
                complex_name = complex_name + " and RNA"
            if self.dna_polymer_components:
                complex_name = complex_name + " and DNA"
            if self.antibody_components:
                complex_name = complex_name + " and antibody"
            if self.prd_components:
                complex_name = complex_name + " and ".join(self.prd_components)
            if self.peptide_components:
                complex_name = complex_name + " and peptide"
            if self.other_protein_components:
                complex_name = complex_name + " and additional unmapped proteins"
        return complex_name

    def get_complex_name(self):
        """
        Returns the complex name

        Returns:
            str: complex_name
        """
        complex_name = self.get_complex_portal_name()
        if complex_name:
            print(complex_name)
            logging.debug(complex_name)
            self.complex_name_type = "complex portal"
        elif len(self.unp_names) == 1 and self.all_protein_unp:
            complex_name = "".join(self.unp_names)
            self.complex_name_type = "protein name from UniProt"
            if self.rna_polymer_components:
                complex_name = complex_name + " and RNA"
                self.complex_name_type = "protein name from UniProt and RNA"
            if self.dna_polymer_components:
                complex_name = complex_name + " and DNA"
                self.complex_name_type = "protein name from UniProt and DNA"
        elif len(self.pdb_entries) == 1:
            if len(self.unp_names) == 1 and not self.all_protein_unp:
                complex_names = []
                complex_names.extend(self.unp_names)
                additional_names = ["UniProt"]
                if self.antibody_components:
                    complex_names.extend(self.antibody_components)
                    additional_names.append("antibody")
                if self.prd_components:
                    complex_names.extend(self.prd_components)
                    additional_names.append("PRD")
                if self.peptide_components:
                    complex_names.append("peptide")
                    additional_names.append("peptide")
                complex_name = " and ".join(complex_names)
                self.complex_name_type = "protein name from {}".format(
                    " and ".join(additional_names)
                )
            if set(self.polymers) == {"PROTEIN"} and len(self.components) == 1:
                pdbid_assembly = self.pdb_entries[0]
                pdbid = pdbid_assembly.split("_")[0]
                protein_entities = self.pdb_descriptions.get(pdbid, {})
                entity_names = set()
                for entity in protein_entities:
                    entity_names.add(protein_entities[entity])
                if entity_names:
                    complex_name = ",".join(entity_names)
                    self.complex_name_type = "protein name from entry"
        elif set(self.polymers) == {"DNA"}:
            complex_name = "DNA"
            self.complex_name_type = "DNA"
        elif set(self.polymers) == {"RNA"}:
            complex_name = "RNA"
            self.complex_name_type = "RNA"
        elif sorted(set(self.polymers)) == {"DNA", "RNA"}:
            complex_name = "DNA and RNA"
            self.complex_name_type = "DNA and RNA"

        return complex_name

    def check_ribosome(self):
        """
        Checks whether the complex is a ribosome

        Returns:
            str: potential name for the ribosome
        """
        skip_ribosome = False
        potential_name = ""
        if self.rna_polymer_accessions:
            if DeriveName().has_ribosomal_rna(self.rna_polymer_accessions):
                logging.debug("has ribosomal RNA")
                potential_name = DeriveName().get_name_from_names_for_ribosome(
                    self.unp_name_and_accession, cut_off=1
                )
                if potential_name:
                    skip_ribosome = True
        if not skip_ribosome:
            potential_name = DeriveName().get_name_from_names_for_ribosome(
                self.unp_name_and_accession, cut_off=15
            )
        logging.debug(potential_name)

        return potential_name

    def check_go(self):
        """
        Checks whether the complex has a GO term associated with it and
        assigns the predefined derived name if it matches

        Returns:
            bool: True/False
        """
        found_match = False
        if self.common_go_terms:
            potential_name = DeriveName().get_name_from_go(self.common_go_terms)
            if potential_name:
                found_match = True
                self.derived_complex_name_list.append(potential_name)
        return found_match

    def check_trna(self):
        """
        Checks whether the complex has tRNA
        """
        if self.rna_polymer_accessions and self.derived_complex_name_list:
            if DeriveName().has_trna(self.rna_polymer_accessions):
                self.derived_complex_name_list.append("tRNA")

    def process_complex_name(self):  # noqa: C901
        """
        The primary method that contains the logic for processing
        complexes data from Complex Portal and PDB to assign
        names to the complexes
        """
        # self.get_complex_portal_entries()

        # pdb_complex_data = self.get_pdb_complex_entries()
        for complex_id in self.complex_data:

            self.all_protein = True
            self.all_unp = True
            self.all_protein_unp = True
            self.components = []
            self.components_with_stoch = []
            self.unp_components_with_stoch_dict = {}
            self.unp_only_components = []
            self.unp_name_and_accession = {}
            self.unp_only_components_no_stoch = []
            self.peptide_components = []
            self.peptide_components_names = []
            self.prd_components = []
            self.antibody_components = []
            self.other_protein_components = []
            self.other_protein_components_names = set()
            self.rna_polymer_components = []
            self.rna_polymer_accessions = []
            self.rna_no_accession = []
            self.dna_polymer_components = []
            self.other_polymer_components = []
            self.non_unp_polymer_components = []
            self.go_terms = {}
            self.common_go_terms = []
            self.taxids = []
            self.polymers = []
            self.databases = []
            self.names = []
            self.unp_names = set()
            self.name_counter = Counter()

            self.derived_complex_name_list = []
            self.partial_complex_portal_id = []
            self.partial_mapping_to_complex_portal = {}
            self.stoichiometry_count = 0
            self.pdb_entries = []

            self.complex_portal_id = None
            self.unp_only_complex_portal_id = None

            derived_complex_name = ""
            self.complex_name_type = ""
            components = self.complex_data[complex_id].get("components", [])

            for row in components:
                # complex_id = row.get('pdb_complex_id')
                polymer_type = row.get("polymer_type", "")
                database = row.get("database", "")
                accession = row.get("accession", "")
                tax_id = row.get("tax_id", "")
                name = row.get("molecule_name", "")
                is_antibody = row.get("is_antibody", "")
                pdb_entity = row.get("pdb_entity", "")
                stoichiometry = row.get("stoichiometry", 0)
                # entity_length = row.get("entity_length")
                if not stoichiometry:
                    stoichiometry = 0
                self.stoichiometry_count += int(stoichiometry)

                monomer = True
                if stoichiometry:
                    if int(stoichiometry) > 1:
                        monomer = False
                if complex_id in self.monomer_data:
                    monomer = False
                self.monomer_data[complex_id] = monomer

                uniq_id = accession if accession else polymer_type
                self.components.append(uniq_id)

                if tax_id:
                    self.taxids.append(tax_id)
                if polymer_type:
                    self.polymers.append(polymer_type)
                if database:
                    self.databases.append(database)

                component = "{}_{}".format(uniq_id, stoichiometry)
                self.components_with_stoch.append(component)

                if database != "UNP":
                    self.non_unp_polymer_components.append(component)

                if polymer_type == "PROTEIN":
                    if database == "UNP":
                        self.unp_only_components.append(component)
                        self.unp_only_components_no_stoch.append(accession)
                        self.individual_unp_component_dict.setdefault(
                            accession, set()
                        ).add(complex_id)
                        self.unp_components_with_stoch_dict[accession] = int(
                            stoichiometry
                        )
                        self.unp_names.add(name)

                        name_list = name.split(" ")
                        # check the name has a name like "subunit" etc...
                        if [x for x in name_list if x.lower() in name_exclude_list]:
                            for sub_name in name_list:
                                if sub_name.lower() not in name_exclude_list:
                                    self.name_counter[sub_name] += 1
                        component_go_terms = self.unp_component_dict.get(accession, [])
                        self.unp_name_and_accession[accession] = {
                            "name": name,
                            "go_terms": component_go_terms,
                        }
                        for go_term in component_go_terms:
                            self.go_terms.setdefault(go_term, []).append(accession)
                    elif is_antibody:
                        self.antibody_components.append(name)
                        # update the name with the name of the antibody
                        name = self.antibody_names.get(pdb_entity, name)
                    elif self.prd_names.get(pdb_entity):
                        name = self.prd_names.get(pdb_entity)
                        self.prd_components.append(name)
                    elif name in (
                        "peptide",
                        "short peptide",
                        "synthetic peptide",
                        "synthetic short peptide",
                    ):
                        self.peptide_components.append(component)
                        self.peptide_components_names.append(name)
                    else:
                        self.other_protein_components.append(component)
                        self.other_protein_components_names.add(name)
                elif polymer_type == "RNA":
                    self.rna_polymer_components.append(component)
                    if database == "Rfam":
                        self.rna_polymer_accessions.append(accession)
                    else:
                        self.rna_no_accession.append(component)
                elif polymer_type == "DNA":
                    self.dna_polymer_components.append(component)
                else:
                    self.other_polymer_components.append(polymer_type)

                if name:
                    self.names.append(name)

            if set(self.polymers) != {"PROTEIN"}:
                self.all_protein = False
            if set(self.databases) != {"UNP"}:
                self.all_unp = False

            # if any non-UNP protein component set all_protein_unp to False
            if (
                self.other_protein_components
                or self.antibody_components
                or self.peptide_components
                or self.prd_components
            ):
                self.all_protein_unp = False
            if "PROTEIN" not in self.polymers:
                self.all_protein_unp = False

            self.pdb_entries = self.complex_data.get(complex_id, {}).get(
                "pdb_entries", []
            )

            components_with_stoch_string = ",".join(sorted(self.components_with_stoch))
            unp_components_with_stoch_string = ",".join(
                sorted(self.unp_only_components)
            )
            self.complex_portal_id = self.get_complex_portal_id(
                components_with_stoch_string
            )
            self.unp_only_complex_portal_id = self.get_complex_portal_id(
                unp_components_with_stoch_string
            )

            # components_with_no_stoch_string = ",".join(
            #     sorted(self.unp_only_components_no_stoch)
            # )
            # complex_portal_id_no_stoch = self.get_complex_portal_id_no_stoch(
            #     components_with_no_stoch_string
            # )

            # complex_portal_id_different_stoch = (
            #     complex_portal_id_no_stoch
            #     if complex_portal_id_no_stoch != self.unp_only_complex_portal_id
            #     else ""
            # )

            self.unp_component_dict_no_stoch_per_complex_id[
                complex_id
            ] = self.unp_only_components_no_stoch
            self.unp_component_dict_with_stoch_per_complex_id[
                complex_id
            ] = self.unp_only_components
            self.unp_component_dict_with_stoch_dict_per_complex_id[
                complex_id
            ] = self.unp_components_with_stoch_dict
            self.non_unp_polymer_components_per_complex_id[
                complex_id
            ] = self.non_unp_polymer_components

            # go terms
            for go_term in self.go_terms:
                if set(sorted(self.go_terms[go_term])) == set(
                    sorted(self.unp_only_components_no_stoch)
                ):
                    self.common_go_terms.append(go_term)

            # get a name for the complex
            complex_name = self.get_complex_name()

            # # check annotated names
            if not complex_name and self.unp_only_components:
                potential_name = self.check_annotated_name()
                print(potential_name)
                if potential_name:
                    complex_name = potential_name
                    self.complex_name_type = "PDBe curated"

            # check partial mapping to complex portal
            if not complex_name and self.unp_only_components:

                self.partial_mapping_to_complex_portal = (
                    self.get_partial_complex_portal_mapping()
                )
                if self.partial_mapping_to_complex_portal:
                    (
                        complex_name,
                        potential_name_list,
                    ) = self.process_partial_complex_portal_mapping()
                    if potential_name_list:
                        self.derived_complex_name_list.extend(potential_name_list)
                        self.complex_name_type = "complex portal super-complex"

            # common complexes identified by GO
            if not complex_name:
                found_match = self.check_go()
                if found_match:
                    self.complex_name_type = "GO"

                # ribosome
                if (
                    not found_match
                    and self.unp_name_and_accession
                    and self.rna_polymer_components
                ):
                    logging.debug("finding potential name for {}".format(complex_id))
                    potential_name = self.check_ribosome()

                    if potential_name:
                        logging.debug(potential_name)
                        self.derived_complex_name_list.append(potential_name)
                        self.complex_name_type = "ribosome"

                """
                protein complexes which haven't got a name elsewhere
                and are all "subunits" or "chains
                """
                if not self.derived_complex_name_list and self.all_protein_unp:
                    if self.name_counter:
                        num_unp_components = len(self.unp_only_components)
                        test_list = [
                            k
                            for k, v in self.name_counter.items()
                            if v == num_unp_components
                        ]
                        if len(test_list) > 1:
                            self.derived_complex_name_list.append(" ".join(test_list))
                            self.complex_name_type = "common name from entity names"

                # two protein complexes which haven't got a name elsewhere
                if (
                    not self.derived_complex_name_list
                    and self.all_protein_unp
                    and len(self.unp_names) == 2
                ):
                    self.derived_complex_name_list.extend(list(self.unp_names))
                    self.complex_name_type = "heterodimer"

            # check for tRNA
            self.check_trna()

            # join the names together to produce the final derived name
            if self.derived_complex_name_list:
                if self.rna_no_accession:
                    self.derived_complex_name_list.append("RNA")
                if self.dna_polymer_components:
                    self.derived_complex_name_list.append("DNA")
                derived_complex_name = " and ".join(self.derived_complex_name_list)

            if complex_name:
                complex_name = str(complex_name).strip()
            if derived_complex_name:
                derived_complex_name = str(derived_complex_name).strip()
            """
            if len(self.components) == 1:
                homo_hetero = "Homo"
            else:
                homo_hetero = "Hetero"
            """

            # print(f"Complex ID is:{complex_id} | Complex name is:{complex_name}
            # | Derived complex name is: {derived_complex_name}")

            self.complex_data_dict[complex_id] = {
                # "complex_portal_id": self.complex_portal_id,
                "complex_name": complex_name,
                "derived_complex_name": derived_complex_name,
                "complex_name_type": self.complex_name_type,
            }
        # print(self.complex_data_dict)
        # self.export_csv()


def run():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-b",
        "--bolt-url",
        required=True,
        help="BOLT url",
    )

    parser.add_argument(
        "-u",
        "--username",
        required=True,
        help="DB username",
    )

    parser.add_argument(
        "-p",
        "--password",
        required=True,
        help="DB password",
    )

    parser.add_argument(
        "-o",
        "--csv-path",
        required=True,
        help="Path to output CSV file containing complexes names",
    )

    parser.add_argument(
        "-i1",
        "--molecule-name-path",
        required=True,
        help="Path to input CSV file containing manually curated complexes names",
    )

    parser.add_argument(
        "-i2",
        "--molecule-components-path",
        required=True,
        help="Path to input CSV file containing manually curated complexes components",
    )

    args = parser.parse_args()

    complex = ProcessComplexName(
        bolt_uri=args.bolt_url,
        username=args.username,
        password=args.password,
        csv_path=args.csv_path,
        molecule_name_path=args.molecule_name_path,
        molecule_components_path=args.molecule_components_path,
    )

    complex.run_processes()


if __name__ == "__main__":
    run()
