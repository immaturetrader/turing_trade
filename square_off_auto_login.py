

"""
A sample Hello World server.

"""
import os
import requests
import telepot
import telegram
from flask import Flask, render_template, request
from turing_library.gcp_pub_sub import pub_sub
#from alice_blue import *
import re
import platform
import requests

import cookielib
import urllib
import urllib2

new_dir = os.getcwd()
os.chdir(new_dir)

url = 'https://squareoffbots.com/aliceblue/login/'
url='https://ant.aliceblueonline.com/oauth/login/'
#url='https://leads.aliceblueonline.com/ANTAPI/'
client_id='AB126971'
password='497666124153$Ai'

values = {'client_id': client_id,
          'password': password}

r = requests.post(url, data=values,allow_redirects=True)


class WebGamePlayer(object):

    def __init__(self, login, password):
        """ Start up... """
        self.login = login
        self.password = password

        self.cj = cookielib.CookieJar()
        self.opener = urllib2.build_opener(
            urllib2.HTTPRedirectHandler(),
            urllib2.HTTPHandler(debuglevel=0),
            urllib2.HTTPSHandler(debuglevel=0),
            urllib2.HTTPCookieProcessor(self.cj)
        )
        self.opener.addheaders = [
            ('User-agent', ('Mozilla/4.0 (compatible; MSIE 6.0; '
                           'Windows NT 5.2; .NET CLR 1.1.4322)'))
        ]

        # need this twice - once to set cookies, once to log in...
        self.loginToFacebook()
        self.loginToFacebook()

    def loginToFacebook(self):
        """
        Handle login. This should populate our cookie jar.
        """
        login_data = urllib.urlencode({
            'client_id' : self.login,
            'password' : self.password,
        })
        response = self.opener.open("https://login.facebook.com/login.php", login_data)
        return ''.join(response.readlines())
    
    
WebGamePlayer(client_id,password)