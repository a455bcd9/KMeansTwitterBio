#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
"""
twitterList.py

Created by Marcel Caraciolo on 2010-01-06.
e-mail: caraciol (at) gmail.com   twitter: marcelcaraciolo
Copyright (c) 2009 Federal University of Pernambuco. All rights reserved.
"""


'''Simple wrapper for Twitter API in order to create and manage Twitter Lists '''



__author__ = 'caraciol@gmail.com'
__version__ = '0.1'

import simplejson
import urllib
import urlparse


class TwitterError(Exception):
	""" Base class for Twitter errors """
	
	@property
	def message(self):
		"""Returns the first argument used to construct this error """
		return self.args[0]


class TwitterListAPI(object):
	
	
	def __init__(self,username=None,password=None):
		'''Instantiate a new TwitterList.TwitterListAPI object.

	  	Args:
			username: the twitter username. (In this case it can be the twitter username).
			password: the twitter password. (In this case it can be the twitter password).
			
		'''
		self._urllib = urllib
		self._InitializeRequestHeaders()
		self._InitializeDefaultParameters()
		self.SetCredentials(username,password)


	
	def SetCredentials(self,username=None,password=None,apikey=None):
		""" Set the username, password for this instance

		Args:
			username: the twitter username. (In this case it can be the twitter username).
			password: the twitter password. (In this case it can be the twitter password).
		"""
		self._username = username
		self._password = password


	def _InitializeRequestHeaders(self):	
		self._request_headers = {}

	def _InitializeDefaultParameters(self):
		self._default_params = {}
		
	
	def createList(self,name,private=False,description=None):
		
		""" Creates a new list for the authenticated user. Accounts are limited to 20 lists.

			Args:
				name: The name of the list you are creating.
				private:  Whether your list is public or private. If True the mode is set to private.
						  Otherwise public.  The default value is False (public)
				description: The description of the list.
		
			Returns:
				The list instance created at Twitter
		"""
		if not self._username or not self._password:
			raise TwitterError('You must have a valid user/password for this operation')
		
		postData = {}
		
 		url = 'http://api.twitter.com/1/%s/lists.json' % self._username

		postData['name'] = name
		
		if private:
			postData['mode'] = 'private'
		else:
			postData['mode'] = 'public'
		
		if description:
			postData['description'] = description
			
		
		json = self._FetchUrl(url,post_data=postData)
		
		try:
			data = simplejson.loads(json)
		except:
			raise TwitterError(json)
			
		self._CheckForTwitterError(data)
		
		return data
		
		
	
	def updateList(self,name,newName=None,private=False,description=None):
		
		""" Updates the specified list.

			Args:
				name: the current name of the list
				newName: The name of the list you'd like'the list name to.
				private:  Whether your list is public or private. If True the mode is set to private.
						  Otherwise public.  The default value is False (public)
				description: The description of the list.
		
			Returns:
				The list instance updated at Twitter
		"""
		if not self._username or not self._password:
			raise TwitterError('You must have a valid user/password for this operation')
		
		postData = {}
		
 		url = 'http://api.twitter.com/1/%s/lists/%s.json' % (self._username,name)

		if newName:
			postData['name'] = newName
		
		if private:
			postData['mode'] = 'private'
		else:
			postData['mode'] = 'public'
		
		if description:
			postData['description'] = description
			
		json = self._FetchUrl(url,post_data=postData)
				
		data = simplejson.loads(json)
		
		self._CheckForTwitterError(data)
		
		return data
		
	
	
	def deleteList(self,id):
		
		""" Deletes the specified list. Must be owned by the authenticated user.

			Args:
				id: The slug of the list.
		
			Returns:
				The list instance removed at Twitter
		"""
		if not self._username or not self._password:
			raise TwitterError('You must have a valid user/password for this operation')
		
		postData = {}
		
 		url = 'http://api.twitter.com/1/%s/lists/%s.json' % (self._username,id)


		postData['_method'] = 'DELETE'
		
			
		json = self._FetchUrl(url,post_data=postData)
				
		data = simplejson.loads(json)
		
		self._CheckForTwitterError(data)
		
		return data
		
		
	
	def addUser(self,list_id,user_id):
		
		""" Add a member to a list. The authenticated user must own the list to be able to add members to it. 
			Lists are limited to having 500 members.
			
			Args:
				list_id: The slug of the list.
				user_id: The id of the user to add as member of the list
				
			Returns:
				The list instance udpated at Twitter
		"""
		if not self._username or not self._password:
			raise TwitterError('You must have a valid user/password for this operation')
		
		try:
			user_id = int(user_id)
		except:
			raise TwitterError('It must be a valid user_id (integer)')
			
		postData = {}
		
 		url = 'http://api.twitter.com/1/%s/%s/members.json' % (self._username,list_id)
		
		postData['id'] = user_id
			
		json = self._FetchUrl(url,post_data=postData)
				
		data = simplejson.loads(json)
		
		self._CheckForTwitterError(data)
		
		return data

	def removeUser(self,list_id,user_id):

		""" Removes the specified member from the list. 
			The authenticated user must be the list's owner to remove members from the list.

			Args:
				list_id: The slug of the list.
				user_id: The id of the user to add as member of the list

			Returns:
				The list instance udpated at Twitter
		"""
		if not self._username or not self._password:
			raise TwitterError('You must have a valid user/password for this operation')

		try:
			user_id = int(user_id)
		except:
			raise TwitterError('It must be a valid user_id (integer)')

		postData = {}

 		url = 'http://api.twitter.com/1/%s/%s/members.json' % (self._username,list_id)


		postData['id'] = user_id
		
		postData['_method'] = 'DELETE'

		json = self._FetchUrl(url,post_data=postData)

		data = simplejson.loads(json)

		self._CheckForTwitterError(data)

		return data
	
	def _FetchUrl(self, url, post_data = None, parameters = None):
		""" Fetch a URL  method request GET/POST
			Args:
				url: the url to retrieve
				post_data:
					A dict of (str,unicode) key/value pairs. if set, POST will be used.
				parameters:
					a dict whose key/values pair should encoded and added to the query string. [OPTIONAL]

			Returns:
				A string containing the body of the response
		"""
		
		#Build the extra parameters dict
		extra_params = {}
		if self._default_params:
			extra_params.update(self._default_params)
		
		if parameters:
			extra_params.update(parameters)
			
		
		#Add key/value parameters to the query string of the url
		url = self._BuildUrl(url,extra_params=extra_params)
		
		#Get a url opener that can handle basic auth
		opener = self._GetOpener(username=self._username,password=self._password)
			
		#Encode the POST data
		encoded_post_data = self._EncodePostData(post_data)
		
		#Open the URL request
		url_data = opener.open(url,encoded_post_data).read()		
		opener.close()

		#Always return the latest version
		return url_data
		
	
	def getUserID(self,user):
		'''Returns a single userID.

		The twitterLis.TwitterListAPI instance must be authenticated.
		
		Args:
		user: The username or id of the user to retrieve.
		
		Returnss:
			A twitter.User instance representing that user

		'''
	    
		url = 'http://twitter.com/users/show/%s.json' % user
		json = self._FetchUrl(url)
		data = simplejson.loads(json)
		self._CheckForTwitterError(data)
		return data['id']	  
	
	
	def loadFile(self,filePath):
		''' Load a file with the list settings
		
		Args:
			filePath: The filePath with the Lists.
		
		Returns:
			the tuple with (name,tagsList,membersList)
		
		'''
		try: 
			fHandler = open(filePath,'r')
		except:
			raise Exception('File not found or some problems with the file!')
		
		name = ''
		tagList = []
		friendsList = []
		
		for line in fHandler:
			if line.startswith('NAME'):
				name = line.split(':')[1]
				name = name.rstrip()
				continue
				
			if line.startswith('TAGS'):
				tagList = []
				tags = line.split(':')[1]
				tags = tags.split(',')
				for tag in tags[:-1]:
					tagList.append(tag.encode('utf-8').rstrip())
				continue
			
			if line.startswith('FRIENDS'):
				friendsList = []
				friends = line.split(':')[1]
				friends = friends.split(',')
				for friend in friends[:-1]:
					friendsList.append(friend.encode('utf-8').rstrip())
				continue
				
		return (name,tagList,friendsList)
			
	def loadFiles(self, fileList):
		'''A wrapper for reading lists more than one.
		Args:
			fileList: the list of files
		Returns:
			the list of tuples (name,tags,members)
		'''
		
		twitterLists = []
		for fileP in fileList:
			twitterLists.append(self.loadFile(fileP))
		return twitterLists
		
	def _EncodePostData(self,post_data):
		""" Return a string in key=value&key=value form
		
		Args:
			post_data:
				A dict of (key,value) tuples.
		
		Returns:
			A URL-encoded string in 'key=value&key=value' form
		
		"""
		if post_data is None:
			return None
		elif type(post_data) == type({}):
			return urllib.urlencode(dict([(k,value) for k,value in post_data.items()]))
		else:
			return post_data
		
	def _EncodeParameters(self,parameters):
		""" Return a string in key=value&key=value form
			
			Value of None are not included in the output string.
			
			Args:
				parameters:
					A dict of (key,value) tuples.
			
			Return:
				a URL-encoded string in 'key=value&key=value' form
		"""
		if parameters is None:
			return None
		else:
			return urllib.urlencode(dict([ (k,value) for k,value in parameters.items() if value is not None]))


	class _FancyURLopener(urllib.FancyURLopener):
		""" This class handles the basic auth, providing user and password 
			when required by http response codd 401
		"""
		def __init__(self,usr,pwd):
			""" Set user/password for http and call base class constructor
			"""
			urllib.FancyURLopener.__init__(self)
			self.usr = usr
			self.pwd = pwd


		def prompt_user_passwd(self,host,realm):
			"""
			Basic auth callback
			"""
			return (self.usr, self.pwd)


	def _GetOpener(self,username=None, password=None):
		if username and password:
			opener = TwitterListAPI._FancyURLopener(username,password)
		else:
			raise TwitterError("Until now no handler for No-Authenticated access")
		opener.addheaders = self._request_headers.items()
		return opener

	
	def _BuildUrl(self,url,path_elements=None, extra_params=None):
		#Break url into consituent parts
		(scheme,netloc,path,params,query,fragment) = urlparse.urlparse(url)
		
		#Add any additional path elements to the path
		if path_elements:
			#Filter out the path elements that have a value of None
			p = [i for i in path_elements if i]
			if not path.endswith('/'):
				path+='/'
			path += '/'.join(p)
		
		#Add any additional query parameters to the query string
		if extra_params and len(extra_params) > 0:
			extra_query = self._EncodeParameters(extra_params)
			#Add it to the existing query
			if query:
				query += '&' + extra_query
			else:
				query = extra_query
		
		#Return the rebuilt URL
		return urlparse.urlunparse((scheme,netloc,path,params,query,fragment))
		

	def _CheckForTwitterError(self,data):
		""" Raises a Twitter Error if tweetphoto returns a error message.

		Args:
			data: a python dict created from Twitter json response.

		Raises:
			TwitterError wrapping the tweetphoto error message if one exists.

		"""
		if 'error' in data:
			raise TwitterError(data['error'])
	


if __name__ == '__main__':
	
	from optparse import OptionParser
	
	
	optPsr = OptionParser('usage: %prog -u USER_NAME -p PASSWORD -l LIST_PATH')
	optPsr.add_option('-u', '--user', type='string', help='Twitter user name')
	optPsr.add_option('-p', '--passwd', type='string', help='Twitter password')
	optPsr.add_option('-l', '--list' , type='string', help= 'Path of the lists')

	(opts,args) = optPsr.parse_args()
	
	if not opts.user:
		optPsr.error('no USER_NAME')

	if not opts.passwd:
		optPsr.error('no PASSWORD')
	
	if not opts.list:
		optPsr.error('no LIST')
		
	try:
		lists = opts.list.split(',')
		if len(lists) == 0:
			opts.error('Invalid format of Lists. It must be: file1,file2...')
	except:
		opts.error('Invalid format of Lists. It must be: file1,file2...')
	
	
	print 'Authenticating ...'
	api = TwitterListAPI(opts.user,opts.passwd)
	
	print 'Reading files...'
	fList = api.loadFiles(lists)
	
	print 'Creating lists...'
	t = 0
	for name,tags,members in fList:
		tgs = ",".join(tags)
		if len(name) == 0:
			raise Exception('Problems in creating the list. Check the NAME: in the %s file' % lists[t])
		api.createList(name,description=tgs)
		
		for member in members:
			userID = api.getUserID(member)
			api.addUser(name,userID)
		t+=1
	
	print 'Lists created !'
	