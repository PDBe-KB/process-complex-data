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

    def __init__(self, bolt_uri, username, password, csv_path=None):

        self.neo4j_info = (bolt_uri, username, password)
        self.csv_path = csv_path
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

    def run_process(self):
        """
        Main method to run all the steps of the process

        Returns:
            none
        """

        self.get_complex_portal_data()
        # self.drop_PDBComplex_nodes()
        self.get_reference_mapping()
        self.process_assembly_data()
        # self.post_processing()
        # self.create_subcomplex_relationships()
        return self.reference_mapping

    def get_complex_portal_data(self):
        """
        Gets and processes Complex Portal data - Complex Portal ID,
        complex composition str and entries

        Returns:
            none
        """
        logger.info("Start querying Complex Portal data")
        mappings = ut.run_query(self.neo4j_info, qy.COMPLEX_PORTAL_DATA_QUERY)
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
        return ut.run_query(self.neo4j_info, qy.DROP_PDB_COMPLEX_NODES_QUERY)

    def get_reference_mapping(self, reference_filename="complexes_master.csv"):
        """
        Store existing mapping of complex-composition strings to pdb_complex_ids
        into a reference dictionary for lookup later

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

    def process_assembly_data(self):
        """
        Aggregate unique complex compositions from PDB data, compares them to
        Complex Portal data and processes them for use later.
        """
        logger.info("Start querying PDB Assembly data")
        mappings = ut.run_query(self.neo4j_info, qy.PDB_ASSEMBLY_DATA_QUERY)
        for row in mappings:
            self._process_mapping(row)

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

    def post_processing(self):
        """
        Create relationships between complexes related nodes in the
        graph db - Uniprot, PDBComplex, Entity, Rfam, Unmapped
        Polymer, Assembly and Complex
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

        ndo = Neo4jDatabaseOperations(self.neo4j_info)
        logger.info("Start creating relationships betweeen nodes")
        for params in query_parameters:
            ndo._create_nodes_relationship(
                params[0], params[1], params[2], params[3], params[4]
            )
        logger.info("Done creating relationships between nodes")

    def create_subcomplex_relationships(self):
        """
        Create subcomplex relationships in the graph db
        """
        logger.info("Creating subcomplex relationships")
        return ut.run_query(self.neo4j_info, qy.CREATE_SUBCOMPLEX_RELATION_QUERY)
