// Load the data from a transitions tsv file with department information added

// Create unique constraints (and indexes)
CREATE CONSTRAINT ON (p:Person) ASSERT p.personId IS UNIQUE;
CREATE CONSTRAINT ON (sk:Skill) ASSERT sk.name IS UNIQUE;
CREATE CONSTRAINT ON (o:Organization) ASSERT o.name IS UNIQUE;

// Syntax for creating additional indexes (without a unique constraint):
//CREATE INDEX ON :Role(title);


// Point this to the location of the import tsv file
:params {importFile: 'file:///Z:/graph_transitions/goldman_dept.tsv'}


// Create Person nodes
USING PERIODIC COMMIT 1000
LOAD CSV FROM $importFile AS row FIELDTERMINATOR '\t'
WITH
  row[0] AS personID,
  {
  	name: row[1],
    yearOfBirth: toInteger(row[2]),
    gender: toInteger(row[3]),
    ethnicity: row[4],
    connectivity: toInteger(row[9]),
    city: row[10],
    country: row[11],
    highestEdu: toInteger(row[12]),
    eliteInst: toBoolean(row[13])
  } AS personProps
MERGE (p:Person {personId: personID})
  ON CREATE SET p += personProps;


// Create Skill nodes for the first skill column
USING PERIODIC COMMIT 1000
LOAD CSV FROM $importFile AS row FIELDTERMINATOR '\t'
WITH
  row[5] AS skill1
MERGE (sk1:Skill {name: skill1});


// Create Skill nodes for the second skill column
USING PERIODIC COMMIT 1000
LOAD CSV FROM $importFile AS row FIELDTERMINATOR '\t'
WITH
  row[7] AS skill2
MERGE (sk2:Skill {name: skill2});


// Create Person-Skill relationships for the first skill column
USING PERIODIC COMMIT 1000
LOAD CSV FROM $importFile AS row FIELDTERMINATOR '\t'
WITH
  row[0] AS personID,
  row[5] AS skill1,
  toFloat(row[6]) AS skill1weight
MATCH (p:Person {personId: personID})
MATCH (sk1:Skill {name: skill1})
MERGE (p)-[r:HAS_SKILL]->(sk1)
  ON CREATE SET r.weight = skill1weight;


// Create Person-Skill relationships for the second skill column
USING PERIODIC COMMIT 1000
LOAD CSV FROM $importFile AS row FIELDTERMINATOR '\t'
WITH
  row[0] AS personID,
  row[7] AS skill2,
  toFloat(row[8]) AS skill2weight
MATCH (p:Person {personId: personID})
MATCH (sk2:Skill {name: skill2})
MERGE (p)-[r:HAS_SKILL]->(sk2)
  ON CREATE SET r.weight = skill2weight;


// Create Organization nodes for source organizations
USING PERIODIC COMMIT 1000
LOAD CSV FROM $importFile AS row FIELDTERMINATOR '\t'
WITH
  coalesce(row[19], row[18], 'Unknown') AS sourceOfficial,
  {
    ticker: row[20],
    exchange: row[21],
    isPublic: toBoolean(row[22]),
    location: row[23],
    industry: row[24],
    isElite: CASE WHEN toBoolean(row[25]) THEN toBoolean(row[27]) END
  } AS sourceProps
MERGE (source:Organization {name: sourceOfficial})
  ON CREATE SET source += sourceProps;


// Create Organization nodes for target organizations
USING PERIODIC COMMIT 1000
LOAD CSV FROM $importFile AS row FIELDTERMINATOR '\t'
WITH
  coalesce(row[33], row[32], 'Unknown') AS targetOfficial,
  {
    ticker: row[34],
    exchange: row[35],
    isPublic: toBoolean(row[36]),
    location: row[37],
    industry: row[38],
    isElite: CASE WHEN toBoolean(row[39]) THEN toBoolean(row[41]) END
  } AS targetProps
MERGE (target:Organization {name: targetOfficial})
  ON CREATE SET target += targetProps;


// Create Role nodes linked to Organizations for source employments
USING PERIODIC COMMIT 1000
LOAD CSV FROM $importFile AS row FIELDTERMINATOR '\t'
WITH
  coalesce(row[19], row[18]) AS sourceOfficial,
  coalesce(row[43], 'Unknown') AS sourceTitle,
  toBoolean(row[25]) AS sourceEdu,
  toInteger(row[26]) AS sourceEduLevel
MATCH (source:Organization {name: sourceOfficial})
MERGE (sourceRole:Role {title:sourceTitle, isEducational: sourceEdu})-[:WITHIN]->(source)
  ON CREATE SET sourceRole.eduLevel = sourceEduLevel;


// Create Role nodes linked to Organizations for target employments
USING PERIODIC COMMIT 1000
LOAD CSV FROM $importFile AS row FIELDTERMINATOR '\t'
WITH
  coalesce(row[33], row[32]) AS targetOfficial,
  coalesce(row[45], 'Unknown') AS targetTitle,
  toBoolean(row[39]) AS targetEdu,
  toInteger(row[40]) AS targetEduLevel
MATCH (target:Organization {name: targetOfficial})
MERGE (targetRole:Role {title:targetTitle, isEducational: targetEdu})-[:WITHIN]->(target)
  ON CREATE SET targetRole.eduLevel = targetEduLevel;


// Create Department nodes linked to Organizations for source employments
USING PERIODIC COMMIT 1000
LOAD CSV FROM $importFile AS row FIELDTERMINATOR '\t'
WITH
  coalesce(row[19], row[18]) AS sourceOfficial,
  coalesce(row[42], 'Unknown') AS sourceDeptName
MATCH (source:Organization {name: sourceOfficial})
MERGE (sourceDept:Department {name:sourceDeptName})-[:PART_OF]->(source);


// Create Department nodes linked to Organizations for target employments
USING PERIODIC COMMIT 1000
LOAD CSV FROM $importFile AS row FIELDTERMINATOR '\t'
WITH
  coalesce(row[33], row[32]) AS targetOfficial,
  coalesce(row[44], 'Unknown') AS targetDeptName
MATCH (target:Organization {name: targetOfficial})
MERGE (targetDept:Department {name:targetDeptName})-[:PART_OF]->(target);


// Create Employment nodes linked to Person and Role for source employments
USING PERIODIC COMMIT 1000
LOAD CSV FROM $importFile AS row FIELDTERMINATOR '\t'
WITH
  row[0] AS personID,
  coalesce(row[19], row[18]) AS sourceOfficial,
  coalesce(row[43], 'Unknown') AS sourceTitle,
  toBoolean(row[25]) AS sourceEdu,
  CASE WHEN row[14] <> "None" THEN date(row[14]) END AS sourceStart,
  CASE WHEN row[15] <> "None" THEN date(row[15]) END AS sourceEnd,
  toInteger(row[16]) AS sourceDuration,
  row[18] AS sourceName
MATCH (p:Person {personId: personID})
MATCH (source:Organization {name: sourceOfficial})
MATCH (sourceRole:Role {title:sourceTitle, isEducational: sourceEdu})-[:WITHIN]->(source)
MERGE (p)-[:EMPLOYMENT]->(sourceEmp:Employment {endDate:sourceEnd})-[:AS]->(sourceRole)
  ON CREATE SET sourceEmp.startDate = sourceStart, sourceEmp.orgNameProvided = sourceName, sourceEmp.duration = sourceDuration;


// Create relationsips between Employment nodes Departments for source employments
USING PERIODIC COMMIT 1000
LOAD CSV FROM $importFile AS row FIELDTERMINATOR '\t'
WITH
  row[0] AS personID,
  coalesce(row[19], row[18]) AS sourceOfficial,
  coalesce(row[43], 'Unknown') AS sourceTitle,
  coalesce(row[42], 'Unknown') AS sourceDeptName,
  toBoolean(row[25]) AS sourceEdu,
  CASE WHEN row[14] <> "None" THEN date(row[14]) END AS sourceStart,
  CASE WHEN row[15] <> "None" THEN date(row[15]) END AS sourceEnd,
  toInteger(row[16]) AS sourceDuration,
  row[18] AS sourceName
MATCH (p:Person {personId: personID})
MATCH (source:Organization {name: sourceOfficial})
MATCH (sourceRole:Role {title:sourceTitle, isEducational: sourceEdu})-[:WITHIN]->(source)
MATCH (sourceDept:Department {name:sourceDeptName})-[:PART_OF]->(source)
MATCH (p)-[:EMPLOYMENT]->(sourceEmp:Employment {endDate:sourceEnd})-[:AS]->(sourceRole)
MERGE (sourceEmp)-[:IN_DEPT]->(sourceDept);


// Create Employment nodes linked to Person and Role for target employments
USING PERIODIC COMMIT 1000
LOAD CSV FROM $importFile AS row FIELDTERMINATOR '\t'
WITH
  row[0] AS personID,
  coalesce(row[33], row[32]) AS targetOfficial,
  coalesce(row[45], 'Unknown') AS targetTitle,
  toBoolean(row[39]) AS targetEdu,
  CASE WHEN row[28] <> "None" THEN date(row[28]) END AS targetStart,
  CASE WHEN row[29] <> "None" THEN date(row[29]) END AS targetEnd,
  toInteger(row[30]) AS targetDuration,
  row[32] AS targetName
MATCH (p:Person {personId: personID})
MATCH (target:Organization {name: targetOfficial})
MATCH (targetRole:Role {title:targetTitle, isEducational: targetEdu})-[:WITHIN]->(target)
MERGE (p)-[:EMPLOYMENT]->(targetEmp:Employment {startDate:targetStart})-[:AS]->(targetRole)
  ON CREATE SET targetEmp.endDate = targetEnd, targetEmp.orgNameProvided = targetName, targetEmp.duration = targetDuration;


// Create relationsips between Employment nodes Departments for source employments
USING PERIODIC COMMIT 1000
LOAD CSV FROM $importFile AS row FIELDTERMINATOR '\t'
WITH
  row[0] AS personID,
  coalesce(row[33], row[32]) AS targetOfficial,
  coalesce(row[45], 'Unknown') AS targetTitle,
  coalesce(row[44], 'Unknown') AS targetDeptName,
  toBoolean(row[39]) AS targetEdu,
  CASE WHEN row[28] <> "None" THEN date(row[28]) END AS targetStart,
  CASE WHEN row[29] <> "None" THEN date(row[29]) END AS targetEnd,
  toInteger(row[30]) AS targetDuration,
  row[32] AS targetName
MATCH (p:Person {personId: personID})
MATCH (target:Organization {name: targetOfficial})
MATCH (targetRole:Role {title:targetTitle, isEducational: targetEdu})-[:WITHIN]->(target)
MATCH (targetDept:Department {name:targetDeptName})-[:PART_OF]->(target)
MATCH (p)-[:EMPLOYMENT]->(targetEmp:Employment {startDate:targetStart})-[:AS]->(targetRole)
MERGE (targetEmp)-[:IN_DEPT]->(targetDept);


// Create precedence relationsips between Employment nodes
USING PERIODIC COMMIT 1000
LOAD CSV FROM $importFile AS row FIELDTERMINATOR '\t'
WITH
  row[0] AS personID,
  coalesce(row[19], row[18]) AS sourceOfficial,
  coalesce(row[43], 'Unknown') AS sourceTitle,
  toBoolean(row[25]) AS sourceEdu,
  CASE WHEN row[15] <> "None" THEN date(row[15]) END AS sourceEnd,
  coalesce(row[33], row[32]) AS targetOfficial,
  coalesce(row[45], 'Unknown') AS targetTitle,
  toBoolean(row[39]) AS targetEdu,
  CASE WHEN row[28] <> "None" THEN date(row[28]) END AS targetStart
MATCH (p:Person {personId: personID})
MATCH (source:Organization {name: sourceOfficial})
MATCH (sourceRole:Role {title:sourceTitle, isEducational: sourceEdu})-[:WITHIN]->(source)
MATCH (p)-[:EMPLOYMENT]->(sourceEmp:Employment {endDate:sourceEnd})-[:AS]->(sourceRole)
MATCH (target:Organization {name: targetOfficial})
MATCH (targetRole:Role {title:targetTitle, isEducational: targetEdu})-[:WITHIN]->(target)
MATCH (p)-[:EMPLOYMENT]->(targetEmp:Employment {startDate:targetStart})-[:AS]->(targetRole)
CREATE (sourceEmp)-[:PRECEDES]->(targetEmp);


// Create relationships between roles corresponding to employment transitions
MATCH (org:Organization)-[:WITHIN]-(r1:Role)-[:AS]-(e1:Employment)-[:PRECEDES]->
(e2:Employment)-[:AS]-(r2:Role)-[:WITHIN]-(org)
WITH r1, r2, count(*) as cnt
CREATE (r1)-[:CAN_LEAD_TO {weight:cnt}]->(r2)
