import csv
import pandas as pd
from py2neo import Graph
import os


def export_csv(data, key_name, headers, csv_path, filename):
    """General function to generate CSV file

    Args:
        data (dict): nested dict containing the desired data
        key_name (string): primary column name for aggregating the data
        headers (list): list of column names
        csv_path (str): output CSV path
        filename (str): the name of the output file
    """
    base_path = csv_path
    complete_path = os.path.join(base_path, filename)
    with open(complete_path, "w", newline="") as reference_file:
        file_csv = csv.writer(reference_file)
        file_csv.writerow([key_name, *headers])
        for key, val in data.items():
            file_csv.writerow([key] + [val.get(i, "") for i in headers])
    print(f"File {filename} has been produced")


def clean_files(
    csv_path, files_to_remove=("complexes_name.csv", "complexes_mapping.csv")
):
    """Removes the parent CSV files after merging them into a single file

    Args:
        csv_path (str): The path to the parent CSV files
        files_to_remove (tuple, optional): The files to remove. Defaults to
                                           ("complexes_mapping.csv",
                                            "complexes_mapping.csv").
    """
    for filename in files_to_remove:
        try:
            os.remove(os.path.join(csv_path, filename))
        except FileNotFoundError:
            print(f"File {filename} does not exist in {csv_path}")


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


def merge_csv_files(
    csv_path, filename1="complexes_mapping.csv", filename2="complexes_name.csv"
):
    """
    Merge the csv files produced by the proccesses above into a single file
    and reorder content

    Args:
        filename1 (str, optional): CSV file produced by the first process. Defaults to
                                   "complexes_mapping.csv".
        filename2 (str, optional): CSV file produced by the second process. Defaults to
                                   "complexes_names.csv".
    """
    output_filename = "complexes_master.csv"
    df1 = pd.read_csv(os.path.join(csv_path, filename1))
    df2 = pd.read_csv(os.path.join(csv_path, filename2))
    merged_df = df1.merge(df2, on="pdb_complex_id")
    merged_df["complex_name_merged"] = (
        merged_df["complex_name"]
        .combine_first(merged_df["derived_complex_name"])
        .astype(str)
    )
    merged_df.drop(["complex_name", "derived_complex_name"], axis=1, inplace=True)
    merged_df.rename({"complex_name_merged": "complex_name"}, axis=1, inplace=True)
    df = merged_df.reindex(
        columns=[
            "md5_obj",
            "pdb_complex_id",
            "complex_portal_id",
            "accession",
            "complex_name",
            "complex_name_type",
            "entries",
        ]
    )
    df["complex_name"] = df["complex_name"].replace({"nan": ""})
    df.to_csv(os.path.join(csv_path, output_filename), index=False)
    print(f"File {output_filename} has been produced")
