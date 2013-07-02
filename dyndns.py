#!/usr/bin/env python

import time, random, cookielib, urllib2, urllib
import requests
from bs4 import BeautifulSoup

OPEN_URL = 'O'
FIND_LINK = 'F'
EXEC_METHOD = 'E'

# the urls to open. (HOW, WHAT)
# HOW:
# 	O=directly open the url
# 	F=find the link identified by 'WHAT' (in the last requests response) and open it
URLS = (
	(OPEN_URL, 'https://account.dyn.com/'),
	(EXEC_METHOD, 'authenticate'),
	(FIND_LINK, 'My Hosts'),
	(FIND_LINK, 'Log Out'),
)

class DynDNS:
	def __init__(self, username, password):
		self.username = username
		self.password = password
		self.opener = None
		self.last_server_response = u''

		#init session
		self.session = requests.Session()
		self.session.headers.update(
			{'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:21.0) Gecko/20100101 Firefox/21.0'}
		)

	def login(self, verbose=False):
		for (how, what) in URLS:
			if verbose:
				print 'current action: %s for %s' % (how, what)
			if how == OPEN_URL:
				self.do_request(what)
			elif how == FIND_LINK:
				self.open_link(what)
			elif how == EXEC_METHOD:
				func = getattr(self, what)
				if not func:
					raise Exception("Method %s does not exist" % what)
				else:
					func()
			else:
				raise Exception("check your URLS configuration!")

			# let's be nice... or better hide that we're a script
			time.sleep(random.randint(0,4))

	def do_request(self, url):
		self.last_server_response = self.session.get(url)

	def open_link(self, linktext):
		soup = BeautifulSoup(self.last_server_response.text)
		print soup('a', text=linktext)

	def authenticate(self, ):
		data = {
			'username' : self.username,
			'password' : self.password,
			'submit' : 'Log in',
			'iov_id' : '', #not necessary
			'multiform' : self._findMultiformID(),
		}
		self.last_server_response = self.session.post("https://account.dyn.com/",
													  data=data,
													  allow_redirects=True)
		#print ('Login successful' if self.username in self.last_server_response.text else '')

	
	def _findMultiformID(self, ):
		"""Helper method needed to find the
		multiform element and return its value.

		BS doesn't seem to find the multiform input-element
		with soup.find(attrs={"name": "multiform"})
		"""
		multiform = ""
		soup = BeautifulSoup(self.last_server_response.text)
		form = soup.find('form')
		for child in form.children:
			try:
				if u'multiform' in child.attrs.values():
				   multiform = child.attrs['value']
			except AttributeError:
				pass
		return multiform

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description='a script to login to your free DynDNS account to prevent it from being deleted.')
	parser.add_argument('username')
	parser.add_argument('password')
	parser.add_argument('-v', action='store_true', help="verbose, show each step", default=False)
	args = parser.parse_args()

	DynDNS(args.username, args.password).login(args.v)
