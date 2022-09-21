from py2neo import Graph

from pdbe_complexes.log import logger


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
        self.run_query(
            query_name,
            param={param_name: param_val},
        )
        logger.info(
            f"Creating relationship between {n1_name} and {n2_name} nodes - DONE"
        )

    def run_query(self, query, param=None):
        """General function to run neo4j query

        Args:
            neo4j_info (tuple): a tuple of 3-elems containing bolt_url, username and password
            query (str): neo4j query
            param (list of dict, optional): neo4j query params. Defaults to None.

        Returns:
            obj: neo4j query result
        """
        graph = Graph(
            self.neo4j_info[0], user=self.neo4j_info[1], password=self.neo4j_info[2]
        )

        if param:
            return graph.run(query, parameters=param)
        else:
            return graph.run(query)
