#!/usr/bin/env python

import time
import random
import requests
from bs4 import BeautifulSoup

OPEN_URL = 'O'
FIND_LINK = 'F'
EXEC_METHOD = 'E'

DYN_HOSTNAME = 'https://account.dyn.com/'

# the urls to open. (HOW, WHAT)
# HOW:
# 	O=directly open the url
# 	F=find the link identified by 'WHAT' (in the last requests response) and open it
URLS = (
	(OPEN_URL, DYN_HOSTNAME),
	(EXEC_METHOD, 'authenticate'),
	(FIND_LINK, 'My Hosts'),
	(FIND_LINK, 'Log Out'),
)

class DynDNS:
	def __init__(self, username, password, verbose=False):
		self.username = username
		self.password = password
		self.last_server_response = u''
		self.verbose = verbose
		self.success = False

		#init session
		self.session = requests.Session()
		self.session.headers.update(
			{'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:21.0) Gecko/20100101 Firefox/21.0'}
		)

	def login(self):
		"""
		logs in to DynDNS and return sa boolean whether the login was successful
		"""
		self.success = False # will be set by authenticate
		for (how, what) in URLS:
			if self.verbose:
				print('current action: %s for %s' % (how, what))
			if how == OPEN_URL:
				self.do_request(what)
			elif how == FIND_LINK:
				self.open_link(what)
			elif how == EXEC_METHOD:
				func = getattr(self, what)
				if not func:
					raise Exception('Method %s does not exist' % what)
				else:
					func()
			else:
				raise Exception('check your URLS configuration!')

			# let's be nice... or better hide that we're a script
			time.sleep(random.randint(0,4))
		return self.success

	def do_request(self, url):
		if self.verbose:
			print('\trequesting %s' % url)
		self.last_server_response = self.session.get(url)

	def open_link(self, linktext):
		soup = BeautifulSoup(self.last_server_response.text)
		links =  soup('a', text=linktext)
		if len(links) > 0:
			self.do_request(self._buildUrl(links[0]['href']))
		else:
			self.success = False
			#raise Exception('link "%s" not found' % linktext)

	def authenticate(self, ):
		data = {
			'username' : self.username,
			'password' : self.password,
			'submit' : 'Log in',
			'iov_id' : '', #not necessary
			'multiform' : self._findMultiformID(),
		}
		self.last_server_response = self.session.post(DYN_HOSTNAME,
			data=data,
			allow_redirects=True)
		self.success = ('Welcome&nbsp;<b>%s' % self.username) in self.last_server_response.text
		if self.verbose:
			print ('\tLogin successful' if self.success else '\tLogin failed')

	
	def _findMultiformID(self, ):
		"""Helper method needed to find the
		multiform element and return its value.
		"""
		multiform = ""
		soup = BeautifulSoup(self.last_server_response.text)
		form_input = soup.find('input', attrs={'name' : 'multiform'})
		if form_input:
			multiform =  form_input['value']
		return multiform

	def _buildUrl(self, href):
		"""
		checks the href link and returns an absolute http or https url

		either href already points to a http(s):// url or
		it's a path on the hostname
		"""
		href = href.lower()
		if u'https://' in href or u'http://' in href:
			return href
		else:
			return DYN_HOSTNAME + href if href[0] != u'/' else DYN_HOSTNAME + href[1:]

if __name__ == '__main__':
	import argparse
	import sys
	parser = argparse.ArgumentParser(description='a script to login to your free DynDNS account to prevent it from being deleted.')
	parser.add_argument('username')
	parser.add_argument('password')
	parser.add_argument('-v', action='store_true', help="verbose, show each step", default=False)
	args = parser.parse_args()

	success = DynDNS(args.username, args.password, args.v).login()
	if success:
		sys.exit(0)
	else:
		print('Login was not successfull!')
		sys.exit(1)

