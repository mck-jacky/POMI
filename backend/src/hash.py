'''
This file contains helper functions to hash sensitive information
'''


import hashlib
import jwt

def get_hash_of(info):
    '''
    Hash a string using the SHA 256 algorithm
    '''
    return hashlib.sha256(info.encode()).hexdigest()


def encode_jwt(token_data, SECRET):
    '''
    Given a token, encode it using jwt
    '''
    return jwt.encode(token_data, SECRET, algorithm='HS256')


def decode_jwt(token, SECRET):
    '''
    Decode a jwt token
    '''
    return jwt.decode(token, SECRET, algorithm='HS256')
