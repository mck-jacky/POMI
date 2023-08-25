'''
This file contains authentication functions such as register, login/log out, and password reset
'''

import smtplib
import re
import hashlib
import jwt
import sys
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from .data import users, valid_token_list, db_state
from .hash import get_hash_of, encode_jwt, decode_jwt
from .errors import InputError, AccessError
from .data_helper import add_account_to_database, password_match, find_user, change_password_in_database
from .helper_functions import send_email_helper


SYSTEM_EMAIL = "pomipomi2023@gmail.com"
EMAIL_PASSWORD = "zlpwyjaxbmfgsvfp"
EMAIL_SUBJECT = 'Your reset code for Pomi'
REGEX = '^[a-z0-9]+[\\._]?[a-z0-9]+@(?:\\w+\\.)+\\w{2,3}$'
SECRET = "HelloWorld2023"


def send_email(target_email, reset_code):
    '''
    Sends an email from pomipomi2023@gmail.com to users who requested for a password 
    reset with the reset code
    '''
    message_to_send = "Your reset code for your Pomi account is:\n\n" + \
        reset_code + "\n\nPlease use it to reset your password." +\
        "\n\nNote that this reset code expires in 15 minutes."
        
    # send the reset code to the user who requested a reset
    send_email_helper(target_email, reset_code,
                      message_to_send, "Your reset code for Pomi")


def check_valid_email(email):
    '''
    Checks if an email address is valid. 
    If the email address is valid, return 1, else return 0
    '''
    # If email is valid, return 1
    if re.search(REGEX, email):
        return 1
    # If the email is not valid, return 0
    return 0


def auth_register(input_email, password, first_name, last_name, cardholder_name, card_number,
                  expiry_month, expiry_year, cvv_num):
    '''
    Given a user's first and last name, email address, and password, create
    a new account and return a new token for authentication in their
    session.
    '''

    global users, valid_token_list

    # Raise error if first name is outside the range of 1 - 50 characters
    if len(first_name) > 50 or len(first_name) < 1:
        raise InputError(
            description='First name should be between 1 and 50 characters')

    # Raise error if last name is outside the range of 1 - 50 characters
    if len(last_name) > 50 or len(last_name) < 1:
        raise InputError(
            description='Last name should be between 1 and 50 characters')

    if first_name == ' ':
        raise InputError(
            description='First name cannot be an empty string')

    if last_name == ' ':
        raise InputError(
            description='Last name cannot be an empty string')

    # Check if email is valid
    if check_valid_email(input_email) == 0:
        raise InputError(
            description='Sorry, the email you entered is not valid.')

    # Check if email is already associated with an account
    for user in users:
        if user['login']['email'] == input_email:
            raise InputError(
                description='Email is taken! Please enter another email.')

    # If password is too short, raise error
    if len(password) < 6:
        raise InputError(
            description='Password is too short: password must not be less than 6 characters')

    # If card number entered involves characters other than digits, raise error
    if not card_number.isdigit():
        raise InputError(description='Card number should all be digits')

    # If card number is not exactly 16 digits, raise error
    # (Converts the number to an int, and back to a str, to remove leading zeroes)
    if len(str(int(card_number))) != 16:
        raise InputError(description='Card number should be 16 digits')

    # expiry month should be between 1 and 12
    try:
        expiry_month = int(expiry_month)
        if expiry_month < 1 or expiry_month > 12:
            raise InputError(description='Month should be between 1 or 12')
    except:
        raise InputError(description='Month should be between 1 or 12')

    # year should consist of 4 digits
    if len(str(expiry_year)) != 4:
        raise InputError(description='Year should consist of 4 digits')

    try:
        expiry_year = int(expiry_year)
        if len(str(expiry_year)) != 4:
            raise InputError(description='Year should consist of 4 digits')
    except:
        raise InputError(description='Year should consist of 4 digits')

    # expiry year must be >= current year
    expiry_month = int(expiry_month)
    expiry_year = int(expiry_year)
    if expiry_year < datetime.today().year:
        raise InputError(description='Expiry year cannot be before this year')

    # Expiry date must be after today
    if expiry_year == datetime.today().year and expiry_month < datetime.today().month:
        raise InputError(description='Expiry date cannot be before today')

    if len(cvv_num) != 3:
        raise InputError(description='The cvv must be 3 digits')

    try:
        cvv_num = int(cvv_num)
    except:
        raise InputError(description='The cvv should all be digits')

    # return a token to user
    return_info = {
        'email': input_email,
        'token': '',
    }

    if db_state == True:
        add_account_to_database(input_email, get_hash_of(password), first_name, last_name,
                                card_number, cvv_num, cardholder_name, expiry_month, expiry_year)

    new_user_info = {
        'name_first': first_name,
        'name_last': last_name,
        'login': {
            'email': input_email,
            'password': get_hash_of(password),
        },
        'payment_details': {
            'cardholder_name': cardholder_name,
            'card_number': get_hash_of(card_number),
            'expiry_month': expiry_month,
            'expiry_year': expiry_year,
            'cvv_num': cvv_num,
        },
        "profile_img_url": '',

        # initially, user doesn't have any tickets. Later it will be populated by tickets
        "tickets": [],
        # e.g. ["music events", "christmas carol"], the strings are search histories
        "search_history": [],

    }

    # Add new user in
    users.append(new_user_info)

    # Create token for the session
    token_data = {
        'email': input_email,
        'session': str(datetime.now().timestamp())  # str(float)
    }

    # encode the token with jwt
    token = encode_jwt(token_data, SECRET)

    valid_token_list.append(token)

    # Add data into return_info
    return_info['token'] = token

    return return_info


def auth_login(email, password):
    '''
    Given a registered users' email and password, generates a valid token
    for the user to remain authenticated
    '''
    global valid_token_list
    email_registered = False

    return_info = {
        'email': email,
        'token': '',
    }

    # Check if email is valid
    if check_valid_email(email) == 0:
        raise InputError(
            description='Sorry, the email you entered is not valid.')

    # Check if user exists (if user's in the database)
    for user in users:
        # If input email matches email in data file
        if user['login']['email'] == email:
            email_registered = True
            # If input password matches stored hashed password
            if user['login']['password'] == hashlib.sha256(password.encode()).hexdigest():
                # Input email and password is valid, continue to create token
                pass
            else: 
                # if password is incorrect, raise error
                raise InputError(description='Incorrect password')
    
    if db_state:
        # Check if user exists (if user's in the database)
        if password_match(email, hashlib.sha256(password.encode()).hexdigest()):
            email_registered = True
            # pass
        else:
            InputError(description='Incorrect password')

    # rejected non registered users
    if not email_registered:
        raise InputError(
            description='Account does not exist: email not registered')

    # Create token
    token_data = {
        'email': email,
        'session': str(datetime.now().timestamp())  # str(float)
    }
    # encoding email and session information as a token
    token = encode_jwt(token_data, SECRET)

    return_info['token'] = token

    valid_token_list.append(token)

    return return_info


def auth_logout(token):
    '''
    Given an active token, invalidates the token to log the user out.
    If invalid token is given, AccessError will be thrown
    This function can never return false because of above line
    '''
    global valid_token_list

    if token not in valid_token_list:
        raise AccessError(description='Invalid token')

    valid_token_list.remove(token)

    return {"is_success": True}

# Password reset related functions below
# ==========================================================
# This send_email function was modified from code on 
# https://humberto.io/blog/sending-and-receiving-emails-with-python/
def send_email(target_email, reset_code):
    '''
    Sends an email from pomipomi2023@gmail.com to users who requested for 
    a password reset with the reset code
    '''

    # Connect with Google's servers
    smtp_ssl_host = 'smtp.gmail.com'
    smtp_ssl_port = 465

    # Login to the system email account
    username = SYSTEM_EMAIL
    password = EMAIL_PASSWORD

    # Send email from system email to users' email
    from_address = SYSTEM_EMAIL
    user_address = target_email

    # Message containing the reset code
    message = MIMEText("Your reset code for your Pomi account is:\n\n" + reset_code
                       + "\n\nPlease use it to reset your password." +
                       "\n\nNote that this reset code expires in 15 minutes.")
    message['subject'] = EMAIL_SUBJECT
    message['from'] = from_address
    message['to'] = user_address

    # Connect using SSL
    server = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port)

    server.login(username, password)
    server.sendmail(from_address, user_address, message.as_string())
    server.quit()


def auth_passwordreset_request(email):
    '''
    Given an email address, if the user is a registered user, send them a an 
    email containing a secret code, that when entered in auth_passwordreset_reset, 
    shows that the user trying to reset the password is the one who got sent this email.
    '''
    email_registered = False

    secret_code = {
        'user_email': '',
        'expiry_time': (datetime.now() + timedelta(seconds=900)).timestamp()
    }

    for user in users:
        if user['login']['email'] == email:
            email_registered = True
            secret_code['user_email'] = user['login']['email']

    if db_state:
        if find_user(email) == True:
            email_registered = True
            secret_code['user_email'] = email

    if not email_registered:
        raise InputError(description='Email not registered to a user')

    # encode the secret code as a jwt string
    secret_code = encode_jwt(secret_code, SECRET)

    # send the code to this email
    send_email(email, secret_code)

    return {'secret': secret_code}


def auth_passwordreset_reset(reset_code, new_password):
    '''
    Given a reset code for a user, set that user's new password to the password provided
    '''
    global users

    if len(new_password) < 6:
        raise InputError(
            description='Invalid password: password must not be less than 6 characters')

    reset_code_bytes = reset_code.encode()
    # Decode reset_code and extract u_id
    decoded_resetcode = jwt.decode(
        reset_code_bytes, SECRET, algorithms=['HS256'])  # !!!

    # Check for valid reset code (in terms of time)
    if (datetime.now().timestamp() > decoded_resetcode['expiry_time']):
        raise InputError(description='Reset code is invalid')

    user_email = decoded_resetcode['user_email']
    new_password_encoded = hashlib.sha256(new_password.encode()).hexdigest()

    for user in users:
        if user['login']['email'] == user_email:
            # Reset user password
            user['login']['password'] = new_password_encoded
            if db_state:
                change_password_in_database(
                    user_email, new_password_encoded)
    return {}


def check_valid_reset_code(reset_code):
    reset_code_bytes = reset_code.encode()
    # Decode reset_code and extract u_id
    decoded_resetcode = jwt.decode(
        reset_code_bytes, SECRET, algorithms=['HS256'])

    # Check for valid reset code (in terms of time)
    if (datetime.now().timestamp() > decoded_resetcode['expiry_time']):
        raise InputError(description='Reset code is invalid')

    return True


if __name__ == '__main__':
    # Some driver code
    # print(check_valid_email("hi@gmail.com"))
    # send_email("@gmail.com", "111")

    # Register user Luya Pan
    registration = auth_register("luyapan1202@gmail.com", "1234567", "Luya", "Pan",
                                 "Luya Pan", "1111222233334444", 12, 2023, "123")
    # print("---> User registered: ")
    # print(registration)

    # Log user in
    login_success = auth_login("luyapan1202@gmail.com", "1234567")
    # print("\n---> User logged in:")
    # print(login_success)

    # Log user out using the token
    logout_success = auth_logout(login_success['token'])
    # print('\n---> User logging out: ')
    # print(logout_success)

    # # Now say Luya forgot her password and would like to request a password reset
    # print('\n---> User requesting password reset: ')
    # # This should send an email with the secret reset code
    # secrete_code = auth_passwordreset_request("luyapan1202@gmail.com")
    # print("secret_reset_code")
    # print(secrete_code['secret'])

    # # User resets the password to 7654321
    # print("\n---> User resets the password...")
    # auth_passwordreset_reset(secrete_code['secret'], "7654321")

    # # Login fails since user has already changed the password. An InputError should be raised
    # # login_fail = auth_login("luyapan1202@gmail.com", "1234567")

    # print("\n---> User logged in:")
    # login_success = auth_login("luyapan1202@gmail.com", "7654321")
    # print(login_success)

    login_success = auth_login("luyapan1202@gmail.com", "123456")
    print("\n---> User logged in:")
    print(login_success)
