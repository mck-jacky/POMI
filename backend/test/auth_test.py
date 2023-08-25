'''
This file tests the functions from auth.py: auth_login, auth_register, auth_logout
'''

import pytest
from src.auth import auth_login, auth_logout, auth_register, auth_passwordreset_request, auth_passwordreset_reset
from src.errors import InputError, AccessError
from test.other import clear


def test_login():
    '''
    This tests the auth_login function, if the user is already registered 
    and have the right password, they should log on successfully
    '''
    clear()
    # REGISTER a user called Jack Citizen, with email and password
    register = auth_register("luyapan1202@gmail.com", "1234567", "Luya", "Pan",
                             "Luya Pan", "1111222233334444", 12, 2023, "123")
    login = auth_login("luyapan1202@gmail.com", "1234567")
    assert register['email'] == login["email"]

    with pytest.raises(InputError):
        # email not registered
        auth_login("didnotregister@gmail.com", "28793247924")

    with pytest.raises(InputError):
        # wrong password
        auth_login("luyapan1202@gmail.com", "28197311")


def test_login_invalid_email():
    '''
    This function tests the function when an invalid email address is entered
    '''
    clear()
    auth_register("luyapan1202@gmail.com", "1234567", "Luya", "Pan",
                  "Luya Pan", "1111222233334444", 12, 2023, "123")

    with pytest.raises(InputError):
        # email entered is not a valid email
        auth_login("abcdefg", "321ABC!!!")


def test_logout():
    '''
    This tests the auth_logout function - whether user is able to log out
    successfully given a valid token
    '''

    clear()
    result_register = auth_register("luyapan1202@gmail.com", "1234567", "Luya", "Pan",
                                    "Luya Pan", "1111222233334444", 12, 2023, "123")
    result_login = auth_login("luyapan1202@gmail.com", "1234567")

    assert result_register['email'] == result_login["email"]

    # user needs a valid token to be logged out
    valid_token = result_login['token']

    # with a valid token, result should be a dictionary with key 'is_success'
    result_logout = auth_logout(valid_token)

    # if the user is successfully logged out it would return a dict with 'is_success' == True
    assert result_logout['is_success'] is True

    # Once user is logged already, then can't logout again
    invalidated_token = result_login['token']

    with pytest.raises(AccessError):
        # Trying to use an invalidated token
        auth_logout(invalidated_token)

    # Invalid Token
    with pytest.raises(AccessError):
        auth_logout("invalid token")


def test_register_email():
    '''
    This tests the auth_register function - whether auth_register can
    successfully register an user with an unregistered/valid email.
    '''

    clear()
    result_register = auth_register("luyapan1202@gmail.com", "1234567", "Luya", "Pan",
                                    "Luya Pan", "1111222233334444", 12, 2023, "123")
    result_login = auth_login("luyapan1202@gmail.com", "1234567")

    assert result_register['email'] == result_login["email"]

    with pytest.raises(InputError):
        # email is already taken
        auth_register("luyapan1202@gmail.com", "123ABCD!", "Jack", "Jackson", "jack j",
                      "1234567812345678", 10, 2024, "321")

    with pytest.raises(InputError):
        # invalid email
        auth_register("registerme", "123ABCD!", "Jack", "Jackson", "jack j",
                      "1234567812345678", 10, 2024, "321")


def test_register_invalid_names():
    '''
    This function tests the auth_register function for invalid names
    '''
    clear()
    auth_register("luyapan1202@gmail.com", "1234567", "Luya", "Pan",
                  "Luya Pan", "1111222233334444", 12, 2023, "123")

    with pytest.raises(InputError):
        # first name is too short (less than 1)
        auth_register("newemail@gmail.com", "123ABCD!", "", "Citizen",
                      "citizen citizen", "1111222233334444", 12, 2023, "123")

    with pytest.raises(InputError):
        # last name is too short
        auth_register("newemail@gmail.com", "123ABCD!", "James", "",
                      "citizen citizen", "1111222233334444", 12, 2023, "123")

    with pytest.raises(InputError):
        # first name is too long (longer than 50)
        auth_register("newemail@gmail.com", "123ABCD!",
                      "thisnameisveryveryveryverysupersupersuperloooggggggg", "Citizen",
                      "citizen citizen", "1111222233334444", 12, 2023, "123")

    with pytest.raises(InputError):
        # last name is too long
        auth_register("newemail@gmail.com", "123ABCD!", "James",
                      "thisnameisveryveryveryverysupersupersuperloooggggggg",
                      "citizen citizen", "1111222233334444", 12, 2023, "123")

    with pytest.raises(InputError):
        # both first name and last name are too short
        auth_register("newemail@gmail.com", "123ABCD!", "", "",
                      "citizen citizen", "1111222233334444", 12, 2023, "123")

    with pytest.raises(InputError):
        # empty string name field
        auth_register("newemail@gmail.com", "123ABCD!", " ", "ha",
                      "citizen citizen", "1111222233334444", 12, 2023, "123")

    with pytest.raises(InputError):
        # empty string name field
        auth_register("newemail@gmail.com", "123ABCD!", "name", " ",
                      "citizen citizen", "1111222233334444", 12, 2023, "123")

    with pytest.raises(InputError):
        # both too long
        auth_register("newemail@gmail.com", "123ABCD!",
                      "thisnameisveryveryveryverysupersupersuperloooggggggg",
                      "thisnameisveryveryveryverysupersupersuperloooggggggg",
                      "citizen citizen", "1111222233334444", 12, 2023, "123")


def test_auth_passwordreset_request():
    '''
    This tests the auth_passwordreset_request function
    '''
    clear()
    auth_register("registerme@gmail.com", "321ABCD!@#", "Jack", "Citizen",
                  "citizen citizen", "1111222233334444", 12, 2023, "123")
    # assert auth_passwordreset_request("registerme@gmail.com") == {}

    with pytest.raises(InputError):
        auth_passwordreset_request("notregistered@gmail.com")


def test_auth_passwordreset_reset():
    '''
    This tests the auth_passwordreset_reset function
    '''
    clear()
    # Register a user to be used
    result = auth_register("registerme@gmail.com", "321ABCD!@#", "Jack", "Citizen",
                           "citizen citizen", "1111222233334444", 12, 2023, "123")
    # Register a user that will not be used (to ensure coverage is 100%)
    auth_register("registermeee@gmail.com", "321ABCD!@#", "Jacks", "Citizens",
                  "citizen citizen", "1111222233334444", 12, 2023, "123")

    # Request password reset
    request = auth_passwordreset_request("registerme@gmail.com")

    # Assert correct functionality
    assert auth_passwordreset_reset(request['secret'], "newpassword123") == {}

    # Invalid password - too short
    with pytest.raises(InputError):
        auth_passwordreset_reset(request['secret'], "12")
