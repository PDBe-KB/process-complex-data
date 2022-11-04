import argparse

from pdbe_complexes.constants import complex_mapping_headers as headers_one
from pdbe_complexes.constants import complex_name_headers as headers_two
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
        "-m",
        "--uniprot-mapping-path",
        required=True,
        help="Path to the dir where the UniProt mapping text file is located",
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
        uniprot_mapping_path=args.uniprot_mapping_path,
    )
    complex.run_process()
    csv_params = (
        complex.reference_mapping,
        "md5_obj",
        headers_one,
        args.csv_path,
        "complexes_mapping.csv",
    )
    ut.export_csv(csv_params)

    complex = ProcessComplexName(
        bolt_uri=args.bolt_url,
        username=args.username,
        password=args.password,
        csv_path=args.csv_path,
        complex_portal_path=args.complex_portal_path,
    )
    complex.run_process()
    csv_params = (
        complex.updated_complex_name_dict,
        "pdb_complex_id",
        headers_two,
        args.csv_path,
        "complexes_name.csv",
    )
    ut.export_csv(csv_params)

    ut.merge_csv_files(args.csv_path)
    ut.clean_files(args.csv_path)


if __name__ == "__main__":
    main()
