#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
"""
twitterCollector-0.1.py

Created by Marcel Caraciolo on 2010-01-06.
e-mail: caraciol (at) gmail.com   twitter: marcelcaraciolo
Copyright (c) 2009 Federal University of Pernambuco. All rights reserved.
"""


''' My simple attempt to cluster the friends of the twitter and organize them in twitter lists '''



__author__ = 'caraciol@gmail.com'
__version__ = '0.1'


import twitterT
import Queue
import threading
import string
import time
import random
import pickle
try:
	import nltk
except ImportError:
	print 'Problems to import nltk, you have to install the Natural Language Toolkit. '
	exit()



class TwitterMiner(threading.Thread):
	''' Threaded Twitter Miner '''
	def __init__(self,queue,strct,api,apiU):
		threading.Thread.__init__(self)
		self.queue = queue
		self.api = api
		self.apiU = apiU
		self.strct = strct	

	def getWords(self,text):
		#Parse the statuses and returns the list of words for each text
		
		#Create the stop words list
		stopwords_pt = nltk.corpus.stopwords.words('portuguese')
		stopwords_pt = map(lambda w: unicode(w, 'utf-8'), stopwords_pt)
		stopwords_en = nltk.corpus.stopwords.words('english')
		stopwords_en = map(lambda w: unicode(w, 'utf-8'), stopwords_en)

		#Split the words by spaces
		words = text.split(" ")
		
		#Remove all illegal characters and convert to lower case
		RemoveWords = string.punctuation
		for item in RemoveWords:
			words = [word.replace(item,'') for word in words]
		words = filter(lambda word: not word.isdigit(), words)
		words = [word.replace("RT",'') for word in words]
		words = filter(lambda word: not word.startswith('http'),words)
		words = filter(lambda word: word != '', words)
		words = [word.lower() for word in words]
		words = filter(lambda word: not word in stopwords_en, words)
		words = filter(lambda word: not word in stopwords_pt, words)

		return words
	
	
	def run(self):
		while True:
			#Grabs statuses from queue
			user,statuses = self.queue.get()
			
			wc  = {}
			
			#Loops over all the entries
			for e in statuses:
				text = e[6]
				#Extract a list of words
				words = self.getWords(text)
				for word in words:
					wc.setdefault(word,0)
					wc[word]+=1
			
			if len(statuses) > 0:
				self.strct.append((statuses[0][1],wc))
			
			else:
				try:
					self.strct.append((self.api.GetUser(user).GetScreenName(),wc))
				except:
					self.strct.append((self.apiU.GetUser(user).GetScreenName(),wc))
			print len(self.strct)
			self.queue.task_done()


class TwitterCollector(threading.Thread):
	''' Threaded Twitter Collector '''
	def __init__(self,queue, out_queue,api, apiU):
		threading.Thread.__init__(self)
		self.queue = queue
		self.out_queue = out_queue
		self.api = api
		self.apiU = apiU

	def getStatuses(self,id=None,statusLimit=200):
		""" Get the statuses from the user 
			Parameters:
				api: The api connector for python-twitter
				id: the twitter ID
				statusLimit: the number of statuses to fetch
			Return:
				statusList: the list of statuses
		"""
		page = 1
		statusFlag = True
		statusList = []
		screenName = None
		api = self.api
		statuses = None
		
		while statusFlag:
			for i in range(5):
				try:
					statuses = api.GetUserTimeline(user_id=id,page=page,count=100)
					break
				except:
					print " FAILED user " + str(id) + ", retrying"
					if i == 2:
						api = self.apiU						
				time.sleep(4)

			if len(statuses) > 0 and len(statusList) < statusLimit:
				tempList = [(status.GetId(),status.GetUser().GetScreenName(),status.GetCreatedAt(),status.GetRelativeCreatedAt(), status.GetInReplyToScreenName(), status.GetFavorited(), status.GetText()) for status in statuses]
				statusList.extend(tempList)
				if len(statusList) > statusLimit:
					statusFlag = False
					page+=1
			else:
				statusFlag = False


		print "Loaded user %d . total %s" % (id,len(statusList))
		return statusList

	
	def run(self):
		while True:
			#Grabs user from queue
			user = self.queue.get()
			
			#Grabs the statuses from the users
			statuses = self.getStatuses(user,100)
			
			self.out_queue.put((user,statuses))
			
			self.queue.task_done()
			

USERNAME = ''
PASSWORD = ''

STATUSES_MAX = 100
TOTAL_REQUESTS = 0
NUMBER_OF_FRIENDS = 100



#Step 01: Getting the friends of the user

apiU = twitterT.Api(username=USERNAME, password=PASSWORD)
api = twitterT.Api()

#Bug 01: Until now it only works with 5000 friends at maximum.
usersIDList = api.GetFriendsIds(USERNAME)

users = []

for i in range(NUMBER_OF_FRIENDS):
	random.shuffle(usersIDList)
	users.append(usersIDList[0])
	del usersIDList[0]



print 'Loaded users. Total: %s' % str(len(users))

#Step 02: Get the last n statuses from each friend
output = open('usersData.pk1','wb')

queue = Queue.Queue()
out_queue = Queue.Queue()
wordCount = []


for i in range(12):	
	t = TwitterCollector(queue,out_queue,api,apiU)
	t.setDaemon(True)
	t.start()

for userID in users:
	queue.put(userID)

for i in range(12):
	tm = TwitterMiner(out_queue,wordCount,api,apiU)
	tm.setDaemon(True)
	tm.start()
	
	
queue.join()
out_queue.join()

wordCounts = {}
apCount = {}

#Step 3: Load it at the database
for screenName,wc in wordCount:
		wordCounts[screenName] = wc
		for word, count in wc.items():
			apCount.setdefault(word,0)
			if count > 1:
				apCount[word]+=1

pickle.dump(wordCounts,output)
pickle.dump(apCount,output)
output.close()
