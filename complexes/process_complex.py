from collections import OrderedDict
from complexes import queries as qy
from complexes.utils import utility as ut
from complexes.constants import complex_mapping_headers as csv_headers
import csv
import hashlib
import os

# TODO This class is doing two very different things - Split into two classes
# One should perform various Neo4j DB operations (drop, create, etc)
# The other should do the data processing


class Neo4JProcessComplex:
    # TODO I suggest this class should only do the data processing
    """
    This class is responsible for processing data related to unique complexes
    and to create persistent, unique complex identifiers
    """

    def __init__(self, bolt_uri, username, password, csv_path):
        # TODO Check if all this attributes are needed
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
        # TODO Check if the consecutive steps should depend on each other
        # E.g. should the pipeline stop if there's no data from complex portal? (I think yes)
        self.get_complex_portal_data()
        # TODO move drop_PDBComplex_nodes() to a new class
        self.drop_PDBComplex_nodes()
        self.get_reference_mapping()
        self.process_assembly_data()
        # TODO move create_graph_relationships() to a new class
        self.create_graph_relationships()
        # TODO move create_subcomplex_relationships() to a new class
        self.create_subcomplex_relationships()
        # # TODO I would consider moving this call outside of the class
        ut.export_csv(
            self.reference_mapping,
            "md5_obj",
            csv_headers,
            self.csv_path,
            "complexes_mapping.csv",
        )

    def get_complex_portal_data(self):
        """
        Gets and processes Complex Portal data - Complex Portal ID,
        complex composition str and entries

        Returns:
            none
        """
        print("Querying Complex Portal data")
        mappings = ut.run_query(self.neo4j_info, qy.COMPLEX_PORTAL_DATA_QUERY)
        for row in mappings:
            accessions = row.get("uniq_accessions")
            complex_id = row.get("complex_id")
            entries = row.get("entries_str")
            self.dict_complex_portal_id[accessions] = complex_id
            self.dict_complex_portal_entries[complex_id] = entries

    def drop_PDBComplex_nodes(self):
        """
        Drop any existing PDB complex nodes in the graph db
        """
        # TODO move this method to a new class that does Neo4j stuff
        return ut.run_query(self.neo4j_info, qy.DROP_PDB_COMPLEX_NODES_QUERY)

    def get_reference_mapping(self, reference_filename="complexes_master.csv"):
        """
        Store existing mapping of complex composition string to pdb_complex_id
        into a reference dictionary for lookup later

        Args:
            reference_filename (str, optional): Reference mapping file. Defaults to
                                                "complexes_master.csv".
        """
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
        print("Querying PDB Assembly data")
        mappings = ut.run_query(self.neo4j_info, qy.PDB_ASSEMBLY_DATA_QUERY)
        for row in mappings:
            self._process_mapping(row)

        # create list of common Complex and PDB_Complex nodes
        for common_complex in self.common_complexes:
            self._update_complex_params_list(common_complex)

        print("Done querying PDB Assembly data")

    def _process_mapping(self, row):
        uniq_accessions = row.get("accessions")
        assemblies = row.get("assemblies")
        # remove all occurences of NA_ from the unique complex combination
        tmp_uniq_accessions = uniq_accessions.replace("NA_", "")
        # pdb_complex_id = basic_complex_string + str(uniq_id)
        accession_hash = hashlib.md5(tmp_uniq_accessions.encode("utf-8")).hexdigest()
        complex_portal_id = self.dict_complex_portal_id.get(tmp_uniq_accessions)
        # print(f"Printing Complex Portal ID: {complex_portal_id}")
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

    def _create_nodes_relationship(
        self, query_name, n1_name, n2_name, param_name, param_val
    ):
        """
        Runs Neo4j query to create a relationship between a given pair of nodes

        Args:
            query_name (string): Neo4j query
            n1_name (string): first node name
            n2_name (string): second node name
            param_name (string): parameter name
            param_val (string): parameter value
        """
        print(f"Creating relationship between {n1_name} and {n2_name} nodes - START")
        ut.run_query(
            self.neo4j_info,
            query_name,
            param={param_name: param_val},
        )
        print(f"Creating relationship between {n1_name} and {n2_name} nodes - DONE")

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

    def create_graph_relationships(self):
        """
        Create relationships between complexes related nodes in the
        graph db - Uniprot, PDBComplex, Entity, Rfam, Unmapped
        Polymer, Assembly and Complex
        """
        # TODO move this method into a new class that does Neo4j stuff
        print("Start creating relationships betweeen nodes")
        # Create relationship between Uniprot and PDBComplex nodes
        self._create_nodes_relationship(
            query_name=qy.MERGE_ACCESSION_QUERY,
            n1_name="Uniprot",
            n2_name="PDBComplex",
            param_name="accession_params_list",
            param_val=self.accession_params_list,
        )
        # Create relationship between Entity and PDBComplex nodes
        self._create_nodes_relationship(
            query_name=qy.MERGE_ENTITY_QUERY,
            n1_name="Entity",
            n2_name="PDBComplex",
            param_name="entity_params_list",
            param_val=self.entity_params_list,
        )
        # Create relationship between UnmappedPolymer and PDBComplex nodes
        self._create_nodes_relationship(
            query_name=qy.MERGE_UNMAPPED_POLYMER_QUERY,
            n1_name="UnmappedPolymer",
            n2_name="PDBComplex",
            param_name="unmapped_polymer_params_list",
            param_val=self.unmapped_polymer_params_list,
        )
        # Create relationship between Rfam and PDBComplex nodes
        self._create_nodes_relationship(
            query_name=qy.MERGE_RFAM_QUERY,
            n1_name="Rfam",
            n2_name="PDBComplex",
            param_name="rfam_params_list",
            param_val=self.rfam_params_list,
        )
        # Create relationship between Assembly and PDBComplex nodes
        self._create_nodes_relationship(
            query_name=qy.MERGE_ASSEMBLY_QUERY,
            n1_name="Assembly",
            n2_name="PDBComplex",
            param_name="assembly_params_list",
            param_val=self.assembly_params_list,
        )
        # Create relationship between PDBComplex and Complex nodes
        self._create_nodes_relationship(
            query_name=qy.COMMON_COMPLEX_QUERY,
            n1_name="PDBComplex",
            n2_name="Complex",
            param_name="complex_params_list",
            param_val=self.complex_params_list,
        )
        print("Done creating relationships between nodes")

    def create_subcomplex_relationships(self):
        """
        Create subcomplex relationships in the graph db
        """
        # TODO move this method into a new class that does Neo4j stuff
        return ut.run_query(self.neo4j_info, qy.CREATE_SUBCOMPLEX_RELATION_QUERY)
