import argparse
from collections import OrderedDict
from complexes import queries as qy
import csv
import hashlib
import os
from py2neo import Graph
import time


class Neo4JProcessComplex:
    def __init__(self, bolt_uri, username, password, csv_path):
        self.graph = None
        self.bolt_uri = bolt_uri
        self.username = username
        self.password = password
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

    def close(self):
        self._driver.close()

    def use_persistent_identifier(
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
        basic_PDB_complex_str = "PDB-CPX-"
        initial_num = 100001
        if hash_str in self.reference_mapping:
            pdb_complex_id = self.reference_mapping.get(hash_str).get("pdb_complex_id")
        # when the dict is empty
        elif len(self.reference_mapping) == 0:
            # identifier = len(self.reference_mapping) + 1
            pdb_complex_id = basic_PDB_complex_str + str(initial_num)
            # print("This is new complex id {pdb_complex_id}")
            # print(complex_portal_id)
            self.reference_mapping[hash_str] = {
                "pdb_complex_id": pdb_complex_id,
                "complex_portal_id": complex_portal_id,
                "accession": accession,
                "entries": entries,
            }
        # when the dict has one or more elems
        elif len(self.reference_mapping) >= 1:
            # last_dict_key = list(self.reference_mapping.keys())[-1]
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

    # def check_reference_data(self):
    #     conn = create_db_connection(self.db_conn_str)

    #     with conn as connection:
    #         query = connection.execute("SELECT * FROM COMPLEX_REFERENCE_MAPPING")

    #         if query:
    #             for row in query:
    #                 self.reference_mapping[row[0]] = {"pdb_complex_id": row[2],
    #                                             "accession": row[1]}

    #             return self.reference_mapping

    # def export_data(self):
    #     data = [(k, v['accession'], v['pdb_complex_id']) for k,
    #              v in self.reference_mapping.items()]
    #     conn = create_db_connection(self.db_conn_str)

    #     with conn as connection:
    #         empty_table_command = "TRUNCATE TABLE COMPLEX_REFERENCE_MAPPING"
    #         insert_data_command = "INSERT INTO COMPLEX_REFERENCE_MAPPING VALUES (:1, :2, :3)"
    #         connection.execute(empty_table_command)
    #         for row in data:
    #             connection.execute(insert_data_command, row)

    def export_csv(self):
        """
        Generate a csv file that contains complexes related information such as
        complex_composition, pdb_complex_id, complex_portal_id, assemblies and
        md5_obj representing the complex_composition
        """
        headers = [  # noqa: F841
            "pdb_complex_id",
            "complex_portal_id",
            "accession",
            "entries",
        ]
        # base_path = Path.cwd()
        base_path = self.csv_path
        filename = "complexes_mapping.csv"
        # csv_filename = (
        #     base_path.joinpath(filename)
        # )  # noqa: F841
        complete_path = os.path.join(base_path, filename)
        with open(complete_path, "w", newline="") as reference_file:
            file_csv = csv.writer(reference_file)
            file_csv.writerow(["md5_obj", *headers])
            for key, val in self.reference_mapping.items():
                file_csv.writerow([key] + [val.get(i, "") for i in headers])
        print("Complexes_mapping file has been produced")

    def get_graph(self):
        """
        Create an instance of Neo4j with the given connection
        parameters
        """
        self.graph = Graph(self.bolt_uri, user=self.username, password=self.password)

    def run_query(self, query, param=None):
        """
        Run Neo4j query

        Args:
            query (string): Neo4j query

        Returns:
            object: Neo4j query result
        """
        if not self.graph:
            self.get_graph()
        if param is not None:
            return self.graph.run(query, parameters=param)
        else:
            return self.graph.run(query)

    def get_complex_portal_data(self):
        """
        Gets and processes Complex Portal data - Complex Portal ID,
        complex composition str and entries
        """
        print("Querying Complex Portal data")
        mappings = self.run_query(query=qy.COMPLEX_PORTAL_DATA_QUERY)
        # rdict = [rec.data() for rec in mappings]
        # print(rdict)
        for row in mappings:
            accessions = row.get("uniq_accessions")
            complex_id = row.get("complex_id")
            entries = row.get("entries_str")
            self.dict_complex_portal_id[accessions] = complex_id
            self.dict_complex_portal_entries[complex_id] = entries

    def create_nodes_relationship(
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
        self.run_query(
            query_name,
            param={param_name: param_val},
        )
        print(f"Creating relationship between {n1_name} and {n2_name} nodes - DONE")

    def create_subcomplex_relationships(self):
        """
        Create subcomplex relationships in the graph db
        """
        return self.run_query(qy.CREATE_SUBCOMPLEX_RELATION_QUERY)

    def drop_PDBComplex_nodes(self):
        """
        Drop any existing PDB complex nodes in the graph db
        """
        return self.run_query(qy.DROP_PDB_COMPLEX_NODES_QUERY)

    def drop_existing_subcomplex_relationships(self):
        """
        Drop any existing subcomplex relationships in the graph db
        """
        return self.run_query(qy.DROP_SUBCOMPLEX_RELATION_QUERY)

    def process_assembly_data(self):
        """
        Aggregate unique complex compositions from PDB data, compares them to
        Complex Portal data and processes them for use later.
        """
        # Had to include this to run in local machine. We don\t need this now
        # cx_Oracle.init_oracle_client(lib_dir="/Users/sria/Downloads/instantclient_19_8")

        # Update self.reference_mapping if reference is available
        # self.reference_mapping = self.check_reference_data()
        print("Querying PDB Assembly data")
        mappings = self.run_query(qy.PDB_ASSEMBLY_DATA_QUERY)
        for row in mappings:
            # count += 1
            # (uniq_accessions, assemblies) = row

            uniq_accessions = row.get("accessions")
            assemblies = row.get("assemblies")

            # remove all occurences of NA_ from the unique complex combination
            tmp_uniq_accessions = uniq_accessions.replace("NA_", "")

            # pdb_complex_id = basic_complex_string + str(uniq_id)
            accession_hash = hashlib.md5(
                tmp_uniq_accessions.encode("utf-8")
            ).hexdigest()
            complex_portal_id = self.dict_complex_portal_id.get(tmp_uniq_accessions)

            # print(f"Printing Complex Portal ID: {complex_portal_id}")
            pdb_complex_id = self.use_persistent_identifier(
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

            for uniq_assembly in assemblies.split(","):
                # [entry, assembly_id] = uniq_assembly.split("_")
                [entry, _] = uniq_assembly.split("_")
                self.assembly_params_list.append(
                    {
                        "complex_id": str(pdb_complex_id),
                        "assembly_id": str(uniq_assembly),
                        "entry_id": str(entry),
                    }
                )

                # uniq_id += 1
            # print(f"Number of records: {count}")

        # create list of common Complex and PDB_Complex nodes
        for common_complex in self.common_complexes:
            (pdb_complex_id, complex_portal_id) = common_complex
            self.complex_params_list.append(
                {
                    "pdb_complex_id": str(pdb_complex_id),
                    "complex_portal_id": str(complex_portal_id),
                }
            )

        print("Done querying PDB Assembly data")
        print(len(self.reference_mapping))

        # for accessions in self.dict_complex_portal_id.keys():
        #     accession_hash = hashlib.md5(accessions.encode("utf-8")).hexdigest()
        #     complex_portal_id = self.dict_complex_portal_id[accessions]
        #     entries = self.dict_complex_portal_entries.get(complex_portal_id)
        #     pdb_complex_id = self.use_persistent_identifier(
        #         accession_hash, accessions, complex_portal_id, entries
        #     )

        #     # keep data for each PDB complex in dict_pdb_complex to be used later
        #     self.dict_pdb_complex[pdb_complex_id] = (accessions, entries)

        #     for item in accessions.split(","):
        #         [accession, stoichiometry, tax_id] = item.split("_")

        #         # this is the data from complex portal, there won't be any PDB entity
        #         # as a participant
        #         accession_params_list.append(
        #             {
        #                 "complex_id": str(pdb_complex_id),
        #                 "accession": str(accession),
        #                 "stoichiometry": str(stoichiometry),
        #             }
        #         )

    # def complex_portal_data_without_correspondence(self):
    #     for accession, complex_portal_id in self.dict_complex_portal_id.items():
    #         entries = self.dict_complex_portal_entries[complex_portal_id]
    #         self.complexes_unique_to_complex_portal.append((complex_portal_id,
    #                                                         accession,
    #                                                         entries))
    #     # print(self.complexes_unique_to_complex_portal)

    # def export_csv_debugging(self):
    #     with open('unique_complexes_from_complex_portal','w') as out:
    #         csv_out=csv.writer(out)
    #         csv_out.writerow(['complex_portal_id', 'accession', 'entries'])
    #         for row in self.complexes_unique_to_complex_portal:
    #             csv_out.writerow(row)

    def create_graph_relationships(self):
        """
        Create relationships between complexes related nodes in the
        graph db - Uniprot, PDBComplex, Entity, Rfam, Unmapped
        Polymer, Assembly and Complex
        """
        print("Start creating relationships betweeen nodes")
        # Create relationship between Uniprot and PDBComplex nodes
        self.create_nodes_relationship(
            query_name=qy.MERGE_ACCESSION_QUERY,
            n1_name="Uniprot",
            n2_name="PDBComplex",
            param_name="accession_params_list",
            param_val=self.accession_params_list,
        )
        # Create relationship between Entity and PDBComplex nodes
        self.create_nodes_relationship(
            query_name=qy.MERGE_ENTITY_QUERY,
            n1_name="Entity",
            n2_name="PDBComplex",
            param_name="entity_params_list",
            param_val=self.entity_params_list,
        )
        # Create relationship between UnmappedPolymer and PDBComplex nodes
        self.create_nodes_relationship(
            query_name=qy.MERGE_UNMAPPED_POLYMER_QUERY,
            n1_name="UnmappedPolymer",
            n2_name="PDBComplex",
            param_name="unmapped_polymer_params_list",
            param_val=self.unmapped_polymer_params_list,
        )
        # Create relationship between Rfam and PDBComplex nodes
        self.create_nodes_relationship(
            query_name=qy.MERGE_RFAM_QUERY,
            n1_name="Rfam",
            n2_name="PDBComplex",
            param_name="rfam_params_list",
            param_val=self.rfam_params_list,
        )
        # Create relationship between Assembly and PDBComplex nodes
        self.create_nodes_relationship(
            query_name=qy.MERGE_ASSEMBLY_QUERY,
            n1_name="Assembly",
            n2_name="PDBComplex",
            param_name="assembly_params_list",
            param_val=self.assembly_params_list,
        )
        # Create relationship between PDBComplex and Complex nodes
        self.create_nodes_relationship(
            query_name=qy.COMMON_COMPLEX_QUERY,
            n1_name="PDBComplex",
            n2_name="Complex",
            param_name="complex_params_list",
            param_val=self.complex_params_list,
        )
        print("Done creating relationships between nodes")


def main():
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
        help="Path to CSV file containing complexes information",
    )

    args = parser.parse_args()

    complex = Neo4JProcessComplex(
        bolt_uri=args.bolt_url,
        username=args.username,
        password=args.password,
        csv_path=args.csv_path,
    )

    complex.get_complex_portal_data()
    # complex.drop_PDBComplex_nodes()
    complex.process_assembly_data()
    # complex.create_graph_relationships()
    # complex.drop_existing_subcomplex_relationships()
    # complex.create_subcomplex_relationships()
    # complex.export_csv()


if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
