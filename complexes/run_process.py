import argparse
import pandas as pd
from pathlib import Path
import subprocess
import shlex


def run_complexes(
    bolt_url, username, password, csv_path, molecule_name_path, molecule_components_path
):
    """
    Run the processes to aggregate/process complex data and assign
    name to complexes

    Args:
        bolt_url (str): bolt url
        username (str): neo4j username
        password (str): neo4j password
    """
    # First process to aggregate/process complex data
    first_process_cmd = f"python complexes/process_complex.py -b {bolt_url[0]} -u {username[0]} -p {password[0]} -o {csv_path[0]}"  # noqa: B950
    # Second process to assign name to complexes
    second_process_cmd = f"python complexes/get_complex_name.py -b {bolt_url[0]} -u {username[0]} -p {password[0]} -o {csv_path[0]} -i1 {molecule_name_path[0]} -i2 {molecule_components_path[0]}"  # noqa: B950

    subprocess.run(shlex.split(first_process_cmd))
    # subprocess.run(shlex.split(second_process_cmd))


def merge_csv_files(filename1="complexes_mapping.csv", filename2="complexes_names.csv"):
    """
    Merge the csv files produced by the proccesses above into a single file

    Args:
        filename1 (str, optional): Csv file produced by the first process. Defaults to
                                   "complexes_mapping.csv".
        filename2 (str, optional): Csv file produced by the second process. Defaults to
                                   "complexes_names.csv".
    """
    output_filename = "complexes_master.csv"
    base_path = Path.cwd()
    complete_path = base_path.joinpath("complexes").joinpath("output")
    df1 = pd.read_csv(complete_path.joinpath(filename1))
    df2 = pd.read_csv(complete_path.joinpath(filename2))
    merged_df = df1.merge(df2, on="pdb_complex_id")
    merged_df.to_csv(complete_path.joinpath(output_filename), index=False)


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
        help="Neo4j username",
    )

    parser.add_argument(
        "-p",
        "--password",
        required=True,
        help="Neo4j password",
    )

    parser.add_argument(
        "-o",
        "--path",
        required=True,
        help="Path to output complexes CSV file",
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

    bolt_url = (args.bolt_url,)
    username = (args.username,)
    password = (args.password,)
    csv_path = (args.path,)
    molecule_name_path = (args.molecule_name_path,)
    molecule_components_path = (args.molecule_components_path,)

    run_complexes(
        bolt_url,
        username,
        password,
        csv_path,
        molecule_name_path,
        molecule_components_path,
    )
    # merge_csv_files()


if __name__ == "__main__":
    main()
