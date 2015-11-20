#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
"""
twitterOrganizer-0.1.py

Created by Marcel Caraciolo on 2010-01-06.
e-mail: caraciol (at) gmail.com   twitter: marcelcaraciolo
Copyright (c) 2009 Federal University of Pernambuco. All rights reserved.
"""


''' My simple attempt to cluster the friends of the twitter and organize them in twitter lists '''



__author__ = 'caraciol@gmail.com'
__version__ = '0.1'


import twitterT
import Queue
import operator
import threading
import string
import time
import random
import pickle
import kmeans
try:
	import nltk
except ImportError:
	print 'Problems to import nltk, you have to install the Natural Language Toolkit. '
	exit()



#Step 04: Open the database and build the user profiles
databases = ['usersData.pk1']
data = []

for database in databases:
	inputF = open(database,'rb')
	data.append([pickle.load(inputF) for i in range(2)])

wordCounts = {}
apCounts = {}

for lt in data:
	wc = lt[0]
	wordCounts.update(wc)
	for user,words in wc.items():
		for word, count in words.items():
			apCounts.setdefault(word,0)
			apCounts[word]+=count


#Filter data
wordlist = []
for word,count in apCounts.items():
	if count > 3:
		wordlist.append(word)


#Join all together for parse it into the cluster algorithm
socialNetworking = {}

for user,wc in wordCounts.items():
	socialNetworking[user] = {}
	for word in wordlist:
		socialNetworking[user].setdefault(word,0)
		if word in wc:
			socialNetworking[user][word] = wc[word]


items  = socialNetworking.items()
users = [item[0] for item in items]
data =  [item[1].items() for item in items]

#Step 05:  Run a cluster algorithm (k-means)
g = kmeans.open_ubigraph_server()
result,clusters = kmeans.kcluster(g,users,data,k=15)

#Step 06: Presenting the results
usersResult =  [[users[v] for v in result[i] ] for i in range(len(result))]

dataClusters = []
for cluster in usersResult:
	apCount = {}
	for user in cluster:
		data = socialNetworking[user]
		for word,wc in data.items():
			apCount.setdefault(word,0)
			apCount[word]+= wc
	
	words = apCount.items()
	words.sort(key=operator.itemgetter(1))
	words.reverse()	
	dataClusters.append(words[0:10])

#Store all in the files
t = 1
for cluster in usersResult:
	fileName = 'list_%d.txt' %t
	fHandler = open(fileName,'w')
	fHandler.write('NAME:\n')
	msg = 'TAGS:'
	for data in dataClusters[t-1][0:10]:
		msg+= data[0]+ ','
	fHandler.write(msg.encode('utf-8')+'\n')
	msg = 'FRIENDS:'
	for user in usersResult[t-1]:
		msg += user + ','
	fHandler.write(msg)
	fHandler.close()
	t+=1
		
kmeans.showResults(dataClusters)


