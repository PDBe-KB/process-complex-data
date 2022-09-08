from pdbe_complexes.log import logger
from pdbe_complexes.utils import utility as ut


class Neo4jDatabaseOperations:
    def __init__(self, connection_params) -> None:
        self.neo4j_info = connection_params

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
        logger.info(
            f"Creating relationship between {n1_name} and {n2_name} nodes - START"
        )
        ut.run_query(
            self.neo4j_info,
            query_name,
            param={param_name: param_val},
        )
        logger.info(
            f"Creating relationship between {n1_name} and {n2_name} nodes - DONE"
        )
