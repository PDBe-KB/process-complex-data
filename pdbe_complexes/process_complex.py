import argparse
import csv
import hashlib
import os
from collections import OrderedDict

from pdbe_complexes import queries as qy
from pdbe_complexes.log import logger
from pdbe_complexes.utils import utility as ut
from pdbe_complexes.utils.operations import Neo4jDatabaseOperations


class Neo4JProcessComplex:
    """
    This class is responsible for processing data related to unique complexes
    and to create persistent, unique complex identifiers
    """

    def __init__(self, bolt_uri, username, password, csv_path, uniprot_mapping_path):

        self.ndo = Neo4jDatabaseOperations((bolt_uri, username, password))
        self.csv_path = csv_path
        self.uniprot_mapping_path = uniprot_mapping_path
        self.dict_complex_portal_id = {}
        self.dict_complex_portal_entries = {}
        self.dict_pdb_complex = {}
        self.common_complexes = []
        self.reference_mapping = OrderedDict()
        self.accession_params_list = []
        self.entity_params_list = []
        self.assembly_params_list = []
        self.rfam_params_list = []
        self.complex_params_list = []
        self.unmapped_polymer_params_list = []
        self.complexes_unique_to_complex_portal = []
        self.existing_complexes_dict = {}
        self.new_complexes_dict = {}

    def run_process(self):
        """
        Main method to run all the steps of the process

        Returns:
            none
        """

        # self.get_complex_portal_data()
        # self.drop_PDBComplex_nodes()
        self.get_reference_mapping()
        self.correct_uniprot_mapping()
        # self.process_assembly_data()
        # self.post_processing()

    def get_complex_portal_data(self):
        """
        Gets and processes Complex Portal data - Complex Portal ID,
        complex composition str and entries

        Returns:
            none
        """
        logger.info("Start querying Complex Portal data")
        mappings = self.ndo.run_query(qy.COMPLEX_PORTAL_DATA_QUERY)
        for row in mappings:
            accessions = row.get("uniq_accessions")
            complex_id = row.get("complex_id")
            entries = row.get("entries_str")
            self.dict_complex_portal_id[accessions] = complex_id
            self.dict_complex_portal_entries[complex_id] = entries
        logger.info("Done querying Complex Portal data")

    def drop_PDBComplex_nodes(self):
        """
        Drop any existing PDB complex nodes in the graph db
        """
        return self.ndo.run_query(qy.DROP_PDB_COMPLEX_NODES_QUERY)

    def get_reference_mapping(self, reference_filename="complexes_master.csv"):
        """
        Store mapping of complex-composition strings to pdb_complex_ids
        into a reference dictionary for lookup if available

        Args:
            reference_filename (str, optional): Reference mapping file. Defaults to
                                                "complexes_master.csv".
        """
        logger.info("Start reading reference information")
        complete_filepath = os.path.join(self.csv_path, reference_filename)
        if os.path.exists(complete_filepath):
            with open(complete_filepath) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    self.reference_mapping[row["md5_obj"]] = {
                        "pdb_complex_id": row["pdb_complex_id"],
                        "complex_portal_id": row["complex_portal_id"],
                        "accession": row["accession"],
                        "entries": row["entries"],
                    }

    def update_reference_mapping(self, updated_complex_strings):
        for (
            obsolete_complex_string,
            new_complex_string,
        ) in updated_complex_strings.items():
            obsolete_complex_hash = hashlib.md5(
                obsolete_complex_string.encode("utf-8")
            ).hexdigest()
            new_complex_hash = hashlib.md5(
                new_complex_string.encode("utf-8")
            ).hexdigest()
            if new_complex_hash not in self.reference_mapping:
                self.reference_mapping[new_complex_hash] = {
                    "pdb_complex_id": self.reference_mapping[obsolete_complex_hash][
                        "pdb_complex_id"
                    ],
                    "complex_portal_id": self.reference_mapping[obsolete_complex_hash][
                        "complex_portal_id"
                    ],
                    "accession": new_complex_string,
                    "entries": self.reference_mapping[obsolete_complex_hash]["entries"],
                }
            del self.reference_mapping[obsolete_complex_hash]

    def _process_remaining_complex_portal_entries(self, accessions):
        """
        Assign pdb_complex_id to the remaining complex compositions
        from Complex Portal
        Args:
            accessions (str): Remaining complex composition strings
                              from Complex Portal
        """
        accession_hash = hashlib.md5(accessions.encode("utf-8")).hexdigest()
        complex_portal_id = self.dict_complex_portal_id[accessions]
        entries = self.dict_complex_portal_entries.get(complex_portal_id)
        pdb_complex_id = self._use_persistent_identifier(
            accession_hash, accessions, complex_portal_id, entries
        )

        # keep data for each PDB complex in dict_pdb_complex to be used later
        self.dict_pdb_complex[pdb_complex_id] = (accessions, entries)

        for item in accessions.split(","):
            [accession, stoichiometry, _] = item.split("_")

            # this is the data from complex portal, there won't be any PDB entity
            # as a participant
            self.accession_params_list.append(
                {
                    "complex_id": str(pdb_complex_id),
                    "accession": str(accession),
                    "stoichiometry": str(stoichiometry),
                }
            )

    def process_assembly_data(self):
        """
        Aggregate unique complex compositions from PDB data, compares them to
        Complex Portal data and processes them for use later.
        """
        logger.info("Start querying PDB Assembly data")
        mappings = self.ndo.run_query(qy.PDB_ASSEMBLY_DATA_QUERY)
        for row in mappings:
            self._process_mapping(row)

        for accessions in self.dict_complex_portal_id.keys():
            self._process_remaining_complex_portal_entries(accessions)

        # create list of common Complex and PDB_Complex nodes
        for common_complex in self.common_complexes:
            self._update_complex_params_list(common_complex)

        logger.info("Done querying PDB Assembly data")

    def _process_mapping(self, row):
        uniq_accessions = row.get("accessions")
        assemblies = row.get("assemblies")
        # remove all occurences of NA_ from the unique complex combination
        tmp_uniq_accessions = uniq_accessions.replace("NA_", "")
        accession_hash = hashlib.md5(tmp_uniq_accessions.encode("utf-8")).hexdigest()
        complex_portal_id = self.dict_complex_portal_id.get(tmp_uniq_accessions)
        pdb_complex_id = self._use_persistent_identifier(
            accession_hash, tmp_uniq_accessions, complex_portal_id, assemblies
        )
        # common complex; delete from dictionary else will be processed again
        if complex_portal_id is not None:
            del self.dict_complex_portal_id[tmp_uniq_accessions]
            self.common_complexes.append((pdb_complex_id, complex_portal_id))
        # keep data for each PDB complex in dict_pdb_complex to be used later
        self.dict_pdb_complex[pdb_complex_id] = (
            tmp_uniq_accessions,
            assemblies,
        )
        for uniq_accession in uniq_accessions.split(","):
            self._process_uniq_accession(pdb_complex_id, uniq_accession)
        for uniq_assembly in assemblies.split(","):
            self._process_uniq_assembly(pdb_complex_id, uniq_assembly)

    def _use_persistent_identifier(
        self, hash_str, accession, complex_portal_id, entries
    ):
        """
        This method generates a new PDB complex ID if the complex composition
        is new and not present in reference_mapping. On the other hand, if it's
        an existing complex composition then the existing ID is returned

        Args:
            hash_str (hash): md5 hash obj of complex composition
            accession (string): complex composition string
            complex_portal_id (string): Complex Portal identifier
            entries (string): assemblies

        Returns:
            string: PDB Complex ID
        """
        pdb_complex_id = ""
        basic_PDB_complex_str = "PDB-CPX-"
        initial_num = 100001
        if hash_str in self.reference_mapping:
            pdb_complex_id = self.reference_mapping.get(hash_str).get("pdb_complex_id")
            self.reference_mapping[hash_str]["entries"] = entries
            self.existing_complexes_dict[accession] = pdb_complex_id
        # when the dict is empty
        elif len(self.reference_mapping) == 0:
            pdb_complex_id = basic_PDB_complex_str + str(initial_num)
            self.reference_mapping[hash_str] = {
                "pdb_complex_id": pdb_complex_id,
                "complex_portal_id": complex_portal_id,
                "accession": accession,
                "entries": entries,
            }
        # when the dict has one or more elems
        elif len(self.reference_mapping) >= 1:
            last_dict_key = next(reversed(self.reference_mapping))
            last_pdb_complex_id = self.reference_mapping[last_dict_key][
                "pdb_complex_id"
            ]
            _, _, last_pdb_complex_id_num = last_pdb_complex_id.split("-")
            current_num = int(last_pdb_complex_id_num) + 1
            pdb_complex_id = basic_PDB_complex_str + str(current_num)
            self.reference_mapping[hash_str] = {
                "pdb_complex_id": pdb_complex_id,
                "complex_portal_id": complex_portal_id,
                "accession": accession,
                "entries": entries,
            }
        return pdb_complex_id

    def _process_uniq_assembly(self, pdb_complex_id, uniq_assembly):
        [entry, _] = uniq_assembly.split("_")
        self.assembly_params_list.append(
            {
                "complex_id": str(pdb_complex_id),
                "assembly_id": str(uniq_assembly),
                "entry_id": str(entry),
            }
        )

    def _process_uniq_accession(self, pdb_complex_id, uniq_accession):
        tokens = uniq_accession.split("_")
        # handle cases of PDB entity
        if len(tokens) == 4:
            [_, entry_id, entity_id, stoichiometry] = tokens
            self.entity_params_list.append(
                {
                    "complex_id": str(pdb_complex_id),
                    "entry_id": str(entry_id),
                    "entity_id": str(entity_id),
                    "stoichiometry": str(stoichiometry),
                }
            )

        # handle cases of UniProt
        elif len(tokens) == 3:
            [accession, stoichiometry, tax_id] = tokens
            self.accession_params_list.append(
                {
                    "complex_id": str(pdb_complex_id),
                    "accession": str(accession),
                    "stoichiometry": str(stoichiometry),
                }
            )

        # handle unmapped polymers and Rfam accessions
        elif len(tokens) == 1:
            token = tokens[0]

            # check for unmapped polymers (:UNMAPPED string)
            if ":UNMAPPED" in token:
                polymer_type = token.replace(":UNMAPPED", "")
                self.unmapped_polymer_params_list.append(
                    {
                        "complex_id": str(pdb_complex_id),
                        "polymer_type": str(polymer_type),
                    }
                )

            # handle Rfam
            else:
                self.rfam_params_list.append(
                    {
                        "complex_id": str(pdb_complex_id),
                        "rfam_acc": str(token),
                    }
                )

    def _update_complex_params_list(self, common_complex):
        (pdb_complex_id, complex_portal_id) = common_complex
        self.complex_params_list.append(
            {
                "pdb_complex_id": str(pdb_complex_id),
                "complex_portal_id": str(complex_portal_id),
            }
        )

    def correct_uniprot_mapping(self):
        logger.info("Start correcting obsolete UniProt mapping for complexes if any")
        uniprot_mapping_dict, obsolete_uniprot_ids = ut.get_uniprot_mapping(
            self.uniprot_mapping_path
        )
        complex_strings = [
            entry["accession"] for _, entry in self.reference_mapping.items()
        ]
        complexes_with_obsolete_id = ut.find_complexes_with_obsolete_id(
            complex_strings, obsolete_uniprot_ids
        )
        updated_complex_strings = ut.create_new_complex_string(
            complexes_with_obsolete_id, uniprot_mapping_dict
        )
        self.update_reference_mapping(updated_complex_strings)

    def post_processing(self):
        """
        1. Create relationships between complexes related nodes in the
        graph db - Uniprot, PDBComplex, Entity, Rfam, Unmapped
        Polymer, Assembly and Complex

        2. Drop existing subcomplex relationships

        3. Create new subcomplex relationships
        """
        query_parameters = [
            (
                qy.MERGE_ACCESSION_QUERY,
                "Uniprot",
                "PDBComplex",
                "accession_params_list",
                self.accession_params_list,
            ),
            (
                qy.MERGE_ENTITY_QUERY,
                "Entity",
                "PDBComplex",
                "entity_params_list",
                self.entity_params_list,
            ),
            (
                qy.MERGE_UNMAPPED_POLYMER_QUERY,
                "UnmappedPolymer",
                "PDBComplex",
                "unmapped_polymer_params_list",
                self.unmapped_polymer_params_list,
            ),
            (
                qy.MERGE_RFAM_QUERY,
                "Rfam",
                "PDBComplex",
                "rfam_params_list",
                self.rfam_params_list,
            ),
            (
                qy.MERGE_ASSEMBLY_QUERY,
                "Assembly",
                "PDBComplex",
                "assembly_params_list",
                self.assembly_params_list,
            ),
            (
                qy.COMMON_COMPLEX_QUERY,
                "PDBComplex",
                "Complex",
                "complex_params_list",
                self.complex_params_list,
            ),
        ]

        logger.info("Start creating relationships betweeen nodes")
        for params in query_parameters:
            self.ndo._create_nodes_relationship(
                params[0], params[1], params[2], params[3], params[4]
            )
        logger.info("Done creating relationships between nodes")

        logger.info("Dropping existing subcomplex relationships if any")
        self.ndo.run_query(qy.DROP_SUBCOMPLEX_RELATION_QUERY)

        logger.info("Start creating subcomplex relationships")
        self.ndo.run_query(qy.CREATE_SUBCOMPLEX_RELATION_QUERY)
        logger.info("Done creating subcomplex relationships")


if __name__ == "__main__":
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
        help="Path to the dir where the output CSV file should be created",
    )

    parser.add_argument(
        "-m",
        "--uniprot-mapping-path",
        required=True,
        help="Path to the dir where the UniProt mapping text file is located",
    )

    args = parser.parse_args()

    complex = Neo4JProcessComplex(
        bolt_uri=args.bolt_url,
        username=args.username,
        password=args.password,
        csv_path=args.csv_path,
        uniprot_mapping_path=args.uniprot_mapping_path,
    )
    complex.run_process()
