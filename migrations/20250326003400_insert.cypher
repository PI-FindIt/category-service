# --- !Ups
LOAD CSV WITH HEADERS FROM 'file:///categories.csv' AS row
MERGE (c:Category {name: row.name })
SET c.name = row.name;


# --- !Downs
MATCH (n) DETACH DELETE n;
