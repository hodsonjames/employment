# -*- coding: utf-8 -*-

#! python

import codecs
import os
import nltk
import re
import unicodecsv as csv
import sys

csv.field_size_limit(sys.maxsize)

#############################################################################
#
#	A module to help better understand and normalise
#	the morass of not very informative job titles
#	and role descriptions that the kind people have
#	provided.
#
#	Works for both employment and education.
#
#############################################################################

#############################################################################
#
#	A necessary utility for accessing the data local to the installation.
#
#############################################################################

_ROOT = os.path.abspath(os.path.dirname(__file__))
def get_data(path):
	return os.path.join(_ROOT, 'data', path)
    
#############################################################################
#
#	TODO: This should be extended and improved.
#	Markers for degree types.
#
#############################################################################

# Markers of each level of education
high_school = set([u"high school",u"liceo",u"lycée",u"baccalauréat",
				   u"baccalaureate",u"general education",u"k-12",u"cse",
				   u"gcse",u"a level",u"a-level",u"gymnasium",
				   u"secondary school",u"hogeschool",u"a levels",
				   u"secondary",u"high",u"grade",u"diploma",u"gimnazija"])

vocational = set([u"btec",u"b.tec",u"certificate",u"certification",
				  u"license",u"lic.",u"licenciatura",u"nvq",
				  u"national vocational qualification",u"bts",
				  u"foundational degree"])

associate = set([u"associate",u"community college",u"associates",
				 u"associate's degree",u"hnc",u"hnd"
				 u"higher national"])

bachelor = set([u"ba",u"minor",u"bachelor",
				u"bachelor's",u'bachelor\u2019s',u"b.s.",u"bba",u"bme",
				u"bacharelado",u"bacharel",u"university",
				u"b.sc.",u"b.com",u"bcom",u"b.a.",u"b.f.a",u"bfa",
				u"bsc",u"bs",u"universidad",u"universidade",
				u"laurea",u"major",u"undergraduate",u"b.s.",u"università",
				u"университет",u"univerzita",u"uni",u"经济学学士",
				u"faculté",u"faculty",u"uc",u"umass"])

master = set([u"m.eng",u"master",u"m.sc",u"m.s.",u"msw",u"msc",
			  u"m.div",u"magister",u"ma",u"máster",u"maestría",
			  u"graduate diploma",u"certificate extension",u"mbo",
			  u"mpp",u"master's",u"mchem"])

mba = set([u"mba",u"m.b.a",u"certificate business administration",u"cba"])

doctor = set([u"p.g. dip",u"post graduate",u"doctor",u"m.d.",u"ph.d",
			  u"phd",u"ll.b.",u"j.d.",u"juris doctor",u"dr.",u"doktor",
			  u"dottore",u"juris",u"jd"])

elites = set([u"princeton",u"harvard",u"mit",
			  u"massachusetts institute of technology",u"m.i.t",u"columbia",
			  u"nyu",u"new york university",u"stanford",u"cmu",
			  u"carnegie mellon",u"upenn",u"university of pennsylvania",u"yale",
			  u"berkeley",u"oxford university",u"cambridge university",
			  u"warwick",u"lse",u"kcl",u"kings college london",
			  u"university college london",u"duke",u"brown",
			  u"university of chicago",u"uchicago",u"uiuc",u"caltech",
			  u"california institute of technology",u"hbs",u"cornell" 
			  u"edinburgh",u"eth zurich",u"sorbonne",u"sciences po",
			  u"moscow state",u"la sapienza",u"ucla",u"stern",u"wharton",
			  u"booth",u"haas",u"gsb",u"tsinghua",u"usc",
			  u"university of southern california",u"northwestern",u"kellogg",
			  u"ucsd",u"uc davis",u"johns hopkins",u"jhu",u"dartmouth",u"lbs"])

#############################################################################
#
#	Utility Functions
#
#############################################################################

# Given a role, return a list of elements
# according to a simple set of rules.
#
# e.g. "Analyst / Associate"
#		-> ["Analyst","Associate"]
#
#	   "Lehman Brothers (in liquidation)"
#		-> ["Lehman Brothers","in liquidation"]
#
# This is to facilitate processing of disambiguation
# and multiple roles.

def listNames(name):

	names = [name,]
	cands = []
	
	if (u"(" in name) and (u")" in name[name.index("("):]):
		
		if len(name[:name.index("(")]) > 2:
			cands.append(name[:name.index("(")])
		
		cands.append(name[name.index("(")+1:name.index(")")].strip())
		
		if len(name[name.index(")")+1:]) > 2:
			cands.append(name[name.index(")")+1:])
	else:
		cands.append(name)
		
	for nme in cands:
	
		ns = re.split(u'/|,|;| - |–',nme)
	
		for n in ns:
			if len(n.strip()) > 2:
				names.append(n.strip())
	
	return names

#############################################################################
#
#	A class to provide role disambiguation.
#
#############################################################################

class Roles (object):

	def __init__(self):
	
		self.abbreviations = {}
		self.departments = {}
		self.validroles = {}
		self.faculties = {}
		
		# Read in mappings...
		
		# ...of manually created role abbreviations.
		self.buildRoleMappings()
		
		# ...of manually filtered departments
		self.buildDepartments()
		
		# ...of most frequent role descriptors
		self.buildReferenceRoles()
		
		# ...of university departments
		self.buildFaculties()
	
	
	# From the role, try to identify a normalized role and department.
	def parse_work (self,name):
	
		# Role and department
		departments = set()
		positions = [name.replace(',',''),]
	
		# Split name into all unigrams bigrams and trigrams
		set_grams = []
		n = 3
		
		# Add all n-grams to the set from 1-n
		while n != 0:
			for i in nltk.ngrams(nltk.word_tokenize(name),n):
				set_grams.append(' '.join(i))
			n -= 1
			
		# For each item in the set, check whether we can
		# replace it with a mapped item.
		for gram in set_grams:
			if gram.lower() in self.abbreviations:
				if len(self.abbreviations[gram.lower()]) == 1:
					for m in self.abbreviations[gram.lower()]:
						name = name.replace(gram,m)
				else:
					for m in self.abbreviations[gram.lower()]:
						if name.lower() in self.abbreviations[gram.lower()][m]:
							name = name.replace(gram,m)
							break
			
			if gram.lower() in self.departments:
				departments.add(self.departments[gram.lower()])
		
		# Isolate this person's role from their boss.	
		# TODO: This should be more sophisticated...	
		if " to the " in name:
			name = name[:name.index(" to the ")].strip()	
		elif " to " in name:
			name = name[:name.index(" to ")].strip()
		
		# "of" appears frequently ahead of department markers.
		if " of " in name:
			name = name[:name.index(" of ")].strip()
			
		# Split name into all unigrams bigrams and trigrams
		set_grams = []
		
		for nm in listNames(name):
		
			n = 5
		
			# Add all n-grams to the set from 1-n
			while n != 0:
				for i in nltk.ngrams(nltk.word_tokenize(name),n):
					set_grams.append(' '.join(i))
				n -= 1
			
			# Look up the portions that correspond to real roles.
			for gram in set_grams:
				if gram.lower() in self.validroles:
					cover = False
					for i in positions:
						if gram.lower() in i:
							cover = True
					
					if not cover:
						positions.append(gram.lower())
				
		if len(positions) == 0:
			positions.append(name)
			
		return positions,departments

		
	# Normalize the degree string associated with education.
	# Return the normalized string, degree level, and eliteness.
	# Works on both institution and degree fields, since there
	# are many instances of misuse.
	def parse_edu(self, degree, uni):
	
		if degree[:len(degree)/2].strip() == degree[len(degree)/2:].strip():
			degree = degree[:len(degree)/2]
		
		degrees = listNames(degree)
		
		# Try to infer the level of education represented.
		majors = set()
		faculties = set()
		level = None
		elite = False
		identifier = None
		
		# Extract all tri-grams with nltk
		set_grams = set()
		n = 5
		sentence = (uni.lower() + " " + degree.lower()).replace(u'-',u' ')
		
		# Add all n-grams to the set from 1-n
		while n != 0:
			for i in nltk.ngrams(nltk.word_tokenize(sentence),n):
				set_grams.add(' '.join(i))
			n -= 1
			
		# Identify Fields of Study
		for gram in set_grams:
			if gram in self.faculties:
				majors.add(gram)
				faculties.add(self.faculties[gram])

		# Any evidence of each type of degree?
		if high_school.intersection(set_grams):
			level = 1
			identifier = "SCHOOL"
		if vocational.intersection(set_grams):
			level = 2
			identifier = "SCHOOL"
		if associate.intersection(set_grams):
			level = 3
			identifier = "UNIVERSITY"
		if bachelor.intersection(set_grams):
			level = 4
			identifier = "UNIVERSITY"
		if master.intersection(set_grams):
			level = 5
			identifier = "UNIVERSITY"
		if mba.intersection(set_grams):
			level = 6
			identifier = "UNIVERSITY"
		if doctor.intersection(set_grams):
			level = 7
			identifier = "UNIVERSITY"
			
		# Is the institution "elite"?
		if elites.intersection(set_grams):
			elite = True
			
			# If it is elite, it must be at least a bachelors
			# degree, so ensure we capture this.
			if level < 4:
				level = 4
		
		# For now, return the first degree we find
		# Needs to be improved
		return degrees, level, elite, identifier, majors, faculties

	# Build mapping of tickers to industries.
	def buildRoleMappings(self):
	
		map_file = csv.reader(open(get_data('all_abbreviations.tsv'),'r'),
							  delimiter='\t', encoding='utf-8')
		
		for line in map_file:
		
			if len(line) != 3:
				continue
			
			source = line[0].strip().lower()
			valid_roles = line[1][1:-1].split(',')
			target = line[2].strip()
			
			if source in self.abbreviations:
				# Add an extra mapping entry
				if target in self.abbreviations[source]:
					for i in valid_roles:
						self.abbreviations[source][target].add(i.lower())
				else:
					self.abbreviations[source][target] = set()
					for i in valid_roles:
						self.abbreviations[source][target].add(i.lower())
			else:
				self.abbreviations[source] = {}
				self.abbreviations[source][target] = set()
				for i in valid_roles:
					self.abbreviations[source][target].add(i.lower())
	
	# Read the file of filtered departments, and make a mapping.
	def buildDepartments(self):
		
		map_file = csv.reader(open(get_data('departments.tsv'),'r'),
							  delimiter='\t', encoding='utf-8')
		
		for line in map_file:
			if len(line) != 3:
				continue
			
			if line[0].lower() not in self.departments:
				self.departments[line[0].lower()] = line[2]
	
	# Make a mapping of all roles with more than 100 people.			
	def buildReferenceRoles(self):
	
		map_file = csv.reader(open(get_data('roles.tsv'),'r'),
							  delimiter='\t', encoding='utf-8')
		
		for line in map_file:
			
			if int(line[0]) >= 100:
				self.validroles[line[1]] = int(line[0])
				
	# Mappings of university departments.
	def buildFaculties(self):
		
		map_file = csv.reader(open(get_data('university_faculties.tsv'),'r'),
							  delimiter='\t', encoding='utf-8')
		
		for line in map_file:
			
			self.faculties[line[0].lower()] = line[1]


# A script to process roles.
def main():

	# Comment
	return 0
		
if __name__ == "__main__":
	sys.exit(main())
