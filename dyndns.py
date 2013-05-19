#!/usr/bin/env python

import time, random, cookielib, urllib2, urllib
from bs4 import BeautifulSoup

OPEN_URL = 'O'
FIND_LINK = 'F'
EXEC_METHOD = 'E'

# the urls to open. (HOW, WHAT)
# HOW:
# 	O=directly open the url
# 	F=find the link identified by 'WHAT' (in the last requests response) and open it
URLS = (
	(OPEN_URL, 'https://account.dyn.com/entrance/'),
	(EXEC_METHOD, 'authenticate'),
	(FIND_LINK, 'My Hosts'),
	(FIND_LINK, 'Log Out'),
)

class DynDNS:
	def __init__(self, username, password):
		self.username = username
		self.password = password
		self.opener = None
		self.last_server_response = str('')

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

	def do_request(self, req_or_url):
		self.last_server_response = self.get_opener().open(req_or_url).read()

	def open_link(self, linktext):
		soup = BeautifulSoup(self.last_server_response)
		print soup('a', text=linktext)

	def get_opener(self):
		if self.opener:
			return self.opener

		cj = cookielib.CookieJar()
		self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
		self.opener.addheaders = [
			('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:21.0) Gecko/20100101 Firefox/21.0'),
		]
		return self.opener

	def authenticate(self, ):
		raise Exception("Not fully implemented yet")
		soup = BeautifulSoup(self.last_server_response)
		data = urllib.urlencode(
			{
			'username' : self.username,
			'password' : self.password,
			'submit' : 'Log in',
			'iov_id' : '', #TODO...
			'multiform' : soup('input', {'name' : 'multiform'})[0]['value']
			}
		)
		req = urllib2.Request('SERVER / PATH...', data) #TODO
		self.last_server_response = self.get_opener().open(req).read()


if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description='a script to login to your free DynDNS account to prevent it being deleted.')
	parser.add_argument('username')
	parser.add_argument('password')
	parser.add_argument('-v', action='store_true', help="verbose, show each step", default=False)
	args = parser.parse_args()

	DynDNS(args.username, args.password).login(args.v)