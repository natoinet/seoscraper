from datetime import datetime
from calendar import timegm 
import threading
import json

import jwt
import treq
from envparse import env

from core.singleton import SingletonMixin

class GoogleToken(SingletonMixin):
    def __init__(self):
        env.read_envfile()
        self.audience = 'https://www.googleapis.com/oauth2/v4/token'
        self.issued_at = None
        self.expire = None
        self.str_jwt = None
        self.token = None
        self.headers = None

    def get_jwt(self, scope):
        if (self.str_jwt is None):
            json_file = json.load(open(env.str('GOOGLE_API_PRIVATE_FILE')))

            self.issued_at = timegm(datetime.datetime.utcnow().utctimetuple())
            self.expire = self.issued_at + 3600
        
            payload = { 'iss' : json_file['client_email'], 
                'scope' : scope, 
                'aud' : self.audience, 
                'exp' : self.expire, 
                'iat' : self.issued_at }

            self.str_jwt = str(jwt.encode(payload, json_file['private_key'], algorithm='RS256'), 'utf-8')
        
        return self.str_jwt
    
    def get_token(self, scope):
        if (self.token is None):
            data = {'grant_type' : 'urn:ietf:params:oauth:grant-type:jwt-bearer', 'assertion' : self.get_jwt(scope) }

            d = treq.post('http://httpbin.org/post', data)
            d.addCallback(print_response)
            return d
            
            response_token = requests.post(self.audience, 
                data = {'grant_type' : 'urn:ietf:params:oauth:grant-type:jwt-bearer', 'assertion' : self.get_jwt(scope) } )

            self.token = response_token.json()['access_token']

        return self.token
        
    def get_headers(self, scope):
        if (self.headers is None):
            self.headers = {'Authorization': 'Bearer ' + self.get_token(scope)}
    
        return self.headers