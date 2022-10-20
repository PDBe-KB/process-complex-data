import csv
import os

import pandas as pd
import requests

from pdbe_complexes.log import logger


def export_csv(params):
    """General function to generate CSV file

    Args:
        params[0] (dict): nested dict containing the desired data
        params[1] (string): primary column name for aggregating the data
        params[2] (list): list of column names
        params[3] (str): output CSV path
        params[4] (str): the name of the output file
    """
    base_path = params[3]
    complete_path = os.path.join(base_path, params[4])
    with open(complete_path, "w", newline="") as reference_file:
        file_csv = csv.writer(reference_file)
        file_csv.writerow([params[1], *params[2]])
        for key, val in params[0].items():
            file_csv.writerow([key] + [val.get(i, "") for i in params[2]])
    logger.info(f"Filename {params[4]} has been written to {params[3]}")


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
            logger.info(f"Filename {filename} in {csv_path} has been deleted")
        except FileNotFoundError:
            logger.info(f"Filename {filename} does not exist in {csv_path}")


# def copy_file(src, dst=None, filename="complexes_master.csv"):
#     """
#     Utility function to copy file from one location to another

#     Args:
#         src (str): source path
#         dst (str, optional): target path. Defaults to None.
#     """
#     source_filepath = os.path.join(src, filename)
#     if dst:
#         shutil.copy2(source_filepath, dst)
#         logger.info(f"Filename {filename} has been copied to {dst}")


def process_complex_names(complex_names):
    flattened_name_list = [
        [k, v["complex_name"], v["derived_complex_name"], v["complex_name_type"]]
        for k, v in complex_names.items()
    ]
    df = pd.DataFrame(
        flattened_name_list,
        columns=[
            "pdb_complex_id",
            "complex_name",
            "derived_complex_name",
            "complex_name_type",
        ],
    )
    df["complex_name_merged"] = df["complex_name"].fillna("") + df[
        "derived_complex_name"
    ].fillna("")
    df.drop(["complex_name", "derived_complex_name"], axis=1, inplace=True)
    df.rename({"complex_name_merged": "complex_name"}, axis=1, inplace=True)
    pdb_complex_id_list = df["pdb_complex_id"].tolist()
    complex_name_list = df["complex_name"].tolist()
    complex_name_params_list = [
        {"pdb_complex_id": x, "complex_name": y}
        for x, y in zip(pdb_complex_id_list, complex_name_list)
    ]
    complex_name_dict = df.set_index("pdb_complex_id").T.to_dict()
    return complex_name_params_list, complex_name_dict


def get_uniprot_mapping():
    uniprot_mapping_dict = {}
    obsolete_uniprot_ids = []
    with open("/Users/sria/desktop/uniprot_mapping_new.txt") as f:
        for line in f:
            obsolete_uniprot_id, _, new_uniprot_id = line.strip().split(" ")
            uniprot_mapping_dict[obsolete_uniprot_id] = new_uniprot_id
            obsolete_uniprot_ids.append(obsolete_uniprot_id)
    return uniprot_mapping_dict, obsolete_uniprot_ids


def find_complexes_with_obsolete_id(data, obselete_identifiers):
    complexes_with_obselete_id = []
    for complex_string in data:
        for id in obselete_identifiers:
            if id in complex_string:
                complexes_with_obselete_id.append((complex_string, id))
    return complexes_with_obselete_id


def get_uniprot_taxid(identifier):
    uniprot_base_url = "https://rest.uniprot.org/uniprotkb/"
    uniprot_complete_url = f"{uniprot_base_url}/{identifier}"
    response = requests.get(uniprot_complete_url).json()
    return response["organism"]["taxonId"]


def create_new_complex_string(data, uniprot_mapping):
    replaced_complex_strings = {}
    for entry in data:
        obsolete_complex_string = entry[0]
        obsolete_accession = entry[1]
        new_accession = uniprot_mapping.get(obsolete_accession)
        obsolete_accession_taxid = get_uniprot_taxid(obsolete_accession)
        new_accession_taxid = get_uniprot_taxid(obsolete_accession)
        new_complex_string = obsolete_complex_string.replace(
            obsolete_accession, new_accession
        )
        if obsolete_accession_taxid != new_accession_taxid:
            obsolete_accession_taxid = "_" + str(obsolete_accession_taxid)
            new_accession_taxid = "_" + str(new_accession_taxid)
            new_complex_string = new_complex_string.replace(
                obsolete_accession_taxid, new_accession_taxid
            )
        replaced_complex_strings[obsolete_complex_string] = new_complex_string
    return replaced_complex_strings


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
    # merged_df["complex_name_merged"] = (
    #     merged_df["complex_name"]
    #     .combine_first(merged_df["derived_complex_name"])
    #     .astype(str)
    # )
    # merged_df.drop(["complex_name", "derived_complex_name"], axis=1, inplace=True)
    # merged_df.rename({"complex_name_merged": "complex_name"}, axis=1, inplace=True)
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
    # df["complex_name"] = df["complex_name"].replace({"nan": ""})
    df.to_csv(os.path.join(csv_path, output_filename), index=False)
    logger.info(f"Filename {output_filename} has been written to {csv_path}")
