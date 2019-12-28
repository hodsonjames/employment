from py2neo import Graph, Node, Relationship
import pandas as pd
import os

# manually set up these on the server before running the script
uri = "bolt://localhost:7687"
user = "neo4j"
password = "123456"


# initialize the graph object
g = Graph(uri=uri, user=user, password=password)

# process one year of data and produce a page rank by iterating through all datasets for one year
def process_one_year(year, batch_size, dataset_names, output_path):
	# load the yearly graph
	for dataset in dataset_names:
		# absolute path of the dataset
		file_path = dataset
		# loading & graph building 
		query = """
				CALL apoc.load.json({}) YIELD value 
				WITH value.user_id AS Username, value.elite_edu AS Elite, value.start AS SDate, value.end AS EDate, value.org AS Company, value.is_edu AS EduFlag
				WHERE SDate CONTAINS {} AND EduFlag CONTAINS "False" AND Company IS NOT NULL
				MERGE(e:Employee {{eid: Username, elite: Elite, sdate: SDate, edate:EDate, company:Company}})
				MERGE(c:Company {{name: Company, eliteNumber: 0, totalNumber: 0}})
				MERGE (e)-[r:WORKSFOR]->(c)
			""".format(str(batch_size), '\'' + file_path + '\'', '\'' + str(year) + '\'')
		g.run(query)

		# calculate number of elite employees in each company in year
		query = """
				MATCH (e1:Employee {elite: "True"})-->(c1:Company)
				SET c1.eliteNumber = c1.eliteNumber + 1
			"""

		g.run(query)

		# calculate total number of employees in each company in year
		query = """
				MATCH (e1:Employee)-->(c1:Company)
				SET c1.totalNumber= c1.totalNumber + 1
			"""

		g.run(query)

		# if an edge already exits, will this set the weight of already existing edge to 0?
		query = """
				MATCH (e1:Employee)-->(c1:Company), (e2:Employee {eid: e1.eid})-->(c2:Company) 
				WHERE e1.edate < e2.sdate
				CREATE UNIQUE (c1)-[t: TRANS {weight:0}]->(c2)
			"""

		g.run(query)

		# add weight to the edge
		query = """
				MATCH (e1:Employee)-->(c1:Company)-[T:TRANS]->(c2:Company)<--(e2:Employee {eid: e1.eid})
				WHERE e1.edate < e2.sdate AND e1.edate CONTAINS {} OR e2.sdate CONTAINS {}
				SET T.weight = T.weight + 1
			""".format('\'' + str(year) + '\'', '\'' + str(year) + '\'')

		g.run(query)

		# decrement number of employees of companies after transition happens
		query = """
				MATCH (e1:Employee)-->(c1:Company)-[T:TRANS]->(c2:Company)<--(e2:Employee {eid: e1.eid})
				WHERE e1.edate  < e2.sdate
				SET c1.totalNumber = c1.totalNumber - 1
			"""

		g.run(query)

		# decrement number of elite employees of companies after transition happens
		query = """
				MATCH (e1:Employee)-->(c1:Company)-[T:TRANS]->(c2:Company)<--(e2:Employee {eid: e1.eid})
				WHERE e1.edate  < e2.sdate AND e1.elite CONTAINS "True"
				SET c1.eliteNumber = c1.eliteNumber - 1
			"""

		g.run(query)
	# run page rank & output the output of page rank as csv file
	query = """
			CALL algo.pageRank.stream('Company', 'TRANS', {
  			iterations:20, dampingFactor:0.85, weightProperty: "weight"})
			YIELD nodeId, score
			RETURN algo.asNode(nodeId).name AS page,score
			ORDER BY score DESC
	"""
	res = g.run(query).to_data_frame()
	res.to_csv(output_path + str(year) + 'pagerank.csv')

	# delete all edges(transition) in this year so it won't mess up with edges in next year
	query = """
			MATCH ()-[t]->() DELETE t
	"""
	g.run(query)

# process through all years & output a page rank per year
batch_size = 100000
# customize input location
input_path = argv[1]
# customize the output file
output_path = argv[2]
# prepare paths to desired datasets
dataset_names = [x for x in os.listdir(input_path) if 'done' not in x]
years = range(2000, 2015)
for year in years:
	process_one_year(year, batch_size, dataset_names, output_path)