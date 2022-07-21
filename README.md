# Basic information

This repository contains code for processes that will aggregate complexes data from the PDBe graph database, assign identifiers and create names for macromolecular complexes.

In general, it will do the following:
- Aggregate complexes data from the PDBe graph database
- Assign unique identifier for each unique complex composition
- Build relationships between several complexes related nodes in the graph database
- Assign name for each unique complex composition

# Usage

Clone this repository

`git clone git@github.com:PDBe-KB/process-complex-data.git`

Install dependencies with pip

`pip install -r requirements.txt`

usage: run_complexes.py -b <BOLT_URL> -u <NEO4J_USERNAME> -p <NEO4J_PASSWORD> -o <OUTPUT_CSV_PATH> -i1 <INPUT_MOLECULES_NAME_PATH> -i2 <INPUT_MOLECULES_COMPONENTS_PATH>

`python complexes/run_complexes.py -b <bolt_url> -u <username> -p <password> -o <output_csv_path> -i1 <input_molecules_name_path> -i2 <input_molecules_components_path>`

# Package explanation

Executing the command above will run two separate processes sequentially: i) **process_complex.py** and ii) **get_complex_name.py**. The steps involved in each process are given below:

**process_complex.py**
- Gets complexes composition data from Complex Portal
- Drops existing PDBComplex nodes in the graph database
- Gets complexes composition data from PDBe graph database
- Assigns unique PDB complex identifer for each unique complex composition and Complex Portal identifer for consensus complex compositions
- Processes complexes composition data from the PDBe graph database in order to create relationships between selected pairs of nodes
- Creates relationships between six pairs of nodes: i) **Uniprot** and **PDBComplex**, ii) **Entity** and **PDBComplex**, iii) **UnmappedPolymer** and **PDBComplex**, iv) **Rfam** and **PDBComplex**, v) **Assembly** and **PDBComplex**, vi **Complex** and **PDBComplex**
- Creates subcomplex relationships
- Creates a CSV file called "complexes_mapping.csv" that contains complexes related information except the names

**get_complex_name.py**
- Gets complexes related data from Complex Portal
- Gets complexes related data from PDBe graph database
- Assigns a complex name for each PDB Complex identifer if possible
- Creates a CSV file called "complexes_names.csv" that contains the names assigned to the complexes


In the final step, the two CSV files are merged together into a single CSV file called "complexes_master.csv" using the "pdb_complex_id" as the column to join on.

# Expected content of the CSV files (examples)

complexes_mapping.csv

|md5_obj                         |pdb_complex_id|accession           |complex_portal_id|assemblies                        |
|--------------------------------|--------------|--------------------|-----------------|----------------------------------|
|52fce5e893d4552c319724c8b6ae7dab|PDB-CPX-100015|A0A010_2_67581      |                 |5b01_1,5b00_1                     |
|e894061d1c2d6dd1e4683de2073998d0|PDB-CPX-100016|A0A011_2_67581      |                 |3vkc_1,3vkd_1,3vka_1,3vkb_1,3vk5_1|
|4fea44b9d12043c924d68c4db918cdd5|PDB-CPX-100017|A0A014C6J9_2_1310912|                 |6br7_1                            |
|6c18bde5b9d22b482f74dbc78456982f|PDB-CPX-100018|A0A014M399_2_1188239|                 |7dg0_1,7dfx_1                     |
|f1a69c0363ad712baa207434fb945c48|PDB-CPX-100019|A0A016UZK2_3_53326  |                 |7a4a_1                            |
|9a0b8b44ab8110be4815e78067862e8d|PDB-CPX-100020|A0A017T5A5_1_1192034|                 |6gmf_1                            |
|f0cf4d1c7555348eb9c917c50242e65f|PDB-CPX-100021|A0A022MQ12_2_1470557|                 |6sj2_1,6sj3_1,6sj4_1,6sj1_1       |
|b948fde7016409880ce63ddfddb05712|PDB-CPX-100022|A0A022MRT4_1_1470557|                 |6siw_1,6tm4_1                     |
|f1bc38b4142fce0d7dc3bb04277f3d3f|PDB-CPX-100023|A0A022MRT4_2_1470557|                 |6siy_1,6siz_1,6six_1              |
|476110a9c73f71d07db1a88e0084d9d1|PDB-CPX-100024|A0A023DFE8_2_1220594|                 |6n9q_1,6n9i_2                     |
|2e36844b6635d060cc866fdb74701fc4|PDB-CPX-100025|A0A023DFE8_6_1220594|                 |6n9r_1                            |
|35ef47e0f84d0bbd4f1f1a8400fc6fe3|PDB-CPX-100026|A0A023GPI4_1_152923 |                 |2m6j_1                            |

complexes_names.csv

|pdb_complex_id                  |complex_name  |derived_complex_name|complex_name_type        |
|--------------------------------|--------------|--------------------|-------------------------|
|PDB-CPX-100015                  |MoeN5         |                    |protein name from UniProt|
|PDB-CPX-100016                  |MoeO5         |                    |protein name from UniProt|
|PDB-CPX-100017                  |Two-component system response regulator protein|                    |protein name from UniProt|
|PDB-CPX-100018                  |DAC domain-containing protein|                    |protein name from UniProt|
|PDB-CPX-100019                  |Integrase catalytic domain-containing protein|                    |protein name from UniProt|
|PDB-CPX-100020                  |Putative cytochrome P450 hydroxylase|                    |protein name from UniProt|
|PDB-CPX-100021                  |Amidohydrolase|                    |protein name from UniProt|
|PDB-CPX-100022                  |AMP-dependent synthetase and ligase|                    |protein name from UniProt|
|PDB-CPX-100023                  |AMP-dependent synthetase and ligase|                    |protein name from UniProt|
|PDB-CPX-100024                  |Putative hydrolase|                    |protein name from UniProt|
|PDB-CPX-100025                  |Putative hydrolase|                    |protein name from UniProt|
|PDB-CPX-100026                  |Toxin AbTx    |                    |protein name from UniProt|

complexes_master.csv

|md5_obj                         |pdb_complex_id|accession           |complex_portal_id        |assemblies                        |complex_name                                   |derived_complex_name|complex_name_type        |
|--------------------------------|--------------|--------------------|-------------------------|----------------------------------|-----------------------------------------------|--------------------|-------------------------|
|52fce5e893d4552c319724c8b6ae7dab|PDB-CPX-100015|A0A010_2_67581      |                         |5b01_1,5b00_1                     |MoeN5                                          |                    |protein name from UniProt|
|e894061d1c2d6dd1e4683de2073998d0|PDB-CPX-100016|A0A011_2_67581      |                         |3vkc_1,3vkd_1,3vka_1,3vkb_1,3vk5_1|MoeO5                                          |                    |protein name from UniProt|
|4fea44b9d12043c924d68c4db918cdd5|PDB-CPX-100017|A0A014C6J9_2_1310912|                         |6br7_1                            |Two-component system response regulator protein|                    |protein name from UniProt|
|6c18bde5b9d22b482f74dbc78456982f|PDB-CPX-100018|A0A014M399_2_1188239|                         |7dg0_1,7dfx_1                     |DAC domain-containing protein                  |                    |protein name from UniProt|
|f1a69c0363ad712baa207434fb945c48|PDB-CPX-100019|A0A016UZK2_3_53326  |                         |7a4a_1                            |Integrase catalytic domain-containing protein  |                    |protein name from UniProt|
|9a0b8b44ab8110be4815e78067862e8d|PDB-CPX-100020|A0A017T5A5_1_1192034|                         |6gmf_1                            |Putative cytochrome P450 hydroxylase           |                    |protein name from UniProt|
|f0cf4d1c7555348eb9c917c50242e65f|PDB-CPX-100021|A0A022MQ12_2_1470557|                         |6sj2_1,6sj3_1,6sj4_1,6sj1_1       |Amidohydrolase                                 |                    |protein name from UniProt|
|b948fde7016409880ce63ddfddb05712|PDB-CPX-100022|A0A022MRT4_1_1470557|                         |6siw_1,6tm4_1                     |AMP-dependent synthetase and ligase            |                    |protein name from UniProt|
|f1bc38b4142fce0d7dc3bb04277f3d3f|PDB-CPX-100023|A0A022MRT4_2_1470557|                         |6siy_1,6siz_1,6six_1              |AMP-dependent synthetase and ligase            |                    |protein name from UniProt|
|476110a9c73f71d07db1a88e0084d9d1|PDB-CPX-100024|A0A023DFE8_2_1220594|                         |6n9q_1,6n9i_2                     |Putative hydrolase                             |                    |protein name from UniProt|
|2e36844b6635d060cc866fdb74701fc4|PDB-CPX-100025|A0A023DFE8_6_1220594|                         |6n9r_1                            |Putative hydrolase                             |                    |protein name from UniProt|
|35ef47e0f84d0bbd4f1f1a8400fc6fe3|PDB-CPX-100026|A0A023GPI4_1_152923 |                         |2m6j_1                            |Toxin AbTx                                     |                    |protein name from UniProt|




