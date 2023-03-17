[![CodeFactor](https://www.codefactor.io/repository/github/pdbe-kb/process-complex-data/badge)](https://www.codefactor.io/repository/github/pdbe-kb/process-complex-data)
[![Maintainability](https://api.codeclimate.com/v1/badges/aee4f254bddad263bf12/maintainability)](https://codeclimate.com/github/PDBe-KB/process-complex-data/maintainability)
[![run-tests](https://github.com/PDBe-KB/process-complex-data/actions/workflows/tests.yml/badge.svg)](https://github.com/PDBe-KB/process-complex-data/actions/workflows/tests.yml)
![GitHub](https://img.shields.io/github/license/pdbe-kb/process-complex-data)

Unique Complex Identifiers for the PDB archive
==

## Background

This repository contains code for a Python package that aggregates macromolecular complexes data from the PDBe graph database, assigns unique identifiers and human-readable maps names to them.

## Quick start

1.) Clone this repository

```shell
git clone git@github.com:PDBe-KB/process-complex-data.git
```

2.) Install dependencies with pip

```shell
pip install -r requirements.txt
```

### Basic usage

```shell
python pdbe_complexes/main.py -b <bolt_url> -u <username> -p <password> -o <output_csv_path> -m <UniProt_mapping_path> -i <complex_portal_path>`
```

A short explanation for each command line argument is given below:

- `bolt_url` = Neo4j bolt url
- `username` = Neo4j username
- `password` = Neo4j password
- `output_csv_path` = The path to the output CSV file
- `UniProt_mapping_path` = The path to the dir containing the UniProt mapping file. A sample mapping file is provided in the sample directory.
- `complex_portal_path` = The path to the Complex Portal FTP site. Please use the following path value "pub/databases/IntAct/current/various/complex2pdb"

The manually curated complexes CSV files (`complexes_molecules.csv`, `complexes_components.csv`) are provided by Romana Gaborova, EMBL-EBI.

The UniProt mapping file contains the mapping between obsolete and new UniProt accessions. Users would need to update this file weekly in order to correct any entries with obsolete UniProt accessions.

## Documentation

Executing `main.py` runs two separate processes sequentially: `process_complex.py` and `get_complex_name.py`.
The steps involved in each process are given below:

### process_complex.py
- Gets complex-composition data from Complex Portal.
- Drops existing PDBComplex nodes in the graph database.
- Reads existing mapping of complex-composition strings to pdb_complex_ids (`complexes_master.csv`) and stores the data in a reference dictionary.
- Gets complexes composition data from PDBe graph database.
- Assigns unique PDB complex identifiers for each unique complex-composition and Complex Portal identifiers for consensus complex compositions.
- Processes complex-composition data from the PDBe graph database to create relationships between selected pairs of nodes.
- Creates relationships between six pairs of nodes:
  1. Uniprot and PDBComplex
  2. Entity and PDBComplex
  3. UnmappedPolymer and PDBComplex
  4. Rfam and PDBComplex
  5. Assembly and PDBComplex
  6. Complex and PDBComplex
- Creates sub-complex relationships
- Creates a CSV file called `complexes_mapping.csv` that contains complex-related information except the names.

### get_complex_name.py
- Gets complex-related data from Complex Portal.
- Gets complex-related data from PDBe graph database.
- Assigns a complex name for each PDB Complex identifier, if possible.
- Creates a CSV file called `complexes_names.csv`, that contains the names assigned to the complexes.

### Post-process

In the final step, the two CSV files are merged together into a single CSV file called `complexes_master.csv` using the `pdb_complex_id` as the column to join on. The parent CSV files are then deleted.

## Expected content of the CSV files (examples)

### complexes_mapping.csv

|md5_obj                         |pdb_complex_id|accession           |complex_portal_id|entries                           |
|--------------------------------|--------------|--------------------|-----------------|----------------------------------|
|52fce5e893d4552c319724c8b6ae7dab|PDB-CPX-100015|A0A010_2_67581      |                 |5b01_1,5b00_1                     |
|e894061d1c2d6dd1e4683de2073998d0|PDB-CPX-100016|A0A011_2_67581      |                 |3vkc_1,3vkd_1,3vka_1,3vkb_1,3vk5_1|
|4fea44b9d12043c924d68c4db918cdd5|PDB-CPX-100017|A0A014C6J9_2_1310912|                 |6br7_1                            |
|6c18bde5b9d22b482f74dbc78456982f|PDB-CPX-100018|A0A014M399_2_1188239|                 |7dg0_1,7dfx_1                     |
|f1a69c0363ad712baa207434fb945c48|PDB-CPX-100019|A0A016UZK2_3_53326  |                 |7a4a_1                            |

### complexes_names.csv

|pdb_complex_id                  |complex_name  |derived_complex_name|complex_name_type        |
|--------------------------------|--------------|--------------------|-------------------------|
|PDB-CPX-100015                  |MoeN5         |                    |protein name from UniProt|
|PDB-CPX-100016                  |MoeO5         |                    |protein name from UniProt|
|PDB-CPX-100017                  |Two-component system response regulator protein|                    |protein name from UniProt|
|PDB-CPX-100018                  |DAC domain-containing protein|                    |protein name from UniProt|
|PDB-CPX-100019                  |Integrase catalytic domain-containing protein|                    |protein name from UniProt|


### complexes_master.csv

|md5_obj                         |pdb_complex_id|accession           |complex_portal_id        |entries.                          |complex_name                                   |derived_complex_name|complex_name_type        |
|--------------------------------|--------------|--------------------|-------------------------|----------------------------------|-----------------------------------------------|--------------------|-------------------------|
|52fce5e893d4552c319724c8b6ae7dab|PDB-CPX-100015|A0A010_2_67581      |                         |5b01_1,5b00_1                     |MoeN5                                          |                    |protein name from UniProt|
|e894061d1c2d6dd1e4683de2073998d0|PDB-CPX-100016|A0A011_2_67581      |                         |3vkc_1,3vkd_1,3vka_1,3vkb_1,3vk5_1|MoeO5                                          |                    |protein name from UniProt|
|4fea44b9d12043c924d68c4db918cdd5|PDB-CPX-100017|A0A014C6J9_2_1310912|                         |6br7_1                            |Two-component system response regulator protein|                    |protein name from UniProt|
|6c18bde5b9d22b482f74dbc78456982f|PDB-CPX-100018|A0A014M399_2_1188239|                         |7dg0_1,7dfx_1                     |DAC domain-containing protein                  |                    |protein name from UniProt|
|f1a69c0363ad712baa207434fb945c48|PDB-CPX-100019|A0A016UZK2_3_53326  |                         |7a4a_1                            |Integrase catalytic domain-containing protein  |                    |protein name from UniProt|

## Dependencies

### Dependencies for running the process
See [requirements.txt](https://github.com/PDBe-KB/process-complex-data/blob/development/requirements.txt)

### Development dependencies

For running unit tests and calculating test coverage, we suggest: `pytest`, `codecov` and `pytest-cov`:

```shell
pip install pytest
pip install codecov
pip install pytest-cov
```

For running sanity checks and linting, we suggest `pre-commit`:

```shell
pip install pre-commit
pre-commit
pre-commit install
```

## Authors
- **[Sri Devan Appasamy](https://github.com/sridevan)** (lead developer)
- **[Mihaly Varadi](https://github.com/mvaradi)** (review & refactoring)
- **[John Berrisford](https://github.com/berrisfordjohn)** (initial process and conceptualisation)

## License
Licensed under the Apache License, Version 2.0.
Please see [LICENSE](https://github.com/PDBe-KB/process-complex-data/blob/development/LICENSE).

## Acknowledgements
We would like to acknowledge the PDBe team for their help both via coding
and consultation, and especially [John Berrisford](https://github.com/berrisfordjohn), who laid the foundations
of this data process and Romana Gáborová, who maintains a list of manually curated complex names.
