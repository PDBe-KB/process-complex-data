MERGE_ACCESSION_QUERY = """
WITH $accession_params_list AS batch
UNWIND batch AS row
MATCH (u:UniProt {ACCESSION:row.accession})
MERGE (c:PDBComplex {COMPLEX_ID:row.complex_id})
MERGE (c)<-[:IS_PART_OF_PDB_COMPLEX {STOICHIOMETRY:row.stoichiometry}]-(u)
"""

MERGE_ENTITY_QUERY = """
WITH $entity_params_list AS batch
UNWIND batch AS row
MATCH (e:Entry {ID:row.entry_id})-[:HAS_ENTITY]->(en:Entity {ID:row.entity_id})
MERGE (c:PDBComplex {COMPLEX_ID:row.complex_id})
MERGE (c)<-[:IS_PART_OF_PDB_COMPLEX {STOICHIOMETRY:row.stoichiometry}]-(en)
"""

MERGE_ASSEMBLY_QUERY = """
WITH $assembly_params_list AS batch
UNWIND batch AS row
MATCH (e:Entry {ID:row.entry_id})-[:HAS_ENTITY]->(:Entity)-
    [:IS_PART_OF_ASSEMBLY]->(assembly:Assembly {UNIQID:row.assembly_id})
MERGE (c:PDBComplex {COMPLEX_ID:row.complex_id})
MERGE (c)<-[:IS_PART_OF_PDB_COMPLEX]-(assembly)
"""

MERGE_RFAM_QUERY = """
WITH $rfam_params_list AS batch
UNWIND batch AS row
MATCH (rfam:RfamFamily {RFAM_ACC:row.rfam_acc})
MERGE (c:PDBComplex {COMPLEX_ID:row.complex_id})
MERGE (c)<-[:IS_PART_OF_PDB_COMPLEX]-(rfam)
"""

COMMON_COMPLEX_QUERY = """
WITH $complex_params_list AS batch
UNWIND batch AS row
MATCH
    (p:PDBComplex {COMPLEX_ID:row.pdb_complex_id}),
    (c:Complex {COMPLEX_ID:row.complex_portal_id})
CREATE (p)-[:SAME_AS]->(c)
"""

MERGE_UNMAPPED_POLYMER_QUERY = """
WITH $unmapped_polymer_params_list AS batch
UNWIND batch AS row
MERGE (up:UnmappedPolymer {TYPE:row.polymer_type})
MERGE (c:PDBComplex {COMPLEX_ID:row.complex_id})
MERGE (c)<-[:IS_PART_OF_PDB_COMPLEX]-(up)
"""

COMPLEX_PORTAL_DATA_QUERY = """
MATCH
    (complex:Complex)<-[rel:IS_PART_OF_COMPLEX]-(unp:UniProt)-[:HAS_TAXONOMY]->(tax:Taxonomy)
OPTIONAL MATCH
    (complex)<-[:IS_PART_OF_COMPLEX]-(entry:Entry)
WITH
    complex.COMPLEX_ID AS complex_id,
    unp.ACCESSION +'_' + rel.STOICHIOMETRY +'_' +tax.TAX_ID AS uniq_accessions,
    COLLECT(entry.ID) AS entries ORDER BY uniq_accessions
WITH
    complex_id AS complex_id,
    COLLECT(DISTINCT uniq_accessions) AS uniq_accessions,
    entries
WITH
    complex_id AS complex_id,
    REDUCE(s = HEAD(uniq_accessions),
    n in TAIL(uniq_accessions) | s +',' +n) AS uniq_accessions,
    entries
RETURN
    complex_id,
    uniq_accessions,
    REDUCE(s = HEAD(entries), n in TAIL(entries) | s +',' +n) AS entries_str
"""

PDB_ASSEMBLY_DATA_QUERY = """
MATCH (assembly:Assembly {PREFERED: 'True'})<-[rel:IS_PART_OF_ASSEMBLY]
-(entity:Entity {TYPE:'p'})
WITH assembly, rel, entity
OPTIONAL MATCH (entity)-[:HAS_UNIPROT {BEST_MAPPING:'1'}]->(uniprot:UniProt)
-[:HAS_TAXONOMY]->(tax:Taxonomy)
OPTIONAL MATCH (entity)-[:HAS_RFAM]->(rfam:RfamFamily)
WITH assembly.UNIQID AS assembly_id,
CASE uniprot
    WHEN null
        THEN
            CASE rfam
                WHEN null
                    THEN
                        CASE entity.POLYMER_TYPE
                            WHEN 'R'
                                THEN 'RNA' +':UNMAPPED'
                            WHEN 'D'
                                THEN 'DNA' +':UNMAPPED'
                            WHEN 'D/R'
                                THEN 'DNA/RNA' +':UNMAPPED'
                            WHEN 'P'
                                THEN 'NA_' +entity.UNIQID +'_' +rel.NUMBER_OF_CHAINS
                        END
                ELSE
                    rfam.RFAM_ACC
            END
    ELSE uniprot.ACCESSION +'_' +rel.NUMBER_OF_CHAINS +'_' +tax.TAX_ID
END AS accession ORDER BY accession
WITH assembly_id AS assembly_id, COLLECT (DISTINCT accession) AS accessions
WITH assembly_id AS assembly_id, REDUCE(s = HEAD(accessions),
n in TAIL(accessions) | s +',' +n) AS accessions
WITH accessions, COLLECT(DISTINCT assembly_id) AS assemblies
WITH accessions AS accessions, REDUCE(s = HEAD(assemblies),
n in TAIL(assemblies) | s +',' +n) AS assemblies
RETURN accessions, assemblies
"""

DROP_PDB_COMPLEX_NODES_QUERY = """
MATCH (p:PDBComplex) DETACH DELETE p
"""

DROP_SUBCOMPLEX_RELATION_QUERY = """
MATCH (:PDBComplex)-[r:IS_SUB_COMPLEX_OF]->(:PDBComplex) DELETE r
"""

CREATE_SUBCOMPLEX_RELATION_QUERY = """
MATCH
(src_complex:PDBComplex)<-[rel1:IS_PART_OF_PDB_COMPLEX]-()-
[rel2:IS_PART_OF_PDB_COMPLEX]->(dest_complex:PDBComplex)
WHERE rel1.STOICHIOMETRY=rel2.STOICHIOMETRY
    WITH DISTINCT src_complex, dest_complex, rel1
    WITH src_complex, startNode(rel1) AS relRelations, dest_complex
    WITH src_complex, COUNT(relRelations) AS relRelationsAmount, dest_complex
    MATCH (src_complex)<-[allRelations:IS_PART_OF_PDB_COMPLEX]-()
        WITH src_complex, relRelationsAmount, count(allRelations) AS allRelationsAmount,
            dest_complex
                WHERE relRelationsAmount = allRelationsAmount
CREATE (dest_complex)<-[:IS_SUB_COMPLEX_OF]-(src_complex)
"""

PDB_COMPLEX_QUERY = """
MATCH (pdb_complex:PDBComplex)<-[rel:IS_PART_OF_PDB_COMPLEX]-(component)
OPTIONAL MATCH (component)-[:HAS_TAXONOMY]->(tax:Taxonomy)
OPTIONAL MATCH (component)-[:HAS_ANTIBODY_MAPPING]->(ab:Antibody)
WITH pdb_complex.COMPLEX_ID AS complex_id,
labels(component) AS component_db,
rel.STOICHIOMETRY AS stoichiometry,
component.TYPE AS component_type,
component.ACCESSION AS accession,
component.RFAM_ACC AS rfam_accession,
component.POLYMER_TYPE AS polymer_type,
component.NUMBER_POLY_SEQ AS entity_length,
tax.TAX_ID AS taxonomy,
CASE labels(component)
    WHEN ['Assembly']
    THEN component.UNIQID
END AS entry_assembly,
CASE ab.ID
    WHEN '1'
        THEN True
    ELSE
        False
    END AS antibody,
component.UNIQID AS entity
RETURN complex_id, component_db, component_type, stoichiometry, accession,
rfam_accession, polymer_type, taxonomy, entry_assembly, entity, antibody,
entity_length
"""

ENTITY_QUERY = """
MATCH (e:Entity)
WITH e.UNIQID AS entity_uniqid,
    e.DESCRIPTION AS description
RETURN entity_uniqid, description
"""

UNIPROT_QUERY = """
MATCH (u:UniProt)
WITH u.ACCESSION AS accession,
    u.DESCR AS description
RETURN accession, description
"""

RFAM_QUERY = """
MATCH (u:RfamFamily)
WITH u.RFAM_ACC AS accession,
    u.DESCRIPTION AS description
RETURN accession, description
"""
