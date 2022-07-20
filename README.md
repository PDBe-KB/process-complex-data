# Basic information

This repository contains code for processes that will aggregate complexes data from the PDBe graph database, assign identifiers and create names for macromolecular complexes.

In general, it will do the following:
- Aggregate complexes data from the PDBe graph database
- Assign unique identifier for each unique complex composition
- Build relationships between several complexes related nodes in the graph database
- Assign name for each unique complex composition

# Usage

Clone this repository

`git clone git@gitlab.ebi.ac.uk:sria/complex-data-process.git`

Install dependencies with pip

`pip install -r requirements.txt`

usage: run_complexes.py -b <BOLT_URL> -u <NEO4J_USERNAME> -p <NEO4J_PASSWORD> -o <CSV_PATH>

`python complexes/run_complexes.py -b <bolt_url> -u <username> -p <password> -o <csv_path>`

# Package explanation

Executing the command above will run two separate processes sequentially: i) **process_complex.py** and ii) **get_complex_name.py**. The steps involved in each process are given below:

**process_complex.py**
- Gets complexes composition data from Complex Portal
- Drops existing PDBComplex nodes in the graph database
- Gets complexes composition data from PDBe graph database
- Assigns unique PDB complex identifer for each unique complex composition and Complex Portal identifer for consensus complex compositions
- Processes complexes composition data from the PDBe graph database in order to create relationships between selected pairs of nodes
- Creates relationships between six pairs of nodes: i) **Uniprot** and **PDBComplex**, ii) **Entity** and **PDBComplex**, iii) **UnmappedPolymer** and **PDBComplex**, iv) **Rfam** and **PDBComplex**, v) **Assembly** and **PDBComplex**, vi **Complex** and **PDBComplex**
- Drops existing subcomplex relationships
- Creates subcomplex relationships
- Creates a CSV file called "complexes_mapping.csv" that contains complexes related information except the names

**get_complex_name.py**
- Gets complexes related data from Complex Portal
- Gets complexes related data from PDBe graph database
- Assigns a complex name for each PDB Complex identifer if possible
- Creates a CSV file called "complexes_names.csv" that contains the names assigned to the complexes


In the final step, the two CSV files are merged together into a single CSV file called "complexes_master.csv" using the "pdb_complex_id" as the column to join on.

# Expected content of the CSV files (examples)




