import csv
import os


def export_csv(data, key_name, headers, csv_path, filename):
    """
    General utility function to produce a CSV file
    """
    base_path = csv_path
    complete_path = os.path.join(base_path, filename)
    with open(complete_path, "w", newline="") as reference_file:
        file_csv = csv.writer(reference_file)
        file_csv.writerow([key_name, *headers])
        for key, val in data.items():
            file_csv.writerow([key] + [val.get(i, "") for i in headers])
    print(f"File {filename} has been produced")
