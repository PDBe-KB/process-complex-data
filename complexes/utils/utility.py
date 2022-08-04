import csv
from py2neo import Graph
import os


def export_csv(data, key_name, headers, csv_path, filename):
    """General function to generate CSV file

    Args:
        data (dict): nested dict containing the desired data
        key_name (string): primary column name for aggregating the data
        headers (list): list of column names
        csv_path (str): output CSV path
        filename (str): the name of the file
    """
    base_path = csv_path
    complete_path = os.path.join(base_path, filename)
    with open(complete_path, "w", newline="") as reference_file:
        file_csv = csv.writer(reference_file)
        file_csv.writerow([key_name, *headers])
        for key, val in data.items():
            file_csv.writerow([key] + [val.get(i, "") for i in headers])
    print(f"File {filename} has been produced")


def run_query(neo4j_info, query, param=None):
    """General function to run neo4j query

    Args:
        neo4j_info (tuple): a tuple of 3-elems containing bolt_url, username and password
        query (str): neo4j query
        param (list of dict, optional): neo4j query params. Defaults to None.

    Returns:
        obj: neo4j query result
    """
    graph = Graph(neo4j_info[0], user=neo4j_info[1], password=neo4j_info[2])

    if param is not None:
        return graph.run(query, parameters=param)
    else:
        return graph.run(query)
