# --- !Ups
LOAD CSV WITH HEADERS FROM 'file:///categories.csv' AS row
MATCH (child:Category {name: row.name})
WHERE row.parent_name IS NOT NULL
MATCH (parent:Category {name: row.parent_name})
MERGE (child)-[:SUBCATEGORY_OF]->(parent);



# --- !Downs
MATCH (n) DETACH DELETE n;
