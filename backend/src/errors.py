'''
This file contains two custom exception classes used for raising errors in
the python code
'''

from werkzeug.exceptions import HTTPException


class AccessError(HTTPException):
    code = 400
    message = 'No message specified'


class InputError(HTTPException):
    code = 400
    message = 'No message specified'
