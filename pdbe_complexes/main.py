import argparse

from pdbe_complexes.get_complex_name import ProcessComplexName
from pdbe_complexes.process_complex import Neo4JProcessComplex
from pdbe_complexes.utils import utility as ut


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
        help="Path to output CSV file",
    )

    parser.add_argument(
        "-i",
        "--complex-portal-path",
        required=True,
        help="Path to Complex Portal ftp site",
    )

    args = parser.parse_args()

    complex = Neo4JProcessComplex(
        bolt_uri=args.bolt_url,
        username=args.username,
        password=args.password,
        csv_path=args.csv_path,
    )
    complex.run_process()

    complex = ProcessComplexName(
        bolt_uri=args.bolt_url,
        username=args.username,
        password=args.password,
        csv_path=args.csv_path,
        complex_portal_path=args.complex_portal_path,
    )
    complex.run_process()

    ut.merge_csv_files(args.csv_path)
    ut.clean_files(args.csv_path)
    ut.copy_file(args.csv_path)


if __name__ == "__main__":
    main()
